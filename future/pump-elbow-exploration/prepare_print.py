"""Prepare one full-base Mark1 TPU85A elbow offline; no submission."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    script = (Path(__file__).resolve().parent / "prints" /
              "2026-10-13-full-base-single-tpu85a-mark1" / "prepare_mark1.py")
    runpy.run_path(str(script), run_name="__main__")
