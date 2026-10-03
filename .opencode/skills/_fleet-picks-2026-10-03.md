# Fleet picks 2026-10-03 (skillworks)

Candidates: anthropics/skills skill-creator, mcp-builder, pdf/docx/pptx;
modelcontextprotocol/servers + python-sdk; VoltAgent awesome-claude-code-subagents
(mcp-developer, documentation-engineer); obra/superpowers writing-skills.
Rejected: anthropics/skills (GitHub license null, no LICENSE file) and
modelcontextprotocol/servers (spdx NOASSERTION) fail the MIT/Apache/BSD/CC0 gate.

Picked 3 (all adapted to book2skill paths, ≤120 lines):
1. skill-eval-harness <- superpowers writing-skills (MIT): baseline-vs-skill
   RED-GREEN + trigger-only descriptions. Users: builder, judge, planner.
2. mcp-server-tester <- VoltAgent mcp-developer (MIT): stdio handshake/list/
   call/bad-call matrix for mcp_server/server.py. Users: builder, runner.
3. manual-extract-qa <- VoltAgent documentation-engineer doc-testing (MIT) +
   own extract.py/tests: receipt counts, table walk, Gutenberg strips.
   Users: builder (extract/split), researcher (source triage).
