"""Line-art reference solid of the neoFit ABU44 acetal bulkhead connector — the 1/4" tube
through-wall union the rear face's CO2 inlet is clamped in.

Reduced to coaxial cylinders: a collet body and release ring at each end with
the M17 barrel spanning the panel and separate nut. Figures come from neoFit's
*Bulkhead Union* dimensional sheet (`ABU44` row). Its B1/B2 dimensions are tube
stop depths. The external division about the flange is a nominal, unmeasured
reference; only the overall length and named panel/nut dimensions are drawn
from the sheet. Confirm received fitting dimensions before accepting this fit.

    Pressure          290 psi at 33 °F and 68 °F, 232 psi at 150 °F
    Max torque        1.1 ft lb on the nut
    Barrel            M17 × 1.5 — a PARALLEL metric thread, so the nut runs the whole length
                      of it and the panel is clamped between nut and flange
    Bag               10

The barrel sets the rear panel's clearance bore. The selected production grid
retains a 6 mm clamped stack between flange and nut, with the colored label
recess included in that stack.

Coordinate convention — jg_bulkhead_union's, so the two families seat the same way:
  Y = tube-flow axis. +Y = outward, toward the customer's tube.
  Origin = the flange's panel-seating face. The flange and everything beyond it sit at y ≥ 0;
      the barrel and the far end sit at y < 0.
  +Z = up. X completes the right-handed frame.

Run:
    tools/cad-venv/bin/python hardware/reference/neofit-bulkhead/neofit_bulkhead.py
    tools/cad-venv/bin/python hardware/reference/neofit-bulkhead/neofit_bulkhead.py selftest
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly
from _materials import M_NEOFIT_ACETAL, one_body  # noqa: E402
from world_workplane import xz_plane_y_up  # noqa: E402

STEP = _here.parent / "neofit-bulkhead.step"

_IN = 25.4


def _corners(across_flats: float) -> float:
    """A hex's across-corners envelope, which is what crowds a neighbour on a panel."""
    return across_flats / math.cos(math.radians(30.0))


# --- the ABU44 row of neoFit's Bulkhead Union sheet -------------------------

TUBE_OD = 6.35                    # 1/4" tube, both ends
THREAD_D = 17.0                   # M17 × 1.5 barrel — what the wall is bored for
THREAD_PITCH = 1.5
OVERALL = 1.346 * _IN             # L  — 34.188
FLANGE_AF = 0.748 * _IN           # H1 — 19.000 across flats
NUT_AF = 0.827 * _IN              # H2 — 21.006 across flats
TUBE_STOP_DEPTH = 0.665 * _IN     # B1 = B2; an internal insertion dimension
NOMINAL_OUTBOARD_REACH = 16.891   # unmeasured flange-to-mouth reference split
# A — 7.899, the BARE BARREL the sheet dimensions between the flange's face and the nut's. It is
# the clear span available to the panel before the separately dimensioned nut.
# The production wall and flush label share the selected 6 mm clamped stack.
PANEL_THREAD = 0.311 * _IN
NUT_LEN = 0.276 * _IN             # E  — 7.010
MASS_G = 9.4
PRESSURE_PSI_68F = 290.0
MAX_TORQUE_FTLB = 1.1

# The two hexes as the circles that crowd a neighbour on the wall.
FLANGE_D = _corners(FLANGE_AF)    # 21.939
NUT_D = _corners(NUT_AF)          # 24.256

# Seating planes along Y. The flange bears at y = 0 and stands proud outboard; the bare barrel
# and the inboard body run to y < 0.
#
# The separate nut is supplied by the panel assembly. A is the clear flange-to-nut
# span and E is the nut width: the threaded barrel continues through both. The
# inboard body begins beyond that complete span, so it does not occupy nut stock.
# Its radial envelope remains conservative and unmeasured.
near_ring_face_y = NOMINAL_OUTBOARD_REACH
far_ring_face_y = NOMINAL_OUTBOARD_REACH - OVERALL
far_body_face_y = -(PANEL_THREAD + NUT_LEN)
PROUD_LENGTH = near_ring_face_y   # what stands OUTSIDE the face it bears on


