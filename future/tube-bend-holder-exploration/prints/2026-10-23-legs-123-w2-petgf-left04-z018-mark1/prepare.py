"""Prepare and slice the 2 mm holder with 1, 2 and 3 mm straight legs on one Mark1 plate.
Manual use; does not send.

    tools/cad-venv/bin/python future/tube-bend-holder-exploration/tube_bend_holder.py
    tools/cad-venv/bin/python future/tube-bend-holder-exploration/prints/2026-10-23-legs-123-w2-petgf-left04-z018-mark1/prepare.py

The process is the wall comparison's, from its own preparer: the shared `petgf.3mf`, solid,
+0.18 mm trim.
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "walls_plate", HERE.parent / "2026-10-23-walls-234-petgf-left04-z018-mark1/prepare.py")
walls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(walls)

STEM = "2026-10-23-tube-bend-holders-w2-legs123-petgf-left04-z018-mark1"
# One row across the middle of the left nozzle's plate, 1 mm legs on the left.
PARTS = (("1 mm legs", "holder-w2-leg1.stl", (-28.0, 0.0)),
         ("2 mm legs", "holder-w2-leg2.stl", (0.0, 0.0)),
         ("3 mm legs", "holder-w2-leg3.stl", (28.0, 0.0)))

if __name__ == "__main__":
    walls.main(folder=HERE, stem=STEM, parts=PARTS,
               title="Tube bend holders 2 mm, 1/2/3 mm legs - black PET-GF - Mark1")
