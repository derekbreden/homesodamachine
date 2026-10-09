# E. Derek's monitor arm, through a whole session — carry, park, dock

Sketch: `../sketches/w3-monitor-arm-session.svg`. Plan to scale for the tube and
the proxy gun at the true opening pose (grip 45, hole dial 30, vertical −15);
updated in wave 5 with the corrected saddle and the operator on −X. Script:
`../calc/arm_svg.py`. Related sketches:
`../sketches/w4-film-grip-session.svg` (carry pins and a two-stop Z, applied to
the film carrier), `../sketches/x2-trolley-parked-carrier.svg` (schematic
one-axis parking).

## Picture it

A gas-spring desk monitor arm (Derek's example) is clamped to the back edge of the
bench. Its head ends in a short drop rod and a swivel hook. The hook carries a
U-bail whose two pins sit in the gun shell at the gun's centre of mass. Those pins
run on a small screw slide that can offset them 12–43 mm to trim out the cable's
torque, and a grease film on them gives light drag. Two spring plungers
("carry pins") can lock the bail at the recipe attitude.

- **Where the gun can be.** The arm moves the gun between three places:
  - a **park cradle** on the back right, which caps the nozzle and holds a
    stickout gauge;
  - **Derek's hand**, where the gun floats weightless for hand tacks;
  - a **dock**, a post rising from the common subplate under the gun body at
    about (−45, −165) mm, carrying three vees, a latch, a rim flag and a Bowden
    trigger lever.
- **What carries.** The arm carries the gun in every state.
- **What locates.** Only the dock locates, and only when the gun is seated and
  latched. The dock's X/Y slides and a printed recipe block hold the pose.
- **Per-tube height.** Taken by the work (screws under the rotator), set against
  the rim flag.
- **Umbilical and wire.** They hang from a fixed saddle at the cable's natural
  apex: ~420–450 mm above the bench, 0.3–0.5 m out along the cable's own
  direction (≈ −105° in plan), so on a stand past the bench's front edge. The
  operator works from −X.
- **What "fixed" is fixed to.** The dock post, the saddle and the rotator share
  the subplate and bench. The arm clamp's position does not matter.

## Major unresolved problems

1. **The hand-to-dock transition.**
   - The cable torque about the CG is 0.14–0.65 N·m (estimate).
   - Trimming the bail cancels it only near the dock attitude; the carry pins fix
     the attitude but need the hand to engage them.
   - It needs a hang test and a real docking trial.
2. **The arm's real friction band and lift curve,** which set the residual on the
   seat. The latch dominates, but the hand feels the stiction.
3. **Where the dock post sits** relative to the rotator's motor and ground towers
   (unknown).
4. **The trigger actuator.** It needs trigger force and travel (unmeasured). The
   Bowden is the main route; the solenoid overheats on a 54 s hold.
5. **The gun's real mass and CG** (a 2 kg arm minimum means ballast either way).

## Derek's example, as he gave it

From "Repeat", listing ideas that "seem stupid at first glance" within the narrow
problem of positioning the gun in XYZ:

> - arms designed to hold monitors in a position on a desk

That is the whole of it: a desk monitor arm holding the gun in a position. His
follow-up guidance (examples-and-history.md) asks what the arm carries, what it
locates, where the reference is, and what else supports or drives the gun, without
requiring an ordinary monitor arm to do every job alone.

**Kept as given:** borrowed-ecosystems developed the arm exactly as proposed
(`../../borrowed-ecosystems/ideas/a0-monitor-arm-holds-gun.md`) and found what it
really is. I build on their findings and credit them here:

- A gas-spring arm has near-zero vertical rate: height is held by friction. Light
  loads creep up. The representative HUANUO arm's reviews report drift to the top.
- Its minimum rated load is 2.0 kg (4.4 lb). Gun + shell is estimated at or below
  that, so it needs ballast.
- Every swivel is vertical and friction-held. The umbilical and wire conduit push it
  with nothing to bring it back. Wobble dither may walk a friction joint (plausible,
  unmeasured).
- Its strengths are weight relief while the hand aims, and parking.
- In `a2-arm-into-kinematic-dock.md` the arm carries and a toolchanger-style
  ball-and-groove dock locates. In `a1` the shell hangs from the arm by a soft hook
  at the centre of mass, so the arm's friction joints cannot push whatever locates.

The original "arm holds the gun in a position" stays true in this arrangement for
every position where precision does not matter: parked, and hovering during hand
tacks. It is not asked to hold the weld pose.

## What it becomes across a session

> *Wave-3 text, kept as written. Two corrections are in the Wave 5 section: the umbilical saddle sits at the cable's natural apex (~420–450 mm), not "about 680 mm", which was a dial-65 figure; and the dock-state trigger is the Bowden lever, with the solenoid replaced by the options there. "Picture it" above describes the current state.*

The sequence has three different needs from whatever holds the gun (my session
chart): **out of the way** (loading, indicating, plate), **weightless and free in
the hand** (hand tacks, today's practice), and **located and still** (dry run,
weld, stuck wire). A monitor arm is naturally the first two. Give the third to a
dock, and let the arm serve all three states without ever being the locator.

### The physical arrangement

- **Arm.** An ordinary gas-spring desk arm (HUANUO class, 2–9 kg) clamped to the
  bench's back edge. Drawn at (40, +360) mm from the tube axis; the reach to the gun
  is ~480 mm. Its links pass ~200 mm above the rim when docked. The head carries a
  short vertical drop rod ending in a swivel hook. Ballast on the head, not the gun,
  brings the load past the 2 kg minimum: gun ~1.0 kg (unknown) + shell 0.3–0.4 +
  bail 0.2 + ballast ~0.4–0.6 kg.
- **The shell hangs from a bail at its centre of mass** (borrowed-ecosystems' hook,
  made into a gimbal). A U-bail pivots on two pins on the shell at the CG, and the
  swivel hook takes the bail.
  - With the CG at the gimbal centre, gravity puts no torque on the gun. The hand
    turns it in any direction with fingertip force.
  - The hook passes only a vertical force, so the arm's friction joints can push
    neither the hand-held gun nor the docked one sideways.
  - Proxy CG at the true pose: (−30, −108) mm in plan, 375 mm above the bench.
- **Park cradle** on the back-right (+X/+Y), about 400 mm above the bench:
  - a printed cup that receives the nozzle (a cap against spatter and knocks);
  - the stickout gauge (session kit K3) built into the cup;
  - a positive stop for the shell.

  The arm's creep, in either direction, is harmless there: the cradle holds.
- **Dock** on a post from the common subplate, outside the loading column: drawn at
  (−45, −165), under the gun body and forward of the grip, top ~80 mm above the rim.
  - Three vees (dowel-pin pairs, ~110 mm ball span) receive three balls on a plate
    on the shell's belly.
  - A cam latch pulls the plate down, ~60 N.
  - The recipe stack sits between post and vees: X/Y slides and a recipe block, in
    who-moves-what's order (lid → X → Y → block), here post → X → Y → block → vees.
  - Per-tube height is taken by the work (who-moves-what's three screws under the
    rotator on one belt), set against a **rim flag** on this same post.
- **Umbilical: a fixed support, not the arm.** The umbilical and wire conduit go from
  the grip base to a fixed overhead saddle about 680 mm above the bench (the digest's
  peak), then to the cart. Because the docked gun is always in the same place, the
  cable between saddle and dock has the **same shape at every dock**, so its pull on
  the seat is one constant. That is the only state where the pull matters. The arm
  carries no cable, so its rating covers the gun alone.
- **Trigger, two ways, never mixed.**
  - *Hand state:* the finger works the gun's own trigger, through a printed presser
    lever that sits over it.
  - *Dock state:* a 12 V solenoid on the shell works the same presser. Its supply
    runs through two pogo contacts in the dock, so it cannot fire unless the gun is
    seated; a button on the dock post commands it.

  Squeezing a button on a post puts no force into the seated shell. The pedal still
  never commands the laser (the rig's rule), unless Derek chooses otherwise.

### States and transitions

| Phase | State | Hands | Eyes | Arm's job |
|---|---|---|---|---|
| 0 open | PARK | trim stickout at the cradle gauge | gauge | hold the shell in the cradle |
| 1–2 load, indicate, height | PARK | tube, adjusters, indicator; work Z knob until the rim touches the flag | indicator, flag | none |
| 3 plate | PARK | rim-bridge hanger H1 on, plate at 6.35 | depth | none |
| 5 tacks (hand) | HAND | lift the gun out; it floats; tack at 8 indexed angles, trigger in hand | puddle, console degrees | carry weight; follow the hand |
| 6 hanger off, index to tack 1 | HAND or PARK | remove H1 | index | — |
| 7 dock + dry run | DOCK | lower onto the vees (chamfers guide), flip latch, jog wire to touch | seated LED, dot vs corner | float the residual weight only |
| 8 weld | DOCK | pedal, dock-post button (or Bowden lever) | puddle + 20° pointer | none |
| 9 stuck wire | DOCK | pedal off, snip | wire | none |
| 10 gun away | HAND → PARK | unlatch, lift, carry to cradle, re-trim stickout | gauge | carry |
| 11 unload / invert | PARK | tube | — | none |

Fixture tacks remain possible (dock first, then tack with the stand-hung plate head of
the exchange file), but the arm's reason to exist here is that **hand tacks keep
working** while the weld pose is stored. That is what my lid (A) and still-gun (B)
could not offer.

## Trying to break it

**E1 — the gimbal is free, and the umbilical is not balanced.** The CG hook cancels
gravity, but the umbilical pulls at the grip base, 129 mm from the CG (proxy). At
5 N that is ~0.65 N·m. When Derek lets go in the HAND state, the gun rotates to the
cable's equilibrium, nozzle first, possibly into the tube. *Repair:* a friction
brake on the bail pins (a thumb knob) for "let go and stay"; and a rule that the
gun is let go only in the cradle or the dock. *Leaves:* the real cable torque.

**E2 — docking needs the orientation to be nearly right.** The vees capture only a
few millimetres and a few degrees. With a free gimbal, the hand must bring the
shell within that. *Repair:* printed lead-in cones around each vee, and a
"pre-dock" funnel. The shell's plate slides in along the approach path, which has
to match the wire-escape rule reversed: down and outward toward the corner, the
last millimetre vertical. Set stickout ~1 mm short so the wire tip arrives above
the corner, not in it (session kit K3, lid A3).

**E3 — the arm's residual on the seat.** Docked, the arm pushes up or down with its
imbalance ±friction. A1 assumed a ±4 N friction band. Against a 60 N latch plus the
gun's own weight, that is under 10% of preload and constant in direction. Only a
vertical force reaches the seat (hook). *Leaves:* the real friction band of a real
arm, which is one kitchen-scale test.

**E4 — minimum load and creep.** Tune the arm slightly heavy (net 2–5 N down). The
HAND state then feels like holding a very light tool. The cradle and dock take the
net force; nothing drifts up into the operator's face. borrowed-ecosystems'
creep-up finding becomes irrelevant, because every rest state has a positive stop.

**E5 — the dock post and the tube's exit.** A post at (−45, −165) blocks a tube
leaving toward −Y (the operator). With the gun parked, the tube leaves toward −X,
or straight up and then out. *Leaves:* where the motor and ground towers really are
(unknown; they may take −X).

**E6 — the arm near a class-4 beam.** In the HAND state the beam points wherever
the hand points, exactly as today; the arm changes nothing there. In the DOCK state
the beam is fixed and the operator's hands are on the post, not the gun.

**E7 — stuck wire.** HAND: as today, and the arm yields rather than bending the
wire. DOCK: the latch holds against the pull while the pedal is released (the
digest's ~140 N capability of the rotator is the reason to release first). Snip,
unlatch, lift. Magnets instead of a cam latch would make a breakaway (A2's idea),
but the gun would then be dragged on the arm instead of held.

**E8 — twist.** Swinging the arm 90–120° between dock and cradle rotates the gun in
plan. The umbilical, hung from a fixed saddle, takes that as bend and some twist
over its free span. The manual forbids twisting. *Repair:* a swivel at the saddle
so the hanging span can turn instead of twist, and put the cradle so the park swing
is small (≤60°) and in the direction the cable already bends. *Leaves:* the real
exit direction from the scan.

**E9 — a second person.** The states are physical and visible: gun in the cradle,
gun in the hand, gun in the dock (seated LED). Numbers per tube: tube length (work
Z dial, or just "touch the flag") and stickout (the cradle gauge makes it a
physical stop). The recipe is the block ID and two slide readings, written on the
post. The arm itself stores nothing and needs to store nothing.

**E10 — second closure.** The same dock, the same height (the rim returns to the
flag). The purge hose goes down the Ø90 passage, away from the arm.

## Branches

- **M2 — Derek's two examples joined.** A pole-mount arm with its collar high
  (~1.1 m above the bench) acts as a manual SCARA: stiff in Z, free in X/Y. It
  carries a spring tool balancer whose line holds the same bail at the CG. That is
  Derek's "hook on a wire", with the wire's anchor riding on his monitor arm, so the
  line stays nearly vertical wherever the gun goes: no pendulum pull-back (my wave-2
  trolley was the one-axis version of this). The balancer's 0.5–1.5 kg class fits the
  gun without ballast. The gas spring and its 2 kg minimum disappear.
- **M3 — record the hand.** AS5600 magnetic encoders (Prime, a few dollars each) on
  the arm's joints log where the hook was during hand tacks. That is
  machine-that-learns' teach-arm idea, used as a record of Derek's hand practice
  before it is replaced. Orientation would need an encoder on the bail pins and hook
  swivel, or a camera.
- **M0 — weight relief only** (borrowed-ecosystems' strongest role for A0): the arm
  and bail with no dock at all. Derek welds by hand as now, without holding the
  weight. It is the smallest step, it keeps his skill in the loop, and the same
  parts go on to M1.

## Parts that matter (see `../../../sourcing/sequence-of-use.md`)

- Gas-spring or mechanical-spring desk arm, 2–9 kg: HUANUO FlowLift (borrowed-
  ecosystems, $35.99, 4K+/month) or FlowLift Pro MechaSpring ($29.99, 4K+/month,
  observed; same 4.4–19.8 lb range, so still ballast).
- QWORK spring balancer 1.1–3.3 lb for M2 (already recorded).
- Heschen 12 V push-pull solenoid (recorded) for the dock-state trigger.
- Dock: 1/2 in balls, 6 × 30 stainless dowel pins, toggle or cam latch (recorded).
- AS5600 modules for M3 (HiLetgo 2-pack, Prime, $7.99, observed).
- Printed: shell with bail pins and ball plate, bail, cradle with gauge, dock
  lead-in cones, presser lever.

## Contribution, open problems, assumptions

**Contribution:** Derek's arm becomes the thing that makes the sequence work.
Loading space, hand tacks and parking come from the arm; precision comes only from
the dock, and only when docked. A CG bail gives the arm a way to carry the gun that
serves all three states. Pairing it with a fixed umbilical support makes the one
state that needs constant cable force get it automatically.

**Biggest open problem:** E1/E2, the free gimbal against the unbalanced umbilical,
in the moment between hand and dock. It needs the real cable torque and a real
docking trial.

**Other open problems:** real gun mass and CG; the arm's friction band; dock-post
placement against the rotator's towers.

**Assumptions:** proxy geometry at dial 30; masses; operator at −Y; cart on −X.

---

## Wave 4 — branches from the exchange with borrowed-ecosystems

- **E-f, film-grip carrier in place of the monitor arm.** borrowed-ecosystems' idea E
  (`../../borrowed-ecosystems/ideas/e-film-grip-carrier.md`) is an iso-elastic
  stabiliser arm on a C-stand, with a yoke gimbal at the CG and the umbilical saddle
  on the same stand.
  - It gives ~0 horizontal return and passes no moments, which removes E3 and E4
    (the friction band and creep).
  - Parking by rolling the stand moves the cable saddle with the gun.
  - The dock, cradle, pogo-contact trigger and plate head stay as above.
- **E1 repaired by carry pins, not a friction brake.** Two M8 pull-ring spring
  plungers lock the bail or gimbal's non-vertical axes at the recipe attitude
  whenever the gun is off the dock. They come out after seating.
  - The reason: a free gimbal's attitude is set by the umbilical, 130–640 N·mm at
    the 129 mm cable-exit lever (`../calc/w4_calcs.py`), not by gravity.
  - A printed indexing ring per recipe carries the plunger holes.
- **HAND state becomes the teaching state of idea F** (`teach-record-replay.md`).
  The same carrier, with pins out, records the pose that the dock later replays.

---

## Wave 5 — borrowed-ecosystems' critique, and what changed

Source: `exchange/borrowed-ecosystems--on--sequence-of-use-w4.md`.

**1. The saddle height was stale (accepted).** "About 680 mm above the bench" was
the digest's wave-1 figure, computed at hole dial 65. At the true pose the cable
leaves the butt on the grip axis at ~407 mm and 30° elevation, and hangs free to a
peak of ~420–450 mm. A saddle at 680 mm forces an upward bend at the butt that
holds 0.3–1.4 N·m against the gun, for an umbilical stiffness EI of 0.1–0.5 N·m²
(unknown). That is as large as the whole E1 torque.

*Changed:* the saddle goes at the natural apex, 0.3–0.5 m out along ≈ −105°. The
"same cable shape at every dock" rule is unchanged.

*New consequence (mine):* at the true pose that places the saddle **past the
bench's front edge, on the −Y side**, on a stand. The −Y side belongs to the cable,
so the operator works from −X and the tube leaves toward −X. The sketch is updated.

**2. Trim, then drag, then a little friction on the bail (accepted, as E1-t).**

- **Trim:** offset the bail pins by d = τ/W (12–43 mm for 15–25 N and
  0.3–0.65 N·m) on a load-leveller screw, so gravity cancels the cable torque at the
  dock attitude.
- **Drag:** helical damping grease on the pins (~0.5–1 N·m·s/rad) filters tremor.
- **Friction:** ~0.1 N·m of Coulomb friction (a wave washer) holds the trimmed
  residual still.

*How it sits with my carry pins (wave 4):* the two are complementary, and I keep
both.

- Trim and drag shape the HAND state's feel: it lets go without moving, near the
  dock attitude.
- The carry pins are a *state*. Pushed in, they make the attitude exact at any
  recipe (a printed indexing ring), whatever the cable does; they are for carrying
  into the dock and for park.

*One disagreement of emphasis:* trim is exact at one attitude and one cable
geometry, and the cable torque changes with where the hand holds the gun. So I
would not rely on trim alone for docking. Pins in for the last approach; trim and
drag for everything the hand does before that.

**3. Trigger (accepted, with a safety note of my own).** The Heschen solenoid's
listing warns the coil heats and is unsuitable for prolonged operation. The weld
holds ~54 s, and pull-in slams. Their options were a hobby servo, hit-and-hold, or
my Bowden.

- *Main:* the **Bowden lever on the dock post**. It is mechanical and silent, and
  it releases when the hand does.
- *Servo branch — power loss is not a release:* an unpowered metal-gear servo can
  stay where it stopped, holding the trigger pressed. If a servo is used, mount it
  **on the dock post**, pushing the presser through a contact pad, so taking the gun
  off the dock physically frees the trigger. Also add a hardware timeout relay on
  its power.
- *Hit-and-hold solenoid:* keeps the spring return on power loss, which the servo
  lacks. That makes it the fail-safe electrical option.

**4. M2's friction swivels (accepted).** Monitor-arm swivels are friction joints,
so the balancer line leans 3–18° (30–200 mm on a 0.6 m line) before the anchor
follows. The hand feels 1–5 N sideways, and the gun swings back on release.

*Changed:* M2 needs bearing hinges (back off the tension screws, or a printed hub
on 6000-series bearings), or it becomes E-f, the film-grip iso-elastic arm, which
has bearing hinges by design.

**5. "Tune slightly heavy" (accepted as stated).** The net force at the dock is
anywhere inside the arm's friction band, and the 60 N latch dominates it. In the
HAND state each vertical move starts with a stiction step. That is acceptable for
tacks, and it is what E-f removes.

**What stays uncertain:** the umbilical's EI and tension (a kitchen-scale hang
test), whether one trim holds over the hand's working range, the arm's friction
band, and trigger force and travel.

**What they built from this:**
`explorers/borrowed-ecosystems/ideas/f-hand-steered-isocentre.md` takes this file's
HAND state (weightless, positive stops) onto joints through the dot. It adds
balance, drag, a disc-brake lock and encoders, so the hand steers angles without
moving the dot. It is the isocentric cousin of my idea F's R2 (guided hand).
