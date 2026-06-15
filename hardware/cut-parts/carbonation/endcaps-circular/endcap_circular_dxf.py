"""
Carbonator end-cap disc — circular vessel, 2 ports per cap.

Two identical discs per vessel, each with 2x tap-drill holes for 1/4"-18 NPT.
4 ports/vessel split 2+2 across both caps.

── Dimensions ──

  Disc diameter:       4.860"    (= tube ID 4.870" − 0.010" slip-fit)
  Disc thickness:      0.250"    (1/4" 316 SS, laser-cut)
  Hole diameter:       0.438"    (7/16" — tap drill for 1/4"-18 NPT)
  Hole spacing:        1.500"    (center-to-center along one axis)
  Hole positions:      (-0.750, 0) and (+0.750, 0)

── Rod register (in-house DRILLED secondary op — deliberately NOT in the cut) ──

  The level-sensing float rod (1/8" 316L) is welded to the bottom plate and
  its top end seats in a shallow blind register in the top plate's inside
  face. That register is a BLIND hole — it must not pierce the plate, because
  the plate is the 90 PSI pressure boundary (hydro 180 PSI). A laser DXF cuts
  THROUGH, so the register cannot live in this cut file without breaching the
  vessel. It is drilled in-house on the WEN 4208T after the discs arrive; the
  laser geometry below is unchanged, so existing discs need no re-cut.

  Both discs are drilled identically (kept interchangeable): top plate captures
  the rod tip, bottom plate seats/locates the rod base for its tack weld.

  Register center:     (0, -1.889)"  on the −Y axis, clear of the two ports.
                       Radius 1.889" = tube-ID radius 2.435" − donut radius
                       0.546" (27.75 mm donor ferrite donut, DEVMO MINI). This
                       parks the donut's OD against the inner tube wall on the
                       −Y side so its magnet couples through the 0.065" wall to
                       the external reed column — the bench-measured "ride the
                       wall within ~2 mm" requirement (level-sensing.md).
                       The −Y azimuth must match where the reeds mount outside.
  Register drill:      9/64" (0.141")  — slip-fit on the 1/8" rod; snug, which
                       self-locates the rod base in the bottom plate for its tack
                       weld. Open the TOP plate's pocket to 5/32" (0.156") only if
                       the cap fights to seat over the rod tip at closure (step 5).
  Register depth:      0.10"  blind, to the drill-point tip, from the inside face
                       — leaves 0.15" of the 0.25" plate as intact pressure
                       boundary. 135° split-point bit ⇒ ~0.07" of full-diameter
                       pocket gripping the rod tip: ample, non-load-bearing capture.

── Material ──

  316 stainless steel, 0.250" thick, laser-cut.

Units: inches.  DXF $INSUNITS = 1 (inches).
"""

import sys
from pathlib import Path

import ezdxf

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
from docgen import substitute_py_comments
from _cadq_export import export_dxf

# Dimensions in inches; DXF $INSUNITS = 1 (inches).

# [4.86 in](DISC_D) — tube ID 4.870" − 0.010" slip-fit.
disc_diameter = 4.860
disc_radius = disc_diameter / 2  # [2.43 in](DISC_R)
# [0.25 in](DISC_THK) — 1/4" 316 SS.
disc_thickness = 0.250

# [0.438 in](HOLE_D) — 7/16" tap drill for 1/4"-18 NPT.
hole_diameter = 0.438
hole_radius = hole_diameter / 2  # [0.219 in](HOLE_R)

# [1.5 in](HOLE_SPACING) center-to-center along one axis — matches the
# CNC dome-cap variants so plumbing layout is identical across cap styles.
hole_spacing = 1.500
hole_positions = [
    (-hole_spacing / 2, 0.0),
    (+hole_spacing / 2, 0.0),
]

# ── Rod register (in-house blind DRILL, not laser-cut — see module docstring) ──
# Source of truth for the level-sensing rod register. NOT emitted into the cut
# DXF: a through-hole here would breach the 90 PSI pressure boundary. Drilled
# blind from the inside face on the WEN 4208T; the drawing carries the callout.
tube_id = 4.870                       # tube inner Ø — donut rides this wall
tube_id_radius = tube_id / 2          # 2.435"
donut_od = 27.75 / 25.4               # 1.0925" — 27.75 mm donor ferrite donut
# Park the rod so the donut OD just reaches the inner wall (wall-scrape fit):
register_radius = tube_id_radius - donut_od / 2  # 1.8887"
register_position = (0.0, -round(register_radius, 3))  # (0, -1.889) on −Y, clear of ports
register_drill_diameter = 0.140625    # 9/64" — slip-fit on the 1/8" rod (snug)
register_depth = 0.100                # to the drill-tip; leaves 0.150" of plate

out_dir = Path(__file__).resolve().parent
out_name = "endcap-circular-2hole"


def make_disc() -> Path:
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    msp.add_circle((0, 0), disc_radius)
    for hole_center in hole_positions:
        msp.add_circle(hole_center, hole_radius)

    # The rod register is intentionally absent: it is a blind in-house drill
    # (register_position / register_drill_diameter / register_depth above), not
    # a through-cut. Emitting it here would pierce the pressure boundary.

    path = out_dir / f"{out_name}.dxf"
    export_dxf(doc, str(path))
    return path


def main() -> None:
    path = make_disc()
    print(f"Exported: {path}  ({len(hole_positions)} holes)")
    print(f"  Disc diameter:   {disc_diameter}\"  (fits 5.000\" OD x 0.065\" wall tube, ID 4.870\")")
    print(f"  Disc thickness:  {disc_thickness}\"")
    print(f"  Hole diameter:   {hole_diameter}\"  (7/16\" tap drill for 1/4\"-18 NPT)")
    print(f"  Hole spacing:    {hole_spacing:.4g}\" center-to-center along one axis")
    print(f"  Material:        316 SS, laser-cut")
    print(f"  Per vessel:      2 identical discs, each tapped 2x 1/4\"-18 NPT")
    print(f"  Rod register:    blind drill (NOT cut) at {register_position} in, "
          f"Ø{register_drill_diameter:.4g}\" x {register_depth:.3g}\" deep, from inside face")

    variables = {
        "DISC_D": f"{disc_diameter:.4g} in",
        "DISC_R": f"{disc_radius:.4g} in",
        "DISC_THK": f"{disc_thickness:.4g} in",
        "HOLE_D": f"{hole_diameter:.4g} in",
        "HOLE_R": f"{hole_radius:.4g} in",
        "HOLE_SPACING": f"{hole_spacing:.4g} in",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "DISC_D": 1,
            "DISC_R": 1,
            "DISC_THK": 1,
            "HOLE_D": 1,
            "HOLE_R": 1,
            "HOLE_SPACING": 1,
        },
    )


if __name__ == "__main__":
    main()
