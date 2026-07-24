"""Basics MTB-0606WP white barb tee × male branch, 3/8" ID barb × 3/8" ID barb ×
3/8" NPT M, white polypropylene — the tap point on the appliance's water path
([`ledger/bom.md`](/hardware/ledger/bom.md) §3). It sits inline in the 3/8" ID
silicone hose between the FFL38BARB38 and the SeaFlo pump inlet, both run legs
under LOKMAN worm-gear clamps, and tees clean-cycle tap water off the branch to
the flavor manifold's V-A inlet through the John Guest PP451223W + PP061208W
chain.

A barbed run with three ridges per leg, a wrench hex at the branch base, and a
3/8"-18 NPT male branch. Ridges are stacked cones — the same modeling class as
the FFL38BARB38's barb stem next door — and the thread is a real 1:16 taper at
pitch diameter, no helix, so the PP451223W's socket shares its surface rather
than fighting it. The moulded bores are cut, so the barb tips read as tube ends.
Dimensions come off the Thogus TT3666 drawing, polypropylene column: the same
3/8" barb × 3/8" barb × 3/8" NPT moulding, with letters as lettered there.

Frame: +X = the run, the two barb tips at ±RUN_LENGTH/2 and the tee body on the
origin; +Z = the branch, its NPT free end at BRANCH_HEIGHT. The hex carries a
corner on the run axis, so its flats face ±Y.

Run:
    tools/cad-venv/bin/python hardware/reference/basics-mtb-0606wp/basics_mtb_0606wp.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

RUN_LENGTH = 56.13          # barb tip to barb tip, 2.21" (TT3666 dim G, PP row)
BARB_ROOT_D = 9.40          # run body Ø, and the root between ridges, .370" (dim A)
BARB_CREST_D = 10.92        # ridge crest Ø, .430" (dim B)
BARB_TIP_D = 9.03           # OD at the tip, where the hose starts on, .3556"
BARB_RIDGES = 3             # per leg
RIDGE_PITCH = 3.94          # .155"; each ridge's sharp shoulder faces the body
LEAD_LENGTH = 3.96          # tip cone ahead of the first ridge, .156"
BRANCH_NECK_D = 9.27        # between the run body and the hex, .365" (dim C)
HEX_ACROSS_FLATS = 17.53    # .69" (dim J)
HEX_LENGTH = 6.35           # wrench flat thickness, .25" (dim D)
BRANCH_HEIGHT = 29.72       # run centerline to the thread's free end, 1.17" (dim F)
THREAD_LENGTH = 12.45       # moulded thread, .49" (dim E)
THREAD_MATE_PITCH_D = 15.93 # 3/8-18 pitch Ø at the plane a female's mouth lands
                            # on (E1 = .62701", ASME B1.20.1)
THREAD_TAPER = 1.0 / 16.0   # NPT taper, on diameter, per unit of length
BRANCH_ENGAGEMENT = 9.53    # 3/8" NPT total makeup, hand plus wrench — how far a
                            # female runs down this thread (ASME B1.20.1)
RUN_BORE_D = 6.22           # through-bore of the run, .245" (dim H)
BRANCH_BORE_D = 10.92       # branch counterbore at the thread, .430" (dim I)
BRANCH_BORE_DEPTH = 16.91   # of that counterbore, in from the free end, .666"
HOSE_ID = 9.53              # the 3/8" ID silicone hose each run leg takes

HEX_ACROSS_CORNERS = HEX_ACROSS_FLATS * 2.0 / math.sqrt(3.0)
THREAD_BASE_Z = BRANCH_HEIGHT - THREAD_LENGTH
HEX_BASE_Z = THREAD_BASE_Z - HEX_LENGTH
BARB_ZONE = LEAD_LENGTH + BARB_RIDGES * RIDGE_PITCH
CLAMP_LAND = RUN_LENGTH / 2.0 - BARB_ZONE - BRANCH_NECK_D / 2.0

thread_end_pitch_d = THREAD_MATE_PITCH_D - BRANCH_ENGAGEMENT * THREAD_TAPER
thread_base_pitch_d = thread_end_pitch_d + THREAD_LENGTH * THREAD_TAPER

# What the female leaves standing once it is made up — the thread this branch
# carries beyond the makeup a 3/8" NPT joint uses.
THREAD_PROUD = THREAD_LENGTH - BRANCH_ENGAGEMENT


def barb_a():
    """The −X run barb tip the silicone hose slips over: (position, outward axis)."""
    return (-RUN_LENGTH / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def barb_b():
    """The +X run barb tip the silicone hose slips over: (position, outward axis)."""
    return (RUN_LENGTH / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0)


def branch_thread():
    """The NPT male branch's free end face: (position, outward axis) — a female
    runs BRANCH_ENGAGEMENT back down it, toward the hex."""
    return (0.0, 0.0, BRANCH_HEIGHT), (0.0, 0.0, 1.0)


def _barb_leg(tip_x, along):
    """One run leg from its tip inward: the lead cone the hose starts on, then
    BARB_RIDGES cones each rising from the root Ø to the crest Ø, so every ridge
    presents its sharp shoulder to the body and the hose ratchets on."""
    axis = cq.Vector(along, 0, 0)
    leg = cq.Solid.makeCone(
        BARB_TIP_D / 2.0, BARB_ROOT_D / 2.0, LEAD_LENGTH,
        cq.Vector(tip_x, 0, 0), axis)
    x = tip_x + along * LEAD_LENGTH
    for _ in range(BARB_RIDGES):
        leg = leg.fuse(cq.Solid.makeCone(
            BARB_ROOT_D / 2.0, BARB_CREST_D / 2.0, RIDGE_PITCH,
            cq.Vector(x, 0, 0), axis))
        x += along * RIDGE_PITCH
    return leg


def _run():
    """The barbed run along X: a root-Ø barrel between the two lead cones, with
    both legs' ridges standing on it."""
    barrel = cq.Solid.makeCylinder(
        BARB_ROOT_D / 2.0, RUN_LENGTH - 2.0 * LEAD_LENGTH,
        cq.Vector(-RUN_LENGTH / 2.0 + LEAD_LENGTH, 0, 0), cq.Vector(1, 0, 0))
    return barrel.fuse(
        _barb_leg(-RUN_LENGTH / 2.0, 1.0),
        _barb_leg(RUN_LENGTH / 2.0, -1.0))


