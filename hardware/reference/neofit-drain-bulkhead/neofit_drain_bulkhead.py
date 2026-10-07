"""Black neoFit ABU44M-E, 4 mm tube bulkhead, in the shared Y-axis fitting frame.

Manufacturer drawing: https://assets.freshwatersystems.com/image/upload/qnbgcy8djx3nj2weqz9v.pdf
The M15 barrel and 8.1 mm panel span determine the printed panel interface.
The un-dimensioned flange rim is represented by a conservative 22 mm envelope.
"""
import math
import sys
from pathlib import Path
import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_assembly
from _materials import M_NEOFIT_ACETAL, one_body

STEP = _here.with_name("neofit-drain-bulkhead.step")
TUBE_OD = 4.0
THREAD_D = 15.0
THREAD_PITCH = 1.5
PANEL_THREAD = 8.1
OVERALL = 32.4
NUT_LEN = 6.5
FLANGE_AF = 17.0
NUT_AF = 18.0
FLANGE_D = 22.0
NUT_D = NUT_AF / math.cos(math.radians(30))
near_ring_face_y = 14.7
far_ring_face_y = near_ring_face_y - OVERALL
far_body_face_y = -PANEL_THREAD
PROUD_LENGTH = near_ring_face_y

def panel_hole_d(clearance):
    return THREAD_D + clearance

def panel_footprint():
    return (NUT_D, NUT_D)

def flange_footprint():
    return FLANGE_D

def port(side):
    return ((0.0, near_ring_face_y if side > 0 else far_ring_face_y, 0.0),
            (0.0, 1.0 if side > 0 else -1.0, 0.0))

def build():
    def cylinder(d, lo, hi):
        return cq.Solid.makeCylinder(d / 2, hi - lo, cq.Vector(0, lo, 0), cq.Vector(0, 1, 0))
    return (cylinder(FLANGE_D, 0, near_ring_face_y)
            .fuse(cylinder(THREAD_D, far_body_face_y, 0))
            .fuse(cylinder(NUT_D, far_ring_face_y, far_body_face_y))
            .cut(cylinder(TUBE_OD, far_ring_face_y, near_ring_face_y)))

if __name__ == "__main__":
    export_assembly(one_body(build(), "neofit-drain-bulkhead", M_NEOFIT_ACETAL), str(STEP))
