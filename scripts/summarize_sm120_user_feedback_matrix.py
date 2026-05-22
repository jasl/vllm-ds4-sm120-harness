#!/usr/bin/env python3
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ds4_harness.user_feedback_matrix_summary import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
