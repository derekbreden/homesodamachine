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

import argparse
import math
import sys
from pathlib import Path

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

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

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
VALVE_TRAY_FRAME_Y = -tray.THICK
VALVE_TRAY_FRAME_Z = SLEEVE_FACE_SEPARATION + valve.port_length / 2.0

# After the valve-seat offset and the quarter turn, this is the Y axis shared by the valve port
# and the tee's run.  Putting the tee's branch nose at REST_DATUM_Y makes that nose flush with
# the fixture's rear datum at rest; its displacement can then be read directly with either
# travel tongue.
TEE_RUN_Y = VALVE_TRAY_FRAME_Y - (valve.port_center_z + tray.SEAT)
REST_DATUM_Y = TEE_RUN_Y + tee.BRANCH_REACH
TEE_RUN_CENTRE_Z = -tee.RUN_HALF

BACKING_FRONT_Y = 0.0
# The complete translating run must clear the guide's fore face even at the
# experimental ceiling; the branch journal continues aft from that face.
TEE_GUIDE_FRONT_Y = TEE_RUN_Y + STROKE_CEILING + tee.HALF_W + TEE_COLLAR_RADIAL_SLIP
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


def _readings():
    inlet = _valve_inlet_world()
    tee_face = _tee_upper_face_world()
    expected = (0.0, TEE_RUN_Y, SLEEVE_FACE_SEPARATION)
    if any(abs(a - b) > 1.0e-9 for a, b in zip(inlet, expected)):
        raise ValueError(f"valve inlet is {inlet}, expected {expected}")
    if any(abs(a - b) > 1.0e-9 for a, b in zip(tee_face, (0.0, TEE_RUN_Y, 0.0))):
        raise ValueError(f"tee upper face is {tee_face}, expected a Z=0 datum")
    collar_near = TEE_RUN_Y + STROKE_CEILING + tee.CAP_NEAR
    engagement = REST_DATUM_Y - max(TEE_GUIDE_FRONT_Y, collar_near)
    if engagement <= 0.0:
        raise ValueError("the tee branch collar has left its guide before the stroke ceiling")
    readings = []
    for label, travel in (("rest", 0.0), ("release", RELEASE_TRAVEL), ("ceiling", STROKE_CEILING)):
        chord = math.dist(inlet, _tee_upper_face_world(travel))
        radius, sag = _circular_witness(chord, EXPOSED_TUBE_LENGTH)
        readings.append((label, travel, chord, radius, sag))
    return engagement, readings


def numbers():
    """The unchanged trial stock, shared production seat cuts and reference placements."""
    import _rust_part
    from _material_base import M_PETGF_BLACK
    from _materials import C_VALVE, M_JG_BLACK_PP, linear
    engagement, _ = _readings()
    return {
        "backing": [-FRAME_X/2, FRAME_X/2, BACKING_FRONT_Y, REST_DATUM_Y, FRAME_Z_MIN, FRAME_Z_MAX],
        "guide": [-TEE_GUIDE_HALF_X, TEE_GUIDE_HALF_X, TEE_GUIDE_FRONT_Y, REST_DATUM_Y,
                  TEE_RUN_CENTRE_Z-TEE_GUIDE_HALF_Z, TEE_RUN_CENTRE_Z+TEE_GUIDE_HALF_Z],
        "tray": tray.tray_stock_numbers(FRAME_X, ((0.0, 0.0),)),
        "valve_frame": [0.0, VALVE_TRAY_FRAME_Y, VALVE_TRAY_FRAME_Z],
        "valve_seat_shift": [0.0, 0.0, tray.SEAT],
        "journal": [TEE_JOURNAL_RADIUS, TEE_GUIDE_FRONT_Y-1.0,
                    REST_DATUM_Y-TEE_GUIDE_FRONT_Y+2.0, TEE_RUN_CENTRE_Z],
        "print_shift": [FRAME_X/2.0, -FRAME_Z_MIN, REST_DATUM_Y],
        "gauge_stock": [[0.0, GAUGE_BODY_X, 0.0, GAUGE_BODY_Y, 0.0, GAUGE_T],
                        [GAUGE_BODY_X, GAUGE_BODY_X+RELEASE_TRAVEL, 2.0, 7.0, 0.0, GAUGE_T],
                        [GAUGE_BODY_X, GAUGE_BODY_X+STROKE_CEILING, 10.0, 18.0, 0.0, GAUGE_T]],
        "gauge_window": [GAUGE_WINDOW_X0, GAUGE_WINDOW_X0+EXPOSED_TUBE_LENGTH,
                         GAUGE_WINDOW_Y0, GAUGE_WINDOW_Y0+GAUGE_WINDOW_W, -1.0, GAUGE_T+1.0],
        "tee_step": _rust_part.step(tee.STEP),
        "valve_step": _rust_part.step(valve.STEP_PATH),
        "tee_translation": [0.0, TEE_RUN_Y, TEE_RUN_CENTRE_Z],
        "travels": [0.0, RELEASE_TRAVEL, STROKE_CEILING],
        "collar_engagement": engagement,
        "tee_checks": {
            "tolerance": tee.MEASURE_TOL,
            "bounds": [tee.RUN_SPAN, tee.RUN_HALF, tee.BRANCH_REACH, tee.COLLAR_ENVELOPE_D],
            "bands": [[0.0, *tee.RUN_COLLAR_BAND, tee.BARREL_R],
                      [1.0, *tee.BRANCH_COLLAR_BAND, tee.BARREL_R],
                      [1.0, *tee.BRANCH_ROOT_BAND, tee.ARM_R]],
            "pressed_branch": [tee.BRANCH_FIXED_END, tee.BRANCH_COLLET_TRAVEL, tee.BRANCH_PRESSED_REACH],
        },
        "black": list(linear(M_PETGF_BLACK)), "tee_color": list(linear(M_JG_BLACK_PP)),
        "valve_color": list(linear(C_VALVE)),
    }


def _report():
    engagement, readings = _readings()
    print(f"sleeve faces: {SLEEVE_FACE_SEPARATION:.2f} mm apart; "
          f"tee journal Ø{2.0 * TEE_JOURNAL_RADIUS:.3f} mm; "
          f"{engagement:.3f} mm collar engagement at ceiling")
    for label, travel, chord, radius, sag in readings:
        print(f"  {label:7s} Y={travel:4.2f} mm  chord={chord:8.5f} mm  "
              f"12 mm circular witness R={radius:8.5f}, sag={sag:8.5f} mm")
    print("tee-valve bow trial selftest OK")


def selftest():
    import _rust_part
    result = _rust_part.check("tooling", "tee-valve-bow-trial", numbers())
    _report()
    return result


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut("tooling", "tee-valve-bow-trial", numbers(), out)
    _report()
    for label, result in zip(("frame", "gauge"), said["results"]):
        body = result["bodies"][0]
        dims = [b-a for a, b in zip(body["min"], body["max"])]
        print(f"-> tee-valve-bow-trial-{label}.step, tee-valve-bow-trial-{label}.stl  "
              f"{dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} mm, {body['volume']/1000:.2f} cm^3")
    print("-> tee-valve-bow-trial-assembly.step")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=["selftest"])
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    if options.command == "selftest":
        selftest()
    else:
        sys.exit(main(options.output))
