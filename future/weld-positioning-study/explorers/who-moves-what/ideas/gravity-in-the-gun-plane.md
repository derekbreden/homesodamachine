# Gravity in the gun's plane: tilted station, nose in the work's cup, one hanging wire

## Picture it

**The cradle.** The whole station sits on the tilt cradle of
`tilt-cradle-escape-rail.md`, pinned at τ ≈ 32.5–38°. There the gun lies flat
in the vertical plane through the station tangent, and gravity's moment falls
almost entirely on the hole axis. The rotator spins the tube, which is
band-clamped to the turntable (wave 5).

**The nose.** A hanger rides the end plate being welded: port nipples, a centre
pin, stainless wheels (work-as-datum). On it sits a sprung cup whose pads lie on
a sphere centred on the dot. Three balls on the shell's nose sit in the cup, so
the **work** fixes the dot's position and every rotation about the dot stays
free.

**The tail.** Derek's base loop, around a collar on the grip axis at the butt,
hangs from **one vertical wire** to a lead-screw anchor on the cradle's column.
That wire is the hole dial, and gravity tensions it. A 1 kg weight on the loop
sets the tension without loading the cup.

**Yaw and roll.** A pin on the loop in a vertical slot sets yaw. The loop and a
front ring are journals on the grip axis, so roll is nearly weightless and a
friction lock holds it.

**Umbilical and wire.** The umbilical leaves the loop's clamp vertically to a
saddle above, and the wire guide rides the gun.

**What carries, locates and is fixed.** Gravity carries the gun: ~8 N into the
cup and the rest along the wire. The cup, the wire, the slot and the lock locate
it. "Fixed" is the plate being welded, for the dot, and the cradle column, for
the angles.

**Sketch:** `../sketches/s7-gravity-in-the-gun-plane.svg` (true opening pose at
τ = 32.5°, view from +X).

**Major unresolved problems:**
- **The tilted weld process** (see `tilt-cradle-escape-rail.md`, Process and
  wave 5).
- **Tube stability under tilt.** An unclamped first-closure tube tips at
  ≈ 30.5°, and this idea needs 32.5–38° plus ~8 N of cup load on the low side.
  The band clamp and preloaded catch are mandatory here.
- **The real gun's mass and centre of mass**, which set the roll-neutral tilt
  and the ballast.
- **Heat at the nose cup**, ~46 mm from the dot.

## The combination as first written (wave 4)


**A combination across explorers.** The source ideas stay intact in their own
files:

- **work-as-datum:** the plate hanger riding the end plate (port nipples,
  centre pin, stainless wheels) and the **cup whose pads lie on a sphere centred
  on the laser dot**, with sprung outer pads (`work-as-datum/ideas/guided-hand.md`
  H1-p, `work-hung-suspension.md` D4).
- **carry-and-locate:** the same cup as the nose of E-RA, with a tail on the
  room (`carry-and-locate/ideas/switch-lock-skate.md`, `nose-and-tail.md`).
- **one-knob-one-parameter:** the plane rule, that a support is a single knob
  when its line meets the other two rotation axes. Also the hole knob as a
  vertical wire from Derek's base loop, tension-loaded Tr8×2 lead-screw anchors,
  and the walk test (`one-knob-one-parameter/ideas/knob-wired-suspension.md`).
- **sequence-of-use:** trigger closed in the shell (K2), stickout gauge and
  touch-off (K3), umbilical rule (K6).
- **Derek:** his base loop hung on a wire, his loops as roll journals, and his
  third ring.
- **Mine:** the tilt cradle and escape direction
  (`tilt-cradle-escape-rail.md`), and yaw as a sideways move.

It is a weld-process change as well as a positioning one (the tilt); see
`tilt-cradle-escape-rail.md` §Process for what is known and unknown.

Sketch: `../sketches/s7-gravity-in-the-gun-plane.svg`. Numbers:
`../gravity_plane_calcs.py`, `../tilt_calcs.py`. Poses are scene dials at the
opening pose (45 / 30 / −15); gun 1.5 kg at the proxy centre of mass (estimate).

