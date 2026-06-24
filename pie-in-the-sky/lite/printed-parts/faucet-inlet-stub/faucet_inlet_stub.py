"""Lite-edition rear-panel carbonated-water pass-through — the
faucet-inlet stub. Carb water from the external Lillium carbonator enters
the rear panel, turns inward and down to the meter, crosses the DIGITEN flow
meter (detected flow triggers the flavor pumps), turns back up, and exits the
rear panel to the faucet.

Flow path, port to port:
    Lillium hose
      -> bulkhead IN  (panel pass-through, +X side)
      -> elbow IN     (drops the run inward to the meter axis)
      -> DIGITEN flow meter  (inline, ports coaxial on +X / -X)
      -> elbow OUT    (lifts the run back up toward the panel)
      -> bulkhead OUT (panel pass-through, -X side)
      -> faucet

The meter is the inline G1/4" 1/4"-PTC part: its two ports are coaxial on
opposite rims (one opening +X, one -X), each taking a 1/4" OD tube directly.
It lies with its flow axis along X, deep in the enclosure; a 1/4" elbow stands
off each collet and turns the run +Y up to a panel bulkhead — so the whole
path is a flat U, in at the +X bulkhead, straight across through the meter,
out at the -X bulkhead. Every collet face mates its neighbour: bulkhead ring
to elbow axial leg, elbow lateral leg to meter collet.

Coordinate frame
----------------
- Y = panel-normal : +Y is outside the enclosure (toward the Lillium hose
                     and the faucet); -Y is inside. The rear panel sits at
                     Y = 0, the bulkhead seating plane.
- X = lateral / meter flow axis : the two bulkheads straddle X = 0 at
                     ±[49.56 mm](BULKHEAD_X); the meter lies between them on
                     the X axis, inlet/outlet collets opening +X and -X.
- Z = up.

The two bulkheads sit [99.12 mm](BULKHEAD_PITCH) apart on the panel. Each
elbow's axial leg drops from a bulkhead's inner ring face down to the meter
axis at Y = -[44.35 mm](STUB_DEPTH_Y), where its lateral leg meets the meter's
collet face; the meter and both elbows live inside the enclosure.
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
# running out to its collet face along +Y and +Z.
elbow_leg = 19.56                # bend corner to collet face, both legs
# Flow meter (digiten_flow_sensor.py frame): inline, ports coaxial on ±X, each
# collet face this far from the body center along the flow axis.
flow_port_face = 30.0            # collet face from center, each port


# --- Layout: inline meter on the X axis, a flat U up to two panel bulkheads --
# The meter lies with its flow axis along X at depth meter_center_y; an elbow
# stands off each ±X collet, dropping +Y to a panel bulkhead. The elbow axial
# leg bridges the bulkhead's inner ring face down to the meter axis, so the
# meter sits one elbow_leg below the bulkhead ring face.
meter_center_y = bulkhead_far_ring_y - elbow_leg          # meter axis depth, -Y
stub_depth_y = meter_center_y                             # chain depth, -Y

# Each elbow's lateral leg runs from its bend corner in to the meter collet
# face (at flow_port_face from center); the corner sits one elbow_leg further
# out, which sets the bulkhead axis.
bulkhead_x = flow_port_face + elbow_leg   # meter collet + elbow lateral leg
bulkhead_pitch = 2.0 * bulkhead_x         # lateral spacing on the panel


def place_bulkhead(sign):
    """Bulkhead union through the panel at X = sign*bulkhead_x, axis along Y."""
    return (
        cq.importers.importStep(str(_BULKHEAD_STEP)).val()
        .translate((sign * bulkhead_x, 0.0, 0.0))
    )


def place_elbow(sign):
    """Elbow at a bulkhead's inner port: axial leg up +Y into the bulkhead far
    ring, lateral leg turned inward (toward X=0) to meet the meter collet.

    Source elbow has legs on +Y and +Z meeting at the corner (origin). The +Y
    leg is the axial leg and stays +Y; rotating about Y swings the +Z leg into
    the lateral direction — -90 about Y sends +Z onto -X (inward for the +X
    bulkhead), +90 sends it onto +X (for the -X bulkhead). The corner lands at
    (sign*bulkhead_x, meter_center_y, 0): its +Y leg reaches the bulkhead ring
    at Y=bulkhead_far_ring_y, its lateral leg the meter collet at X=sign*flow_port_face."""
    fit = cq.importers.importStep(str(_ELBOW_STEP)).val()
    fit = fit.rotate((0, 0, 0), (0, 1, 0), -90 * sign)
    return fit.translate((sign * bulkhead_x, meter_center_y, 0.0))


def place_flow_meter():
    """Inline flow meter centered on X=0 at the chain depth, flow axis along X
    so its +X / -X collets face the two elbows. No rotation — the reference
    model is already built inline on X."""
    return (
        cq.importers.importStep(str(_FLOW_SENSOR_STEP)).val()
        .translate((0.0, stub_depth_y, 0.0))
    )


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
