# datum-03-rim-crown: the gun rides on the tube, not on the room

Scenes: `scenes/datum-03-rim-crown/index.html` (tube turns), `scenes/datum-03b-orbiting-crown/index.html` (branch: gun orbits a still tube; own file `datum-03b-orbiting-crown.md`). Depth: **deep** (eight rounds below). Origin: swarm.

## Picture it

A teal ring sits on the rim and outer wall of the tube and turns with it. Above it, an amber ring rides on balls, does not turn, and carries a short boom to the gun's printed shell. A small vertical stage in the boom sets the gun's height; a plunger reaches down to the plate face beside the dot; a counterweight sits opposite the gun; two soft cords to posts on the rotator base keep the upper ring from wandering round. The gun then follows this tube's own wobble, so the runout that a room-fixed gun would see mostly drops out.

## The proposal

Give the gun a support that is anchored to the work instead of the room. A slewing ring seats on the rim (height) and the outer wall (radial); its non-rotating half carries the gun. Nothing about the bench, the rotator's height or the rotator's runout enters the gun-to-corner pose. What remains is what the rim cannot know: how far the plate sits below the rim (seat depth), how square the plate sits against the rim (tilt), and how concentric the wall is with the bore. A plunger on the plate face at the station, feeding a small vertical stage, takes the first two out.

The seam is a circle, so rotating the whole upper assembly about the tube axis does not change gun-to-corner pose at all. That makes the tether easy (it only stops the ring wandering to another azimuth) and makes the tube-turns and gun-orbits versions the same problem for pose (see datum-03b).

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** the rim (a 1.65 mm wall, 650 mm^2 annulus) carries rings, boom, stage, gun, counterweight: about 3 kg is 0.05 MPa [calc/rim_crown.py], which is not the concern. Balls carry the upper ring on the lower. Two soft cords carry only the umbilical's drag torque.
- **Position:** rim top sets height; outside of the tube (OD skirt) sets radial position; plunger sets fine height; the boom and gun position are set by hand once.
- **Free / restrained / driven:** the upper ring's rotation about the axis is free (loosely tethered); the gun's roll, pitch and radial position on the boom are set by hand; the vertical stage is driven (proposed); the tube and lower ring are driven by the existing rotator.

## What software could command, observe, and what stays manual

- **Command:** rotator speed (existing); vertical stage position (proposed).
- **Observe:** plunger reading, which is the plate face against the ring at the station (proposed). Nothing observes the dot; radial position is set by the ring and the boom.
- **Manual / unresolved:** seating the crown, the gun's roll/pitch/radial position, the counterweight for the gun in use, seat depth if there is no plunger.

## What was tried to break it

Numbers from `calc/rim_crown.py` and the scene; masses, drag and tether stiffness are illustrative; the gun's mass and centre of mass are [unknown].

