# Loop kernel v2

Rules every loop shares. Center owns this file: `node loopkit.mjs update` copies it to every repo as `.opencode/kernel.md`. Never edit a copy. Rules one repo alone has stay in its `/sprint`, `AGENTS.md`; where they differ, the repo wins.

## Start and lock
- After compaction the files, not memory, carry the loop: redo Start.
- One lock token per session, kept in the handoff. Another fresh token: stop unless `takeover` and the old session closed. Release only your own lock.
- A halt or `STOP` file means stop. Only the owner removes it.
- `.opencode/knobs.json` wins over numbers in `/sprint`. Never edit it; propose via a `KNOB PROPOSAL:` line in the handoff.

## The batch
- The keeper names each batch: chain steps and one-offs first, then seats in fair turns, at most `heavy_max` CPU-heavy; also in the queue's `batch.md`.
- Send the whole list as ONE message of Task calls: `subagent_type` the role, `description` the title, `prompt` exactly `packet: <name>`. The keeper fills the text, so every helper runs at once, live, foreground. Never `background: true`. Send full width while eligible work exists; held seats rest, and a sent seat with nothing to do ends `RESULT: NOOP - <reason>` with proof, never filler.
- A packet has Goal, Scope, Proof, Stop, owned paths and a done-when, or the keeper refuses it. Every helper ends `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what> | proof: <where>`; BLOCKED and NOOP name the cause.
- When the batch returns, collect every result, then send the next batch same turn. A question you need now is one more Task in the batch. Never redo a helper's work.

## The chain
- A writer seat carries `chain: start`. Its DONE gets the judge's review atop the next batch.
- Every writer is judged independently before it lands. A FAIL gets one repair by the writer; a second FAIL or a BLOCKED comes to you. A PASS comes to you to commit: by path, never `-A`, the proof's one-line result in the commit body.
- A round that moved nothing says why. A finding is a packet, not an essay. Research lands only with source, license, row it feeds, spike.

## Commit
- Commit verified paths only. Never `git add -A`, another session's files, a secret or force-push.

## Tools on this box
- Shell is pwsh: prefer grep/glob/read tools; in shell `rg`, `Select-String`, `Get-Content -TotalCount/-Tail`, `Measure-Object`; cap big outputs.
- Edit: re-read exact lines just before editing; files are CRLF, copy oldString from the latest read.
- Research: read `.opencode/repomap.md` first, never list trees; deepwiki once then `gh api`; never guess raw.githubusercontent URLs — `gh api repos/O/R/contents/PATH` or `.../git/trees/HEAD?recursive=1`; rate-limit = authed `gh api`, not search.

## Stop
- Ending a turn is not a stop. `[loop-keeper]` messages are not the owner.
- Stop only for the stop reasons in `/sprint`. Then write the handoff (lock token, what moved with SHAs, blockers, next), say PASS, PARTIAL or BLOCKED, release your lock and end `LOOP STOP: <reason>`.
- The keeper reviews before a stop is final: follow GO, FIX, PIVOT or STOP.
