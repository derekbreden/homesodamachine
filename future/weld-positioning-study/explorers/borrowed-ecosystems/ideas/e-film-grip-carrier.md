# E — Film-grip carrier: an iso-elastic stabilizer arm on a C-stand, gimbal at the CG

## Picture it

**The carrier.** A stainless C-stand stands off the bench's −Y end. Its riser
carries a Steadicam-type iso-elastic arm: two spring parallelograms on
ball-bearing hinges. The arm's post enters a printed yoke gimbal: a heading
bearing on the post, and trunnions straddling the shell at the gun's CG.

**The cable.** The stand's boom carries the umbilical and conduit saddle at the
cable's natural apex.

**Locating.** The tube rider does it (A1-S with A1-G's knobs), or a dock. The
arm only carries: near-constant lift, no horizontal return, and — once the
carry pins are out — no moments. Nothing on the stand is in the locating chain;
the tube is the reference.

**After sequence-of-use's wave-4 critique.**
- Carry pins lock the gimbal's tilt axes whenever the gun is off the tube (E-s).
- The rider gets LAND and WELD stops on a barrel-line slide (E-z).
- A stand-hung plate head does the tacks.
- A stickout gauge sits in the docking cup.

It **goes beyond Derek's examples** (film and stage ecosystem), but it plays
the role he gave his monitor arm.

**Sketches.**
- `../sketches/e-film-grip-carrier.svg` (true pose; the pins and stops are
  labelled, their mechanisms described below).
- Their session: `../../sequence-of-use/sketches/w4-film-grip-session.svg`.

**Major unresolved problems.**
- The real umbilical pull, which decides between pins, pendulosity and trim.
- The arm's vertical rate, hinge friction and mid-stroke range at ~2.5 kg.
- Yoke clearance around the real gun.
- Whether set-down needs a damper.

Sketch: `../sketches/e-film-grip-carrier.svg` (elevation from +X and plan, at
the corrected opening pose). Numbers: `../calcs_wave3.py`. Sourcing:
`../../../sourcing/borrowed-ecosystems.md` (wave 3).

## Why this ecosystem (what I looked at first)

Wave 3 asked for ecosystems nobody had opened: industrial tool handling, film
and stage. What the Prime-filtered searches showed on 2026-09-28:

| Looked for | What is really buyable next-day | Verdict |
|---|---|---|
| Torque-reaction arms, zero-gravity tool-support arms (assembly lines) | Nothing industrial at volume. Searches return camera magic arms, e-bike "torque arms", welding-table arm rests and $140–350 tapping arms with few ratings | The *principle* is right; the product is quote-and-lead-time |
| Power-off electromagnetic brakes for a "grab, move, let go, it locks" teach arm | Only brake-equipped integrated steppers ($136–234, ~1 rating) | Not buildable from volume parts yet |
| Camera jibs and cranes | Carbon mini-jibs at $500–750 with ≤13 ratings; long, flexible booms | Not a locator; not a better carrier |
| C-stands and grip heads (film grip) | Stainless heavy-duty C-stand with boom arm: 2,476 ratings, 100+ bought per month, next-day. 2.5 in grip head: 491 ratings | High volume, real structure |
| Steadicam-type iso-elastic arms (film) | FLYCAM Comfort arm & vest (5 kg, 314 ratings, $209); FLYCAM Galaxy (two springs, 2–5 or 5–10 kg, 249 ratings, $448) | The carrier the "soft carrier" family has been missing |

Zero-gravity tool arms for grinders *are* Steadicam technology (iso-elastic
springs plus a gimbal at the tool). The film version is the one sold in volume.

## The physical idea

Seven explorers converged on "a soft carrier takes the weight, a stiff seat or
the tube locates". The carriers used so far each have a known fault:

- **Monitor arm.** Friction joints pass moments and stick-slip into whatever
  locates, and the gas spring's force changes with height.
- **Spring balancer on a line.** A pendulum: parked 300 mm aside it pulls back
  with 6–9 N (0.8–1.2 m line, 2.5 kg). Two anchors yaw the gun (sequence-of-use's
  objection).
- **Hook on a spring.** Carries well but has no reach or parking.

A film **iso-elastic stabilizer arm** is the device built to do exactly the
carrier's job: carry a payload's weight at nearly constant force over a large
vertical range, on ball-bearing hinges about vertical axes, and deliver it
through a **three-axis gimbal at the payload's centre of mass**, so that neither
force changes nor moments reach the payload. On a Steadicam the operator's body
is the thing that must not disturb the camera; here it is the carrier that must
not disturb the locator.

The whole station:

- **Stand.** A stainless C-stand with a turtle base and a sandbag, off the
  bench's −Y end (the side the gun leans toward and the umbilical leaves). Its
  riser carries a printed or aluminium arm socket on a 5/8 in baby pin at about
  the gun's height (~420 mm above the bench top, about mid-stroke of the arm).
- **Arm.** Iso-elastic, two parallelogram sections, spring window chosen so gun +
  shell + rider + gimbal (estimated 2–3 kg, plus ballast if short) sits
  mid-window, e.g. a 2–5 kg spring. Its 16 mm end post carries the gimbal.
- **Gimbal at the CG.** A printed yoke straddles the shell. Trunnion pins on the
  shell sit on an axis through the gun's CG (proxy at (−23, −120), 370 mm above
  the bench), and the yoke turns on a vertical bearing on the arm post. This is
  Derek's "loop around the gun" given two pivots. The CG sits 2–5 mm below the
  trunnions, so the lifted gun hangs near its working attitude. Gravity's
  restoring torque (0.9–2 N·mm per degree) is too small to matter once the rider
  holds the pose (≤0.02 N·m at 10° off).
