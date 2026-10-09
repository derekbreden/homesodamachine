# one-knob-one-parameter on who-moves-what (wave 4): the tilt cradle and escape rail

I worked on `explorers/who-moves-what/ideas/tilt-cradle-escape-rail.md`, as drawn
(branch T-b: the whole station on a cradle tilting about the station tangent
through the dot, τ* = 32.5°, recipe block on a carriage riding a straight escape
rail, yaw on a Y slide). My view asks three things of every setting: that it
changes one thing, and that it can be read and returned to. Gravity is here
made an explicit knob, which is the most interesting thing anyone has done with
it, so I held τ to the same test.

Calculations: `explorers/one-knob-one-parameter/tilt_exchange_calcs.py`. Numbers
use the scene's proxy at the opening pose (dial convention). Tube and plate
masses are from 316L density.

## What it does that my arrangements lack

- **Gravity becomes a knob, with an absolute reading.** An inclinometer on the
  cradle floor reads τ against gravity itself. No other setting in the study
  reads without a calibrated zero.
- **Everything rides the cradle.** The tilt mechanism therefore needs no
  precision: a quadrant and a pin.
- **The escape rail** turns loading, lift-off and return into one gravity-seated
  motion to a stop, clear for all 32 feasible recipes. My stations needed a
  drawer, a standoff retract lever and a wire-guide flip to do the same.
- **The tangent tilt is a pure work-angle knob in weld language** (their table:
  1° about the tangent = grip +1.11, hole −0.26, vertical −0.55). My wave-1
  table found that the same pure work-angle change takes three of Derek's dials.

## Difficulty 1 — the rail stop sets two things (standoff and yaw), and nothing sets the dot across the corner

**Variant.** T-b as drawn: carriage on the rail, recipe block for roll and hole,
"stop screw at the bottom of travel sets the seated position", Y slide for yaw.
The rotator's three Z screws put the corner back on the trunnion axis per tube.

**What the stop actually moves.** At τ* the rail is vertical and the beam lies in
the vertical plane through the tangent, 32.4° from the rail. Moving the seat
1 mm up the rail:
- changes the standoff by +1.18 mm;
- slides the dot 0.64 mm along the seam.

A slide along the seam is a vertical-axis angle change of s/R = **0.59° per mm**,
and the dot camera cannot see it, since the dot is still on the corner.

So the stop screw is a standoff knob that also turns yaw, and the Y slide must
undo it. The direction that moves the dot *across* the corner, between wall and
cap, is horizontal and radial in the room at τ* (perpendicular to both the beam
and the seam). Nothing on the gun side moves along it. The rotator's Z screws
move the corner along the tilted tube axis, which in the room is a mix of
vertical (standoff plus seam) and horizontal (across).

**Assumption.** A recipe is fully set by the block's two angles and the rail's
stop; the stop is "where the gun sits".

**Repair: branch T-b1, the rail only stops.**
1. The rail stop becomes a fixed hard stop, a motion to a stop that is never
   adjusted per recipe.
2. The carriage carries two small translation stages whose directions are
   chosen to be one-parameter:
   - **S (standoff):** parallel to the beam. At τ* that is 32.4° from the rail
     in the vertical tangent plane. It changes focus only, because the beam
     line does not move.
   - **A (across):** horizontal and radial in the room at τ*, perpendicular to
     beam and seam. It moves the dot between wall and cap only.
3. **Yaw** stays the Y slide (circle symmetry, 1.08 mm per degree).
4. **The rotator Z screws** become per-tube calibration: set once by the rim
   flag so that the stop lands the dot on this tube's corner, then left alone.

The recipe block has no rotations downstream of the stages, so the stages can
sit anywhere in the chain without coupling (my chain rule is satisfied
trivially). Their range needs to be ±2 mm each. That is exactly what a printed
parallelogram flexure with a micrometer lever does (part 2 of my wave; see
`explorers/one-knob-one-parameter/ideas/flexure-trim-head.md`).

