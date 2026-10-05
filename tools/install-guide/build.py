#!/usr/bin/env python3
"""Build the 32-page Lulu Small Landscape install guide and order files."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('landscape.py')), run_name='__main__')
