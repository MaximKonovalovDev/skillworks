# Attribution: snapshot pattern ported from syrupy-project/syrupy@7dc8f88
# (MIT licence, https://github.com/syrupy-project/syrupy). Syrupy keeps a
# SnapshotAssertion that discovers-or-creates a stored value and compares or
# rewrites it behind an update flag, with SingleFileSnapshotExtension holding
# one verbatim golden file. This file rebuilds that shape in this repo style
# with stdlib only. No donor code copied.
# Donor files: src/syrupy/assertion.py + src/syrupy/extensions/single_file.py
# (https://raw.githubusercontent.com/syrupy-project/syrupy/7dc8f88a0b039467f808d40b9ccbf7b93488af69/src/syrupy/assertion.py)
"""Stdlib-only snapshot harness: golden-compare freezing SKILL.md + proof."""
import difflib
import json
import os
import subprocess
import sys
from pathlib import Path

GOLDEN_SKILL = Path(__file__).with_name("test_steal_snapshot.skill.md")
GOLDEN_PROOF = Path(__file__).with_name("test_steal_snapshot.proof.json")


def _render_skill_md() -> bytes:
    text = (
        "---\n"
        "name: snapshot-demo\n"
        "description: Use when testing snapshot harness.\n"
        "---\n"
        "\n"
        "# Snapshot Demo\n"
        "\n"
        "Body line one.\n"
        "Body line two.\n"
    )
    return text.encode("utf-8")


def _render_trial_proof() -> bytes:
    record = {
        "fingerprint": "ab" * 32,
        "lift": 0.5,
        "runs": 12,
        "spread": 0.5,
        "with_rate": 0.75,
        "without_rate": 0.25,
    }
    return (json.dumps(record, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _snapshot_status(actual: bytes, golden: Path) -> int:
    """Compare bytes against a verbatim golden file; 0 match, 1 mismatch.

    Rewrites the golden only when env SNAPSHOT_UPDATE=1 (discover-or-create
    plus compare-or-write-behind-update-flag).
    """
    if os.environ.get("SNAPSHOT_UPDATE") == "1":
        golden.write_bytes(actual)
        print(f"updated {golden.name}")
        return 0
    if not golden.exists():
        print(f"missing golden {golden.name}: rerun with SNAPSHOT_UPDATE=1")
        return 1
    expected = golden.read_bytes()
    if actual == expected:
        return 0
    want = expected.decode("utf-8", "replace").splitlines()
    got = actual.decode("utf-8", "replace").splitlines()
    for line in difflib.unified_diff(want, got, str(golden.name), "actual"):
        print(line)
    return 1


def _assert_snapshot(actual: bytes, golden: Path) -> None:
    if _snapshot_status(actual, golden) != 0:
        raise SystemExit(1)


def test_skill_md_render_matches_golden(monkeypatch) -> None:
    monkeypatch.delenv("SNAPSHOT_UPDATE", raising=False)
    _assert_snapshot(_render_skill_md(), GOLDEN_SKILL)


def test_trial_proof_shape_matches_golden(monkeypatch) -> None:
    monkeypatch.delenv("SNAPSHOT_UPDATE", raising=False)
    _assert_snapshot(_render_trial_proof(), GOLDEN_PROOF)


def test_update_flag_rewrites_golden(tmp_path, monkeypatch) -> None:
    golden = tmp_path / "demo.golden"
    golden.write_bytes(b"old\n")
    monkeypatch.setenv("SNAPSHOT_UPDATE", "1")
    assert _snapshot_status(b"new\n", golden) == 0
    assert golden.read_bytes() == b"new\n"
    monkeypatch.delenv("SNAPSHOT_UPDATE", raising=False)
    assert _snapshot_status(b"new\n", golden) == 0
    assert _snapshot_status(b"other\n", golden) == 1


def test_deliberate_mismatch_exits_1(monkeypatch) -> None:
    import pytest

    monkeypatch.delenv("SNAPSHOT_UPDATE", raising=False)
    bad = b"deliberately wrong\n"
    assert _snapshot_status(bad, GOLDEN_SKILL) == 1
    with pytest.raises(SystemExit) as exc:
        _assert_snapshot(bad, GOLDEN_SKILL)
    assert exc.value.code == 1
    env = {k: v for k, v in os.environ.items() if k != "SNAPSHOT_UPDATE"}
    probe = (
        "import sys;"
        f"sys.exit(0 if open(r'{GOLDEN_SKILL}', 'rb').read() == {bad!r} else 1)"
    )
    done = subprocess.run([sys.executable, "-c", probe], capture_output=True, env=env)
    assert done.returncode == 1
