"""Step-3 bench trial for the bowed tube between one anchor tee and one lifted valve.

This is tooling, not appliance geometry.  In the in-use frame:

* X runs across the fixture.
* Y is the anchor tee's release travel; +Y is the pull direction.
* Z runs from the anchor tee's upper run collet to the fixed valve's inlet.

The actual project reference geometry sets both seats.  At rest the two sleeve faces are
coaxial and 10.0 mm apart.  The tee's branch collar runs in a fixed journal, leaving the tee
free to translate along +Y while the valve stays in its ordinary four-post socket.  A separate
flat gauge carries the 12.0 mm exposed-tube witness and the 3.15 / 4.62 mm travel tongues.

The printable frame is exported already turned onto its broad rear face: Z=0 is the bed and
the valve sockets and tee journal open upward.  The assembly STEP stays in the in-use frame.

Run:
    tools/cad-venv/bin/python \
      hardware/printed-parts/fixtures/tee-valve-bow-trial/tee_valve_bow_trial.py
    tools/cad-venv/bin/python \
      hardware/printed-parts/fixtures/tee-valve-bow-trial/tee_valve_bow_trial.py selftest
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq


_here = Path(__file__).resolve()
_hw = next(parent for parent in _here.parents if parent.name == "hardware")
_repo = next(parent for parent in _here.parents if (parent / "tools" / "docgen").is_dir())
for _path in (
    _hw / "scripts",
    _hw / "reference" / "tee-connector",
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "enclosure" / "valve-tray",
    _hw / "printed-parts" / "valve-seat",
    _repo / "tools",
):
    sys.path.insert(0, str(_path))

from _cadq_export import export_assembly, import_step  # noqa: E402
from _material_base import M_PETGF_BLACK, one_body  # noqa: E402
from _materials import C_VALVE, M_JG_BLACK_PP  # noqa: E402
import beduan_solenoid as valve  # noqa: E402
import tee_connector as tee  # noqa: E402
import valve_tray as tray  # noqa: E402


# The four trial dimensions.  They are local on purpose: this fixture is the experiment which
# decides whether these provisional appliance dimensions survive contact with the real parts.
SLEEVE_FACE_SEPARATION = 10.0
EXPOSED_TUBE_LENGTH = 12.0
RELEASE_TRAVEL = 3.15
STROKE_CEILING = 4.62

# The tee-wall journal's current radial slip, copied here rather than importing the entire
# appliance assembly into a bench tool.  The reference tee supplies the collar radius.
TEE_COLLAR_RADIAL_SLIP = 0.25
TEE_JOURNAL_RADIUS = tee.BARREL_R + TEE_COLLAR_RADIAL_SLIP

# One actual valve-tray seat, backed by a broad flat trial card.  `tray.SEAT` places the valve's
# natural origin below the tray face so its central boss lands on that face, exactly as it does
# in enclosure-front-top.  Turning that local frame +90 degrees about X makes the valve inlet
# face down toward the tee.
FRAME_X = 70.0
FRAME_Z_MIN = -45.0
FRAME_Z_MAX = 66.5
VALVE_TRAY_FRAME_Y = -10.0
VALVE_TRAY_FRAME_Z = SLEEVE_FACE_SEPARATION + valve.port_length / 2.0

# After the valve-seat offset and the quarter turn, this is the Y axis shared by the valve port
# and the tee's run.  Putting the tee's branch nose at REST_DATUM_Y makes that nose flush with
# the fixture's rear datum at rest; its displacement can then be read directly with either
# travel tongue.
TEE_RUN_Y = VALVE_TRAY_FRAME_Y - (valve.port_center_z + tray.SEAT)
REST_DATUM_Y = TEE_RUN_Y + tee.BRANCH_REACH
TEE_RUN_CENTRE_Z = -tee.RUN_HALF

BACKING_FRONT_Y = 0.0
TEE_GUIDE_FRONT_Y = -3.0
TEE_GUIDE_HALF_X = 16.0
TEE_GUIDE_HALF_Z = 16.0
BACKING_T = REST_DATUM_Y - BACKING_FRONT_Y

GAUGE_T = 2.0
GAUGE_BODY_X = 22.0
GAUGE_BODY_Y = 28.0
GAUGE_WINDOW_X0 = 4.0
GAUGE_WINDOW_Y0 = 19.0
GAUGE_WINDOW_W = 7.0

MESH_TOLERANCE = 0.02
MESH_ANGLE = 0.15


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float):
    """Axis-aligned box from its six faces."""
    return cq.Workplane(
        obj=cq.Solid.makeBox(
            x1 - x0,
            y1 - y0,
            z1 - z0,
            cq.Vector(x0, y0, z0),
        )
    )


def _turn_valve_frame(shape):
    """Carry valve-frame geometry into the fixture's in-use frame."""
    return shape.rotate((0, 0, 0), (1, 0, 0), 90.0).translate(
        (0.0, VALVE_TRAY_FRAME_Y, VALVE_TRAY_FRAME_Z)
    )


