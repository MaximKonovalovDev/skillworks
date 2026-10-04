# DELIVERY O-025: order:fleet-vol-1-store-art-for-skillworks-cov for skillworks
1. Landing in skillworks: `packs/fleet-vol-1/from-design-studio/O-025/` (copy this whole folder; never edit a file outside from-design-studio/).
2. `out.png` 1280x720 = Gumroad cover; `out-630x500.png` = store card crop; `thumb-256.png` = readability proof at 256 px.
3. Source: `page.html` + `tokens.css` (art is CSS-only: 0 real pictures exist, the pack ships no preview/ images); `assets.json` lists each picture (none).
4. Gates: `brief.json` (+`system` clean), `design-audit.json` (audit PASS 23 gates), `DESIGN-REVIEW.md` (judge 10/10 SHIP), `VERDICT.md` (worker PASS, keeper chain pending); no `compare.png`: the listing says Not live, so no cover exists to beat.
5. Cover to beat: `none`; facts only from `C:/Users/me/Desktop/skillworks/packs/fleet-vol-1/listing.md`.
6. Adopt: commit these bytes in skillworks, then point the Gumroad listing at `out.png` (card: `out-630x500.png`).
7. Proof in skillworks: `git log -1 --format=%h -- packs/fleet-vol-1/from-design-studio/O-025/out.png`; here: `node tools/orders-check.mjs` and `node tools/audit.mjs designs/O-025/brief.json`.
8. Honest limits: the listing's demo GIF (10-20 s screen capture, grep fails then Select-String) and 3 screenshots (1280x800) are still open in skillworks; this folder covers only the PNG cover art.
9. Tool gaps worked around by hand: `tools/donor.mjs`, `tools/compose.mjs` and `orders-check --built` have not landed, so system pick (clean), compare and proof ran through `tools/cover.mjs` instead; see NEED-05.
