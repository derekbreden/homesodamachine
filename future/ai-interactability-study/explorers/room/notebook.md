# room — notebook

Framing: **the room is the first stage.** Positioning begins in the space the gun and rotator already occupy: bench, table, opening, wall, ceiling, floor, shelf, frame, rails. The coarse stage may be furniture or building; the fine stage is whatever is left.

Tags used below follow `context/shared-context.md`: **[Derek] [repo] [manual] [derived] [unknown]**, plus **[illustrative]** for a number I chose to make a picture or a comparison. Nothing here is a budget screen.

## Wave 1

### 0. What I found before choosing anything (reading the physical situation as a room)

- The joint is 6.35 mm below the rim and the rim stands 238.4 mm above the bench **[repo]**. So the *joint* is 232 mm up: bench height plus 232. A table top at rim height is not "a table"; it is a datum plane that touches nothing but the nozzle's neighbourhood.
- At the reference scene's opening pose (roll 45, hole dial 30, vertical -15; illustrative) the nozzle tip is **5.0 mm above the rim plane**, the barrel rises at **45° elevation**, and the housing sits **143-185 mm above the rim plane** **[derived, illustrative proxy]** (`calc/opening-pose-geometry.mjs`). The gun body never comes near a flush table top; only the nozzle is within 30 mm of it. So a table that is flush with the rim has to *carry* the gun only through a riser or a lug on the shell, and it cannot *reference* the gun by contact except at the tip.
- The gun body goes toward -X and -Y from the nozzle: **over the bore first**, then over the table. Anything at countertop height that crosses in plan the region "(x 55 to 20, y -9 to -50)" is in the barrel's way once it is more than about 5 mm above the rim plane. A low gantry works only if it is offset from the barrel in plan and reaches the shell with a riser.
- The fibre wants 350 mm radius while emitting and 240 mm stored **[manual]**. A loop of the 5 m fibre is at least 0.7 m across. That is a room-scale constraint before it is an arm-scale one, and it is why ceilings, table undersides and walls come into a study about the gun.
- The rotator needs the tube *standing*; process position is not something to change casually **[repo]** (weld sequence, qualified angle). I do not tilt the work. Tilting the work about a horizontal axis also makes the seam bob by r*sin(tilt) per turn, so it is not a substitute for tilting the gun.

### 1. Arrangements the framing suggests (one line each; silly ones stay)

Ids are the ones used in `ideas/` and `scenes/`.

