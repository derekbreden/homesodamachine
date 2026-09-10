"""Command-line entry point for the solid funnel mold's CAD generator."""
from pathlib import Path
import runpy


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    runpy.run_path(str(root/'hardware/printed-parts/zone-c/funnel-mold/solid/solid_mold.py'),
                   run_name='__main__')
