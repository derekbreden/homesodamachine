"""PP0208E measured clearance reference, run on ±Z and branch on +Y.

Fixed roots/collars use the unscaled scan envelope; run and branch faces and
their distinct operating strokes use Derek's calipers. Terminal-ring detail
remains explicitly unqualified. This is an external clearance reference,
not a detailed internal fitting or manufacturing tolerance specification.
"""
import json
import sys
from pathlib import Path
import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _measuring import collet_offsets
from _cadq_export import export_assembly, import_step
from _materials import M_JG_BLACK_PP, one_body

STEP = _here.parent / "tee-connector.step"
BRANCH_MEASUREMENTS = _hw / "reference/jg-pp0208e-tee/branch-operating-measurements.json"
_branch = json.loads(BRANCH_MEASUREMENTS.read_text())

# Calipered operating dimensions. Insertion is from the PRESSED sleeve face.
TUBE_D = 6.35
RUN_SPAN = 42.5
RUN_SPAN_PRESSED = 39.2
RUN_HALF = RUN_SPAN / 2.0
RUN_COLLET_TRAVEL = (RUN_SPAN - RUN_SPAN_PRESSED) / 2.0
FIRST_RESISTANCE = 7.0
GRIP_DEPTH = 8.5
INSERTION = 10.0
RUN_INSERTION_EXTENDED = INSERTION + RUN_COLLET_TRAVEL

# Fitted collar midpoints are Ø16.224..16.330; the outer draft reaches the
# rounded Ø16.5 sample envelope. Printed passages add their own running air.
COLLAR_NOMINAL_D = 16.3
COLLAR_ENVELOPE_D = 16.5
BARREL_R = COLLAR_ENVELOPE_D / 2.0
HALF_W = BARREL_R
ARM_R = 7.0  # rounded envelope of the Ø13.75..13.86 fitted fixed roots
RUN_ROOT_BAND = (6.9, 9.8)
BRANCH_ROOT_BAND = (8.7, 11.7)
RUN_COLLAR_BAND = (12.0, 15.1)
BRANCH_COLLAR_BAND = (13.8, 16.6)
ARM_ROOT = BRANCH_ROOT_BAND[0]
CAP_NEAR, CAP_FAR = BRANCH_COLLAR_BAND
BARREL_NEAR = RUN_ROOT_BAND[0]
# These conservative envelope transitions precede the observed shoulders.
# The fit bands above are interior measurement patches, NOT shoulder edges.
RUN_ENVELOPE_SHOULDER = (9.8, 10.5)
BRANCH_ENVELOPE_SHOULDER = (11.7, 12.0)

# The caliper's back jaw meets the NOMINAL fixed collar, not the conservative
# clearance envelope. The resulting faces are nominal axis stations; the raw
# outside-to-outside readings remain the primary measurements.
BRANCH_WIDTH_EXTENDED = _branch["extended_width_mm"]
BRANCH_WIDTH_PRESSED = _branch["pressed_width_mm"]
BRANCH_REACH = BRANCH_WIDTH_EXTENDED - COLLAR_NOMINAL_D / 2.0
BRANCH_PRESSED_REACH = BRANCH_WIDTH_PRESSED - COLLAR_NOMINAL_D / 2.0
BRANCH_COLLET_TRAVEL = BRANCH_WIDTH_EXTENDED - BRANCH_WIDTH_PRESSED
if abs(BRANCH_COLLET_TRAVEL - _branch["branch_collet_travel_mm"]) > 1e-9:
    raise ValueError("branch stroke differs from its raw overall-width readings")
BRANCH_INSERTION_EXTENDED = INSERTION + BRANCH_COLLET_TRAVEL

# Fixed reduced barrels precede the small moving terminal rings. These are
# conservative clearance bounds around the observed scan surfaces, not exact
# molded shoulder or moving-ring seam measurements. Run and branch have
# distinct fixed profiles. No part of either fixed barrel moves on release.
FIXED_NOSE_R = 7.75
RUN_COLLAR_END = 15.75
BRANCH_COLLAR_END = 17.5
RUN_FIXED_END = 18.5
BRANCH_FIXED_END = 20.25
COLLET_NOSE_R = 5.715
BARREL_FAR = RUN_COLLAR_END
COLLET_PROUD = BRANCH_REACH - BRANCH_FIXED_END
UNQUALIFIED_DATUMS = {
    "run_fixed_nose_clearance_end_mm": RUN_FIXED_END,
    "branch_fixed_nose_clearance_end_mm": BRANCH_FIXED_END,
    "fixed_reduced_barrel_clearance_radius_mm": FIXED_NOSE_R,
    "release_nose_radius_mm": COLLET_NOSE_R,
    "qualification": "Fixed ends and sleeve radius are conservative clearance proxies; the exact terminal-ring seam/OD is not caliper-qualified.",
}
MEASURE_TOL = 0.01

