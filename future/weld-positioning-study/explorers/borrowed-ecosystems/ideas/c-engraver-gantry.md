# C — Engraver gantry: a diode-laser engraver's XY frame carries the gun

## Picture it

**The gantry.** A diode-laser engraver's open XY frame — 400 × 400 mm, belts,
NEMA 17s, a GRBL-class controller — with its laser module removed, stands on
four ~500 mm 2040 legs around the rotator.

**The gun.** A ball-screw Z module hangs from the X carriage and holds the shell
by its housing top. The angles live in a printed cassette, or in small roll
stages under the Z. A USB camera on the frame watches the dot. The umbilical
passes under the rear rail to a saddle on a rear leg.

**How it moves.** G-code moves the gun. With one-knob-one-parameter's C-G2
branch, the vertical angle is a G2/G3 arc about the fitted tube axis, radial is
a G1, height is Z. "Fixed" is the bench, through the legs; a common plate is
recommended.

**Branches.** C-T is **Derek's table-hole example**: the frame flat on the
tabletop over a hole, the rotator on a shelf below. The legged version is my own
step beyond it.

**Sketches.**
- `../sketches/c-engraver-gantry.svg` (true pose).
- C-G2: `../../one-knob-one-parameter/sketches/c-g2-vertical-angle.svg`.

**Major unresolved problems.**
- Carriage stiffness and creep with 2–3 kg hanging on POM wheels.
- A back-driving Z ball screw.
- Angle axes do not pass through the dot unless a roll stage is built about it.
- A stuck wire can cost the gantry steps.

Sketch: `../sketches/c-engraver-gantry.svg` (elevation from outside the dot +
plan). Developed to a medium depth. Belt numbers from `../calcs.py` §5.

## The physical idea

Open-frame diode-laser engravers are mass-produced machines whose entire job is
to carry a laser head and put its spot at commanded X/Y over a work surface.
They arrive with belts, steppers, an ESP32/GRBL-class controller, homing,
G-code, a large hobby software ecosystem (LightBurn-class, with camera
alignment features), and — because users engrave tall objects — riser kits to
lift the frame. Remove the laser module and the frame is a 400 × 400 mm
motorised XY gantry that already expects to live over something.

Arrangement:

- The frame (LONGER Ray5 class, 400 × 400 mm work area, ~660 mm outside) stands
  on four 2040 legs (~500 mm) at its corners, outside the rotator's 300 × 250 mm
  base. The X beam then passes ~70 mm above the top of the gun (~430 mm above the
  bench at the opening pose), so legs of ~500 mm.
- A motorised Z module (100 mm SFU1605 ball-screw stage with NEMA 17) hangs from
  the X carriage and holds the scan-fitted shell by its top.
- The gun's angles live in the printed shell (a fixed "angle cassette" per
  recipe), or in two small roll stages between the Z module and the shell.
