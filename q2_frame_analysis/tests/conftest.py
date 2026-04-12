from pathlib import Path
import sys


TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
ASSIGNMENT_ROOT = PROJECT_ROOT.parent

for path in (ASSIGNMENT_ROOT, PROJECT_ROOT, TESTS_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)