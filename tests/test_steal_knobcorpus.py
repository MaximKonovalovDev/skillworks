"""Knob valid/invalid corpus: valid exit 0, invalid exit 2 with fragment."""
# Steal (pattern only, fresh code): toml-lang/toml-test@ff49d10, MIT,
# valid must pass / invalid must fail split after runner.go valid/invalid split,
# their tests/valid + tests/invalid + runner.go
# (https://github.com/toml-lang/toml-test/tree/ff49d109861c1ad25af53f687f2aef19ab650600/tests).
# Our target: tools/knob_check.py. No parser code borrowed.
import json
from pathlib import Path

from tools import knob_check as kc

ROOT = Path(__file__).resolve().parent.parent
VALID_DIR = ROOT / "tests" / "fixtures" / "knobs" / "valid"
INVALID_DIR = ROOT / "tests" / "fixtures" / "knobs" / "invalid"

INVALID_EXPECTED = {
    "unknown_key.json": "unknown-key bogus_xyz",
    "width_string.json": "type-mismatch width",
    "dispatch_int.json": "type-mismatch dispatch",
    "width_bool.json": "type-mismatch width",
    "min_free_gb_string.json": "type-mismatch min_free_gb",
    "heavy_max_string.json": "type-mismatch heavy_max",
}

def test_corpus_counts() -> None:
    valid = sorted(VALID_DIR.glob("*.json"))
    invalid = sorted(INVALID_DIR.glob("*.json"))
    assert len(valid) == 3, [p.name for p in valid]
    assert len(invalid) == 6, [p.name for p in invalid]

def test_valid_corpus_exits_0() -> None:
    for path in sorted(VALID_DIR.glob("*.json")):
        findings, code = kc.run_corpus_file(path)
        assert code == 0, [str(f) for f in findings]
        assert findings == []

def test_invalid_corpus_exits_2_with_fragment() -> None:
    assert len(list(INVALID_DIR.glob("*.json"))) == len(INVALID_EXPECTED)
    for name, fragment in sorted(INVALID_EXPECTED.items()):
        path = INVALID_DIR / name
        assert path.is_file(), name
        findings, code = kc.run_corpus_file(path)
        assert code == 2, [str(f) for f in findings]
        text = " ".join(str(f) for f in findings)
        assert fragment in text, text
        assert (path.name + ":1") in text, text

def test_corpus_dirs_sweep_clean() -> None:
    errors = kc.run_corpus_dirs(VALID_DIR, INVALID_DIR)
    assert errors == [], errors

def test_valid_json_shapes() -> None:
    for path in sorted(VALID_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(raw.get("knobs"), dict), path.name
