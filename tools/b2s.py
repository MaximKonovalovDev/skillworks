"""Run the book2skill CLI from a file path: python tools/b2s.py <stage> ... (same as python -m book2skill)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from book2skill.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
