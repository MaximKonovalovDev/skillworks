# packs

Packs for sale, and the proof that each one works.

- `fleet-vol-1/` - the first pack for sale. Holds `pack.json` (title, price, skills), the buyer README, the listing, the free Vol 0 sample and the price evidence.
- `mcp-template/` - an MCP server template, with `server.py`, `selftest.py` and a proof note `proof.md`.
- `catalog.md` - every tested pack in one list. A row lands only with its proof green.
- Other notes here: `free-vol0-publish-checklist.md`, `*-prep-*.md` (store prep) and `vol0-triage-*.md`.
- Open first: `catalog.md`, then `fleet-vol-1/pack.json`.
- Build the buyer files: `python tools/pack_build.py packs/<slug> --starter`.
- The ZIP is built into `dist/`, which is git-ignored.
- A pack ships only with its proof (see `VISION.md`, delivery evidence).
