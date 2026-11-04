"""The 1 mm TPU ring between the machine display glass and its snap-retained cover.

The ring lies in the cover's local frame: X across, Y up the display plane and Z
out of the face. Its outer outline matches the glass and its inner outline the window.
"""
from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure"))
if __name__=='__main__':
    import _rust_part
    _rust_part.start()

import cadquery as cq
from _cadq_export import export_assembly
from _materials import M_TPU_BLACK, linear, one_body
from docgen import substitute_md, substitute_py_comments
from _enclosure_interface import (
    display_bezel_depth,
    display_bezel_slope,
    display_bezel_x,
    display_corner_r,
    display_inset_depth,
    display_inset_lap,
)


from _enclosure_data import read as _read


def _data():
    return _read('gasket', display_bezel_x=display_bezel_x,
                 display_bezel_slope=display_bezel_slope,
                 display_corner_r=display_corner_r, display_inset_lap=display_inset_lap,
                 display_bezel_depth=display_bezel_depth, display_inset_depth=display_inset_depth,
                 color=linear(M_TPU_BLACK))


globals().update(_data()['scalars'])


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


def numbers():
    """The glass/window outlines and their shared compressed-gap thickness."""
    return _data()['recipe']


def main():
    import _rust_part
    result = _rust_part.cut('enclosure-components','display-gasket',numbers(),_here.parent)

    out = _here.parent / "display-gasket.step"
    print(f"-> {out.name}")

    lo,hi = result['bodies'][0]['min'],result['bodies'][0]['max']
    print("Display gasket")
    print(f"  {outer_x:g} x {outer_slope:g} outer, {inner_x:g} x {inner_slope:g} inner — "
          f"a {display_inset_lap:g} ring, r{corner_r:g} corners")
    print(f"  {thickness:g} thick, from the plate's underside at {display_inset_depth:g} "
          f"down to the glass at {glass_face_depth:g}")
    print(f"  Bounding box: X [{lo[0]:.2f}, {hi[0]:.2f}]  Y [{lo[1]:.2f}, {hi[1]:.2f}]  "
          f"Z [{lo[2]:.2f}, {hi[2]:.2f}]")

    variables = _data()['variables']

    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")

    substitute_py_comments(Path(__file__), variables=variables)
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
