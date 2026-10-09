from tools import skill_trial as trial

def _ten():
    return [{"id": f"t{n:02d}"} for n in range(1, 11)]

def test_median_p10_correct_on_fixture():
    tasks = _ten()
    with_out = {t["id"]: (t["id"] not in ("t09", "t10")) for t in tasks}
    without_out = {t["id"]: (t["id"] in ("t01", "t02", "t03", "t04", "t05")) for t in tasks}
    record = trial.summarize("demo", tasks, with_out, without_out)
    assert record["with_rate"] == 0.8
    assert record["with_median"] == 1.0
    assert record["with_p10"] == 0.0
    assert record["without_median"] == 0.5
    assert record["without_p10"] == 0.0
    print("fixture median 1.0/0.5 p10 0.0/0.0")
    full = {t["id"]: True for t in tasks}
    record_full = trial.summarize("demo", tasks, full, without_out)
    assert record_full["with_median"] == 1.0
    assert record_full["with_p10"] == 1.0
    assert trial._median([1.0] * 8 + [0.0] * 2) == 1.0
    assert trial._p10([1.0] * 8 + [0.0] * 2) == 0.0

def test_record_check_grades_exit_zero_with_output_as_pass():
    passed, finding = trial.check_record({"exit": 0, "output": "did run ok"}, 0, "t01")
    assert passed and finding is None
    refused, _msg1 = trial.check_record({"answer": "words only"}, 0, "t01")
    assert not refused
    wrong_exit, _msg2 = trial.check_record({"exit": 2, "output": "did run ok"}, 0, "t01")
    assert not wrong_exit