1. **Round 1: full ring with a spigot in the bore.** *Conflict:* the ring's bore spigot turns with the tube and sweeps through the nozzle and beam corridor. *Assumption:* the bore is free at rim height. *What the numbers say:* in the reference opening pose the nozzle tip is 5.0 mm above the rim and 55 mm from the axis, and the beam crosses the bore below the rim [derived from the kit's proxy pose]. The scene's clash test fires for the bore spigot. *Change:* locate on the outside of the tube (OD skirt), inner edge of both rings outside the corridor. *Cost:* radial position now depends on wall thickness and OD-to-bore offset, a term of about 0.1 mm (illustrative) that the wall-at-the-station reference would not have (see datum-01).
2. **Round 2: a ring cannot turn through the gun.** *Conflict:* any material of the *turning* lower ring passes the station once per revolution. *Change:* it is a low full annulus on the rim with inner radius outside the corridor (62.2 mm by default); only the non-turning upper ring may have a gap, which the scene provides. *Uncertain:* clearance to the wire guide is drawn geometry with the kit's proxy guide.
3. **Round 3: the centre of mass is not over the ring.** *Conflict:* with the proxy gun in the opening pose the gun's centre of mass is about 118 mm from the axis; the ball ring is 66 mm. The assembly would tip. *Change:* a counterweight opposite the gun at 100 mm radius. Three thresholds, with illustrative masses (gun and shell 1.15 kg, boom and stage 0.25 kg, rings 0.30 kg): about 0.23 kg keeps the centre of mass inside the ring (no tipping); about 0.7 kg keeps it within half the ring radius, so the ring stays in contact all round and does not rock on the rim; about 1.5 kg centres it on the axis (1.0 to 2.1 kg for 0.75 to 1.65 kg guns). The scene reports all three. The loops of `datum-16` carry most of the gun's weight and remove most of this need. *Uncertain:* real mass and centre of mass; a printed shell shifts the balance; the drive motor in the orbiting version adds to it.
4. **Round 4: the umbilical drags the ring around.** *Conflict:* 3 N at the cable exit (234 mm from the axis) is 0.7 N.m. *Assumption:* it needs a stiff tether. *What changes:* a turning ring only slides the dot along the seam; the scene shows the seam cross-section unchanged. *Change:* two soft cords. *Uncertain:* real drag; the fibre's 350 mm bend limit while emitting [manual p. 20] and an overhead-hook height slider show when routing breaks it.
5. **Round 5: the rim is not the plate.** *Conflict:* seat depth and plate-against-rim tilt stay in the vertical offset. *Change:* a plunger on the plate face at the station and a stage; the servo branch drives the stage from it (ideal servo: vertical peak-to-peak 0.00 mm against 0.20 mm without; the scene's "lap" readout). *Uncertain:* the plunger's room beside the dot, its heat and spatter, and the last 20 degrees of overlap where the bead passes under it.
6. **Round 6: thermal and spatter near the pocket.** *Left standing:* the ring is 8 to 16 mm above the rim and the plunger tip is in the pocket 3.9 mm from the wall. Nothing here says how much heat the ring or plunger sees.
7. **Round 7: the ball race under a gap.** *Left standing:* the upper ring has a gap for the gun and the balls need a cage; drawn as a full ring of balls; how they are held is not solved. The off-the-shelf 6 in lazy Susan bearing does not obviously fit (see sourcing).
8. **Round 8: which body moves.** The same hardware with the roles swapped (tube held, ring driven) is datum-03b: same pose, no rotator belt and race, a drive on the ring, and an umbilical that must go 380 degrees round.

### From travel's exchange (wave 3: `exchange/travel--on--datum-w2.md` section 1; my answers in `exchange/datum--reply-to-travel-w3.md`)

9. **Round 9: the seat was drawn, not built.** *Conflict (travel):* the scene put the ring exactly on the outside's centre; a hardware seat is a clearance fit with a job it cannot do both ways, and a plain clearance ring is a one-point follower. *Assumption:* the ring is centred by construction. *What the change alters:* the scene now draws the seat (`Ring seat on the outside`: exactly on the centre, plain clearance, three pads locked, six pads or rockers locked) with wall shape sliders (ovality, three-lobing) and a pad-clock slider. A ring rigid on the tube follows the tube's motion and none of its shape; k equal pads pass out-of-round harmonics k-1 and k+1 at gain 1 into the ring's centre (`calc/mate_harmonics.js`, `travel/calc/08`). On the scene's default tube the radial p-p over a lap is 0.24 mm for the ideal ring, 0.37 for a clearance ring, 0.18 for three pads (by luck of the clock: move it), 0.24 for six, against 0.43 for the room post. *Leaves uncertain:* the tube's real lobes and eccentricity (five tubes, eight positions each).
10. **Round 10: n=1 and the radial win.** *Conflict (travel):* if the outside's offset from the bore is the larger amplitude, no seat matters and the crown's radial win is nil. *Answer:* the eccentricity is common to a room-fixed gun and to every ring on the outside (it is the corner's own offset from the outside's centre), so it raises both floors and cannot cancel the crown's win. What decides it is w (the wobble left after indicating) minus what the pads pass. For tubes the rig accepts (w and the lobes together at most about 0.125), the crown wins at most about 0.05 mm rms and loses up to 0.03 with three pads on an oval tube; four pads or rockers are at worst neutral (`mate_harmonics.out` G). Radial is a wash; the crown's lasting case is height. *Leaves uncertain:* w after indicating, which is Derek's to say.
11. **Round 11: height needs the plate.** *Conflict:* the crown follows the rim, the corner is on the plate. *What the numbers say* (`calc/plate_seat.js`): the plate's diagonal (123.607 mm) is shorter than the bore (123.698 mm), so the slip fit does not square it; the rig's own face acceptance is a tilt of 0.139 degrees. The plunger and the stage measure what the rim cannot know; `datum-22-setting-ring` makes it instead: a plug that hangs the plate by its ports from the ledge the gun rides. This is also how the crown's vertical case survives travel's "the case is vertical alone".
12. **Round 12: the plunger's loop.** *Conflict (travel):* the plunger sits on the ring, not the gun, 22 degrees (24 mm of arc, 3 s at 8 mm/s) from the dot; the servo closes on plate-versus-ring and leaves the boom and shell out; the 1x tilt term arrives phase-shifted. *What the scene now shows:* `Delay the plunger reading by the travel to the dot` (software holds the reading 3 s). *Leaves uncertain:* the compliance between ring and dot.
13. **Round 13: the tether reacts a torque as a force.** *Conflict (travel):* two cords or a rod to one tab at 76 mm reacts the 233 mm-arm drag as a net force 3.07 times the drag into the seat (9.2 N at 3 N). *What the scene now shows:* the readout `Tether force into the ring seat`. *Answer:* the drawn tether stays two cords (the reference for comparison); the repair is travel's, a pre-tensioned steel wire pair wrapped on the ring (a pure couple, about 900 times stiffer than 1 N/mm cords, and one strain-gauged wire reads the drag torque) in `travel-14-exact-crown`. Turning about the tube axis costs nothing at the seam, so a stiff element there is free of consequence except for its reaction. *Leaves uncertain:* pretension over a lap.
14. **Round 14: three rim pads, not a full annulus.** *Conflict (travel):* a full annulus rests on the three highest spots it finds and, with a fourth, has two stable seatings; rim flatness f gives a once-per-revolution vertical error up to about f. *Answer:* accepted; `datum-22` draws three fixed rim pads and the soft-then-lock rockers (`travel-05b`). This scene keeps the annulus as first drawn. *Leaves uncertain:* f (feeler gauge on a plate).
15. **Round 15: soft pads are as stiff as the ring; a locked ring on a hot tube.** *Conflict (travel):* a pad soft enough to seat is as stiff as the ring (75 N/mm for three 50 N/mm pads: 0.013 mm per newton of change of pull). *Answer:* soft to centre, then lock (contact stiffness, 0.004 mm for 3 N at an assumed 500 N/mm per pad): the seat of `datum-22`. *Leaves uncertain:* a locked ring on a tube that grows 0.03 to 0.06 mm when hot (the lock would have to yield, or the pad be a spring flat that stiffens only sideways); whether a printed pad can be such a flat.
16. **Round 16: the flip.** *Conflict (use, via travel):* a crown that stays on its tube serves one closure. *Answer:* accepted as a design rule; `datum-22`'s ring is per closure by design (its job is to set that closure's plate) and its seat is a fresh draw at each end. `travel-14b`'s cartridge (the crown stays on its tube, the gun docks on trunnion pins in V-notches: an amplifier, 20 micron at a pin is 0.1 mm at the dot by tilt over a 40 mm span) is not drawn.

