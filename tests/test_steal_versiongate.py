"""Steal version gate: single-pattern exact N.N.N check."""
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "g18-lock.py"
_spec = importlib.util.spec_from_file_location("g18_lock", str(TOOL))
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_exact_pins_accepted():
    for v in ("1.2.0", "0.3.1", "10.20.30", "0.0.0", " 1.2.0 ", "01.02.03"):
        assert _mod.is_range(v) is False, v


def test_range_and_odd_rejected():
    for v in ("", "  ", "^0.3.0", "~1.2.0", ">=1.0.0", "<=2.0.0", ">1.0.0", "<1.0.0", "1.2", "1", "1.2.3.4", "*", "1.2.x", "1.2.*", "v1.2.0", "1.2.0-alpha", "1.2.0||1.3.0", "1.2..3", "a.b.c"):
        assert _mod.is_range(v) is True, repr(v)


def test_single_pattern_gate():
    assert hasattr(_mod, "_VERSION_RE") or hasattr(_mod, "VERSION_PATTERN")
    assert hasattr(_mod, "InvalidVersion")
    assert not hasattr(_mod, "is_exact")
    assert not hasattr(_mod, "RANGE_HINT")
