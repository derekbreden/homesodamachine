# Session kit — pieces every arrangement needs because of the sequence

Not an arrangement of its own. These are the parts and rules that fall out of
walking a session phase by phase (`../sketches/session-states.svg`). A, B, C and D
refer to them.

**At a glance (still current):**

- **K1** holding the plate at its recess. The stand-hung plate head, with pads at
  45° / 150° / 255° at the true pose, allows fixture tacks.
- **K2** trigger paths. The Bowden lever is the main one. A dock-gated actuator
  must still release on power loss.
- **K3** stickout gauge and wire touch-off.
- **K4** overlap pointer beside the puddle.
- **K5** a clear side for the cutters; snip before any motion.
- **K6** the umbilical rule: clamp so the gun-to-clamp span keeps one shape;
  ≥ 350 mm radius; cross hinges in a plane perpendicular to the axis; saddles at the
  cable's natural apex.
- **K7** what gets recorded.
- **K8** the welder's own sequence settings.

The chart `../sketches/session-states.svg` is pose-independent and still accurate.

> **Pose note (wave 3).** Numbers in the wave-1 text below were computed at scene hole **dial 65** (my proxy passed the dial straight into `posePoint`; the scene subtracts 35). Derek's opening pose is dial 30. The corrected numbers and the repaired branches are in the *Wave 3* sections at the end; dial-65 values are kept where they describe that reachable orientation.

## K1. Holding the plate at the recess (phases 3–6)

The end plate is a slip-fit plug (~0.005 in radial slip). Standing vertically, it
falls down the bore unless something holds it 6.35 mm below the rim until it is
tacked. For the first closure it would fall toward the nest; for the second it
lands on the float rod's tip (the rod is deliberately 1 mm short) and cocks.
**Question for Derek:** what holds it at depth today?

**The collision:** a fixed or seated gun has its nozzle ~9 mm above the rim and its
wire down in the corner at the station. Anything that bridges the rim and turns
with the tube crosses the station when the table indexes from one tack to the next.
With eight tacks at opposite-bisecting angles, no placement of two rim feet avoids
the station. This is what forces either a gun retract between tacks or the
hanger below.

**H1 — rim bridge (hand tacks).** A bar across the rim with two 1/4 NPT 316 plugs
threaded a turn or two into the plate's tapped ports (tapped at step 1, before
welding). Feet on the rim set 6.35 mm. Fine when the gun is in the hand; removed
after the tacks. Joywayus 1/4 NPT stainless plugs (Prime, 100+/month) are the
threaded part.

**H2 — stationary swivel hanger (fixture tacks).** The arm is fixed to the frame on
the far (−X) side, reaches over the rim ~50 mm up, and ends in a vertical spindle on
the tube axis turning in a 608 bearing. A fork on the spindle carries the two port
plugs. The plate and tube turn under a stationary arm; nothing crosses the station.

```
   frame (-X side)                               gun (+X side, seated)
   |======== arm, stationary ========o spindle          \
   |                                 |  (608 bearing)    \ barrel
   |                          fork [plug]   [plug]        \
   |   rim ___                  ___|_________|___       ___\__ rim
   |       |  |                |   plate (turns)  |    |  |  . dot
```

In the proxy pose the gun is at x ≈ 40–50 mm at 50 mm above the rim and the lens is
25 mm off axis at ~100 mm up; a spindle shorter than ~80 mm above the rim and an arm
leaving toward −X clear it. Depth reference: a gauge ring touched to the rim while
the spindle height is locked, or a dial set to the measured tube length. It can stay
on through the weld (it holds the plate at the port circle, 19 mm from centre, far
from the 62 mm bead). It turns fixture tacks into eight short trigger pulses at eight
indexed angles — the tack pattern becomes as repeatable as the bead.

**Carrier (for B).** The same two port plugs on a small cross-bar with fold-down
rim feet: it holds the plate at depth at the load position and while the carriage
travels in; H2 picks it up by a centre boss; the feet fold clear of the rim.

## K2. Getting the trigger pressed without pushing the gun (phases 5, 8)

In any fixture, a finger on the gun's trigger pushes the gun through the whole aim
chain. Trigger force and travel are unknown. Ways to close that force loop inside
the shell, or remove it:

- **Bowden lever (keeps the hand in command).** A bicycle brake lever on the lid
  handle or frame; the cable runs to a printed lever on the shell that presses the
  light switch. Both housing ends seat on the shell, so the squeeze reacts inside the
  shell; the gun only sees the housing's bending stiffness. The hand still commands
  the laser, consistent with the rig's rule that the foot pedal never does.
  Shimano brake cable and housing set (Prime, 1K+/month).
- **In-shell solenoid.** A 12 V push-pull solenoid on the shell presses the trigger;
  de-energised it releases. Heschen 60 N / 20 mm (Prime, $19.99) — its force is low
  at the start of stroke (3 N), so it needs a lever arranged to finish the trigger
  near the solenoid's closed end.
