"""STEAL trial golden gate: drift refuses without explicit update."""
import json
from tools import skill_trial as trial
def _record(runs=12, with_rate=1.0, lift=0.5):
    return {"runs": runs, "with_rate": with_rate, "without_rate": 0.5, "lift": lift, "spread": 0.5, "fingerprint": "abc"}
def test_matching_proof_passes(tmp_path):
    golden = tmp_path / "trial-proof.golden.json"
    record = _record()
    ok, reason = trial.check_trial_golden(record, golden, update=True)
    assert ok and reason is None
    ok2, reason2 = trial.check_trial_golden(dict(record), golden)
    assert ok2 and reason2 is None
    saved = json.loads(golden.read_text(encoding="utf-8"))
    assert saved == {"lift": 0.5, "runs": 12, "with_rate": 1.0}
def test_drifted_proof_fails(tmp_path):
    golden = tmp_path / "trial-proof.golden.json"
    trial.check_trial_golden(_record(), golden, update=True)
    drifted = _record(with_rate=0.75)
    ok, reason = trial.check_trial_golden(drifted, golden)
    assert not ok and "golden drift with_rate" in reason and "--update-golden" in reason
    ok2, reason2 = trial.check_trial_golden(_record(runs=10), golden)
    assert not ok2 and "golden drift runs" in reason2
    ok3, reason3 = trial.check_trial_golden(_record(), tmp_path / "missing.json")
    assert not ok3 and "--update-golden" in reason3
def test_update_flag_refreshes(tmp_path, monkeypatch):
    golden = tmp_path / "trial-proof.golden.json"
    trial.check_trial_golden(_record(), golden, update=True)
    drifted = _record(with_rate=0.8333, lift=0.3333)
    ok, _reason = trial.check_trial_golden(drifted, golden)
    assert not ok
    ok_up, _ = trial.check_trial_golden(drifted, golden, update=True)
    assert ok_up
    ok_after, _ = trial.check_trial_golden(dict(drifted), golden)
    assert ok_after
    drifted2 = _record(with_rate=0.9, lift=0.4)
    monkeypatch.setenv(trial.GOLDEN_ENV, "1")
    ok_env, _ = trial.check_trial_golden(drifted2, golden)
    assert ok_env
    monkeypatch.delenv(trial.GOLDEN_ENV)
    assert trial.check_trial_golden(dict(drifted2), golden)[0]
