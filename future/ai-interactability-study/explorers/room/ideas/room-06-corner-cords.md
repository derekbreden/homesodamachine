# room-06: corner cords

**Origin:** swarm (room framing applied to Derek's suspension: the anchors are the room's corners). **Scene:** `scenes/room-06-corner-cords`. **Depth:** worked through several rounds, each with a script.

## Picture it

Four poles at the corners of a cage about a metre across, each with two small winches near its top and near its bottom. Eight thin taut lines run from the eight eyelets to eight lugs on the printed shell. The gun hangs in the middle of the web, over the tube, held by nothing else. To move it, eight winches change eight lengths; to point it, the same. The umbilical is the only other thing that touches it.

## The proposal

Let the anchors be the room's corners and the lengths be the whole control. Derek's rings and bungees are *soft* lateral supports; taut fixed-length lines are not: their stiffness comes from the material's stretch (EA/L) instead of from gravity or pretension acting over a length. With eight lines the pose has all six degrees of freedom and a margin of two. Software commands a pose; inverse kinematics makes the lengths. The anchors are placed to a few millimetres with a tape measure and then **calibrated by software watching the dot**.

## What carries, what establishes position, what is free

- **Carries:** lines in tension carry everything (thickness in the scene follows tension); the cage carries the lines.
- **Establishes position:** the winches' lengths plus the anchor geometry. The anchors are only as good as the calibration.
- **Free:** nothing; if a line goes slack the pose is no longer held (the scene turns all lines red).
- **Driven:** eight winches. **Restrained:** by the lines' tension.
- **Escape at the end of a bead:** lengthen the two top lines: a straight lift by command.

## What software could command, observe, and what stays manual

