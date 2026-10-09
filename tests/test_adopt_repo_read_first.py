"""Adopt repo-read-first: misses/loads mapping is per-repo with gap flags."""
from tools import adopt_repo_read_first as arr


def test_misses_by_repo_counts_matching_class_only() -> None:
    scan = {"classes": {
        "deepwiki_ask_wiki_question Repository not found": {"repos": {"alpha": 3, "beta": 1}},
        "github_get_file_contents does not point to a file": {"repos": {"alpha": 2}},
        "deepwiki_ask_wiki_question ok": {"repos": {"alpha": 99}},
        "other_tool Repository not found": {"repos": {"gamma": 7}},
    }}
    assert arr.misses_by_repo(scan) == {"alpha": 5, "beta": 1}


def test_loads_by_repo_filters_skill() -> None:
    detail = {("repo-read-first", "alpha"): 4, ("other-skill", "alpha"): 9,
              ("repo-read-first", "beta"): 1}
    assert arr.loads_by_repo(detail) == {"alpha": 4, "beta": 1}


def test_rows_sorts_and_flags_gap() -> None:
    data = arr.rows({"beta": 1, "alpha": 5}, {"alpha": 2})
    assert [r["repo"] for r in data] == ["alpha", "beta"]
    assert data[0] == {"repo": "alpha", "misses": 5, "loads": 2, "gap": False}
    assert data[1]["gap"] is True


def test_rows_ignores_loads_without_misses() -> None:
    assert arr.rows({}, {"alpha": 3}) == []