def build_frame_in_use():
    """One-piece frame holding a fixed valve and journalling one translating tee."""
    backing = _box(
        -FRAME_X / 2.0,
        FRAME_X / 2.0,
        BACKING_FRONT_Y,
        REST_DATUM_Y,
        FRAME_Z_MIN,
        FRAME_Z_MAX,
    )

    # This is the production tray construction, reduced to one seat.  Its four socket bores,
    # port clearance and landing face therefore come from the actual valve reference rather
    # than a second fixture-only sketch of the valve.
    valve_plate = _turn_valve_frame(
        tray.build_valve_tray(FRAME_X, ((0.0, 0.0),))
    )

    guide = _box(
        -TEE_GUIDE_HALF_X,
        TEE_GUIDE_HALF_X,
        TEE_GUIDE_FRONT_Y,
        REST_DATUM_Y,
        TEE_RUN_CENTRE_Z - TEE_GUIDE_HALF_Z,
        TEE_RUN_CENTRE_Z + TEE_GUIDE_HALF_Z,
    )
    frame = backing.union(valve_plate).union(guide)

    # The bore is normal to the card in use and normal to the bed in the exported print pose.
    # It bears on the tee's branch collar, clears the narrower arm behind it, and remains on
    # 2.635 mm of collar at the 4.62 mm ceiling.
    bore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            TEE_JOURNAL_RADIUS,
            REST_DATUM_Y - TEE_GUIDE_FRONT_Y + 2.0,
            cq.Vector(0.0, TEE_GUIDE_FRONT_Y - 1.0, TEE_RUN_CENTRE_Z),
            cq.Vector(0.0, 1.0, 0.0),
        )
    )
    return frame.cut(bore)


def print_pose(shape):
    """Put the broad +Y rear face on Z=0 and move the print into positive X/Y."""
    return (
        shape.rotate((0, 0, 0), (1, 0, 0), -90.0)
        .translate((FRAME_X / 2.0, -FRAME_Z_MIN, REST_DATUM_Y))
    )


def build_gauge():
    """Flat gauge: 12 mm mark window plus 3.15 and 4.62 mm depth tongues.

    The body edge at X=GAUGE_BODY_X is the common stop face.  The narrow tongue is the
    release stroke; the wide tongue is the ceiling.  Their lengths lie in the print plane,
    independent of layer-height quantisation.
    """
    body = _box(0.0, GAUGE_BODY_X, 0.0, GAUGE_BODY_Y, 0.0, GAUGE_T)
    release_tongue = _box(
        GAUGE_BODY_X,
        GAUGE_BODY_X + RELEASE_TRAVEL,
        2.0,
        7.0,
        0.0,
        GAUGE_T,
    )
    ceiling_tongue = _box(
        GAUGE_BODY_X,
        GAUGE_BODY_X + STROKE_CEILING,
        10.0,
        18.0,
        0.0,
        GAUGE_T,
    )
    gauge = body.union(release_tongue).union(ceiling_tongue)
    window = _box(
        GAUGE_WINDOW_X0,
        GAUGE_WINDOW_X0 + EXPOSED_TUBE_LENGTH,
        GAUGE_WINDOW_Y0,
        GAUGE_WINDOW_Y0 + GAUGE_WINDOW_W,
        -1.0,
        GAUGE_T + 1.0,
    )
    return gauge.cut(window)


