"""
Touch-Flo shell — printed shroud that wraps around the harvested faucet
body, the flavor tubes, and (eventually) the lever swing volume. Sits
on top of the touch-flo-mounting-plate.

WORK IN PROGRESS — GROWING BOTTOM-UP
====================================
This file is being grown one zone at a time, starting at the deck and
moving up. Right now it covers only ZONE 1 — the first 13 mm, where the
faucet body is still a full Ø 31.5 mm cylindrical base. Later zones
will be appended as we work our way up the body.

GEOMETRY (zone 1 only, so far)
==============================
- Outer:  filled cylinder, Ø 46 mm × 13 mm tall, centered at world
  (1.5875, 0) — same lateral center as the mounting plate.
- Z range: [0, 13]. Bottom face flush with the plate top (= deck).
- Inner hole at this level: union of TWO cuts that merge into a
  single connected opening because the body and the flavor tubes are
  tangent in the assembly:
    1. Body bore — Ø 32 mm at world (0, 0). 0.5 mm diametric
       clearance over the 31.5 mm body cylindrical base; slip-fit
       for assembly.
    2. Flavor-tube pill — same shape as the mounting plate's pill at
       world (17.3375, 0), 6.775 × 3.6 mm, Y-oriented.
  The pill's -X edge at X=15.5375 sits 0.4625 mm inside the body
  bore's +X edge at X=16, so the merged hole has a clean overlapping
  connection rather than a knife-edge tangent point.

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path

import cadquery as cq


# ═══════════════════════════════════════════════════════
# SHELL OUTER
# ═══════════════════════════════════════════════════════

SHELL_OUTER_DIAMETER = 46.0      # mm — smaller than the 50 mm mounting plate
SHELL_OUTER_R        = SHELL_OUTER_DIAMETER / 2.0
SHELL_CENTER_X       = 1.5875    # match the mounting plate's lateral center
SHELL_CENTER_Y       = 0.0


# ═══════════════════════════════════════════════════════
# ZONE 1 — first 13 mm; body is a full Ø 31.5 mm cylinder here
# ═══════════════════════════════════════════════════════

ZONE1_Z_BOTTOM = 0.0
ZONE1_Z_TOP    = 13.0
ZONE1_HEIGHT   = ZONE1_Z_TOP - ZONE1_Z_BOTTOM      # 13 mm

# Body bore — 0.5 mm diametric clearance over the 31.5 mm body
BODY_BORE_DIAMETER = 32.0
BODY_BORE_X        = 0.0
BODY_BORE_Y        = 0.0

# Flavor-tube pill (mirrored from the mounting plate)
FLAVOR_TUBE_X        = 17.3375
FLAVOR_TUBE_HOLE_DIA = 3.6
FLAVOR_TUBE_Y_OFFSET = 1.5875
PILL_LENGTH_Y = 2 * FLAVOR_TUBE_Y_OFFSET + FLAVOR_TUBE_HOLE_DIA   # 6.775
PILL_WIDTH_X  = FLAVOR_TUBE_HOLE_DIA                                # 3.6


# ═══════════════════════════════════════════════════════
# GEOMETRY BUILDERS
# ═══════════════════════════════════════════════════════

def build_zone1_outer() -> cq.Workplane:
    """Filled cylinder, the bottom 13 mm of the shell."""
    return (
        cq.Workplane("XY")
        .workplane(offset=ZONE1_Z_BOTTOM)
        .moveTo(SHELL_CENTER_X, SHELL_CENTER_Y)
        .circle(SHELL_OUTER_R)
        .extrude(ZONE1_HEIGHT)
    )


def build_zone1_inner_cut() -> cq.Workplane:
    """Combined body bore + flavor-tube pill, as one solid to subtract.

    The two shapes overlap by 0.4625 mm in X at the body/pill seam, so
    the result is a single connected hole.
    """
    body_bore = (
        cq.Workplane("XY")
        .workplane(offset=ZONE1_Z_BOTTOM)
        .moveTo(BODY_BORE_X, BODY_BORE_Y)
        .circle(BODY_BORE_DIAMETER / 2.0)
        .extrude(ZONE1_HEIGHT)
    )
    pill = (
        cq.Workplane("XY")
        .workplane(offset=ZONE1_Z_BOTTOM)
        .moveTo(FLAVOR_TUBE_X, 0)
        .slot2D(PILL_LENGTH_Y, PILL_WIDTH_X, angle=90)
        .extrude(ZONE1_HEIGHT)
    )
    return body_bore.union(pill)


def build_shell() -> cq.Workplane:
    """Top-level shell — at the moment, just zone 1."""
    return build_zone1_outer().cut(build_zone1_inner_cut())


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    shell = build_shell()

    out = Path(__file__).resolve().parent / "touch-flo-shell.step"
    cq.exporters.export(shell, str(out))

    print("Touch-Flo shell (work in progress)")
    print(f"  Outer:           Ø{SHELL_OUTER_DIAMETER} mm cylinder")
    print(f"  Center:          X = {SHELL_CENTER_X}, Y = {SHELL_CENTER_Y}")
    print(f"  Zone 1 height:   Z = {ZONE1_Z_BOTTOM} → {ZONE1_Z_TOP}")
    print(f"  Body bore:       Ø{BODY_BORE_DIAMETER} mm at "
          f"({BODY_BORE_X}, {BODY_BORE_Y})  "
          f"(0.5 mm clearance over 31.5 mm body)")
    print(f"  Flavor pill:     {PILL_LENGTH_Y} × {PILL_WIDTH_X} mm "
          f"at ({FLAVOR_TUBE_X}, 0), Y-oriented")
    print(f"-> {out.name}")