def panel_hole_d(clearance: float) -> float:
    """The through-hole diameter, given the slip a panel wants around the barrel."""
    return THREAD_D + clearance


def panel_footprint() -> tuple:
    """`(width, height)` the fitting takes on the panel FACE — the nut, which is the wider of
    its two hexes. Round to a neighbour, so one figure twice."""
    return (NUT_D, NUT_D)


def flange_footprint() -> float:
    """What the OUTBOARD flange covers, and so what a bulkhead ring has to reach past to show."""
    return FLANGE_D


def port(side: float) -> tuple:
    """One of the two 1/4" tube ports: `(position, outward axis)`, `side` picking the near
    (+Y, outboard) or far (−Y, inboard) end."""
    face = near_ring_face_y if side > 0 else far_ring_face_y
    return ((0.0, face, 0.0), (0.0, 1.0 if side > 0 else -1.0, 0.0))


def build_neofit_bulkhead():
    """The fitting as a single solid: flange, bare barrel, inboard body, bored through.

    The barrel spans the manufacturer's A + E panel-and-nut region. The panel
    assembly supplies the independent nut at its actual clamp plane."""
    flange = (cq.Workplane(xz_plane_y_up)
              .circle(FLANGE_D / 2.0).extrude(near_ring_face_y))
    barrel = (cq.Workplane(xz_plane_y_up)
              .circle(THREAD_D / 2.0).extrude(far_body_face_y))
    far = (cq.Workplane(xz_plane_y_up)
           .workplane(offset=far_ring_face_y)
           .circle(NUT_D / 2.0).extrude(far_body_face_y - far_ring_face_y))
    bore = (cq.Workplane(xz_plane_y_up)
            .workplane(offset=far_ring_face_y)
            .circle(TUBE_OD / 2.0).extrude(OVERALL))
    return flange.union(barrel).union(far).cut(bore)


def selftest() -> int:
    """The fitting against the sheet it is read from."""
    fails = []
    if abs((near_ring_face_y - far_ring_face_y) - OVERALL) > 1e-9:
        fails.append(
            f"the two end faces stand {near_ring_face_y - far_ring_face_y:.3f} apart and the "
            f"sheet's L is {OVERALL:.3f}")
    if FLANGE_D >= NUT_D:
        fails.append(
            f"the flange Ø{FLANGE_D:.3f} is not narrower than the nut Ø{NUT_D:.3f}, and "
            f"`panel_footprint` reports the nut as the wider")
    if TUBE_OD >= THREAD_D:
        fails.append(f"a Ø{TUBE_OD:g} bore does not fit inside a Ø{THREAD_D:g} barrel")
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"ok  neofit-bulkhead ABU44  M{THREAD_D:g}×{THREAD_PITCH:g}, "
              f"flange Ø{FLANGE_D:.2f} / nut Ø{NUT_D:.2f}, "
              f"{PANEL_THREAD:.2f} mm panel span plus {NUT_LEN:.2f} mm nut width, "
              f"{PRESSURE_PSI_68F:g} psi at 68 °F")
    return 1 if fails else 0


def main():
    part = build_neofit_bulkhead()
    bb = part.val().BoundingBox()
    print("neoFit ABU44 — 1/4\" acetal bulkhead connector")
    print(f"  barrel M{THREAD_D:g} × {THREAD_PITCH:g} / flange Ø{FLANGE_D:.3f} / "
          f"nut Ø{NUT_D:.3f}")
    print(f"  overall {OVERALL:.3f}, proud {PROUD_LENGTH:.3f}, "
          f"nominal external split; panel span {PANEL_THREAD:.3f}, nut width {NUT_LEN:.3f}")
    print(f"  Canonical-frame bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Solid valid: {part.val().isValid()}")
    export_assembly(one_body(part, "neofit-bulkhead", M_NEOFIT_ACETAL), str(STEP))
    print(f"-> {STEP.name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
