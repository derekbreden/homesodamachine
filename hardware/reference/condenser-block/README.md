# Condenser block + fan — donor primitive

The refrigeration loop's hot end: a finned serpentine with its fan bolted to
one face, harvested from the donor appliance along with the compressor. There
is **no STEP here** — the block was calipered, not scanned.
[`condenser_block.py`](condenser_block.py) draws the envelope the pack takes
and declares the three arrivals on it.

## Geometry (calipered)

Overall **56 × 178 × 151 mm**. The 56 mm is the fan-plus-finstack depth along
the airflow axis; the other two are the serpentine's standing faces.

In the module's own frame — origin at the lower-front-west corner, `AIRFLOW`
on X, `FACE_A` on Y, `FACE_B` on Z:

| Station | Face | Location | Stands on |
|---|---|---|---|
| `refrig-inlet` | intake, −X | (0, 45.25, 75) | the compressor shroud's discharge stub |
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

## Where it stands

Which wall the block stands against, which way its air crosses the cabinet,
and what the lane beside it is worth are the machine's —
[`front_half.py`](/hardware/manifold-layout/front_half.py) and
[`../../printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md).
It stands on the floor slab east of the compressor shroud, its intake face mated
flush against the shroud's, with the `AIRFLOW` axis across the machine.
