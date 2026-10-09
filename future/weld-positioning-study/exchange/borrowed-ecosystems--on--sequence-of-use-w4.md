# borrowed-ecosystems on sequence-of-use, wave 4: the monitor-arm session

Subject: `explorers/sequence-of-use/ideas/monitor-arm-session.md` (their idea E).
Numbers: `explorers/borrowed-ecosystems/calcs_wave4.py` §1–5. Corrected opening
pose throughout (grip 45, hole dial 30, vertical −15). New sourcing is in
`sourcing/borrowed-ecosystems.md` (wave 4).

## What their arrangement does that mine lacked

- **It designs the session, not the pose.** Park, hand and dock are three
  states, each with a positive stop, and the arm is never the locator.
  - "Every rest state has a positive stop" dissolves my A0 finding that
    gas-spring arms creep up at light load. The cradle and the dock hold whatever
    the arm does.
  - Hand tacks keep working while the weld pose is stored, which none of my
    arrangements offered.
- **The cradle doubles as the stickout gauge,** and the solenoid only has power
  when the gun is seated, so the trigger interlock follows the dock.
- **The M0 → M1 path** (weight relief first, the same parts then docked) is the
  cheapest learning path in the study.

## 1. The hand-to-dock transition (their biggest open problem, E1/E2)

**Variant.** The main arrangement:
- a CG bail with free pins on the arm's swivel hook;
- the umbilical run to a fixed overhead saddle "about 680 mm above the bench";
- let go only in the cradle or the dock, with a thumb-knob friction brake on the
  bail pins.

**Assumptions behind it.**
- (a) The umbilical's torque is a fixed ~0.65 N·m disturbance, to be braked.
- (b) The saddle belongs at the digest's ~680 mm peak.

