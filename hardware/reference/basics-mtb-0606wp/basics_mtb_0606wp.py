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

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

import math
from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "basics-mtb-0606wp.step"
PAYLOAD_PATH = _here.parent / "basics-mtb-0606wp.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

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


def main():
    print("basics-mtb-0606wp")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
