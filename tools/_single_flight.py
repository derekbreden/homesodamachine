#!/usr/bin/env python3
"""Single-flight marker ownership supplied by the native host runtime."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hardware/scripts"))
from _run_native import read as _read


def holder(lock): return _read("single_holder", {"path": str(lock)})
def alive(pid): return _read("single_alive", {"pid": pid})
def take(lock): return tuple(_read("single_take", {"path": str(lock)}))