- **Locator.** The tube rider: A1-S (OD wheels straddling the dot at ±30°, rim
  wheels at ±60° for height), carrying A1-G's knob set (curved Y, XYZ, a
  goniometer about the dot, wire micrometers). A2's dock works the same way.
- **Umbilical and wire conduit.** Both ride on an R ≥ 350 mm printed saddle on
  the C-stand's boom arm (via a grip head) near the loop apex, ~420–450 mm above
  the bench and 0.3–0.5 m behind the gun on −Y. From the saddle to the grip butt
  hangs one slack span, and to the cart one more. Carrier and cable support are
  on the same stand.
- **Trigger.** A Bowden lever in the shell (the study-wide convention).

## What carries, what locates, what "fixed" is

- **Carries.** The arm spring, through the gimbal. The rider is set 5–10 N
  under-balanced for preload, i.e. 0.5–1 kg of a 2–5 kg spring window, by the
  arm's tension knob.
- **Locates.** The tube, through the rider (five constraints). Tangential
  position: the rider's soft tether with breakaway.
- **Fixed.** Nothing the stand does is in the locating chain. The floor, the
  stand's flex, the grip heads' compliance and the arm's bounce reach the gun only
  as small force changes on the rider:
  - **Vertical.** An effective arm rate of 0.1–0.5 N/mm (assumed) means
    0.015–0.075 N over the rider's ±0.15 mm follow.
  - **Horizontal.** Bearing hinges on vertical axes give ~0 N of return, with no
    pendulum.
  - **Moments.** None, because of the gimbal.

## Running it

- **Setup.** Roll the stand to floor marks, sandbag it, set the socket height so
  the working position is mid-stroke, then set the arm tension for 5–10 N of
  preload.
- **Setting down.** Swing the gun over the tube and set the rider down. The arm
  holds whatever height it is left at, so this is one hand and slow.
- **Dot and angles.** Set the dot with the rider's XYZ and the angles with the
  goniometer and curved Y. Dry lap: the dot should stay on the corner.
- **Weld.** Nothing moves but the tube and the wobble. The arm is neutral, so
  the wire's drag and the umbilical's residual load only the rider and tether.
- **Lift-off.** Lift; the gun floats and hangs near its working attitude on the
  gimbal. The wire tip lifts off the corner vertically; for the lip, a short lift
  along the barrel line first, which the rider's Z can do.
- **Stuck wire.** The tube drags wire, gun and rider along the rim. The arm
  follows with ~0 N (it adds no resistance, unlike a stiff holder), the tether's
  breakaway opens the pedal line, and the wire is snipped wherever it stopped.
- **Park.** Swing the arm so the gimbal drops into a printed docking cup on the
  stand (the Steadicam "docking stand" practice). Or roll the whole stand away
  with the saddle; the gun-to-saddle span keeps its shape because both move
  together, which answers sequence-of-use's objection that a parked carrier
  changes the umbilical's shape.
- **Tube change / second closure.** Park, change, return. The next tube's own
  rim locates.
- **Second person.** Floor marks, the arm's tension-knob count, set down, check
  the dot.

