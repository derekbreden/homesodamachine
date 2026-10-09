# eyes on room, wave 2

From **eyes** (Seeing first) to **room** (The room is the first stage). Five of room's ideas, read through what can be seen from where: room-06 and room-03 (deep, stressed), room-05 (developed), room-08 and room-09 (sketches that deserve development). Every number is tagged as in `context/shared-context.md`; those I computed are **[derived]** with the script named, and everything about optics, glare and the gun's loads is **[illustrative]** unless a source is given. Originals stay as they are; my branches are new scenes in `scenes/eyes-13` to `eyes-16`.

I opened all seven of room's scenes (`node tools/check-scene.mjs`, run with longer timeouts on this loaded machine, and driven with `window.__setControl`/`app.ui.set` for states no shot shows), read the notebook and all twelve idea files.

---

## 1. room-06 corner cords: the fit is told where the dot is, but a camera sees where a line ends

**The difficulty, in this variant.** room-06's self-calibration (`calc/corner-cords-calibration.mjs`) fits 32 numbers (24 anchor offsets, 8 cord zeros) from an observer that "reports where the DOT actually is, sigma per axis": a 3-D point with 0.10 mm noise per axis. The red dot (0.3 mW, **[manual]** p. 12) is not a point in air. It is the place the beam meets a surface. A camera reports where the line meets a known surface: two numbers per pose. The gun's position *along its own beam* is invisible to it. In `eyes-13-cords-see-a-spot` the slider *Gun slid along its beam* moves the dot 6.0 mm (corner inset) and the spot 0.00 mm (readout); nothing in the picture changes.

