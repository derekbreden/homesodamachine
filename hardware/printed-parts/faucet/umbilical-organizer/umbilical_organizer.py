"""PET-GF umbilical organizer, in its upright print frame.

The quarter-inch soda bore uses the tested A sample's fit. The three 4 mm
bores use the tested B drain-bore dimension; black flavor-stock fit is unmeasured.

The print origin is the centre of the round stock; Z=0 is the bottom face.
Tube-axis XY values below use the faucet assembly's coordinates. Placement
adds CENTRE_XY and sets the bottom face below the chosen installed top face.
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[2]
sys.path.insert(0, str(HARDWARE / "scripts"))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq
from _materials import C_FAUCET_BLACK, linear
sys.path.insert(0, str(HARDWARE / "printed-parts/faucet"))
import _faucet_interface as interface
import faucet_paths

from _rust_data import request


def _data():
    return request("faucet-data", "faucet-data", {
        "op": "organizer", "color": list(linear(C_FAUCET_BLACK)),
    })


globals().update(_data()["datums"])
CABLE_XY = tuple(CABLE_XY)
CENTRE_XY = tuple(CENTRE_XY)
BORES = tuple((name, tuple(xy), diameter) for name, xy, diameter in BORES)


def axis(name):
    """One passage's XY axis in the mounted faucet frame."""
    return next(xy for label, xy, _diameter in BORES if label == name)


def build_organizer():
    """One puck, four smooth tube bores and a flat, loose ribbon slot."""
    body = cq.Workplane("XY").circle(OD / 2).extrude(LENGTH)
    body = body.edges("%Circle").chamfer(OUTSIDE_EASE)
    for name, xy, diameter in BORES:
        x, y = xy[0] - CENTRE_XY[0], xy[1] - CENTRE_XY[1]
        r = diameter / 2
        entry = CABLE_ENTRY if name == "SIG" else ENTRY
        if name == "SIG":
            def wire(z, grow=0.0):
                return (cq.Workplane("XY", origin=(x, y, z))
                        .slot2D(CABLE_SLOT_LENGTH + 2*grow, CABLE_SLOT_DEPTH + 2*grow)
                        .val())
            bore = cq.Solid.extrudeLinear(wire(-1), [], cq.Vector(0, 0, LENGTH + 2))
            bottom = cq.Solid.makeLoft([wire(0, entry), wire(entry)], ruled=True)
            top = cq.Solid.makeLoft([wire(LENGTH-entry), wire(LENGTH, entry)], ruled=True)
            body = body.cut(bore.fuse(bottom, top))
            continue
        bore = cq.Solid.makeCylinder(r, LENGTH + 2, cq.Vector(x, y, -1))
        bottom = cq.Solid.makeCone(r + entry, r, entry, cq.Vector(x, y, 0))
        top = cq.Solid.makeCone(r, r + entry, entry, cq.Vector(x, y, LENGTH-entry))
        body = body.cut(bore.fuse(bottom, top))
    return body.val().clean()


def placed(top_z):
    return build_organizer().translate((*CENTRE_XY, top_z - LENGTH))


def numbers():
    """The Rust scalar program supplies the organizer's upright-print recipe."""
    return _data()["numbers"]


def main():
    import _rust_part

    said = _rust_part.cut("faucet", "umbilical-organizer", numbers(), HERE)
    stl = HERE / "umbilical-organizer.stl"
    step = HERE / "umbilical-organizer.step"
    import flute_payload
    flute_payload.cut(step, stl, preserve_print_triangles=True)
    print(f"-> {step.name}, {stl.name}, {step.name}.mesh")


if __name__ == "__main__":
    main()
