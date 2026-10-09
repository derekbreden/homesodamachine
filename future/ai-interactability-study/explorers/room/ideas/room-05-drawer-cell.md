# room-05: drawer cell

**Origin:** swarm (room framing; a different sequence). **Scene:** `scenes/room-05-drawer-cell`. **Depth:** developed.

## Picture it

A cabinet the size of a small oven: a frame with panels, a door with a laser window, and inside it a printed shell on a small XYZ stage on the back wall, two cameras fixed to the frame, and, at the bottom, a drawer. The rotator with the tube on it rides out on the drawer for loading and indicating, rolls back in, and climbs a short ramp into three balls that seat it. The gun and the cameras never move. The door interlock tells the laser when it may fire.

## The proposal

Make the room a machine cell. It is the laser enclosure (which unattended operation needs anyway), the datum (a dock for the rotator), and one rigid frame for gun and cameras. The rotator's own nest already registers the tube on its ID with 0.20 mm radial clearance and three adjusters **[repo]**; adding a dock for the rotator brings the tube's position relative to the cell to a few tenths of a millimetre sideways. What remains for the gun's fine stage is millimetres in plate depth, not tens of millimetres of placement.

## What carries, what establishes position, what is free

- **Carries:** the cell frame carries the gun stage, the cameras and the drawer rails; the drawer carries the rotator.
- **Establishes position:** the three-ball dock for the rotator; the nest for the tube; the frame for gun and cameras.
- **Driven:** the drawer (motor optional), the gun stage (3 small axes), the rotator. **Free:** the drawer between stops. **Restrained:** the gun's three rotations (saddle print).
- **Escape at the end of a bead:** the dock ramp lowers the drawer 26 mm over its first 40 mm; it can serve as the vertical escape if it is fast enough (speed unmeasured).

## Software

- **Command:** drawer position; gun stage X, Y, Z; rotator.
- **Observe:** two fixed cameras (A: the dot, from the frame top; B: the nozzle tip against the rim, from the far side of the bore at rim height; wave 3: **B is seen, not blind**, and A and B are the complementary pair a calibration needs: where the beam lands, and where the nozzle is along it), dock and door switches, step counts. **The drawer stroke is an observing stroke:** as the tube rolls in past a fixed camera its rim's height and lateral position pass through the frame before the dock seats it. Because the gun and cameras are one frame, the dot sits at the same pixel in every image and the seam is what moves: calibration is done once.
- **Interlock as logic:** laser enabled only if the drawer is seated and the door closed (on top of the existing work-contact interlock).
- **Manual:** loading, seating, indicating and tacking with the drawer out; one-time alignment of gun and cameras.

## What was tried to break it

1. **"A fixed gun still needs a big stage."** *Assumption:* the tube's position varies as it does on a bench. *Finding:* dock repeat 0.04 (illustrative) + nest clearance 0.20 [repo] + indicated runout/2 0.125 [repo] = ±0.4 mm sideways in the worst case; the loose table hole was ±16.8 (`calc/drawer-rollup.mjs`, `room-07-coarse-fine-budget`). Z is unchanged by the cell: plate seat depth ±3 mm (illustrative, unmeasured). *Leaves:* tube tilt (face runout 0.30 TIR) is nothing's to correct.
2. **The wall slides under the nozzle.** *Assumption:* pulling a drawer out is harmless. *Finding:* the nozzle is 5 mm above the rim and inside the bore near the wall; the wall passes under it within about 20 mm of travel. *Change:* the dock ramp lowers the tube 26 mm as it leaves. *Leaves:* a controlled, damped ramp.
3. **A stuck wire.** *Assumption:* the door can stay closed. *Finding:* the workflow snips a stuck wire with the head where it stopped, by hand. *Change:* a door that opens with the laser interlocked off. *Leaves:* the operator no longer sees the weld directly; the window and cameras take over.
4. **Slide play.** Ball-bearing slides are rated to 100 lb (sourcing 4) but have side play (unchecked, likely 0.5 to 1 mm); the dock, not the slides, sets position. *Leaves:* a dock that grabs a drawer that arrives 1 mm off.
5. **Fume and argon** in a small volume: extraction and purge undesigned (first version). *Wave 3:* at 18 L/min into 0.34 m3 a box that only loses gas by displacement reaches 19.5 % oxygen in 1.3 minutes (well mixed); a 100 CFM fan and a low vent fix the arithmetic, see room-18.
6. **Second closure.** The ports are reached through a Ø90 mm bore in the rotator [repo]: the drawer plate needs the matching opening.

