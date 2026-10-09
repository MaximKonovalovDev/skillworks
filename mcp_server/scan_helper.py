"""Pre-install skill scan: verdict/confidence/summary/guidance/findings.

Pattern steal (ideas only, no code copied): openclaw/clawhub@d044664 (MIT,
https://github.com/openclaw/clawhub/blob/d044664a7636ec74b0092aa13fc0fcad1e660121/packages/clawhub/src/cli/commands/scan.ts)
scan verdict/confidence/summary/guidance/findings with severity printed
before install. Written fresh in our style; no donor code copied.

Stdlib-only, local-only: walks one local skill dir (SKILL.md frontmatter
present, licence declared, eval report present). No network, no deps.
Prints severity lines before the verdict so the caller decides install.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VERDICT_PASS = "pass"
VERDICT_WARN = "warn"
VERDICT_FAIL = "fail"
VERDICTS = (VERDICT_PASS, VERDICT_WARN, VERDICT_FAIL)

SEVERITY_INFO = "info"
SEVERITY_WARN = "warn"
SEVERITY_ERROR = "error"
SEVERITIES = (SEVERITY_INFO, SEVERITY_WARN, SEVERITY_ERROR)

CHECK_FRONTMATTER = "frontmatter"
CHECK_LICENSE = "license"
CHECK_EVAL_REPORT = "eval-report"

EVAL_GATE = 0.6
DESCRIPTION_MIN = 20

CONFIDENCE_PASS = 0.95
CONFIDENCE_WARN = 0.65
CONFIDENCE_FAIL = 0.90


def _parse_frontmatter(text: str) -> dict | None:
    """Return lower-cased frontmatter map, or None when no block present."""
    if not isinstance(text, str) or not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    head = parts[1]
    if not head.strip():
        return None
    meta: dict[str, str] = {}
    for line in head.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip().strip("'\"")
        if key:
            meta[key] = val
    return meta


def _finding(check: str, severity: str, message: str) -> dict:
    return {"check": check, "severity": severity, "message": message}


def _check_frontmatter(skill_dir: Path, skill_name: str, meta: dict | None, has_skill_md: bool) -> dict:
    if not has_skill_md:
        return _finding(CHECK_FRONTMATTER, SEVERITY_ERROR, "SKILL.md missing in '" + skill_name + "'; cannot install without an entrypoint")
    if meta is None:
        return _finding(CHECK_FRONTMATTER, SEVERITY_ERROR, "frontmatter missing in '" + skill_name + "/SKILL.md'; expected --- name/description block")
    name = (meta.get("name") or "").strip()
    desc = (meta.get("description") or "").strip()
    if not name:
        return _finding(CHECK_FRONTMATTER, SEVERITY_ERROR, "frontmatter missing required 'name'")
    if name != skill_name:
        return _finding(CHECK_FRONTMATTER, SEVERITY_ERROR, "frontmatter name '" + name + "' != dir '" + skill_name + "'")
    if not desc:
        return _finding(CHECK_FRONTMATTER, SEVERITY_ERROR, "frontmatter missing required 'description'")
    if len(desc) < DESCRIPTION_MIN:
        return _finding(CHECK_FRONTMATTER, SEVERITY_WARN, "frontmatter description too short (" + str(len(desc)) + " chars < " + str(DESCRIPTION_MIN) + "); expand before install")
    return _finding(CHECK_FRONTMATTER, SEVERITY_INFO, "frontmatter ok: name '" + name + "' with description (" + str(len(desc)) + " chars)")


def _check_license(meta: dict | None) -> dict:
    if meta is None:
        return _finding(CHECK_LICENSE, SEVERITY_ERROR, "cannot verify licence: frontmatter missing")
    lic = (meta.get("license") or meta.get("licence") or "").strip()
    if not lic:
        return _finding(CHECK_LICENSE, SEVERITY_WARN, "licence not declared: add 'license: MIT' (or the real licence) to SKILL.md frontmatter")
    return _finding(CHECK_LICENSE, SEVERITY_INFO, "licence declared: " + lic)


def _check_eval_report(skill_dir: Path, skill_name: str) -> dict:
    report_path = skill_dir / "eval_report.json"
    if not report_path.is_file():
        return _finding(CHECK_EVAL_REPORT, SEVERITY_WARN, "eval report missing: '" + skill_name + "/eval_report.json' not found; run eval before install")
    try:
        doc = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return _finding(CHECK_EVAL_REPORT, SEVERITY_WARN, "eval report unreadable: " + str(exc))
    if not isinstance(doc, dict):
        return _finding(CHECK_EVAL_REPORT, SEVERITY_WARN, "eval report unreadable: expected a JSON object")
    rate = doc.get("rate")
    try:
        if rate is None and "passed" in doc and "total" in doc:
            rate = float(doc["passed"]) / float(doc["total"]) if float(doc["total"]) else 0.0
        rate_f = float(rate) if rate is not None else None
    except (TypeError, ValueError):
        rate_f = None
    if rate_f is None:
        return _finding(CHECK_EVAL_REPORT, SEVERITY_WARN, "eval report has no numeric 'rate' (or passed/total); re-run eval before install")
    if rate_f < EVAL_GATE:
        return _finding(CHECK_EVAL_REPORT, SEVERITY_WARN, "eval rate " + format(rate_f, ".2f") + " below gate " + format(EVAL_GATE, ".1f") + "; fix the skill before install")
    return _finding(CHECK_EVAL_REPORT, SEVERITY_INFO, "eval report ok: rate " + format(rate_f, ".2f") + " >= gate " + format(EVAL_GATE, ".1f"))


def scan_skill(skill_dir) -> dict:
    """Scan one local skill dir; return verdict/confidence/summary/guidance/findings.

    Verdict is pass (install), warn (review then install), or fail (refuse).
    Confidence is 0.0-1.0. Findings carry per-check severity info/warn/error.
    """
    path = Path(skill_dir)
    skill_name = path.name if path.name else str(skill_dir)
    if not path.is_dir():
        findings = [_finding("skill-dir", SEVERITY_ERROR, "skill dir missing: '" + str(path) + "' is not a directory")]
        summary = "skill '" + skill_name + "' blocked: skill dir missing."
        guidance = "Point the scan at an existing local skill folder; do not install."
        return {"skill": skill_name, "verdict": VERDICT_FAIL, "confidence": CONFIDENCE_FAIL, "summary": summary, "guidance": guidance, "findings": findings}
    skill_md = path / "SKILL.md"
    has_skill_md = skill_md.is_file()
    meta = None
    if has_skill_md:
        try:
            meta = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        except OSError:
            meta = None
    findings = [
        _check_frontmatter(path, skill_name, meta, has_skill_md),
        _check_license(meta),
        _check_eval_report(path, skill_name),
    ]
    errors = sum(1 for f in findings if f["severity"] == SEVERITY_ERROR)
    warns = sum(1 for f in findings if f["severity"] == SEVERITY_WARN)
    passed = len(findings) - errors - warns
    if errors:
        verdict, confidence = VERDICT_FAIL, CONFIDENCE_FAIL
        summary = "skill '" + skill_name + "' blocked: " + str(errors) + " error(s), " + str(warns) + " warning(s); fix before installing."
        guidance = "Fix the errors above before installing; do not install until the scan is pass or warn."
    elif warns:
        verdict, confidence = VERDICT_WARN, CONFIDENCE_WARN
        summary = "skill '" + skill_name + "' needs review before install: " + str(warns) + " warning(s), " + str(passed) + "/" + str(len(findings)) + " checks passed."
        guidance = "Review the warnings above before installing; re-run the scan after fixing."
    else:
        verdict, confidence = VERDICT_PASS, CONFIDENCE_PASS
        summary = "skill '" + skill_name + "' ready to install: " + str(passed) + "/" + str(len(findings)) + " checks passed."
        guidance = "Proceed with install."
    return {"skill": skill_name, "verdict": verdict, "confidence": confidence, "summary": summary, "guidance": guidance, "findings": findings}


def format_scan(report: dict) -> str:
    """Render severity lines first, then the verdict line (print before install)."""
    lines = []
    for item in report.get("findings", []):
        sev = str(item.get("severity", SEVERITY_INFO)).upper()
        lines.append("[" + sev + "] " + str(item.get("check", "?")) + ": " + str(item.get("message", "")))
    lines.append("verdict: " + str(report.get("verdict", "?")).upper() + " (confidence " + format(float(report.get("confidence", 0.0)), ".2f") + ") - " + str(report.get("summary", "")))
    lines.append("guidance: " + str(report.get("guidance", "")))
    return chr(10).join(lines) + chr(10)


def _exit_for(verdict: str) -> int:
    return {VERDICT_PASS: 0, VERDICT_WARN: 1, VERDICT_FAIL: 2}.get(verdict, 2)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Pre-install scan: verdict/confidence/findings over one local skill dir.")
    parser.add_argument("skill_dir", help="Local skill folder to scan (holds SKILL.md).")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    report = scan_skill(args.skill_dir)
    sys.stdout.write(format_scan(report))
    return _exit_for(report["verdict"])


if __name__ == "__main__":
    raise SystemExit(main())
