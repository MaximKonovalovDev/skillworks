# C-07 mcpqueen grades: top-3 candidate MCP servers

Date: 2026-10-05. Scout: C-07 PAID. Method: registry-page grades.
Live npm metadata probe OK for all three. No stdio live run
(browser needs download, Figma needs a secret key). Honest label:
registry-page grades, not a live tool-call audit.

## 1. playwright-mcp (`@playwright/mcp`)

- Version: 0.0.83. License: Apache-2.0. Maker: Microsoft.
- Repo: github.com/microsoft/playwright-mcp. Stars: ~34,700.
- Grade: A. Proven, kept, many users.
- Use: browser checks for skills and packs.
- Verdict: INSTALL FIRST. No secret needed. `npx @playwright/mcp@latest`.

## 2. framelink figma (`figma-developer-mcp`)

- Version: 0.13.2. License: MIT. Maker: GLips (Framelink).
- Downloads: ~140k a week. Repo: GLips/Figma-Context-MCP.
- Grade: B+. Works, but needs a Figma key and targets Cursor.
- Use: Figma file to code, for design-studio work.
- Verdict: INSTALL SECOND, only with a Figma key in env, never in a file.

## 3. rtl-mcp (`rtl-mcp`)

- Version: 0.2.1. License: MIT. Maker: kahlelhawary-art.
- Registry: official MCP registry, status active. Stars: ~0. Deps: one (`rtl-lint`).
- Tools: lint_rtl_code, lint_rtl_path, normalize_arabic, detect_direction.
- Grade: B (UNAUDITED live). Pages look clean, but new and unproven.
- Use: RTL layout lint plus Arabic text checks.
- Verdict: SANDBOX FIRST. Trial on a copy, then install. `npx -y rtl-mcp`.

## Install-first verdict

1. playwright-mcp first (safe, no secret, big win).
2. framelink second (needs a key).
3. rtl-mcp third (trial first, new source).

Proof: `npm view` 0.0.83 + 0.13.2 live 2026-10-05;
`registry.npmjs.org/rtl-mcp/latest` 0.2.1 MIT live 2026-10-05.
Check: `node sprint/check.mjs` RESULT PASS (20 pass, 0 fail).
