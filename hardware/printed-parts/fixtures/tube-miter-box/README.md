# Tube miter box

A printed block that holds 1/4" and 3/8" OD LLDPE tube round and guides a razor blade
square across it. Two open troughs, one per tube size, run the length of the block; one
slot crosses both. The tube lies in its trough, a single-edge razor blade drops into the
slot, and the slot's walls either side of the trough hold the blade in one plane while
the trough holds the tube round under it. The stroke ends when the blade's spine lands on
the top face, with the edge [1.55 mm](TMB_RAZOR_PAST_FLOOR) below the trough floor.

**Status: CAD checked, physical trial untested.** The printed slot's width and a cut on
real tube have to be seen before this replaces anything. This is bench tooling, separate
from the machine assembly and its BOM.

| File | Use |
|---|---|
| [`tube_miter_box.py`](tube_miter_box.py) | Generator, dimensions and geometric checks |
| [`tube-miter-box.stl`](tube-miter-box.stl) | The print, on its bottom face |
| [`tube-miter-box.step`](tube-miter-box.step) | Exact, material-coloured solid |

## Print

Print in the owned PET-GF15, flat on its bottom face. Every surface is vertical, upward
or a valley; nothing needs support. The slot is [0.8 mm](TMB_SLOT_W) wide as drawn, two
facing walls with the gap between them, and takes a 0.009" single-edge razor blade with
room or a 0.025" utility blade close. A print whose slot binds a utility blade still
takes the razor.

## Use

The block is [50 × 24.8 × 18 mm](TMB_BLOCK). The troughs are [6.85 mm](TMB_TROUGH_1_4)
and [10.02 mm](TMB_TROUGH_3_8) wide, the tube's diameter plus a [0.25 mm](TMB_RUNNING)
running fit each side, [20 mm](TMB_TROUGH_PITCH) apart. The slot is [40 mm](TMB_SLOT_L)
long and stands [5 mm](TMB_OFFCUT_SIDE) from one end face and [19 mm](TMB_KEEP_SIDE) from
the other: the tube being kept lies along the long side, the offcut on the short.

1. Lay the tube in its trough with the cut line over the slot and the kept length on the
   long side. The trough takes the tube from above at any point along its length.
2. Drop a single-edge razor blade into the slot, edge down, and push it down flat until
   its spine lands on the top face. One stroke: the edge passes
   [1.55 mm](TMB_RAZOR_PAST_FLOOR) below the tube's floor.
3. Lift the blade out and lift the tube out.

A utility knife's blade goes into the same slot and stops on the slot floor,
[2.5 mm](TMB_TROUGH_FLOOR_ABOVE_SLOT_FLOOR) below the trough floor, with the knife's nose
on the top face. The 3/8" tube's crown sits [2.98 mm](TMB_WALL_ABOVE_3_8) below the top
face, so the blade is already held by the slot walls before it reaches either tube.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/fixtures/tube-miter-box/tube_miter_box.py`
