# datum-18-flush-to-the-table: the tabletop as a surface plate, the tube found by touch

Scene: `scenes/datum-18-flush-to-the-table/index.html`. Depth: developed. Origin: branch of `room-01-table-opening` (Derek's table-opening example), combining `datum-07-touch-off` and `datum-01-datum-chain`. Exchange: `exchange/datum--on--trials-w2.md`, the examples paragraph.

## Picture it

A section through the table opening: the tabletop with its hole, the shelf and box hung below, the tube standing with its rim at table height, a gantry rail on the table and a carriage with a probe. Three numbered touches: the tabletop beside the hole, the rim, the plate. A magnified strip shows the rim against the tabletop, in tenths of a millimetre. Below, twelve tubes as dots on three lines (how far the dot is above or below the seam for each way of setting the shelf), and a plan of the hole with the tube where it fell and three touches on its wall.

## The proposal

In the table opening the rim stands flush with the table and the gun works at countertop height (`room-01`). The room explorer reads the table as the rim plane. Read it also as a datum: a plane that a probe on the gantry can compare the rim with. The shelf that lifts the tube then has a different job. Instead of a precise axis (its own accuracy, plus the tube's length, plus the seat depth all in the dot height) it is a servo on a null: raise the shelf until a touch of the tabletop and a touch of the rim agree. What is left is the probe (a few hundredths of a millimetre) and the table's local flatness, and the tube's length has dropped out because the rim, not the tube's bottom, is what was set. Seat depth stays, as in the datum chain; a touch of the plate at the station removes it and sets the dot height directly.

The same probe finds the tube's place in the loose hole. A hole of Ø160 around a Ø127 tube leaves 16.5 mm each way (`room-01`); an untouched off-centre tube puts the station where the gun does not expect it, and 1 mm across the gun's line is 0.93 degrees of yaw (the tangent arithmetic of the shared context). Three wall touches at the station, 15 mm either side of the line, give the circle's centre: two wall points 2a apart differ by 2a/R = 0.485 of the tangent offset, so 0.02 mm of touch noise gives the offset to about 0.06 mm. This does the job of the fitted collar in `room-07`, and it finds the tube whatever the fit.

## What carries the loads, what establishes position, what is free or restrained

Unchanged from `room-01`: the table and its hung box carry the rotator on the shelf; rails, bridge, carriage and post carry the shell. The tabletop carries nothing new; it is a flat surface to compare against. Position: the tabletop plane for the rim; the tube's own wall for radial and tangent, by touch; the plate face by touch. Driven: shelf Z (proposed), gantry X and Y, the probe's down and back.

## What software could command, observe, and what stays manual

- **Command:** shelf Z to flush; gantry X and Y to each touch point; probe down until contact.
- **Observe:** a contact bit and an axis position at each touch; from them rim minus tabletop, plate depth, the wall's position at three stations, the circle's centre.
- **Manual:** dropping the tube in and seating it; fitting the probe (in place of the nozzle for a dry run, `datum-07`); flattening a ring of table round the hole.

## What was tried to break it

Spreads are placeholders and unmeasured (tube length 0.6 mm and seat depth 0.4 mm one standard deviation, shelf repeatability 0.3 mm, probe 0.03 mm, table flatness 0.10 mm).

1. **Dot height over twelve tubes:** dead reckoning (the shelf goes to a recipe height) 0.91 mm rms (draw 3); flush 0.35 (seat depth 0.4 and flatness 0.10 remain); plate touch 0.03. Seat depth and tube length are the two spreads the datum-chain scene flagged as unknown; ten calipers and a depth gauge would size them.
2. **The tabletop is not a surface plate.** The flush mode inherits the local flatness one for one. Repair: an aluminium or steel ring set flush round the hole; or touch the table on both sides of the hole and use the mean.
3. **Touches sixty millimetres apart** carry the gantry's own tilt and sag. *Left standing:* a differential probe (both touches in one move) would cancel most of it; not drawn.
4. **The wall is 6 mm down.** The wall touches need a stylus that reaches the pocket, not a carriage sensor; the rim edge could be touched from the carriage but the wall's foot cannot.
5. **The rim may not be touched** without care on a finished edge (a fraction of a newton). *Left standing.*

## Branches and combinations

- Branch of `room-01-table-opening`; uses `datum-07` (the touch), `datum-01` (what a reference on the work makes unnecessary), relates to `room-09-move-only-shelf` (the shelf as the only motorised axis: here it is a servo), `room-07-grid-table`, `room-05-drawer-cell`, `trials-14` (contact sense).

## Unresolved problems and questions for Derek

- Tube length and seat depth over a dozen tubes; what the table is made of and how flat it is where the hole would go; whether a 12 V linear actuator with a limit switch has a repeatability within a millimetre, so the servo can finish the job.
- Whether the rim can be touched.

## Assumptions

Hole and tube dimensions from `room-01` and `[repo]`; spreads above; twelve tubes drawn from a seeded generator.

## Sourcing pointers

`sourcing/room.md` entry 11 (12 V linear actuator); `sourcing/datum.md` (CR Touch class probe, ruby-ball stylus); a flat aluminium plate for the ring (this pass).

## Scene id

`datum-18-flush-to-the-table`.
