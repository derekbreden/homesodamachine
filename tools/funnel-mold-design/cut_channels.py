"""Command-line entry point for the funnel mold's optional V channels."""
from pathlib import Path
import runpy


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    runpy.run_path(str(root/'hardware/printed-parts/zone-c/funnel-mold/solid/channels/cut_channels.py'),
                   run_name='__main__')
