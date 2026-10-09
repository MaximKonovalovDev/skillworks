"""What: run the book2skill CLI from a file path (same as python -m book2skill).

Needs: run from the skillworks repo root; a source you own (file, folder, or URL).

Example: python tools/b2s.py make --in manual --name demo-skill --description "Use when ..." --qa evals/demo-skill_qa.jsonl

Stages: make | extract | split | index | build | audit | eval | refresh | export.
Full help: python tools/b2s.py --help (this screen) or python tools/b2s.py <stage> --help.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from book2skill.cli import main  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h"):
        print(__doc__.strip())
        sys.argv[1] = "--help"
    main()

