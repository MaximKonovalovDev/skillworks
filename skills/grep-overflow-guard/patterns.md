# Patterns

- Narrow then chunk then merge: one folder, file-type filter, per-folder chunks, merged hits.
- Filter then rerun: include or glob or exact literal first, rerun chunked, report PASS.
- Split then count: per-folder chunks, merge the counts, state what is unverified.
- Miss then report: scope plus filter plus chunks plus merged hits in one closing block.
