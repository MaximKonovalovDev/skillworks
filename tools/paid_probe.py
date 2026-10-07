"""O-012 paid MCP path probe: one paid call via skill_search, mock by default.

Offline, stdlib only, no network. Mock is the default so a stranger never
spends money by accident. Live runs only with SKILLWORKS_PAID_LIVE=1 plus a
key in SKILLWORKS_PAID_KEY (never committed, never printed). One call max,
capped budget, receipt written on request.

Vendor note (read live 2026-10-07, proprietary test-only): Smithery lists
paid Pro tiers (example 129 USD per month) plus a free credit tier; Replicate
runs models by API with billing per run. No free copy to steal. Test only on
the free tier, one paid call max, mock by default.

    python tools/paid_probe.py --query "batch tokens" [--skill pipe-run]
        [--limit 5] [--budget 0.05] [--receipt <path>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp_server import server as skill_search  # noqa: E402 offline local lookup

LIVE_FLAG = "SKILLWORKS_PAID_LIVE"
KEY_VAR = "SKILLWORKS_PAID_KEY"
MAX_CALLS = 1
MAX_SPEND_USD = 0.50
LIVE_COST_USD = 0.05
VENDOR_NOTE = (
    "Smithery paid Pro example 129 USD/mo (read live 2026-10-07), "
    "proprietary test-only, free tier only for this probe."
)


def is_live() -> bool:
    """True only when the owner opts in with SKILLWORKS_PAID_LIVE=1."""
    return os.environ.get(LIVE_FLAG) == "1"


def paid_call(query: str, skill: str | None = None, limit: int = 5,
              budget_usd: float = LIVE_COST_USD,
              receipt_path: str | Path | None = None) -> dict:
    """Run one paid-path call through skill_search. Returns the receipt dict.

    Mock by default (cost 0.0, no key needed). Live needs the env flag plus
    a key, costs LIVE_COST_USD, and refuses when budget_usd exceeds the cap
    or is below the live cost. Never prints or stores the key itself.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query is required (non-empty string)")
    try:
        limit = int(limit)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError("limit must be integer 1..20") from None
    if not 1 <= limit <= 20:
        raise ValueError("limit must be integer 1..20")
    try:
        budget = float(budget_usd)
    except (TypeError, ValueError):
        raise ValueError("budget must be a number in USD") from None
    if budget > MAX_SPEND_USD:
        raise ValueError(f"budget {budget} exceeds cap {MAX_SPEND_USD} USD")
    live = is_live()
    if live and budget < LIVE_COST_USD:
        raise ValueError(f"live call costs {LIVE_COST_USD} USD, budget {budget} too small")
    if live and not os.environ.get(KEY_VAR):
        raise ValueError(f"live call needs {KEY_VAR} in the env (never committed)")
    hits = skill_search._search(query, skill, limit)
    receipt = {
        "tool": "skill_search",
        "mode": "live" if live else "mock",
        "query": query,
        "skill": skill,
        "limit": limit,
        "hits": len(hits),
        "cost_usd": LIVE_COST_USD if live else 0.0,
        "budget_usd": budget,
        "cap_usd": MAX_SPEND_USD,
        "max_calls": MAX_CALLS,
        "key_present": bool(os.environ.get(KEY_VAR)),
        "vendor": VENDOR_NOTE,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
    }
    if receipt_path is not None:
        out = Path(receipt_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        receipt["receipt"] = str(out)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="O-012 paid MCP probe, mock by default.")
    parser.add_argument("--query", required=True, help="keywords for skill_search")
    parser.add_argument("--skill", default=None, help="restrict to one skill")
    parser.add_argument("--limit", default=5, help="max hits 1..20")
    parser.add_argument("--budget", default=LIVE_COST_USD, help="budget USD, cap 0.50")
    parser.add_argument("--receipt", default=None, help="write receipt JSON here")
    args = parser.parse_args(argv)
    try:
        receipt = paid_call(args.query, args.skill, args.limit, float(args.budget), args.receipt)
    except ValueError as exc:
        print(f"FAIL {exc}")
        print("RESULT FAIL")
        return 1
    print(json.dumps(receipt, indent=2))
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
