# tests

The pytest suite for the book2skill package, the tools and the skills.

- Run all: `python -m pytest tests/ -q`
- One file per area, named `test_<area>.py`. For example `test_export_guard.py` and `test_edit_guard.py`.
- Shared helpers (not tests): `skill_stock.py` (the stock tests every fleet skill repeats), `skill_gates.py` (points to `book2skill/gates.py`), `live_proof.py` (runs the live tests of the fleet skills and records a proof).
- Open first: `skill_stock.py`, then the `test_*.py` for the part you change.
- A claim counts only with the one-line test result in the commit body.
