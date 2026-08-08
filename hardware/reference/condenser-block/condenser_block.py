"""Condenser block + fan — the refrigeration loop's hot end, as a donor primitive.

There is no harvested solid here and no STEP beside this file. The block arrived as a
finned serpentine with its fan bolted to one face; what the pack takes of it is its
ENVELOPE, where a leg may arrive, and the two holes it hangs off — this module draws the
first, declares the second, and cuts the third.

Coordinate frame
----------------
- Origin at the box's own lower-front-west corner, so the six faces are 0 and the three
  dimensions. `AIRFLOW` on X — the fan's own axis, the short one — `FACE_A` on Y and
  `FACE_B` on Z, the standing serpentine's two large faces. The fan is on the face its air
  leaves by.
- The MOUNT is one vertical line through the body: a Ø5 hole in the base plate, a Ø5 hole
  in the crown plate, and a 16 x 20 shaft between them running the full standing height.
  It stands 29 in from the INTAKE face and 15 in from the AFT face. The machine currently
  sets the block down unturned (`front_half.build_condenser`), so those two read as the
  world's X− and Y+ faces at this pose.
- BOTH REFRIGERANT LEGS ARRIVE ON A FACE THE BLOCK IS MATED TO, which is what a donor
  packed as an envelope is for: the serpentine's own headers are re-dressed to reach them.
  Hot gas enters the INTAKE face on the compressor shroud's own discharge stub, and the
  liquid line leaves the AFT face on the cold core's own evaporator-inlet station. Each is
  therefore made up across a plane two bodies already share, and no copper is drawn between
  them — `front_half.refrigerant_joints()` measures both at every build and fails the build
  if either opens.

Which wall the block stands against and which way its air crosses the cabinet is the
enclosure's business (`../../manifold-layout/front_half.py`).
"""

import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

# --- Calipered off the donor ----------------------------------------------
AIRFLOW = 56.0        # fan + finstack stack depth, along the flow
FACE_A = 178.0        # the serpentine's long face
FACE_B = 151.0        # the serpentine's standing face

# --- The mount --------------------------------------------------------------
# Two holes, drilled in sheet — one at the base, one at the crown — on one shaft that runs
# the block's whole standing height.
PLATE_T = 0.4         # the sheet the two holes are drilled in, at base and at crown
MOUNT_D = 5.0         # the holes themselves
MOUNT_IN_INTAKE = 29.0  # hole centre, in from the INTAKE face (x = 0)
MOUNT_IN_AFT = 15.0     # hole centre, in from the AFT face (y = FACE_A)
SHAFT_X = 16.0        # the shaft between the two plates, on the AIRFLOW axis
SHAFT_Y = 20.0        #   and on FACE_A's
SHAFT_Z = FACE_B - 2.0 * PLATE_T   # 150.2 — the standing height less a plate at each end


def mount_xy() -> tuple:
    """Where the mount stands on the block's floor plan. One place, read at both ends."""
    return (MOUNT_IN_INTAKE, FACE_A - MOUNT_IN_AFT)


def build():
    """The block as the pack carries it: one box, its own corner at the origin, less the
    shaft that runs its full standing height and the hole drilled through the plate at
    either end of that shaft."""
    x, y = mount_xy()
    block = cq.Workplane("XY").box(AIRFLOW, FACE_A, FACE_B, centered=(False, False, False))
    shaft = (cq.Workplane("XY", origin=(x, y, PLATE_T))
             .rect(SHAFT_X, SHAFT_Y).extrude(SHAFT_Z))
    bore = cq.Solid.makeCylinder(MOUNT_D / 2.0, FACE_B,
                                 cq.Vector(x, y, 0.0), cq.Vector(0, 0, 1))
    return block.cut(shaft).cut(bore).val()


# --- The three penetrations, in the block's own frame -----------------------
# Picks, on a donor packed as a primitive: each stands where a 1/4" copper leg can arrive on
# the face it names, and moves with that face.
#
# The two refrigerant ones are struck on the NEIGHBOUR that stands against the face they
# take, not on anything about the block: the inlet on the compressor shroud's discharge
# stub, which crosses the plane the two share at mid-height and a quarter of the way down
# the depth; the outlet on the cold core's evaporator-inlet station, which crosses the
# plane behind the block on that core's own port lane. Both are one point read twice, and
# the machine measures each at every build.

def stations() -> dict:
    """All three, under the names the loop knows them by."""
    return {
        "refrig-inlet":  ((0.0, 45.25, 75.0), (-1.0, 0.0, 0.0)),
        "refrig-outlet": ((39.0, FACE_A, 47.75), (0.0, 1.0, 0.0)),
        "fan-power":     ((AIRFLOW, 30.0, FACE_B / 2.0), (1.0, 0.0, 0.0)),
    }


def mounts() -> dict:
    """Both mount points, shaped like `stations()`: one drilled DOWN through the base plate,
    one UP through the crown plate, on the one shaft."""
    x, y = mount_xy()
    return {
        "mount-base":  ((x, y, 0.0), (0.0, 0.0, -1.0)),
        "mount-crown": ((x, y, FACE_B), (0.0, 0.0, 1.0)),
    }


