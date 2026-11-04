"""neoFit ARD4M4-E: 1/4-inch stem to 4 mm tube, along local +Y.

Supplier drawing: ogt8i8sqv3vd0r25jd0r.pdf, ARD4M4 row, inch dimensions.
The shoulder is the nominal valve-collet datum. Stem insertion is unmeasured;
the complete 21.006 mm stem is retained in this reference, not a seal model.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""
from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "neofit-flavor-reducer.step"
PAYLOAD_PATH = _here.parent / "neofit-flavor-reducer.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('neofit_flavor_reducer')
globals().update({name: _reference_values[name] for name in ('HERE', 'STEM_OD', 'TUBE_OD', 'BODY_D', 'OVERALL', 'STEM_LENGTH', 'PROUD_LENGTH')})

HARDWARE = HERE.parents[1]

STEP = HERE / "neofit-flavor-reducer.step"

def port():
    return _reference_data('neofit_flavor_reducer', 'port', (), {})


def placed(origin, direction):
    """Frozen reducer, shoulder at the valve mouth and outlet along its axis."""
    import math
    import sys

    import cadquery as cq

    sys.path.insert(0, str(HARDWARE / "scripts"))
    from _cadq_export import import_step

    start, end = cq.Vector(0, 1, 0), cq.Vector(*direction).normalized()
    shape = import_step(STEP_PATH).val()
    cross = start.cross(end)
    if cross.Length > 1e-9:
        shape = shape.rotate((0, 0, 0), cross.toTuple(),
                             math.degrees(start.getAngle(end)))
    elif start.dot(end) < 0:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    return shape.translate(origin)


def main():
    print("neofit-flavor-reducer")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