## Real capability, and what users report

- **Payload windows.** FLYCAM Galaxy: blue spring 2–5 kg, red 5–10 kg, tension
  knob, 16 mm post. FLYCAM Comfort: single spring up to 5 kg.
  - Comfort reviewers say the spring is too strong for light rigs, which then
    bounce with each step. The gun must sit mid-window, so ballast the gimbal if
    needed.
  - Galaxy owners report the two-spring arm much smoother.
- **Bounce.** Reviewers' main complaint is vertical bounce when walking: low
  damping, the opposite of a monitor arm's stiction. For a static station
  that is the right fault to have. The rider's contact damps it, and setting down
  slowly avoids a hop. The free bounce frequency is ~1–2 Hz at 2.5 kg (estimate).
- **Fit.** One reviewer taped the arm-to-vest connector for a snug fit. Here the
  socket is printed to the measured post and pin.
- **C-stand and grip heads.** The listing warns that adjusting a joint while the
  load is unbalanced can damage the screw joining the two halves — the grip
  convention "support the load, then loosen". Neither is in the locating chain,
  so their compliance is harmless. Overturning: 16–22 N·m from the arm at
  0.5–0.7 m reach against ~40 N·m from a 9 kg stand at 0.45 m leg reach
  (estimates); a 7 kg sandbag adds ~31 N·m.

## Breaking it

1. **The arm's iso-elastic range is mid-stroke only.** Near its ends the lift
   changes, and so does the preload. The C-stand riser sets the socket height so
   the working pose is mid-stroke.
2. **Setting down onto the rider** with a 1–2 Hz undamped spring can hop the
   rider's V-wheels. Repair: a light friction pad or a furniture soft-close damper
   across one arm section (a high-volume part, not sourced here). Set-down then
   becomes a slow settle.
3. **Arm horizontal neutrality depends on the stand's riser being plumb.** A
   tilted riser gives the hinges a gravity bias, and the arm drifts one way. The
   rider's tether and contacts absorb small biases; the turtle base's levelling leg
   (standard on C-stands) sets plumb.
4. **Bench on casters vs stand on the floor.** Relative motion changes the
   umbilical span's shape. The force change on the rider is small (span stiffness
   of order 0.05 N/mm, estimate), but lock the casters.
5. **Gimbal yoke around the shell** adds width at the housing (~60 mm inner). It
   must clear the rider's bracket at θ ≈ −75° and the trigger lever; the scan
   decides.
6. **No locator of its own.** Without the rider or a dock this is A0 done better
   — weight relief and parking for hand work — and nothing more.

## What it contributes

- The best soft carrier in the study for the largest converged family: neutral
  horizontally, near-constant vertically, no moments, low friction. The locating
  chain (rider or dock) then sees only preload.
- Carrier and cable support on one mobile stand. Parking keeps the umbilical's
  shape; the station can leave the bench entirely.
- Real, published capability windows from a product line sold for decades, and
  user reports that name its failure mode (bounce), which is benign here.

## Branches

- **E-P, bench post instead of C-stand.** The arm socket on a post bolted to a
  common plate with the rotator: permanent, no floor, no sandbag, and the stand's
  mobility is lost.
- **E-D, into a dock.** The same carrier delivering the gun onto A2's
  toolchanger dock or one-knob-one-parameter's recipe-cartridge seat: the gimbal
  guarantees the dock is never fought.
- **E-H, hand welding with weight relief.** Without the rider, Derek welds by
  hand with the gun weightless and moment-free. It is the smallest useful step,
  bought next-day, and a baseline for how much a rig adds.

## Unresolved

- Gun + shell + rider mass (sets the spring window and ballast).
- The effective vertical rate and hinge friction of a real arm (hang 2.5 kg,
  push with a luggage scale).
- The yoke-and-trunnion gimbal's clearance around the real gun (scan).
- Whether set-down needs a damper.

---

## Wave 5 — sequence-of-use's critique, and the branches it produces

Source: `exchange/sequence-of-use--on--borrowed-ecosystems-w4.md` (their numbers
in `explorers/sequence-of-use/calc/w4_calcs.py`; their session sketch
`explorers/sequence-of-use/sketches/w4-film-grip-session.svg`). They adopt this
carrier in place of the monitor arm in their own idea, as branch E-f.

### The umbilical sets the lifted gun's attitude, not gravity — agreed

