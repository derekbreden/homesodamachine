# A1 — The arm carries, the tube locates (tube-riding rider)

## Picture it

**How it stands after waves 2–3.** The gun sits in its scan-fitted shell. The
shell is fixed through a small stage stack to a printed **rider** that hugs the
tube's working end from outside:
- two wheels on the OD straddle the dot at ±30°, 25 mm below it, for radial
  position;
- a lower OD wheel stops tilt about the local tangent;
- two V-groove wheels on the rim edge at ±60° set height.

**What moves.** The tube turns under the rider; the rider stays put. It is held
along the tangent only by a soft tether whose magnetic breakaway is wired into
the pedal line.

**Carrying and locating.** The gun's weight hangs from a monitor arm (or spring
balancers, or E's film arm) through a soft spring on a line through its CG. The
carrier carries; the tube locates. The umbilical has its own saddle at its
natural apex behind. For the dot, "fixed" is the tube's own working end; bench,
arm, nest and rotator are outside the locating chain.

**Branches.**
- **A1-G:** one-knob-one-parameter's isocentric rider — an XYZ stage, then an
  arc or bought goniometer about the dot, with the wire on the stage.
- **A1-Y:** a curved Y slide concentric with the tube.
- **A1-B:** Derek's suspension, located.
- **A1-Z:** a pole-mount "SCARA" carrier.
- The wave-1 original (rim V-wheels ahead at −30/−60°) is kept below.

It **grew from Derek's monitor-arm and suspension examples.**

**Sketches.**
- `../sketches/a1-arm-carries-tube-locates.svg` (true pose, revised rider).
- A1-G: `../../one-knob-one-parameter/sketches/a1g-isocentric-rider.svg`.
- The rider under the film carrier: `../sketches/e-film-grip-carrier.svg`.

**Major unresolved problems.**
- The rider follows what it touches: rim and OD shape versus the corner
  (ovality, lip distortion near the overlap, the seam bead).
