"""
Touch-Flo faucet assembly — work-in-progress build-up of the user's
faucet vision on top of the reference valve body.

WHAT THIS IS
============
A growing assembly model that combines the harvested Touch-Flo valve
body (read from `../valve-body-reference/touch-flo-valve-body-reference.step`)
with the parts we are designing around it. The script writes a single
multi-solid STEP file so each iteration can be eyeballed in a viewer.

This is NOT the printed shell. The shell will be a separate file that
wraps around the assembly described here. This file is the body +
tubes + (eventually) other inserts that the shell must accommodate.

PARTS CURRENTLY MODELED
=======================
1. Valve body (loaded from the reference STEP — never modified here).
2. Water dispense tube — Ø 9.5 mm × straight section, inserted into
   the body's water port and extending 40 mm above the plateau.
   O-rings on the actual tube exist but are not modeled (geometry
   only; envelope is the bare 9.5 mm OD).
3. Two flavor dispense tubes — Ø 1/8" (3.175 mm), behind the water
   tube. Each tube starts at X = BODY_R + tube_R = 17.3375 mm (butting
   against the body's +X rectangular face and the other flavor tube),
   runs vertical from Z = -50, then S-bends just above the plateau to
   come in tangent against the water tube. After the bends the tubes
   run vertical to Z = 79, butted against the water tube. Not inserted
   into the body.

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

import math
from pathlib import Path

import cadquery as cq


# ═══════════════════════════════════════════════════════
# REFERENCE BODY GEOMETRY (mirrored from valve-body-reference)
# ═══════════════════════════════════════════════════════
#
# These constants are duplicated from
# `../valve-body-reference/generate_step_cadquery.py`.
# If they change there, update them here too.
#
PORT_CENTER_X = 8.875        # mm — water port center (X axis)
PORT_CENTER_Y = 0.0          # mm — water port center (Y axis)
PLATEAU_Z     = 39.0         # mm — top face of the rectangular body
BODY_OD       = 31.50        # mm — cylinder OD = rectangle long dim
BODY_R        = BODY_OD / 2  # mm — 15.75 mm
SHANK_LENGTH  = 50.0         # mm — shank extends from Z=0 down to Z=-SHANK_LENGTH


# ═══════════════════════════════════════════════════════
# WATER DISPENSE TUBE
# ═══════════════════════════════════════════════════════
#
# A straight Ø 9.5 mm tube that drops into the 9.75 mm water port.
# The 0.25 mm radial gap is taken up by O-rings on the real tube
# (not modeled). The tube extends a comfortable amount into the
# port for retention, and 40 mm above the plateau for visualization.
# Eventually this tube will be bent; for now it is a straight stub.
#
WATER_TUBE_OD            = 9.5    # mm — outer diameter of the tube body
WATER_TUBE_ABOVE_PLATEAU = 40.0   # mm — length above the plateau
WATER_TUBE_INTO_PORT     = 15.0   # mm — length inserted into the port

WATER_TUBE_Z_BOTTOM = PLATEAU_Z - WATER_TUBE_INTO_PORT     # 24.0 mm
WATER_TUBE_Z_TOP    = PLATEAU_Z + WATER_TUBE_ABOVE_PLATEAU # 79.0 mm
WATER_TUBE_LENGTH   = WATER_TUBE_Z_TOP - WATER_TUBE_Z_BOTTOM


# ═══════════════════════════════════════════════════════
# FLAVOR DISPENSE TUBES (×2)
# ═══════════════════════════════════════════════════════
#
# Two Ø 1/8" tubes behind the water tube. They are NOT inserted into
# the body — they sit alongside it. Each tube is tangent to:
#   - the +X rectangular face of the body (X = BODY_R = 15.75 mm)
#   - the other flavor tube (so both touch at Y = 0)
#
# Mirror across the X-Z plane: one at +Y, one at -Y.
# Tube centers are therefore at:
#   X = BODY_R + (FLAVOR_TUBE_OD / 2) = 17.3375 mm
#   Y = ± (FLAVOR_TUBE_OD / 2)        = ±1.5875 mm
#
# Z span matches the working height of the assembly:
#   bottom = bottom of the shank (Z = -SHANK_LENGTH = -50 mm)
#   top    = top of the water tube  (Z = WATER_TUBE_Z_TOP = 79 mm)
#
FLAVOR_TUBE_OD       = 1.0/8.0 * 25.4   # 3.175 mm — 1/8"
FLAVOR_TUBE_R        = FLAVOR_TUBE_OD / 2.0
FLAVOR_TUBE_X        = BODY_R + FLAVOR_TUBE_R           # 17.3375 mm — initial X
FLAVOR_TUBE_Y_OFFSET = FLAVOR_TUBE_R                    # ±1.5875 mm — constant
FLAVOR_TUBE_Z_BOTTOM = -SHANK_LENGTH                    # -50.0 mm
FLAVOR_TUBE_Z_TOP    = WATER_TUBE_Z_TOP                 # 79.0 mm

# S-bend geometry: each flavor tube rises vertical, S-bends in toward
# the water tube just above the plateau, then runs vertical again
# tangent to the water tube up to the top.
#
# Final X position is set by tangency to the water tube at the same Y:
#   (X_FINAL - PORT_CENTER_X)² + Y_OFFSET² = (WATER_TUBE_R + FLAVOR_TUBE_R)²
# with Y constant through both bends.
WATER_TUBE_R = WATER_TUBE_OD / 2.0
_dx_sq = (WATER_TUBE_R + FLAVOR_TUBE_R) ** 2 - FLAVOR_TUBE_Y_OFFSET ** 2
FLAVOR_TUBE_X_FINAL = PORT_CENTER_X + math.sqrt(_dx_sq)  # 15.012 mm

# X offset the S-bend has to absorb (positive number, magnitude only)
_x_offset = FLAVOR_TUBE_X - FLAVOR_TUBE_X_FINAL          # 2.326 mm

# Bend radius: chosen for clean hand-bending of 1/8" SS — 2.5× OD,
# well above the kink threshold and visually generous.
FLAVOR_BEND_RADIUS    = 8.0
# Bend angle is then derived: 2·R·(1 − cos θ) = X_offset (with no middle
# straight). Both bends use the same radius and angle.
FLAVOR_BEND_THETA_RAD = math.acos(1.0 - _x_offset / (2.0 * FLAVOR_BEND_RADIUS))
FLAVOR_BEND_THETA_DEG = math.degrees(FLAVOR_BEND_THETA_RAD)

# How far above the plateau the first bend starts. Kept short to mimic
# the user's "shortly after that, as shortly as is reasonable."
PRE_BEND_RISE = 3.0                                      # mm above plateau
PRE_BEND_Z    = PLATEAU_Z + PRE_BEND_RISE                # 42.0 mm

# Geometry checks:
#  - lower straight (tube-local Z=0 → Z=PRE_BEND_Z − Z_BOTTOM = 94 mm)
#  - bend 1 (arc length R·θ ≈ 4.4 mm, Z gain R·sin θ ≈ 4.2 mm)
#  - bend 2 (mirror of bend 1)
#  - upper straight (remainder up to Z_TOP)


# ═══════════════════════════════════════════════════════
# REFERENCE BODY LOADING
# ═══════════════════════════════════════════════════════

REF_BODY_STEP = (
    Path(__file__).resolve().parent.parent
    / "valve-body-reference"
    / "touch-flo-valve-body-reference.step"
)


def load_valve_body() -> cq.Workplane:
    """Load the harvested valve body from the reference STEP file.

    Read-only — this file never modifies the body geometry.
    """
    return cq.importers.importStep(str(REF_BODY_STEP))


# ═══════════════════════════════════════════════════════
# TUBE BUILDERS
# ═══════════════════════════════════════════════════════

def build_water_dispense_tube() -> cq.Workplane:
    """A straight Ø 9.5 mm cylinder sitting in the water port.

    Centered on the port location in X-Y; spans from inside the port
    (Z = WATER_TUBE_Z_BOTTOM) to WATER_TUBE_Z_TOP above the plateau.
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=WATER_TUBE_Z_BOTTOM)
        .center(PORT_CENTER_X, PORT_CENTER_Y)
        .circle(WATER_TUBE_OD / 2.0)
        .extrude(WATER_TUBE_LENGTH)
    )


