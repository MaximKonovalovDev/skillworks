---
role: judge
title: review installer global-alias fix (Vol1 upkeep)
chain: review
of: pilot-install-vol1-repair
writer: builder
attempt: 1
origin_title: repair log Vol1 loads run (S110)
---
Review pilot-install-vol1-repair, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\pilot-install-vol1-repair.md (if missing, judge the tree and say so). Rerun its proof yourself, read its diff. You never edit. Scope: tools/install_fleet_skills.py only (the `--to global` alias resolving to a literal ./global folder); yq-jq FLEET lines belong to BK-1007-5, not this packet.

Rerun and paste each result line: `python tools/install_fleet_skills.py --to global --check pwsh-for-bash-writers` exit 0; `--to C:/Users/me/.config/opencode/skills --check pwsh-for-bash-writers` exit 0; `node sprint/check.mjs` PASS.

Always: (a) full pytest equal or better than before (pre-existing fails test_g16_install5, c02, seat-guard untracked, fleet stales named, not charged); (b) privacy: no other repo's path, text or number, no secret; (c) only the installer file changed; no weakened gate; (d) ONE REAL THING: the global-alias check flips exit 1 to exit 0 on this diff, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.
