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
- BOTH Y FACES ARE A RECESS BETWEEN TWO FLANGES. The serpentine's end brackets are folded
  sheet at the crown and the base, and between them each face stands `RECESS_Y` back: the
  block's own width the whole way across, the standing height less a flange at either end.
  So each face presents two flanges of `AIRFLOW` x `RECESS_Y` x `PLATE_T` with open air
  between them, and the recess opens on THREE sides — its own face and both flanks.
- The MOUNT is one vertical line through the AFT flanges: a Ø5 hole in the base one and a
  Ø5 hole in the crown one, standing 29 in from the INTAKE face and 15 in from the AFT
  face. THE FORE FLANGES CARRY NO HOLE — that end of the block is held by sliding into
  something, and the mount is the two screws at this one.
  The machine sets the block down unturned (`enclosure_assembly.build_condenser`), so those
  two insets read off the world's X− and Y+ faces at this pose.
- BOTH REFRIGERANT LEGS ARRIVE ON A FACE THE BLOCK PRESENTS TO ITS NEIGHBOUR, which is what
  a donor packed as an envelope is for: the serpentine's own headers are re-dressed to reach them.
  Hot gas enters the INTAKE face on the compressor's own discharge stub, a plane the two bodies
  share, so that leg is made up across it with no copper drawn between them. The liquid line leaves
  the AFT face for the cold core's evaporator inlet. `enclosure_assembly.refrigerant_joints()`
  takes a reading over every leg of the loop at each build, and `check_refrigerant_joints` reads
  red on the card for one standing open and for one with no pair of placed stations to measure.

Which wall the block stands against and which way its air crosses the cabinet is the
enclosure's business (`../../manifold-layout/enclosure_assembly.py`).
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
FACE_A = 154.0        # the serpentine's long face
FACE_B = 137.0        # the serpentine's standing face

# --- The two recesses -------------------------------------------------------
# One on each Y face, and the same on both: the block's own width, `RECESS_Y` in from the
# face, and the standing height less the sheet of a flange at either end.
PLATE_T = 0.4         # the folded end brackets, and the sheet the two holes are drilled in
RECESS_Y = 20.0       # how far each recess reaches IN from the face it opens on
RECESS_Z = FACE_B - 2.0 * PLATE_T   # 136.2 — the standing height less a flange at each end

# --- The mount --------------------------------------------------------------
# Two holes, drilled in the AFT flanges — one at the base, one at the crown — on one line
# that runs the block's whole standing height.
MOUNT_D = 5.0         # the holes themselves
MOUNT_IN_INTAKE = 29.0  # hole centre, in from the INTAKE face (x = 0)
MOUNT_IN_AFT = 15.0     # hole centre, in from the AFT face (y = FACE_A)


def mount_xy() -> tuple:
    """Where the mount stands on the block's floor plan. One place, read at both ends."""
    return (MOUNT_IN_INTAKE, FACE_A - MOUNT_IN_AFT)


def recess_y() -> tuple:
    """Each recess's own Y band, as `(fore, aft)` — the fore one first."""
    return ((0.0, RECESS_Y), (FACE_A - RECESS_Y, FACE_A))


def flange_z() -> tuple:
    """A recess's two flanges in height, as `(base, crown)`. Both recesses read the same:
    the sheet left standing at either end of the recess."""
    return ((0.0, PLATE_T), (FACE_B - PLATE_T, FACE_B))


def build():
    """The block as the pack carries it: one box, its own corner at the origin, less the
    recess each Y face stands back to and the hole drilled through the flange at either end
    of the aft one."""
    x, y = mount_xy()
    block = cq.Workplane("XY").box(AIRFLOW, FACE_A, FACE_B, centered=(False, False, False))
    for y0, y1 in recess_y():
        block = block.cut(cq.Workplane("XY", origin=(0.0, y0, PLATE_T))
                          .box(AIRFLOW, y1 - y0, RECESS_Z, centered=(False, False, False)))
    bore = cq.Solid.makeCylinder(MOUNT_D / 2.0, FACE_B,
                                 cq.Vector(x, y, 0.0), cq.Vector(0, 0, 1))
    return block.cut(bore).val()


# --- The three penetrations, in the block's own frame -----------------------
# Picks, on a donor packed as a primitive: each stands where a 1/4" copper leg can arrive on
# the face it names, and moves with that face.
#
# The two refrigerant ones are struck on the NEIGHBOUR that stands against the face they
# take, not on anything about the block: the inlet on the compressor's discharge
# stub, which crosses the plane the two share at mid-height and a quarter of the way down
# the depth; the outlet on the cold core's evaporator-inlet station, which crosses the
# plane behind the block on that core's own port lane. Both are one point read twice, and
# the machine measures each at every build.

def stations() -> dict:
    """All three, under the names the loop knows them by."""
    return {
        "refrig-inlet":  ((0.0, 66.0, 61.0), (-1.0, 0.0, 0.0)),
        "refrig-outlet": ((50.5, FACE_A, 33.75), (0.0, 1.0, 0.0)),
        "fan-power":     ((AIRFLOW, 30.0, FACE_B / 2.0), (1.0, 0.0, 0.0)),
    }


def mounts() -> dict:
    """Both mount points, shaped like `stations()`: one drilled DOWN through the base flange,
    one UP through the crown flange, on the one line."""
    x, y = mount_xy()
    return {
        "mount-base":  ((x, y, 0.0), (0.0, 0.0, -1.0)),
        "mount-crown": ((x, y, FACE_B), (0.0, 0.0, 1.0)),
    }