def _arc_from_tangent(start, tangent, radius, theta_rad, ccw):
    """Compute waypoints of an arc starting at `start` with `tangent`,
    sweeping `theta_rad` with the given `radius`.

    ccw=True: tangent rotates counterclockwise (tube turns left when
    looking along +Y).
    ccw=False: clockwise.

    Returns (mid, end, end_tangent) — all in the same 2D X-Z frame.
    """
    sign = +1 if ccw else -1
    # Center is perpendicular to tangent, on the bending side.
    if ccw:
        perp = (-tangent[1], tangent[0])    # rotate tangent +90°
    else:
        perp = (tangent[1], -tangent[0])    # rotate tangent -90°
    center = (start[0] + radius * perp[0], start[1] + radius * perp[1])

    # Radial vector from center to start.
    rad = (start[0] - center[0], start[1] - center[1])

    def _rot(v, a):
        c, s = math.cos(a), math.sin(a)
        return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)

    rad_mid = _rot(rad, sign * theta_rad / 2.0)
    rad_end = _rot(rad, sign * theta_rad)

    mid = (center[0] + rad_mid[0], center[1] + rad_mid[1])
    end = (center[0] + rad_end[0], center[1] + rad_end[1])
    end_tangent = _rot(tangent, sign * theta_rad)

    return mid, end, end_tangent


