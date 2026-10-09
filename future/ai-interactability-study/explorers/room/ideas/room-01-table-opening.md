# room-01: table opening, low gantry, shelf under the hole

**Origin:** Derek's example, developed as he described it. **Scene:** `scenes/room-01-table-opening`. **Depth:** worked through several rounds.

## Picture it

A tabletop with a round hole. Under it, in a box hung from the underside, the rotator sits on a shelf that four corner posts guide up and down. The tube stands through the hole with its rim flush with the table top. On the table beside the tube, a short gantry (two short rails, a bridge, a carriage) reaches the printed shell with a post and an arm. The gun's nozzle is about 5 mm above the rim; everything else of the gun is above and behind, over the table. A laser dot sits in the corner against the wall, six millimetres below the rim.

## The proposal

Put the rotator in a pit. The table becomes the datum plane at rim height, the gun structure stands about 40 mm above its rails instead of about 270 mm, the fibre and wire have a flat surface behind the gun, and everything mechanical except the gun is under the table. Axes: shelf Z lifts the tube; the gantry moves the gun in X (radial) and Y (tangent slide). The roll, the hole-axis tilt and the turn in plan are fixed by the saddle the shell sits in. Cameras: one fixed to the room looks down at the dot, one at table height sees the nozzle against the rim.

## What carries the loads, what establishes position, what is free and restrained

- **Carries:** the table and its hung box carry the rotator; rails, bridge, carriage, post and arm carry the shell; the umbilical is carried by the table (it lies on it or leaves through a grommet).
- **Establishes position:** the table plane is the rim plane; the tube's axis is set only by the hole (loose: anywhere within about ±16.5 mm for a Ø160 hole around the Ø127 tube [derived]); the gun's height relative to the seam is the shelf; radial position is the gantry X; angles come from the saddle print.
- **Free / restrained / driven:** driven: gantry X, carriage Y, shelf Z, rotator. Restrained by print: the three rotations. Nothing free by design; the umbilical is the loose element.
- **Escape at the end of a bead** (the workflow lifts the head straight away, trigger held [repo `46-the-per-weld-sequence.html`]): the shelf can drop the tube instead of the gun lifting, if it can do so quickly. Speed unmeasured.

## What software could command, observe, and what stays manual

- **Command:** gantry X, carriage Y, shelf Z, rotator speed and direction.
- **Observe:** the top camera sees the dot when nothing blocks it (the scene tests this); the side camera sees nozzle height over the rim and, from about 14 mm above the rim upward, the plate-wall corner too (wave 3 correction: I had written that it cannot; the scene now has a height slider and reads plate depth from two edges in one frame with the laser off, eyes-16); step counts.
- **Manual or unresolved:** dropping the tube in and seating it, indicating it through the open face of the box, tacking the plate, registering the gantry frame on the table, printing a new saddle when a fixed angle changes. Wire tip, stuck wire, umbilical pull: no sensor proposed.

## What was tried to break it

