# freud-dream-psychology — listing draft (Vol 1, DRAFT — not shipped)

> Status: PREP-ONLY draft. Not shipped until the Delivery evidence bar in
> `VISION.md` is met. The store upload is the factory's or Maxim's; there is
> no `Live listing:` URL yet, so `python tools/finish_proof.py s3` stays open.

- Skill: `skills/freud-dream-psychology/` (eval 10/12 = 0.833, gate 0.6 passes, ships)
- Source: Sigmund Freud, The Interpretation of Dreams. First German edition 1900; English translation by A. A. Brill (Translator line, Macmillan 1913 — see `work/freud-dreams/src.txt` lines 15, 24). Source text stays in `work/` (gitignored, never committed).
- Public-domain basis: author died 1939; US edition 1913, so public domain in the US. Gutenberg ebook #66048 carries the same Brill text under the Project Gutenberg License (free to copy, give away, re-use).
- Price: Vol 0 free. Full-pack price set at listing time by the factory/Maxim (PREP-ONLY: no paid ship from this repo, no fee numbers as fact).
- Price evidence (sellers' own pages, read 2026-10-03, ideas only, never pasted):
  - Source free: `https://www.gutenberg.org/ebooks/66048` — Gutenberg page for this exact Brill text, $0, no restrictions beyond the Gutenberg License.
  - Listing shape reference: itch.io seller-page shape (Status / Category / tags / Files name+size block) and Gumroad adding-a-product outline (type → price → description → content) — structure observed, not copied; homes `skills/progit-branching/listing.md` pattern (research/cards/2026-10-03-S19.md).
  - Take-home math, if a paid Vol 1 is ever listed, is recomputed from the live store's own fee page on that date (S19 Card 3: re-check official pages before relying).
- Sales: **0** (honest counter — stays 0 until a real sale).
- Vol 0 free sample: [`vol0-sample.md`](vol0-sample.md) — dream-work excerpt (condensation, displacement, manifest/latent, censorship), free to share, no purchase needed.
- Demo: text try-it below (no `demo/demo.gif` yet — GIF-first demo lands with the factory upload, or the Demo line stays absent; no placeholder pixels shipped).
- Install (Claude target): copy `export/claude/freud-dream-psychology/` into your skill dir; SKILL.md at root. Other targets: `export/codex|opencode|gemini/`. ZIP artifact (K-41): `out/<target>/freud-dream-psychology.zip` with SKILL.md at root, regenerated on demand via `python -m book2skill export`.
- Try it (15-min check): ask what condensation does to latent dream-thoughts; ask how displacement shifts intensity to the manifest content; ask what censorship distorts — all answerable from the Vol 0 sample, no book needed.
- Status: draft (PREP-ONLY, not shipped).
- Category: psychology dream-interpretation how-to.
- Tags: freud, dreams, psychoanalysis, condensation, displacement.
- Marketplace (skills-manager shape, own words, honest zeros until listed):
  - author: skillworks (PREP-ONLY draft, not yet a store author).
  - repository: none published yet (this repo path only).
  - stars: 0 (not listed, no stars).
  - weekly-installs: 0 (not listed, no installs).
- Files:
  - `vol0-sample.md` (1666 B, 2026-10-03) — free excerpt, no purchase needed.
  - `SKILL.md` — skill entry (PREP-ONLY draft).
  - `references/sources.md` — chunk index backing the cheatsheet.
  - `chapters/notes.md` — condensed chunk heads from the Brill text.
  - `out/claude/freud-dream-psychology.zip` — store-ready ZIP (SKILL.md at root, regenerated; never committed, `skills/*/export/` ignored).

## Changelog

- 2026-10-03: K-44 draft created (listing + Vol 0 sample + ZIP via export; freud 0.833 chosen over james 0.667; marketplace fields author/repository/stars/weekly-installs landed).
