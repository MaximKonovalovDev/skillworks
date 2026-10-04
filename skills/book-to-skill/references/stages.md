# The stages, one by one

Every command is `python tools/b2s.py <stage> ...` from the skillworks repo root (or `python <skillworks>/tools/b2s.py`
from elsewhere with explicit paths). `make` runs the first six in order; the stage commands are for one step.

| Stage | Command | Writes | One line it prints |
|---|---|---|---|
| extract | `extract --in <src> --out work/<name> [--glob P]` | `full_text.txt`, `metadata.json`, `receipt.json` | `extracted <n> chars (<kind>)` |
| split | `split --work work/<name>` | `chunks/0000.txt` ... (5000 characters, 200 overlap) | `split into <n> chunks` |
| index | `index --work work/<name>` | `index.jsonl` | `indexed <n> records` |
| build | `build --work W --skill skills/<name> --name <name> --description "..."` | the scaffold in `skills/<name>/` | `built <skill> (<n> note chars)` |
| eval | `eval --work W --skill S --qa evals/<name>_qa.jsonl` | `eval_report.json` beside SKILL.md | a JSON report with `total`, `passed`, `rate` |
| audit | `audit --skill skills/<name>` | nothing | a JSON report with `total_tokens` and tokens per file |
| refresh | `refresh --work W` | `.skillworks.lock`, `index.jsonl` | `changed, reindexed` or `unchanged, no-op` |
| export | `export --skill S --target claude --out dist --work W --qa Q` | `dist/claude/<name>/`, `dist/claude/<name>.zip` | a JSON receipt with `dest` and `zip` |

## What make prints

```
extract  folder, 194 chars, 2 files
split    1 chunks
index    1 records
build    skills\demo-skill
eval     2/2 = 1.000 (gate 0.6)
audit    6 files, 250 tokens
fill     SKILL.md, glossary.md, patterns.md, cheatsheet.md still hold the scaffold text (a person or agent writes them)
receipt  work\demo-skill\make.json
```

`make.json` holds `gate` (`pass` or `refused`), `placeholders` (the `fill` list) and one entry per stage. Exit codes:
0 done; 1 for `eval gate refused` and `export held`; 2 for a usage refusal.

## The eval gate

`eval` searches the chunks for each question and passes it when every `must` string is in the top 5 hits. The rate is
`passed / total`. Under 0.6, `export` and `make --target` refuse. It tests the text, not a model's answer: it shows
a skill still contains the facts, not that an agent uses them well. Fleet skills add live tests and a proof.

## Refresh

`refresh` fingerprints the chunk files. The first run says `changed, reindexed`; a second run with the same chunks says
`unchanged, no-op` and does not touch `index.jsonl`. After a source changes, run `extract` and `split` again, then
`refresh`.

## Export

- `--target` is one of `claude`, `codex`, `opencode`, `gemini`. `make` needs the placeholders written first;
  `export` needs an eval rate of 0.6 or more: an `eval_report.json` beside SKILL.md (the `eval` stage writes it), or
  `--work` and `--qa` together to run the eval inline.
- The copy leaves out the `export` folder of the skill and links, writes `.lock.json` (name, version, eval rate, target,
  date), and the zip skips dotfiles. The zip root holds SKILL.md.
- Refusals: `export refused:` for a destination that is the skill folder, above it, or over 240 characters;
  `eval gate refused export` for a missing report or a rate under 0.6.

## Budgets for a skill that ships

Body of SKILL.md at most 2000 tokens (characters divided by 4, plus 10, as `audit` counts), every `.md` of the skill at
most 14000 tokens in total, description 40 to 1024 characters with a `Use when` phrase, a `license` line, name equal to
the folder, plain ASCII text. `audit` prints the numbers.
