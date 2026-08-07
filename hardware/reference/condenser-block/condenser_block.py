"""Condenser block + fan — the refrigeration loop's hot end, as a donor primitive.

There is no harvested solid here and no STEP beside this file. The block arrived as a
finned serpentine with its fan bolted to one face; what the pack takes of it is its
ENVELOPE and where a leg may arrive, and this module draws the one and declares the other.

Coordinate frame
----------------
- Origin at the box's own lower-front-west corner, so the six faces are 0 and the three
  dimensions. `AIRFLOW` on X — the fan's own axis, the short one — `FACE_A` on Y and
  `FACE_B` on Z, the standing serpentine's two large faces.
- Hot gas enters the CROWN and the liquid line leaves LOW on the intake face: a standing
  serpentine fills from the top and drains from the bottom. The fan is on the face its air
  leaves by.

Which wall the block stands against and which way its air crosses the cabinet is the
enclosure's business (`../../manifold-layout/front_half.py`).
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

# --- Calipered off the donor ----------------------------------------------
AIRFLOW = 56.0        # fan + finstack stack depth, along the flow
FACE_A = 178.0        # the serpentine's long face
FACE_B = 151.0        # the serpentine's standing face


def build():
    """The block as the pack carries it: one box, its own corner at the origin."""
    return cq.Workplane("XY").box(AIRFLOW, FACE_A, FACE_B,
                                  centered=(False, False, False)).val()


# --- The three penetrations, in the block's own frame -----------------------
# Picks, on a donor packed as a primitive: each stands where a 1/4" copper leg can arrive on
# the face it names, and moves with that face.

def stations() -> dict:
    """All three, under the names the loop knows them by."""
    return {
        "refrig-inlet":  ((27.0, 146.0, FACE_B), (0.0, 0.0, 1.0)),
        "refrig-outlet": ((0.0, 161.0, 32.5), (-1.0, 0.0, 0.0)),
        "fan-power":     ((AIRFLOW, 30.0, FACE_B / 2.0), (1.0, 0.0, 0.0)),
    }


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
    return ["  all three penetrations stand on the block's own faces"]


def main():
    bb = build().BoundingBox()
    print(f"condenser block  X[{bb.xmin:.1f}, {bb.xmax:.1f}]  Y[{bb.ymin:.1f}, {bb.ymax:.1f}]"
          f"  Z[{bb.zmin:.1f}, {bb.zmax:.1f}]")
    for name, (pos, axis) in stations().items():
        print(f"  {name:15s} {tuple(round(c, 2) for c in pos)}  out {axis}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("condenser_block selftest OK")
    else:
        main()