**What it leaves uncertain.** At τ ≠ τ* the rail is no longer vertical. S and A
are fixed on the carriage, so they stay one-parameter only if they are defined
relative to the beam, which they are: they ride the cradle with the gun, and the
beam's relation to the cradle does not change with τ. So they hold at every τ.
✓. The stop's hard seat must repeat to microns (a ball-in-vee at the bottom of
the rail, gravity-loaded, as their note already implies).

**Branch T-g — gravity and work angle on one line.** The cradle's axis *is*
the seam tangent through the dot. Put a small work-angle pivot about that same
line on the carriage, between A/S and the recipe block (an arc, or the flexure
remote-centre pivot of part 2). Then:
- the gun's pivot α changes the **work angle with gravity fixed**;
- the cradle τ changes **gravity with the work angle fixed**;
- α = −τ reproduces their T-c "the work takes the angle" (work angle *and*
  gravity together).

The two knobs are coaxial and nested, and each reads directly: α on its
micrometer, τ on the inclinometer. The "is it the angle or is it gravity?"
question becomes a two-factor experiment instead of a confound.

## Difficulty 2 — τ reaches the relative pose through gravity-loaded contacts

**Variant.** T-b's claim: "the trunnions and lock then set only gravity's
direction. Their play or compliance tilts gun and work together, so it never
reaches the relative pose."

**Where it breaks.** True for the trunnions. Not true for the contacts *inside*
the cradle's loop (gun → carriage → column → floor → rotator base → race →
turntable → nest → tube), because τ rotates gravity relative to each of them:

- **The tube tips in its nest before the turntable does.** The first-closure
  tube carries its plate at the top: 1.40 kg with its centre of mass 108 mm above
  the rim it stands on, which puts the tipping angle about the rim edge at
  τ = 30.5°, before τ*.
  - It starts sliding on its rim near 17° (µ ≈ 0.3). Between 17° and 30° it
    slides into the low-side adjuster; beyond 30° it leans on the OD guide.
  - The guide allows 0.4 mm radial clearance over its 10 mm height, so an
    unclamped tube can lean by a degree or more. The corner, 146 mm above the
    rim, would then move by millimetres.
  - The second closure is lower (2.2 kg, CoM 76 mm, tips at ≈ 40°).
  - Their break 2 treated sliding (0.54 W at τ*), not tipping.
- **The turntable itself lifts at 30–40°** (their break 1): the 1 mm lift gap
  lets the whole tube tilt.
- **Contacts that change load with τ:** the carriage's seat changes from
  0.84 W along the rail plus 0.54 W across it at τ = 0 to W along it at τ*.
  Every gravity-loaded seat moves by its compliance times that change.

**The effect in my terms.**
- τ changes gravity (intended), and through the nest and race it changes the dot
  place (the camera sees it) and the angles (the camera does not).
- A τ = 0 against τ* comparison would carry an unknown angle change on top of
  the gravity change.

**Assumption.** Everything on the cradle is rigid, or at least equally loaded at
every τ.

**Repair, making the loop gravity-proof and measuring what remains:**
1. **Clamp the tube to the turntable** instead of letting it stand in the nest.
   - A 5 in band clamp around the OD (work-as-datum's stock exhaust band clamp,
     C1), tied down to the turntable by three printed posts.
   - It goes between the ground shoe's wiped stripe (15–65 mm above the nest)
     and the rim, at about 70–110 mm, so it clears the shoe and stays well below
     the weld.
   - The three adjusters remain the indicator adjustment; the band holds
     against tipping.
   - Both closures fit, since the band grips the tube, not a plate.
   - The posts turn with the table, so they must clear the ground tower (low)
     and the gun (above the rim).
2. **Preload the turntable catch** (their repair b: PTFE thrust washer + wave
   spring). The preload must exceed the tipping moment at the largest τ used:
   about 25 N × 0.12 m × sin τ ≈ 1.6 N·m at 32.5°, estimate, i.e. about 20 N at
   the race radius, plus margin.
3. **Seat the carriage by a spring beyond gravity**, so its seating force does
   not switch between 0.84 W and W.
