"""Pre-install scan helper: verdict/confidence/findings over a local skill dir."""
import inspect
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from mcp_server import scan_helper as sh

ROOT = Path(__file__).resolve().parent.parent

LONG_DESC = "A helpful test skill with a long enough description for the scan gate to pass without warnings."


def _make_skill(base, name, desc=LONG_DESC, lic="MIT", body="Body.", eval_doc=None, frontmatter=True):
    d = base / name
    d.mkdir(parents=True, exist_ok=True)
    if frontmatter:
        lines = ["---", "name: " + name]
        lines.append("description: " + desc)
        if lic is not None:
            lines.append("license: " + lic)
        lines += ["---", "", "# " + name, "", body, ""]
        (d / "SKILL.md").write_text(chr(10).join(lines), encoding="utf-8")
    else:
        (d / "SKILL.md").write_text("# " + name + chr(10) + chr(10) + body + chr(10), encoding="utf-8")
    if eval_doc is not None:
        (d / "eval_report.json").write_text(json.dumps(eval_doc), encoding="utf-8")
    return d


def _good_eval(name, rate=0.8):
    return {"skill": name, "total": 10, "passed": 8, "rate": rate}


def test_report_shape_and_keys(tmp_path):
    d = _make_skill(tmp_path, "demo", eval_doc=_good_eval("demo"))
    rep = sh.scan_skill(d)
    assert set(("skill", "verdict", "confidence", "summary", "guidance", "findings")) <= set(rep)
    assert rep["skill"] == "demo"
    assert rep["verdict"] in ("pass", "warn", "fail")
    assert isinstance(rep["confidence"], float) and 0.0 <= rep["confidence"] <= 1.0
    assert isinstance(rep["summary"], str) and rep["summary"]
    assert isinstance(rep["guidance"], str) and rep["guidance"]
    checks = [f["check"] for f in rep["findings"]]
    assert checks == ["frontmatter", "license", "eval-report"]
    for f in rep["findings"]:
        assert set(("check", "severity", "message")) <= set(f)
        assert f["severity"] in ("info", "warn", "error")
        assert f["message"]


def test_pass_on_good_tmp_skill(tmp_path):
    d = _make_skill(tmp_path, "demo", eval_doc=_good_eval("demo", 0.8))
    rep = sh.scan_skill(d)
    assert rep["verdict"] == "pass"
    assert rep["confidence"] == 0.95
    assert all(f["severity"] == "info" for f in rep["findings"])
    assert "ready to install" in rep["summary"]
    assert rep["guidance"] == "Proceed with install."


def test_pass_on_real_skill():
    d = ROOT / "skills" / "pipe-run"
    rep = sh.scan_skill(d)
    assert rep["verdict"] == "pass", sh.format_scan(rep)
    assert rep["confidence"] == 0.95
    assert all(f["severity"] == "info" for f in rep["findings"])


def test_missing_frontmatter_is_fail(tmp_path):
    d = _make_skill(tmp_path, "demo", frontmatter=False, eval_doc=_good_eval("demo"))
    rep = sh.scan_skill(d)
    assert rep["verdict"] == "fail"
    assert rep["confidence"] == 0.90
    fm = [f for f in rep["findings"] if f["check"] == "frontmatter"][0]
    assert fm["severity"] == "error"
    assert "frontmatter" in fm["message"].lower()
    assert "do not install" in rep["guidance"].lower()


def test_name_mismatch_is_fail(tmp_path):
    d = tmp_path / "demo"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(chr(10).join(["---", "name: other", "description: " + LONG_DESC, "license: MIT", "---", "", "# demo", ""]), encoding="utf-8")
    (d / "eval_report.json").write_text(json.dumps(_good_eval("demo")), encoding="utf-8")
    rep = sh.scan_skill(d)
    assert rep["verdict"] == "fail"
    fm = [f for f in rep["findings"] if f["check"] == "frontmatter"][0]
    assert fm["severity"] == "error"
    assert "other" in fm["message"] and "demo" in fm["message"]


def test_missing_license_is_warn(tmp_path):
    d = _make_skill(tmp_path, "demo", lic=None, eval_doc=_good_eval("demo"))
    rep = sh.scan_skill(d)
    assert rep["verdict"] == "warn"
    assert rep["confidence"] == 0.65
    lic = [f for f in rep["findings"] if f["check"] == "license"][0]
    assert lic["severity"] == "warn"
    assert "licence" in lic["message"].lower() or "license" in lic["message"].lower()


def test_missing_eval_report_is_warn(tmp_path):
    d = _make_skill(tmp_path, "demo", eval_doc=None)
    rep = sh.scan_skill(d)
    assert rep["verdict"] == "warn"
    ev = [f for f in rep["findings"] if f["check"] == "eval-report"][0]
    assert ev["severity"] == "warn"
    assert "eval" in ev["message"].lower()


def test_low_eval_rate_is_warn(tmp_path):
    d = _make_skill(tmp_path, "demo", eval_doc=_good_eval("demo", 0.2))
    rep = sh.scan_skill(d)
    assert rep["verdict"] == "warn"
    ev = [f for f in rep["findings"] if f["check"] == "eval-report"][0]
    assert ev["severity"] == "warn"
    assert "0.20" in ev["message"] and "0.6" in ev["message"]


def test_format_prints_severity_before_verdict(tmp_path):
    d = _make_skill(tmp_path, "demo", lic=None, eval_doc=None)
    rep = sh.scan_skill(d)
    text = sh.format_scan(rep)
    assert "[WARN]" in text
    assert "[INFO]" in text
    assert "verdict: WARN" in text
    assert "guidance:" in text
    first_finding = text.index("[")
    assert text.index("verdict:") > first_finding
    assert text.index("guidance:") > text.index("verdict:")
    assert "demo" in text or "needs review" in text


def test_cli_exit_codes(tmp_path):
    good = _make_skill(tmp_path / "g", "demo", eval_doc=_good_eval("demo"))
    warn = _make_skill(tmp_path / "w", "demo2", lic=None, eval_doc=None)
    bad = _make_skill(tmp_path / "b", "demo3", frontmatter=False, eval_doc=None)
    with redirect_stdout(io.StringIO()):
        assert sh.main([str(good)]) == 0
    with redirect_stdout(io.StringIO()):
        assert sh.main([str(warn)]) == 1
    with redirect_stdout(io.StringIO()):
        assert sh.main([str(bad)]) == 2


def test_missing_dir_is_fail(tmp_path):
    rep = sh.scan_skill(tmp_path / "nope-missing")
    assert rep["verdict"] == "fail"
    assert rep["findings"] and rep["findings"][0]["severity"] == "error"


def test_stdlib_only_and_attribution():
    src_path = ROOT / "mcp_server" / "scan_helper.py"
    text = src_path.read_text(encoding="utf-8")
    assert "openclaw/clawhub" in text
    assert "MIT" in text
    assert "https://github.com/openclaw/clawhub/blob/d044664a7636ec74b0092aa13fc0fcad1e660121/packages/clawhub/src/cli/commands/scan.ts" in text
    assert "no donor code copied" in text.lower() or "no code copied" in text.lower()
    src = inspect.getsource(sh.scan_skill) + inspect.getsource(sh.format_scan) + inspect.getsource(sh.main) + inspect.getsource(sh._check_eval_report) + inspect.getsource(sh._check_frontmatter)
    for token in ("urlopen", "requests", "httpx", "http.client", "socket", "urllib"):
        assert token not in src, token
    assert "SKILL.md" in src
    assert "eval_report.json" in src
