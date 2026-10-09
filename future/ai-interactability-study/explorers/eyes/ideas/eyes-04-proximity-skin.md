# eyes-04 Proximity skin

Scene: `scenes/eyes-04-proximity-skin/` (developed). Origin: swarm (eyes framing). Maturity: developed.

**Picture it.** Four small pads, or coils, sit in a ring around the nozzle tip, printed into the shell. There is no camera and no light. Each pad reports how close the nearest metal is: the plate below, the wall beside. From four numbers the software solves two: how far the dot is from the corner, radially and vertically. A map beside the drawing shows where the solve is good (green), poor (orange) or blind (red).

## The proposal

Sense the tube by its metal, not by light. Capacitive pads (FDC1004-class chip: 4 channels, 0.5 fF resolution) or eddy-current coils (LDC1612-class: 28-bit inductance conversion, 2 channels) measure distance to the plate and the wall. Glare on stainless, fume, the rim and the gun's own shadow do not matter. The dot is inferred from a fixed offset between the pads and the beam (calibrated once). Several pads facing different ways, at two distances behind the tip, give a solvable set of equations for the two unknowns.

## What carries loads, what establishes position, what is free or restrained

Nothing new carries the gun. The pads ride on the printed shell; sensor board and two wires join the umbilical. The metal of the plate and wall is the reference. The dot is not observed.

## What software could command, observe, and what stays manual

- **Observe:** four raw readings (fF or ppm), a solved radial and vertical offset from a calibrated model, and whether the gun is inside the sensing envelope. It does not observe the dot, its own model error, nearby conductors, or drift.
- **Command:** nothing here; the solved offset could drive the trim stage of eyes-01.
- **Manual:** calibrating the model against a ground-truth view (eyes-07); mounting the pads; zeroing drift before each pass.

## What was tried to break it

1. **Pads on the barrel, far from the dot.** Assumption: pads anywhere on the shell will do. In the drawing at 60 mm behind the tip the plate and wall are 30 to 50 mm away; capacitive resolution there is worse than half a millimetre (calc/proximity-model.mjs: 0.9 mm at a 30 mm gap with 0.5 fF noise, 60 mm^2 pad). What this changes: the pad distance slider; pads must be near the nozzle tip (0.04 to 0.08 mm at 5 to 8 mm). What it leaves uncertain: that region is hot and exposed to spatter.
2. **Pads all looking the same way.** With a facet angle of 0 (every pad looks along the beam) each pad sees plate and wall together and the solve is ill-conditioned. At about 40 degrees the wall-facing pads read the wall and the plate-facing pads read the plate. What this changes: the shell's shape (facets) is part of the sensor. Uncertain: whether a printed skirt of that shape fits beside the nozzle in the canyon (the nozzle is about 8 mm from the wall and 7 mm above the rim in the reference pose, illustrative).
3. **The ambiguity line.** The eddy-current map shows a dark diagonal where several offsets give the same four readings: a fold in the map. What this changes: the software must not trust the solve across it. It also marks where the sensor is blind even though the readings are large.
4. **A gain error of a few percent on the wall-facing pads.** The solver assumes the calibrated gain; the pads actually read a little high. The solved dot slides by tenths of a millimetre and the map turns red. What this changes: nothing in the sensor; the fix is outside it (eyes-07). Left standing: the sensor cannot see its own model error.
5. **A conductor near the front pad** (wire guide, wire, hand, umbilical clip): adds to that pad's reading; nothing in the four numbers says it is there. Left standing.
6. **Drift.** 50 ppm of inductance equals 0.017 mm at 8 mm with a 5 mm coil and 0.07 mm at 12 mm (calc). Slow: a per-pass zero at a known pose would remove most of it; not drawn.
7. **The perfect-conductor model.** The eddy model assumes a one-turn loop over a perfect conductor. 316L has a skin depth of about 0.19 mm at 5 MHz (calc), thin against the 1.65 mm wall and the 6.35 mm plate, so it behaves as a thick target; but the copper nozzle next to the coil, the shell and the real coil are not modelled. Uncertain.

