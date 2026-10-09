# room-07: grid table (dog holes, welding-table or breadboard grid)

**Origin:** swarm (room framing). **Scene:** none of its own; the budget view `scenes/room-07-coarse-fine-budget` carries its numbers. **Depth:** sketch, with one wrong first guess corrected.

## Picture it

A bench top drilled with a regular grid of round holes, like the multi-function tables woodworkers use (20 mm holes on a 96 mm grid) or a welding table's or optical breadboard's. Round pegs (dogs) drop into holes and locate whatever is pushed against them. The rotator's base and the gun's frame both sit on the same grid.

## The proposal

Use the grid as a shared datum. The rotator's four Ø10 clamping holes [repo] and the gun frame's feet are fitted to grid pegs, so the relative position of tube and gun is *registered* to the grid's accuracy and the peg fit, and is the same every time the set-up is rebuilt after the bench is cleared. It is a way of making "clamped to the bench" repeatable without any moving part.

## What carries, what establishes position, what is free

Carries: the bench top. Position: dog fit plus grid accuracy. Free: nothing; nothing moves. Driven: nothing (the gantry or fine stage on it is another idea). Escape at the end of a bead: not provided.

## Software

Commands: none. Observes: none by itself; it makes a *camera's* calibration to the bench repeatable (the frame of the bench holes is the frame the cameras are calibrated in). Manual: dropping the dogs in the right holes.

## What was tried to break it

1. **My first guess:** the grid pitch sets the range left for the fine stage (pitch/2, 48 mm for a 96 mm grid). *Assumption:* the gun frame must be placed at the nearest hole to where it is needed. *Finding:* the gun-to-tube offset is a design constant. A printed adapter can carry any offset, so the pitch drops out; what remains is dog fit and grid accuracy (illustrative 0.25 mm together) plus the tube's own variation (`room-07-coarse-fine-budget`). The grid provides registration, not range.
2. **Accuracy is not stated.** No accuracy figure was found for the 96 mm pattern (it is a widely copied pattern; drilling templates are sold); a machined welding table or a breadboard has a stated hole accuracy but was not priced here. *Leaves:* measure a hole pattern with the indicator Derek already owns.
3. **It does nothing for Z.** Plate depth is untouched.
4. **The roll-up has no observer term (eyes, wave 2).** The budget view's row for the software-calibrated arrangements (room-06, room-03) carried a residual of 0.15 mm [illustrative] whatever the observer. *Finding:* the residual depends on what the observer reports (room-06, item 8): a spot on the plate alone leaves about 0.4 mm (median 0.22), the spot plus a nozzle-height camera about 0.135, a marker cube on the shell about 0.11. *Change:* `room-07-coarse-fine-budget` takes an observer choice for those rows and an input for a depth read from a picture (eyes-16: about 0.03 mm) that replaces the plate-seat-depth term in every row; the scene is tagged as a lens. *Leaves:* the observer noise is illustrative; the depth number still needs an axis to apply it.

## Branches and combinations

The grid is the coarse layer under `room-01` (a table with a hole in the grid) or `room-05` (the cell's floor).

## Unresolved

Grid accuracy; whether a wooden top holds it over time; whether the rotator's base can take dog holes in its printed feet.

## Assumptions

Hole 20 mm, pitch 96 mm, top 1157 x 773 mm: as listed by retailers of a commercial table (sourcing 16), not verified against the maker. Dog fit and accuracy 0.25 mm: **[illustrative]**.

## Sourcing pointers

`sourcing/room.md` entry 16 (no price observed; the grid is a copied pattern).

## Scene

`scenes/room-07-coarse-fine-budget` (grid row).