1. **room-01 Table opening + low gantry** **[Derek's example, as described]**: rotator on a height shelf under a hole, rim flush with the table, low gantry over it, gun in a fitted shell.
2. **room-01b Neighbours of the opening**: tube hangs off the table *edge* on a bracket; a horseshoe *notch* (seat and indicate at a bench, slide the rotator in); a through-*slot* the rotator carriage runs along. (Derek asked why not the edge.)
3. **room-02 Ceiling carries, table locates**: ceiling trolley and spring balancer take a share of the weight, the umbilical hangs from the same track; the gun stands on three ball feet on the table plane; a planar drive moves it sideways. (Started as "ceiling bridge with balancer"; the drawing changed it.)
4. **room-03 Wall port**: the gun on a rod through a ball in an enclosure lid; the wall is the fulcrum, the actuators sit on a long tail outside; distance buys reduction for the actuators and amplifies only the ball's own play.
5. **room-04 Orbit the gun, park the tube**: a spindle on the tube axis and a boom carry the gun once round a stationary tube; the rotator becomes a stand; the fibre must not twist.
6. **room-05 Drawer cell**: the rotator on drawer slides inside a laser-safe cabinet, a kinematic dock, gun and cameras fixed in one frame; a ramp lowers the tube so the wall does not slide under the nozzle.
7. **room-06 Corner cords**: eight taut lines from cage corners (or poles) to lugs on the shell; winches; nothing else carries the gun; software calibrates sloppy anchors by watching the dot.
8. **room-07 Grid table**: dog-hole top, welding table or breadboard as a shared datum for rotator and gun frame; plus a view of the coarse/fine budget of the whole family.
9. **room-08 Observe only**: a fixed frame with cameras on kinematic mounts and fiducials on the shell; the operator still holds the gun; software watches and moves nothing.
10. **room-09 Move only**: a motorised shelf under a hand-guided gun resting on the table; software moves one axis (recipe height) and watches nothing.
11. **room-10 Sit-stand frame**: the two lifting columns as a portal (rejected: too much travel, skew) or as an elevator dock (the drawer turned vertical).
12. **room-11 Pegboard as anchor lattice** for Derek's rings and bungees (the wall as hole grid, the ceiling as long Z); numbers say what it can and cannot do.

Also noted and kept: plumb-hung gun (gravity sets pitch: folded into room-02 and room-11); cable drop through a table grommet (folded into room-01: it needs 0.8 m of table); floor-to-ceiling tension poles as no-drill anchor columns (folded into room-06: the room is too big for a small shell); puck on a carousel (branch of room-05); lazy-susan ring around the tube (branch of room-04).

### 2. Depth

Several rounds of break and repair, with numbers: **room-01**, **room-03**, **room-06**. A scene and a break/repair pass: **room-02**, **room-05**. Sketched in scene or file: **room-04**, **room-07 to room-11**.

### 3. Rounds (what changed my mind)

- **Round 0, geometry.** The nozzle is 5 mm above the rim and inside the bore radius; the barrel rises at 45° toward -X, -Y. A low bridge over the tube hits the barrel. (room-01)
- **What the hole buys.** I expected "the hole shrinks XY". A Ø160 hole leaves ±16.5 mm. It shrinks *height* (the gun structure stands 40 mm above its rails, not 270) and makes a datum plane. A bare 2020 post 270 mm tall bends 13.6 µm/N, so for a 2 N tug the pit is a simplifier, not a stiffness fix. (`calc/table-opening-numbers.mjs`)
- **Umbilical as a room-scale constraint.** The cable leaves the grip 130 mm above the table pointing away and slightly up; at 350 mm radius the route needs about 0.8 m of table. Bezier first gave nonsense (10 mm radii); replaced by an arc-plus-line route at the manual's radius.
- **Tripod.** The first three-foot stance put the centre of mass outside the foot triangle; splayed legs fixed it; then relief share vs stability (foot A: 2.3 N at 30 %, 0.7 N at 50 %, -0.9 N at 70 %). (`calc/stool-feet.mjs`, checked against the scene)
- **Pendulum and bungees.** m·g/L and 2T/L give 0.007 to 0.2 N/mm; 1 N/mm would need 250 to 750 N of pretension. Ceiling as positioner is dead; ceiling as carrier is alive. (`calc/suspension-stiffness.mjs`)
- **Wall port.** I first thought a far pivot amplifies everything. It amplifies only the ball's play (1 + d/Lt); actuator compliance and cable loads are reduced by d/Lt; if the actuators ride on the ball's plate a plate slide is a pure translation. The gun is not a rod: the pivot must sit behind the housing (d ≥ 269 mm). (`calc/wall-port-lever.mjs`)
- **Bore plug.** Drawn first for the orbit idea; the camera inset said "blocked by locate": the plug fills the bore's top where the nozzle goes. Replaced by a steady ring on the OD.
- **Hand pairing of cords.** Lug i to corner i has no positive tension mode. Search over 40320 pairings: 4360 feasible, 43 clear of the shell, at least eight robust over 72 sampled cases. At room scale none exist unless the shell has wings (43, 10, 0 pairings at 0.7, 1.2, 2.4 m; wings ×3 restore 59 at 2.4 m). (`calc/corner-cords-pairing-search.mjs`, `corner-cords-room-scale.mjs`)
- **Calibration.** Fitting 32 numbers to 10 to 40 observed dot positions cuts 2.4 to 8 mm of error to 0.05 to 0.25 mm in simulation; unfitted 1 mm lug errors leave 0.25 mm. (`calc/corner-cords-calibration.mjs`)
- **Grid pitch.** I thought pitch/2 was the residual range. Wrong: a printed adapter carries any offset; the grid registers, it does not give range. (room-07)
- **Roll-up.** A first arithmetic error in the drawer scene (runout counted at TIR instead of half) was caught by writing the script (`calc/drawer-rollup.mjs`).
- **Collision axis.** Adding a nozzle/barrel-to-tube clearance check to every scene showed that the shelf (room-01) and the rod insertion (room-03) can drive the plate into the nozzle within the ranges I first gave.

### 4. Practical sourcing

`sourcing/room.md`: 14 Amazon Prime entries and two other entries, each with how Prime was confirmed and what volume evidence the page shows. The strongest volume evidence is for lazy-susan bearings, drawer slides, wire rope, sit-stand frames and linear actuators; the weakest for OD6+ laser windows, the manual XYZ stage and the GE30C spherical bearing.

### 5. Open threads at the end of wave 1 (kept as written)

- **Measure (Derek):** plate seat depth and tube length over a dozen tubes (rim to plate face); gun mass and centre of mass; the umbilical's pull at the grip base on a spring scale; hole clearance a collar would need; hand placement error of the clamped rotator.
- **Ask the manufacturer (Derek):** is there a rotary path for this fibre? (room-04); real OD rating of any window at the X1 Pro's wavelength (safety, room-05).
- **Not yet drawn:** room-08, room-10, room-11 have no scenes; the third-ring variant of Derek's suspension is only a note.
- **For the exchange waves:** the escape motion at the end of a bead is a requirement everyone's arrangement must meet (mine: drop the tube, ramp, retract, lengthen two lines, lift the boom, fast balancer lift); a fibre rotary path decides room-04; the fine stage for room-05 has only weak-volume sources; room-03's ball needs a measured bearing.
- **Combinations I would try:** room-03's cabinet with room-05's drawer (ball port replaces the fine stage); room-06's self-calibration on room-03's ball plate; room-02's ceiling festoon with room-04's wrap-unwrap.
- **Things I would do next wave:** a scene for the escape motion (which arrangements can lift straight away, how fast); a top view of what each arrangement does to the operator's access for a stuck-wire snip; the wire feeder conduit's path in each scene (only the fibre is routed now).


## Wave 2: exchange with use

Partner: **use** (the day of use). Output: `exchange/room--on--use-w2.md`; new scenes `room-12` to `room-15`; a revision of `room-02`; sourcing entries 17 to 19; calculations `seat-loop.mjs`, `plunge-only.mjs`, `ring-seat.mjs`, `cable-above.mjs`. I opened every use scene (checker with `--exercise`, per-control shots for use-02, use-06, use-03, use-07 and the lenses) and read every idea file. The machine was heavily loaded at the start (eight explorers' Chrome runs, load average above 50): the stock checker's 20 s navigation limit failed every scene, so I ran a copy with a 240 s limit from the scratchpad.

### Borrowed (pieces from other explorers I now use)

- **trials-02-dock-reset**: three load cells under the seats weigh the gun and the way the umbilical pulls. Used in `room-02` as *Weigh-in mode*: the stool is a scale. It answers the unknowns I listed in wave 1 (gun mass, centre of mass, umbilical pull) and it is the way to fill room-13's load-change row.
- **freedom-06-lock-and-release** and **freedom-02**: the friction arm's stiffness as a model (7 to 11 mm per newton at the tip). Used as a row in room-13; it is what a coach loop is up against.
- **use-02-swing-head** (their own): the three-ball seat, the float, the SAMP gun-sample list and the swap volume. Used as the base of room-12; the ring seat's amplification is a port of their coupling matrix.
- **use-06-coach-loop**: the coach line and the rule that the last adjustment follows the last thing that shifts. Used in room-15 and room-13.
- **use-09-programmed-table**: index, lap and bead programs. Used as room-15's rotator.
- **use-04-the-lap**: 0.016 mm/s of slew at 8 mm/s. Used to size the knob (about 11 degrees a second at 0.5 mm per turn).
- **trials-06-mule-gun** (as a note in room-12): test the plunge and seat sequence with a dummy before the real gun goes on the rail.
- **trials-01b-nest-as-puck**: ball-and-dowel seats; the direction the Hertz numbers point (hardened inserts).
- **travel-08-cable-travel** and **borrowed-11-balancer-festoon**: the cable owns its own path. room-12's hook is a fixed mast hook; the ceiling helped only a little (`cable-above.mjs`).
- **use-05-gates** (their own): "a hand fires, software may only veto" as the rule room-14 gives a mechanism.
- **trials-14-contact-sense** and the manual (pp.19, 32): the laser's own conduction circuit; room-14 and the exchange use the manual text, not a proposal.

### Rounds (what changed my mind)

- **The swing is one of three ways to get out of the way.** Writing `plunge-only.mjs` with use-02's own gun samples showed the plunge alone clears their swap volume at 88 mm; the swing was buying a sideways move the axis already provided. Then the fork intruded (a ring at 108 mm behind the nozzle intrudes 12 mm), which moved the seat plane to 138 and made the ring wider (Rc 45: amplification 4.25 against their 5.1).
- **The loop I first called "10 times the seat" was wrong.** The scene draws round bars; only the T-slot case gave 119 micrometres per newton. The first statement in the exchange was corrected to a table (25, 71, 119 and 7 micrometres per newton for round steel, round aluminium, T-slot and box) after a frame-solver check against a hand cantilever (13.6 micrometres per newton at 270 mm for a 2020 bar).
- **A ceiling hook is not a rescue for the fibre.** My first guess was that the fibre's climb at the grip would be used by a hook above the head. In 3D with the same Bezier rule, a rigid eye above helps only at 0.2 to 0.6 m and a swivelling fairlead saves about 200 mm; the cable's bench-depth requirement stays 0.8 to 1.0 m for a moving head. What removes it is moving the other body: whichever body owns the cable stays put.
- **A veto does not need the laser's port.** Looking for where use-05's veto could attach led to the trigger, and to the manual text that emission needs a complete circuit between clip and gun and that loss of conduction stops the beam (pp.19, 32). A mechanical, fail-safe lockout on a lever needs no protocol; the flaws (a stuck lever fires; a solenoid on for a whole weld) are on the page.
- **The open-frame solenoid I found says under 30 s on time.** Energise-to-permit means a coil on for a minute or more; the cabinet-lock solenoid is more plausible. Recorded in sourcing 18 and in room-14.
- **use-06's Monte-Carlo has no term after the loop.** The load change the weld brings comes after the last coach step; room-13 puts one division on the page and the measurement that fills it.

### Ideas born here

- `room-12-one-axis-head`, `room-13-load-change-budget`, `room-14-trigger-path`, `room-15-one-knob-table`; see `index.md`. Named, not drawn: use-03's cartridge record feeding room-09's shelf; use-12's golden tube on the spare station of room-12's carriage.

## Wave 3: answer eyes, and the work in another orientation

Partner: **eyes** (seeing first). Output: `exchange/room--reply-to-eyes-w3.md`; new scenes `room-08-observe-only-frame`, `room-16-which-way-is-down`, `room-17-tipped-tube`, `room-18-cabinet-station`; revised scenes `room-01`, `room-03`, `room-05`, `room-06`, `room-07`, `room-12` (a control that did nothing), `room-02` and `room-04` (text); new calculations `corner-cords-observer.mjs`, `corner-cords-occlusion.mjs`, `rod-under-tilt.mjs`, `orientation-family.mjs`; sourcing entries 20 to 26. The machine was quiet (load below 5) so the stock checker worked; I drove scenes with a small puppeteer script in the scratchpad to read readouts and badges at chosen control values.

### Rounds (what changed my mind)

- **A camera does not report a dot.** eyes was right about room-06. I did not copy their number: I wrote my own fit (`corner-cords-observer.mjs`, Levenberg-Marquardt, six observers) and got the same order of magnitude (spot on the plate 0.39 mm rms, median 0.22; with nozzle height 0.135; 3-D dot 0.114). Two additions of my own: a shell marker cube also fixes the aim (0.03 degrees against 0.12 to 0.17), and the fit fails to converge on a spot that switches between plate and wall (a kink, not a finding about the tube's corner). The first draft of the fit diverged because room-06's pose range includes poses that put the dot in the wall; limiting poses to the nozzle-in-bore fixed it and matches eyes's 12.5 %.
- **The cords do cross the camera.** The sight line from the cage-top camera to the dot is crossed by two cords in 19.5 % of poses as I drew it, 2.6 % from over the shell.
- **The rod.** eyes's 2.4 mm reproduced from a closed form (F d^2 (d + Lt) / 3EI). What I had left as "the rod's stiffness" was thirty times the ball's play.
- **My own scenes were wrong in three places.** room-05's camera B (kit default eps on a point on a thin part's axis), room-01's side camera (raised to 30 mm; the corner is seen from 14), and room-03's layout (the zoom window sat on the rod). Also room-12's stuck-wire toggle and column radio did nothing visible.
- **Tipping the tube does not plumb the reference gun.** I expected the tilt to bring the barrel vertical. The reference gun's barrel is 45 degrees in the section and 32 out of it (the wire arrives along the tangent): tipping about the tangent removes only the first, so 32 degrees from plumb at best and a sixth less weight lever. Taking the wire off the gun (travel-16's radial-plane attitude) makes it exactly plumb at 30 degrees, lever 23 mm. That turned a negative finding into the arrangement (room-17), with the wire's alignment as its price.
- **Tipping does nothing for the cameras.** I expected a horizontal or tilted tube to open the view. The visible cone is fixed in the work's frame (toward the bore, over the far rim); tipping turns it, does not grow it, and a far-side bench camera loses the corner by 9 degrees of tilt. For 0 to 90 degrees toward the station the cone stays wholly above the horizon (43 % of the room's upper hemisphere); away, or past horizontal, it closes.
- **I expected the rim to sweep through the barrel on tipping in and built a sweep check.** It says the opposite: with the hinge on the station side the corner rises to the nozzle from below (8.8 mm at the end, 30 degrees, attitude B), so the tilt is a free parking motion. I rewrote the scene's text and the readout to say what the sweep found.
- **Argon.** The pocket holds a pond up to the lowest rim point (6.35 mm today, 5.5 at 30, none at 90). Separately, a sealed 342 L box at 18 L/min reaches 19.5 % oxygen in 1.3 minutes (well mixed): extraction has to be sized to the argon, not the fume. This is the one finding of the new direction that is about safety; nothing in the scenes is a safety design.
- **Light.** A lamp beside camera A does not light the corner's double bounce: the dihedral returns light to the camera's direction mirrored across the section plane. A diffuse panel that starts below about 60 degrees elevation glares on the plate. Geometry only; the photograph is missing.

