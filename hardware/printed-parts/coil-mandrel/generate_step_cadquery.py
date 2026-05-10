"""
Plan A coil winding mandrel.

Open-tube mandrel for hand-winding 1/4" OD copper around a 5" round
316L pressure vessel.  Smooth outer surface (no helical guide groove):
the copper is wound by hand and pitch is set by feel or by pencil-mark
on the surface.

An earlier version cut a helical groove via parametricCurve + sweep,
but the boolean cut produced a degenerate solid (negative / zero volume,
isValid()=False) for helices wrapping more than a few turns — OCCT's
BOP can't reconcile the self-revisiting swept tube with the cylinder.
Plan B's coil-mandrel has the same bug; its STEP exports without
crashing but contains no real groove geometry either.

Pitch precision isn't function-critical — the coil's job is heat
conduction through the foil-tape interface, which doesn't care whether
loops sit at 9 mm or 11 mm spacing.  The groove was tooling polish, not
a functional feature.  The smooth-tube version is also half the print
time of the solid + low-infill original (no infill bridging, no surprises).

Springback compensation:
  Soft-annealed copper bent around the bare 5" tank releases to a
  1-3 mm radial gap.  Bending instead onto an undersize mandrel and
  stretching the resulting coil over the tank biases the spring
  direction inward — the loop wants to close to a smaller radius
  than the tank, so it clamps the coil against the tank + 3M 425 foil
  tape rather than springing away from it.

  Tank OD = 5.000" = 127.0 mm (R = 63.5 mm).  On a smooth (no groove)
  mandrel the wound copper centerline rests one tube radius (3.175 mm)
  outside the cylinder surface, so net copper bend radius =
  mandrel_R + TUBE_RAD.  ODs are picked so the bend radius is undersize
  relative to the tank by the desired springback compensation.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# ═══════════════════════════════════════════════════════
# PHYSICAL DIMENSIONS (inches → mm)
# ═══════════════════════════════════════════════════════

TUBE_OD_IN = 0.250                            # 1/4" copper tubing OD
TUBE_RAD   = (TUBE_OD_IN / 2) * 25.4          # 3.175 mm

TANK_OD_MM = 127.0                            # 5" carbonator tank OD
TANK_R     = TANK_OD_MM / 2                   # 63.5 mm

# Mandrel ODs to generate, in mm.  On a smooth mandrel, the wound copper
# centerline ends up at radius (mandrel_OD/2 + TUBE_RAD).  Net radial
# undersize relative to the 5" tank is shown for reference.
#
#   Mandrel OD   Copper bend R       Net undersize    Notes
#   ----------   --------------      -------------    -----
#   111.0 mm     55.5+3.175 = 58.7   4.8 mm           tighter clamp, harder install
#   113.0 mm     56.5+3.175 = 59.7   3.8 mm           recommended starting point
#   115.0 mm     57.5+3.175 = 60.7   2.8 mm           looser clamp, easier install
MANDREL_ODS_MM = [111.0, 113.0, 115.0]

# Open-tube wall thickness.  Mechanical loads on a winding mandrel are
# tiny — tangential bend force per loop is ~20 N and forces balance
# around the circumference (zero net crush, only distributed contact
# pressure).  2 mm PETG has roughly three orders of magnitude of margin
# in both beam bending and local crush.
WALL_MM = 2.0

# Mandrel length zones (along Z).
TOTAL_LEN_IN  = 7.5
HANDLE_LEN_IN = 0.75
WIND_LEN_IN   = 6.0    # matches the 6" tank tube height

TOTAL_LEN  = TOTAL_LEN_IN  * 25.4    # 190.5 mm
HANDLE_LEN = HANDLE_LEN_IN * 25.4    # 19.05 mm
WIND_LEN   = WIND_LEN_IN   * 25.4    # 152.4 mm


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def build_mandrel(mandrel_od_mm):
    outer_r = mandrel_od_mm / 2
    inner_r = outer_r - WALL_MM

    # Hollow open-tube: annular cross-section extruded along Z.  Open at
    # both ends — no end caps, so trapped-air problems don't happen
    # during print, and slicer doesn't need to bridge anything.
    return (
        cq.Workplane("XY")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(TOTAL_LEN)
    )


out_dir = Path(__file__).resolve().parent

for od in MANDREL_ODS_MM:
    mandrel = build_mandrel(od)
    solids = mandrel.solids().vals()
    bend_r = od / 2 + TUBE_RAD
    undersize = TANK_R - bend_r
    print(
        f"\nMandrel OD {od:.1f} mm "
        f"(copper bend R {bend_r:.2f} mm, "
        f"net undersize {undersize:.2f} mm): "
        f"{len(solids)} solid(s)"
    )
    for i, s in enumerate(solids):
        bb = s.BoundingBox()
        print(
            f"  Solid {i}: X[{bb.xmin:.1f},{bb.xmax:.1f}] "
            f"Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}], "
            f"V={s.Volume():.0f} mm^3"
        )
    out_path = out_dir / f"coil-mandrel-{int(round(od))}mm.step"
    export_step(mandrel, str(out_path))
    print(f"  Exported: {out_path}")