- A USB camera (Derek's ELP 16 MP) on the frame looks at the dot; a second one
  from another side if needed.
- The umbilical leaves the butt heading −Y at ~30° with its apex ~450 mm above
  the bench, so it passes under the rear rail; its saddle clamps to a rear leg
  (stationary), and the slack span to the carriage changes shape only by the
  carriage's small search moves.

Derek's table-hole example is the same frame flat on the tabletop over a hole,
with the rotator hung on a shelf below so the rim sits near countertop height
(branch C-T below).

## What carries, locates and drives

- Carries: carriage wheels and X beam (weight); belts carry no weight
  (gravity is vertical, belts are horizontal).
- Locates: belts + stepper holding torque in X/Y; the ball screw in Z.
- Fixed to: the bench, through the legs. The tube is located separately by the
  nest; runout is not followed mechanically, but a camera loop can see it.
- Drives: G-code. A recipe is a file.

## Breaking it

1. **Payload.** Stock laser modules are ~0.5–1 kg (estimate). Gun + shell + Z
   module is ~2–3 kg, hung ~100–250 mm below the carriage. The belts don't care;
   the POM V-wheels and the carriage plate do: a static moment on eccentric-
   preloaded POM wheels will tilt the carriage slightly and creep (flat-spotting)
   over hours. Static offsets cancel between a dry run and the weld minutes later;
   creep over a session means re-checking the dot per session — which the camera
   does anyway. Repair: steel V-wheels or a linear-rail carriage conversion
   (MGN12, also 3D-printer commodity), and a counter-spring from the frame taking
   most of the weight.
2. **Stiffness.** Belt + motor ≈ 120–190 N/mm at the carriage (estimate from a
   GT2-6 EA ≈ 24 kN and ~22 N·m/rad stepper holding stiffness): a 2 N change in
   wire drag or umbilical pull moves the carriage ~11–16 µm. The carriage tilt on
   POM wheels multiplied by a 150–250 mm hang is unmodelled and probably larger —
   measure with the dial indicator and a 2 N pull.
3. **Power-off.** Unpowered steppers let the gantry be pushed in X/Y, and a
   5 mm-lead ball screw back-drives under ~2–3 kg (the vertical rating is 15 kg,
   but holding when unpowered is another matter). Keep holding current on, or use
   a 2 mm-lead T8 lead screw (self-locking) for Z.
4. **Stuck wire.** The turning tube pulls the wire; a NEMA 17 on a 20T pulley
   skips at a few tens of N, far below the wire's ~230–460 N capacity. The gantry
   loses position rather than breaking anything; rehome after. A breakaway in the
   shell mount is kinder.
5. **Angles.** The gantry gives X/Y/Z only. Changing a roll angle about the dot
   needs either a new cassette plus an X/Y/Z correction, or roll stages whose
   axes are not through the dot, compensated in software (inverse kinematics).
   Fine for a motorised search; tedious by hand. Putting B's nodal rolls under the
   Z module combines both.
6. **Heat and fume.** Belts and POM are ~300 mm above the weld; the frame is
   open. Fine.
7. **Tube change.** Park the beam at +Y and Z up; the tube lifts straight out.
8. **Inverted closure / second person.** Same station; recipe = G-code file +
   cassette number; home first.

## Branch C-T — Derek's table hole

Frame flat on the tabletop over a hole; rotator on a height-adjustable shelf
hung from the table by four rods (his "four corners"); rim near countertop
height. The X beam is then only ~70 mm above the rim, so it runs beside the gun
at mid-height and the carriage holds the shell from the side; heat, fume and
view are all closer to the belts. It keeps everything low and makes the shelf
the coarse Z. The legged version above needs no hole.

## Contribution

The cheapest, fastest route to motorised X/Y/Z with homing, G-code and a camera
software ecosystem — the platform for Derek's "let an AI iterate dry runs" goal
— from a product category sold in very high volume. Its role is best as the
search-and-repeat positioner; whether it is stiff enough to hold during a weld
is the open question.

## Unresolved

- Carriage tilt stiffness with a 2–3 kg hanging payload; creep.
- Whether the angle problem is left to cassettes, to software, or to B's head.
- The controller's suitability for closed-loop camera work (GRBL streaming is
  fine for moves; the camera loop would run on a PC).

## Needs Derek's observation

- Gun + shell mass (sets whether the stock carriage is plausible at all).
- How far he is willing to let the rig move the gun during a session (umbilical
  slack-span behaviour).

---

## Wave 3 — objections from one-knob-one-parameter

Source: `exchange/one-knob-one-parameter--on--borrowed-ecosystems.md`, sketch
`explorers/one-knob-one-parameter/sketches/c-g2-vertical-angle.svg`.

- **"Y is not a position axis near the corner" — agreed.** A straight Y move of
  s turns the approach by s/R (0.93°/mm) and leaves the dot s²/2R off the corner
  (0.23 mm at 5°, 2.0 mm at 15°). A search that "walks Y to find the corner" is
  changing an angle.
- **"A software pivot is only as single as its calibration" — agreed.** A pivot
  mislocated by d moves the dot d·Δθ (0.09 mm for 0.5 mm and 10°). On POM wheels,
  each compensation move also shifts the hanging CG, so the carriage tilt changes
  in a way the model does not contain.

**Branch C-G2 (theirs), adopted.** The engraver ecosystem's own vocabulary does
the vertical angle exactly:
- **Vertical angle.** A **G2/G3 arc about the tube axis** moves the dot round the
  corner circle, so the approach turns by the arc angle and the dot never leaves
  the corner. GRBL-class controllers run G2/G3 in the XY plane natively. The tube
  axis in machine coordinates comes from fitting the corner circle with the dot
  camera at three points, stored like a work offset.
- **Radial place and height.** Radial is a G1 along the radius at the current
  arc angle; height is Z.
- **Knobs as macros.** Named macros, one per parameter; calibration is the pivot
  coordinates and the tube-axis fit; motions to a stop are homing and park.

**Grip roll on a physical axis.** They propose a preloaded bearing pair on the
grip axis, hung from the Z carriage behind the butt. The stiffness is fine (their
estimate: ~7 µm for 2 N at the nozzle). But a closed pair cannot be fitted: seen
along the grip axis the proxy gun needs a 145 mm circle, so an 80 mm bore
cannot pass nose-first, and the umbilical is captive.

- **My repair (wave 2 exchange):** two hinged clamshell rings around a printed
  sleeve on the grip axis behind the butt, with roll set by a micrometer under a
  gravity-loaded lever. These hang from the Z module.

**What stays uncertain.**
- Carriage stiffness under a 2–3 kg hanging payload. An MGN12 conversion and a
  counter-spring from the frame are the repair; the walk test measures what is
  left.
- The legs and rotator share only the bench. A common plate — or a welding
  fixture table's hole grid, see notebook wave 3 — takes the wood out of the loop.
