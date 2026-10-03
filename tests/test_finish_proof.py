"""FINISH-LINE proofs for S2 (adoption in 5 repos) and S3 (a tested pack live on a store)."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import finish_proof as fp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def _csv(tmp_path: Path, rows: list[str]) -> Path:
    p = tmp_path / "adopted.csv"
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return p


def test_s2_counts_distinct_repos_that_adopted(tmp_path: Path) -> None:
    four = [f"2026-10-03,repo{i},pwsh-for-bash-writers,adopted,50,20" for i in range(4)]
    ok, msg = fp.s2(_csv(tmp_path, four + ["2026-10-03,repo0,git-one-branch,adopted,9,3", "2026-10-03,repo9,x,proposed,1,1"]))
    assert not ok and "4 repos" in msg  # a second skill in one repo and a proposal do not count
    ok, msg = fp.s2(_csv(tmp_path, four + ["2026-10-03,repo4,pwsh-for-bash-writers,adopted,50,20"]))
    assert ok and "5 repos" in msg


def test_s2_without_the_record_is_open(tmp_path: Path) -> None:
    ok, msg = fp.s2(tmp_path / "missing.csv")
    assert not ok and "no adopted.csv" in msg


def _pack(skills: Path, name: str, listing: str, rate: float | None) -> None:
    d = skills / name
    d.mkdir(parents=True)
    (d / "listing.md").write_text(listing, encoding="utf-8")
    if rate is not None:
        (d / "eval_report.json").write_text(json.dumps({"rate": rate}), encoding="utf-8")


def test_s3_needs_a_live_url_and_a_tested_pack(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    _pack(skills, "draft-pack", "# Listing\nstatus: PREP-ONLY\n", 0.9)
    ok, msg = fp.s3(skills)
    assert not ok and "no listing.md" in msg
    _pack(skills, "untested-pack", "Live listing: https://shop.example/untested\n", None)
    ok, msg = fp.s3(skills)
    assert not ok and "below" in msg
    _pack(skills, "good-pack", "# Listing\nLive listing: https://shop.example/good\n", 0.833)
    ok, msg = fp.s3(skills)
    assert ok and "good-pack" in msg  # an untested live listing earlier in name order does not hide a good one


def test_s3_met(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    _pack(skills, "good-pack", "# Listing\nLive listing: https://shop.example/good\n", 0.833)
    ok, msg = fp.s3(skills)
    assert ok and "good-pack" in msg and "https://shop.example/good" in msg


def test_command_line_exit_codes(tmp_path: Path) -> None:
    run = lambda *a: subprocess.run([sys.executable, str(ROOT / "tools" / "finish_proof.py"), *a], capture_output=True, text=True)  # noqa: E731
    assert run("nope").returncode == 2
    assert run("s2", str(tmp_path / "missing.csv")).returncode == 1
    assert run("s3", str(tmp_path)).returncode == 1
