#!/usr/bin/env python3

import sys
from pathlib import Path

print("__file__:", __file__)
print("sys.argv[0]:", sys.argv[0])

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
SCRIPTS_DIR = REPO_ROOT / "scripts"

print("REPO_ROOT:", REPO_ROOT)
print("SRC_DIR:", SRC_DIR)
print("SCRIPTS_DIR:", SCRIPTS_DIR)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

print("sys.path[0:5]:", sys.path[0:5])

# Now try the exact import that's failing
try:
    from scripts.vendor.arc_lens.scrapers import WikiItemScraper
    print('SUCCESS: Import worked')
except Exception as e:
    print('FAILED: Import failed with error:', e)
    import traceback
    traceback.print_exc()