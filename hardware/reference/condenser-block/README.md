# Condenser block + fan — donor primitive

The refrigeration loop's hot end: a finned serpentine with its fan bolted to
one face, harvested from the donor appliance along with the compressor. There
is **no STEP here** — the block was calipered, not scanned.
[`condenser_block.py`](condenser_block.py) draws the envelope the pack takes,
declares the three arrivals on it, and cuts the two holes it hangs off.

## Geometry (calipered)

Overall **56 × 154 × 137 mm**. The 56 mm is the fan-plus-finstack depth along
the airflow axis; the other two are the serpentine's standing faces.

In the module's own frame — origin at the lower-front-west corner, `AIRFLOW`
on X, `FACE_A` on Y, `FACE_B` on Z:

| Station | Face | Location | Stands on |
|---|---|---|---|
| `refrig-inlet` | intake, −X | (0, 66, 61) | the compressor's discharge stub, on its shell's +X tangent |
| `refrig-outlet` | aft, +Y | (50.5, 154, 33.75) | the cold core's evaporator-inlet station |
| `fan-power` | exhaust, +X | (56, 30, 68.5) | — |

**Both refrigerant legs arrive on a face the block is mated to**, which is what a
donor packed as an envelope is for: the serpentine's own headers are re-dressed to
reach them. Each joint is therefore one point read twice, with no copper drawn
between the two bodies, and
[`enclosure_assembly.refrigerant_joints()`](/hardware/manifold-layout/enclosure_assembly.py) measures
both at every build, each off the two stations meant to be one point, and
`check_refrigerant_joints` reds the `refrigerant-joints` gate if either opens. The fan
is on the face its air leaves by.

`stations_hold()` holds all three to the box this module draws: each stands on
the face its own axis points out of, and inside that face's own edges.

## The two recesses

**Both Y faces stand back, and the same way.** Each is a **20 mm** recess running
the block's whole 56 mm width and the whole standing height less **0.4 mm** of
folded sheet at either end — so each face presents two flanges of 56 × 20 × 0.4
with 136.2 mm of open air between them, and each recess opens on **three** sides:
its own face and both flanks. Between the two, 114 mm of serpentine.

That is what the box has to hold the block by. There is no other purchase on a
donor packed as an envelope.

## The mount

The block hangs off two holes, both in the **aft** flanges. Both are Ø5, drilled
in the 0.4 mm sheet — one in the base flange, one in the crown — on a single
vertical line standing **29 in from the intake face** and **15 in from the aft
face**. The **fore flanges carry no hole**: that end of the block slides into
something instead.

| Mount | Face | Location |
|---|---|---|
| `mount-base` | base, −Z | (29, 139, 0) |
| `mount-crown` | crown, +Z | (29, 139, 137) |

`mount_seats()` is the same line read as a pair of FACES rather than holes — the
underside of each flange, which is where a screw down that line closes and what a
boss under it has to reach. The machine sets the block down unturned
([`enclosure_assembly.build_condenser`](/hardware/manifold-layout/enclosure_assembly.py)), so
those two insets read off the world's X− and Y+ faces at this pose.

`mounts_hold()` holds both holes clear of all four flanks, inside the aft
recess's own depth and clear of both its flange root and its free edge, the sheet
at either end at its own thickness, and probes the solid for material or air where
each of those puts it.

## Where it stands

Which wall the block stands against, which way its air crosses the cabinet,
and what the lane beside it is worth are the machine's —
[`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) and
[`../../printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md).
It stands east of the compressor with its intake face closed on that shell's own +X
tangent — an oblong can meets a plane along one line, and the discharge stub it is
made up to stands on the same line — one `SUCTION_LANE` aft of that can, so its own
aft face is the plane the cold core butts. It does **not** stand on the floor slab:
the box takes its four flanges, a groove off the front wall at the fore pair and a
bored boss under each aft hole, and the crown of what carries it is what the flavour
pack sets down on.
