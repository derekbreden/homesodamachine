# B — Nodal head: rolls about the dot, the work moves in X/Y

## Picture it

**The work side.** The rotator sits on a cast-iron compound cross-slide that
moves the tube in X (radial) and Y (tangent — which is really the vertical-axis
angle).

**The gun side.** On +X, a column carries a Z carriage. On it, a rotator's axis
*is* the horizontal radial line through the dot (the hole axis), at the dot's
height ~30 mm outside the OD. Its face carries a plate spoke that runs back
along −Y at the grip axis' 30° to a roll element on the grip axis behind the
butt. That element holds the shell.

**What that gives.** Both rolls pivot on the dot, a panorama head's
"no-parallax point", so changing either angle leaves the dot in place; X/Y/Z
then put it on the corner. Gun and cables stay still while the work moves.
"Fixed" is a common plate under cross-slide and column.

**Branches.**
- B-G: an inverted lens gimbal head as the hole joint.
- B-A: an all-Arca panorama stack.
- B0–B3: roll options (wedges, clamped arc, rotisserie rings, one closed
  bearing).
- From the wave-2 exchange: a hinged-ring roll sleeve and a gauge-block sine arm.

It is the same family as one-knob-one-parameter's isocentric gantry and
who-moves-what's protractor-and-stub. It **goes beyond Derek's examples.**

**Sketches.**
- `../sketches/b-nodal-head.svg` (true pose).
- `../sketches/x-okop-gravity-sine-arms.svg` (sine-arm and hinged-ring branch).

**Major unresolved problems.**
- A roll element that is both stiff and fits around a captive umbilical.
- Lock shift and tilt of bought rotators under 1–3.3 N·m.
- Cross-slide backlash and table size.
- Runout is left in unless combined with a rider stop.

Sketch: `../sketches/b-nodal-head.svg` (section + plan). Numbers from
`../calcs.py` §1, §6, §7 and `../geometry.py` (scene proxy, opening pose; the
hole *dial* offset of 35° is applied — wave 1 omitted it, corrected in wave 2).

## The physical idea

Panorama photographers need a camera to rotate about a point that is not on
any mount — the lens's no-parallax point — and their whole ecosystem of
rotators, offset rails, L-arms and gimbal heads exists to put rotation axes
through a point out in space. The welding problem is the same: Derek's grip
and hole rotations are defined about the laser dot. So:

- **Hole axis.** A rotator whose axis *is* the horizontal radial line through
  the dot: it sits at the dot's height, ~30 mm outboard of the tube OD on the +X
  side, axis pointing at the dot. Its face carries a **hole arm**: a plate ~30 mm
  outside the OD that runs back along −Y and up at the grip axis' 30°, then steps
  inboard to the grip-roll element behind the butt (the spoke layout
  one-knob-one-parameter reached independently). Turning it tilts the whole gun
  about the dot, exactly as the scene's hole control does.
- **Grip axis.** A roll about the line through the dot and the cable exit,
  realised beyond the grip base (options below).
- **Vertical axis** (setup only): the column's foot slides on an arc plate of
  radius ≈253 mm centred on the dot's vertical.
- **X/Y at the work, Z at the head.** A cast-iron machinist compound cross-slide
  under the rotator moves the *tube* so the corner comes to the fixed pivot; a
  lever-lift Z on the column (drill-stand style, spring return to a depth stop,
  or a 100 mm ball-screw module) sets height and does lift-off.

Result: every angle change leaves the dot where it is, and every X/Y/Z change
moves the corner or the pivot by exactly the dial reading. Setup becomes
separable — angles first, then position — and every setting is a number.

## Chain and reference ("fixed" = the bench top, or better a shared plate)

- Gun side: bench → arc plate (vertical axis) → column → Z carriage → hole
  rotator → hole arm → grip-roll element → shell → gun → dot.
- Work side: bench → cross-slide (X radial 210 mm, Y 110 mm travel as listed) →
  rotator base → ball race → turntable → nest → tube → corner.
- The gun is **stationary in space** for all X/Y adjustment, so the umbilical
  and the wire conduit spans do not change when the dot is walked onto the
  corner — the best umbilical situation of my three arrangements. The umbilical
  saddle bolts to the column.

