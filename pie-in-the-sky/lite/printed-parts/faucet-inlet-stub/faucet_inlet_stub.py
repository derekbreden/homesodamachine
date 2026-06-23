"""Lite-edition rear-panel carbonated-water pass-through — the
faucet-inlet stub. Carb water from the external Lillium carbonator enters
the rear panel, turns inward, crosses the DIGITEN flow meter (detected
flow triggers the flavor pumps), turns back, and exits the rear panel to
the faucet.

Flow path, port to port:
    Lillium hose
      -> bulkhead IN  (panel pass-through, +X side)
      -> elbow IN     (turns the run inward, toward the meter inlet)
      -> DIGITEN flow meter  (90° L-body, inlet and outlet at 90°)
      -> elbow OUT    (turns the run back toward the panel)
      -> bulkhead OUT (panel pass-through, -X side)
      -> faucet

The meter is the G1/4" 1/4"-PTC part: both ports take a 1/4" OD tube
directly, so the 1/4" elbows mate it without any reducer. Its two ports sit
at 90°, so it is set corner-down (the L straddling X=0), the inlet opening
toward the +X bulkhead and the outlet toward the -X bulkhead, both leaning
+Y toward the panel.

Coordinate frame
----------------
- Y = panel-normal : +Y is outside the enclosure (toward the Lillium hose
                     and the faucet); -Y is inside. The rear panel sits at
                     Y = 0, the bulkhead seating plane.
- X = lateral      : the two bulkheads straddle X = 0 at ±[38.65 mm](BULKHEAD_X);
                     the flow meter sits centered between them.
- Z = up.

The two bulkheads sit [77.3 mm](BULKHEAD_PITCH) apart on the panel — the
meter's two ports stand 27 mm off its center at 90°, and an elbow leg stands
off each port. The flow meter, both elbows, and the meter corner live inside
the enclosure at Y = -[63.44 mm](STUB_DEPTH_Y).
"""

import sys
import math
from pathlib import Path

import cadquery as cq

# This part lives under pie-in-the-sky/lite, a sibling of hardware/.
_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware").is_dir())
_hw = _repo / "hardware"
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_md, substitute_py_comments


_FLOW_SENSOR_STEP = _hw / "reference" / "digiten-flow-sensor" / "digiten-flow-sensor.step"
_ELBOW_STEP = _hw / "reference" / "elbow-connector" / "elbow-connector.step"
_BULKHEAD_STEP = _hw / "reference" / "jg-bulkhead-union" / "jg-bulkhead-union.step"


# --- Reference-part anchors (in each imported STEP's own frame) --------------
# Bulkhead (jg_bulkhead_union.py frame): axis along Y, panel-seating face at
# Y=0; the far ring face is its inner tube port, reaching into the enclosure.
bulkhead_far_ring_y = -24.79     # inner tube-port face, into the enclosure
# Elbow (elbow-connector.step frame): bend corner at the origin, each leg
# running out to its collet face.
elbow_leg = 19.56                # bend corner to collet face, both legs
# Flow sensor (digiten_flow_sensor.py frame): inlet +Y, outlet +X, each
# collet face this far from the body center along its own axis.
flow_port_face = 27.0            # collet face from center, each port


# --- Layout: 90° L-meter straddling X=0, inside the enclosure ----------------
# The meter is set corner-down (rotated 45° about Z) so its two 90° ports lean
# symmetrically toward the panel: the inlet opens up-and-toward +X, the outlet
# up-and-toward -X. Each port face then sits at lateral offset and depth
# flow_port_face/√2 from the meter center. An elbow turns each port's run +Y
# to the bulkhead's inner ring face; the bulkhead X is the elbow bend corner.
_diag = flow_port_face / math.sqrt(2.0)   # port-face X offset and Y rise, each port

