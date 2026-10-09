import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pack_check as pc

PACK = {"price_usd": 9}
URL = "https://store.example/fix-pack"
LIVE_TEXT = "# Fix pack\nLive listing: https://store.example/fix-pack\nBody here\n"
PLAIN_TEXT = "# Fix pack\nBody with no live line here\n"

def fails(rep):
    return [w for lv, w in rep.lines if lv == "FAIL"]

def warns(rep):
    return [w for lv, w in rep.lines if lv == "WARN"]

def passes(rep):
    return [w for lv, w in rep.lines if lv == "PASS"]

def test_no_live_line_has_no_fail():
    rep = pc.Report()
    pc.check_storefront_drift(PACK, PLAIN_TEXT, rep, False, lambda u: 200, fetch_text=lambda u: "$9")
    assert rep.count("FAIL") == 0
    assert rep.lines == []

def test_offline_warns_without_fail():
    rep = pc.Report()
    pc.check_storefront_drift(PACK, LIVE_TEXT, rep, True, lambda u: 200, fetch_text=lambda u: "$9")
    assert rep.count("FAIL") == 0
    assert rep.count("WARN") == 1
    assert "storefront-drift" in warns(rep)[0]

def test_matching_price_agrees():
    rep = pc.Report()
    pc.check_storefront_drift(PACK, LIVE_TEXT, rep, False, lambda u: 200, fetch_text=lambda u: "Only $9 today")
    assert rep.count("FAIL") == 0
    assert any("agrees with pack.json" in w for w in passes(rep))

def test_drifted_price_fails():
    rep = pc.Report()
    pc.check_storefront_drift(PACK, LIVE_TEXT, rep, False, lambda u: 200, fetch_text=lambda u: "Only $25 today")
    assert any("page-price vs live-link drift" in w for w in fails(rep))

def test_dead_link_fails():
    for code in (404, 410):
        rep = pc.Report()
        pc.check_storefront_drift(PACK, LIVE_TEXT, rep, False, lambda u, c=code: c, fetch_text=lambda u: "$9")
        assert any("is dead" in w for w in fails(rep))

def test_unknown_and_empty_body_fail_as_unknown():
    for code in (0, 500):
        rep = pc.Report()
        pc.check_storefront_drift(PACK, LIVE_TEXT, rep, False, lambda u, c=code: c, fetch_text=lambda u: "$9")
        assert any("UNKNOWN is never OK" in w for w in fails(rep))
    rep = pc.Report()
    pc.check_storefront_drift(PACK, LIVE_TEXT, rep, False, lambda u: 200, fetch_text=lambda u: "")
    assert any("UNKNOWN is never OK" in w for w in fails(rep))

def test_body_with_no_price_fails():
    rep = pc.Report()
    pc.check_storefront_drift(PACK, LIVE_TEXT, rep, False, lambda u: 200, fetch_text=lambda u: "No money sign on this page at all")
    assert any("carries no price" in w for w in fails(rep))

def test_check_pack_calls_gate_with_fetch_text():
    src = inspect.getsource(pc.check_pack)
    assert "check_storefront_drift" in src
    assert "fetch_text" in src
    assert "check_storefront_drift(pack, listing, rep, offline, fetch, fetch_text)" in src
