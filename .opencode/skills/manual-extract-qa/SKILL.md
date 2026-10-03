---
name: manual-extract-qa
description: Use when running book2skill extract or split on a manual and you must prove the text is complete, tables survived, and sources are licit before build.
---

# Manual Extract QA

Extraction is guilty until proven innocent: prove completeness, table
fidelity, and license BEFORE `build`. Only owned or public-domain
sources; Gutenberg downloads stay in `work/`, never committed.

## 1. Source triage

- Owned or public-domain only. Copyrighted books are rejected at intake.
- Record origin in `work/<name>/receipt.json` with counts (pages,
  chunks, tables) at every stage.

## 2. Format checks

```powershell
python -m book2skill extract --in <src> --out work/<name>
python -m book2skill split --work work/<name>
```

- PDF: page-break map sane, no merged chapters, headings intact.
- DOCX: tables walked cell by cell, order preserved, no dropped rows.
- EPUB: nav body only, no heavy front/back matter duplication.
- Gutenberg: start/end markers stripped, boilerplate gone.

## 3. Completeness proof

- Chunk counts in receipt match source size order-of-magnitude.
- Spot-check 3 passages: source sentence appears verbatim in chunks.
- Glossary terms and code blocks present, not summarized away.
- `split` chunk sizes within the tested bounds (`test_split_chunk_sizes`).

## 4. Hand to build

Only when receipts, spot-checks, and `python -m pytest tests/ -q` pass:
`python -m book2skill index --work work/<name>`, then build. A QA note
with counts lands beside the receipt.

## Do not

- Feed a source with unclear rights. Commit `work/` books. Rebuild to
  hide extraction loss; refresh no-ops only on matching fingerprints.
Source: https://github.com/VoltAgent/awesome-claude-code-subagents (MIT, fetched 2026-10-03)
