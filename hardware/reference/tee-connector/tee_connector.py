"""PP0208E measured clearance reference, run on ±Z and branch on +Y.

Fixed roots/collars use the unscaled scan envelope; run faces and operating
stroke use Derek's calipers. The branch face and fixed/moving nose split remain
explicitly unqualified layout datums. This is an external clearance reference,
not a detailed internal fitting or manufacturing tolerance specification.
"""
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

# Calipered operating dimensions. Insertion is from the PRESSED sleeve face.
TUBE_D = 6.35
RUN_SPAN = 42.5
RUN_SPAN_PRESSED = 39.2
RUN_HALF = RUN_SPAN / 2.0
COLLET_TRAVEL = (RUN_SPAN - RUN_SPAN_PRESSED) / 2.0
FIRST_RESISTANCE = 7.0
GRIP_DEPTH = 8.5
INSERTION = 10.0
INSERTION_EXTENDED = INSERTION + COLLET_TRAVEL

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

# Retained layout proxies, NOT scan/caliper readings. Qualification of these
# axial/nose interfaces is independent of the known radial correction. The
# full collar envelope continues to the provisional body face. Only the
# separate terminal sleeve moves; none of the measured collar moves with it.
BRANCH_REACH = 20.07
BODY_FACE = 16.95
COLLET_NOSE_R = 5.715
BARREL_FAR = BODY_FACE
COLLET_PROUD = BRANCH_REACH - BODY_FACE
UNQUALIFIED_DATUMS = {
    "branch_extended_face_mm": BRANCH_REACH,
    "fixed_body_to_moving_sleeve_split_mm": BODY_FACE,
    "release_nose_radius_mm": COLLET_NOSE_R,
}
MEASURE_TOL = 0.01

CARRIER_AFT_COLLET_GAP = 0.5
CARRIER_STROKE = COLLET_TRAVEL + CARRIER_AFT_COLLET_GAP
CARRIER_MAX_STROKE = 2.5
if not COLLET_TRAVEL <= CARRIER_STROKE <= CARRIER_MAX_STROKE:
    raise ValueError("carrier stroke must release the sleeve within 2.5 mm")
CARRIER_RELEASE_OFFSET = 0.0
CARRIER_SQUEEZE_OFFSET = 0.0
CARRIER_CONNECTED_OFFSET = CARRIER_STROKE
CARRIER_PARK_OFFSET = CARRIER_STROKE
CARRIER_STATES = {
    "release": (CARRIER_RELEASE_OFFSET, INSERTION),
    "squeeze": (CARRIER_SQUEEZE_OFFSET, INSERTION),
    "connected": (CARRIER_CONNECTED_OFFSET, INSERTION_EXTENDED),
    "park": (CARRIER_PARK_OFFSET, None),
}


def carrier_collet_depression(offset: float) -> float:
    """Sleeve movement while its nose bears against the fixed release plate."""
    return min(COLLET_TRAVEL, max(0.0, COLLET_TRAVEL - offset))


def _cylinder(radius, near, far, axis):
    return cq.Solid.makeCylinder(radius, far - near,
                                 cq.Vector(*(near * a for a in axis)), cq.Vector(*axis))


def _fixed_arm(axis, shoulder):
    """Measured radial envelopes joined before the observed shoulder.

    The full collar envelope is retained to the provisional body face, so an
    unqualified chamfer cannot earn clearance. The central root union is also
    conservative. Neither connecting surface is a measured shoulder-edge datum.
    """
    near, far = shoulder
    root = _cylinder(ARM_R, 0.0, near, axis)
    transition = cq.Solid.makeCone(
        ARM_R, BARREL_R, far - near,
        cq.Vector(*(near * a for a in axis)), cq.Vector(*axis))
    collar = _cylinder(BARREL_R, far, BODY_FACE, axis)
    return root.fuse(transition, collar)


def build(depression: float = 0.0):
    """Clearance reference with only the branch's terminal proxy sleeve moved."""
    if not 0.0 <= depression <= COLLET_TRAVEL + 1e-9:
        raise ValueError("branch depression exceeds the measured sleeve stroke")
    arms = []
    for axis, shoulder, reach, travel in (
        ((0, 0, 1), RUN_ENVELOPE_SHOULDER, RUN_HALF, 0.0),
        ((0, 0, -1), RUN_ENVELOPE_SHOULDER, RUN_HALF, 0.0),
        ((0, 1, 0), BRANCH_ENVELOPE_SHOULDER, BRANCH_REACH, depression),
    ):
        arms.extend((_fixed_arm(axis, shoulder),
                     _cylinder(COLLET_NOSE_R, BODY_FACE - travel, reach - travel, axis)))
    solid = arms[0].fuse(*arms[1:]).clean()
    # Tube clearance bores do not claim teeth, an O-ring or the hydraulic bore.
    # The internal stop is a measured station, not an inferred scanned feature.
    bores = (_cylinder(TUBE_D / 2, -RUN_HALF - 1, RUN_HALF + 1, (0, 0, 1)),
             _cylinder(TUBE_D / 2, 0, BRANCH_REACH + 1, (0, 1, 0)))
    return solid.cut(*bores).clean()


def depress_branch(solid, depression: float):
    """Move the terminal proxy sleeve, preserving every measured fixed patch."""
    if not 0.0 <= depression <= COLLET_TRAVEL + 1e-9:
        raise ValueError("branch depression exceeds the measured sleeve stroke")
    if depression <= 1e-9:
        return solid
    bb = solid.BoundingBox()
    cutter = cq.Solid.makeBox(bb.xlen + 2, bb.ymax - BODY_FACE + 1, bb.zlen + 2,
                             cq.Vector(bb.xmin - 1, BODY_FACE, bb.zmin - 1))
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
        ("branch face proxy", BRANCH_REACH, bb.ymax),
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
    pressed = depress_branch(solid, COLLET_TRAVEL)
    if abs(pressed.BoundingBox().ymax - (BRANCH_REACH - COLLET_TRAVEL)) > MEASURE_TOL:
        raise ValueError("branch proxy sleeve does not provide the measured release travel")
    band = cq.Solid.makeBox(40, CAP_FAR - CAP_NEAR, 50, cq.Vector(-20, CAP_NEAR, -25))
    if solid.intersect(band).cut(pressed).Volume() > 1e-7:
        raise ValueError("release travel removed measured fixed collar material")


def selftest():
    stations_hold()
    return ["measured collar envelopes, run span, bores and fixed-collar release check pass",
            "branch axial face, body/sleeve seam and release rim remain unqualified"]


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