def _branch():
    """The branch up +Z: neck → hex → NPT cone. The neck starts on the run
    centerline, buried in the run, so the two meet in the moulding's saddle."""
    up = cq.Vector(0, 0, 1)
    neck = cq.Solid.makeCylinder(
        BRANCH_NECK_D / 2.0, HEX_BASE_Z, cq.Vector(0, 0, 0), up)
    hex_sec = (
        cq.Workplane("XY")
        .workplane(offset=HEX_BASE_Z)
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(HEX_LENGTH)
        .val()
    )
    thread = cq.Solid.makeCone(
        thread_base_pitch_d / 2.0, thread_end_pitch_d / 2.0, THREAD_LENGTH,
        cq.Vector(0, 0, THREAD_BASE_Z), up)
    return neck.fuse(hex_sec, thread)


def _bores():
    """The moulded waterway: the run bored end to end, and the branch bored to
    meet it — wide at the thread for the core pin, narrow at the junction."""
    run_bore = cq.Solid.makeCylinder(
        RUN_BORE_D / 2.0, RUN_LENGTH,
        cq.Vector(-RUN_LENGTH / 2.0, 0, 0), cq.Vector(1, 0, 0))
    counterbore_base_z = BRANCH_HEIGHT - BRANCH_BORE_DEPTH
    branch_bore = cq.Solid.makeCylinder(
        RUN_BORE_D / 2.0, counterbore_base_z, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    counterbore = cq.Solid.makeCylinder(
        BRANCH_BORE_D / 2.0, BRANCH_BORE_DEPTH,
        cq.Vector(0, 0, counterbore_base_z), cq.Vector(0, 0, 1))
    return run_bore.fuse(branch_bore, counterbore)


def build():
    return _run().fuse(_branch()).cut(_bores())


def main():
    part = build()
    bb = part.BoundingBox()
    print("Basics MTB-0606WP 3/8\" barb × 3/8\" barb × 3/8\" NPT M white PP tee")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Run {RUN_LENGTH:g} tip to tip; {BARB_RIDGES} ridges Ø{BARB_CREST_D} per leg "
          f"at {RIDGE_PITCH:g} pitch; {CLAMP_LAND:.2f} of Ø{BARB_ROOT_D} land per side")
    print(f"  Branch {BRANCH_HEIGHT:g} to the NPT end; hex {HEX_ACROSS_FLATS:g} across flats "
          f"× {HEX_LENGTH:g} (top face Z = {THREAD_BASE_Z:.2f})")
    print(f"  Thread pitch Ø{thread_base_pitch_d:.2f}→Ø{thread_end_pitch_d:.2f} "
          f"× {THREAD_LENGTH:g}; a female runs {BRANCH_ENGAGEMENT:g} down it, its mouth "
          f"landing at Z = {BRANCH_HEIGHT - BRANCH_ENGAGEMENT:.2f}, {THREAD_PROUD:.2f} proud")
    for name, (pos, axis) in (("barb_a", barb_a()), ("barb_b", barb_b()),
                              ("branch_thread", branch_thread())):
        print(f"  {name}: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}) "
              f"out ({axis[0]:.0f}, {axis[1]:.0f}, {axis[2]:.0f})")
    print(f"  Solid valid: {part.isValid()}")
    out = _here.parent / "basics-mtb-0606wp.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