## What the combination does that none of its parts do

Each source idea fights gravity in a different way:
- the cup needs a preload, and a balancer or sprung pads;
- the room-side tail needs three set-and-locked freedoms;
- the wire suspension needs six taut wires, with a margin of 5.9 N;
- Derek's hanging rings roll under the 85 mm centre-of-mass offset.

Tilting the work to **τ\* ≈ 32.5° about the station tangent** puts the gun, its
beam, its grip axis and its centre of mass in **one vertical plane**. Gravity
then acts as follows (`gravity_plane_calcs.py`, 1.5 kg):

| Axis about the dot | Upright (τ = 0) | τ\* = 32.5° | Note |
|---|---:|---:|---|
| vertical (yaw) | 0 | 0 | a vertical force never twists about a vertical axis |
| grip (roll) | 0.77 N·m | **0.13 N·m** | crosses zero near τ ≈ 38° (proxy) |
| hole | 1.88 N·m | 1.30 N·m | normal to the gun's plane |

So **one** of Derek's three angles carries the gun's whole gravity moment, and
the other two are (nearly) weightless. That changes what each borrowed part has
to do:

- The **hole wire** becomes the only loaded support, and gravity tensions it.
  No bungee or preload fight: 6.8 N from the gun alone, and whatever ballast
  adds.
- **Derek's rings** become a genuinely free roll hinge (sequence-of-use's
  objection to D2, 0.41–0.72 N·m upright, drops about 6×). A light friction lock
  holds it.
- **Yaw** needs only a position, not a load path: a pin in a vertical slot.
- The **cup** only has to hold the dot's three translations; every rotation is
  free about the dot. Its seating direction, the corner's escape direction, is
  vertical at τ\*, so the gun **drops in**.

## The arrangement

