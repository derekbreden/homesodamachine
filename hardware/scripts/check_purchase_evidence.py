#!/usr/bin/env python3
"""Read-only integrity and generated-output check for the project purchase ledger.

Missing historical payment evidence is reported separately from structural errors. It is the
purchases program's `--check`. Run hardware/scripts/test_ledger_analysis.py for the synthetic
model tests.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == '__main__':
    from _rust_part import program
    raise SystemExit(subprocess.call([str(program('ledger', 'purchases')), '--check'],
                                     cwd=Path(__file__).resolve().parents[2]))