def build_tee_reference(travel: float = 0.0):
    """The harvested tee reference, seated in the guide at one release station."""
    return import_step(str(tee.STEP)).translate(
        (0.0, TEE_RUN_Y + travel, TEE_RUN_CENTRE_Z)
    )


def build_valve_reference():
    """The project Beduan reference, seated in the same socket geometry as the appliance."""
    seated = valve.build_beduan_solenoid().translate((0.0, 0.0, tray.SEAT))
    return _turn_valve_frame(seated)


def _valve_inlet_world() -> tuple[float, float, float]:
    """Reference inlet station after the seat translation and frame turn."""
    (x, y, z), _axis = valve.inlet()
    z += tray.SEAT
    return (
        x,
        VALVE_TRAY_FRAME_Y - z,
        VALVE_TRAY_FRAME_Z + y,
    )


def _tee_upper_face_world(travel: float = 0.0) -> tuple[float, float, float]:
    return (0.0, TEE_RUN_Y + travel, TEE_RUN_CENTRE_Z + tee.RUN_HALF)


def _circular_witness(chord: float, arc: float) -> tuple[float, float]:
    """Radius and sag of the minor circular arc with this chord and length.

    This is reported only as a comparison witness.  It is not a prescribed tube shape: the
    real short stub includes collet tilt and end compliance, which this trial exists to measure.
    """
    if not 0.0 < chord < arc:
        raise ValueError(f"a {arc:g} mm arc cannot span a {chord:g} mm chord")
    lo = chord / 2.0
    hi = 1.0e6
    for _ in range(100):
        radius = (lo + hi) / 2.0
        length = 2.0 * radius * math.asin(chord / (2.0 * radius))
        if length > arc:
            lo = radius
        else:
            hi = radius
    radius = (lo + hi) / 2.0
    sag = radius - math.sqrt(radius * radius - (chord / 2.0) ** 2)
    return radius, sag


def _single_valid(name: str, shape):
    solids = shape.solids().vals()
    if len(solids) != 1:
        raise ValueError(f"{name}: expected one solid, found {len(solids)}")
    if not solids[0].isValid() or solids[0].Volume() <= 0.0:
        raise ValueError(f"{name}: invalid or empty solid")
    return solids[0]


def _overlap(a, b) -> float:
    return a.intersect(b).val().Volume()


