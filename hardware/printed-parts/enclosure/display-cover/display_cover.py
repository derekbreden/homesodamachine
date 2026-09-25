"""Machine display cover with a rounded bezel and two broad retaining skirts.

The visible face lies at local Z=0. The cover prints face down with its skirts pointing up,
and the assembly seats it as modelled: each skirt's lip rests under its catch with the skirt
unbent. The TPU ring separates bezel and glass.
"""

import sys
from pathlib import Path
import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for directory in (_hw / "scripts", _hw / "printed-parts" / "enclosure" / "enclosure"):
    sys.path.insert(0, str(directory))
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
sys.path.insert(0, str(_tools))
from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK, one_body
from docgen import substitute_md
import _enclosure_interface as dims
import _display_retention as retention
import _stated_bounds as bounds
from _swept_top import rounded_prism

skirt_inset = 0.6
cover_slip = dims.display_cover_slip
cover_x = dims.display_inset_x - 2.0 * cover_slip
cover_slope = dims.display_inset_slope - 2.0 * cover_slip
cover_corner_r = dims.display_cover_corner_r
skirt_outer_x = retention.OUTER_X - skirt_inset
catch_overlap = skirt_outer_x + retention.LIP - retention.NECK_X
window_x = dims.display_bezel_x - 2.0 * dims.display_inset_lap
window_slope = dims.display_bezel_slope - 2.0 * dims.display_inset_lap
window_corner_r = dims.display_corner_r

bounds.state('display-cover-reveal', 'The display bezel is a smooth reveal in the curved top',
             'a 2 mm visible edge; optical and gasket surfaces remain smooth',
             dims.flute_reach(dims.display_cover_thickness) < dims.flute_depth,
             f'{dims.display_cover_thickness:g} mm bezel; the retention skirts sit inside the housing')


def build_cover_skirt(side):
    """The cover-owned skirt, inset from the housing's fixed receiver datum."""
    return retention.skirt(side).translate((-side * skirt_inset, 0, 0))


def build_cover_outer():
    body = rounded_prism(cover_x, cover_slope, cover_corner_r,
                         -dims.display_cover_thickness, 0.0)
    for side in (-1, 1):
        body = body.fuse(build_cover_skirt(side))
    return cq.Workplane(obj=body.clean())


def build_cover_inner_cut():
    return cq.Workplane(obj=rounded_prism(window_x, window_slope, window_corner_r,
                                          -retention.DEPTH - 1.0, 1.0))


def build_display_cover():
    return build_cover_outer().cut(build_cover_inner_cut())


def glass_shadow():
    probe = rounded_prism(dims.display_bezel_x, dims.display_bezel_slope,
                          dims.display_corner_r, -retention.DEPTH-1.0,
                          -dims.display_cover_thickness - 0.0001)
    return abs(build_display_cover().val().intersect(probe).Volume())


def selftest():
    body = build_display_cover().val()
    assert body.isValid() and len(body.Solids()) == 1
    assert glass_shadow() < 0.0001
    for side in (-1, 1):
        skirt = build_cover_skirt(side)
        missing = skirt.cut(retention.pocket(side)).Volume()
        assert abs(missing) < 0.0001, (side, missing)
        for lateral in (-cover_slip, 0.0, cover_slip):
            seated = skirt.translate((lateral, 0, 0))
            assert abs(seated.cut(retention.pocket(side)).Volume()) < 0.0001
            pulled = seated.translate((0, 0, retention.BEARING_SLIP + 0.01))
            assert pulled.cut(retention.pocket(side)).Volume() > 0.0001
    print(f"Display cover: one valid solid; glass clear; skirts inside their pockets, "
          f"{cover_slip:g} mm perimeter clearance; {catch_overlap:g} mm catch overlap, "
          f"{retention.BEARING_SLIP:g} mm below catches")
    return 0


def main():
    selftest()
    cover = build_display_cover()
    out = _here.parent / "display-cover.step"
    export_assembly(one_body(cover, "display-cover", M_PETGF_BLACK), str(out))
    cover.val().copy(mesh=False).exportStl(str(out.with_suffix('.stl')),
        tolerance=0.005, angularTolerance=0.05, relative=False)
    from flute_payload import cut
    cut(out, out.with_suffix('.stl'))
    variables = {
        "COVER_X": f"{cover_x:g} mm", "COVER_SLOPE": f"{cover_slope:g} mm",
        "COVER_CORNER_R": f"{cover_corner_r:g} mm", "COVER_T": f"{dims.display_cover_thickness:g} mm",
        "COVER_SLIP": f"{cover_slip:g} mm", "WINDOW_X": f"{window_x:g} mm",
        "WINDOW_SLOPE": f"{window_slope:g} mm", "WINDOW_CORNER_R": f"{window_corner_r:g} mm",
        "SKIRT_WALL": f"{retention.WALL:g} mm", "SKIRT_LENGTH": f"{retention.LENGTH:g} mm",
        "SKIRT_DEPTH": f"{retention.DEPTH:g} mm", "LIP_START": f"{retention.LIP_START:g} mm",
        "LIP_LAND": f"{retention.LIP_LAND:g} mm", "LIP_ENGAGEMENT": f"{retention.LIP:g} mm",
        "BEARING_SLIP": f"{retention.BEARING_SLIP:g} mm",
        "SKIRT_INSET": f"{skirt_inset:g} mm", "CATCH_OVERLAP": f"{catch_overlap:g} mm",
    }
    substitute_md(_here.parent / "README.md", variables=variables)
    print('-> display-cover.step, display-cover.stl, README.md')


if __name__ == '__main__':
    sys.exit(selftest() if len(sys.argv) > 1 and sys.argv[1] == 'selftest' else main())
