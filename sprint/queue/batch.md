# Next batch: skillworks (the keeper rewrites this file, 2026-10-03T19:11:24.279Z)

Send every line below as ONE message of 7 Task calls: subagent_type = the role, description = the title, prompt = `packet: <name>` exactly. The keeper puts each packet's text into its call, so all of them run at once, live in your session. Width 7, CPU-heavy at most 3.

1. builder | MCP skill_search serves only repo-root skills/; scratch-built skill invisible | packet: 015-pilot-mcp-scratch-invisible
2. builder | build accepts --name that breaks the name-matches-dir rule (silent invalid skill) | packet: 016-pilot-build-name-dir-mismatch
3. planner | planner (rows from the vision) | packet: planner-rows
4. researcher | scout (steals that land on a finish bar) | packet: researcher-steal
5. builder | builder (board rows) | packet: builder-rows
6. pilot | pilot (the user's view) | packet: pilot-view
7. researcher | vision researcher (scorecard, parts, gaps) | packet: researcher-vision

Not in this batch (readiness: planner-research-merge).
