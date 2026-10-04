# Distill prompt v2 (versioned prompt fragment, llm-style)

Chapter-to-rule distill prompt. Versioned here, never inline. Bump `version:`
when the wording changes; `distill.py` stamps the version into its plan
receipt. Supersedes `build-skill.md` v1 for the distill pass: v1 wrote a
scaffold with placeholder files, v2 writes finished rules with locators.

version: v2

Given one reading packet (its chunks plus their locators, e.g. 0042.txt),
write the skill rules the packet teaches.

Rules: one rule per idea, each rule on its own `- ` bullet with the exact
command or pattern in backticks. Every rule carries its locator on the same
bullet: the chunk file it came from (e.g. `0042.txt`) or the tested pair that
proves it (a `prints:` line with the measured output). A rule with no locator
is refused by `distill check`. Never invent beyond the packet: if the packet
does not show it, write "needs source" instead of guessing.

Budgets: the finished SKILL.md body stays within 2000 tokens (chars // 4).
The skill carries 10 or more tested pairs, each with its `prints:` output.
No scaffold text ("Built from owned sources", "Fill ... while reading").
Plain ASCII only, so no tool output turns into mojibake on Windows.
