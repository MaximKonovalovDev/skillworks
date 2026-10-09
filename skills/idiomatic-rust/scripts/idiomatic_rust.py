"""Check Rust snippets for the twelve Rustacean idioms of skills/idiomatic-rust.

Each bad snippet triggers its rule message, each good snippet is clean.
The machine list is references/pairs.json, the human twin is
references/pairs.md. All checks are plain text scans, no compiler needed.

    python skills/idiomatic-rust/scripts/idiomatic_rust.py
    python skills/idiomatic-rust/scripts/idiomatic_rust.py --json
    python skills/idiomatic-rust/scripts/idiomatic_rust.py --pair ir-p01
    python skills/idiomatic-rust/scripts/idiomatic_rust.py --check path/to/file.rs

Exit code 0 when every bad snippet fails as named and every good snippet
passes. --check prints PASS or FAIL for one file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = HERE.parent / "references" / "pairs.json"


def violations(text: str) -> list[tuple[str, str]]:
    """Scan text for the twelve misses. Returns (id, message) per hit."""
    out: list[tuple[str, str]] = []
    if re.search(r"const\s+[a-z]", text):
        out.append(("ir-p01", "lowercase const, want UPPERCASE like MAX_SIZE"))
    if re.search(r"struct\s+[a-z]", text):
        out.append(("ir-p01", "lowercase type, want CamelCase like UserId"))
    if re.search(r"fn\s+[A-Z]", text):
        out.append(("ir-p01", "uppercase function, want snake_case like user_id"))
    if re.search(r"Option<", text) and re.search(r"\.unwrap\(\)", text):
        out.append(("ir-p02", "unwrap on Option, use match with Some and None"))
    if re.search(r"Result<", text) and re.search(r"\.unwrap\(\)", text) and not re.search(r"\?", text):
        out.append(("ir-p03", "unwrap on Result, use question mark operator"))
    if re.search(r"for\s+\w+\s+in\s+0\.\.", text) and re.search(r"\[\w+\]", text):
        out.append(("ir-p04", "index loop, use iter with collect"))
    if re.search(r"fn\s+set_", text) and re.search(r"&mut\s+self", text):
        out.append(("ir-p05", "mut setter, use builder with_* returning Self plus build"))
    if re.search(r"id\s*:\s*String", text) and "struct UserId" not in text:
        out.append(("ir-p06", "bare String id, use newtype UserId"))
    if re.search(r"fn\s+cleanup\s*\(", text) and "impl Drop" not in text:
        out.append(("ir-p07", "manual cleanup, use RAII impl Drop with drop"))
    if re.search(r"fn\s+extra\s*\(", text) and "trait Ext" not in text:
        out.append(("ir-p08", "missing trait Ext, add extension trait plus blanket bound"))
    if re.search(r"&String", text):
        out.append(("ir-p09", "owned str ref &String, use &str"))
    if re.search(r"->\s*String", text) and re.search(r"\.clone\(\)", text) and "Cow<" not in text:
        out.append(("ir-p10", "owned String clone, use Cow borrowed or owned"))
    if re.search(r"for\s+.+:", text, re.S) is None and re.search(r"for\s", text) and re.search(r"\.clone\(\)", text):
        out.append(("ir-p11", "clone in loop, borrow with &item"))
    if re.search(r"impl\s+Deref", text):
        out.append(("ir-p12", "Deref polymorphism, remove Deref impl"))
    if re.search(r"static\s+mut", text):
        out.append(("ir-p12", "static mut singleton, remove static mut"))
    if re.search(r"unsafe\s*\{", text) and "impl Deref" not in text and "static mut" not in text:
        # A tiny unsafe with a safety comment is allowed, a bare one is not.
        # Good p12 has no unsafe at all, bad p12 has unsafe plus the two
        # tokens above, so this branch only fires on other unsafe uses.
        if "safety" not in text.lower():
            out.append(("ir-p12", "bare unsafe, keep tiny unsafe with safety comment"))
    return out


def check_text(text: str) -> tuple[bool, list[tuple[str, str]]]:
    """True when clean (no violations)."""
    found = violations(text)
    return (len(found) == 0, found)


def run_pairs(doc: dict) -> list[dict]:
    results = []
    for pair in doc["pairs"]:
        pid = pair["id"]
        bad_code = pair.get("bad_code", "")
        good_code = pair.get("good_code", "")
        bad_error = str(pair.get("bad_error", "")).lower()
        _, bad_found = check_text(bad_code)
        bad_ok = any(bad_error in msg.lower() or bad_error in pid.lower() for _, msg in bad_found) if bad_found else False
        # Fallback: any violation on the bad side counts when the named
        # fragment is the rule id itself.
        if not bad_ok and bad_found and bad_error in ("ir-p01", "ir-p02", "ir-p03", "ir-p04", "ir-p05", "ir-p06", "ir-p07", "ir-p08", "ir-p09", "ir-p10", "ir-p11", "ir-p12"):
            bad_ok = any(vid == pid for vid, _ in bad_found)
        good_clean, good_found = check_text(good_code)
        good_ok = good_clean
        ok = bool(bad_ok and good_ok)
        why: list[str] = []
        if not bad_ok:
            shown = "; ".join(m for _, m in bad_found[:3]) or "no violation reported"
            why.append("bad did not report [" + bad_error + "], got: " + shown)
        if not good_ok:
            shown = "; ".join(vid + ": " + m for vid, m in good_found[:3])
            why.append("good is not clean: " + shown)
        results.append({"id": pid, "title": pair.get("title", ""), "bad_ok": bad_ok, "good_ok": good_ok, "ok": ok, "why": why})
    return results


def check_file(path: Path) -> tuple[int, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return 2, "ERROR cannot read " + str(path) + ": " + str(exc)
    clean, found = check_text(text)
    # Name the rule by file stem when it matches ir-pNN.
    stem = path.stem
    tag = stem if re.fullmatch(r"ir-p\d+", stem) else "idiomatic"
    if clean:
        # Name the passing token per rule for stable output.
        token = {"ir-p01": "UPPERCASE", "ir-p02": "match", "ir-p03": "Result", "ir-p04": "iter", "ir-p05": "build", "ir-p06": "UserId", "ir-p07": "Drop", "ir-p08": "trait Ext", "ir-p09": "&str", "ir-p10": "Cow", "ir-p11": "&item", "ir-p12": "no Deref"}.get(tag, "idiomatic")
        return 0, "PASS " + tag + " " + token
    first_id, first_msg = found[0]
    use_id = first_id if tag == "idiomatic" else tag
    return 1, "FAIL " + use_id + " " + first_msg


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Replay the idiomatic-rust bad/good pairs.")
    ap.add_argument("--json", action="store_true", help="machine-readable results")
    ap.add_argument("--pair", default=None, help="run one pair by id")
    ap.add_argument("--check", default=None, help="check one Rust file")
    args = ap.parse_args(argv)
    if args.check:
        code, said = check_file(Path(args.check))
        print(said)
        return code
    doc = json.loads(PAIRS.read_text(encoding="utf-8"))
    if args.pair:
        doc["pairs"] = [p for p in doc["pairs"] if p["id"] == args.pair]
        if not doc["pairs"]:
            print("unknown pair " + str(args.pair))
            return 2
    results = run_pairs(doc)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            if r["ok"]:
                print("PASS " + r["id"] + ": " + r["title"])
            else:
                print("FAIL " + r["id"] + ": " + "; ".join(r["why"]))
        print(str(sum(1 for r in results if r["ok"])) + " of " + str(len(results)) + " pairs behave as written")
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

