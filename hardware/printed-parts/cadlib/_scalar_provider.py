"""Locate the shared Rust provider from a standalone cadlib caller."""
from pathlib import Path
import sys

_scripts = Path(__file__).resolve().parents[2] / 'scripts'
if str(_scripts) not in sys.path:
    sys.path.insert(0,str(_scripts))
from _shared_data import call
