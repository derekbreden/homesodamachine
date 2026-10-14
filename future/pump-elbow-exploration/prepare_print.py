"""Prepare one TPU85A elbow, Engineering Plate and zero Z trim; no submission."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    script = (Path(__file__).resolve().parent / "prints" /
              "2026-10-13-compact-single-tpu85a-engineering-z000-mark1" / "prepare_mark1.py")
    runpy.run_path(str(script), run_name="__main__")
