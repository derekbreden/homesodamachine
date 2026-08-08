# Condenser block + fan — donor primitive

The refrigeration loop's hot end: a finned serpentine with its fan bolted to
one face, harvested from the donor appliance along with the compressor. There
is **no STEP here** — the block was calipered, not scanned.
[`condenser_block.py`](condenser_block.py) draws the envelope the pack takes,
declares the three arrivals on it, and cuts the two holes it hangs off.

## Geometry (calipered)

Overall **56 × 178 × 151 mm**. The 56 mm is the fan-plus-finstack depth along
the airflow axis; the other two are the serpentine's standing faces.

In the module's own frame — origin at the lower-front-west corner, `AIRFLOW`
on X, `FACE_A` on Y, `FACE_B` on Z:

| Station | Face | Location | Stands on |
|---|---|---|---|
| `refrig-inlet` | intake, −X | (0, 45.25, 75) | the compressor's discharge stub, on its shell's +X tangent |
| `refrig-outlet` | aft, +Y | (39, 178, 47.75) | the cold core's evaporator-inlet station |
| `fan-power` | exhaust, +X | (56, 30, 75.5) | — |

**Both refrigerant legs arrive on a face the block is mated to**, which is what a
donor packed as an envelope is for: the serpentine's own headers are re-dressed to
reach them. Each joint is therefore one point read twice, with no copper drawn
between the two bodies, and
[`front_half.refrigerant_joints()`](/hardware/manifold-layout/front_half.py) measures
both at every build and fails the build if either opens. The fan is on the face its
air leaves by.

`stations_hold()` holds all three to the box this module draws: each stands on
the face its own axis points out of, and inside that face's own edges.

## The mount

The block hangs off two holes, and the block is otherwise envelope. Both are
Ø5, drilled in **0.4 mm sheet** — one in the base plate, one in the crown plate
— on a single vertical line standing **29 in from the intake face** and **15 in
from the aft face**. Between them a **16 × 20 × 150.2** shaft runs the full
standing height, the 151 less a plate at each end.

| Mount | Face | Location |
|---|---|---|
| `mount-base` | base, −Z | (29, 163, 0) |
| `mount-crown` | crown, +Z | (29, 163, 151) |

The machine currently sets the block down unturned
([`front_half.build_condenser`](/hardware/manifold-layout/front_half.py)), so those
two insets read off the world's X− and Y+ faces at this pose.

`mounts_hold()` holds the shaft clear of all four sides, both holes inside that
shaft, the sheet at either end at its own thickness, and probes the solid for
material or air where each of those puts it.

## Where it stands

Which wall the block stands against, which way its air crosses the cabinet,
and what the lane beside it is worth are the machine's —
[`front_half.py`](/hardware/manifold-layout/front_half.py) and
[`../../printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md).
It stands on the floor slab east of the compressor, its intake face closed on that
shell's own +X tangent — an oblong can meets a plane along one line, and the
discharge stub it is made up to stands on the same line.