- Departing-side contacts run on warm metal.
- Angles are only explorable with A1-G.
- The breakaway changes the pedal circuit (Derek's call).

Sketch: `../sketches/a1-arm-carries-tube-locates.svg` (section + plan, drawn at
the corrected opening pose). Grew out of A0 (`a0-monitor-arm-holds-gun.md`),
which stays as proposed. Numbers from `../calcs.py` and `../geometry.py`.

**Wave-2 correction.** My wave-1 geometry passed the scene's hole *dial* value
straight into the pose math; `main.js` subtracts 35°. At the true opening pose
(grip 45, hole dial 30, vertical −15) the barrel is at 45° elevation, the gun
lies back over the arriving (−Y) side, the grip base is ~140 mm above the dot
and ~233 mm back, and the wire crosses the arriving-side rim low, between −15°
and −30°. The wave-1 rim stations are kept below as the original; the arrangement
now leads with the straddle rider that survives the correction.

## The physical idea

Split the monitor arm's job from the locating job, and give the locating job to
the one thing that always knows where the corner is: the tube itself.

- The scan-fitted shell is fixed, through a small fine-XYZ stage, to a
  **rider**: a printed yoke with metal axle posts that hugs the tube **outside
  and below the rim**, where nothing of the gun, wire or beam goes.
- The **weight** of gun + shell goes into a gas-spring monitor arm (or overhead
  spring balancers) through a **single soft hook**: a spring or bungee of
  0.3–0.5 N/mm on a vertical line through the gun's CG. This is Derek's pegboard
  loop on a wire, carried by his monitor arm.
- The **umbilical** has its own fixed saddle behind the station (the cable
  leaves the butt heading −Y at ~30°; apex ~450 mm above the bench, ~0.5–0.8 m
  back), not on the arm and not on the rider.
- The **tangential** position — the one freedom the rider leaves open — is held
  by a soft tether with a magnetic breakaway.

## Contacts and freedoms (reference for "fixed": the tube's working end)

| Contact | Where (tube frame; tube turns CCW from above, −θ is the cold arriving side) | Constrains |
|---|---|---|
| OD wheel, axle vertical | θ = −30°, 25 mm below the dot | radial |
| OD wheel, axle vertical | θ = +30°, 25 mm below the dot | radial (with −30°: radial position and yaw) |
| OD roll wheel, axle vertical | θ = 0°, 60 mm below the dot | tilt about the local tangent |
| V-wheel on the rim edge | θ = −60° | height |
| V-wheel on the rim edge | θ = +60° | height (with −60°: height and pitch) |
| Tether (bungee + magnet) | to a post on the +Y side | tangential position, softly |

Six contact points, five independent constraints from the tube (the two OD pairs
share yaw and radial), one soft constraint from the bench. The rider holds the
gun's pose in the tube's local frame — the frame the scene's angles are defined
in.

**Clearances at the corrected pose** (`geometry.py`): a rim wheel at −30° would
sit 4 mm from the wire, at −45° 12 mm, at −60° 21 mm; on the departing side
+30° is 28 mm and +60° 57 mm clear. The OD wheels 25 mm below the dot are below
everything of the gun. The bracket from the yoke to the shell rises outside the
OD at θ ≈ −75° to the lens-drawer / housing-front region (the drawer sits just
outside the rim at θ ≈ −86°, ~90 mm above the dot).

**Preload.** The arm is set slightly under-balanced so the hook leaves a net
5–10 N down on the rider; the OD wheels need an inward load, which a light
spring clip pinching the wall (an inboard pad on the lip, far ahead of the
wire) or a preload mass hung outboard supplies. On a 90° V riding a square edge,
a radial load lifts the wheel by an equal amount, so the rim V-wheels are used
only for height here and carry no radial load. Rolling drag at 10 N ≈ 0.05 N.

**Why a hook and not the VESA plate.** The arm's head joints are friction joints;
bolted to the shell they would pass moments and stick-slip into the rider. A
single spring on a line through the CG passes only a vertical force. With
k = 0.5 N/mm, following ±0.15 mm of runout changes that force by 0.07 N; the arm's
friction band (assumed ±4 N) can stick anywhere within 8 mm of travel before the
rider notices. The CG proxy now sits ~150 mm from the rider in plan, so nearly
all the weight goes to the hook and the rider only locates.

## How well it follows (calcs.py §2; once-per-rev runout at the procedure limits)

| Contacts | Radial (0.25 TIR) | Height (0.30 TIR) | Ovality leakage |
|---|---|---|---|
| No following | ≤0.125 | ≤0.15 | — |
| Symmetric OD pair ±30° (radial) | 0.017 | — | 0.5× |
| Symmetric rim pair ±60° (height) | — | 0.075 | 1.5× |
| Original: rim ahead at −30/−60° | 0.033 | 0.040 | 1.8× |
| Rim ahead at −45/−75° (clear of wire) | 0.062 | 0.074 | 1.8× |

The ±60° height pair halves the unfollowed height error but amplifies a
twice-per-rev shape; if the rim is oval, leaving height to the carrier (a
pole-mount arm is stiff in Z, free in X/Y) may be better. A clean track below
the plate — work-as-datum's stock 5 in band clamp (`lip-collar-track.md`) — would
give height without touching the rim at all.

## Running it, phase by phase

- **Setup (once per recipe).** Tube in the nest, plate tacked. Float the gun
  over, lower the rider onto the tube. With the guide beam on, bring the dot onto
  the corner with the fine XYZ stage, then lock. Angles are baked into the
  rider/shell interface (printed wedges); changing a recipe angle is a swap.
- **Dry run.** Pedal one lap with the guide beam on and a camera on the dot. The
  dot should stay on the corner through the tube's runout; the dry run tests the
  rider directly.
- **Weld.** Trigger through a lever in the shell pulled by a Bowden cable.
  The +30° OD wheel runs 25 mm below the fresh weld, ~4 s after the puddle; the
  +60° rim wheel ~8 s after, on a lip that is warm (estimated 100–200 °C,
  unmeasured). Steel bearings, metal posts; printed parts kept ≥20 mm off.
- **Overlap.** The −30/−60° contacts ride over the start of the bead in the last
  ~20–40°: warm and possibly distorted at the lip, followed during the overlap.
- **Lift-off.** The arm lifts the rider off.
- **Stuck wire.** The tube drags wire, gun and rider along the rim; nothing
  bends. At ~5–10 N the magnetic tether separates and opens a normally-closed
  switch in series with the pedal contact (the firmware already stops on an open
  pedal contact). *A change to the pedal circuit; a proposal, not an edit.*
- **Tube change.** Lift, swing away (the monitor arm's best trick). The next
  tube's own OD and rim relocate the gun, so reseating and indicating error drop
  out of the dot position — and so does tube length (±3.2 mm cut tolerance),
  which the digest shows moves a room-referenced dot ~0.6–1 mm per mm.
- **Inverted second closure.** Same geometry at the working end.
- **Second person.** Drop the rider on, check the dot, weld.

## The original (wave 1), kept

Two V-groove bearings (624-size) riding the rim edge ahead of the puddle at −30°
and −60°, one OD wheel for roll, everything on the cold side. It is simpler (no
departing-side contact) and has the best extrapolation of the ahead-only
layouts. At the corrected pose its −30° station sits 4 mm from the wire, and
ahead-only layouts extrapolate ovality by 1.8×. It would return if the wire
approach changes (for example a wire guide from +Y) or if ovality proves
negligible.

## Branches

**A1-B — Derek's suspension, located.** Two overhead spring balancers
(0.5–1.5 kg each): one on the CG hook, one on the umbilical saddle. The
balancer cable is a pendulum (≈0.03–0.05 N/mm sideways for 0.4–0.8 m of cable
at 2 kg), so it only carries weight; the rider locates.

**A1-Z — pole-mount "SCARA" carrier.** Z locked on a pole collar, X/Y free on
the arm's vertical swivels; the rider supplies radial only (OD pair), height
comes from the collar. Useful if the rim turns out oval.

## Parts (see `../../sourcing/borrowed-ecosystems.md`)

Monitor arm ($36, 4K+/month) or two balancers ($17 a pair); V-groove 624
bearings ($10 for 20) for the rim; 608-class wheels for the OD; shoulder bolts;
extension spring or shock cord; magnets and a reed or micro switch; optional
40 mm XYZ stage. Printed: rider yoke, shell with trigger lever, CG hook lug,
umbilical saddle (R ≥ 350 mm).

## Contribution

A locator whose reference is the joint's own geometry: runout, reseating, tube
length, the nest and the bench drop out of the dot position. Derek's two
"stupid" examples co-operate: the monitor arm carries and parks, the loop on a
spring couples without fighting, the tube locates.

## Major unresolved problems

- Rim/OD vs corner: ovality, lip distortion near the overlap, the seam bead.
- Angles are baked in; exploring them needs wedges or arcs about the dot in the
  rider–shell joint (see the exchange with one-knob-one-parameter).
- Departing-side wheels on warm metal; heat creep of printed parts nearby.
- Pedal-circuit breakaway is a rotator wiring change.

## Needs Derek's observation

1. Bore/OD runout and ovality at the rim vs at the plate level on a tacked assembly.
2. Rim movement near the start after one lap; rim temperature 45–60° behind.
3. The tube's seam bead at the rim edge and on the OD.
4. Gun + shell mass and CG; trigger force.

---

## Wave 3 — objections from one-knob-one-parameter, and the branches they produce

Source: `exchange/one-knob-one-parameter--on--borrowed-ecosystems.md` (written
against my wave-1 text and its dial-65 geometry; the station clearances there are
superseded by the wave-2 revision above, the rest stands). Numbers:
`../calcs_wave3.py`.

### "A wedge swap pivots about its seat, not the dot" — agreed

A seat 100–200 mm from the dot moves the dot 3.5–7 mm per 2° and 8.7–17.5 mm per
5°. With wedges as the only angle mechanism, every angle change is a part swap
plus a three-screw re-trim, and the wire (on the gun) moves 6.5–8.7 mm per 5° too.
The assumption was that angles are recipe constants that rarely change. That is
true for production and false for learning, which is what the station is for.
Wedges stay, but only as coarse recipe angles.

### Branch A1-G (partner's): the isocentric rider — adopted, with a bought arc

Their chain on the rider: **rider → XYZ micrometer stage → { wire-guide mount ;
work-angle arc centred on the seam tangent through the dot → shell → gun }**.
XYZ then changes only the dot's place (the beam and wire move together), the arc
turns the gun about the dot without moving the wire, and the wire has its own
micrometers. Their arc is printed, R 70, in the plane 40 mm behind the dot, and
clears the gun by 47–65 mm at the real pose.

My ecosystem's contribution is **a bought optics goniometer as that arc**. A
goniometer stage is exactly an arc slide whose rotation centre sits a fixed
height above its top.

- **Representative part.** Huanyu 65 × 65 mm manual goniometer: ±10°, central
  worm drive, dovetail, 8 kg load, 0.1° scale and 0.05° minimum adjustment,
  $299, Prime, 4 ratings. The goniometer *pattern* is standard (60/65 mm stages
  from several sellers); the listing does not publish its centre height, which
  must be measured.
- **Layout.** A printed wedge sets the coarse work angle; the goniometer sits on
  it with its rotation centre on the seam tangent through the dot and gives ±10°
  of fine work angle about the dot.
- **Calibration.** The centre is found by the walk test (sweep ±10°, camera on
  the dot) and shimmed. A centre 0.5 mm off walks the dot 0.09 mm over 10°; 1 mm
  off walks it 0.17 mm.
- **A second angle.** A second goniometer stacked at 90° with the same centre
  height (the optics practice for two-axis tilt about one point) gives a second
  angle about the dot.
- **Loads.** They are only disturbances if the weight is carried at the CG
  (hook, or E's gimbal). An 8 kg-rated stage is far inside its rating.
- **What it leaves uncertain.** Whether a ±10° fine range around printed coarse
  wedges is enough for exploration. The partner's printed arc gives 0–60° at
  lower stiffness and resolution; both belong in the branch.

**Where the wire lives.** Putting the wire guide on the XYZ carriage separates
the conduit from the umbilical, which Derek wants kept together. That is the
price of "arc moves don't move the wire". The alternative is the scene's choice:
the wire on the gun, rolling with it, with the wire micrometers re-set after an
arc move. Both are listed. With the guide off the gun, the interlock needs a
jumper from guide to gun body (the manual's conduction check).

**Stations.** They proposed moving the rim stations to −40/−70° (worst error
0.052/0.062 mm). The wave-2 revision instead put the radial contacts on the OD
*below* the rim at ±30° (0.017 mm, clear of the wire and barrel), with rim
wheels only for height at ±60°. The A1-G arc sits above the dot's height, so it
does not meet the OD wheels 25 mm below.

### Branch A1-Y: a curved Y slide concentric with the tube — agreed

A straight Y screw on the rider is two parameters: 0.93° of vertical angle per
mm, plus s²/2R off the corner. Because the rider already references the tube's
OD, a printed arc slide on the rider concentric with the tube axis is accurate
to print tolerance. It is then an exact vertical-angle knob, with the dot kept on
the corner. Chain: rider → curved Y → XYZ → arc(s) → gun. The rider's own
position along the rim is irrelevant (the joint is symmetric), so the tether
stays soft.

### Still unresolved after the exchange

- Rim/OD vs corner shape (ovality, lip distortion near the overlap).
- The heat budget of printed arcs 30 mm outside an OD that is hot during the
  overlap.
- Whether the nozzle and wire guide collide at the fine-arc extremes (needs the
  scan).
