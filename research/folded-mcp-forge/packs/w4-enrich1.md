# w4-enrich1: sec gate spec

Date: 2026-10-06. Loop OFF. Scope: `packs/` only. No code copied.

Goal: one deny-by-default gate in front of every tool call. Three checks, in order. Any fail blocks the call.

## 1. Isolate (from ToolHive)

Run each server boxed. No host fs, no raw net, no env secrets. Allow-list tools per server. Unknown tool = deny.

## 2. Audit (from AgentShield)

Log each call: time, server, tool, args hash, allow/deny, reason. Keep 30 days. A deny without a log line is a bug.

## 3. Severity (from mcp-scanner)

Scan server config plus tool list before first use. Levels: low, medium, high, critical. High or critical = block until fixed. Re-scan on config change.

## Build

Rewrite: `packs/sec-gate/` under 200 net lines. One filter, one audit log, one scan stub with fixed severities. Tests: allowed call passes, unknown tool denied, high severity blocked, each deny logged.

## Proof

`node sprint/check.mjs` in `C:/Users/me/Desktop/mcp-forge`.
