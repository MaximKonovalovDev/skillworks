# Steal port: godic97/mutation-gate@aa7fee1 (licence MIT)
# Source: https://github.com/godic97/mutation-gate/blob/aa7fee10b2551ec80acfbf1a07870779e1627855/mutation_gate/gate.py
# Written fresh in our style; no donor code pasted.
"""Diff-scoped mutation verdict: kill-score gate on changed lines only."""

_BANNER_LIMIT = 5


def _mut_id(mut):
    if isinstance(mut, dict):
        return str(mut.get("id", mut))
    return str(mut)


def _mut_line(mut):
    if isinstance(mut, dict):
        line = mut.get("line")
        if isinstance(line, bool):
            return None
        if isinstance(line, int):
            return line
        return None
    return None


def _mut_file(mut):
    if isinstance(mut, dict):
        value = mut.get("file")
        if isinstance(value, str):
            return value
    return None


def _in_scope(mut, changed_lines):
    if changed_lines is None:
        return True
    if isinstance(changed_lines, dict):
        name = _mut_file(mut)
        line = _mut_line(mut)
        if name is None or line is None:
            return False
        try:
            allowed = set(changed_lines.get(name, ()))
        except TypeError:
            return False
        return line in allowed
    mid = _mut_id(mut)
    line = _mut_line(mut)
    name = _mut_file(mut)
    for entry in changed_lines:
        if isinstance(entry, bool):
            continue
        if isinstance(entry, int) and line is not None and entry == line:
            return True
        if isinstance(entry, str) and entry == mid:
            return True
        if isinstance(entry, str) and ":" in entry and name is not None and line is not None:
            if entry == "%s:%s" % (name, line):
                return True
    return False


def _kill_score(n_killed, n_survived):
    total = n_killed + n_survived
    if total == 0:
        return 1.0
    return n_killed / total


def _survivors_banner(survivor_ids, limit=_BANNER_LIMIT):
    ids = [str(item) for item in survivor_ids]
    if not ids:
        return "survivors (0): none - all mutants killed"
    shown = ids[:limit]
    head = ", ".join(shown)
    if len(ids) > limit:
        return "survivors (%d): %s +%d more" % (len(ids), head, len(ids) - limit)
    return "survivors (%d): %s" % (len(ids), head)


def _suppressed_note(mut, suppressions):
    sid = _mut_id(mut)
    own = None
    if isinstance(mut, dict) and mut.get("suppressed"):
        own = mut.get("note") or mut.get("reason") or "suppressed"
    if suppressions is None:
        return own
    if isinstance(suppressions, dict):
        if sid in suppressions:
            value = suppressions[sid]
            if isinstance(value, str) and value:
                return value
            return own or "suppressed"
        return own
    try:
        if sid in suppressions:
            return own or "suppressed"
    except TypeError:
        pass
    return own


def _verdict_dict(killed, survived, threshold=0.8, changed_lines=None, suppressions=None):
    """Verdict over changed lines only: threshold score plus banner plus notes."""
    killed = list(killed or [])
    survived = list(survived or [])
    scoped_killed = [m for m in killed if _in_scope(m, changed_lines)]
    scoped_survived = [m for m in survived if _in_scope(m, changed_lines)]
    effective = []
    notes = []
    for item in scoped_survived:
        note = _suppressed_note(item, suppressions)
        if note is not None:
            notes.append("%s: %s" % (_mut_id(item), note))
        else:
            effective.append(item)
    n_killed = len(scoped_killed)
    n_survived = len(effective)
    score = _kill_score(n_killed, n_survived)
    passed = score >= threshold
    banner = _survivors_banner([_mut_id(m) for m in effective])
    return {
        "score": score,
        "threshold": threshold,
        "verdict": "PASS" if passed else "FAIL",
        "passed": passed,
        "killed": n_killed,
        "survived": n_survived,
        "total": n_killed + n_survived,
        "banner": banner,
        "suppression_notes": notes,
    }


def test_surviving_mutant_on_changed_line_fails_gate():
    killed = [{"id": "k1", "line": 10, "file": "a.py"}]
    survived = [{"id": "s1", "line": 12, "file": "a.py"}]
    verdict = _verdict_dict(killed, survived, threshold=0.8, changed_lines={10, 12})
    assert verdict["score"] == 0.5
    assert verdict["threshold"] == 0.8
    assert verdict["verdict"] == "FAIL"
    assert verdict["passed"] is False
    assert "s1" in verdict["banner"]


def test_full_kill_passes_gate():
    killed = [
        {"id": "k1", "line": 10, "file": "a.py"},
        {"id": "k2", "line": 12, "file": "a.py"},
    ]
    verdict = _verdict_dict(killed, [], threshold=0.8, changed_lines={10, 12})
    assert verdict["score"] == 1.0
    assert verdict["verdict"] == "PASS"
    assert verdict["passed"] is True
    assert verdict["survived"] == 0
    assert verdict["total"] == 2


def test_off_diff_survivor_does_not_fail_gate():
    killed = [{"id": "k1", "line": 10, "file": "a.py"}]
    survived = [{"id": "s9", "line": 99, "file": "a.py"}]
    verdict = _verdict_dict(killed, survived, threshold=0.8, changed_lines={10})
    assert verdict["survived"] == 0
    assert verdict["total"] == 1
    assert verdict["score"] == 1.0
    assert verdict["verdict"] == "PASS"
    assert "s9" not in verdict["banner"]


def test_survivors_banner_capped_at_five():
    survived = [{"id": "s%d" % i, "line": 10 + i, "file": "a.py"} for i in range(7)]
    verdict = _verdict_dict([], survived, threshold=0.8, changed_lines=None)
    assert verdict["verdict"] == "FAIL"
    assert verdict["score"] == 0.0
    assert "+2 more" in verdict["banner"]
    assert "survivors (7):" in verdict["banner"]
    for head_id in ("s0", "s1", "s2", "s3", "s4"):
        assert head_id in verdict["banner"]
    assert "s5" not in verdict["banner"]
    assert "s6" not in verdict["banner"]


def test_suppression_notes_only_on_changed_lines():
    killed = []
    survived = [
        {"id": "s1", "line": 12, "file": "a.py", "suppressed": True, "note": "equivalent mutant"},
        {"id": "s9", "line": 99, "file": "a.py", "suppressed": True, "note": "off diff note"},
    ]
    verdict = _verdict_dict(killed, survived, threshold=0.8, changed_lines={12})
    assert verdict["survived"] == 0
    assert verdict["score"] == 1.0
    assert verdict["verdict"] == "PASS"
    assert len(verdict["suppression_notes"]) == 1
    assert "s1" in verdict["suppression_notes"][0]
    assert "equivalent mutant" in verdict["suppression_notes"][0]
    assert all("s9" not in note for note in verdict["suppression_notes"])


def test_suppression_dict_and_threshold_boundary():
    killed = [{"id": "k1", "line": 10, "file": "a.py"}]
    survived = [{"id": "s1", "line": 12, "file": "a.py"}]
    suppressed = _verdict_dict(
        killed, survived, threshold=0.5, changed_lines={10, 12}, suppressions={"s1": "waived flake"}
    )
    assert suppressed["survived"] == 0
    assert suppressed["verdict"] == "PASS"
    assert suppressed["suppression_notes"] == ["s1: waived flake"]
    boundary = _verdict_dict(killed, survived, threshold=0.5, changed_lines={10, 12})
    assert boundary["score"] == 0.5
    assert boundary["verdict"] == "PASS"
    strict = _verdict_dict(killed, survived, threshold=0.51, changed_lines={10, 12})
    assert strict["verdict"] == "FAIL"