8. **The scene's gain error (a few percent on the wall-facing pads) has two calibrations, span and zero, and the arrangement has a tool for each** *(from freedom's exchange, section 5)*. Conflict: entry 4 left standing that the sensor cannot see its own model error and that only eyes-07 (off the real tube) can fix it. Assumption behind it: mine, that the model can be calibrated only outside the loop; theirs, that the trim stage and a contact are both in the loop already. **Span** (gain): nudge the trim stage by a known amount (its own encoder or step count is the ruler) and read the pad; the ratio is the gain at the working gap, in situ (borrowed-05's nudge-and-watch, with the pad as the watcher). **Zero** (offset, a nearby conductor, drift): a contact at a known geometry (the wall roller of freedom-07, the stylus of freedom-12 at the instant it triggers) puts the shell at a known radius, so the wall pad's gap is known then. Re-run in `calc/pad-selectivity.mjs` (a copy of the scene's capacitive model, 6 to 8 mm pads, 0.5 fF noise): with no noise the nudge removes all of a 3 to 10 % gain error (0.14 to 0.48 mm of bias); with the chip's noise at the scene's pads the signals are too small, and a 5 % gain error (0.24 mm) is one solve's own noise: it takes a 3 to 6 mm nudge and about 16 repeats to reach a 2.5 to 5 % estimate (rms position error 1.2 to 0.8 mm at that geometry, against 0.55 mm for a single uncalibrated solve's own noise, so the calibration is as noisy as the error it removes unless the pads are closer or bigger). An offset is worse than a gain and a nudge cannot see it: 1.5 fF (three times the chip's noise) on the front wall pad moves the solve 1.06 mm. A zero from free space (the retract lift at the end of every bead, or the approach at the start) is a third source that needs no contact. What it leaves uncertain: the roller (5 to 8 mm beside the nozzle, freedom-07's entry 4) and the pads want the same place, and one has to give; a copper nozzle beside the coil is in neither model; the stage's ruler is as good as its backlash (borrowed-05 measures it from a reversal).
9. **Which pad reads only the wall and which only the plate, and would a contact in place of the wall pair leave a fold?** *(freedom's two questions, section 5)* At the 40° facet with the dot on the corner none reads only one surface: the front wall pad 83 % wall / 17 % plate, the front plate pad 95 % plate / 5 % wall, the rear pads 81 / 19 and 85 / 15 (0° facet: 64 % and 59 %; at 60° they are pure but the pads look so far sideways that the readings shrink). The leak is why a wall-pad gain error moves the vertical answer too; the scene shows the shares under each bar. With the wall pair replaced by a contact, the plate pair alone has no fold but no radial information at all: noise-only 1-sigma of the solved r is 3.6 to 13 mm against 0.2 to 1 mm for z (8 mm pads 17 mm back: median 3.6 and 0.42). A contact gives the wall's position once, at the instant it triggers: it can calibrate the wall pads, not replace them as a signal. What it leaves uncertain: the same fit beside the nozzle.

## Branches and combinations

- Pairs with `eyes-01-gun-borne-eye`: the same two numbers by a second, light-free route (a disagreement between the two says something is wrong with one).
- Pairs with `eyes-03-marker-cube`: tags give the coarse pose, pads the fine one.
- `eyes-11-what-each-eye-sees`: pads are direct-ish for radial and vertical only after calibration (marked inferred there).
- Touch: `eyes-05-touch-off-interlock` is the discrete cousin (contact instead of proximity); `freedom-12-touch-trigger` gives the zero of entry 8.

## Unresolved problems, questions for Derek

Where a pad can physically go beside the nozzle; the copper nozzle's effect; electrical noise from the 2.5 kW laser supply and stepper drivers next to a femtofarad measurement; spatter on the pads; whether the laser's work-contact check is affected by extra conductors on the shell; whether the wall and plate can be told apart when the gun is over the rim edge. **Question for Derek:** is the copper nozzle removable, and what does the work-contact circuit actually connect to at the gun end?

## Assumptions

- Section geometry: plate top at z = 0 for r < 0, wall face at r = 0 up to the rim at 6.35 mm, wall 1.65 mm **[repo]**; beam tilt 32 degrees and 16 mm clearance are illustrative (kit).
- Capacitive: C = eps0 A / (d + 1 mm) x cos^2 facing factor, pad area = size^2 x 0.94; noise 0.5 fF **[TI FDC1004 product page, read 2026-09-28]**. Eddy: single-turn loop by the image method with elliptic integrals; noise assumed 1 ppm of L **illustrative**, not checked against LDC1612 noise plots. LDC1612: 28-bit, 2 channels **[TI product page]**.
- Nearest-point distances to the finite plate and wall with a facing factor: a schematic response, not an electromagnetic simulation.
- Skin depth from a typical austenitic resistivity **[derived]** (textbook value, not measured for this tube).

## Sourcing pointers

`sourcing/eyes.md`: Seeed Grove LDC1612 module ($16.40, in stock, not Prime); ProtoCentral FDC1004 breakout (back-order 7-10 days, price on that page in rupees; not Prime). No Prime listing found for either. Sales volume: none observed.

## Scene

`eyes-04-proximity-skin` (custom 2D stage: section drawing, error map, raw readings with the plate/wall share of each). Wave 3: the default pads are 8 mm at 17 mm behind the dot, the closest the shell allows in the scene. Scene edits: sensor type, pad size, pad distance, beam tilt, facet angle, noise, disturbances, and where the gun is. Nothing is an actuator.
