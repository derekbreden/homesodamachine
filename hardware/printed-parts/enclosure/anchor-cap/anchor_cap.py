"""The anchor cap: the printed half pipe that closes a 1/4" tube anchor in place of its zip tie.

Exported standing on its end, the way it prints: the tube's axis is Z, the section lies on the
bed at Z = 0, and the shoulders that seat on the rib's lips face +Y. The section is
`_anchor_cap_interface.cap`'s, the same call the enclosure assembly seats at each capped anchor.
"""
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for directory in (_hw / "scripts", _hw / "printed-parts/enclosure/enclosure", _hw.parent / "tools"):
    sys.path.insert(0, str(directory))
from _cadq_export import export_assembly  # noqa: E402
from _materials import M_PETGF_BLACK, one_body  # noqa: E402
from docgen import substitute_md  # noqa: E402
import _anchor_cap_interface as cap  # noqa: E402

PRINT_FRAME = cap.Frame((0.0, 0.0, cap.CAP_LEN / 2.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
# The accepted faucet display cover's wing on the same beam estimate, read off its published
# STEP in the tip frame: 1.35 mm thick, bezel's inner face at n 22.05 to the middle of the lip at
# n 4.8, spreading 2.6 mm from its relaxed lip face (x 10.9) over the neck's 13.5 going on.
FAUCET_COVER_WING = (1.35, 22.05 - 4.8, 2.6)


def faucet_cover_strain():
    thick, length, spread = FAUCET_COVER_WING
    return 1.5 * thick * spread / length ** 2


def build_anchor_cap():
    return cap.cap(PRINT_FRAME)


def selftest():
    body = build_anchor_cap()
    assert body.isValid() and len(body.Solids()) == 1, "the cap is one valid solid"
    bb = body.BoundingBox()
    assert abs(bb.zmin) < 1e-6 and abs(bb.zmax - cap.CAP_LEN) < 1e-6, "it stands on its end"
    assert abs(bb.xmax - cap.WING_OUT) < 1e-6 and abs(bb.ymax - cap.WING_TOP) < 1e-6
    # One section the whole length: every layer prints the same outline.
    areas = {round(body.intersect(cq.Solid.makeBox(40, 40, 0.1, cq.Vector(-20, -20, z))).Volume(), 3)
             for z in (0.5, cap.CAP_LEN / 2.0, cap.CAP_LEN - 0.6)}
    assert len(areas) == 1, f"the section changes along the cap: {areas}"
    assert cap.CAVITY >= 0.6, f"a {cap.CAVITY:.2f} mm gap may print shut"
    assert cap.wing_strain() <= faucet_cover_strain() + 1e-4, (
        f"the wings reach {100 * cap.wing_strain():.2f}% going on, past the faucet cover's "
        f"{100 * faucet_cover_strain():.2f}% on the same estimate")
    print(f"Anchor cap: one valid solid, {body.Volume():.0f} mm^3, wings "
          f"{100 * cap.wing_strain():.2f}% (faucet cover {100 * faucet_cover_strain():.2f}%).")
    return 0


def main():
    selftest()
    out = _here.parent / "anchor-cap.step"
    body = cq.Workplane(obj=build_anchor_cap())
    export_assembly(one_body(body, "anchor-cap", M_PETGF_BLACK), str(out))
    body.val().copy(mesh=False).exportStl(str(out.with_suffix(".stl")),
                                          tolerance=.005, angularTolerance=.05, relative=False)
    from flute_payload import cut
    cut(out, out.with_suffix(".stl"))
    metric_out = _here.parent / "anchor-cap-4mm.step"
    metric = cap.cap(PRINT_FRAME, 2.0 + cap.fits.slip)
    export_assembly(one_body(metric, "anchor-cap-4mm", M_PETGF_BLACK), str(metric_out))
    metric.copy(mesh=False).exportStl(str(metric_out.with_suffix(".stl")),
                                     tolerance=.005, angularTolerance=.05, relative=False)
    cut(metric_out, metric_out.with_suffix(".stl"))
    volume = body.val().Volume()
    substitute_md(_here.parent / "README.md", variables={
        "CAP_LEN": f"{cap.CAP_LEN:g} mm",
        "CAP_WIDTH": f"{2.0 * cap.WING_OUT:.2f} mm",
        "CAP_HEIGHT": f"{cap.WING_TOP + cap.WING_OUT:.2f} mm",
        "SADDLE": f"{cap.SADDLE:g} mm",
        "WING": f"{cap.WING:g} mm",
        "WING_AIR": f"{cap.WING_AIR:g} mm",
        "ENGAGE": f"{cap.ENGAGE:g} mm",
        "LEAD_IN": f"{cap.LEAD_IN:g}°",
        "CAVITY": f"{cap.CAVITY:.2f} mm",
        "CAVITY_DEG": f"{cap.CAVITY_DEG:g}°",
        "WING_FLEX": f"{cap.wing_flex_len():.1f} mm",
        "WING_STRAIN": f"{100 * cap.wing_strain():.2f}%",
        "FAUCET_COVER_STRAIN": f"{100 * faucet_cover_strain():.2f}%",
        "BEARING_PLAY": f"{cap.BEARING_PLAY:g} mm",
        "SEAT_D": f"{2.0 * cap.SEAT_R:.2f} mm",
        "CAP_VOLUME": f"{volume / 1000.0:.2f} cm³",
    })
    print("-> anchor-cap.step, anchor-cap.stl, anchor-cap.step.mesh, README.md")


if __name__ == "__main__":
    sys.exit(selftest() if len(sys.argv) > 1 and sys.argv[1] == "selftest" else main())
