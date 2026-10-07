# Lead 2 journeys: skillworks
Edit this file. Lead 2 walks these: one helper per journey, at most 3 a run (never walked first, then the lowest score).
Keep each journey to four one-line fields: Start, Steps, Good, Proof. Keep 3 to 6 journeys. In the popper: the ... menu of the card, Edit Lead 2 journeys.

Persona: a loop that installs a skill and wants its failures to drop, and a stranger who wants a tested pack.
Maxim's words: "skillworks: books to skills, and it improves and diagnoses the other repos' agents"
Rule: Never publish or upload a pack.

## J1 Install as a stranger
Start: the installer pilot (pilot-installer.md).
Steps: pick one skill, put it in a scratch loop folder and run its test.
Good: installed in 15 minutes and its eval passes.
Proof: the skill, the command and the result.

## J2 The failure drop
Start: C:/Users/me/.empire/state/skilldoctor/adopted.csv (one line per installed skill, with failure counts before and after).
Steps: pick 3 rows that have both counts.
Good: the failure class fell by half or more.
Proof: the 3 rows and the percent each.

## J3 The MCP server lists every skill
Start: `python -m pytest tests/test_mcp_schema.py tests/test_mcp_skills_dir.py -q` in C:/Users/me/Desktop/skillworks.
Steps: run it.
Good: it passes.
Proof: the printed result line.

## J4 One text everywhere
Start: the same skill name in several places, for example bash-spawn-guard.
Steps: compare the copies in skillworks, the loop repos and C:/Users/me/.config/opencode/skills.
Good: one text everywhere.
Proof: the differing lines (see center research/MONOREPO-PASTE-REVIEW-2026-10-07.md).
