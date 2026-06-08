"""Lite Edition enclosure shell — a transparent PETG box sized to the
arrangement in `../enclosure-contents-assembly/`.

The shell is six walls (floor, four sides, lid). The contents sit on the floor
plane (z = 0); their +X face points to the cabinet back, their -X face is the
enclosure front, the trays carry the -X wall, the funnel rides under the lid.
A square hole in the lid clears the funnel inlet so it sits flush with the top
of the cabinet.

Dimensions follow the contents at build time: the bounding box of
`enclosure-contents-assembly.step` is read live, padded by an interior
clearance, then walled out. The lid hole is centered on the funnel's lid
footprint with matching clearance.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments

CONTENTS_STEP = (
    _repo / "pie-in-the-sky" / "lite" / "enclosure-contents-assembly"
    / "enclosure-contents-assembly.step"
)
FUNNEL_STEP = (
    _repo / "pie-in-the-sky" / "lite" / "printed-parts" / "funnel" / "funnel.step"
)

# Shell parameters.
# [3 mm](WALL) PETG wall thickness.
wall = 3.0
# [5 mm](INTERIOR_CLEARANCE) gap between contents and inner wall, on all sides.
interior_clearance = 5.0
# [2 mm](LID_HOLE_CLEARANCE) gap between funnel rim and lid-hole edge.
lid_hole_clearance = 2.0


def _bbox(path):
    return cq.importers.importStep(str(path)).val().BoundingBox()


def build_enclosure():
    contents = _bbox(CONTENTS_STEP)

    # Inner cavity: contents bbox padded by clearance on all sides; floor at
    # z = contents.zmin (contents sit on it), lid inner face at contents.zmax
    # (funnel inlet flush with it).
    ix0, ix1 = contents.xmin - interior_clearance, contents.xmax + interior_clearance
    iy0, iy1 = contents.ymin - interior_clearance, contents.ymax + interior_clearance
    iz0, iz1 = contents.zmin, contents.zmax

    # Outer shell: cavity grown by wall on all six faces.
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

    # Lid hole sized to the funnel's lid footprint plus clearance.
    funnel = _bbox(FUNNEL_STEP)
    hx0 = funnel.xmin - lid_hole_clearance
    hx1 = funnel.xmax + lid_hole_clearance
    hy0 = funnel.ymin - lid_hole_clearance
    hy1 = funnel.ymax + lid_hole_clearance
    hole = (
        cq.Workplane("XY")
        .box(hx1 - hx0, hy1 - hy0, wall + 2.0, centered=False)
        .translate((hx0, hy0, iz1 - 1.0))
    )
    shell = shell.cut(hole)

    return shell, (ox0, ox1, oy0, oy1, oz0, oz1), (hx0, hx1, hy0, hy1)


def main():
    shell, outer, lid_hole = build_enclosure()
    out = _here.parent / "enclosure.step"
    export_step(shell, str(out))
    print(f"-> {out.name}")
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    hx0, hx1, hy0, hy1 = lid_hole
    print(
        "  outer envelope %.1f (X) x %.1f (Y) x %.1f (Z) mm"
        % (ox1 - ox0, oy1 - oy0, oz1 - oz0)
    )

    variables = {
        "WALL": f"{wall:.4g} mm",
        "INTERIOR_CLEARANCE": f"{interior_clearance:.4g} mm",
        "LID_HOLE_CLEARANCE": f"{lid_hole_clearance:.4g} mm",
        "OUTER_X": f"{ox1 - ox0:.4g} mm",
        "OUTER_Y": f"{oy1 - oy0:.4g} mm",
        "OUTER_Z": f"{oz1 - oz0:.4g} mm",
        "LID_HOLE_X": f"{hx1 - hx0:.4g} mm",
        "LID_HOLE_Y": f"{hy1 - hy0:.4g} mm",
    }
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={
            "WALL": 1,
            "INTERIOR_CLEARANCE": 1,
            "LID_HOLE_CLEARANCE": 1,
            "OUTER_X": 1,
            "OUTER_Y": 1,
            "OUTER_Z": 1,
            "LID_HOLE_X": 1,
            "LID_HOLE_Y": 1,
        },
    )
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "WALL": 1,
            "INTERIOR_CLEARANCE": 1,
            "LID_HOLE_CLEARANCE": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