def mount_seats() -> dict:
    """What a boss under each mount hole has to reach: the face the screw pulls that flange
    down onto — the base flange's underside and the crown flange's underside.

    BOTH LOOK UP, because both screws come down the one line the mount is, and each closes
    on the face below the sheet it passes through."""
    x, y = mount_xy()
    return {
        "mount-base":  ((x, y, 0.0), (0.0, 0.0, 1.0)),
        "mount-crown": ((x, y, FACE_B - PLATE_T), (0.0, 0.0, 1.0)),
    }


def mounts_hold():
    """Hold the mount to the block it is cut in: both holes standing clear of all four sides,
    inside the aft recess's own depth, through sheet left at its own thickness, and material
    or air where each of those puts it."""
    x, y = mount_xy()
    if not (MOUNT_D / 2.0 < x < AIRFLOW - MOUNT_D / 2.0):
        raise ValueError(
            f"the Ø{MOUNT_D:g} hole stands at x {x:g} and the block's own face runs "
            f"0..{AIRFLOW:g} — it has broken out of the block's flanks.")
    fore, aft = recess_y()
    if not (aft[0] < y - MOUNT_D / 2.0 and y + MOUNT_D / 2.0 < aft[1]):
        raise ValueError(
            f"the Ø{MOUNT_D:g} hole at y {y:g} runs past the aft recess's own "
            f"{aft[0]:g}..{aft[1]:g} — it is cutting the flange's own root or its free edge, "
            f"and a screw through it would find no sheet to pull on.")
    if fore[1] > aft[0]:
        raise ValueError(
            f"the two recesses reach {fore[1]:g} and {aft[0]:g} in from their own faces and "
            f"meet — a {FACE_A:g} deep block cannot stand {RECESS_Y:g} back on both faces, so "
            f"there is no serpentine left between them.")
    if RECESS_Z + 2.0 * PLATE_T - FACE_B:
        raise ValueError(
            f"recess {RECESS_Z:g} and two {PLATE_T:g} flanges come to "
            f"{RECESS_Z + 2.0 * PLATE_T:g} against the block's own {FACE_B:g} standing height "
            f"— the sheet at one end is not the thickness it is drilled at.")
    solid = build()
    probes = [("base flange", (x + MOUNT_D, y, PLATE_T / 2.0), True),
              ("crown flange", (x + MOUNT_D, y, FACE_B - PLATE_T / 2.0), True),
              ("base hole", (x, y, PLATE_T / 2.0), False),
              ("crown hole", (x, y, FACE_B - PLATE_T / 2.0), False),
              ("aft recess", (x, y, FACE_B / 2.0), False),
              ("aft recess at its own face", (x, FACE_A - 0.5, FACE_B / 2.0), False),
              ("aft recess at the intake flank", (0.5, y, FACE_B / 2.0), False),
              ("aft recess at the exhaust flank", (AIRFLOW - 0.5, y, FACE_B / 2.0), False),
              ("aft recess's inner end", (x, aft[0] + 0.5, FACE_B / 2.0), False),
              ("fore recess", (x, fore[1] - 0.5, FACE_B / 2.0), False),
              ("fore base flange", (x, fore[1] - 0.5, PLATE_T / 2.0), True),
              ("fore crown flange", (x, fore[1] - 0.5, FACE_B - PLATE_T / 2.0), True),
              ("the serpentine between them", (x, FACE_A / 2.0, FACE_B / 2.0), True)]
    for name, (px, py, pz), want_material in probes:
        state = BRepClass3d_SolidClassifier(solid.wrapped, gp_Pnt(px, py, pz), 1e-3).State()
        if (state == 0) != want_material:
            had = "material" if state == 0 else "air"
            raise ValueError(
                f"condenser {name} at ({px:g}, {py:g}, {pz:g}) is {had} — the mount this "
                f"module declares is not the mount its geometry was cut with.")


def stations_hold():
    """Hold every station to the box this module draws: on the FACE its own axis points out
    of, and inside that face's own two edges.

    THE FACE AND NOT THE SOLID, because both Y faces are a recess now: the block's box reaches
    `FACE_A` on the aft flanges alone, and the outlet leaves on that plane — where the
    serpentine's own header is re-dressed to meet the core, not where the recess stands back."""
    span = {"x": (0.0, AIRFLOW), "y": (0.0, FACE_A), "z": (0.0, FACE_B)}
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
    fore, aft = recess_y()
    return ["  all three penetrations stand on the block's own faces",
            f"  each Y face stands {RECESS_Y:g} back over the block's whole {AIRFLOW:g} width, "
            f"leaving a {PLATE_T:g} flange at either end of a {RECESS_Z:g} opening",
            f"  the mount is one Ø{MOUNT_D:g} line at {mount_xy()}, through the aft recess's "
            f"two flanges, and the fore ones carry no hole"]


def main():
    bb = build().BoundingBox()
    print(f"condenser block  X[{bb.xmin:.1f}, {bb.xmax:.1f}]  Y[{bb.ymin:.1f}, {bb.ymax:.1f}]"
          f"  Z[{bb.zmin:.1f}, {bb.zmax:.1f}]")
    for name, (pos, axis) in {**stations(), **mounts()}.items():
        print(f"  {name:15s} {tuple(round(c, 2) for c in pos)}  out {axis}")
    (fz0, fz1), (cz0, cz1) = flange_z()
    for face, (y0, y1) in zip(("fore", "aft"), recess_y()):
        print(f"  {face + ' recess':15s} x[0.0, {AIRFLOW:.1f}] y[{y0:.1f}, {y1:.1f}] "
              f"z[{fz1:.1f}, {cz0:.1f}]  {AIRFLOW:g} x {y1 - y0:g} x {RECESS_Z:g}, "
              f"open on its own face and both flanks")
    print(f"  flanges         base z[{fz0:.1f}, {fz1:.1f}]  crown z[{cz0:.1f}, {cz1:.1f}]")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("condenser_block selftest OK")
    else:
        main()