def _build_flavor_tube_at_origin() -> cq.Workplane:
    """Build one bent flavor tube at the origin.

    Tube-local frame: bottom of the tube at Z = 0, X = 0, going +Z.
    The S-bend translates the upper section by `_x_offset` in -X.
    The Y axis is the workplane's normal (the tube lives in the X-Z
    plane); the caller translates the result to its target (X, Y, Z).
    """
    pre_bend_z_local = PRE_BEND_Z - FLAVOR_TUBE_Z_BOTTOM         # 94.0 mm
    top_z_local      = FLAVOR_TUBE_Z_TOP - FLAVOR_TUBE_Z_BOTTOM  # 129.0 mm

    p0 = (0.0, 0.0)
    p1 = (0.0, pre_bend_z_local)

    # Bend 1: tangent (0,1) rotates CCW by θ → (−sin θ, cos θ).
    mid1, end1, tan1 = _arc_from_tangent(
        p1, (0.0, 1.0), FLAVOR_BEND_RADIUS, FLAVOR_BEND_THETA_RAD, ccw=True
    )
    # Bend 2: tangent rotates CW by θ → back to (0, 1).
    mid2, end2, tan2 = _arc_from_tangent(
        end1, tan1, FLAVOR_BEND_RADIUS, FLAVOR_BEND_THETA_RAD, ccw=False
    )

    # Final straight from end of bend 2 up to Z_TOP, X unchanged.
    p_top = (end2[0], top_z_local)

    path = (
        cq.Workplane("XZ")
        .moveTo(*p0)
        .lineTo(*p1)
        .threePointArc(mid1, end1)
        .threePointArc(mid2, end2)
        .lineTo(*p_top)
    )

    profile = cq.Workplane("XY").circle(FLAVOR_TUBE_R)

    return profile.sweep(path, transition="round")


def build_flavor_tube(y_sign: int) -> cq.Workplane:
    """One Ø 1/8" flavor tube placed at its world position.

    Built at the origin, then translated to (FLAVOR_TUBE_X,
    y_sign · FLAVOR_TUBE_Y_OFFSET, FLAVOR_TUBE_Z_BOTTOM).
    """
    tube = _build_flavor_tube_at_origin()
    return tube.translate((
        FLAVOR_TUBE_X,
        y_sign * FLAVOR_TUBE_Y_OFFSET,
        FLAVOR_TUBE_Z_BOTTOM,
    ))


# ═══════════════════════════════════════════════════════
# ASSEMBLY
# ═══════════════════════════════════════════════════════

def build_assembly() -> cq.Assembly:
    """Combine the reference body and our new parts into one assembly."""
    body = load_valve_body()
    water_tube = build_water_dispense_tube()
    flavor_tube_pos_y = build_flavor_tube(+1)
    flavor_tube_neg_y = build_flavor_tube(-1)

    silver = cq.Color(0.85, 0.85, 0.88)   # near-stainless silver

    assy = cq.Assembly(name="touch-flo-faucet-assembly")
    assy.add(body, name="valve_body", color=cq.Color("black"))
    assy.add(water_tube, name="water_dispense_tube", color=silver)
    assy.add(flavor_tube_pos_y, name="flavor_tube_pos_y", color=silver)
    assy.add(flavor_tube_neg_y, name="flavor_tube_neg_y", color=silver)
    return assy


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    assy = build_assembly()

    here = Path(__file__).resolve().parent
    out  = here / "touch-flo-faucet-assembly.step"
    # cq.Assembly.save() emits a deprecation warning in this CadQuery
    # version but still produces correct multi-solid STEP. The
    # cq.exporters.export(assy, ...) replacement currently rejects
    # Assembly objects on this install — revisit when the venv is bumped.
    assy.save(str(out))

    print("Touch-Flo faucet assembly")
    print(f"  Reference body:        {REF_BODY_STEP.name}")
    print(f"  Water dispense tube:   Ø{WATER_TUBE_OD} mm "
          f"× {WATER_TUBE_LENGTH:.1f} mm long")
    print(f"                         Z = {WATER_TUBE_Z_BOTTOM:.1f} → {WATER_TUBE_Z_TOP:.1f}")
    print(f"                         {WATER_TUBE_INTO_PORT} mm into port + "
          f"{WATER_TUBE_ABOVE_PLATEAU} mm above plateau")
    print(f"                         center at X={PORT_CENTER_X} mm, Y={PORT_CENTER_Y} mm")
    print(f"  Flavor tubes (×2):     Ø{FLAVOR_TUBE_OD:.3f} mm")
    print(f"                         Z = {FLAVOR_TUBE_Z_BOTTOM:.1f} → {FLAVOR_TUBE_Z_TOP:.1f}")
    print(f"                         lower X = {FLAVOR_TUBE_X:.4f} mm "
          f"(tangent to body +X + to each other)")
    print(f"                         upper X = {FLAVOR_TUBE_X_FINAL:.4f} mm "
          f"(tangent to water tube + to each other)")
    print(f"                         Y = ±{FLAVOR_TUBE_Y_OFFSET:.4f} mm (constant)")
    print(f"                         S-bend: 2 × R{FLAVOR_BEND_RADIUS:.1f} mm "
          f"@ {FLAVOR_BEND_THETA_DEG:.2f}° starting at Z = {PRE_BEND_Z:.1f}")
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