## Loads (calcs.py)

- At the opening pose the gun lies back over the arriving side (CG proxy
  offset from the dot ≈ (−84, −120, +138) mm). Gravity torque about the hole axis
  is 1.35–2.7 N·m for 1–2 kg gun + shell (up to 3.1 N·m at hole 20), about the
  grip axis 0.4–0.9 N·m; one sign over the working range, so worm backlash is
  taken up one way.
- Bending on the hole rotator's bearing ≈ 1.4–2.5 N·m (CG ~116 mm inboard of a
  face 30 mm outside the OD), plus the arm's own weight.
- A worm-driven 4 in rotary table holds these without a lock; a friction
  indexing rotator (camera pano) holds them with its clamp, and a light
  counterweight on the far side of the hole arm can zero the torque, the way a
  gimbal head balances a long lens.

## Calibrating the pivot onto the dot (borrowed procedure)

Panorama users find the no-parallax point by rotating and watching for
parallax. Here: put a flat target at the corner height, turn the hole rotator
±5–10° with the guide beam on, and slide the shell along the hole arm (Arca rail
with a mm scale) until the dot stops moving. An axis that misses the dot by
d mm moves it by about d·θ: 1 mm miss × 5° ≈ 0.09 mm. Do the same for the grip
roll. After that, X/Y/Z are the only things that move the dot.

## Breaking it

1. **Grip roll is the weak link.** Any single rotary element at the grip base
   is ~280–320 mm from the dot. A printed arc on U/V-groove rollers with contacts
   of ~50 N/mm spaced ~70 mm has a tilt stiffness of order 1 × 10⁵ N·mm/rad; a
   2 N wire-drag change at the nozzle then tilts it ~5 mrad and moves the dot
   ~1.4 mm (rough estimate, but the order is the point). Repairs, each a branch:
   - **B0, roll set in the shell.** Interchangeable roll wedges; the shell bolts
     to the hole arm at two stations spanning the gun (grip end and the
     barrel/body junction, ~140 mm from the dot). Stiff; roll is a recipe, not a
     knob.
   - **B1, open arc, clamped for the weld.** Adjust on rollers during dry runs,
     then clamp a large face; roll becomes a setup axis.
   - **B2, rotisserie.** Two large ring bearings (12 in lazy-susan class, 247 mm
     inner ring) spaced ~100–150 mm along the grip axis around the gun body, so
     tilt stiffness comes from their spacing. The gun slides through them nose
     first before the shell closes. Stamped rings are sloppy; tilt stiffness
     unverified.
   - **B3, one stiff closed bearing around the cable exit** (crossed-roller or
     thin-section). The umbilical would have to be threaded through it once,
     which means disconnecting the QBH at the gun one time. Derek's call.
2. **Cable twist.** The scene draws the cable leaving the butt along the grip's
   rake (30° off the grip axis) and bending onto the grip axis within 70 mm; held
   on the axis, a roll about the grip axis twists it about its own length there
   (my wave-1 figure of 1.3° came from my own mis-drawn grip, since corrected).
   Over a ±10° exploration range that twist spreads along metres of free cable;
   over ±45° it is not small. The real exit direction needs the scan.
3. **Near-rim hardware.** The hole rotator lives at the dot's height just
   outboard of the rim, and the hole arm runs back ~30 mm outside the OD. It must
   clear the ground shoe and the motor tower at whatever azimuth they sit, and a
   hot rim radiates at it. The operator views from above/inboard, so it does
   not block the view.
