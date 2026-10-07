# Patterns: symptom to branch

Each recipe starts from a structured-data query miss the loop really makes, then names the one branch that fixes it. All replays ran on this PC on 2026-10-07.

## Blob grepped raw with no transform

Symptom: grep on raw JSON never shows the absolute path to a value.

- Gron first: gron turns each `JSON` document into `discrete assignments`, then `grep` finds the line and its absolute `path` (pair `gr-p01`).
- prints: `gron PASS discrete-assignments`

## Filtered lines never turned back

Symptom: the pipeline ends in assignment text where valid JSON belongs.

- Pipe the `filtered` lines through `gron --ungron` (`-u`) so they turn `back into JSON` (pair `gr-p02`).
- prints: `ungron PASS back-into-json`

## Reverse flag typed in full every time

Symptom: the long `--ungron` flag slows every round-trip.

- Use the `norg` `alias` (twin `ungron`) kept in `~/.bashrc`; each alias wraps `gron --ungron` (pair `gr-p03`).
- prints: `alias PASS norg-wraps-ungron`

## Full assignments where only values belong

Symptom: downstream steps choke on paths when they need right-hand sides.

- Pass `gron --values` (`-v`) to print `just the values` and drop the `path` (pair `gr-p04`).
- prints: `values PASS just-values`

## JSON lines parsed as one document

Symptom: line-delimited input fails as a single blob.

- Pass `gron --stream` (`-s`) so each line parses as a `separate JSON` object (pair `gr-p05`).
- prints: `stream PASS separate-json`

## Assignment text fed to a JSON tool

Symptom: a JSON consumer cannot read gron assignment lines.

- Pass `gron --json` (`-j`) to emit a `JSON stream` of path plus value pairs (pair `gr-p06`).
- prints: `json PASS json-stream`

## Keys appended by hand

Symptom: hand-built paths mix bare words, quoted keys, and indexes.

- Use the `statement` builders `withBare` (bare word), `withQuotedKey` (quoted key string), and `withNumericKey` (`int` index) (pair `gr-p07`).
- prints: `paths PASS three-builders`

## Pipeline fails with no stage named

Symptom: nobody can tell whether statement parsing or JSON encoding broke.

- Read the `Exit Codes` section: `Failed to parse` statements is code `5`, `Failed to encode` JSON is code `6` (pair `gr-p08`).
- prints: `errors PASS parse-stage-named`
