# skillworks board

The only work list. Status: TOP, READY, DOING, BLOCKED, OWNER, DONE. A DONE row
names its commit SHA. Each row names the Scorecard row of `VISION.md` it moves.

| ID | Status | Scorecard row | What | Done when | Owner role | Evidence |
|---|---|---|---|---|---|---|
| K-01 | TOP | all | Fill the vision: Scorecard (5+ rows, 3+ real competitors), Parts, Open gaps, Steal map (10 competitors, 10 adjacent) | `node C:/Users/me/Desktop/center/vision-check.mjs skillworks` has no FAIL | planner | |
| K-02 | READY | the first part | First measurable slice of the vision | `python -m pytest tests/ -q` passes its first step, pasted in the commit | builder | |
| K-03 | READY | all | Split the vision into board rows, each with its proof command | 10+ READY rows, each naming its Scorecard row and proof | planner | |
| T-01 | READY | R1 book-to-skill in hours, with receipts | Steal skill-pack layout: progressive-disclosure SKILL.md + references/ (obra/superpowers, MIT, https://github.com/obra/superpowers) into build stage | `python -m pytest tests/ -q` green + seed skill rebuilt in new layout, receipted | researcher | target `book2skill/build.py` + `skills/<name>/` |
| T-02 | READY | R1 book-to-skill in hours, with receipts | Steal per-page PDF text extraction with order preserved (mozilla/pdf.js getTextContent pattern, Apache-2.0, https://github.com/mozilla/pdf.js) for the extract stage | `python -m pytest tests/ -q` green + extract receipt (pages, chars) on a PD test PDF | researcher | target `book2skill/extract.py` |
| T-03 | READY | R1 book-to-skill in hours, with receipts | Steal docx paragraph/table text walk (python-openxml/python-docx, MIT, https://github.com/python-openxml/python-docx) as second extract lane | `python -m pytest tests/ -q` green + extract receipt on a test docx | researcher | target `book2skill/extract.py` |
| T-04 | READY | R1 book-to-skill in hours, with receipts | Steal prompt-fragment discipline for the build stage (simonw/llm prompt-template pattern, Apache-2.0, https://github.com/simonw/llm) so chapter-to-skill prompts are versioned files, not inline strings | `python -m pytest tests/ -q` green + one build prompt moved to a versioned template file | researcher | target `book2skill/build.py` |
| T-05 | READY | R2 honest eval gate (Q&A pass rate blocks ship) | Steal signature-compiled QA generation for eval sets (stanfordnlp/dspy signatures pattern, MIT, https://github.com/stanfordnlp/dspy) to grow source-derived QA per skill | `python -m pytest tests/ -q` green + eval QA set grown from one chapter, pass rate logged | researcher | target `book2skill/eval.py` |
