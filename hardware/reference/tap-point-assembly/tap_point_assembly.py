"""Tap-point assembly: the Basics MTB-0606WP barb tee with the two adapters that
fasten directly onto its branch.

The tap point is where the flavor manifold draws its water. The tee is clamped
inline in the 3/8" ID silicone hose running from the ASSE 1022's barb to the
SeaFlo suction, and its threaded branch necks that 3/8" line down to the 1/4"
LLDPE the flow regulator and V-A take — the chain
[`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) Open items 3
closes, in the order it builds:

    3/8" hose → [MTB-0606WP] → 3/8" hose → SeaFlo suction
                     └ branch ↑ PP451223W → PP061208W → 1/4" LLDPE → regulator → V-A

Every station is read off the part below it: each fitting's own module says how
deep its threads make up or how far its stem is swallowed, and this file stacks
those reaches along the branch axis. Move a length in any reference module and
the stack closes on the new one.

The two branch joints are made up at the bench, not in the cabinet. A 3/8" NPTF
female landing 9.53 mm down the tee's branch leaves 2.92 mm between the two
hexes, and the adapter's 7/8" hex overhangs the tee's 11/16" by 2.35 mm a side,
so no second jaw reaches the tee once the adapter is on it. The reducer above it
has no flats at all and its stem swivels in its socket, so nothing about the
branch above the tee is wrench-work in place.

Frame: the tee's own — the run along ±X with the barb tips at ±RUN_LENGTH/2, the
branch climbing +Z. The tee is symmetric about its branch, so either barb leg
takes either end of the hose.

Run:
    tools/cad-venv/bin/python hardware/reference/tap-point-assembly/tap_point_assembly.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "basics-mtb-0606wp",
    _hw / "reference" / "jg-pp451223w",
    _hw / "reference" / "jg-pp061208w",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import basics_mtb_0606wp as tee
import jg_pp451223w as adapter
import jg_pp061208w as reducer

# Render colors, not material colors: the viewer draws thumbnails in x-ray, where a
# body is carried by its edges in its own color against a #1a1a2e ground. All three
# fittings here are white polypropylene, and three coaxial white bodies read as one
# barrel, so each is carried at a hue the stack uses once. Every one clears 3:1 on
# the ground, which is what makes it legible at all.
WHITE_PP = cq.Color(0.88, 0.89, 0.91)     # the tee — the material's own read
ADAPTER_PP = cq.Color(0.45, 0.72, 0.93)   # the PP451223W, one step up the branch
REDUCER_PP = cq.Color(0.95, 0.70, 0.38)   # the PP061208W, the branch's last fitting

# Where each fitting lands on the branch axis, each read off the part below it.
# The female adapter runs down the tee's branch to its makeup depth, so its NPTF
# mouth lands that far below the thread's free end.
ADAPTER_Z = tee.BRANCH_HEIGHT - tee.BRANCH_ENGAGEMENT
# Its 3/8" collet mouth is the plane the reducer's shoulder lands on.
COLLET_Z = ADAPTER_Z + adapter.LENGTH
# The reducer's stem is swallowed to that shoulder, so its own origin — the stem
# tip — sits that far inside the collet.
REDUCER_Z = COLLET_Z - reducer.STEM_LENGTH


def _up(part, z):
    """Stand a fitting on the branch axis: its own +X axis onto +Z, its origin to
    `z`. The branch is coaxial with the tee's, so X and Y stay at the run's."""
    return part.rotate((0, 0, 0), (0, 1, 0), -90.0).translate((0.0, 0.0, z))


def build():
    assy = cq.Assembly(name="tap-point-assembly")
    assy.add(tee.build(), name="basics-mtb-0606wp", color=WHITE_PP)
    assy.add(_up(adapter.build(), ADAPTER_Z), name="jg-pp451223w", color=ADAPTER_PP)
    assy.add(_up(reducer.build(), REDUCER_Z), name="jg-pp061208w", color=REDUCER_PP)
    return assy


def hose_a():
    """The west barb tip the hose from the ASSE 1022 slips over: (position,
    outward axis). Either leg takes either end — the tee is symmetric."""
    return tee.barb_a()


def hose_b():
    """The east barb tip the hose on to the SeaFlo suction slips over:
    (position, outward axis)."""
    return tee.barb_b()


def tube_out():
    """The 1/4" PTC mouth the branch's LLDPE run pushes into: (position, outward
    axis) — the assembly's terminal on the way to the flow regulator and V-A."""
    pos, axis = reducer.tube_port()
    return (pos[1], pos[2], REDUCER_Z + pos[0]), (0.0, 0.0, 1.0)


def main():
    assy = build()
    bb = assy.toCompound().BoundingBox()
    print("Tap-point assembly (MTB-0606WP tee + PP451223W + PP061208W)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Branch stack: adapter mouth Z {ADAPTER_Z:.2f}, its collet Z {COLLET_Z:.2f}, "
          f"reducer stem tip Z {REDUCER_Z:.2f}")
    for label, (pos, axis) in (("hose-a  ", hose_a()), ("hose-b  ", hose_b()),
                               ("tube-out", tube_out())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "tap-point-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
