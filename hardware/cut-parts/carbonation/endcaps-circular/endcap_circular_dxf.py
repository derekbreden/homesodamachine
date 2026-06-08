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

out_dir = Path(__file__).resolve().parent
out_name = "endcap-circular-2hole"


def make_disc() -> Path:
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    msp.add_circle((0, 0), disc_radius)
    for hole_center in hole_positions:
        msp.add_circle(hole_center, hole_radius)

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