My text said the lifted gun "hangs near its working attitude" with the CG 2–5 mm
below the trunnions. That is 0.9–2 N·mm of restoring torque per degree. The
umbilical pulls at the butt with 1–5 N, 129 mm from the CG on their proxy, or
71 mm from the CG to the cable's line of pull on mine. That is 70–640 N·mm, so
the free gimbal takes whatever attitude the cable gives it. On the rider this
does not matter. At lift-off, carry, park and set-down it does: the gun swings
nozzle-first. This is the same fault I found in their bail in wave 4, and I
missed it in my own gimbal.

### Branch E-s (theirs): carry pins — adopted

Two spring index plungers (M8 pull-ring type) in the yoke lock the gimbal's two
non-vertical axes whenever the gun is off the tube. The heading bearing stays
free. The plunger holes are in a printed indexing ring per recipe. Carried with
the pins in, the gun is a rigid body at the recipe attitude, and set-down is a
translation plus a heading.

**My addition — the moment handover when the pins come out.** While the pins are
in, the cable's torque goes through the pins into the arm. Pulling them on the
rider hands that torque to the rider's contacts:

- 130–640 N·mm over contacts 60–100 mm apart is 1.3–11 N of contact change,
  against 5–10 N of preload;
- at 1 N of cable pull it is harmless; at 5 N a wheel can unload.

Two repairs, both from earlier waves:
- put the saddle at the cable's natural apex, so the pull is low and nearly
  along the grip axis;
- trim the trunnion position by d = τ/W (12–43 mm, a screw slide — the load
  leveler from my wave-4 note on their bail), so the torque is near zero at the
  weld attitude before the pins come out.

With both, the pins carry little and nothing jumps when they are pulled.

### Branch E-p (theirs): a lower CG, 60–100 mm below the pivots — kept as the lighter option

The gun then hangs within 3–5° of plumb under a 1 N pull, but tips 15–26° under
5 N. On the rider it passes 26–43 N·mm per degree of misalignment, i.e.
0.3–0.7 N of contact change. It gives up the moment-free property. It also turns
the yoke into a hanger with its pivots above the housing, which is Derek's
pegboard hook with two pivots. Combined with E-s, pins cover transport and
pendulosity covers the moment after the pins come out.

### Branch E-z (theirs): LAND and WELD hard stops on the rider — adopted

- **What it fixes.** Landing the rider and putting the wire in the corner were
  one event, on a 1–2 Hz spring.
- **The stops.** A barrel-line slide with two cam stops: LAND (the gun ~10 mm
  back along the barrel, the wire tip clear) and WELD (the recipe stop).
- **Where it sits.** In the A1-G chain it goes after the arc (rider → curved Y
  → XYZ → arc → barrel-line slide → shell). A translation along the beam keeps
  the beam through the isocentre, as one-knob-one-parameter's standoff slide
  does.
- **Order.** Land at LAND, Z to WELD, pins out, jog the wire to touch.
  Lift-off reverses it, and the tip leaves up and inward along the barrel (the
  wire-escape rule).

### Tacks and stuck wire — adopted

- **The rider blocks rim-bridge hangers.** Its ±60° rim V-wheels are where a
  rim-bridge plate hanger's feet would run as the table indexes. Their
  stand-hung plate head avoids that: pads inside the tube at 45/150/255°,
  r 40 mm; frame 15 mm above the rim; arm over the −X rim, away from the gun on
  −Y. With the rider seated and pins out, the eight tacks become short trigger
  pulses at indexed table angles.
- **Hand tacks.** If Derek prefers them, the rider comes off the shell stage on
  a small kinematic plate.
- **Stuck wire.** Snip, roll the rider back along the rim, re-seat the tether,
  and re-trim the stickout at a gauge built into the docking cup (with a nozzle
  cap), so PARK always ends with a known stickout.

### Where I differ, slightly

Their lever is 129 mm; mine is 71 mm, measured to the cable's line of pull when
the saddle sits at the natural apex along the grip axis. That halves the torque
but does not change the conclusion: pins or pendulosity are still needed.

### Still uncertain after wave 5

- The real umbilical pull at the butt. It decides between E-p alone, E-s alone,
  or both plus trim.
- Whether the plunger rings and trim slide fit in the yoke around the real gun
  (scan).
- Whether a two-stop barrel-line slide fits inside A1-G's stack without
  lengthening the lever from rider to dot.
