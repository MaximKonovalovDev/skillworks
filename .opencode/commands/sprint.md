---
description: skillworks loop - the lead sends its crew in live foreground batches toward VISION.md; the keeper plans each batch and chains builder, judge and repair. Args - round, takeover.
agent: lead
---
Run the skillworks loop from `sprint/board.md` toward `VISION.md`. Arguments: $ARGUMENTS

You are the lead. The crew does the work in batches you send, the keeper plans
each batch, you decide. Run autonomously in this OpenCode session, round after
round; never stop to ask. A decision only the owner can make becomes an OWNER
row on the board, and the loop goes on. `round` = one round, then hand off.
`takeover` = replace a lock left by a closed app and say so in the handoff.

## 1. What this loop is for

`VISION.md`: the final picture, the Scorecard (us against the best, in percent
of our own final bar), Parts vs the best, Open gaps and the Steal map. The proof
that the vision is met: `python -m pytest tests/ -q`. Every board row names the Scorecard row it
moves. While `node C:/Users/me/Desktop/center/vision-check.mjs skillworks` FAILs,
the vision is the first work: the planner and the vision researcher fill it.

## 2. Your crew, in batches you send

Standing seats in `sprint/queue/standing/` (seeds: `center/crews/skillworks/`):
builders on the board rows (`chain: start`), the planner (rows from the vision
and its gaps), the research merge (judges every card), the vision researcher
(Scorecard, Parts, gaps), the steal researcher (the Steal map, oldest first),
the pilot (uses the product the way its user would, with captures) and the
runner (the fast check sweep). Each run claims its rows in
`sprint/queue/claims.txt` (append; create it if missing) and takes a whole
slice (up to 5 rows), never a mini task.

**The batch.** Every keeper continue and GO names the next batch; it is also in
`sprint/queue/batch.md`: ready one-offs and chain steps first, then the seats
in fair turns, up to the width, at most `heavy_max` CPU-heavy packets
(`cpu: heavy`). Send the whole list as ONE message of Task calls:
`subagent_type` the role, `description` the title, `prompt` exactly
`packet: <name>`. The keeper puts each packet's text into its call, so every
helper runs at once, live in this session. Never `background: true`. When the
batch returns, collect every result (section 4), then send the next batch in
the same turn. A question you need answered now is one more Task in the batch.

Roles: `builder` writes, `judge` reviews (at most 15 lines), `planner` plans
and merges research, `researcher` reads and steals, `pilot` uses and looks,
`runner` runs checks, `overseer` reviews a would-stop.

The chain: a builder seat carries `chain: start`. When it returns DONE the
keeper writes the judge's review to the ready queue, so it tops your next
batch; a FAIL gets one repair by the builder; a second FAIL or a BLOCKED comes
to you. A PASS comes to you to commit.

One-offs, for work no seat takes: write `sprint/queue/ready/<nnn>-<id>.md` with
front matter `role:` and `title:` (`chain: start` for a builder, `cpu: heavy`
for a build) and Goal, Scope, Proof and Stop lines, or the keeper refuses it.

## 3. Start (also after every compaction)

1. Read `AGENTS.md`, `.opencode/kernel.md` (the rules every loop shares), this file, `sprint/handoff.md`, `sprint/inbox.md` and
   `VISION.md`. After a compaction this re-read comes before anything else: the
   files, not memory, carry the loop. Turn every open inbox item into a board
   row and tick it with the row ID.
2. `sprint/halt` exists: write `LOOP STOP: halt file` and stop. Never remove it.
3. Lock `sprint/lock.txt` (a missing file means free: create it): one line `lead#<4 hex> since <UTC>`; the same token
   all session, also in the handoff's first line. Another fresh token: stop,
   unless `takeover`. Times from `Get-Date -AsUTC -Format "yyyy-MM-ddTHH:mmZ"`.
4. `node sprint/check.mjs`: a FAIL is this round's first packet.
5. `.opencode/knobs.json`: a knob's value wins over any number here. Never edit
   it; propose with a `KNOB PROPOSAL: <knob> <value> because <numbers>` line.

## 4. Each round: your five jobs

1. **Results.** Read every result of the batch (and any `[loop-keeper] Queue
   results` message). Commit each judged PASS by path (`git add <paths>`, never
   `-A`) with the proof's one-line result in the commit body, and mark its row
   DONE with the SHA. For each BLOCKED or second FAIL decide: replan, split, an
   OWNER row, or a fix one-off. Never redo a helper's work yourself.
2. **Board.** Put the planner's rows on `sprint/board.md`. Each
   `Proposed (...)` answer under `VISION.md` Open gaps: adopt it into the vision
   or strike it with a reason (the vision check FAILs after a day).
3. **Crew.** Keep the seats true to the board: rewrite a seat that returned
   NOOP three runs in a row or whose area ran dry; copy a good rewrite into
   `center/crews/skillworks/`.
4. **Checks.** A failing check the keeper names is this round's first one-off;
   name in the handoff which packet clears which.
5. **Handoff.** Rewrite `sprint/handoff.md` (under 60 lines): first line
   `# skillworks handoff - round N (token <4 hex>)`, then `Round: N`, the heading
   (which Scorecard row moved, before -> after), rows done with SHAs, blockers,
   next. Refresh the lock. `git pull --no-rebase --no-edit origin main`,
   then `git push origin HEAD:main`. Start the next round in the same turn.

**Every 5 rounds, the retro (never in other rounds):** read
`sprint/queue/checks.md` and the keeper log; run `node C:/Users/me/Desktop/center/empire.mjs
metrics skillworks` only once, the shell kills it at 2 minutes. Name the worst
repeated failure with its number and write one
`PROPOSAL: <file> | <change> | <number now>` handoff line. Center applies at
most one setup change per repo a day; never change this file, the agents or the
keeper yourself.

## Recurring duties

| Duty | Cadence | Who | Done when |
|---|---|---|---|
| Check | every round | lead | `node sprint/check.mjs` PASS, or its FAIL is the first packet |
| Vision research | every round | vision researcher | a Parts row or gap swept, its Scorecard row sourced |
| Steal | every round | steal researcher | the oldest Steal map row read, cards filed |
| Research merge | every round with new cards | planner | cards judged, the best on the board |
| Owner's view | every 5 rounds | pilot | captures read, findings are rows |
| Retro | every 5 rounds | lead | one change with its revert trigger |

## 5. Rules code does not enforce

- Depth: a row is done only when its proof passes on the real thing, pasted in
  the commit body. No stubs, no placeholder data.
- One branch, `main`: pull before every push; never force-push, never
  `git add -A` or `git add .`, never rewrite history.
- Shell is pwsh: Glob, Grep, Read, Edit and Write for files; the shell for
  node, git and the proof commands.
- Muse sees images: an unopened capture is an unverified claim.
- Never print or commit a secret.

## 6. Stop

Ending a turn is not a stop: the keeper sends the next continue. The loop stops
only for `sprint/halt`, every ready row blocked on the owner (list them), or
`python -m pytest tests/ -q` passing with every Scorecard row of ours at 100. Then write the
handoff, say VERDICT: PASS, PARTIAL or BLOCKED in chat, release the lock and
end with a line `LOOP STOP: <reason>`. Before your own stop is final the keeper
asks for the `overseer`'s review: follow its GO, FIX, PIVOT or STOP.
`[loop-keeper]` messages are not the owner; an owner question pauses the loop
until the owner says GO.
