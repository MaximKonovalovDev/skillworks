---
role: builder
title: make crashes with raw KeyError traceback on QA jsonl that is not {"q","must"} shaped
---

Goal: A stranger who writes `--qa` questions in the everyday `{question, answer, keywords}` shape (or any shape other than `{"q","must"}`) gets a clean refusal quoting the expected shape, instead of a Python traceback.

Scope: `book2skill/eval.py` (validate each QA item before `item["q"]`) + `book2skill/make.py` (surface as an early refusal like the name/places refusals) + one test with a wrong-shaped QA file. No gate-arithmetic change.

Proof (pilot-view-r1, 2026-10-03T21:02Z, scratch only in `%TEMP%\pilot-r1`, repo `work/ skills/ book2skill/ mcp_server/ tests/` untouched):
- Scratch docs folder: 2 own-words files (harbor.md, beacon.md).
- `python -m book2skill make --in <src> --name pilot-r1-demo --description "Use when ..." --qa qa.jsonl` where qa.jsonl holds `{"question": "...", "answer": "...", "keywords": [...]}` lines → exit 1, raw traceback ending `File "book2skill\eval.py", line 42, in run_eval / hits = search(workdir, item["q"], limit=5) / KeyError: 'q'`.
- Same command with `{"q": "...", "must": [...]}` QA → exit 0: `extract folder, 760 chars, 2 files / split 1 chunks / index 1 records / build ... / eval 3/3 = 1.000 (gate 0.6) / audit 6 files, 366 tokens / receipt ...\make.json`.
- The `{"q","must"}` shape is documented only in the `make.py` missing-file error string and the `eval.py` docstring; `--help` says only "QA jsonl: questions drawn from the failure the skill fixes". A stranger has no reason to guess `q`/`must`.
- Precedent: K-36 refuses a bad `--name` with exit 2 and the rule quoted (`--name 'x' must match skill dir ...`). A bad QA shape deserves the same: exit 2 + expected shape quoted.

User sees differently: with a wrong-shaped QA file, `make` prints one line like `Error: --qa <file> line 1 must be {"q", "must"} (got keys: answer, keywords, question)` and exits 2, instead of dumping a traceback that points at framework internals.

Stop: M 30 min for the packet; fix sized S. Proof for DONE: wrong-shaped QA exits 2 with the shape quoted + correct-shaped QA still builds end to end + `python -m pytest tests/ -q` green with a new wrong-shape test.