CARRIER_AFT_COLLET_GAP = 0.5
CARRIER_STROKE = BRANCH_COLLET_TRAVEL + CARRIER_AFT_COLLET_GAP
CARRIER_MAX_STROKE = 2.5
if not BRANCH_COLLET_TRAVEL <= CARRIER_STROKE <= CARRIER_MAX_STROKE:
    raise ValueError("carrier stroke must release the sleeve within 2.5 mm")
CARRIER_RELEASE_OFFSET = 0.0
CARRIER_SQUEEZE_OFFSET = 0.0
CARRIER_CONNECTED_OFFSET = CARRIER_STROKE
CARRIER_PARK_OFFSET = CARRIER_STROKE
CARRIER_STATES = {
    "release": (CARRIER_RELEASE_OFFSET, INSERTION),
    "squeeze": (CARRIER_SQUEEZE_OFFSET, INSERTION),
    "connected": (CARRIER_CONNECTED_OFFSET, BRANCH_INSERTION_EXTENDED),
    "park": (CARRIER_PARK_OFFSET, None),
}


def carrier_collet_depression(offset: float) -> float:
    """Sleeve movement while its nose bears against the fixed release plate."""
    return min(BRANCH_COLLET_TRAVEL, max(0.0, BRANCH_COLLET_TRAVEL - offset))


def _cylinder(radius, near, far, axis):
    return cq.Solid.makeCylinder(radius, far - near,
                                 cq.Vector(*(near * a for a in axis)), cq.Vector(*axis))


def _fixed_arm(axis, shoulder, collar_end, fixed_end):
    """Measured radial envelopes joined before the observed shoulder.

    The reduced barrel remains fixed behind the terminal sleeve. The central
    root union and flat transition faces are conservative clearance envelopes;
    their edges do not claim measured molded shoulder stations.
    """
    near, far = shoulder
    root = _cylinder(ARM_R, 0.0, near, axis)
    transition = cq.Solid.makeCone(
        ARM_R, BARREL_R, far - near,
        cq.Vector(*(near * a for a in axis)), cq.Vector(*axis))
    collar = _cylinder(BARREL_R, far, collar_end, axis)
    nose = _cylinder(FIXED_NOSE_R, collar_end, fixed_end, axis)
    return root.fuse(transition, collar, nose)


def build(depression: float = 0.0):
    """Clearance reference with only the branch's terminal proxy sleeve moved."""
    if not 0.0 <= depression <= BRANCH_COLLET_TRAVEL + 1e-9:
        raise ValueError("branch depression exceeds the measured sleeve stroke")
    arms = []
    for axis, shoulder, collar_end, fixed_end, reach, travel in (
        ((0, 0, 1), RUN_ENVELOPE_SHOULDER, RUN_COLLAR_END, RUN_FIXED_END, RUN_HALF, 0.0),
        ((0, 0, -1), RUN_ENVELOPE_SHOULDER, RUN_COLLAR_END, RUN_FIXED_END, RUN_HALF, 0.0),
        ((0, 1, 0), BRANCH_ENVELOPE_SHOULDER, BRANCH_COLLAR_END, BRANCH_FIXED_END, BRANCH_REACH, depression),
    ):
        arms.extend((_fixed_arm(axis, shoulder, collar_end, fixed_end),
                     _cylinder(COLLET_NOSE_R, fixed_end - travel, reach - travel, axis)))
    solid = arms[0].fuse(*arms[1:]).clean()
    # Tube clearance bores do not claim teeth, an O-ring or the hydraulic bore.
    # The internal stop is a measured station, not an inferred scanned feature.
    bores = (_cylinder(TUBE_D / 2, -RUN_HALF - 1, RUN_HALF + 1, (0, 0, 1)),
             _cylinder(TUBE_D / 2, 0, BRANCH_REACH + 1, (0, 1, 0)))
    return solid.cut(*bores).clean()


def depress_branch(solid, depression: float):
    """Move the terminal proxy sleeve, preserving every measured fixed patch."""
    if not 0.0 <= depression <= BRANCH_COLLET_TRAVEL + 1e-9:
        raise ValueError("branch depression exceeds the measured sleeve stroke")
    if depression <= 1e-9:
        return solid
    bb = solid.BoundingBox()
    cutter = cq.Solid.makeBox(bb.xlen + 2, bb.ymax - BRANCH_FIXED_END + 1, bb.zlen + 2,
                             cq.Vector(bb.xmin - 1, BRANCH_FIXED_END, bb.zmin - 1))
    sleeve = solid.intersect(cutter)
    return solid.cut(cutter).fuse(sleeve.translate((0, -depression, 0))).clean()


