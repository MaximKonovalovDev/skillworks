"""Skill lint: the distill kit CLI (TS-2, R1 book-to-skill in hours, with receipts).

    python tools/skill_lint.py plan --work work/<name>
    python tools/skill_lint.py check --skill skills/<name> [--work work/<name>]
    python tools/skill_lint.py --help

plan groups work/chunks into reading packets of at most 6000 tokens, each
with its chunk locators (writes work/distill_plan.json). check is the gate a
distilled skill must pass before the cure smith ships it: SKILL.md body within
2000 tokens, no scaffold text, every rule carries a locator that exists,
10 or more tested pairs or trials, plain ASCII. Prints one line per finding
and ends with one RESULT PASS or RESULT FAIL line; exit 0 only on PASS.
check writes nothing; plan writes only work/distill_plan.json.

One code path: both commands call book2skill/distill.py, the same functions
the `book2skill distill` commands use.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from book2skill import distill as distill_mod  # noqa: E402


def cmd_plan(args: argparse.Namespace) -> int:
    try:
        distill_mod.plan(Path(args.work))
    except ValueError as exc:
        print(f"FAIL {exc}")
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    report = distill_mod.check(Path(args.skill), Path(args.work) if args.work else None)
    for finding in report["findings"]:
        print(f"FAIL {finding}")
    print(f"rules {report.get('rules', 0)}, locators "
          f"{sum(report.get('locators', {}).values()) if isinstance(report.get('locators'), dict) else 0}, "
          f"pairs {report.get('pairs_total', 0)}, body {report.get('body_tokens', 0)} tokens")
    print("RESULT PASS" if report["ok"] else "RESULT FAIL")
    return 0 if report["ok"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Distill kit: reading packets and the cure-smith gate.")
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan", help="group work/chunks into reading packets of at most 6000 tokens")
    plan.add_argument("--work", required=True, help="work dir, e.g. work/mybook")
    plan.set_defaults(func=cmd_plan)
    check = sub.add_parser("check", help="gate a distilled skill (budget, scaffold, locators, pairs, ASCII)")
    check.add_argument("--skill", required=True, help="skill dir, e.g. skills/mybook")
    check.add_argument("--work", default=None, help="work dir whose chunks locators must resolve to")
    check.set_defaults(func=cmd_check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
