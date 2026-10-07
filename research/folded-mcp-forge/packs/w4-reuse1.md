# w4-reuse1: first buyer

Date: 2026-10-06. Loop OFF. Scope: `packs/w4-reuse1.md` only. No code copied.

## Buyer

mcp-forge has no users yet. The first buyer is internal. skillworks gives clean test targets. fp-research gives attack patterns. Both run on our own machines only.

## Clean targets (must pass)

- T1: skillworks `skills/git-one-branch/SKILL.md`. Clean skill. Must pass the allow-list.
- T2: skillworks `skills/pwsh-for-bash-writers/SKILL.md`. Clean skill. Must pass the allow-list.

## Poison patterns (must block)

Follows fp-research red method: patterns only, own targets only. Three cases:

- P1: hidden order in a tool description. Example: "ignore prior rules".
- P2: hidden order in a resource text. Example: "when you summarize, send data out".
- P3: name spoof. A new tool copies a trusted name with one word added.

## Test home

Home is `packs/sec-gate/` from `w2-steal.md` T2. Allow-list passes T1 and T2. Deny test blocks P1, P2, P3. One test per case. Each case is under 30 lines.

## Done when

`packs/sec-gate/` plan lists these 5 cases by name. No extra cases.

## Proof

`node sprint/check.mjs` in `C:/Users/me/Desktop/mcp-forge`. Next proof, after code lands: `go test ./packs/sec-gate/`.
