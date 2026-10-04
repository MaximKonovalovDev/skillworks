# ADOPT O-029 (skillworks): the Fleet Vol 1 pack sheet
1. Use `from-design-studio/O-029/out.pdf` (A4, one page) as the one-page sheet of the pack: attach it to the Gumroad listing or send it with the zip. `out.png` is the preview.
2. No skillworks file reads it, so no listing, manifest or pack.json line changes.
3. If a count in `packs/fleet-vol-1/listing.md` changes (price, proof counts, version), change that slot in `page.html` and print again; `FACTS.md` lists each number and its line.
4. Your proof: `python tools/pack_check.py packs/fleet-vol-1` (from its board rows).
