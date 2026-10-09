# travel-13-print-to-adjust: an adjustment made by a printer

**Picture it.** The AI reads the dot's error after a dry run, works out that the gun needs to rise 0.35 mm and shift 0.2 mm toward the wall, and does two things: it picks brass shims from a stack (0.05 mm steps) for the vertical and queues a small printed spacer for the radial. Twenty minutes later a person drops them in and locks the holder. The stage is a printer and a hand; the software computed it and will check the result.

Scene: none. Idea only.

## The proposal

For adjustments needed once per batch or once per tube type, motion is overkill. A shim or a printed spacer is a stage with one position and no bearing. Derek's stated preference is to build and print; lead time for a print is minutes, and there is no order or quote. The AI's job: compute the thickness from the observed error and the known lever, say which shims to use, and verify afterwards.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** whatever the shim sits in (holder pad, nest register, seat). **Establishes position:** the shim's thickness. **Free / restrained / driven:** none: locked after insertion.

## What software could command, observe, what stays manual

- **Commands:** a print job (if the printer is reachable), or an instruction. **Observes:** the dot after insertion. **Manual:** inserting, locking; measuring the shim.

## What was tried to break it

**1. Printed thickness.** *Conflict:* a printed PET-GF or PETG shim is good to perhaps 0.05-0.1 mm and creeps under a clamp (illustrative). *Change:* use metal shim stock as the standard (0.002 to 0.016 in in Prime assortments, `sourcing/travel.md` 17) and print only wedges and spacers, measured with calipers before use. *Leaves:* creep of the printed part.

**2. Resolution versus the loop.** *Conflict:* a 20-minute loop is fine for a lot offset, useless for the per-tube trim. *Change:* use it for the coarse-fine boundary: the shim takes the per-lot mean, a stage takes the rest.

**3. Angle.** *Conflict:* a shim moves position, a wedge changes angle by thickness over span, and the lever from the wedge to the dot multiplies. *Change:* compute with `travel-05-lever-map`. *Leaves:* wedge stability.

**Wave 3 entry, from use's exchange ("Also noticed").** **The printer as the coarse stage, with a two-tube delay (use).** What the AI has that a person does not is hundreds of logged closures: if the per-tube trim is N(0.8, 0.3) mm and the fine range is +-0.5 mm, 16 % of tubes fit; a shim that recentres the mean puts 90 % inside (illustrative). The 20-minute print runs while the hand is busy with the next tube, its lag is two tubes, and its input is the same mean-learning as the clamp's bias (`travel-05b`, `calc/13`). *Assumption behind it:* each tube is corrected from its own measurement. *What it leaves uncertain:* printed thickness and creep.

## Branches and combinations

- **With travel-01/02:** shims set the neighbourhood the stack works from. **With travel-04:** shims under the seat's block are the "adjust once per batch" step.

## Unresolved problems and questions for Derek

- Does he have a printed-part loop he trusts to +-0.05 mm? Would he accept shimming by hand between lots?

## Assumptions

- Printed accuracy and creep: illustrative. Shim thicknesses: listing text.

## Sourcing pointers

`sourcing/travel.md`: brass shim stock (17).

## Scene id

None.