4. **Tube change.** The gun lies back over the −Y side with only the barrel
   crossing the rim (nozzle ~5 mm above it). Lift Z ~40–60 mm, or retract the gun
   up its barrel line, and slide the tube out along +Y, away from the gun; or crank
   X by up to 210 mm. A kinematic dock between rotator
   and cross-slide (A2's coupling applied to the work) would make removal quick
   and exact.
5. **Height.** The cross-slide raises the joint by the table height (estimate
   100–130 mm), to ~340–360 mm above the bench; the adjustable bench can drop to
   compensate.
6. **Backlash and gibs.** Cross-slide screws have backlash; approach each
   setting from the same direction and lock the gibs. Their dial graduation is
   not published for the representative table.
7. **Stuck wire.** The head is rigid; the wire will bend or drag the tube.
   Release the pedal (the belt drive backdrives, per the repo). A breakaway at
   the shell–arm joint (magnetic kinematic seat, as on robot torch mounts) is an
   option.
8. **Inverted second closure.** Identical from the head's side; 2.01 kg on the
   cross-slide is trivial.
9. **Second person.** Rotator degrees, two cross-slide dial readings, a depth
   stop, a roll wedge number. A recipe card.

## Branches using other borrowed heads

- **B-G, inverted gimbal head.** A telephoto-lens gimbal head (Neewer GM101
  class, $130, 605 ratings) hung upside down so its tilt pivot sits at the dot's
  height outboard with the tilt axis radial: its swing bracket rises to an Arca
  platform above the rim, and an Arca rail reaches inboard to the shell. Bearings,
  lock and a sliding platform for pivot calibration come in the box; a printed
  tangent-screw fine drive is added. Its pan axis is then not through the dot
  (setup only anyway).
- **B-A, all-Arca multi-row panorama head.** Rotators, L-rails, nodal rails and
  clamps assembled exactly as photographers do, with printed adapters to the
  shell. Fastest to prototype, least stiff.

## Motorised version (Derek's automated vision)

Five motors map one-to-one onto this kinematics: X and Y (NEMA 23 on the
cross-slide handwheels — a common hobby conversion), Z (100 mm SFU1605 module;
5 mm lead back-drives, so keep holding current or use a 2 mm-lead lead screw),
hole roll (worm stage or the rotary table's handwheel), grip roll (worm on the
arc). Because both rolls pivot on the dot, an AI sweeping roll does not have to
re-centre after each step — the search is separable, which makes dry-run
experiments cleaner to interpret.

## Parts (see `../../sourcing/borrowed-ecosystems.md`)

VEVOR compound table ($136, 50+/month); Sunwayfoto DDP-64Si indexing rotator
($55, low stock) or a 4 in H/V rotary table ($99–135 generic, $469 Vertex);
Neewer GM101 gimbal head ($130) for B-G; SFU1605 100 mm module ($74) for Z;
2040 column; printed hole arm or 25 × 50 mm aluminium bar (a 300 mm cantilever
of that bar is ~500–2000 N/mm, so the arm is not the weak link).

## Contribution

The only one of my arrangements where Derek's three rotations exist as real,
separately adjustable joints about the dot, with the dot left in place — the
closest physical match to the orientation scene — and where the gun (and its
cables) stay still while the work is positioned.

## Unresolved

- Grip-roll stiffness vs adjustability vs cable twist (branches B0–B3).
- Actual stiffness of pano rotators and gimbal-head tilt locks under 1–2 N·m.
- Cross-slide screw lead, backlash and table size (listing inconsistent).
- Whether the corner should instead be followed (A1) — B leaves runout in.

## Needs Derek's observation

- Would he disconnect the QBH once to thread a bearing (B3)?
- Motor-tower and ground-tower azimuths, so the outboard rotator can be placed.
- Bench flex between a column and the rotator when leaning on the bench (a
  shared plate under both is the obvious answer).

---

## Wave 3 note

one-knob-one-parameter reads B as their isocentric gantry and finds the
"no-parallax point" a better name for the isocentre. For the grip-roll weak link
they estimate that a lightly preloaded 6816 pair 30 mm apart moves the dot only
~7 µm for 2 N at the nozzle. The stiffness is fine, but the fitting is not: the
proxy gun's silhouette along the grip axis needs 145 mm, so the 80 mm bore cannot
pass nose-first. The wave-2 hinged-ring sleeve (two clamshells, micrometer under
a gravity-loaded lever) is the repair I carry into B, and the gauge-block sine
arm is the hole-angle branch (`exchange/borrowed-ecosystems--on--one-knob-one-parameter.md`).
B and their gantry are one family; the walk test is B's QA.
