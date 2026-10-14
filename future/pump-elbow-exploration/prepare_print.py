"""Prepare one TPU85A elbow, 215 C normal layers, outer10, Engineering Plate, Z0."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    script = (Path(__file__).resolve().parent / "prints" /
              "2026-10-13-compact-single-tpu85a-t215-engineering-z000-mark1" / "prepare_mark1.py")
    runpy.run_path(str(script), run_name="__main__")
