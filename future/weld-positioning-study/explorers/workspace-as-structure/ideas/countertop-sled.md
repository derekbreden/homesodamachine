# Countertop sled: the table surface is the positioning stage

## Picture it

- **The plane:** a flat reference plate at rim height around the tube mouth.
  It can be the collar, a granite surface plate beside the mouth, or a deck
  standing on the rotator's own base (the no-cutting branch).
- **The sled:** the gun's fitted shell stands on it on three ball feet.
  - Two buttons on the shell's side bear on a fence along Y: that sets X and
    heading.
  - A stop at the rear sets Y.
  - A light spring pulls the sled into fence and stop.
- **What comes from where:** the plane carries the weight and sets height and
  the two tilts. The fence and stop only locate.
- **Lift-off:** the gun lifts off (tube change, stuck wire) and returns to the
  same pose. It is a 3-2-1 kinematic mount.
- **Cables:** anchored to the plate behind the sled, so the sled only sees a
  slack loop.
- **"Fixed" is fixed to:** the plate.
- **Motorised form:** six stationary actuators move the six contacts.
- **Pusher-gantry branch:** a light gantry sets X/Y through a pin and carries
  no weight.

**Sketch:** `../sketches/countertop-sled.svg`.

**Major unresolved problems:**

- The preload needed against umbilical force, which is unmeasured.
- Dust and spatter under the feet.
- Angles are discrete: printed sled bases.
- Per-tube height still needs a shelf trim or the collar centre.


Sketch: `../sketches/countertop-sled.svg`. Numbers: `../loop_calcs.py` §4.

## The physical idea

Take Derek's "gun tip at countertop height" literally and let the countertop do
the work. A flat reference plate sits at rim height around the tube mouth (the
collar plate, a granite surface plate, or a deck — see branches). The gun's
fitted shell stands on it on **three ball feet**, like a surface gauge on a
surface plate. A plane contact removes exactly three freedoms — height and the
two tilts about horizontal axes — and leaves the three in-plane freedoms free:
X, Y and turning about a vertical axis. So:

- **Height, grip-axis/hole-axis angles:** built into the shell and its feet.
  Three foot screws trim Z and the two tilts.
- **X, Y, heading:** the sled slides on the plate. A **fence** (two contact
  buttons on the sled bearing on a straight bar along Y) sets X and heading; a
  **stop** at the sled's rear sets Y. A light spring pulls the sled into the
  fence and onto the stop.

Three feet + two fence buttons + one stop = six contacts = a kinematic mount
(3-2-1). The sled is located exactly, held by gravity and one spring, and
**can be lifted off and set back to the same pose**.

What makes it different from a gantry: nothing carries the gun's weight except
the plane; the positioning elements (fence, stop) only push against a spring's
preload. They can be light, cheap and far from the gun's weight path.

## Geometry around the actual gun

At the scene's opening pose (grip 45°, hole 30°, vertical −15°), with the plate
top at rim level [Agent proxy]:

- Gun body over the plate on the −Y side of the mouth, 70–200 mm above it;
  grip base ~133 mm above it, ~233 mm along −Y.
- Representative feet (world plan, tube centre at origin, dot at (61.85, 0)):
  F1 (40, −95) under the front of the housing; F2 (40, −260) and F3 (−80, −250)
  behind the grip. Leg heights ~95 mm (front) and ~125 mm (rear) from plate to
  shell. The dot lies ~95 mm beyond F1, outside the triangle; the gun's CG sits
  inside it.
- Fence on the operator's side, x ≈ −112, buttons at y −120 and −280. Stop at
  the rear (y ≈ −300).

Sensitivities (small-motion, from the layout):

| Adjuster, +1 mm | Dot |
|---|---|
| Foot F1 | +1.59 mm height (F2 −0.40, F3 −0.18) |
| Both fence buttons | 1.00 mm across the seam, heading unchanged |
| Front fence button only | 1.75 mm across the seam, heading 0.36° |
| Y stop | heading vs local tangent 0.93°, radial 8 µm |