| Freedom | Support | Loaded? | Knob / rate |
|---|---|---|---|
| dot X, Y, Z | sprung cup, pads on a sphere centred on the dot, on the plate hanger riding the plate being welded | ~8 N up (the gun's own share) | none: follows this plate's runout, tube length and inversion |
| hole angle | **one vertical wire** from Derek's base loop at the grip base to a Tr8×2 lead-screw anchor above | carries the gravity moment: 6.8 N; **16.6 N with 1 kg ballast** | 0.245° per mm of wire; 0.005° per dial division; per recipe |
| yaw | pin on the base loop in a **vertical slot** (constrains X only) | ~0.3 N | slot's X position: 0.245° per mm; per recipe |
| grip roll | the base loop and a front ring are journals concentric with the grip axis; friction lock | 0.13 N·m residual | ring angle, or Derek's third ring on a wire as a fine trim; per recipe |
| wire preload | a hooked 1 kg weight hung from the base loop | adds only to the wire, not to the cup | per session |
| cup preload | optional balancer at the centre of mass | lowers the cup load; ballast restores the wire | per session |
| spin | the existing rotator, tilted on the cradle | — | during the weld |
| tilt | cradle on the station tangent, quadrant and pin | only gravity's direction | per session |

**Why each support is exactly one knob** (one-knob's plane rule, first order):

- The wire meets the grip axis (at the grip base) and is parallel to the vertical
  axis, so it has zero moment about both and sets **hole** only.
- The slot's constraint line runs along X through the grip base: it meets the
  grip axis and is parallel to the hole axis, so it sets **yaw** only.
- The journals are concentric with the grip axis, so they set **roll** only.
- The cup is a ball joint *at the dot*, so no angle change moves the dot. There
  is **no couch** and no re-trim; the dot is this plate's corner.

**Where "fixed" is fixed:**
- The cup, to the plate being welded.
- The wire anchor and the slot, to a column on the tilt cradle (the −Y side
  plate's upper extension, as in `tilt-cradle-escape-rail.md`), with an arm
  reaching over the base loop.
- The cradle's trunnions carry no precision, because work, cup and anchors all
  tilt together.

**Cable.** The umbilical is clamped to the shell at the base loop (K6), and its
free loop leaves that clamp **vertically** to a saddle on the same arm. Its pull
then acts at the wire's own attachment, along the wire, so it behaves exactly
like ± ballast. It changes only the wire tension: never the cup, roll or yaw.

**Trigger.** Closes inside the shell (K2), so no hand load enters the supports.

## A closure, phase by phase

| Phase | What happens |
|---|---|
| Load, tack | Gun lifted and parked on a hook. Tube in, plate at its recess, tacks as today (by hand with the rim spacer; the shell lifts free of everything, nothing to unbolt) |
| Hanger on | Thread the two port nipples; lower the plate hanger; its fork pin drops into its slot (work-as-datum's sequence) |
| Tilt | Cradle to τ\* on its pin (or leave it tilted and load along the tilted axis) |
| Dock | Lower the gun straight down (the escape direction). The nose seats in the cup, the pin enters the slot, the wire comes taut. Pose = wire length + slot position + roll lock |
| Stickout | Jog the wire to touch (K3) |
| Dry run, weld | Pedal, trigger. The only loads are gravity (constant), the cable (constant) and the wire-touch reaction |
| Stuck wire | Snip. The drag goes into the cup's sprung pads and the slot |
| Lift | Straight up: the cup lets go, the wire slackens, the pin rides up the slot. The gun is clear of the tube after 43 mm (`tilt_calcs.py`; 32 of 32 feasible recipes) |

The second closure is the same: the cup rides whichever plate is up, and the
float stays at the far end for τ < 90°.

## Break it, and the repairs

1. **Cable along its natural exit loads the cup sideways.** Left to leave along
   −Y (its exit direction at τ\*), a 5 N umbilical pull puts 4.9 N sideways on
   the cup against only 4.8 N vertical: a plain dome would let the nose ride
   out. *Repair:* (a) the vertical free loop above, which makes the cable ±
   ballast; (b) work-as-datum's **sprung outer pads**, so the cup holds in every
   direction. Both are cheap; do both. *Leaves:* the real cable force.
2. **Wire margin.** Gravity alone gives 6.8 N, and a 5 N upward cable pull
   leaves 1.8 N. *Repair:* 1 kg of ballast at the base loop gives 16.6 N (11.6 N
   with the pull), and 2 kg gives 26.4 N. The cup load stays ~8 N either way,
   because the ballast hangs on the wire's own line. This is one wire needing
   tension, supplied by gravity, where the untilted version needs six held by
   preloads. *Leaves:* the gun's real mass and centre of mass.
3. **Wire attachment point.** Attaching the wire nearer the dot (s = 140–200 mm)
   makes the cup load go negative with ballast: the cup would have to pull the
   nose down. *Rule:* keep the wire at the grip base (s ≈ 279 mm); there the cup
   carries ~8 N up in every case run.
4. **Roll neutrality depends on the real centre of mass.** With the proxy it is
   0.13 N·m at 32.5° and zero near 38°. *Repair and a gift:* the tilt knob finds
   it. Unlock roll, hang the gun, and step τ until the gun no longer turns. That
   measures the plane of the real centre of mass with the real gun, which no
   scan gives. The friction lock takes any residual.
5. **The loose tube carries the cup load at a tilt.** About 8 N, vertical, at
   the station gives ~4 N radially at the rim, roughly 0.6 N·m about the nest
   (estimate), against work-as-datum's 0.9–2.5 N·m rim-lift estimate (upright).
   *Repair:* a balancer at the centre of mass lowers the cup load, and ballast
   at the base loop keeps the wire tension, so the two preloads are set
   independently. The three M3 adjusters are snugged, not just touched. *Leaves:*
   the tube's real resistance at a tilt.
6. **The rotator at τ\*.** Its gravity-seated turntable lifts at roughly 30–40°
   (my estimate), and roll-neutral 38° is at the edge. *Repair:* preload the
   spool catch, run at 32.5° and accept 0.13 N·m on the roll lock, or use a
   positioner built to tilt (`tilt-cradle-escape-rail.md` T-f).
7. **Heat at the nose and cup** (~46 mm from the dot, near the rim). This is
   work-as-datum's open item: metal pads, a light shield, nothing printed within
   the reflected-light cone.
8. **Large recipe changes.** The wire, slot and journals are single knobs to
   first order. Like one-knob's finite moves, the pivot drifts roughly with θ²
   for big steps, but here the pivot is the cup, which is at the dot by
   construction, so the drift is in the angles, not the dot. The tilt itself
   must follow the recipe to keep gravity in the plane: for grip ±15° the plane
   shifts, and roll gravity grows back toward its upright value.
9. **Process change.** The tilt moves the puddle toward 1F (fillet bisector 12.5°
   from vertical). τ = 0 is still available, but at τ = 0 this arrangement loses
   its point: roll carries 0.77 N·m and the wire 7.5 N.

## Parts (representative; see `../../../sourcing/who-moves-what.md`)

- Tr8×2 lead screw with brass nut (single start, self-locking) for the hole
  anchor.
- 1/16 in stainless rope (one-knob's sourcing).
- A hooked 1 kg iron weight as ballast (or any shop steel offcut).
- The plate hanger and cup parts per work-as-datum's sourcing.
- XIKE UCP204 trunnions and the quadrant (tilt idea).
- Printed shell with the base-loop collar, ring journals and the slot pin.

## Contribution / unresolved / assumptions

- **Contribution:**
  - It finds the one attitude at which three of the study's suspension-family
    problems collapse together: the thin wire margin, the rolling rings and the
    cup's preload.
  - Gravity's moment is confined to one axis, so one gravity-tensioned wire,
    one slot and one friction lock replace six preloaded wires or three locked
    tail freedoms.
  - Docking is a straight drop along the escape direction, and the dot lives on
    the plate itself, so there is no couch and no per-tube step.
- **Unresolved:**
  - the real gun's mass and centre of mass (sets τ for zero roll, the ballast and
    the cup load);
  - the tilted weld process (shielding, purge, requalification);
  - the loose tube under the cup load at a tilt;
  - the rotator's tipping angle;
  - heat at the nose.
- **Rests on:** the proxy gun and its centre of mass, a straight proxy wire
  guide, the estimated masses, and the two borrowed cups and hanger working as
  their authors describe.

---

## Wave 5: what the tube-tipping finding means here

one-knob-one-parameter found (on the tilt cradle) that the first-closure tube,
standing unclamped in its nest, tips about its rim at **≈ 30.5°** and slides
from ≈ 17°. This combination sits at τ = 32.5–38°, above that, so for it the
finding is not a refinement but a precondition.

- **The cup makes it worse.** At τ\* the station is ~77 mm outboard (downhill) of
  the tube's tipping edge. The cup's ~8 N adds **≈ 0.6 N·m** of tipping moment,
  about ten times the tube's own margin at that tilt (≈ 0.06 N·m past tipping,
  first closure; my check). **The band clamp to the turntable and the preloaded
  catch are therefore required**, sized for the tube's and turntable's own
  tipping moment plus ~0.6 N·m. A balancer at the centre of mass (repair 5)
  lowers the cup's share, and the ballast keeps the wire tension.
- **What the cup does and does not protect.** The cup rides the plate, so the
  *dot position* follows any residual lean of the tube: a lean cannot move the
  dot off the corner. The *angles* are set from the cradle column, so a lean of δ
  changes the relative angles by δ, which the camera cannot see. The clamp is
  needed for the angles even though the dot is safe. The tilt walk test (two
  inclinometers: shell and rotator base) is the check.
- **The second closure** tips later (≈ 40°), so the roll-neutral 38° is close
  for it too.
- **Their T-b1 stages** have counterparts here in different places:
  - standoff (S) is the cup-to-nose geometry, so a flexure S stage between the
    nose balls and the shell;
  - across-the-corner (A) is the cup's radial position on the hanger, so a
    flexure A stage in the cup's mount.
  - The rail and stop are not needed, because the cup is the stop.
