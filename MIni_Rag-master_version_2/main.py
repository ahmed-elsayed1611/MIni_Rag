import importlib.util
import os
import sys

_BASE_DIR = os.path.dirname(__file__)
_SRC_DIR = os.path.join(_BASE_DIR, "src")

if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

_spec = importlib.util.spec_from_file_location("src_main", os.path.join(_SRC_DIR, "main.py"))
_src_main = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_src_main)

app = _src_main.app
