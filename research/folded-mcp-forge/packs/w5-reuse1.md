# w5-reuse1: sec gate user #1

Date: 2026-10-06. Loop OFF. Scope: `packs/w5-reuse1.md` only. No code copied.

## User #1

skillworks. First outside user of the sec-gate spec (`packs/w4-enrich1.md`, tests from `packs/w4-reuse1.md`).

## What it reuses

Allow-list filter plus 5 cases: T1-T2 clean skills pass, P1-P3 poison patterns block. No gateway, no scan levels yet.

## How

skillworks copies the 5 case names into its own pilot checklist. It runs them against its skill loader. Pass means clean skills load, poison skills block with a log line. Fail means it files one inbox item here.

## Done when

skillworks reports 2 pass + 3 block by name. No code moves. `packs/sec-gate/` stays the only home.

## Proof

`node sprint/check.mjs` in `C:/Users/me/Desktop/mcp-forge`.
