"""STEAL gatefront: strict-subset frontmatter keys plus NAME_REGEX plus word budgets."""
import book2skill.gates as g


def _strict(text, path="SKILL.md"):
    return g.lint_frontmatter_text(text, path=path, strict=True)


def _base(text, path="SKILL.md"):
    return g.lint_frontmatter_text(text, path=path)


GOOD = "---\nname: demo\nlicense: MIT\ndescription: Use when testing the gatefront strict subset with enough words here for the check.\n---\nbody here\n"


def test_constants_match_donor():
    assert g.REQUIRED_PROPERTIES == {"name", "description"}
    assert g.RECOMMENDED_PROPERTIES == {"license"}
    assert "license" in g.ALLOWED_PROPERTIES
    assert "version" in g.ALLOWED_PROPERTIES
    assert "name" in g.ALLOWED_PROPERTIES
    assert g.NAME_REGEX == r"^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$"
    assert g.NAME_MAX_LENGTH == 64
    assert g.DESCRIPTION_MAX_LENGTH == 1024
    assert g.BODY_WORDS_WARNING == 1500
    assert g.BODY_WORDS_ERROR == 5000


def test_valid_strict_stays_clean():
    assert _strict(GOOD) == []
    assert _base(GOOD) == []
    text = GOOD.replace("license: MIT", "license: MIT\nversion: 0.1.0")
    assert _strict(text) == []


def test_unknown_key_refused_strict_only():
    text = "---\nname: demo\nlicense: MIT\ndescription: Use when testing unknown keys with enough words here ok.\nbogus: 1\n---\nbody\n"
    base = _base(text)
    assert base == []
    issues = _strict(text)
    assert len(issues) == 1
    assert issues[0]["type"] == "warning"
    assert "Unknown" in issues[0]["msg"]
    assert "bogus" in issues[0]["msg"]


def test_bad_name_refused():
    for bad in ("Bad_Name", "UPPER", "-leading", "trailing-", "has space"):
        text = "---\nname: " + bad + "\nlicense: MIT\ndescription: Use when testing bad names with enough words here ok.\n---\nbody\n"
        issues = _strict(text)
        assert any("malformed" in i["msg"] for i in issues), bad
        assert _base(text) == []


def test_double_hyphen_refused():
    text = "---\nname: a--b\nlicense: MIT\ndescription: Use when testing double hyphens with enough words here ok.\n---\nbody\n"
    issues = _strict(text)
    assert any("consecutive" in i["msg"] for i in issues)
    assert _base(text) == []


def test_missing_recommended_warns_strict_only():
    text = "---\nname: demo\ndescription: Use when testing missing license with enough words here ok.\n---\nbody\n"
    assert _base(text) == []
    issues = _strict(text)
    assert any("recommended" in i["msg"].lower() for i in issues)


def test_description_too_long():
    long_desc = "d" * 2000
    text = "---\nname: demo\nlicense: MIT\ndescription: " + long_desc + "\n---\nbody\n"
    issues = _strict(text)
    assert any("too long" in i["msg"] for i in issues)


def test_body_word_budgets():
    warn_body = "word " * 1600
    text = "---\nname: demo\nlicense: MIT\ndescription: Use when testing body budgets with enough words here ok.\n---\n" + warn_body + "\n"
    issues = _strict(text)
    assert any("1500" in i["msg"] for i in issues)
    err_body = "word " * 5100
    text2 = "---\nname: demo\nlicense: MIT\ndescription: Use when testing body error budget with enough words here ok.\n---\n" + err_body + "\n"
    issues2 = _strict(text2)
    assert any("5000" in i["msg"] for i in issues2)
    assert g.body_words(text) == 1600
    assert g.body_words(text2) == 5100


def test_malformed_coverage_up():
    cases = [
        "---\nname: demo\nlicense: MIT\ndescription: Use when testing unknown with enough words here ok.\nbogus: 1\n---\nbody\n",
        "---\nname: Bad_Name\nlicense: MIT\ndescription: Use when testing bad name with enough words here ok.\n---\nbody\n",
        "---\nname: a--b\nlicense: MIT\ndescription: Use when testing hyphens with enough words here ok.\n---\nbody\n",
        "---\nname: demo\ndescription: Use when testing missing license with enough words here ok.\n---\nbody\n",
        "---\nname: demo\nlicense: MIT\ndescription: " + "d" * 2000 + "\n---\nbody\n",
        "---\nname: demo\nlicense: MIT\ndescription: Use when testing body budget with enough words here ok.\n---\n" + "word " * 1600 + "\n",
    ]
    base_hits = sum(1 for t in cases if _base(t) != [])
    strict_hits = sum(1 for t in cases if _strict(t) != [])
    assert base_hits == 0
    assert strict_hits == 6