def mounts_hold():
    """Hold the mount to the block it is cut in: the shaft standing clear of all four sides,
    both holes inside that shaft, the sheet at either end left at its own thickness, and
    material or air where each of those puts it."""
    x, y = mount_xy()
    for ax, at, half, span in (("x", x, SHAFT_X / 2.0, AIRFLOW),
                               ("y", y, SHAFT_Y / 2.0, FACE_A)):
        if not (0.0 < at - half and at + half < span):
            raise ValueError(
                f"condenser mount shaft reaches {at - half:g}..{at + half:g} on {ax} and the "
                f"block's own face runs 0..{span:g} — the shaft has broken out of the block.")
        if half - MOUNT_D / 2.0 <= 0.0:
            raise ValueError(
                f"the Ø{MOUNT_D:g} hole is {MOUNT_D / 2.0 - half:g} wider than its own shaft "
                f"on {ax} — the hole is cutting the shaft's wall rather than the plate.")
    if SHAFT_Z + 2.0 * PLATE_T - FACE_B:
        raise ValueError(
            f"shaft {SHAFT_Z:g} and two {PLATE_T:g} plates come to "
            f"{SHAFT_Z + 2.0 * PLATE_T:g} against the block's own {FACE_B:g} standing height "
            f"— the sheet at one end is not the thickness it is drilled at.")
    solid = build()
    probes = [("base plate", (x + MOUNT_D, y, PLATE_T / 2.0), True),
              ("crown plate", (x + MOUNT_D, y, FACE_B - PLATE_T / 2.0), True),
              ("base hole", (x, y, PLATE_T / 2.0), False),
              ("crown hole", (x, y, FACE_B - PLATE_T / 2.0), False),
              ("shaft", (x, y, FACE_B / 2.0), False),
              ("shaft corner", (x + SHAFT_X / 2.0 - 0.5, y + SHAFT_Y / 2.0 - 0.5,
                                FACE_B / 2.0), False),
              ("body beside the shaft", (x + SHAFT_X, y, FACE_B / 2.0), True)]
    for name, (px, py, pz), want_material in probes:
        state = BRepClass3d_SolidClassifier(solid.wrapped, gp_Pnt(px, py, pz), 1e-3).State()
        if (state == 0) != want_material:
            had = "material" if state == 0 else "air"
            raise ValueError(
                f"condenser {name} at ({px:g}, {py:g}, {pz:g}) is {had} — the mount this "
                f"module declares is not the mount its geometry was cut with.")


def stations_hold():
    """Hold every station to the box this module draws: on the FACE its own axis points out
    of, and inside that face's own two edges."""
    bb = build().BoundingBox()
    span = {"x": (bb.xmin, bb.xmax), "y": (bb.ymin, bb.ymax), "z": (bb.zmin, bb.zmax)}
    for name, (pos, axis) in stations().items():
        for i, ax in enumerate("xyz"):
            lo, hi = span[ax]
            if axis[i]:                                   # the axis it leaves by
                face = hi if axis[i] > 0 else lo
                if abs(pos[i] - face) > 1e-9:
                    raise ValueError(
                        f"condenser {name} stands at {ax} = {pos[i]:g} and the face it leaves "
                        f"by is at {face:g} — the pick has come off the block's own wall.")
            elif not (lo <= pos[i] <= hi):
                raise ValueError(
                    f"condenser {name} stands at {ax} = {pos[i]:g}, outside the block's own "
                    f"{lo:g}..{hi:g} — the pick is off the face it is meant to cross.")


# --- controls -------------------------------------------------------------

def selftest():
    stations_hold()
    mounts_hold()
    return ["  all three penetrations stand on the block's own faces",
            f"  the mount is one Ø{MOUNT_D:g} line at {mount_xy()}, through "
            f"{PLATE_T:g} of plate at each end of a {SHAFT_X:g} x {SHAFT_Y:g} x "
            f"{SHAFT_Z:g} shaft"]


def main():
    bb = build().BoundingBox()
    print(f"condenser block  X[{bb.xmin:.1f}, {bb.xmax:.1f}]  Y[{bb.ymin:.1f}, {bb.ymax:.1f}]"
          f"  Z[{bb.zmin:.1f}, {bb.zmax:.1f}]")
    for name, (pos, axis) in {**stations(), **mounts()}.items():
        print(f"  {name:15s} {tuple(round(c, 2) for c in pos)}  out {axis}")
    x, y = mount_xy()
    print(f"  shaft           x[{x - SHAFT_X / 2:.1f}, {x + SHAFT_X / 2:.1f}] "
          f"y[{y - SHAFT_Y / 2:.1f}, {y + SHAFT_Y / 2:.1f}] "
          f"z[{PLATE_T:.1f}, {FACE_B - PLATE_T:.1f}]  {SHAFT_X:g} x {SHAFT_Y:g} x {SHAFT_Z:g}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("condenser_block selftest OK")
    else:
        main()
