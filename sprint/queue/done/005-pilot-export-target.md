---
role: builder
title: clean error on unknown export target (traceback today)
---

Goal: A stranger who typos `--target` gets `Error: unknown target ...` and the legal list, not a Python traceback.

Scope: `book2skill/export.py` (raise `click.UsageError` instead of `ValueError`) or `cli.py` (`click.Choice(TARGETS)` on `--target`). One test optional.

Proof (pilot-view-r2, 2026-10-03):
- `python -m book2skill export --skill skills/pilot-view-demo --target bogus --out dist/pilot-view-demo` → exit 1 with full `Traceback ... ValueError: unknown target bogus; legal: [...]` (20+ lines through click internals).
- `refresh` no-op pathcontrast: second `refresh` run prints `unchanged, no-op`, exit 0 — that lane already behaves.
- `python -m pytest tests/ -q` → 7 passed (baseline).

User sees differently: `export --target bogus` prints a two-line usage error naming `claude|codex|opencode|gemini`, instead of a traceback.

Stop: M 30 min. Sized XS. Proof for DONE: bad-target run shows clean error + pytest green.


## Result (completed)

<task id="ses_efec066a2ffe3ueWOP0X6KwRbj" state="completed">
<task_result>
RESULT: NOOP - fix already landed in HEAD, no edit; bad-target shows clean usage error | proof: `python -m pytest tests/ -q` → 12 passed
</task_result>
</task>
