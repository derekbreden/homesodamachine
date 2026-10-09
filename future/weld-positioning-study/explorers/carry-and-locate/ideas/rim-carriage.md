# D — Rim carriage: the turning tube carries the locator

**Picture it.**
- **Ring.** A C-shaped ring sits on the tube's rim on three stainless rollers,
  open around the weld station. Roller pairs at ±30° pinch the 1.65 mm lip
  from inside and outside.
- **Tether.** The ring does not turn; the tube turns under it. A soft tether
  resists only the spin, which does not matter to the dot.
- **Gun.** A post from the ring carries an adjustment stack and the gun.
- **Carry.** A balancer overhead carries most of the weight so the rim sees a
  chosen 10–20 N; a saddle carries the cable.
- **"Fixed."** The tube itself: the rim plane and the lip.
- **Branch D-s** (machine-that-learns) keeps only a light stylus on the tube as
  a sensor and moves the carrying elsewhere.

**Sketch:** `../sketches/D-rim-carriage.svg` (true opening pose).

**Major unresolved problems:**
- The rim is not the joint: cap tilt is unseen.
- The lip is warm and may be burred.
- The rollers could bond the gun to the work electrically (interlock).
- The open ring's torsional stiffness.
- D-s answers most of these but needs an actuator.

Sketch: `../sketches/D-rim-carriage.svg`. Numbers: `../calc/dock_and_rim.py`,
`../calc/ovality.py`. (Likely overlaps an explorer working from "the work as
datum"; this file follows the load paths.)

## The physical idea

Let part of the gun's weight rest on the tube itself, through rollers on the
rim, so that the load path from gun to joint is short and runs through the
workpiece. A printed or aluminium C-ring sits on the rim on three rollers and
turns nothing: the tube turns under it. The gun hangs from the ring on an
adjustment stack. A float above (balancer) carries most of the gun, ring and
cable weight and leaves only a chosen preload on the rim. A soft tether keeps
the ring from being carried round.

Position loop: rim and lip → rollers → ring → post → stack → shell → gun → dot.
The rotator base, ball race, nest, bench and tube seating are not in it.

## Geometry around the actual gun

- C-ring ~8 mm above the rim, open ±24° around the station so the beam, wire
  and nozzle have the gap. At the opening pose the nozzle tip is ~5 mm above
  the rim and the barrel axis crosses the rim plane ~4 mm inside the bore; the
  ring stays clear by the opening.
- **Rim rollers** at +30°, 180°, −30° (on the rim top): set Z and both tilts
  from the rim plane.
- **Pinch pairs** at ±30°: a roller inside the lip and one outside, squeezing
  the 1.65 mm wall. They set the ring's centre and put **no net radial force**
  on the tube.
- **Post** at 180° rising to ~470 mm above the bench, then to the adjustment
  stack at the housing back.
- **Float**: balancer from overhead to the post top; rim preload ~10–20 N.
- **Tether**: a bungee from the post to a fixed point, resisting only spin.

## Why a soft tether is enough

Turning the ring about the tube axis slides the dot along the joint, which is
a circle: it does not move the dot off the joint at all. That DOF — the one the
turning tube tries to drive — is the one position does not care about. The
tether only has to keep the ring (and umbilical) from winding up.

## What the tube can take

- Downward load inside the tube's own footprint cannot tip it; it only adds
  seat load in the nest. A 20 N preload adds ~8 N·mm of race drag against
  ~8500 N·mm available at the table. **[Calc, estimate of race rolling
  resistance]**
- A net *radial* push at the rim of only ~6 N (first closure, 1.40 kg) to
  ~8 N (second, 2.01 kg) would lift the far lower edge in the nest. Pinch
  pairs avoid it; so must the cable (carried by the saddle and float, not by
  the ring).

## What the dot then follows

- **Radial runout, face runout, reseating, tube-to-tube variation**: the ring
  rides the actual tube, so the 0.25 / 0.30 mm TIR acceptance becomes much
  less important.
- **Ovality**: depends on where the radial references are. With pinches at
  ±a from the station, the bore's ovality amplitude e leaks into the dot's
  radial position as ±2.0e at ±60°, ±1.0e at ±45°, ±0.42e at ±30°, ±0.10e at
  ±15° (a gun fixed to the base sees ±1.0e plus eccentric runout). That is why
  the pinches sit at ±30°, as close to the station as the gun allows.
  **[Calc, ovality.py]**
- **Rim vs joint**: the ring follows the rim; the joint is the cap face and
  bore 6.35 mm below. A cap seated with a face tilt (≤ 0.30 mm TIR allowed)
  changes standoff without the rim knowing. The rim itself must be square and
  deburred if it is the reference.

**Branch D2 — local shoe at the joint.** A small follower 20–30 mm ahead of the
dot on the arriving side: one wheel on the cap face 5–10 mm inboard of the
bore, one on the bore 3–5 mm above the cap face (clear of the fillet leg and of
tacks). The ring then carries and places roughly; the shoe locates radius and
height from the joint surfaces themselves; the ring's rollers keep only the
tilts. The preload that presses the shoe into the corner is down (residual
weight) and outward (Derek's X bungee reappears here, as the radial preload).

## Heat, surfaces, contamination

- Ahead of a moving source at 5–15 mm/s the characteristic heated length in
  316L is 2α/v ≈ 0.5–1.6 mm, so a contact 20+ mm ahead of the puddle sees bulk
  temperature. The vessel warms ~10–20 K per revolution overall (estimate).
  The 180° roller sees material welded ~24 s earlier; the lip near the bead
  may be warm there. **[Calc, Rosenthal scaling and a lumped estimate]**
- Printed parts stay ≥ 10 mm off the rim; rollers on metal axles in metal
  brackets. PET-GF softens near 70–80 °C.
- Rollers in 440 stainless or hybrid ceramic, not chrome steel, so no iron is
  left on the 316L.
- Tacks sit in the corner; rim rollers never meet them. D2's wheels must stay
  inboard and above the fillet.

## How it is used

- **Setup**: set the ring on the rim, hook the float and tether, dock the gun
  on the stack, and set dot and angles with the reference beam during a slow
  revolution. The setting is relative to the ring, so it carries over to the
  next tube.
- **Tube change**: lift ring + gun together on the float; the next tube's rim
  receives them; the setting comes with them.
- **Stuck wire**: the tube drags the wire; the ring is held only by the soft
  tether, so ring, gun and wire rotate a few degrees *with* the tube instead of
  bending the wire guide — the don't-care DOF becomes the fuse. Then pedal off
  and snip. The umbilical saddle must tolerate those few degrees.
- **Second closure**: the heavier tube is steadier under the ring; nothing
  else changes at the top.
- **Second person**: "set the ring on the rim" is the whole location step.

## Unresolved

- Whether the rim is a trustworthy reference (cut quality, squareness, burrs)
  — Derek's observation.
- Whether a C-ring with a 48° gap is stiff enough in torsion; aluminium may
  be needed.
- The contact interlock: the X1 Pro's product page states the laser only fires
  when the gun touches metal **[Vendor page]**. Rollers electrically bonded to
  the gun would make that contact continuous. That would change what the
  interlock protects, so it is a question for Derek, not a proposal.
- D2 geometry around the actual wire guide and nozzle needs the gun scan.

## Parts

- 440 stainless S695ZZ bearings (Prime; thin stock on that listing, universal
  size), hybrid-ceramic S624 as alternative.
- QWORK 0.5–1.5 kg or larger balancer for the float (ring + gun + stack may
  exceed 1.5 kg; the 1.5–3 kg size exists in the same format).
- Shock cord for the tether.
- Printed or aluminium ring, post, stack mount; metal roller brackets.

## Wave 3: branch D-s (machine-that-learns) — sense, don't carry

Their objection to D as written:

- the carriage that follows the tube also carries: 10–20 N of float residual
  plus ring and gun, through rollers on a warm, possibly burred 1.65 mm lip;
- it reads the rim, not the joint, so it misses cap tilt;
- it bonds the gun electrically to the work;
- its 48° open ring must be stiff in torsion;
- ovality leaks at 0.42e.

**D-s keeps the following and drops the carrying.**

- A ceramic-tipped stylus on a spring (0.5–1 N) touches the tube's outside at
  the dot's own angle, ~9 mm below the joint.
- Its stem runs on a slide with a scale read continuously (an iGaging absolute
  caliper beam via its data port, or an AS5048 on a lever).
- It stands on whatever carries the gun.

In my terms, D-s splits locating into sensing (the stylus) and acting (a stage
that moves the gun or the tube). Carrying goes to the float and saddle as
everywhere else. I agree with the branch.

**What it fixes:**

- 0.5–1 N cannot tip the tube (6–8 N would).
- An insulating tip makes no interlock path.
- Ovality is measured at the dot's angle instead of leaking.
- It works during the weld, when the red dot cannot be seen.

**What it leaves:**

- The stylus reads the outside, the joint is on the bore, so wall-thickness
  variation around the tube leaks in. The spec is ±10 %; the variation around
  one tube is unknown and probably much smaller. A dry-run camera map against
  the stylus calibrates it once per tube.
- The outside seam passes the tip once per revolution; mask it.
- Face runout needs a second stylus on the rim top.
- The scale must be kept 60 mm or more from the heat.
- It needs an actuator.
- It loses D's spin fuse.

**Where the stylus stands matters.** On the gun's own carrier (their A portal,
their B carriage, my E plate), it reads tube relative to gun, which is the
quantity a null-seeking stage needs. On the bench it reads tube relative to
bench, and the gun's position would also have to be known.

**With a locked skate (`switch-lock-skate.md`)** nothing follows during the
weld. D-s then becomes the weld-time log: every bead leaves a trace of radial
runout, ovality and thermal growth at the dot. That trace is what decides
whether a follower is worth building at all.

D as written stays above as the original: the tube carrying the locator is
still the only arrangement here in which the don't-care spin is the fuse.
