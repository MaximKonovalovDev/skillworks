# Build prompt v1 (versioned prompt fragment, llm-style)

Chapter-to-skill prompt. Versioned here, never inline. Bump `version:`
when the wording changes; `build.py` stamps the version into its receipt.

version: v1

Given the chapter notes below, write the skill section requested.
Rules: only concepts named in the notes, one idea per paragraph,
plain words, no invented terms. If a note is unclear, say
"needs source" instead of guessing.
