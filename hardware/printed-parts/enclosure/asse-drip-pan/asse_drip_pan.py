"""The ASSE drip pan under the atmospheric vent.

The open pan slides through one rectangular slot in back-top's nine-millimetre
west wall. Its floor and the two end-wall rims bear on the slot. The pull face
rests against the exterior and stops the insertion. The Shutao moisture plate
lies loose on the floor, with its lead rising from the open mouth to the dry
wall's cable clip.

The local origin is the lower west/front corner of the pull face. +X is the
insertion direction, +Y is the pan's depth, and +Z is up.
"""

import sys
from collections import namedtuple
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "reference" / "shutao-moisture-plate"))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly
from _materials import M_PETG_BLACK, one_body
from docgen import substitute_md
import shutao_moisture_plate as plate
import fits

PAN_X, PAN_Y, PAN_Z = 51.0, 76.0, 15.0
WALL, FLOOR = 2.5, 3.0
FLOOR_COVE = 2.0
PAN_SLIP = fits.running
VENT_GAP = 4.0

# The pull face covers the slot and meets the exterior wall at the insertion stop.
# Its overlap with the pan closes the west wall of the basin before the cavity begins.
PULL_FACE_DEPTH = 5.95
PULL_FACE_Y_OVERHANG = 4.0
PULL_FACE_CHAMFER = WALL

PLATE_X, PLATE_Y = plate.PLATE_X, plate.PLATE_Y
PLATE_SLIP = 1.0
Bound = namedtuple("Bound", "id label ok value target detail")


def flat_floor():
    return (PAN_X - 2 * WALL - 2 * FLOOR_COVE,
            PAN_Y - 2 * WALL - 2 * FLOOR_COVE)


def check_plate() -> Bound:
    fx, fy = flat_floor()
    need_x, need_y = PLATE_Y + 2 * PLATE_SLIP, PLATE_X + 2 * PLATE_SLIP
    ok = fx >= need_x and fy >= need_y
    return Bound(
        "plate-lies-flat", "The moisture plate lies flat on the pan's floor", ok,
        f"flat floor {fx:.2f} x {fy:.2f}", f"{need_x:.2f} x {need_y:.2f}",
        [] if ok else [f"The floor needs {need_x:.2f} x {need_y:.2f} mm inside its coves."])


def build():
    """One basin and one exterior pull face, fused into one printable solid."""
    x = PULL_FACE_Y_OVERHANG
    outer = (cq.Workplane("XY")
             .box(PAN_X, PAN_Y, PAN_Z, centered=(False, False, False))
             .translate((x, x, 0)))
    cavity = (cq.Workplane("XY")
              .box(PAN_X - 2 * WALL, PAN_Y - 2 * WALL, PAN_Z,
                   centered=(False, False, False))
              .edges("<Z").fillet(FLOOR_COVE)
              .translate((x + WALL, x + WALL, FLOOR)))

    y1 = PAN_Y + 2 * PULL_FACE_Y_OVERHANG
    c = PULL_FACE_CHAMFER
    section = [(c, 0), (y1 - c, 0), (y1, c), (y1, PAN_Z - c),
               (y1 - c, PAN_Z), (c, PAN_Z), (0, PAN_Z - c), (0, c)]
    pull = (cq.Workplane("YZ").polyline(section + section[:1]).wire()
            .extrude(PULL_FACE_DEPTH))
    return outer.union(pull).cut(cavity).clean()


def capacity_ml():
    return ((PAN_X - 2 * WALL) * (PAN_Y - 2 * WALL)
            * (PAN_Z - FLOOR) / 1000.0)


def main():
    pan = build()
    bb = pan.val().BoundingBox()
    if not pan.val().isValid() or len(pan.val().Solids()) != 1:
        raise ValueError("ASSE drip pan must be one valid solid")
    print("ASSE drip pan")
    print(f"  box {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm; "
          f"basin {PAN_X:g} x {PAN_Y:g} x {PAN_Z:g} mm; "
          f"{capacity_ml():.1f} mL to the rim")
    plate_bound = check_plate()
    print(f"  {'PASS' if plate_bound.ok else 'FAIL'} {plate_bound.label}: "
          f"{plate_bound.value}, wants {plate_bound.target}")
    if not plate_bound.ok:
        raise ValueError(plate_bound.detail[0])
    out = _here.parent / "asse-drip-pan.step"
    export_assembly(one_body(pan, out.stem, M_PETG_BLACK), str(out))
    stl = out.with_suffix(".stl")
    pan.val().copy(mesh=False).exportStl(str(stl),
        tolerance=0.005, angularTolerance=0.05, relative=False)
    print(f"-> {out.name} / {stl.name}")
    substitute_md(_here.parent / "README.md", variables={
        "PAN_LEN": f"{PAN_X:g}", "PAN_DEPTH": f"{PAN_Y:g}",
        "PAN_HEIGHT": f"{PAN_Z:g}", "PAN_WALL": f"{WALL:g}",
        "PAN_FLOOR": f"{FLOOR:g}", "PAN_CAPACITY": f"{capacity_ml():.1f}",
        "PAN_COVE_R": f"{FLOOR_COVE:g}",
        "PLATE_LEN": f"{PLATE_X:g}", "PLATE_DEPTH": f"{PLATE_Y:g}",
        "PLATE_SLIP_MM": f"{PLATE_SLIP:g}", "PAN_VENT_GAP": f"{VENT_GAP:g}",
        "PULL_FACE_DEPTH": f"{PULL_FACE_DEPTH:g}",
        "PULL_FACE_Y_OVERHANG": f"{PULL_FACE_Y_OVERHANG:g}",
        "PULL_FACE_CHAMFER": f"{PULL_FACE_CHAMFER:g}",
    })


if __name__ == "__main__":
    main()
