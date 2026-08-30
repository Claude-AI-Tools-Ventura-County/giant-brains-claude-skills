from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


SKILL_ROOT = Path(__file__).resolve().parents[1]
HELPER = SKILL_ROOT / "scripts" / "btw.py"


class BtwHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)
        self.state_home = self.base / "state"
        self.env = os.environ.copy()
        self.env["BTW_STATE_HOME"] = str(self.state_home)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_process(
        self,
        args: Iterable[str],
        *,
        stdin: str = "",
        cwd: Optional[Path] = None,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(HELPER), *args],
            input=stdin,
            cwd=str(cwd or self.base),
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            expected,
            msg=f"command failed\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        return completed

    def run_json(
        self,
        args: Iterable[str],
        *,
        stdin: str = "",
        cwd: Optional[Path] = None,
        expected: int = 0,
    ) -> Dict[str, Any]:
        completed = self.run_process(args, stdin=stdin, cwd=cwd, expected=expected)
        self.assertTrue(completed.stdout.strip(), "expected JSON stdout")
        payload = json.loads(completed.stdout)
        self.assertIsInstance(payload, dict)
        return payload

    def git(self, repo: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(repo),
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"git {' '.join(args)} failed\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        return completed.stdout.strip()

    def make_git_repo(self, name: str = "sample-repo", *, ignore_btw: bool = False) -> Path:
        repo = self.base / name
        repo.mkdir()
        self.git(repo, "init")
        self.git(repo, "config", "user.email", "btw-tests@example.invalid")
        self.git(repo, "config", "user.name", "BTW Tests")
        if os.name != "nt":
            self.git(repo, "config", "core.excludesFile", "/dev/null")
        self.git(repo, "checkout", "-b", "main")
        (repo / "README.md").write_text("# test\n", encoding="utf-8")
        if ignore_btw:
            (repo / ".gitignore").write_text("BTW/\n", encoding="utf-8")
        self.git(repo, "add", "README.md")
        if ignore_btw:
            self.git(repo, "add", ".gitignore")
        self.git(repo, "commit", "-m", "initial")
        return repo

    def common(self, session_id: str, repo: Path) -> list[str]:
        return ["--claude-session-id", session_id, "--project-dir", str(repo)]

    def start(self, repo: Path, session_id: str = "claude-session-1", prompt: str = "/btw task one") -> Dict[str, Any]:
        return self.run_json(["start", *self.common(session_id, repo)], stdin=prompt, cwd=repo)

    def set_focus(
        self,
        repo: Path,
        items: list[str],
        *,
        session_id: str = "claude-session-1",
        allow_git_writes: bool = False,
        expected: int = 0,
    ) -> Dict[str, Any]:
        return self.run_json(
            ["focus", *self.common(session_id, repo)],
            stdin=json.dumps({"items": items, "allow_git_writes": allow_git_writes}),
            cwd=repo,
            expected=expected,
        )

    def test_full_lifecycle_creates_a_new_file_after_end(self) -> None:
        repo = self.make_git_repo()
        first = self.start(repo, prompt="/btw Fix auth; add tests")
        self.assertTrue(first["ok"])
        self.assertTrue(first["created"])
        self.assertEqual(first["repo"], repo.name)
        self.assertEqual(first["branch_at_start"], "main")
        self.assertFalse(first["git_ignored"])
        self.assertIsNotNone(first["warning"])

        first_path = repo / first["file"]
        text = first_path.read_text(encoding="utf-8")
        self.assertIn("/btw Fix auth; add tests", text)
        self.assertIn(f"Repository: `{repo.name}`", text)
        self.assertIn("Active branch at start: `main`", text)

        focus = self.set_focus(repo, ["Fix auth", "Add regression tests"])
        self.assertTrue(focus["changed"])
        self.assertEqual(focus["focus"], ["Fix auth", "Add regression tests"])

        parked = self.run_json(
            ["park", *self.common("claude-session-1", repo)],
            stdin=json.dumps(
                [
                    {
                        "category": "action",
                        "finding": "Unrelated retry loop can spin forever",
                        "why": "It can exhaust a worker",
                        "evidence": "Static inspection",
                        "path": "README.md",
                    },
                    {
                        "category": "review",
                        "finding": "Logging names are inconsistent",
                        "why": "A cleanup would improve maintainability",
                        "path": "README.md",
                    },
                ]
            ),
            cwd=repo,
        )
        self.assertEqual(parked["written"], 2)
        self.assertEqual(parked["counts"], {"action": 1, "interesting": 0, "review": 1, "total": 2})

        self.git(repo, "checkout", "-b", "feature/focus")
        status = self.run_json(["status", *self.common("claude-session-1", repo)], cwd=repo)
        self.assertEqual(status["current_branch"], "feature/focus")
        self.assertEqual(status["context_events_written"], 1)
        self.assertIn("Active branch changed from `main` to `feature/focus`", first_path.read_text(encoding="utf-8"))

        ended = self.run_json(
            ["end", *self.common("claude-session-1", repo)],
            stdin=json.dumps({"completed": ["Fix auth"], "open": ["Add regression tests"]}),
            cwd=repo,
        )
        self.assertTrue(ended["ended"])
        self.assertFalse(ended["active"])

        second = self.start(repo, prompt="/btw Prepare release notes")
        self.assertTrue(second["created"])
        self.assertNotEqual(second["file"], first["file"])
        self.assertTrue((repo / second["file"]).is_file())

    def test_reinvocation_while_active_recovers_existing_file(self) -> None:
        repo = self.make_git_repo()
        first = self.start(repo, prompt="/btw First prompt")
        second = self.start(repo, prompt="/btw This must not replace the first prompt")
        self.assertFalse(second["created"])
        self.assertEqual(second["file"], first["file"])
        content = (repo / first["file"]).read_text(encoding="utf-8")
        self.assertIn("/btw First prompt", content)
        self.assertNotIn("This must not replace", content)

    def test_gitignore_suppresses_warning(self) -> None:
        repo = self.make_git_repo(ignore_btw=True)
        result = self.start(repo)
        self.assertTrue(result["git_ignored"])
        self.assertIsNone(result["warning"])

    def test_duplicate_skip_and_material_update(self) -> None:
        repo = self.make_git_repo()
        self.start(repo)
        self.set_focus(repo, ["Task one"])
        entry = {
            "category": "action",
            "finding": "Potential null dereference",
            "why": "A production request can crash",
            "evidence": "Code path A",
            "path": "README.md",
        }
        first = self.run_json(
            ["park", *self.common("claude-session-1", repo)],
            stdin=json.dumps([entry]),
            cwd=repo,
        )
        self.assertEqual(first["written"], 1)

        duplicate = self.run_json(
            ["park", *self.common("claude-session-1", repo)],
            stdin=json.dumps([entry]),
            cwd=repo,
        )
        self.assertEqual(duplicate["written"], 0)
        self.assertEqual(duplicate["duplicates_skipped"], 1)
        self.assertEqual(duplicate["counts"]["total"], 1)

        updated_entry = dict(entry)
        updated_entry["evidence"] = "A failing regression test now reproduces it"
        update = self.run_json(
            ["park", *self.common("claude-session-1", repo)],
            stdin=json.dumps([updated_entry]),
            cwd=repo,
        )
        self.assertEqual(update["written"], 1)
        self.assertEqual(update["updates_written"], 1)
        self.assertEqual(update["counts"]["total"], 2)

        shown = self.run_json(
            ["show", *self.common("claude-session-1", repo), "--category", "action"],
            cwd=repo,
        )
        self.assertEqual(len(shown["entries"]), 2)
        self.assertIsNotNone(shown["entries"][1]["update_of"])

    def test_focus_limit_and_external_path_are_rejected(self) -> None:
        repo = self.make_git_repo()
        self.start(repo)
        focus_error = self.set_focus(repo, ["one", "two", "three", "four"], expected=2)
        self.assertFalse(focus_error["ok"])
        self.assertIn("1 to 3", focus_error["error"])

        self.set_focus(repo, ["one"])
        outside = self.base / "outside.txt"
        outside.write_text("x", encoding="utf-8")
        park_error = self.run_json(
            ["park", *self.common("claude-session-1", repo)],
            stdin=json.dumps(
                [
                    {
                        "category": "review",
                        "finding": "External issue",
                        "why": "Outside project",
                        "path": str(outside),
                    }
                ]
            ),
            cwd=repo,
            expected=2,
        )
        self.assertFalse(park_error["ok"])
        self.assertIn("inside the project root", park_error["error"])

    def test_opening_prompt_secret_is_redacted(self) -> None:
        repo = self.make_git_repo()
        secret = "sk-ant-" + "A" * 32
        result = self.start(repo, prompt=f"/btw investigate key {secret}")
        self.assertGreaterEqual(result["redactions"], 1)
        content = (repo / result["file"]).read_text(encoding="utf-8")
        self.assertNotIn(secret, content)
        self.assertIn("[REDACTED: ANTHROPIC KEY]", content)

    def test_non_git_project_still_records_context(self) -> None:
        project = self.base / "plain-project"
        project.mkdir()
        result = self.start(project, prompt="/btw write documentation")
        self.assertFalse(result["git_repository"])
        self.assertEqual(result["branch_at_start"], "not-a-git-repository")
        self.assertIsNone(result["warning"])
        self.assertTrue((project / result["file"]).is_file())

    def test_optional_git_guard(self) -> None:
        repo = self.make_git_repo()
        self.start(repo)
        self.set_focus(repo, ["Inspect repository"])

        allowed_payload = {
            "session_id": "claude-session-1",
            "cwd": str(repo),
            "tool_name": "Bash",
            "tool_input": {"command": "git status --short"},
        }
        allowed = self.run_process(["guard-git-hook"], stdin=json.dumps(allowed_payload), cwd=repo)
        self.assertEqual(allowed.stdout, "")

        denied_payload = dict(allowed_payload)
        denied_payload["tool_input"] = {"command": "git commit -m test"}
        denied = self.run_json(["guard-git-hook"], stdin=json.dumps(denied_payload), cwd=repo)
        decision = denied["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("Git commands", decision["permissionDecisionReason"])

        self.set_focus(repo, ["Commit the inspected changes"], allow_git_writes=True)
        allowed_after_focus = self.run_process(["guard-git-hook"], stdin=json.dumps(denied_payload), cwd=repo)
        self.assertEqual(allowed_after_focus.stdout, "")


if __name__ == "__main__":
    unittest.main()
