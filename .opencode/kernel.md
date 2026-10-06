# Loop kernel v3

Rules every loop shares. Center owns this file: `node loopkit.mjs update` copies it to every repo as `.opencode/kernel.md`. Never edit a copy. Rules one repo alone has stay in its `/sprint`, `AGENTS.md`; where they differ, the repo wins.

## Start and lock
- After compaction the files, not memory, carry the loop: redo Start.
- One lock token per session, kept in the handoff. Another fresh token: stop unless `takeover` and the old session closed. Release only your own lock.
- A halt or `STOP` file means stop. Only the owner removes it.
- `.opencode/knobs.json` wins over numbers in `/sprint`. Never edit it; propose via a `KNOB PROPOSAL: <knob> <value> because <numbers>` line in the handoff (center's lead reads them each round).

## The batch
- The keeper names each batch: chain steps and one-offs first, then seats in fair turns, at most `heavy_max` CPU-heavy; also in the queue's `batch.md`.
- Send the whole list as ONE message of Task calls: `subagent_type` the role, `description` the title, `prompt` exactly `packet: <name>`. The keeper fills the text, so every helper runs at once, live, foreground. Never `background: true`. Send full width while eligible work exists; held seats rest, and a sent seat with nothing to do ends `RESULT: NOOP - <reason>` with proof, never filler.
- A packet has Goal, Scope, Proof, Stop, owned paths and a done-when, or the keeper refuses it. Every helper ends `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what> | proof: <where>`; BLOCKED and NOOP name the cause.
- Big work is split before dispatch, never given to one writer: a row over ~3 files or ~200 lines becomes N writer packets with disjoint owned paths (one writer per file per dispatch, group-per-dir owners so two writers never share a file). A writer that finishes early takes the next READY row (claim first) or sends its own helpers (up to the keeper cap) for independent pieces in disjoint files only.
- Re-read before editing: every writer re-reads its target files in the same packet and keeps oldString under ~30 lines copied from the latest read. A no-file-change run is re-scoped, never repeated or judged.
- When the batch returns, collect every result, then send the next batch same turn. A question you need now is one more Task in the batch. Never redo a helper's work.

## The chain
- A writer seat carries `chain: start`. Its DONE gets the judge's review atop the next batch, but only when the result changed files: no file change means no judge Task (collect-time drop, never a FAIL). Small same-area results share one review (up to 4 per judge Task); trivial probe/doc-only PASSes the lead lands after its own read, naming the proof.
- Every writer is judged independently before it lands. A FAIL gets one repair by the writer; a second FAIL or a BLOCKED comes to you. A PASS comes to you to commit: by path, never `-A`, one packet per file-set per round (serialize landing), the proof's one-line result in the commit body.
- A round that moved nothing says why. A finding is a packet, not an essay. Research lands only with source, license, row it feeds, spike.

## Commit
- Commit verified paths only. Never `git add -A`, another session's files, a secret or force-push.

## Tools on this box
- Shell is pwsh: prefer grep/glob/read tools; in shell `rg`, `Select-String`, `Get-Content -TotalCount/-Tail`, `Measure-Object`; cap big outputs.
- Edit: re-read exact lines just before editing; files are CRLF, copy oldString from the latest read.
- Research: read `.opencode/repomap.md` first, never list trees; deepwiki once then `gh api`; never guess raw.githubusercontent URLs — `gh api repos/O/R/contents/PATH` or `.../git/trees/HEAD?recursive=1`; rate-limit = authed `gh api`, not search.

## Grow (the point of the loop: agents, skills and repo get better and smaller)
- Drift first: a FAIL from the repo's checks is the first packet of the next batch. Never tick or close a row over a FAIL. Commit your own paths in the batch you edit them.
- Parts (only with a part-score tool and `team/`; else skip, never FAIL a missing score): each vision part has a score and a note `team/<part>.md` (tried, moved, failed). The part's builder aims at the score; the judge re-runs it; no rise and no stated reason is a FAIL.
- Steals: a scout works one part at a time (lowest score first), at most 3 licensed PINs per part, written under "Next steals" in the part's plan. No loose cards. An idea older than 5 days with no spike is archived. Tools and workspace are a part too.
- Skills: a non-obvious win adds at most 5 lines to the part's skill; a skill line that matches a FAILED note is deleted.
- Compact: every 5 rounds one compaction (finished rows, duplicate docs, stale ideas, dead code) with gates identical, logged in `team/compact-log.md` (or the handoff).
- Coach: every 5 rounds, one change to a seat, note or skill, undone if the score did not rise in 3 rounds. Rule sheets: `C:/Users/me/Desktop/center/crews/_shared/` (part-owner, scout, compactor, coach).

## Stop
- Ending a turn is not a stop. `[loop-keeper]` messages are not the owner.
- Stop only for the stop reasons in `/sprint`. Then write the handoff (lock token, what moved with SHAs, blockers, next), say PASS, PARTIAL or BLOCKED, release your lock and end `LOOP STOP: <reason>`.
- A loop-side stop is final: the keeper sends no review before it (overseer retired 2026-10-02).
