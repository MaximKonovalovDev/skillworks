---
role: builder
title: reseal bevy-rust-ecs stale live proof (Vol1 member failing gates)
---
Goal: make Vol1 member bevy-rust-ecs pass its own gates again (pytest names it 3x FAIL while sibling pwsh-for-bash-writers is green).

Scope: skills/bevy-rust-ecs/ plus its live proof only. Own repo paths only, never commit. No other repo's text, paths or numbers in any committed file.

Proof: `python -m pytest tests/ -q -k "bevy"` green; failure today: test_qa_musts_literally_appear_in_the_skill_text plus test_fleet_skill_eval_gate[bevy-rust-ecs] plus test_fleet_skill_matches_its_last_live_proof[bevy-rust-ecs], fingerprint `changed since its live tests last passed (2026-10-06T18:01Z), run python tests/live_proof.py bevy-rust-ecs`. Distinct from DR-1005-9 DONE (viewer aborts); this is proof staleness after a skill edit.

Stop: M 30 min. End with the RESULT line.