def selftest():
    tee.stations_hold()

    inlet = _valve_inlet_world()
    tee_face = _tee_upper_face_world()
    expected_inlet = (0.0, TEE_RUN_Y, SLEEVE_FACE_SEPARATION)
    if any(abs(a - b) > 1.0e-9 for a, b in zip(inlet, expected_inlet)):
        raise ValueError(f"valve inlet is {inlet}, expected {expected_inlet}")
    if any(abs(a - b) > 1.0e-9 for a, b in zip(tee_face, (0.0, TEE_RUN_Y, 0.0))):
        raise ValueError(f"tee upper face is {tee_face}, expected a Z=0 datum")
    if abs(math.dist(inlet, tee_face) - SLEEVE_FACE_SEPARATION) > 1.0e-9:
        raise ValueError("the two sleeve faces are not 10.0 mm apart at rest")
    if abs(REST_DATUM_Y - (TEE_RUN_Y + tee.BRANCH_REACH)) > 1.0e-9:
        raise ValueError("the fixed rear datum is not flush with the tee branch sleeve at rest")

    frame = build_frame_in_use()
    gauge = build_gauge()
    _single_valid("frame", frame)
    _single_valid("gauge", gauge)

    valve_reference = build_valve_reference()
    valve_overlap = _overlap(frame, valve_reference)
    if valve_overlap > 1.0e-5:
        raise ValueError(f"the seated valve and its frame overlap by {valve_overlap:.6f} mm^3")

    readings = []
    for label, travel in (
        ("rest", 0.0),
        ("release", RELEASE_TRAVEL),
        ("ceiling", STROKE_CEILING),
    ):
        tee_reference = build_tee_reference(travel)
        overlap = _overlap(frame, tee_reference)
        if overlap > 1.0e-5:
            raise ValueError(
                f"the tee and frame overlap by {overlap:.6f} mm^3 at {label} ({travel:g} mm)"
            )
        chord = math.dist(inlet, _tee_upper_face_world(travel))
        radius, sag = _circular_witness(chord, EXPOSED_TUBE_LENGTH)
        readings.append((label, travel, chord, radius, sag))

    # The guide must still carry real collar length at the ceiling, not merely clear the arm.
    collar_near = TEE_RUN_Y + STROKE_CEILING + tee.CAP_NEAR
    collar_overlap = REST_DATUM_Y - max(TEE_GUIDE_FRONT_Y, collar_near)
    if collar_overlap <= 0.0:
        raise ValueError("the tee branch collar has left its guide before the stroke ceiling")

    print(
        f"sleeve faces: {SLEEVE_FACE_SEPARATION:.2f} mm apart; "
        f"tee journal Ø{2.0 * TEE_JOURNAL_RADIUS:.3f} mm; "
        f"{collar_overlap:.3f} mm collar engagement at ceiling"
    )
    for label, travel, chord, radius, sag in readings:
        print(
            f"  {label:7s} Y={travel:4.2f} mm  chord={chord:8.5f} mm  "
            f"12 mm circular witness R={radius:8.5f}, sag={sag:8.5f} mm"
        )
    print("tee-valve bow trial selftest OK")
    return frame, gauge, valve_reference


def _export_print(name: str, shape):
    out = _here.parent
    step = out / f"tee-valve-bow-trial-{name}.step"
    stl = out / f"tee-valve-bow-trial-{name}.stl"
    # Write the slicer-facing mesh first.  `export_assembly` then sees that sibling and does not
    # mint an untracked viewer payload for this deliberately isolated trial.
    cq.exporters.export(
        shape,
        str(stl),
        tolerance=MESH_TOLERANCE,
        angularTolerance=MESH_ANGLE,
    )
    export_assembly(one_body(shape, f"tee-valve-bow-trial-{name}", M_PETGF_BLACK), str(step))
    solid = shape.val()
    bb = solid.BoundingBox()
    print(
        f"-> {step.name}, {stl.name}  "
        f"{bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm, "
        f"{solid.Volume() / 1000.0:.2f} cm^3"
    )


def main():
    frame, gauge, valve_reference = selftest()
    frame_print = print_pose(frame)
    _export_print("frame", frame_print)
    _export_print("gauge", gauge)

    assembly = cq.Assembly(name="tee-valve-bow-trial")
    assembly.add(frame, name="trial-frame", color=M_PETGF_BLACK)
    assembly.add(build_tee_reference(), name="pp0208e-tee-reference", color=M_JG_BLACK_PP)
    assembly.add(valve_reference, name="beduan-valve-reference", color=C_VALVE)
    export_assembly(assembly, str(_here.parent / "tee-valve-bow-trial-assembly.step"))
    print("-> tee-valve-bow-trial-assembly.step")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        sys.exit(selftest())
    elif sys.argv[1:]:
        sys.exit("usage: tee_valve_bow_trial.py [selftest]")
    else:
        sys.exit(main())
