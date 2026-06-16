"""
Carbonator end-cap — 3D solid for CNC machining quotes.

The complete machined cap: the 4.860" × 1/4" 316 SS disc, the two 1/4"-18 NPT
tap-drill through-holes, AND the blind level-sensing rod register. This is the
quote artifact for CNC vendors (Xometry / Protolabs / Fictiv / RapidDirect),
where the register IS a machined feature — unlike the laser cut file
`endcap-circular-2hole.dxf`, which omits it because a laser cuts only THROUGH
and a through-hole there would breach the 90 PSI pressure boundary.

One part covers both caps: the top and bottom plates are this identical
geometry (the top-plate register captures the float-rod tip; the bottom-plate
register seats it for the tack weld). The two holes are modelled at tap-drill
diameter — the vendor taps 1/4"-18 NPT per the drawing callout.

── Geometry (built in mm; the cap's source specs are in inches) ──

  Disc:            123.4 mm Ø × 6.35 mm  (4.860" × 1/4", = tube ID 4.870" − 0.010")
  NPT tap-drill:   2× 11.13 mm Ø  (7/16") THRU, at X = ±19.05 mm (±0.750")
  Rod register:    3.572 mm Ø (9/64") blind, 2.54 mm (0.100") deep, at
                   (0, −50.97 mm) on the inside (+Z) face — leaves 3.81 mm
                   (0.150") of plate as intact pressure boundary.

The register sits on the +Z face = the vessel INSIDE face; the −Z face is the
plain outside face. STEP is exported in millimetres (CadQuery / CNC default).

Units: millimetres.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from _cadq_export import export_step
from docgen import substitute_py_comments

inch = 25.4  # mm per inch — the cap's source specs are in inches.

# [123.4 mm](DISC_D) — 4.860" disc (tube ID 4.870" − 0.010" slip-fit).
disc_diameter = 4.860 * inch
disc_radius = disc_diameter / 2.0  # [61.72 mm](DISC_R)
# [6.35 mm](DISC_THK) — 1/4" 316 SS plate.
disc_thickness = 0.250 * inch

# [11.13 mm](HOLE_D) — 7/16" tap drill for 1/4"-18 NPT, through the full plate.
hole_diameter = 0.438 * inch
hole_radius = hole_diameter / 2.0  # [5.563 mm](HOLE_R)
# [19.05 mm](HOLE_OFFSET) — each NPT hole's |X| from center (1.500" c-c).
hole_offset = 0.750 * inch
hole_positions = [(-hole_offset, 0.0), (hole_offset, 0.0)]

# ── Rod register — blind retention pocket, machined (see module docstring) ──
# Mirrors the source-of-truth derivation in endcap_circular_dxf.py: park the rod
# so the 27.75 mm donor donut's OD reaches the inner wall, then add a 3 mm
# wall-preload to pin it there — matches the reservoir test-fit (reservoir.py
# rod_position_x 104 → 107 mm).
tube_id = 4.870 * inch                       # donut rides this wall
donut_od = 27.75                             # mm — donor ferrite donut (DEVMO MINI)
wall_preload = 3.0                           # mm closer to the wall (empirical preload)
# [50.97 mm](REG_Y) — register center on the −Y axis (= 2.007"), clear of ports.
register_radius = tube_id / 2.0 - donut_od / 2.0 + wall_preload
register_position = (0.0, -register_radius)
# [3.572 mm](REG_D) — 9/64" slip-fit drill on the 1/8" rod.
register_drill_diameter = 0.140625 * inch
# [2.54 mm](REG_DEPTH) — 0.100" blind; leaves 3.81 mm (0.150") of plate.
register_depth = 0.100 * inch

out_dir = Path(__file__).resolve().parent
out_name = "endcap-circular-2hole"


def build_endcap() -> cq.Workplane:
    disc = cq.Workplane("XY").circle(disc_radius).extrude(disc_thickness)

    # Two 1/4"-18 NPT tap-drill holes, through the full plate (tool over-runs
    # both faces so the boolean leaves no zero-thickness slivers).
    npt_holes = (
        cq.Workplane("XY")
        .workplane(offset=-0.5)
        .pushPoints(hole_positions)
        .circle(hole_radius)
        .extrude(disc_thickness + 1.0)
    )

    # Blind rod register, entered from the +Z (inside) face. The tool over-runs
    # the +Z face only; its floor stops at register_depth below it, so the −Z
    # outside face — the pressure boundary — is never broken.
    register = (
        cq.Workplane("XY")
        .workplane(offset=disc_thickness + 0.5)
        .moveTo(*register_position)
        .circle(register_drill_diameter / 2.0)
        .extrude(-(register_depth + 0.5))
    )

    return disc.cut(npt_holes).cut(register)


def main() -> None:
    model = build_endcap()
    path = out_dir / f"{out_name}.step"
    export_step(model, str(path))

    print(f"Exported: {path}")
    print(f"  Disc:      Ø{disc_diameter:.3f} × {disc_thickness:.3f} mm, 316 SS")
    print(f"  NPT holes: 2× Ø{hole_diameter:.3f} mm THRU at X = ±{hole_offset:.3f} mm")
    print(f"  Register:  Ø{register_drill_diameter:.4g} × {register_depth:.3g} mm blind "
          f"at (0, {-register_radius:.3f}), +Z (inside) face")

    variables = {
        "DISC_D": f"{disc_diameter:.4g} mm",
        "DISC_R": f"{disc_radius:.4g} mm",
        "DISC_THK": f"{disc_thickness:.4g} mm",
        "HOLE_D": f"{hole_diameter:.4g} mm",
        "HOLE_R": f"{hole_radius:.4g} mm",
        "HOLE_OFFSET": f"{hole_offset:.4g} mm",
        "REG_Y": f"{register_radius:.4g} mm",
        "REG_D": f"{register_drill_diameter:.4g} mm",
        "REG_DEPTH": f"{register_depth:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={k: 1 for k in variables},
    )


if __name__ == "__main__":
    main()