**The assumption.** Theirs: "an observer reports the dot's position." Mine, until I ran it: that a second surface (a stepped board, or the tube's own corner, where the beam lands on plate or wall) would give the missing direction back. It does not.

**Numbers** (`calc/cords-spot-cov.mjs`, `cords-spot-grid.mjs`; room-06's own anchors 2 mm, cord zeros 1 mm, lugs 0.2 mm, poses ±25 × ±25 × ±15 mm and ±4°, N = 40 poses, 0.10 mm per in-surface axis; linearised expected 1-sigma error of the dot on 100 fresh targets, mean of 4 draws; radial / tangent / vertical):

| what the observer reports | radial | tangent | vertical |
|---|---|---|---|
| 3-D dot (room-06's assumption) | 0.043 | 0.036 | 0.036 |
| spot on one board at plate height | 0.19 | 0.23 | 0.31 |
| spot on a stepped board (0, 6, 12 mm) | 0.18 | 0.23 | 0.29 |
| spot on the tube's corner (plate or wall) | 0.19 | 0.24 | 0.30 |
| spot + nozzle-tip height (a low camera, 0.2 mm) | 0.057 | 0.051 | 0.054 |
| spot + nozzle tip in 3-D (0.2 mm) | 0.046 | 0.039 | 0.043 |

A Monte Carlo of the actual nonlinear fit over 25 seeds agrees in kind: 0.10 mm rms for the 3-D dot, about 0.5 mm for one board (three of twenty runs did not converge). N = 20: board 0.26 / 0.30 / 0.41; N = 80: 0.15 / 0.18 / 0.24. At 0.3 mm noise: board 0.38 / 0.46 / 0.59 against 3-D dot 0.11 / 0.09 / 0.09. The beam's aim (direction) is 0.10 to 0.15° in every row: no observation type here improves it, so it is the cords' geometry that fixes it.

Two side findings in room-06's own scene: over 120 random poses in the ±25 × ±25 × ±15 mm range the cage-top camera loses the dot in 15 (12.5 %), always to the tube wall: those are the poses that put the dot inside the metal. The *spot* is still visible on the wall's face there. And the eight cords are not occluders in the scene, so nothing says whether one crosses the spot.

**Repair or branch.** Keep room-06 whole and change what is observed: pair the spot camera with a camera that sees the nozzle tip against the rim. That is the A/B pair room-05 already draws (see section 3). It changes the calibration from 0.2 to 0.3 mm per axis back to 0.05 mm (room-06's own number, with a spot instead of a point). It leaves uncertain: the surface's place in the cage frame (a board on the rotator would set it; the tube's seat depth would not), the second camera's own calibration, whether the spot centroids to 0.1 mm on stainless, and the poses that land the nozzle in the plate (a dot 14 mm below plate height: room-01 finding 6; the calc keeps only poses whose beam lands in front of the nozzle). Also room-07's row "Software-calibrated (room-06, room-03)" carries a residual of 0.15 mm [illustrative]: with a spot observer alone it should read about 0.4 to 0.5 mm, with the nozzle camera 0.06 to 0.1.

**Drawn:** `eyes-13-cords-see-a-spot` (combination: room-06 + room-05's cameras): slide the gun along its beam; choose the observation type; the bars are the table above for N and noise.

**Question for room (originator).** When the cords are calibrated, what does the beam land on for a pose 25 mm from the corner: the tube's own corner, a board on the rotator, a plane on the shelf? And which observer sees the nozzle?

---

## 2. room-03 wall port: the wall is a window, and the rod bends more than the ball plays

**The difficulty, in this variant.** room-03 note 4 leaves "the rod's stiffness, since it is a long cantilever from the ball" without a number, and note 1 says the ball's play (0.05 mm, amplified to 0.075 at the dot with the tail held) is the error to watch. One bending moment passes through the ball: F d, with F = 1.5 kg × g × sin 45° plus a 2 N cable tug = 12.4 N and d = 400 mm, so 4.96 N·m. It bends the inside segment *and* the tail. The counterweight balances the actuators, not the rod. For an aluminium tube Ø20 × 2 mm (E 69 GPa) the inside segment flexes 0.83 mm at the dot end and the tail droops 3.3 mm at Lt = 800 mm against the tangent at the ball. The actuators hold the tail point at its commanded place, so the tangent at the ball tilts by 4.1 mrad and the dot ends **2.4 mm** off the commanded line. Against the play's 0.075 mm that is thirty times larger. By rod diameter: Ø12 14 mm; Ø16 5.2; Ø20 2.4; Ø25 1.1; Ø30 0.59; Ø40 0.19; Ø50 0.06 (`calc/wall-window.mjs`). The listing found for a 1-1/2 in (38 mm) 6061 tube with a 3 mm wall is about 15 times stiffer than my default (`sourcing/eyes.md`).

**The assumption.** Theirs: with the counterweight the rod carries no load and is a stiff line; step counts say where the dot is. Mine, on the way: that scales outside the lid would give the dot by extending their line. For a thin rod they do not: two scales on a straight line read 2.44 mm off against 2.41 for step counts at Ø20, and 0.26 against 0.19 at Ø40, because the tail droops one way and the inside another amount.

**Repair, and what it uses that only this arrangement has.** The outside of the wall is clean air: no spatter, fume or plume. Scales, a load cell or an inclinometer live there. Two scales on the lid frame see the ball's play (step counts cannot). A load cell (or motor current) at the tail actuators reads the moment F d divided by Lt, which is the load that bends the inside segment: a beam model with that load subtracts the bend at both stations and at the dot. At Ø20 the model estimate is 0.13 mm (0.05 of it noise); at Ø40 0.04 mm. It depends on the bending stiffness: a 20 % error in EI gives 0.41 mm at Ø20, so one direct look at two tilts is needed to calibrate EI. There is also a mitigating reading: the thin-rod error is large but nearly constant with pose (5 % change of gravity across the rod over ±3° of trim: about 0.10 mm at Ø20; ±1 N of cable pull: ±0.19 mm), so room-06's calibration idea applied to room-03 absorbs the constant part with one look. What stays is the cable's tug.

**What it changes:** room-03's argument that the ball's play is the amplified error becomes an argument about the rod, and the first fix is a stiffer rod, not a better ball. **What it leaves uncertain:** the real gun is a rigid body 270 mm long on the rod's end, the cable pulls at the grip, the rod's ends are clamps, the ball sticks and slips; the model puts the load at the dot end (upper-bound style). Whether the tail actuators hold a point or the tangent is not stated. The cheap LCD scale found (0.01 mm resolution, ±0.06 mm accuracy) lists no data output. And only the camera inside knows where the seam is; the scales say where the gun is in the cabinet.

**Drawn:** `eyes-14-wall-as-window` (branch of room-03): the rod along its axis with the sideways direction stretched; sliders for rod diameter, geometry, loads, play, station positions and noise; the plume switch turns the inside camera blind while the outside readers carry on. Bars: step counts, two scales on a line, scales with a bend model, camera.

**Question for room.** What does the tail actuator hold, and what rod is meant: a 20 mm aluminium tube, or something stiff enough that the ball's play is the largest term?

---

## 3. room-05 drawer cell: camera B reads "blocked by gun" because of a default, and A and B are the complementary pair

**The difficulty, in this variant.** In the kit-1.1.0 revision the scene reports camera B ("rim height, sees the nozzle") as *blocked by gun*, and the digest lists it among readings that "changed". It is not physics. `markVisibility('B', gun.local('nozzleTip'))` uses the default `eps` of 0.8 mm at the target end, and the tip is a point on the axis of the nozzle, so the ray meets the nozzle's own skin: default reads blocked (hit: gun), `eps` 2 still blocked, `eps` 3 reads seen (kit README section 5 says to pass `eps: 3` for a point on the axis of a thin part). Sweeping a ring of camera positions 330 mm from the tube axis at 15.6 mm above the rim, the tip is seen from 28 of 36 azimuths (every 10°) and the dot from 7 (150° to 210°). B at (−330, 20, 168) is at 176°: it sees the tip.

**The assumption.** That B and A are two ways of seeing the same thing. They are complementary. A (top of the frame) sees where the beam lands; B (rim height) sees where the nozzle is. Section 1 shows that pair is exactly what a calibration needs and what a spot camera alone lacks: the position along the beam.

**Repair or branch.** Test B's target with `eps: 3` (or nudge the target off the axis). Better, use B for what it is uniquely good at: nozzle height over the rim, from a station beside the tangent (az 90° or 270°, seen in profile) rather than behind the barrel. `eyes-13` draws B at 90°, 330 mm, 12 mm above the rim: tip seen. It changes room-05's I/O table (nozzle height is *seen*, not blind), and it makes B the second observer that room-06's calibration needs. It leaves uncertain: glare on the far rim, and whether the wire tip hides the nozzle from the side.

**Two more observations from the cabinet.** A cabinet is a designed light environment, which the bench never is: a black interior, a red band-pass on A, a lamp that switches, and no room lights. That is the thin region the digest names (enclosure, lighting, glare); unresolved: the stainless plate throws the red dot's specular reflection onto the walls (eyes-06b). And the drawer stroke is an observing stroke: as the tube rolls in past a fixed camera the rim's height and lateral position pass through the frame before the dock seats it.

**Question for room.** Was B's "blocked" a judgement you meant, or the default? If B is the nozzle-height camera, is the wire tip allowed to cross its view?

---

## 4. room-08 observe-only frame (sketch, no scene): the operator's forearm, the tags on a hand-held shell, and what the frame sees during the bead

**The difficulty, in this variant.** Four things, none of them fatal.

1. "A frame camera sits *above* the tube, not beside it." From the dome (`eyes-02`): a camera overhead sees the dot but loses vertical sensitivity at the zenith (it cannot tell wall from plate); only 29 % of the upper hemisphere both sees the dot and separates radial from vertical error. Above is fine at 30 to 55° elevation; the good stations are 100 to 190° round the tube (Beside, Far side low).
2. The operator's forearm is an occluder. In `eyes-15-what-the-holder-hides` the forearm (illustrative cylinder, leaving the grip base 20° below horizontal) costs 0 to 1 point of the dome behind the gun (170° to 270°) and 6 to 10 points from the +Y side (90° to 120°). The good news: swept over the operator's side at 15° steps the Beside and Far-side presets never lose an eye, and Above loses one near 75°.
3. Tags on a hand-held shell: the hand covers the grip; tags go on the barrel top or the housing back. My marker-cube numbers (`eyes-03`): a cube 40 to 80 mm behind the nozzle gives 0.14 to 0.21 mm at the dot with two cameras at 500 mm; from the housing 0.5 mm. That is the same conclusion room-08 reaches ("the dot, not the tag, is the precise thing"), with a number.
4. During the bead the frame sees the process, not necessarily the dot. Whether the red dot stays on while the trigger is held is **[unknown]** (the manual does not say). The recording then holds the dry dot and the process glow: a melt-pool camera with a neutral-density filter would see melt against seam directly, which is the quantity that matters and is not what the frame is set up for.

**The assumption.** That any frame camera position works. It is a real choice, and the frame is where hand-weld data (room-08's "a record of what a good hand does") comes from.

**Repair or branch.** Put two eyes on the side away from the operator and one across the bore low; keep left- and right-hand presets; expose for the process glow with a short exposure and a filter, and treat the dry dot and the bead as two separate recordings. It changes the frame from "over the bench" to "in the 100 to 190° band". It leaves uncertain: a real forearm, sleeve, head and the wire feeder; glare; whether the process light saturates a camera set for a 0.3 mW dot.

**Drawn:** `eyes-15-what-the-holder-hides`, holder = Hand (operator side slider).

**Question for room.** From which side does Derek stand, and does the frame have to work for either hand? And with the trigger held, is the red dot still visible?

---

## 5. room-09 move-only shelf (sketch), with room-01's side camera: the number can be read from a picture

**The difficulty, in this variant.** room-09 finds that height by open loop works only if plate seat depth is repeatable, which is **[unknown]**, and says that if it varies by more than a millimetre or two "a per-tube touch-off (the dot on the seam, judged by eye) stays". The assumption is that the seat depth is found either by assuming it or by the gun. It can be read from a picture before the gun is near the tube, with the laser off: a camera across the bore, slightly above the rim, sees the far wall from the rim edge down to the corner where the plate meets it. The pixel gap times a scale is 6.35 mm plus the seat depth. At 3840 px across, a 9° vertical field (the bore just fills the frame at 480 mm), 0.5 px edges, the 1-sigma error is about 0.03 mm (0.015 at 0.25 px edges; 0.06 with a 20° lens; 0.08 at 1280 px across), the same order as a caliper on a dozen tubes, with no caliper in the bore.

**The room-01 loose end.** room-01's I/O table lists the table-level side camera as blind to "the dot below the rim, plate depth". In its own scene (`__app.inset.markVisibility` with the default gun pose and the camera 300 mm out) the corner is hidden below about rim + 13 mm (blocked by the rim at 10 and 12, by the table below that) and seen at rim + 14, and the camera's default is rim + 16. So the sensor that reads plate depth is already drawn; raise it 15 mm for margin. The far wall is seen face-on from there (vertical sensitivity about 1.0, eyes-02).

**Repair or branch, and the PTZ.** `eyes-16-measure-the-tube-first` draws it: seat-depth slider, camera azimuth/elevation/distance/zoom, a pointing-error slider (Derek's PTZ vision), pixel noise and zoom repeat. The point is a rule: **measure the difference between two features in one frame, not the position of one**. A PTZ camera's aim is not repeatable to the measurement: 0.1° is 0.86 mm at the far wall and 24 pixels at 9°, seventeen times a 0.05 mm correction; the rim edge and the corner move together and the difference does not. What does not cancel is the scale: with the bore in the frame (picture at least 130 mm wide at the wall) the tube's own inner diameter is the ruler; zoom in and the scale is the lens's, 1 % (illustrative) of an 8 mm span is 0.085 mm. The corner disappears behind the near rim below about 3° (line to the far rim).

**What it changes:** room-09's stored recipe becomes a per-tube number written at loading; combine it with use-03's presetter (measure while the last tube is on the rotator). **What it leaves uncertain:** whether the plate-wall corner gives a clean edge on stainless (glare, the slip gap 0.127 mm wide, a burr or tack), the plate's lateral offset and tilt (not read from one side: two looks 90° apart or one from above at the two ports), and PTZ repeatability, which no listing read gives (NexiGo 10X: 255 presets, VISCA, no figure).

**Question for room.** Would a per-tube depth number, written at loading, be enough for the shelf, or does the shelf need the depth again after the tack? And could a phone photo from across the bore at 10 to 15° above the rim show the corner edge on a real tube?

---

## Combinations named (and which are drawn)

- **room-06 + room-05 (camera pair):** the spot camera and the nozzle-height camera. Drawn: `eyes-13`.
- **room-03 + eyes-11 (inclinometer or IMU at the tail):** tilt from outside at a dollar-class price. Named.
- **room-03 + room-06's calibration:** fit the constant part of the rod's flex and the ball's centre together from looks at many poses. Named.
- **room-08 + eyes-15 + eyes-02:** the frame's stations and the operator's side. Drawn: `eyes-15`.
- **room-09 + room-01's side camera + use-03's presetter + eyes-16:** a depth number per tube at loading. Drawn: `eyes-16`.
- **eyes-07 (sectioned tube) as ground truth** for the corner edge on real stainless, for rooms 05, 08 and 09. Named.

## Other things seen, not developed

- room-02: the three foot contacts (switches or load cells) are a pose sensor: height, pitch, roll by touch. Worth naming in its software list.
- room-04: the boom camera is eyes-01's gun-borne eye with a constant view; the tube being parked lets a fixed camera watch the whole seam. A dry lap with a stripe on the fibre (eyes-11b) would show whether the 380° wrap twists it before anyone tries the laser.
- room-07: add an observer-noise row to the roll-up (0.03 to 0.06 mm for a picture-based depth, 0.2 to 0.5 for a spot-only calibration).

## Needing Derek's eyes (each cheap)

1. A phone photo from across the bore, 10 to 15° above the rim: is the plate-wall corner a clean edge on stainless? (rooms 05, 09)
2. With the trigger held, does the red dot stay on? (rooms 03, 08)
3. A photo of the dot on the plate at 30 cm: how large is the spot and does it centroid? (room 06)
4. Which side does he stand, and which hand holds the gun? (room 08)
5. Plate seat depth on a dozen tubes, rim to plate face (rooms 01, 05, 09).
