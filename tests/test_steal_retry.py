"""steal retry bound: litl/backoff-style expo plus jitter plus giveup for extract fallback."""
import pytest
from book2skill import extract as extract_mod


def test_flaky_twice_succeeds_on_third():
    calls = []
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("boom")
        return "ok"
    assert extract_mod.with_retry(flaky, sleep=lambda _: None) == "ok"
    assert len(calls) == 3



def test_always_fail_raises_after_three():
    calls = []
    seen = {}
    def bad():
        calls.append(1)
        raise RuntimeError("nope")
    def hook(details):
        seen.update(details)
    with pytest.raises(RuntimeError):
        extract_mod.with_retry(bad, tries=3, sleep=lambda _: None, on_giveup=hook)
    assert len(calls) == 3
    assert seen["tries"] == 3
    assert "nope" in str(seen["cause"])



def test_giveup_on_valueerror_immediate():
    calls = []
    def bad():
        calls.append(1)
        raise ValueError("fatal")
    with pytest.raises(ValueError):
        extract_mod.with_retry(bad, sleep=lambda _: None)
    assert len(calls) == 1



def test_fallback_note_records_tries_and_cause(tmp_path, monkeypatch):
    src = tmp_path / "x.pdf"
    src.write_bytes(b"%PDF-1.4 fake")
    work = tmp_path / "work"
    def fail(path):
        exc = RuntimeError("convert boom")
        exc.retry_tries = 3
        raise exc
    monkeypatch.setattr(extract_mod, "_read_pdf_markitdown", fail)
    monkeypatch.setattr(extract_mod, "_read_pdf_classic", lambda path: ("hello", 1))
    receipt = extract_mod.extract(str(src), work, engine="auto")
    assert receipt["engine"] == "classic-fallback"
    assert "3" in receipt["note"]
    assert "convert boom" in receipt["note"]