def run(sign):
    return ((0.0, 0.0, sign * RUN_HALF), (0.0, 0.0, sign))


def run_barrel(sign):
    near, far = RUN_COLLAR_BAND
    return (((0.0, 0.0, sign * (near + far) / 2), (0.0, 0.0, sign)),
            BARREL_R, far - near)


def branch():
    return ((0.0, BRANCH_REACH, 0.0), (0.0, 1.0, 0.0))


def branch_collar():
    return (((0.0, (CAP_NEAR + CAP_FAR) / 2, 0.0), (0.0, 1.0, 0.0)),
            BARREL_R, CAP_FAR - CAP_NEAR)


def stations():
    return {"+z": run(1.0), "-z": run(-1.0), "branch": branch()}


def _branch_radius(solid, lo, hi):
    band = cq.Solid.makeBox(40, hi - lo, 50, cq.Vector(-20, lo, -25))
    bb = solid.intersect(band).BoundingBox()
    return max(bb.xmax, -bb.xmin, bb.zmax, -bb.zmin)


def _arm_radius(solid, lo, hi):
    band = cq.Solid.makeBox(40, 50, hi - lo, cq.Vector(-20, -25, lo))
    bb = solid.intersect(band).BoundingBox()
    return max(bb.xmax, -bb.xmin)


def stations_hold():
    """CAD consistency of the export, NOT qualification of UNQUALIFIED_DATUMS."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    for name, expected, got in (
        ("run span", RUN_SPAN, bb.zlen), ("positive run", RUN_HALF, bb.zmax),
        ("nominal extended branch face", BRANCH_REACH, bb.ymax),
        ("sample collar envelope", COLLAR_ENVELOPE_D, bb.xlen),
        ("run collar", BARREL_R, _arm_radius(solid, *RUN_COLLAR_BAND)),
        ("branch collar", BARREL_R, _branch_radius(solid, *BRANCH_COLLAR_BAND)),
        ("branch root", ARM_R, _branch_radius(solid, *BRANCH_ROOT_BAND)),
    ):
        if abs(expected - got) > MEASURE_TOL:
            raise ValueError(f"tee {name}: expected {expected:g}, exported {got:g}")
    for axis in ("z", "y"):
        if collet_offsets(solid, axis, TUBE_D / 2) != [(0.0, 0.0)]:
            raise ValueError(f"tee {axis} tube bore is off its declared axis")
    if abs(2 * (RUN_HALF - RUN_COLLET_TRAVEL) - RUN_SPAN_PRESSED) > MEASURE_TOL:
        raise ValueError("run sleeve stroke differs from the measured pressed run span")
    if abs(BRANCH_REACH + COLLAR_NOMINAL_D / 2 - BRANCH_WIDTH_EXTENDED) > MEASURE_TOL:
        raise ValueError("extended branch station differs from the nominal back-collar datum")
    pressed = depress_branch(solid, BRANCH_COLLET_TRAVEL)
    if abs(pressed.BoundingBox().ymax - BRANCH_PRESSED_REACH) > MEASURE_TOL:
        raise ValueError("branch sleeve does not provide the measured release travel")
    if abs(pressed.BoundingBox().ymax + COLLAR_NOMINAL_D / 2 - BRANCH_WIDTH_PRESSED) > MEASURE_TOL:
        raise ValueError("pressed branch station differs from the nominal back-collar datum")
    band = cq.Solid.makeBox(40, BRANCH_FIXED_END - CAP_NEAR, 50, cq.Vector(-20, CAP_NEAR, -25))
    if solid.intersect(band).cut(pressed).Volume() > 1e-7:
        raise ValueError("release travel removed fixed collar or reduced-barrel material")


def selftest():
    stations_hold()
    return ["measured collar envelopes, distinct run/branch strokes, nominal branch stations and fixed-barrel release check pass",
            "terminal-ring seam/OD and conservative fixed-nose envelope ends remain unqualified"]


def main():
    solid = build()
    if not solid.isValid() or len(solid.Solids()) != 1:
        raise ValueError("tee clearance reference must be one valid solid")
    export_assembly(one_body(cq.Workplane(obj=solid), "tee-connector", M_JG_BLACK_PP), str(STEP))
    for line in selftest():
        print(line)


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        for line in selftest():
            print(line)
    else:
        main()
