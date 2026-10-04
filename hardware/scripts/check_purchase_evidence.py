#!/usr/bin/env python3
"""Read-only integrity and generated-output check for the project purchase ledger.

Missing historical payment evidence is reported separately from structural errors.
Run hardware/scripts/test_ledger_analysis.py for the synthetic model tests.
"""
import subprocess
import sys
from pathlib import Path

if __name__ == '__main__':
    raise SystemExit(subprocess.call([
        sys.executable, str(Path(__file__).with_name('_ledger_totals.py')), '--check',
    ]))