- **Two-stage foot switch (for Derek to judge).** Linemaster 636-S Clipper,
  two-stage momentary (Prime, $99.99, only 6 left; Linemaster is a widely
  distributed industrial line): stage 1 = rotation (the ESP32 pedal input), stage 2 =
  the solenoid. The pedal's travel then *enforces* the per-weld order: rotation
  first, then laser; laser off first, then rotation. **This contradicts the current
  rig's explicit rule** ("the foot pedal never commands the laser"); it is listed
  because it encodes the procedure, not as a recommendation.
- **DB25 "PLC integration" port** (manual section 3.3) might take an external start
  and remove all mechanical force. The pinout is not in the pages I had. Question for
  Derek / XLaserlab.

Every option must release on its own (spring return, de-energise). The welder's
E-stop and interlock stay as they are. The process switch (11) on the grip must stay
reachable or be deliberately covered.

## K3. Stickout and touch (phases 0, 7, 10)

After a snip the wire ends wherever the cutters were. In A and B the tip must land
~1 mm short of the corner at the moment the pose seats (A3, B3), so stickout is a
sequence-critical number.

- **Stickout gauge:** a printed cap that slips over the copper nozzle with a stop
  face on the wire's line at the recipe stickout and a slot for the cutter jaws. Jog
  the feeder (manual 3.5: press to advance, press to retract) until the wire meets
  the stop; cut flush in the slot. It lives at the park position (A, C) or is used
  with the carriage out (B).
- **Touch-off:** the welder only emits when gun and work are electrically connected
  through the safety clip circuit (manual 3.6.2; "Unconducted alarm" in chapter 4).
  If the monitoring screen shows that conduction live, a wire touching the corner is
  visible on the welder with no extra wiring — a per-tube zero and a stickout check.
  **Question for Derek:** does the screen show it live?

## K4. Keeping the eyes in one place for the overlap (phase 8)

The procedure stops ~20° past the first tack, judged at the index mark while
watching the puddle — two places to look. A printed pointer on the frame beside the
station, 20° past the dot on the departing side, reading a paint tick on the tube OD
made at the first tack (below the heat band, ~30 mm under the rim) puts both in one
field of view. The console's degrees remain the check.

## K5. Snip window (phase 9)

Keep one side of the station open at rim height (no frame within ~60 mm of the dot
below rim + 40 mm on the +Y or −Y side) so the Knipex 70 11 110 reaches the wire
between wire nozzle and bead. Rule in every arrangement: **snip before any gun,
lid, saddle or carriage motion.**

## K6. Umbilical rule

Clamp umbilical + wire conduit to whatever carries the gun, 300–400 mm from the
grip butt, so the gun-to-clamp section keeps one shape. Beyond the clamp, cross any
hinge in a plane perpendicular to its axis (bend, never twist); ≥ 350 mm radius
wherever it can be emitting, ≥ 240 mm anywhere (manual 3.7).

## K7. What gets recorded, so a second person can repeat it

- **Per session:** welder parameter set, including the sequence settings the manual
  exposes (gas before/after laser, turn-on and off delay, rise and fall time, wire
  feed speed, wire feed delay, pullback length and speed, patch length), wobble,
  graduated-tube reading, stickout, table speed and direction, fine-stage readings.
- **Per tube:** id, measured length, radial and face TIR, closure number, hanger type.
- **Per weld:** degrees at release, stuck wire (yes/no, where), dot-track video from
  the dry run, puddle video, later PT and hydro results.

## K8. The welder is part of the sequence machine

Pullback length/speed after trigger release is the welder's own lever against a
wire freezing in the crater, and the power fall time shapes the crater the wire sits
in. Both are recipe variables for the stuck-wire problem, alongside any fixture.

---

## Wave 3 — corrections at the true opening pose (hole dial 30) and additions

**K1 (H2 and the stand-hung plate head).**

- The clearance sentence above (gun at x ≈ 40–50 mm, 50 mm above the rim; lens 25 mm
  off axis) describes dial 65.
- At dial 30 the barrel crosses the −Y quadrant. It passes 47 mm from the axis in
  plan, at rim + 5…+76 mm.
- Nothing stationary may stand in that sector at those heights. The spindle on the
  axis is clear.
- Pads for the plate-from-P head: **45° / 150° / 255°** at r = 40 mm, frame at
  rim + 15 mm, arm from −X. That gives 38.8 mm centre-line clearance to the barrel
  (`calc/head_w3.py`), and the centre sits 10 mm inside the pad triangle, so the pull
  is stable.
- The wave-2 layout (180° / ±60° at rim + 40) intersects the barrel at this pose.

**K3.** Retracting the wire until its tip clears the rim takes **14 mm** of feeder
retract at dial 30 (8 mm at dial 65), because the wire rises at 38° from the tip.

**K2, one more trigger path (from idea E).** A solenoid on the shell presses the
trigger presser, and its supply runs through two pogo contacts in a dock. It can
only fire when the gun is seated, from a button on the dock post. The gun's own
trigger remains the hand's in every other state. The welder's electrical interlock
is untouched: only its trigger is pressed.
