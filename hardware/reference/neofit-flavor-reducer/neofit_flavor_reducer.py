"""neoFit ARD4M4-E: 1/4-inch stem to 4 mm tube, along local +Y.

Supplier drawing: ogt8i8sqv3vd0r25jd0r.pdf, ARD4M4 row, inch dimensions.
The shoulder is the nominal valve-collet datum. Stem insertion is unmeasured;
the complete 21.006 mm stem is retained in this reference, not a seal model.
"""
import sys
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[1]
sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_assembly
from _materials import M_NEOFIT_ACETAL, one_body

STEM_OD = 6.35
TUBE_OD = 4.0
BODY_D = 0.520 * 25.4
OVERALL = 1.445 * 25.4
STEM_LENGTH = 0.827 * 25.4
PROUD_LENGTH = OVERALL - STEM_LENGTH
STEP = HERE / "neofit-flavor-reducer.step"

def port():
    return ((0.0, PROUD_LENGTH, 0.0), (0.0, 1.0, 0.0))

def build():
    axis = cq.Vector(0, 1, 0)
    stem = cq.Solid.makeCylinder(STEM_OD/2, STEM_LENGTH,
                                cq.Vector(0, -STEM_LENGTH, 0), axis)
    body = cq.Solid.makeCylinder(BODY_D/2, PROUD_LENGTH, cq.Vector(), axis)
    bore = cq.Solid.makeCylinder(TUBE_OD/2, OVERALL,
                                cq.Vector(0, -STEM_LENGTH, 0), axis)
    return stem.fuse(body).cut(bore)

def placed(origin, direction):
    """Nominal shoulder at the valve mouth, reducer outlet along its axis."""
    start, end = cq.Vector(0, 1, 0), cq.Vector(*direction).normalized()
    shape = build()
    cross = start.cross(end)
    if cross.Length > 1e-9:
        import math
        shape = shape.rotate((0, 0, 0), cross.toTuple(),
                             math.degrees(start.getAngle(end)))
    elif start.dot(end) < 0:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    return shape.translate(origin)

if __name__ == "__main__":
    export_assembly(one_body(build(), "neofit-flavor-reducer", M_NEOFIT_ACETAL), str(STEP))