### Borrowed (pieces from other explorers I now use)

- **eyes-13, eyes-14, eyes-16, eyes-15, eyes-02, eyes-03, eyes-11, eyes-06b:** the observer choice, the outside observers, picture depth, the forearm, the dome, the marker cube, the IMU, the corner mirror.
- **travel-16-radial-plane:** attitudes B and B2 (no wire on the gun); the plumb gun of room-17 is theirs with a tilt.
- **travel-03-dot-centred:** tilting the work; I chose a bench hinge over dot-centred arcs because the arcs need a 260 mm radius and 430 mm of arc for 60 degrees.
- **room-12, room-02, room-14 (mine):** the one axis as plunge, seat and lift; the cable owned from above; the permit chain.
- **borrowed-14 and freedom-02:** the balancer's mass window for the gun's weight down the barrel axis.

### Ideas born here

`room-16-which-way-is-down` (lens), `room-17-tipped-tube` (deep), `room-18-cabinet-station` (developed), and `room-08` moved from a sketch to a scene. Named, not drawn: a plumb rod through a ceiling ball (room-03 + gravity along the rod: 0.05 mm at 38 x 3 mm); a hinge-side variant; the tilt about a radial line (seam slope); the horizontal tube as a lens limit only.

## Open threads

- **Measure or try (Derek):** a coupon welded by hand on an incline (plate tipped 30 degrees, seam level) and one on a floor: does the melt care? (rooms 16, 17); a phone photograph across the bore, 10 to 15 degrees above the rim, of a real tube (the corner edge: rooms 01, 05, 09); a photograph of the dot on the plate at 30 cm (room 06); the stainless corner under a phone flashlight (room 18); with the trigger held, is the red dot on (rooms 03, 08); gun mass and centre of mass (kitchen scale or room-02's three cells), the umbilical's pull at the grip base with the wire jogged, the gas on and off, a trigger pressed; plate seat depth over a dozen tubes; which side he stands and which hand holds the gun.
- **Ask the machine (Derek):** at standoff with the wire not touching, does the trigger emit or does the laser show the unconducted alarm (manual p.32); what part of the gun closes the conduction circuit; is the real gun's wire bracket unusable or usable in attitude B?
- **Wave 4 (combine, with a new partner):** room-17's wire guide is the largest open problem: how rigid, how it follows 0.25 mm of runout, whether a height trim is enough (a partner who knows guides or trials); the printed race at 30 degrees (freedom for the force path, datum for the runout it adds); room-17 in room-18's cabinet (one box); room-03's rod plumb through a ceiling ball; room-16 with a second axis (the seam's slope) and a coupon result typed in.
- **Not yet drawn:** room-10, room-11 have no scenes; room-04's stripe test; a hinge-side variant of room-17; the third-ring variant of Derek's suspension is still a note.
- **Combinations I would try next:** room-08's frame with room-18's lamps (the frame carries them); room-15's one-knob table on room-17's tipped plate (the knob is then across the trough); room-14's pendant with room-18's fan permit; room-13 with real measurements typed in.
- **Kit notes:** the kit's `ghost`, `sensor` and `laser` roles never occlude, so a person or a lamp drawn in those roles is invisible to `markVisibility` (room-08 draws the forearm as `compliant`); a `//` comment on the same line as `app.add(...)` swallows it (bit me once); `Object3D` visuals for controls must be objects, not the inset API; the checker's phone-width warning is triggered by any chip of about 50 characters or more (all `transferable` chips are now under 40).
