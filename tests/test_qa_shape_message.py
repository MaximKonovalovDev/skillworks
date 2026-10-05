"""pilot-112: string-`must` refusal names the type violation, not the keys."""
import json

import pytest

from book2skill import eval as eval_mod


def test_string_must_names_list_violation(tmp_path):
    qa = tmp_path / "qa.jsonl"
    qa.write_text(json.dumps({"q": "What color is the beacon?", "must": "green"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r'"must" must be a list of words'):
        eval_mod.validate_qa(qa)


def test_list_must_still_passes_shape_check(tmp_path):
    qa = tmp_path / "qa.jsonl"
    qa.write_text(json.dumps({"q": "What color is the beacon?", "must": ["green"]}) + "\n", encoding="utf-8")
    eval_mod.validate_qa(qa)  # no refusal
