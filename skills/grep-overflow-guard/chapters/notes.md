# Grep overflow notes (DR-1007-18)

Class: `Grep` JSON-overflow misses, 29 in 48 h in 8 repos (center 14 plus
works 5 plus jobhunt 3 plus video-studio 2 plus engine2040 2 plus asset-vault 1
plus forge 1 plus skillworks 1), 0 loads for the new name, scan generatedAt
2026-10-08T07:41Z. Distinct from BK-1007-1 (ripgrep precision) and BK-1007-4
(fd file-find scoping): this skill owns only the overflow fallback to a
chunked narrow search.

## What fails

A whole-tree or unfiltered `Grep` call comes back with
`Ripgrep JSON record exceeded N bytes`. The recorded shape splits six ways:
wide scope with no folder (gl8-b01), unfiltered search with no file-type
filter (gl8-b02), no glob over the whole repo (gl8-b03), one single call over
many folders (gl8-b04), unbounded hits with no limit (gl8-b05), broad regex
with no literal (gl8-b06).

## What fixes it

Narrow the scope to one folder first, add a file-type filter or a glob,
switch a broad regex to its exact literal, rerun chunked folder by folder,
merge the hits, and report chunk results plus merged hits plus what is still
unverified with PASS. The graded sweep is gl8-b01 to gl8-b06 plus gl8-g01 to
gl8-g06 in `evals/grep-overflow-guard_trials.jsonl`; the live pairs are
`references/pairs.json`.
