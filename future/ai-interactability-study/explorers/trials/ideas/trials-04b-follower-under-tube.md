# trials-04b-follower-under-tube: the actuator on the workpiece side

Branch of `trials-04-seam-map-replay`. The scene's "where the follower sits" radio shows it (gun side, X slide only, X slide plus lift).

## Picture it

The gun hangs from whatever passive support is convenient. Under the rotator sits a small stage: one horizontal axis toward the gun and a small lift. The seam map, learned in the first turns, is replayed by moving the whole rotator by a few tenths of a millimetre, slowly, keyed to its own angle.

## The proposal

Only two directions matter to the dot-to-seam error: radial (toward the gun) and vertical. So a tube-side follower needs only those two: an X slide under the rotator and a lift. The Y direction just slides the dot along the seam. All the actuators are on the workpiece side, which is stationary and well supported; the gun side needs no actuator at all. The demand is small (about 0.03 mm/s at 1× for 0.125 mm amplitude at the fastest speed, `seam_rates.py`), which is why moving a few kilograms is plausible.

## Carries, locates, free

The stage carries the rotator base, motor tower, shoe and tube (rotating mass 1.40 to 2.01 kg **[repo]** plus the base, PET-GF 300 x 250 x 12 mm, and the tower; a few kilograms in total, **[unknown]** exactly). The rotator angle keys the map.

## Software

Command: stage X (and lift), rotator speed. Observe: the judge camera's dot-to-seam offset; stage position (step count or a scale). Manual: rough placement.

## Tried to break it

1. **X-only leaves the height error.** The scene shows it: switch the placement to "X slide only" and the height strip is unchanged. Repair: add the lift. Leaves: the lift carries the same mass and must not tilt the rotator; a lift that tilts turns into a face error.
2. **The gun's own sway is not corrected by the map.** A passive support sways with cable pull and vibration; the map only handles what repeats with the rotator angle. Repair: closed loop on the judge camera (the stage follows the dot error, not just the map). Leaves: closed-loop bandwidth with a several-kilogram stage; a 1 Hz loop is easy, higher is not.
3. **The shoe and the wire.** The ground shoe wipes the tube **[repo]**; if it rides on the rotator base it moves with the stage. Leaves: the wire feed and gas geometry are relative to the gun, which does not move: the tube moves under it, which is the same as today's operator holding still.
4. **Existing hardware.** The rotator is clamped to a bench through four Ø10 holes **[repo]**; the stage would sit between it and the bench. Leaves: a stage that stiff enough to carry a running rotator.

5. **The passive support has to be stiff on two axes, and a crown is one (from datum's exchange, wave 2, section 5).** *Conflict, in this variant:* the follower is sized for the tube's wobble (0.03 mm/s, tenths of a millimetre to a few for seating). The gun's static offset from a soft passive support is not in that budget: `freedom-01` finds that with only bungees and wires holding the gun, 1 N of umbilical pull moves the dot about 40 mm radially, thirty times the follower's stroke and far outside the dot knee's capture range (about 0.5 mm). *Assumption behind it:* the gun can hang from anything and the passive support's only cost is bandwidth. *Change:* the passive support must be stiff on radial and vertical and soft on the tangent, and standing on the work: a **crown** on the rim (`datum-03`, `datum-16`) follows the runout mechanically (0.125 mm radial and 0.15 face at the station), leaving the tube-side stage the slow part only (seat depth, a constant per tube; the plate's tilt against the rim, about 0.10 mm). The scene's support radio shows it: 1.5 N at 0.6 mm/N is 0.9 mm on a stiff boom (inside the follower's travel), and 60 mm at 40 mm/N puts a LIMIT badge on the stroke row. The supports must be forces: a stiff vertical support anchored in the room and attached to a gun that rides the rim fights the rim by stiffness times the face wobble (30 N for a 200 N/mm wire against 7.4 N of crown, `datum-16`). *Leaves uncertain:* every pull and compliance is **[unknown]**; three supports on one printed shell without over-constraining it; the answer to my own open question ("how far does a gun on a passive support wander in ten minutes") has a floor now: the cable's pull divided by the support's stiffness.

## Combinations

`trials-16-tube-moves-gun-hangs` is the same idea with the map dropped and a camera in the loop. `trials-03` finds the seam first.

## Unresolved

Q: How much stage stroke do you expect to need for tube-to-tube seating differences (0.5 mm? 2 mm?) with the nest as it is today?

## Assumptions

Speeds and rotating mass **[repo]**; amplitudes **[derived]** from the accepted runout; stage mass **[unknown]**.