7. **"Camera B reads blocked by gun" (eyes, wave 2 exchange).** *Variant:* B at rim height, 330 mm behind the barrel (176 degrees round). *Assumption:* B and A are two ways of seeing the same thing, and the drawn "blocked" was a judgement. *Finding:* it was the drawn test, not the physics: the tip is a point on the axis of a thin part and the kit's default 0.8 mm end tolerance hides it behind the nozzle's own skin (kit README section 5: pass eps 3). With eps 3 B reads the tip over the rim (5.0 mm) from the far side of the bore. eyes's sweep of stations 330 mm out and 15.6 mm above the rim: the tip is seen from 28 of 36 azimuths, the dot from 7. The profile station eyes drew (az 90) stands **on the drawer's own path**: the drawer travels 420 mm along +Y and the tube would reach a camera at y = 330 (the scene draws both and raises a limit badge). *Change:* the scene's test uses eps 3; a radio moves B between the far side and the profile place; the I/O table lists nozzle height as seen and the stroke as an observing stroke. *Leaves:* whether the wire tip may cross B's view (it is not an occluder in the drawn scene); glare on the far rim.
8. **"The cabinet is a designed light environment" (eyes, wave 2).** *Answer:* yes, and the design is a branch: `room-18-cabinet-station` (matte black interior, a red band-pass on A, switchable lamps, the specular and double-bounce map of lamp places, extraction sized to the argon, a sleeve port). *Leaves:* the photometric part waits for a photograph (eyes-06b).

## Branches and combinations

- **Puck on a carousel:** the tube seated in a puck at one station, a turntable (a lazy susan bearing, sourcing 3) indexing it to the weld rotator.
- `room-01b`'s notch and slot are the same idea without the cabinet.
- Combination with `room-03-wall-port`: replace the small fine stage by the ball port and tail in the cabinet lid.
- **`room-18-cabinet-station`** (wave 3 branch): this cabinet with extraction, gas, lamps and a hand port.
- **`eyes-13-cords-see-a-spot`** (combination of room-06 and this cabinet's cameras, adopted): A (spot) and B (nozzle height) are its calibration pair.

## Unresolved, questions for Derek

- Dock hardware: three balls in V grooves, a commercial zero-point clamp, or pins; the rotator has none.
- Motorised or hand-pulled drawer.
- Cabinet size (about 0.8 x 0.7 x 0.65 m here) and where it stands.
- OD-rated viewing window: see sourcing 14; safety-critical and unchecked.

## Assumptions

Dock repeat 0.04 mm, drawer travel 420 mm, ramp 26 mm over 40 mm, stage ranges ±3 / ±5 mm: **[illustrative]**. Nest clearance 0.20 mm, runout 0.25 / 0.30 mm TIR: **[repo]**. Plate seat depth ±3 mm: **[unknown]**.

## Sourcing pointers

`sourcing/room.md` entries 4 (22 in drawer slides), 12 (2020 frame), 13 (XYZ manual stage; low volume), 14 (OD6+ window).

## Scene

`scenes/room-05-drawer-cell`

## Wave 2

- The cell's contacts (door, dock, seat) are the natural permit chain for `room-14-trigger-path`: a hand fires from a pendant outside the head's reach; a fail-safe pin can only withhold. use-05's gates lens gets a place.
- The drawer with the dock is `room-12-one-axis-head`'s *tube clears* branch; use-02's plunge does the clearing job my ramp did, so the ramp is not needed if the plunge is out 20 mm before the drawer moves (the nozzle then passes the rim with 19 mm, not 5).