# The meter center depth into the enclosure (-Y). The elbow axial leg
# (length elbow_leg) bridges from the bulkhead far ring face down to the
# elbow corner, which sits one elbow_leg in +Y above each port face.
meter_center_y = bulkhead_far_ring_y - elbow_leg - _diag   # meter center, -Y
stub_depth_y = meter_center_y                              # chain depth, -Y

# Each port face is at lateral ±_diag from center; the elbow's lateral leg
# meets it there and its bend corner sits one elbow_leg further out laterally,
# which sets the bulkhead axis.
bulkhead_x = _diag + elbow_leg            # elbow bend corner = bulkhead axis
bulkhead_pitch = 2.0 * bulkhead_x         # lateral spacing on the panel


def place_bulkhead(sign):
    """Bulkhead union through the panel at X = sign*bulkhead_x, axis along Y."""
    return (
        cq.importers.importStep(str(_BULKHEAD_STEP)).val()
        .translate((sign * bulkhead_x, 0.0, 0.0))
    )


def place_elbow(sign):
    """Elbow at the bulkhead's inner port: axial leg up +Y into the bulkhead
    far ring, lateral leg turned inward (toward X=0) to meet the meter port.

    Source elbow has legs on +Y and +Z meeting at the corner (origin). The +Y
    leg is the axial leg and stays +Y; rotating about Y swings the +Z leg into
    the lateral direction — -90 about Y sends +Z onto -X (inward for the +X
    bulkhead), +90 sends it onto +X (for the -X bulkhead). The corner lands at
    (sign*bulkhead_x, stub_depth_y + _diag, 0)."""
    fit = cq.importers.importStep(str(_ELBOW_STEP)).val()
    fit = fit.rotate((0, 0, 0), (0, 1, 0), -90 * sign)
    return fit.translate((sign * bulkhead_x, stub_depth_y + _diag, 0.0))


def place_flow_meter():
    """Flow meter centered at X=0 at the chain depth, rotated 45° about Z so its
    inlet (+Y) and outlet (+X) ports lean symmetrically toward the panel."""
    return (
        cq.importers.importStep(str(_FLOW_SENSOR_STEP)).val()
        .rotate((0, 0, 0), (0, 0, 1), 45)
        .translate((0.0, stub_depth_y, 0.0))
    )


PANEL_COLOR = cq.Color(0.85, 0.78, 0.62)
BULKHEAD_COLOR = cq.Color(0.55, 0.57, 0.60)   # gray acetal
ELBOW_COLOR = cq.Color(0.20, 0.22, 0.26)      # black PP
METER_COLOR = cq.Color(0.30, 0.55, 0.85)      # blue, to read clearly


def build():
    assy = cq.Assembly(name="faucet-inlet-stub")
    assy.add(place_bulkhead(+1), name="bulkhead-in", color=BULKHEAD_COLOR)
    assy.add(place_bulkhead(-1), name="bulkhead-out", color=BULKHEAD_COLOR)
    assy.add(place_elbow(+1), name="elbow-in", color=ELBOW_COLOR)
    assy.add(place_elbow(-1), name="elbow-out", color=ELBOW_COLOR)
    assy.add(place_flow_meter(), name="flow-meter", color=METER_COLOR)
    return assy


def main():
    export_assembly(build(), str(_here.parent / "faucet-inlet-stub.step"))
    print("-> faucet-inlet-stub.step")
    md_vars = {
        "BULKHEAD_X": f"{bulkhead_x:.4g}",
        "BULKHEAD_PITCH": f"{bulkhead_pitch:.4g}",
        "STUB_DEPTH_Y": f"{abs(stub_depth_y):.4g}",
    }
    substitute_md(
        _here.parent / "README.md",
        variables=md_vars,
        expected_counts={"BULKHEAD_X": 1, "BULKHEAD_PITCH": 1, "STUB_DEPTH_Y": 1},
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables={k: f"{v} mm" for k, v in md_vars.items()},
        expected_counts={"BULKHEAD_X": 1, "BULKHEAD_PITCH": 1, "STUB_DEPTH_Y": 1},
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