## Branches and combinations

- **datum-03b-orbiting-crown:** the gun goes round; separate scene and file.
- **datum-08 (port-pin mast):** the same idea carried by the plate instead of the rim.
- **Combinations not built:** crown lower ring carrying the fiducial tags on its top face (datum-05); the crown's Z stage as the eddy coil's scan axis (datum-06) or the touch-off axis (datum-07); the crown's plunger as the height sensor for the seam signature (datum-02).

## Unresolved problems and questions for Derek

- Gun mass and centre of mass. Whether the tubes' outside is clear from the rim to the nest. How much seat depth and rim-to-plate square vary tube to tube.
- Whether a rim-seated ring is acceptable on a finished surface, and whether it may rest on the rim while the plate is only tacked.
- Whether the counterweight plus rings (about 3 kg on the turntable) is acceptable to the printed race [unknown].

## Assumptions

- Geometry: tube, plate, rim [repo]; gun proxy 253 x 143 x 34 mm [manual] with illustrative sections and opening pose; ring sizes, boom, tether posts, plunger position illustrative.
- Runout limits 0.25 / 0.30 mm TIR [repo]; seat-depth error, tilt against the rim, OD-to-bore offset illustrative.
- Statics with illustrative masses; drag and tether stiffness illustrative.

## Sourcing pointers

`sourcing/datum.md`: 6 in lazy Susan bearing (Prime, 1.1K ratings, unchecked fit), mini linear stage (fine axis class), touch probe class for the plunger.

## Scene id

`datum-03-rim-crown` (branch `datum-03b-orbiting-crown`).
