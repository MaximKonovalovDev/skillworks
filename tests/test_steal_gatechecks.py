"""Steal gatechecks: ported validator checks live in book2skill gates."""
import pytest
from book2skill import gates as g

GOOD = """---
name: demo
description: Use when testing the gate checks with enough characters here.
license: MIT
---
# Demo
```python
def add(a, b):
    return a + b
```
"""

BAD_SYNTAX = GOOD.replace("return a + b", "def broken(:")
TODO_TEXT = GOOD + "TODO: finish this section"

def test_bad_syntax_refused():
    with pytest.raises(AssertionError):
        g.check_code_syntax_and_markers(BAD_SYNTAX)

def test_todo_marker_refused():
    with pytest.raises(AssertionError):
        g.check_code_syntax_and_markers(TODO_TEXT)

def test_good_skill_passes():
    g.check_code_syntax_and_markers(GOOD)
    text = (g.SKILLS / "git-one-branch" / "SKILL.md").read_text(encoding="utf-8")
    g.check_code_syntax_and_markers(text)
