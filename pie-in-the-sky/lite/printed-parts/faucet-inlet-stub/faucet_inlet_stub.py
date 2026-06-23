"""Lite-edition rear-panel carbonated-water pass-through — the
faucet-inlet stub. Carb water from the external Lillium carbonator enters
the rear panel, turns inward, crosses the DIGITEN flow meter (detected
flow triggers the flavor pumps), turns back, and exits the rear panel to
the faucet.

Flow path, port to port:
    Lillium hose
      -> bulkhead IN  (panel pass-through, +X side)
      -> elbow IN     (turns the run inward, toward -X)
      -> reducer      (3/8" PTC -> 1/4" PTC)
      -> DIGITEN flow meter  (axis along X, inside the enclosure)
      -> reducer      (1/4" PTC -> 3/8" PTC)
      -> elbow OUT    (turns the run back toward the panel)
      -> bulkhead OUT (panel pass-through, -X side)
      -> faucet

Coordinate frame
----------------
- Y = panel-normal : +Y is outside the enclosure (toward the Lillium hose
                     and the faucet); -Y is inside. The rear panel sits at
                     Y = 0, the bulkhead seating plane.
- X = lateral      : the two bulkheads straddle X = 0 at ±[79.56 mm](BULKHEAD_X);
                     the flow meter spans between them along X.
- Z = up.

The two bulkheads sit [159.1 mm](BULKHEAD_PITCH) apart on the panel — the
flow meter is 60 mm port-to-port, and a reducer plus an elbow leg stand off
each end. The flow meter, both elbows, and both reducers live inside the
enclosure at Y = -[44.35 mm](STUB_DEPTH_Y).
"""

import sys
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
# Flow sensor (digiten_flow_sensor.py frame): axis along Y, ports at ±this.
flow_port_face = 30.0            # collet face from center, each port


# --- Reducer adapter: JG PP201208WP, 3/8" PTC x 1/4" PTC reducing union ------
# Modeled as a stepped coaxial stub for layout keep-out. Length and the
# diameters are photo/catalog estimates pending a part in hand.
reducer_len = 30.0               # overall length, port face to port face (estimated)
reducer_38_dia = 16.0            # 3/8" collet barrel OD (estimated)
reducer_14_dia = 12.0            # 1/4" collet barrel OD (estimated)


# --- Layout: lateral chain along X, inside the enclosure ---------------------
# The flow meter sits centered on X=0 at a fixed depth into the enclosure,
# its axis along X. Working outward from each port face: a reducer, then an
# elbow whose lateral leg meets the reducer and whose axial leg points +Y
# to the bulkhead's inner port. The bulkhead X is whatever puts that elbow
# axial-leg collet face on the bulkhead's far ring face.
#
# The lateral chain (flow meter, both reducers, both elbow corners) lives at
# one depth into the enclosure along -Y, at Z=0. The elbow axial leg
# (length elbow_leg) bridges that depth out to the bulkhead far ring face.
stub_depth_y = bulkhead_far_ring_y - elbow_leg   # elbow corner / chain depth, -Y

# Outboard end of one reducer = flow port face + reducer length. The elbow's
# lateral-leg collet face meets the reducer there; its bend corner sits one
# elbow_leg further out, which sets the bulkhead axis.
_reducer_outer_x = flow_port_face + reducer_len
bulkhead_x = _reducer_outer_x + elbow_leg         # elbow bend corner = bulkhead axis
bulkhead_pitch = 2.0 * bulkhead_x                 # lateral spacing on the panel


def build_reducer():
    """JG 3/8x1/4 reducing union as a stepped coaxial stub along Y: a
    reducer_38_dia barrel toward the elbow and a reducer_14_dia barrel toward
    the flow-meter port."""
    big = (
        cq.Workplane("XZ")
        .circle(reducer_38_dia / 2.0)
        .extrude(reducer_len / 2.0)
    )
    small = (
        cq.Workplane("XZ")
        .circle(reducer_14_dia / 2.0)
        .extrude(-reducer_len / 2.0)
    )
    return big.union(small)


def place_bulkhead(sign):
    """Bulkhead union through the panel at X = sign*bulkhead_x, axis along Y."""
    return (
        cq.importers.importStep(str(_BULKHEAD_STEP)).val()
        .translate((sign * bulkhead_x, 0.0, 0.0))
    )


def place_elbow(sign):
    """Elbow at the bulkhead's inner port: axial leg up +Y into the bulkhead
    far ring, lateral leg turned inward (toward X=0) to meet the reducer.

    Source elbow has legs on +Y and +Z meeting at the corner (origin). The +Y
    leg is the axial leg and stays +Y; rotating about Y swings the +Z leg into
    the lateral direction — -90 about Y sends +Z onto -X (inward for the +X
    bulkhead), +90 sends it onto +X (for the -X bulkhead). The corner lands at
    (sign*bulkhead_x, stub_depth_y, 0)."""
    fit = cq.importers.importStep(str(_ELBOW_STEP)).val()
    fit = fit.rotate((0, 0, 0), (0, 1, 0), -90 * sign)
    return fit.translate((sign * bulkhead_x, stub_depth_y, 0.0))


def place_reducer(sign):
    """Reducer between the elbow lateral leg and the flow-meter port, axis
    along X, centered between the flow port face and the elbow corner."""
    cx = sign * (flow_port_face + reducer_len / 2.0)
    return (
        build_reducer()
        .rotate((0, 0, 0), (0, 0, 1), -90)  # Y-axis stub -> X-axis
        .translate((cx, stub_depth_y, 0.0))
    )


def place_flow_meter():
    """Flow meter centered at X=0 at the chain depth, axis rotated from Y onto
    X so its ports face ±X toward the reducers."""
    return (
        cq.importers.importStep(str(_FLOW_SENSOR_STEP)).val()
        .rotate((0, 0, 0), (0, 0, 1), 90)
        .translate((0.0, stub_depth_y, 0.0))
    )


PANEL_COLOR = cq.Color(0.85, 0.78, 0.62)
BULKHEAD_COLOR = cq.Color(0.55, 0.57, 0.60)   # gray acetal
ELBOW_COLOR = cq.Color(0.20, 0.22, 0.26)      # black PP
REDUCER_COLOR = cq.Color(0.95, 0.95, 0.97)    # white PP
METER_COLOR = cq.Color(0.30, 0.55, 0.85)      # blue, to read clearly


def build():
    assy = cq.Assembly(name="faucet-inlet-stub")
    assy.add(place_bulkhead(+1), name="bulkhead-in", color=BULKHEAD_COLOR)
    assy.add(place_bulkhead(-1), name="bulkhead-out", color=BULKHEAD_COLOR)
    assy.add(place_elbow(+1), name="elbow-in", color=ELBOW_COLOR)
    assy.add(place_elbow(-1), name="elbow-out", color=ELBOW_COLOR)
    assy.add(place_reducer(+1), name="reducer-in", color=REDUCER_COLOR)
    assy.add(place_reducer(-1), name="reducer-out", color=REDUCER_COLOR)
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
