# Steal fencegrade: fenced-only behavior grade cuts prose/comment/string false passes.
# Ported fresh from DietrichGebert/ponytail@7efd0b7c (MIT,
# https://github.com/DietrichGebert/ponytail/pull/966) benchmarks/behavior.js:
# onecheck scans only inside fenced blocks, then strips strings/comments before
# the assert/test regex. No donor code copied; expectations rewritten for build.py.
from book2skill import build as bmod

F = chr(96) * 3
DQ3 = chr(34) * 3
SQ3 = chr(39) * 3
DQ = chr(34)
SQ = chr(39)

PROSE = "the assert passes and the test is green"
PY_COMMENT = F + "python\n# assert x\nx = 1\n" + F
JS_COMMENT = F + "js\n// assert x\nlet x = 1;\n" + F
DQ_STRING = F + "python\nmsg = " + DQ + "assert works" + DQ + "\n" + F
SQ_STRING = F + "python\nmsg = " + SQ + "assert works" + SQ + "\n" + F
INLINE_COMMENT = F + "python\nx = 1  # assert here\n" + F
BLOCK_COMMENT = F + "js\n/* assert x */\nlet x = 1;\n" + F
GOOD_PY = F + "python\nassert x == 1\n" + F
DOC_THEN_ASSERT = F + "python\n" + DQ3 + "docstring with assert" + DQ3 + "\nassert x == 1\n" + F
GOOD_JS = F + "js\nassert(x === 1);\n" + F
MIXED = PY_COMMENT + "\ntext\n" + GOOD_PY

FALSE_CASES = [PROSE, PY_COMMENT, JS_COMMENT, DQ_STRING]


def naive(text):
    # Old behavior: whole-answer assert/test scan (prose counts).
    return bool(bmod._CHECK_RE.search(text))


def test_prose_false_positive_killed():
    assert naive(PROSE)
    assert not bmod.grade_fenced(PROSE)


def test_python_comment_holds_no_check():
    assert naive(PY_COMMENT)
    assert not bmod.grade_fenced(PY_COMMENT)


def test_javascript_comment_holds_no_check():
    assert naive(JS_COMMENT)
    assert not bmod.grade_fenced(JS_COMMENT)


def test_string_literals_hold_no_check():
    assert naive(DQ_STRING)
    assert not bmod.grade_fenced(DQ_STRING)
    assert naive(SQ_STRING)
    assert not bmod.grade_fenced(SQ_STRING)


def test_inline_and_block_comments_hold_no_check():
    assert not bmod.grade_fenced(INLINE_COMMENT)
    assert not bmod.grade_fenced(BLOCK_COMMENT)


def test_valid_python_assertion_passes_after_docstring():
    assert bmod.grade_fenced(GOOD_PY)
    assert bmod.grade_fenced(DOC_THEN_ASSERT)


def test_valid_javascript_assertion_passes():
    assert bmod.grade_fenced(GOOD_JS)


def test_mixed_bad_fence_plus_good_fence_passes():
    assert bmod.grade_fenced(MIXED)


def test_false_pass_count_falls_to_zero():
    before = sum(1 for c in FALSE_CASES if naive(c))
    after = sum(1 for c in FALSE_CASES if bmod.grade_fenced(c))
    assert (before, after) == (4, 0)
