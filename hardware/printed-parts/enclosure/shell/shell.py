"""Kitchen Edition enclosure shell — a six-walled PETG box sized to the
arrangement in `../contents-assembly/`, sized to fit the H2C left-nozzle
build envelope.

Dimensions follow the contents at build time: the bounding box of
`contents-assembly.step` is read live, padded by an interior clearance,
then walled out. Six closed walls; no penetrations modelled.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware"))
from _cadq_export import export_step

CONTENTS_STEP = (
    _repo / "hardware" / "printed-parts" / "enclosure" / "contents-assembly"
    / "contents-assembly.step"
)

# Shell parameters.
wall = 3.0                  # PETG wall thickness
interior_clearance = 0.0    # gap between contents bbox and inner wall

# H2C left-nozzle build envelope; the shell's outer must fit inside this.
H2C_X, H2C_Y, H2C_Z = 325.0, 320.0, 320.0


def _bbox(path):
    return cq.importers.importStep(str(path)).val().BoundingBox()


def build_enclosure():
    contents = _bbox(CONTENTS_STEP)

    ix0, ix1 = contents.xmin - interior_clearance, contents.xmax + interior_clearance
    iy0, iy1 = contents.ymin - interior_clearance, contents.ymax + interior_clearance
    iz0, iz1 = contents.zmin - interior_clearance, contents.zmax + interior_clearance

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz0, oz1 = iz0 - wall, iz1 + wall

    outer = (
        cq.Workplane("XY")
        .box(ox1 - ox0, oy1 - oy0, oz1 - oz0, centered=False)
        .translate((ox0, oy0, oz0))
    )
    inner = (
        cq.Workplane("XY")
        .box(ix1 - ix0, iy1 - iy0, iz1 - iz0, centered=False)
        .translate((ix0, iy0, iz0))
    )
    shell = outer.cut(inner)
    return shell, (ox0, ox1, oy0, oy1, oz0, oz1)


def main():
    shell, outer = build_enclosure()
    out = _here.parent / "shell.step"
    export_step(shell, str(out))
    print(f"-> {out.name}")
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    dx, dy, dz = ox1 - ox0, oy1 - oy0, oz1 - oz0
    print(f"  outer envelope    {dx:.1f} (X) x {dy:.1f} (Y) x {dz:.1f} (Z) mm")
    print(f"  H2C left nozzle   {H2C_X:.1f} (X) x {H2C_Y:.1f} (Y) x {H2C_Z:.1f} (Z) mm")
    fits = dx <= H2C_X + 1e-3 and dy <= H2C_Y + 1e-3 and dz <= H2C_Z + 1e-3
    print(f"  fits H2C bed:     {fits}")


if __name__ == "__main__":
    main()