With 0.5 mm-pitch foot screws and a 0.01 mm micrometer on the fence, Z and X
resolve to ~0.01–0.02 mm at the dot.

## How it is used

- **Setup:** set the sled on the plate against fence and stop; spring engages.
  Watch the reference dot (camera from the +Y side); turn the two fence
  micrometers (X, heading) and the stop (Y = vertical-axis angle) until the dot
  sits in the corner. Trim Z with the three foot screws (or with the rotator
  shelf, if there is one). Record six numbers.
- **Weld:** nothing moves but the tube. The cables are anchored to the plate
  ~150 mm behind the sled with a slack loop, so the sled sees only the loop's
  small stiffness.
- **Tube change from above:** lift the sled off (it's ~2 kg), park it on the
  plate, lift the tube out through the opening as today, drop the next one in,
  set the sled back against fence and stop. The pose returns without
  re-adjustment, to the repeatability of clean ball-on-flat contacts under a
  consistent preload (microns to hundredths, if the contacts are clean).
- **Stuck wire:** the tube drags the wire along ±Y. Toward −Y the stop holds;
  toward +Y the preload holds until exceeded, then the sled slides off the stop
  along the insensitive axis and goes back to it afterward. The breakaway comes
  for free.
- **Lift-off check:** tip the sled up about its rear feet, look, set it back.
- **Second person:** set sled against fence and stop; nothing to adjust unless
  the numbers change.

## Motorizing it: move the contacts, not the sled

Put the six contacts on six small stationary actuators: three lifting pads in
the plate under the feet (the Voron-style three-point Z tilt), two pushers
along X at the fence buttons, one along Y at the stop. The sled carries no
motors or wires beyond the gun's own. For small motions the sled's pose is a
linear function of the six contact positions, so software can compose any small
rotation about the dot — the three scene rotations included — from six
straight-line actuators. Range is a few mm and a few degrees; bigger changes
come from a different printed sled base. This is a 3-2-1 hexapod with each leg
along a principal direction, and it fits the automated-setup vision: six
steppers, two PTZ cameras, the laser dot.

**Decoupled pusher gantry (a branch that keeps Derek's gantry):** a light XY
gantry at countertop height holds a vertical pin that drops into a bushing on
the sled. The pin sets X and Y; the plane carries weight, height and tilt. The
gantry needs no stiffness against the gun's weight or moments — printer-grade
rails and belts are enough — and its sag can't reach the dot.

## Breaking it

1. **Friction vs. cable tug.** Sled weight ~17 N [gun 1.2 kg + shell 0.5 kg,
   assumed]. Unpreloaded, friction holds 1.7–3.3 N (μ 0.1–0.2). A stiff
   umbilical loop can push that hard. Repair: the 3-2-1 preload spring
   (10–20 N) keeps all in-plane contacts closed; anchor the cables to the plate,
   not the sled. The preload must exceed friction too, or moving one fence
   button leaves the sled behind.
2. **Stick-slip.** Moving a fence button slides the three feet on the plate.
   Sub-10 µm moves may jump. Polished steel balls on granite or hardened steel
   slide more evenly than on aluminium; a drop of oil helps. Precision is
   needed only once the sled has settled; recheck the dot after each move.
3. **Dirt and spatter between foot and plate.** A 50 µm grain under F1 is
   80 µm at the dot. The plate is 6 mm above an open weld. Repair: feet on
   small raised pads, wipe before seating, a skirt around the mouth.
4. **Plate choice.**
   - Granite surface plate (Dasqua Grade A 400 × 250 × 70 mm, 0.0029 mm flat,
     $142.54, Prime, observed 2026-09-28): hard, stable, doesn't pit easily,
     non-magnetic, 23 kg, no hole — it sits beside the mouth, not around it,
     so its top must be at rim height (with the rim flush with a bench top, the
     70 mm granite puts its top 70 mm above the rim; the sled's legs shorten by
     70 mm — the front foot nearly touches the housing).
   - MIC-6 collar plate (laser-cut with the opening): flat enough locally,
     soft — steel balls dent it under preload; use hardened pads or ball-on-
     hardened-insert.
   - Mild-steel plate: magnetic, so an on/off switch magnet can clamp the sled
     during a weld (engaging it may shift the sled; the dot check shows it).
5. **Printed legs creep.** PET-GF or PETG legs ~100 mm tall under a steady
   17–30 N creep slowly. Over one weld (~1 min) negligible; over days, the
   recorded foot numbers drift. Repair: metal foot screws in a short printed
   shell, or aluminium legs.
6. **Wobble motor vibration.** Unknown amplitude and frequency (80 Hz wobble
   used). A sled held by gravity and a spring has a rocking mode; if it
   chatters, the preload rises or a switch magnet clamps it.
7. **Angles are discrete.** Large grip/hole angle changes mean a different
   printed sled base under the same shell. Small trims are foot screws, but a
   foot screw tips the sled about a line through two feet, not through the
   dot, so an angle trim also moves the dot and is followed by an X/Z trim.
   Software does that composition in the motorized version; by hand it's two
   steps.
8. **Tube length and cap seat depth** move the dot in Z as in every
   arrangement; the three feet (or the shelf) trim it per tube.

## Branch: the rotator grows a deck (no hole in any bench)

Leave the rotator clamped on the bench as it stands. Stand four legs on the
rotator's own base — at its corners, sharing the four Ø10 bench-clamp holes —
up to a deck plate at rim height (214 mm above the base bottom), with an
opening around the tube. The motor tower (~140 mm) and ground arm (91 mm) sit
below the deck. The sled lives on the deck.

```
            sled on three feet
        ______/  |   \______
  ====deck plate at rim height====     <- reference plane
   ||    | tube  |          ||
   ||    |_______|  motor   ||         legs on the rotator's own base
   ||   [turntable ]  tower ||
  ==========rotator base==========  <- clamped to bench as today
```

The loop becomes sled → deck → four legs → rotator base → ball race → nest →
tube: all inside one module that sits on any bench. Nothing to cut; the
existing top-loading procedure is unchanged; the runout indicator still reaches
the OD below the deck through the gap between legs. The deck can equally carry
Derek's gantry rails. The joint stays ~232 mm above the bench, so the gun is at
chest height rather than countertop height — the ergonomic part of Derek's
table idea is traded for no cutting.

## Contribution

- Separates weight/height/tilt (a plane) from in-plane position (light
  pushers), so each can be simple.
- A removable gun that returns to its pose: tube changes from above and stuck
  wires cost no re-setup.
- A direct route to the automated vision with six stationary actuators and no
  moving cables beyond the gun's.

## Unresolved / rests on

- Gun mass and CG, umbilical stiffness [Unknown] → preload size.
- Contact repeatability in a welding environment (dust, spatter) — untested.
- Which of granite / MIC-6 / steel suits the shop; whether Derek wants the
  deck branch (no cutting) as a first build.

---

## Wave 3 notes (from work-as-datum's exchange)

- **Their suggestion: put the sled's plane on the lid, on the work.** They
  hold back from it themselves, because the lid would then carry the sled's
  weight on the plate seat. I agree.
- **With T-W1 (a centre on the plate, hung from the collar; see
  `table-opening-gantry.md`),** the collar-level plane already sees a corner
  that doesn't move from tube to tube except for face tilt. So the sled stays
  on the collar and keeps its lift-off-and-return.
- **The paddle compass is the sled with two of its three feet moved onto the
  work** (on the dot's radius, with a centre pin and a hold-down) and the third
  on the room plane
  (`../../../exchange/workspace-as-structure--on--work-as-datum.md` §1). The
  3-2-1 mounts form one family; they differ only in which contacts touch the
  work:

  | Contacts on the work | Arrangement |
  |---|---|
  | 0 | sled |
  | 2 + pin | paddle |
  | 3 + pin | compass |

- **Borrowed: the calibration puck.** Cut a second opening in the same collar
  plate, give it its own fence and stop, and seat a tube ring with a real
  plate in it. The sled then moves from rotator to puck for dry runs and
  camera or AI experiments without a tube in the rotator.
