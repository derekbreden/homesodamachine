"""Foam lid generator — the thin PETG cover for the cold-core body's open +Z
top. Exports foam-lid.step. See ../_foam_lid.py for the geometry and
../foam-shell/README.md for how it seats over the cured body-pour foam."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_lid import build_foam_lid


def main():
    lid = build_foam_lid()
    export_step(lid, str(_here / "foam-lid.step"))
    print("-> foam-lid.step")

    bbox = lid.val().BoundingBox()
    print(f"  lid: {bbox.xlen:.1f} x {bbox.ylen:.1f} x {bbox.zlen:.1f} mm, "
          f"{len(lid.val().Solids())} solid")


if __name__ == "__main__":
    main()
