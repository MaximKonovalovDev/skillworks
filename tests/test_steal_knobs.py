"""Steal knobs: unknown-key gate plus dead-knob set-vs-read scan in tools/knob_check.py."""
import json
import subprocess
import sys
from pathlib import Path

from tools import knob_check as kc

ROOT = Path(__file__).resolve().parent.parent
KNOBS = ROOT / ".opencode" / "knobs.json"
KEEPER = ROOT / ".opencode" / "plugin" / "loop-keeper.js"

EXPECTED_DEAD = {
    ("set-never-read", "paid_mode"),
    ("read-never-set", "repeat_cap"),
    ("read-never-set", "min_free_gb"),
    ("read-never-set", "fresh_ctx_k"),
}

GOOD_DEFINED = {
    "width": {"value": 1},
    "dispatch": {"value": "foreground"},
}

READER_JS = 'const w = knobValue("width");\nconst d = knobValue("dispatch");\n'


def _write_tree(tmp_path: Path, defined: dict) -> tuple[Path, Path]:
    knobs = tmp_path / "knobs.json"
    knobs.write_text(json.dumps({"knobs": defined}), encoding="utf-8")
    reader = tmp_path / "reader.js"
    reader.write_text(READER_JS, encoding="utf-8")
    return knobs, reader


def test_unknown_key_refused() -> None:
    defined = dict(GOOD_DEFINED, bogus_xyz={"value": 1})
    findings = kc.check_unknown_and_types(defined)
    assert any(f.kind == "unknown-key" and f.key == "bogus_xyz" for f in findings)


def test_type_mismatch_refused() -> None:
    findings = kc.check_unknown_and_types({"width": {"value": "wide"}})
    assert any(f.kind == "type-mismatch" and f.key == "width" for f in findings)


def test_real_knobs_four_dead_keys() -> None:
    defined = kc.read_defined(KNOBS)  # read-only; the protected file is never written
    reads = kc.scan_reads([KEEPER])
    dead = kc.cross_check(defined, reads)
    pairs = {(f.kind, f.key) for f in dead}
    assert pairs == EXPECTED_DEAD, [str(f) for f in dead]
    for finding in dead:
        if finding.kind == "read-never-set":
            assert ":" in finding.detail, str(finding)
    print("dead knobs: " + "; ".join(str(f) for f in dead))


def test_unknown_key_exits_2(tmp_path: Path) -> None:
    knobs, reader = _write_tree(tmp_path, dict(GOOD_DEFINED, bogus_xyz={"value": 1}))
    _, code = kc.check(knobs, [reader])
    assert code == 2


def test_dead_knob_exits_1_and_clean_exits_0(tmp_path: Path) -> None:
    knobs, reader = _write_tree(tmp_path, dict(GOOD_DEFINED, paid_mode={"value": 0}))
    _, code = kc.check(knobs, [reader])
    assert code == 1
    knobs.write_text(json.dumps({"knobs": GOOD_DEFINED}), encoding="utf-8")
    _, code = kc.check(knobs, [reader])
    assert code == 0


def test_cli_exit_code_and_finding_text(tmp_path: Path) -> None:
    knobs, reader = _write_tree(tmp_path, dict(GOOD_DEFINED, paid_mode={"value": 0}))
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "knob_check.py"),
         "--knobs", str(knobs), "--scan", str(reader)],
        capture_output=True, text=True, timeout=60, cwd=str(ROOT),
    )
    assert proc.returncode == 1, proc.stderr
    assert "set-never-read paid_mode" in proc.stdout, proc.stdout
