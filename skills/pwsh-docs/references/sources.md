# Sources and licences (read 2026-10-06)

The skill text and every example are written fresh. The docs below were read to check each rule. Only short command lines and output fragments are quoted, each with its file.

- MicrosoftDocs PowerShell-Docs, commit a3de8f22552170e70852470d46cd52cd9ca471ec on main (pushed 2026-09-24), read 2026-10-06 from a local download in `work/pwsh-docs/src/` (git-ignored, never committed). Upstream https://github.com/MicrosoftDocs/PowerShell-Docs, licence CC-BY-4.0 text plus MIT code samples read live 2026-10-06.
  - Licence: CC-BY-4.0 for documentation text, MIT for code samples (LICENSE plus LICENSE-CODE in the repo root, re-read live 2026-10-06). Permissive: no NonCommercial and no ShareAlike restriction, so this skill may be shared and sold; attribution via the credit line below.
  - Files used: about_Parsing.md, about_Special_Characters.md, about_Quoting_Rules.md, about_Comparison_Operators.md, about_Operators.md, about_Pwsh.md, about_Splatting.md, about_Redirection.md, about_Pipelines.md, about_Pipeline_Chain_Operators.md, about_Automatic_Variables.md.
  - Command outputs quoted in parsing.md, quoting.md, and patterns.md were run on this PC with pwsh 7.6 on 2026-10-06, not copied from the docs.
- The trial sheet `evals/pwsh-docs_trials.jsonl` (12 tasks: 7 answer, 5 run) pins each task to its docs section via its `locator` field at commit a3de8f22.
- This skill is original work under MIT. It is free to use and share.

Chunk manifest for `distill check` without `--work`: no `NNNN.txt` chunk refs are used; every SKILL.md rule is covered by the 12 trial rows above (`evals/pwsh-docs_trials.jsonl`).

Credit line for THIRD_PARTY_NOTICES.md: MicrosoftDocs/PowerShell-Docs (CC-BY-4.0 text, MIT code, pinned a3de8f22 read 2026-10-06; own words and own examples, short quotes only).
