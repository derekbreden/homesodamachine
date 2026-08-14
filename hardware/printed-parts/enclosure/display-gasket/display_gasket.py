"""Display gasket — the TPU ring under the cover plate's lap, between the plate and the glass.

Material: Bambu TPU 90A (black), from the same per-unit-trivial stock as the foam-cap and
reservoir gaskets.

The plate's underside lies one `display_inset_depth` below the 45° face and the display's cover
glass stands `display_bezel_depth` less its own 1 mm below it, so the lap passes over the glass
with air under it. This is what fills that: the plate draws down onto this and this onto the
glass, so the two screws hold the display and not just the plate, and the 45° face a customer
wipes has no opening at its edge.

Frame: the cover plate's own, so every figure here reads against the depths the facet is cut to
— +X lateral, +Y up the 45° slope, origin on the glass's centre in the 45° plane, and Z a depth
below that face. `enclosure_assembly.build_display_gasket` turns it onto the facet and moves it
by nothing else.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure"))
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
from enclosure import (
    display_bezel_depth,
    display_bezel_slope,
    display_bezel_x,
    display_corner_r,
    display_inset_depth,
    display_inset_lap,
)


# THE RING IS THE LAP. Outer edge on the glass's own outline, inner edge on the cover plate's
# window — so it lies under the border exactly, out of the screen and short of the bezel wall.
outer_x = display_bezel_x                                     # [113.5 mm](OUTER_X)
outer_slope = display_bezel_slope                             # [77 mm](OUTER_SLOPE)
inner_x = display_bezel_x - 2.0 * display_inset_lap           # [107.5 mm](INNER_X)
inner_slope = display_bezel_slope - 2.0 * display_inset_lap   # [71 mm](INNER_SLOPE)
corner_r = display_corner_r

# THE THICKNESS IS THE GAP, so it is derived and not chosen: the glass's front face down from
# the 45° plane, less where the plate's underside sits. `glass_thickness` is the cover glass
# standing proud of the display's own front face inside the bezel counterbore.
glass_thickness = 1.0
glass_face_depth = display_bezel_depth - glass_thickness      # [3 mm](GLASS_FACE_DEPTH)
thickness = glass_face_depth - display_inset_depth            # [1 mm](THICKNESS)

z_top = -display_inset_depth                                  # against the plate's underside
z_bottom = z_top - thickness                                  # against the glass


def _rounded_prism(x, slope, r, z0, z1) -> cq.Workplane:
    return (
        cq.Workplane("XY").workplane(offset=z0)
        .rect(x, slope).extrude(z1 - z0)
        .edges("|Z").fillet(r)
    )


def build_display_gasket() -> cq.Workplane:
    """The ring, cut from the glass's outline by the plate's window."""
    proud = 1.0                                   # struck past both faces so the cut breaks clean
    ring = _rounded_prism(outer_x, outer_slope, corner_r, z_bottom, z_top)
    window = _rounded_prism(inner_x, inner_slope, corner_r,
                            z_bottom - proud, z_top + proud)
    return ring.cut(window)


def main():
    gasket = build_display_gasket()

    out = _here.parent / "display-gasket.step"
    export_step(gasket, str(out))
    print(f"-> {out.name}")

    bb = gasket.val().BoundingBox()
    print("Display gasket")
    print(f"  {outer_x:g} x {outer_slope:g} outer, {inner_x:g} x {inner_slope:g} inner — "
          f"a {display_inset_lap:g} ring, r{corner_r:g} corners")
    print(f"  {thickness:g} thick, from the plate's underside at {display_inset_depth:g} "
          f"down to the glass at {glass_face_depth:g}")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")

    variables = {
        "OUTER_X": f"{outer_x:.4g} mm",
        "OUTER_SLOPE": f"{outer_slope:.4g} mm",
        "INNER_X": f"{inner_x:.4g} mm",
        "INNER_SLOPE": f"{inner_slope:.4g} mm",
        "RING_W": f"{display_inset_lap:.4g} mm",
        "CORNER_R": f"{corner_r:.4g} mm",
        "THICKNESS": f"{thickness:.4g} mm",
        "GLASS_FACE_DEPTH": f"{glass_face_depth:.4g} mm",
        "PLATE_UNDERSIDE": f"{display_inset_depth:.4g} mm",
    }

    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")

    substitute_py_comments(Path(__file__), variables=variables)
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