- **Command:** eight winch lengths from a commanded pose; the rotator.
- **Observe:** cameras (wave 3: a camera reports where the beam meets a surface, **two numbers per pose**, not a 3-D point; a second number that depends on the gun's place along its beam comes from a nozzle-height camera or a marker cube on the shell); winch step counts; motor current as a rough proxy for tension. The anchor and length errors are *not* observable directly; they are recovered by watching over many poses.
- **Manual:** standing the cage, fitting winches, tying the eight lines in the recorded order, loading the tube, the first anchor guesses.

## What was tried to break it

1. **"It will sway."** *Variant:* rings and bungees (Derek's) at room scale. *Finding:* a pendulum is m·g/L (0.015 N/mm at 1 m); a perpendicular bungee pair is 2T/L (0.007 to 0.2 N/mm for 5 to 50 N); 1 N/mm needs 250 to 750 N of pretension. Taut fixed lines are different: 1 mm Dyneema-type braid (EA about 60 kN, an assumption) is about 100 N/mm per line at 0.6 m, and the eight together give 194 to 380 N/mm in every direction at the opening pose. A 2 N umbilical pull moves the dot 10 µm (32 µm including the shell turning). *Leaves:* creep, drum winding, guides, sag (0.02 to 0.44 mm depending on line and tension): none in the tension model.
2. **My first pairing of lugs to corners could not hold the gun at all.** *Variant:* lug i to anchor i, in order. *Assumption:* any reasonable pairing works. *Finding:* no non-negative solution exists even for gravity alone: every cord turned the gun the same way about x (all eight moments about x had the same sign). *Change:* search all 8! pairings, requiring feasibility and that cords stay out of the shell (`calc/corner-cords-pairing-search.mjs`): 4360 hold the gun, 43 of them also clear the shell, and eight of those held all 72 sampled poses and six umbilical directions with tensions in [5, 150] N. *Leaves:* re-tying the lines must copy the pairing.
3. **The room is too big for a small shell.** *Variant:* the same lug layout in a 2.4 m cage. *Finding:* feasible pairings: 43 at 0.7 m, 10 at 1.2 m, 0 at 2.4 m. *Change:* lug outriggers scaled 3 times about the centre of mass restore 59 pairings at 2.4 m, 4 times 161; stiffness at 2.4 m is 56 N/mm (`calc/corner-cords-room-scale.mjs`). *Leaves:* outriggers sweep the working volume; jammed telescoping poles would need to take the lines' sideways pull. This is a warning about *room-corner* anchors: the room's corners are the wrong distance unless the shell has wings.
4. **Sloppy anchors** (first version: the observer reports the dot's 3-D position; see item 8 for what a camera reports). *Variant:* anchors at 2 mm (1 sigma) and winch zeros at 1 mm. *Finding:* the dot lands 2.4 to 8 mm from where it was commanded. Fitting 24 anchor offsets and 8 length offsets to observed dot positions (observer noise 0.10 mm per axis, 10 to 40 poses) gave 0.05 to 0.25 mm rms over 200 fresh targets (`calc/corner-cords-calibration.mjs`, seeds 1 to 5); 5 mm anchors with 0.3 mm noise gave 0.16 mm; 1 mm errors in the lug positions, unfitted, leave 0.25 mm rms (0.66 max). The scene runs the same fit in the page: press *Self-calibrate*. *Leaves:* pulleys instead of fixed eyelets move each line's effective end by radius times angle (0.3 mm for an 8 mm pulley over 2°); the fit does not model it. This is a transferable mechanism: any arrangement with sloppy geometry can be calibrated by driving to many poses and watching the dot.
5. **The lines cross the working space** past the umbilical, the wire conduit and the plume. Dyneema melts. *Change (untested):* stainless wire near the nozzle, every lug on the far side of the housing. *Leaves:* how a hand reaches the nozzle to snip a stuck wire.
6. **Orientation range.** ±25 × ±25 × ±15 mm and ±4° about the dot held with every line between 5 and 97 N over 400 sampled poses. Larger turns were not tried; a different coarse angle is a different shell.
7. **Winch sizing.** Up to 100 N at a 10 mm drum radius is 1 N·m per winch: a geared NEMA 17 or a NEMA 23. Not designed.

8. **"A camera reports where a line ends" (eyes, wave 2 exchange: `eyes-13-cords-see-a-spot`).** *Variant:* the fit of item 4 with the observer made honest. *Assumption (mine, in the first version):* the observer reports the dot's position in 3-D at 0.10 mm per axis. *Finding:* the red dot is where the beam meets a surface. Sliding the gun along its beam leaves the spot unchanged, so a spot alone loses one direction per pose. I re-ran the fit (`calc/corner-cords-observer.mjs`, my own nonlinear fit, 8 seeds, 40 poses, anchors 2 mm, zeros 1 mm, dot error over 100 fresh poses with the nozzle tip inside the bore): 3-D dot 0.114 mm rms (radial 0.096, tangent 0.038, vertical 0.044); **spot on the plate 0.39 mm (median 0.22; one of eight runs did not converge)**; spot plus the nozzle tip's height (0.2 mm) 0.135; spot plus the nozzle in 3-D 0.101; a marker cube on the shell (dot in 3-D at 0.2 mm, aim at 0.05 degrees) 0.107 and the beam's aim 0.03 degrees against 0.12 to 0.17 for every spot row. That agrees with eyes's linearised table (0.19 / 0.23 / 0.31 for one board, 0.06 with the nozzle camera). A spot on plate or wall together (the tube's own corner) did not converge with my fit (7 of 8 runs) because the surface changes where the beam crosses the corner; I do not claim it is worse than a board. The in-page fit of the scene gives 0.10 / 0.35 / 0.09 / 0.11 mm for one seed. *Change:* the scene's *Self-calibrate* takes an observer (radio); the default is the honest one (spot plus nozzle height); the 3-D dot stays selectable as "what the first version assumed". `room-07` carries the row with the observer's cost. *Leaves:* the second camera's own calibration, whether the spot centroids to 0.1 mm on stainless, and the surface's place in the cage frame.
9. **The cage-top camera is crossed by the cords (eyes, wave 2: "the eight cords are not occluders").** *Finding:* I tested the sight line from the camera to the dot against the eight true cord segments (`calc/corner-cords-occlusion.mjs`, 600 random poses in range, 313 with the nozzle in the bore, a cord blocks within 1.15 mm): the camera as first drawn, (20, -40, 700), is crossed by cords 2 and 6 in 61 of 313 poses (19.5 %); over the shell, (-60, -20, 700), in 8 (2.6 %); off to the +Y side, (20, 300, 600), in none. *Change:* the scene offers the three places and a badge when a cord crosses the line; the drawn cords stay non-occluding (they are 1 mm thin, the drawn rods are thicker) and the test uses the true segments. Eyes's other finding, that 12.5 % of poses put the dot inside the wall, is the reason calibration poses are limited to those whose nozzle tip is in the bore. *Leaves:* where the second camera (nozzle height) stands.

## Branches and combinations

- **Wide-winged shell:** required for room-scale anchors (finding 3).
- **Combination with `room-02-ceiling-carries`:** two lines from the ceiling track replace the balancer line.
- The self-calibration step transfers to `room-03-wall-port` (calibrate the ball position and plate slide directions, and the constant part of the rod's flex: eyes-14) and any arm.
- **Combination `eyes-13-cords-see-a-spot`** (room-06 + room-05's camera pair): adopted; the scene's observer radio is its content, and the pair (spot camera A, nozzle-height camera B) is the two-camera calibration.

## Unresolved, questions for Derek

- Would Derek accept eight thin lines through the working space?
- The lines' real stiffness (EA) and creep; the lug positions from a scan of the shell.
- **Needs Derek's eyes:** a photo of the red dot on the plate at 30 cm, and how large the spot is: does it centroid to 0.1 mm on stainless?
- Weigh the gun; measure the umbilical pull.

## Assumptions

Gun mass 1.47 kg, CoM local (0, −23, 181), lug layout, cage geometry, EA values, sigmas, observer noise: **[illustrative]**. Cord model: massless straight segments; small sag ignored in the tension solve. Gun mass, umbilical pull, real line properties: **[unknown]**. Tube seat depth is irrelevant to the cords but still needs the shelf.

## Sourcing pointers

`sourcing/room.md` entries 6 (UHMWPE 1 mm cord), 7 (304 stainless 1 mm wire rope), 8 (telescoping support poles, 49 to 114 in), 12 (2020 extrusion).

## Scene

`scenes/room-06-corner-cords`