4. **Tilt walk test** (the τ version of my isocentre walk test):
   - With the corner phantom in the band clamp and the red dot on, cycle
     τ 0 → τ* → 0 three times.
   - Read the dot on the cradle camera (dot place).
   - Read two digital angle gauges, one on the shell and one on the rotator
     base (both Klein 935DAG class). Their *difference* is the relative angle
     change the camera cannot see.
   - τ is a clean gravity knob when the dot stays within, say, 0.02 mm and the
     gauge difference within 0.1°. Those are thresholds for Derek to choose.

**What it leaves uncertain:** band-clamp distortion of the thin wall (0.065 in)
if it is overtightened. A wide band at modest torque, checked by indicating the
rim with the band on and off, answers it.

## Difficulty 3 — τ is not one parameter for the gas

**Variant.** Their "Process" list already separates pool, shielding, purge and
lip. From my view the problem is that one knob (τ) moves all four, so a bead
difference between τ = 0 and τ* cannot be attributed.

**An estimate that splits it** (Richardson number of the shielding jet,
Ri = g′L/U² with g′ = g·Δρ/ρ_Ar ≈ 3.2 m/s² for argon in air; nozzle bore
**[Unknown]**, 6–10 mm tried):

| Flow | Near the pool (10 mm, jet speed) | Over the lip (30 mm, jet decayed to 20 %) |
|---|---:|---:|
| 6 L/min | 0.003–0.02 | 0.19–1.5 |
| 15 L/min | < 0.003 | 0.03–0.24 |
| 20 L/min | < 0.002 | 0.02–0.13 |

**Reading.**
- At the pool the jet's momentum dominates, so coverage there should hardly
  notice τ.
- The slow gas over the hot lip, the trailing bead and the recess "cup" is where
  buoyancy competes. That is also where their 2.9° spill-over matters.
- So τ plausibly changes **pool attitude** and **trailing/lip shielding**, not
  the shielding of the pool itself.

**Repair, making the confound measurable rather than hoping it away:**
- **Read the gas side.** Heat tint on the lip and the trailing bead is the
  shielding outcome; the root-side tint is the purge outcome. Photograph both
  at fixed lighting beside every τ run.
- **Run τ against flow as two factors** (0° / 32.5° × low / high flow). If the
  bead's τ effect does not change with flow, it is the pool, not the gas.
- **If it does,** a shallow printed-and-steel skirt around the nozzle, riding
  just above the rim on the station side, makes local coverage independent of
  τ. It can be tested as its own knob, in or out.

**What it leaves uncertain:** the nozzle's real exit bore and flow, and whether
tint grades finely enough to be a reading.

## Gravity as a knob, summarised

| Asked of τ | T-b as drawn | With T-b1 + the repairs above |
|---|---|---|
| Read | inclinometer on the cradle floor, absolute ✓ | same |
| Return | pin holes, exact ✓ (discrete) | same; a worm + lock if continuous τ is wanted |
| Changes only gravity? | no: tube tipping, race lift, seat load changes reach the pose | band clamp, preloaded catch, sprung seat; the tilt walk test measures the rest |
| One gas parameter? | no: pool, lip shielding and purge all move | τ × flow factorial; tint as the reading; optional skirt |
| Recipe knobs independent? | the stop screw moves standoff + yaw (0.59° per mm) | S along the beam, A across the corner, stop fixed |

## Transfers

**From them to me.**
- The escape rail is the loading motion my stations lack: a single
  gravity-seated motion to a stop that clears for every recipe. My couch's Y
  drawer, standoff retract and wire-guide flip could all collapse into it.
- τ as an absolute-reading knob belongs in any station that wants to test 2F
  against 1F.
- Their evidence that the tangent tilt is a pure weld-language work angle
  supports my collimator branch. The same line, used twice (T-g), separates the
  two.

**From me to them.**
- Choose stage directions by what they change: along the beam, and across the
  corner.
- Separate stops from knobs.
- The tilt walk test with two inclinometers.
- The first-closure tube tips before the turntable does.

## Questions this adds for Derek

- For the first closure, is the tube normally clamped in the nest at all, or
  only indicated? At τ > 30° it must be clamped.
- Would he accept a band clamp on the tube OD near the nest?
