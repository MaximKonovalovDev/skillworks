# skillworks research

Cards live in `research/cards/`. The research merge seat retired 2026-10-04: the toolsmith lands tools and logs them in `sprint/steals.md`; the lines below are the old record.

## Merges

Merge: 2026-10-03T01:30Z | cards 5 | accepted 4 | rejected 0 | dupes 1
Merge: 2026-10-03T01:48Z | cards 5 | accepted 3 | rejected 0 | dupes 2
Merge: 2026-10-03T13:46Z | cards 4 | accepted 4 | rejected 1 | dupes 1
Merge: 2026-10-03T14:10Z | cards 5 | accepted 2 | rejected 8 | dupes 1 (S16 C1-C2 kept -> K-34,K-35 with home+proof; S16 C3/C5 reject-deferred folded into K-34/K-35, C4 reject no-home; S17 0 cards 5 rejects; dupe S17-R3=K-28 DONE; K-26..K-29 checked, no dup; S16/S17 already dated, nothing re-dated)
Merge: 2026-10-03T14:20Z | cards 5+0 | accepted 2 | rejected 8 | dupes 0 (S19 C2->K-37 + C4->K-38 READY PREP-ONLY docs-only with home+proof; S19 C1/C3 K-27-gated no row, C5 owned by K-08 changelog no row; S20 0 cards 5 rejects stand; K-26..K-36 checked, no dup; K-27 split DECIDE-OWNER + K-39 ACT-BLOCKED; S19/S20 already dated, nothing re-dated)

## S49 prompts-plus-workflows hunt (PW-1006-1, researcher-toolsmith-r6, 2026-10-06)

11 cards read on disk in center research cards, all licences read live 2026-10-06 by the center sweep. Takes are shapes only, zero code vendored.

S49-01 coder Roo-Kilo: RooCodeInc Roo-Code at b867ec9 plus Kilo-Org kilocode at 9d0f7a1. Licence Apache-2.0 plus MIT. Take: prompt-as-function with named sections per mode plus live env block from repo facts plus todoList and diff-strategy carried through generation.
S49-02 pr-agent judge: qodo-ai pr-agent at 06a2991c0ce6b055c77fbcbd7f09faf4c5acfcaf. Licence MIT. Take: added-lines-only scope plus untrusted-input guard plus concrete-scenario flag rule plus YAML verdict with score plus effort plus risk plus merge enum plus fingerprint dedupe plus capped repo-context file.
S49-03 researcher scout: grapeot deep_research_agent plus SkyworkAI DeepResearchAgent at HEAD. Licence MIT plus MIT. Take: shared scratchpad with sections plus typed task deliverables blockers envelope plus no-dispatch-without-written-plan guard plus per-round prompt files plus debate-manager verdict seat.
S49-04 orchestration handoffs: openai swarm at 6af0b4c plus VRSEN agency-swarm at 1aeb325 plus camel-ai camel at 24fde60 plus OpenBMB ChatDev at 4fb2db0 plus langchain-ai langgraph-swarm-py at 5442a15. Licence MIT for swarm agency-swarm langgraph-swarm-py plus Apache-2.0 for camel ChatDev. Take: handoff-as-return plus communication_flows allowlist plus shared_instructions header plus fan-out-collect pool plus phased review gate before handoff accept.
S49-05 tool-use cline-aider: cline cline at cd80a20 plus aider-ai aider at 5dc9490 plus Roo-Code plus SWE-agent plus OpenHands licence-only. Licence Apache-2.0 for cline aider Roo-Code plus MIT for SWE-agent OpenHands. Take: batch-first dispatch plus read-only-until-added scope plus verify-before-claim suffix as three prompt lines.
S49-06 debug SWE-aider edit-miss guards: sst opencode at dev plus SweepAI sweep at a8b8b67 plus kentaro-m auto-assign at ad14993 plus bors-ng bors-ng at master. Licence MIT for opencode plus ISC for auto-assign plus Apache-2.0 for bors-ng, Sweep EE ideas-only never vendored. Take: re-read-before-edit in the same packet plus one writer per file per dispatch plus owned paths per dir plus serialize landing per file.
S49-07 gamedev tween-physics: godotengine godot-demo-projects at 3e08537616661a5883831628decab4c526260289. Licence MIT. Take: feel-loop tween chain plus loops plus parallel plus ease picks plus functional-vs-perf test split plus id path manifest as assembly gate plus menu plus cmdline headless runner plus manifest as cook list.
S49-08 asset direction: LuoJiangYong muse-video-skill at e01a6cf. Licence MIT. Take: one role sheet per direction axis plus mood-to-hex table with usage column plus visual_cause sentence per asset plus per-section approval flag plus assembler filling a fixed template from JSON state.
S49-09 marketing hooks: blacktwist social-media-skills at 4f85b07 plus AgriciDaniel claude-seo at 4b99de2. Licence MIT plus MIT. Take: nine-pattern hook library plus multi-variant test plus ER plus top-performer diagnosis joined to readbacks plus programmatic gates with 40 percent unique and batch caps.
S49-10 design obra: obra superpowers at 8ca22db plus microlinkhq cards at be9fa97. Licence MIT plus MIT. Take: brief-gate HARD-GATE before build plus verify-gate checklist before any done-claim plus covers as pure function from query params plus open-props tokens plus og-image fallback.
S49-11 redteam attacker: promptfoo promptfoo at HEAD plus berstend puppeteer-extra at HEAD. Licence MIT plus MIT. Take as prose never code: plugin-catalog times strategy-wrap split plus iterative tree loop with per-round metric plus one-evasion-one-drill checklist.

First-experiment handoff to the cure smith (DR-1006-4 owns skills edit-verify plus evals plus tests): lint-after-edit trial setup is 12 tasks in evals edit-verify_trials.jsonl, kinds run plus answer, each with must plus must_not plus a locator into the donor lines above (cline act.ts batch-first plus verify-edited-files, aider base_prompts scope plus suggest-files-then-stop, opencode edit.ts lock plus CRLF normalize plus empty-oldString refusal). Grade gate per the row: with_rate 0.8 or more and lift 0.3 or more via python tools skill_trial.py grade --skill edit-verify.

## Archived

2026-10-03 (fixer pass): 16 cards moved to `archive/2026-10-03/research/cards/`: S04 S05 S11 S12 S13 S14 S15 S18 (donors the part cards P1/P2/P4/P5 and rows K-26 K-29 K-41 K-42 K-43 already carry), S06 S07 S08 S09 S10 (the sweep card `2026-10-03-S06-S10.md` stays), S16 S17 S20 (closed by the Merge lines of 14:10Z and 14:20Z). Read them by path; searches skip `archive/`.