1. **Conflict:** "a low gantry bridge over the tube" hits the barrel. *Variant:* bridge spanning the hole at countertop height. *Assumption:* the gun stays out of the way of a bridge 20 to 40 mm above the table. *Finding:* at the opening pose (roll 45, hole dial 30, vertical −15, illustrative) the nozzle is 5.0 mm above the rim and the barrel rises at 45°; at 25 mm along, it is already 30 mm above the rim (`calc/opening-pose-geometry.mjs`). *Change:* the bridge sits outside the tube's plan (x about 100) and a post and arm reach the collar lug. *Leaves:* a cantilevered arm of about 95 mm and a post of about 83 mm; stiffness is a picture, not a number.
2. **Conflict:** "the hole shrinks the tube's XY range." *Assumption:* a hole positions the tube. *Finding:* a loose hole leaves ±16.5 mm (`calc/table-opening-numbers.mjs`); a hand-placed clamped rotator is about as good. What the hole reliably shrinks is Z and the height of the support: a bare 2020 post 270 mm tall deflects 13.6 µm/N, 40 mm tall 0.04 µm/N. For 2 N that is 0.03 mm against nothing, and for a 20 N stuck-wire yank 0.27 mm against nothing. *Change:* the pit is a simplifier and a stiffness margin, not a fix for something broken; the collar (below) gives the XY shrink. *Leaves:* real stiffness of the table top and the fitted rails.
3. **Conflict:** the umbilical. *Variant:* cable lying on the table trailing toward a far grommet. *Assumption:* it can simply drop into the table. *Finding:* the exit is 130 mm above the table and points away and slightly up; with 350 mm minimum bend radius while emitting [manual] the route needs about 800 mm of table behind the tube axis, or the badge in the scene turns amber then red. *Change:* deeper table, or hang the fibre from above (room-02). *Leaves:* the cable's bending stiffness and its pull on the gun: unmeasured.
4. **Conflict:** the Y axis. *Assumption:* Y is a position axis. *Finding:* 1 mm along the tangent turns the approach 0.93° in plan and misses the seam radially by 0.008 mm; it is an angle in disguise. *Change:* keep Y small; larger changes are a new saddle print. *Leaves:* there is no driven yaw.
5. **Conflict:** spatter, clippings and scattered light near an open ring around a plastic rotator. *Assumption:* the ring is harmless. *Change (untested):* a metal skirt or collar ring, a metal insert around the hole. *Leaves:* whether stray beam scorches the table 5 mm below the nozzle.
6. **Conflict:** the shelf's upward travel is a collision axis. *Assumption:* Z is a harmless adjustment. *Finding:* the nozzle tip is about 11 mm above the plate face at the opening pose (clearance readout in the scene: 10.0 mm in the initial state, zero at about +11 mm of shelf travel); an upward command beyond that crashes the plate into the copper nozzle. *Change:* a hard stop above nominal set for the print, and a limit switch the software respects. *Leaves:* nothing detects a plate that is deeper or shallower than expected until the dot is looked at.
7. **Conflict:** the notch and the edge are Derek's own neighbours. *Findings:* see `room-01b-edge-notch-slot.md`.
8. **Conflict:** "the side camera cannot see the corner, so only the dot loop reveals plate depth" (my I/O table; eyes, wave 2). *Assumption:* the table-level camera at the default height. *Finding:* in the scene the corner is hidden below rim + 13 mm (blocked by the rim at 10 and 12, by the table below that) and seen from rim + 14; the default camera was at rim + 16, so the sensor that reads plate depth was already drawn. *Change:* the default is raised to rim + 30 mm, a slider moves it, and the I/O table reports the depth as a picture-measured difference of two edges (illustrative noise 0.03 mm); the same test for the nozzle tip needed eps 3. *Leaves:* whether the corner is a clean edge on stainless.

## Branches and combinations

- `room-01b-edge-notch-slot` (edge, notch, slot; inside the scene as the table-form radio).
- Repair: **fitted collar** at the hole (a prior study's idea; here as the input `collar centring` in `room-07-coarse-fine-budget`).
- `room-02-ceiling-carries`: same table, umbilical and weight from above, gun on three feet.
- `room-05-drawer-cell`: same idea with the pit turned into a drawer and a dock.
- `room-09-move-only-shelf`: only the shelf is motorised.

## Unresolved problems, and questions that need Derek's observation

- How loose or fitted the hole should be: it decides whether the gantry covers ±16 mm or ±0.5 mm.
- Tube length and plate seat depth over a dozen tubes (caliper, rim to plate face). ±3 mm is a guess.
- The bench: depth behind the gun, top material, height, and whether a hole can be cut.
- Gun mass, centre of mass, and umbilical pull (spring scale at the grip base with the cable laid out).
- The escape motion: how fast may the shelf drop with the trigger still held?
- The second closure's ports are reached through a Ø90 mm service bore [repo]; the shelf needs a matching opening.

## Assumptions

- Proxy gun, opening pose, 16 mm nozzle clearance: **[unknown]** (kit; from the reference scene).
- Table 30 mm, hole Ø160, shelf ±12 mm, gantry ±15 mm: **[illustrative]**.
- Nest ID clearance 0.20 mm radial, accepted runout 0.25 / 0.30 mm TIR: **[repo]** `weld-rotation-rig.md`.
- Tangent-slide arithmetic, hole clearance, post deflection scaling: **[derived]**.
- Cable minimum bend radius 350 / 240 mm: **[manual]** p. 20.
- Gun mass, umbilical pull, tube seat depth variation: **[unknown]**.

## Sourcing pointers

`sourcing/room.md` entries 10 (MGN12H rail), 11 (12 V linear actuator for coarse Z), 12 (2020 extrusion), 15 (Klipper/Moonraker as the command layer).

## Scene

`scenes/room-01-table-opening`
