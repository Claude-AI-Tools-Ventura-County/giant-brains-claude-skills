RABBIT-HOLE GUARD ACTIVE — scope-drip discipline.

This is a trigger rule, not a response template. Most replies are unchanged.

## Fire when scope is dripping

- The user signals it: "you keep finding one more thing", "stop nickel-and-diming", "this was supposed to be simple", "stop going down rabbit holes", "just tell me everything at once".
- The user framed the task as small ("quick", "simple", "one-line", "just") and you are about to raise a **third** unsolicited finding. Fire on yourself instead of interrupting again.
- A small, explicitly-scoped task has already absorbed several mid-flight additions.

## Do not fire

- The work is genuinely open-ended or exploratory and incremental discovery *is* the method.
- You are mid-debug and each finding narrows the **same** bug — that is tracing, not drip. (Unrelated issues surfaced mid-debug still count as drip.)
- The user explicitly asked for the deep dive: "find everything, take your time".
- The task really is large. Consolidating does not shrink real scope — say "this isn't small" rather than faking a tidy list.

**Never invent a finding to fill a bucket.** Empty buckets are dropped from the output. Nothing to triage means do not triage.

## When it fires

1. **Stop.** Hold every pending and new finding. No more piecemeal.
2. **Sweep once.** One end-to-end pass. Sort each finding into exactly one bucket: **Blocking** (task is wrong, broken, or incomplete without it) / **In scope, optional** (real improvement, the user's call) / **Out of scope, dropped** (gold-plating, YAGNI, tangent — named so it stops resurfacing).
3. **Get the nod.** Recommend a set — usually blocking only. Ask. Execute only the agreed set.

Sort against the task the user actually asked for, not against what is interesting. Gut-check each Blocking item: if you had not already stumbled on it, would you still call it blocking for the exact task asked? If no, it is Optional or Dropped.

After the triage you have spent your interruption budget. New findings append silently to Dropped. Do not re-open the drip.

Full output format and worked examples: the `rabbit-hole` skill.
