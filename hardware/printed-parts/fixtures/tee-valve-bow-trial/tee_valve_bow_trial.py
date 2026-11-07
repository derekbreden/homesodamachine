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
    _repo / "tools",
):
    sys.path.insert(0, str(_path))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import beduan_solenoid as valve  # noqa: E402
import tee_connector as tee  # noqa: E402


# The four trial dimensions.  They are local on purpose: this fixture is the experiment which
# decides whether these provisional appliance dimensions survive contact with the real parts.

def _reference_inputs(method='state'):
    values = {}
    if method == 'numbers':
        import _rust_part
        from _material_base import M_PETGF_BLACK
        from _materials import C_VALVE, M_JG_BLACK_PP, linear
        values.update(
            tee_step=_rust_part.step(tee.STEP), valve_step=_rust_part.step(valve.STEP_PATH),
            black_color=list(linear(M_PETGF_BLACK)), tee_color=list(linear(M_JG_BLACK_PP)),
            valve_color=list(linear(C_VALVE)))
    return values

import pathlib as _reference_pathlib
_reference_hardware = next(p for p in _reference_pathlib.Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('tee_valve_bow_trial', inputs=_reference_inputs())
globals().update({name: _reference_values[name] for name in ('SLEEVE_FACE_SEPARATION', 'EXPOSED_TUBE_LENGTH', 'RELEASE_TRAVEL', 'STROKE_CEILING', 'TEE_COLLAR_RADIAL_SLIP', 'TEE_JOURNAL_RADIUS', 'FRAME_X', 'FRAME_Z_MIN', 'FRAME_Z_MAX', 'VALVE_TRAY_FRAME_Y', 'VALVE_TRAY_FRAME_Z', 'TEE_RUN_Y', 'REST_DATUM_Y', 'TEE_RUN_CENTRE_Z', 'BACKING_FRONT_Y', 'TEE_GUIDE_FRONT_Y', 'TEE_GUIDE_HALF_X', 'TEE_GUIDE_HALF_Z', 'BACKING_T', 'GAUGE_T', 'GAUGE_BODY_X', 'GAUGE_BODY_Y', 'GAUGE_WINDOW_X0', 'GAUGE_WINDOW_Y0', 'GAUGE_WINDOW_W', 'MESH_TOLERANCE', 'MESH_ANGLE')})


# The tee-wall journal's current radial slip, copied here rather than importing the entire
# appliance assembly into a bench tool.  The reference tee supplies the collar radius.

# One actual valve-tray seat, backed by a broad flat trial card.  The tray's `SEAT` places the valve's
# natural origin below the tray face so its central boss lands on that face, exactly as it does
# in enclosure-front-top.  Turning that local frame +90 degrees about X makes the valve inlet
# face down toward the tee.

# After the valve-seat offset and the quarter turn, this is the Y axis shared by the valve port
# and the tee's run.  Putting the tee's branch nose at REST_DATUM_Y makes that nose flush with
# the fixture's rear datum at rest; its displacement can then be read directly with either
# travel tongue.

# The complete translating run must clear the guide's fore face even at the
# experimental ceiling; the branch journal continues aft from that face.




def _valve_inlet_world():
    'Reference inlet station after the seat translation and frame turn.'
    return _reference_data('tee_valve_bow_trial', '_valve_inlet_world', (), {}, inputs=_reference_inputs())


def _tee_upper_face_world(travel: float=0.0):
    return _reference_data('tee_valve_bow_trial', '_tee_upper_face_world', (travel,), {}, inputs=_reference_inputs())


def _circular_witness(chord: float, arc: float):
    'Radius and sag of the minor circular arc with this chord and length.\n\n    This is reported only as a comparison witness.  It is not a prescribed tube shape: the\n    real short stub includes collet tilt and end compliance, which this trial exists to measure.\n    '
    return _reference_data('tee_valve_bow_trial', '_circular_witness', (chord, arc), {}, inputs=_reference_inputs())


def _readings():
    return _reference_data('tee_valve_bow_trial', '_readings', (), {}, inputs=_reference_inputs())


def numbers():
    'The unchanged trial stock, shared production seat cuts and reference placements.'
    return _reference_data('tee_valve_bow_trial', 'numbers', (), {}, inputs=_reference_inputs('numbers'))


def _report():
    return _reference_data('tee_valve_bow_trial', '_report', (), {}, inputs=_reference_inputs())


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
    from _part_output import summary
    for label, result in zip(("frame", "gauge"), said["results"]):
        body = result["bodies"][0]
        report = summary(body, volume_spec='.2f', span_spec='.2f')
        dims = report['dimensions']
        print(f"-> tee-valve-bow-trial-{label}.step, tee-valve-bow-trial-{label}.stl  "
              f"{dims[0]} x {dims[1]} x {dims[2]} mm, {report['volume']} cm^3")
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
