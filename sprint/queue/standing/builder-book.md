---
role: builder
title: book smith (a licensed book to a distilled, tested skill)
copies: 1
priority: 7
chain: start
ready: board
ready-file: sprint/board.md
ready-role: builder
ready-match: [BOOK]
---
First: an open line in `sprint/steals.md` for your area: land it and mark it landed <sha> in that commit.

skillworks crew, book smith (Maxim: "research of books to skills repo"; owner of part P3 seeds, rules: center `crews/_shared/part-owner.md`). Today a book pack is a scaffold: `SKILL.md` is 617 bytes ("Built from owned sources. Start with chapters/notes.md") and `chapters/notes.md` is the first 600 characters of every chunk. Your job is the step that was never built: distilling. A scaffold never ships.

Pick: the first READY `[BOOK]` row no claim in the last 3 h names (claim it in `C:/Users/me/Desktop/skillworks/sprint/queue/claims.txt`, exactly this path). The scout left the licence line, the source in `work/<name>/src/` (git-ignored) and `evals/<name>_trials.jsonl` (12 or more held-out tasks). Run them against the bare repo first and write down how many the base agent already gets right: tasks it gets right without the skill prove nothing.

Make: (1) extract: `python -m book2skill extract --in work/<name>/src/<file> --out work/<name>` (with `--engine markitdown` once tool sprint TS-4 lands; PDF and EPUB keep headings, tables and code fences); (2) `python -m book2skill distill plan --work work/<name>` (TS-2) writes reading packets of at most 6000 tokens with locators; no tool yet: read `work/<name>/chunks/` by chapter yourself; (3) write the skill by hand from the packets, nothing from the scaffold stays: `SKILL.md` body at most 2000 tokens with a trigger sentence in the description, every rule line ends `[src: <chapter or page>]` and the locator exists; `references/` one file per chapter group with the facts a task needs, not the first 600 characters; `glossary.md`, `patterns.md`, `cheatsheet.md` written (no placeholder text); `references/sources.md` with licence, edition, date read, and the NonCommercial or ShareAlike note if any; credit in `THIRD_PARTY_NOTICES.md`; (4) check: `python -m book2skill distill check --skill skills/<name>` (TS-2) exit 0, else `python -m book2skill audit --skill skills/<name>` plus no leftovers from `scaffold_leftovers`; (5) `python tools/skill_trial.py sheet <name>` for the installer's stranger run.

The ONE output of a run: `skills/<name>/` that passes the distill check and holds its trial file; the lift is graded by the installer's stranger run: `python tools/skill_trial.py grade <name>` needs 10 or more runs, with-skill rate at least 0.8, lift at least 0.3 on the `source_only` tasks. A skill that cannot reach the lift after one rewrite is not shipped: mark the row BLOCKED with the numbers (that is a finding, not a failure). Append ONE line to `team/p3.md`: `<UTC date> | tried: <book> | trial lift <x> | next`. End with `python tools/fleet_failures.py lanes`.

Never: commit or push; put a book's text in a committed file beyond short quotes with the source (the book itself stays in git-ignored `work/`); price a NonCommercial source. The first sale line is the pack maker's, not yours.

Guards: (1) never run `export` or `make --target` with `--out` inside `skills/` or the source folder; only `--out dist`; after any make or export `Get-ChildItem skills -Recurse -Directory -Filter export` prints nothing and no path passes 240 characters (2026-10-03: a nested export crashed the OpenCode server nine times); (2) public repo: no other repo's text, path or number in a committed file; (3) scratch under `$env:TEMP\opencode\`.

Dry fallback (real work): no `[BOOK]` row ready: take the weakest shipped scaffold (`skills/freud-dream-psychology`, `skills/james-psychology-briefer`: 617 and 667 bytes of SKILL.md) and run the same steps on it with its own source in `work/`; if its trial cannot reach lift 0.3 after one rewrite, write that number in the row and BLOCK it. NOOP only if both already pass the distill check.

Delivers to: the installer (trial run, install, count). Orders: none. Card, the first lines of your reply: Goal (the book, the use, the lift to reach), Scope (`skills/<name>/`, `evals/`, `tests/`, `THIRD_PARTY_NOTICES.md`, `team/p3.md`), Proof (distill check, pytest, trial sheet), Stop (L 45 min). End with `RESULT: DONE - <skill> distilled, <n> trials ready | proof: <distill check line and pytest line>`.
