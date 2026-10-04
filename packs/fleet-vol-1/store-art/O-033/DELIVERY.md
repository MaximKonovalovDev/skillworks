# DELIVERY O-033: order:demo-gif-for-fleet-vol-1-a-bad-command-t for skillworks
1. Landing in skillworks: `packs/fleet-vol-1/from-design-studio/O-033/` (copy this whole folder; never edit a file outside from-design-studio/).
2. `demo.gif` 480x288 15s 30 frames 167382B + `demo.gif.json` (real pwsh: grep fails, Select-String finds it); `out.png` 1280x720 + `out-630x500.png` poster + `thumb-256.png`.
3. Source: `page.html` + `tokens.css` + `assets/shot.png` (factory fleet-pack screenshot-pairs.png, same Fleet Vol 1 content); `assets.json` carries source path and sha256.
4. Gates: `brief.json` (+`system` developer), `design-audit.json` (audit PASS), `DESIGN-REVIEW.md` (judge 10/10 SHIP); no `compare.png`: there is no cover to beat.
5. Cover to beat: `none`; facts only from `C:/Users/me/Desktop/skillworks/packs/fleet-vol-1/listing.md` (PowerShell 7, grep fails, Select-String, $19, Vol 0).
6. Adopt: commit these bytes in skillworks, then point the listing demo slot at `demo.gif` (poster: `out.png`, card: `out-630x500.png`).
7. Proof here: `node tools/orders-check.mjs --built O-033` (BUILT PASS) and `node tools/gifcap.mjs --demo --out designs/O-033/demo.gif` (GIFCAP PASS, real session).
8. Honest limits: brief asked 10s 1280x720 GIF; the gifcap gate renders 480x288 15s, so stickers and GIF say 15s 480x288, not 1280x720.
9. Tool gaps by hand: `tools/donor.mjs` missing (system developer picked by eye) and `assets.mjs` has no Facts path for O-033 (picture copied from factory preview by path); see NEED-08.
