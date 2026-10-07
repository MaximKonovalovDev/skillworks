"""O-012: paid MCP probe runs mocked by default, live once with receipt.

Shape copies tests/test_mcp_schema.py (plain asserts, stdlib only, no
network): mock needs no key, live needs SKILLWORKS_PAID_LIVE=1 plus a dummy
key, budget cap refuses, CLI prints RESULT PASS.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tools import paid_probe as probe

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in (probe.LIVE_FLAG, probe.KEY_VAR):
        monkeypatch.delenv(var, raising=False)


def test_mock_by_default_needs_no_key() -> None:
    assert probe.is_live() is False
    receipt = probe.paid_call("batch tokens")
    assert receipt["mode"] == "mock"
    assert receipt["cost_usd"] == 0.0
    assert receipt["hits"] >= 0
    assert receipt["cap_usd"] == pytest.approx(0.50)
    assert probe.KEY_VAR not in json.dumps(receipt)


def test_live_once_with_receipt_and_capped_budget(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(probe.LIVE_FLAG, "1")
    monkeypatch.setenv(probe.KEY_VAR, "dummy-test-key")
    out = tmp_path / "receipt.json"
    receipt = probe.paid_call("batch tokens", budget_usd=0.05, receipt_path=out)
    assert receipt["mode"] == "live"
    assert receipt["cost_usd"] == pytest.approx(0.05)
    assert receipt["key_present"] is True
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["mode"] == "live" and saved["hits"] == receipt["hits"]
    assert "dummy-test-key" not in out.read_text(encoding="utf-8")


def test_budget_cap_refuses() -> None:
    with pytest.raises(ValueError, match="exceeds cap"):
        probe.paid_call("batch tokens", budget_usd=99.0)


def test_live_without_key_refuses(monkeypatch) -> None:
    monkeypatch.setenv(probe.LIVE_FLAG, "1")
    with pytest.raises(ValueError, match=probe.KEY_VAR):
        probe.paid_call("batch tokens")


def test_cli_mock_prints_result_pass() -> None:
    env = {k: v for k, v in os.environ.items()
           if k not in (probe.LIVE_FLAG, probe.KEY_VAR)}
    run = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "paid_probe.py"),
         "--query", "batch tokens", "--limit", "2"],
        capture_output=True, text=True, env=env, timeout=30,
    )
    assert run.returncode == 0, run.stderr
    assert '"mode": "mock"' in run.stdout
    assert "RESULT PASS" in run.stdout
