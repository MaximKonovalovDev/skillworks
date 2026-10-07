---
role: judge
title: review mcp-template tested pack
chain: review
of: builder-pack-mcp
writer: builder
attempt: 1
origin_title: adopt mcp server template as tested pack (PIPE-1006-1)
---
Review builder-pack-mcp, built by builder. Its record: C:\Users\me\Desktop\skillworks\sprint\queue\done\builder-pack-mcp.md (if missing, judge the tree and say so). Rerun the proofs yourself, read the diff, check PIPE-1006-1's done-when as written (selftest SELFTEST PASS plus pack listed in catalog with test green; check PASS). You never edit.

Run the check that fits what it made, and paste the result line of each:
1. A pack: the template server selftest ends SELFTEST PASS; the pack test (`pytest tests/test_mcp_template.py -q`) green; the catalog lists the pack.
2. Licence: donor modelcontextprotocol python-sdk MIT only, credit line matches; no NonCommercial, no price on a template; sources stay out of the commit or are original.

Always: (a) `python -m pytest tests/ -q` and `node sprint/check.mjs` equal or better than before (pre-existing out-of-scope fails named, not charged); (b) privacy: no other repo's path, text or number, no secret; (c) only owned files changed (packs/mcp-template/, its test, catalog file); no weakened gate; (d) ONE REAL THING: selftest plus pack test green on the rerun, or FAIL paperwork.

Your whole reply is at most 15 lines: `VERDICT: PASS|FAIL|BLOCKED`, what changed, the checks before and after (commands and numbers, the one real thing named), and how to revert it. A proof you cannot run is BLOCKED, never a guess.

Built result, cut:
<task_result> RESULT: DONE - mcp-template pack tested and catalog-listed (server --selftest + selftest.py SELFTEST PASS, catalog row added, new pack test 5 passed, check.mjs PASS) | proof: `python -m pytest tests/test_mcp_template.py -q` 5 passed; `node sprint/check.mjs` RESULT PASS 20/0/0 </task_result>

Keeper facts: run builder-pack-mcp (seat builder, @builder), adopt mcp server template as tested pack.
