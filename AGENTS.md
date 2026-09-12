# AGENTS.md — skillworks operator lanes

## Lanes (only shell lane)

```powershell
python -m book2skill extract --in <src> --out work/<name>
python -m book2skill split --work work/<name>
python -m book2skill index --work work/<name>
python -m book2skill build --work work/<name> --skill skills/<name>
python -m book2skill audit --skill skills/<name>
python -m book2skill eval --skill skills/<name> --qa evals/sample_qa.jsonl
python -m book2skill export --skill skills/<name> --target claude|codex|opencode|gemini
python -m pytest tests/ -q
python mcp_server/server.py
```

## Rules

0. Only feed sources you own or public-domain texts. Never commit
   copyrighted books. Gutenberg downloads stay in `work/`, ignored by git.
1. SKILL.md frontmatter must carry `name` + `description`; name matches dir.
2. Eval gate: pass rate below 0.6 refuses `export`. Fix the skill, not the test.
3. Refresh wins over rebuild: `refresh` no-ops when the fingerprint matches.
4. Receipts: every stage writes `work/<name>/receipt.json` with counts.