**What I found.**
- **(b) is my wave-1 error propagating.** 680 mm was computed at hole dial 65.
  At the true pose the cable is on the grip axis 70 mm out of the butt, at 407 mm
  above the bench and 30° elevation. Hanging free at the 350 mm minimum radius,
  it peaks at ~450 mm (their partner's cable model gives ~416).
- **A saddle at 680 mm forces a bend at the butt.** To reach it the cable must
  first turn *upward* at close to minimum radius: 303 mm of rise over 175 mm.
  The butt then holds a bending moment EI/R of 0.3–1.4 N·m for an umbilical EI
  of 0.1–0.5 N·m² (unknown). That is as large as the whole E1 torque they
  estimated, and it comes from where the saddle is.
- **(a) is partly geometry.** The cable's tension leaves along the grip axis,
  71 mm from the CG proxy, so 2–8 N of tension gives 0.14–0.57 N·m. Unlike the
  bending part, it changes with where the hand holds the gun relative to the
  saddle.

**Repair — the film operator's recipe: balance first, then drag, then a little
friction.**

1. **Put the saddle where the cable wants to go.** Dock the gun, let the
   umbilical hang free, and fix the saddle at its natural apex: roughly
   420–450 mm above the bench, 0.3–0.5 m behind, along the cable's own plan
   direction (≈ −105°). The cable then leaves the butt nearly straight and the
   bending term mostly disappears. The same constant cable shape at every dock
   survives.
2. **Trim instead of brake.** Move the bail pins off the CG by d = τ/W so that
   gravity cancels the residual cable torque at the dock attitude. For 15–25 N
   of gun and 0.3–0.65 N·m that is 12–43 mm, horizontal. Put the pins on a
   lead-screw slide: the automotive engine *load leveler* (a screw moving the
   lift point along a bar) at printed scale. With the offset horizontal, a 20°
   hand tilt leaves only 0.02–0.04 N·m of imbalance. The gun then hangs at the
   dock attitude when let go, so docking needs position, not rotation.
3. **Drag, not a lock, on the pins.** A damping-grease film in the bail-pin
   housing (camera-lens helical grease, ~0.5–1 N·m·s/rad):
   - hand steering at 20°/s feels 0.17–0.35 N·m;
   - the trimmed residual drifts at most a few degrees per second;
   - a light Coulomb friction (~0.1 N·m, one wave washer) holds it still.
   Drag alone cannot hold an untrimmed 0.65 N·m: it drifts at 19–74°/s. That is
   why trim comes first. Fluid heads pair counterbalance with drag for the same
   reason.
4. **Keep their lead-in cones and the 1 mm-short stickout rule (E2).**

**What it leaves uncertain.**
- The umbilical's real EI and tension. A hang test settles both: with the gun
  on a kitchen scale and the cable to the saddle, read the force change and the
  angle.
- Whether one trim holds across the whole HAND range. It is exact only at the
  dock attitude.

## 2. The dock-gated solenoid trigger

**Variant.** The Heschen 12 V push-pull solenoid on the shell works the trigger
presser, powered through two pogo contacts in the dock.

**Assumption.** A solenoid can hold the trigger for the weld.

**Real capability.**
- The weld holds the trigger continuously for ~54 s (one 48.6 s lap at 8 mm/s,
  plus the 20° overlap and start).
- The listing gives 3 N initial force at the 20 mm stroke and 60 N only at
  closure with its shim removed. It also states that the coil heats and is
  unsuitable for prolonged operation without switching off.
- Pull-in slams the plunger into its stop at the first instant of the weld,
  inside the shell that is meant to be quiet.

**Repairs.**
- **A — hobby servo.** A metal-gear MG996R-class servo presses the presser
  slowly (a 0.2–0.5 s ramp) and holds position:
  - 12 kg·cm at 6 V is 47–78 N at a 15–25 mm horn;
  - Deegoo 4-pack, $18.99, 1,346 ratings, 300+ bought per month.
  Gate its *power* through the dock's pogo contacts, so it cannot press
  unseated. Its signal comes from the dock-post button through a small
  controller or a servo tester. This keeps their interlock idea and removes the
  heat and the slam.
- **B — keep the solenoid, drive it hit-and-hold.** Full voltage for ~100 ms,
  then PWM at 25–30%, with a rubber stop against the slam.
- **C — the Bowden lever** they already list: mechanical, silent, no power.

**Leaves:** trigger force and travel (unmeasured), which sets the horn length.

## 3. M2: a pole-mount arm carrying a spring balancer

**Variant.** The collar high (~1.1 m above the bench), the arm a manual SCARA,
the balancer's line holding the bail, "so the line stays nearly vertical
wherever the gun goes."

**Assumption.** The arm's swivels follow the gun freely.

**Real behaviour.** Monitor-arm swivels are friction joints tuned so a monitor
stays where it is pushed. The line must lean until its horizontal pull beats that
friction. For 1–5 N of swivel friction at the tip and a 15–20 N gun, that is:
- a lean of 3–18° before the anchor follows;
- 30–200 mm of offset on a 0.6 m line;
- the same 1–5 N pushing sideways on the gun in the hand;
- a swing back through that offset on release.

This is the trolley's pendulum pull-back, reduced but not removed. The friction
value is an assumption; it is one push-scale test on a real arm.

**Repairs, in order of effort.**
1. Back the swivel tension screws right off, which most arms allow, and measure.
2. Replace the swivel bushings with bearings: a printed hub on 6000-series
   bearings, a simple mod.
3. A carrier whose hinges are bearings by design: my film iso-elastic arm
   (`explorers/borrowed-ecosystems/ideas/e-film-grip-carrier.md`), which also
   drops the balancer.
4. Or keep their rule of letting go only in the cradle or dock. The swing then
   only matters in mid-air.

## 4. Smaller: "tune the arm slightly heavy" (E3/E4)

Real gas-spring arms have a friction band (±4 N was my assumption) and a lift
that changes with height. Owners of the representative arm report that it
creeps to the top and is hard to set at a given height. So the net force at the
dock is anywhere within the friction band of the setting, possibly upward. The
60 N cam latch dominates it, which is fine. In the HAND state every vertical
move starts with a stiction step — acceptable for hand tacks, and the thing an
iso-elastic arm removes.

## 5. Transfers

- **To them.**
  - Saddle at the natural apex.
  - The trim–drag–friction recipe for the bail.
  - A servo trigger gated by the dock.
  - A bearing-hinged carrier for M2.
  - The dial-30 correction to the 680 mm figure, which appears in their
    arrangement and the digest.
- **To me.**
  - My film carrier (E) gains their cradle, their dock-gated trigger and the
    positive-stop rule.
  - Its gimbal yoke should get the same pin trim and drag. A free Steadicam
    gimbal has exactly their E1 problem once an umbilical is attached. Steadicam
    operators fight the same thing with cables hung off the sled.
- **Combined.** Their session design plus a bearing-hinged carrier plus a
  trimmed, damped bail is a hand state that feels like holding nothing and lets
  go without moving. Their M0 then becomes a proper instrument for learning
  what Derek's hand does, and the M3 encoders record it.
