# Cap-Weld Rotation Rig

The fixture that turns the carbonator under a stationary weld head so each closure fillet closes in **one continuous bead**. It serves steps 3 and 5 of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) — the two plate-to-tube pressure welds — and nothing else.

Design intent for the vessel itself lives in [`/hardware/future.md`](/hardware/future.md); the joint and the weld recipe live in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md). This document is the rig: what it has to hit, what could hit it, and which one gets built.

**The rotation is drawn at [`/spin`](https://homesodamachine.com/spin)** — the part turning under a fixed head at the real rate, on the real geometry, with the travel speed and the table RPM tied to each other the way the rig ties them.

## The joint, as the rig sees it

The plate is an ID-fit plug recessed [6.35 mm](RECESS) below the tube end. The bore wall and the plate's outer face meet in an internal corner, and the fillet that fills that corner is a **flat circle on the tube's own axis**:

| | |
|---|---|
| Bead circle diameter (= tube ID) | [123.70 mm](BEAD_D) |
| One lap of bead | [388.61 mm](BEAD_C) |
| Corner depth below the tube end | [6.35 mm](RECESS) |
| Part mass turned, step 3 / step 5 | [1.40 kg](MASS_S3) / [2.01 kg](MASS_S5) |

Everything the rig does follows from those four numbers. A circle means a rotary axis, not a gantry. 388.6 mm at a hand-weld travel speed means the axis runs at **[1.235 RPM](RPM_NOM)** at the nominal [8 mm/s](V_NOM), which is slow enough that most motion hardware is at the wrong end of its range. And 2 kg means torque is never the problem — the whole load is bearing drag.

### Travel speed is the setpoint; RPM is what you dial

The bead sees travel speed, not RPM. `v = ωR` at the bore radius converts:

| Travel | Table | One rev | 360° + 20° | Wire:travel at [12 mm/s](WIRE_NOM) | Fillet leg |
|---|---|---|---|---|---|
| 5 mm/s | [0.772 RPM](RPM_5) | [77.7 s](REV_5) | 82.0 s | 2.40 | [1.48 mm](LEG_5) |
| 6 mm/s | [0.926 RPM](RPM_6) | [64.8 s](REV_6) | 68.4 s | 2.00 | [1.35 mm](LEG_6) |
| **8 mm/s** | **[1.235 RPM](RPM_8)** | **[48.6 s](REV_8)** | **51.3 s** | **1.50** | **[1.17 mm](LEG_8)** |
| 10 mm/s | [1.544 RPM](RPM_10) | [38.9 s](REV_10) | 41.0 s | 1.20 | [1.05 mm](LEG_10) |
| 12 mm/s | [1.853 RPM](RPM_12) | [32.4 s](REV_12) | 34.2 s | 1.00 | [0.96 mm](LEG_12) |
| 15 mm/s | [2.316 RPM](RPM_15) | [25.9 s](REV_15) | 27.3 s | 0.80 | [0.85 mm](LEG_15) |
| 20 mm/s | [3.088 RPM](RPM_20) | [19.4 s](REV_20) | 20.5 s | 0.60 | [0.74 mm](LEG_20) |

The leg column is the second thing the rig hands you. A hand cannot hold a travel speed, so fillet size has been a feel; on a turned part it is arithmetic. Deposit per unit length is the wire's own section ([0.456 mm²](WIRE_AREA) for ER316L .030) times how much wire arrives per mm travelled, and a triangular fillet of that area has legs of √(2A). Wire feed and table speed are two knobs on one number.

**The useful window is [0.77 – 2.32 RPM](RPM_WINDOW)** — 5 to 15 mm/s. That window is the single hardest specification to buy, and it decides the option below.

### Heat, which is not the problem it feels like

At 60 % of the X1 Pro's 700 W, a lap at 8 mm/s is **[52.5 J/mm](HEAT_MM)** and **[20.4 kJ](HEAT_LAP)** total. Spread through the [1.40 kg](MASS_S3) of tube and plate, that is a **[29 K](HEAT_DT)** bulk rise if none of it escapes. A continuous lap does not cook a 0.065" wall; it is an order of magnitude under what the same joint costs in TIG. What continuous heat *does* do is bias the second half of the bead — the metal arriving at 270° is warmer than the metal that arrived at 30° — so penetration drifts across the lap even though the part never gets hot.

That drift is the argument for keeping the eight tacks. It is not an argument against the lap.

## What one continuous motion buys, and what it costs

Buys: one start and one stop instead of sixteen. A fillet of constant leg, because travel speed is constant. Constant torch angle, standoff and wire lead, because none of them are being held by a wrist. Argon that stays over the puddle for the whole bead. A hand free to hold the trigger and watch the puddle instead of aiming. And a recipe that is a number rather than a feel — the line in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 3 stops being *"8-tack opposite-side-bisecting pattern, trail-off motion at end of bead"* and becomes *"eight tacks indexed at 45°, then 380° at [1.235 RPM](RPM_NOM)"*.

Costs: one bad moment ruins 388 mm instead of 48. A wire stick at 200° is a 50-second exposure rather than eight 2-second ones. And a fixed head cannot chase a part that is not running true, which is why half of this document is about runout.

**The lap does not replace the tacks.** Eight tacks first — the rig indexes them — then the lap over the top of them. The tacks hold the plate concentric and square while the bead shrinks around it, and they give the lap a fused place to start.

## What the rig has to hit

| # | Requirement | Why |
|---|---|---|
| R1 | Speed anywhere in [0.77 – 2.32 RPM](RPM_WINDOW), settable and repeatable across 20 welds | The window is the travel-speed window; repeatable because unit 10's weld has to be unit 1's weld |
| R2 | Speed stable to ±3 % through a lap | A 10 % sag at 270° is a 10 % fatter fillet at 270° |
| R3 | Radial runout at the bead circle ≤ 0.25 mm TIR | The wobble is 2 mm wide; the corner has to stay near its centre for the whole lap |
| R4 | Axial (face) runout at the plate's outer face ≤ 0.3 mm TIR | Axial wander is focus wander — the standoff is set once and never touched again |
| R5 | Turns at least 380° without stopping, and stops where told | 360° plus a deliberate overlap onto the start; a crater at 360° is a PT indication |
| R6 | Indexes to 45° stops for the tacks | The eight-tack pattern becomes a program instead of eight guesses |
| R7 | Unbroken electrical continuity from the work lead to the part, turning | The X1 Pro's interlock senses conductance; a rotating part cannot wear the clamp |
| R8 | Head holder rigid in all six degrees of freedom once set | Any droop over 50 s is standoff and angle drift |
| R9 | Head lifts straight up, ~30 mm, in one motion, trigger still held | The Don't-Let-Go exit ([`dont-let-go.md`](/marketing/video/dont-let-go.md)) is how the bead ends without a stuck wire |
| R10 | Nothing structural within ~40 mm of the bead is plastic | The corner is at melting point and the tube conducts |

R3 and R4 are the ones that bite. They are not about the rig's bearing — a $20 turntable bearing runs truer than 0.25 mm — they are about **how the tube is held** and **whether the tube's cut end is square**, because the plate seats to a depth stop referenced off that end. A band-sawn end that is 0.5 mm out of square puts a 0.5 mm axial wave in the weld path, and the fixed head reads that as the focus moving in and out twice per lap. Squaring the tube ends becomes a rig prerequisite in a way it never was for a hand weld.

## The option space

Four families, by what actually moves.

### A — Turn the part, axis vertical

The fillet sits in an upward-facing internal corner, so gravity holds the puddle in the corner it is filling. This is flat-position welding (1F) and it is the reason every option worth taking is in this family.

| Option | What it is | Cost | Speed | Indexes? | Verdict |
|---|---|---|---|---|---|
| **A1** CNC 4th-axis rotary table | 100 mm chuck on a 50:1 worm with a NEMA 23, laid face-up; driven by any stepper driver | ~$240 | Exact, by command, anywhere in the window | Yes, for free | **The pick** |
| **A2** Rotary welding positioner | 10 kg class, 3-jaw chuck, 0–90° tilt, foot pedal — e.g. VEVOR 1–12 RPM | ~$300–500 | Dial, and **1 RPM is its floor** — the bottom third of the window is off the end | No | Turnkey, but the window is the problem |
| **A3** Synchronous rotisserie motor | 4 W AC synchronous, 2–2.4 RPM (CHANCS TYD-50 class), under a lazy-susan bearing and a plate | ~$18 + ~$25 | One speed, but **line-locked** — quartz-stable, better than any PWM dial | No | The afternoon that proves the idea |
| **A4** Machinist's rotary table + gearmotor | 4–6" hand table (72:1 or 90:1 worm), a 100 RPM 12 V gearmotor on the handwheel | ~$150–280 | PWM dial, whole window comfortably | Yes, by graduation, manually | Precise and heavy; the hand-crank fallback is real |
| **A5** Turntable bearing + stepper + gearbox, from parts | 4" lazy-susan ring, NEMA 17/23, 27:1 planetary, driver, ESP32 | ~$150–200 | Exact, by command | Yes | A1 without the worm, and with the runout to chase yourself |
| **A6** Drill press + friction wheel | A rubber wheel on the tube OD off a geared motor | ~$30 | Unstable | No | Proof-of-concept only |

**A2's floor is the whole story of this table.** The commercial positioners are built for pipe-to-flange TIG at 3–10 RPM; ours wants 0.8–2.3, and a 20 W PWM'd DC motor at the very bottom of its dial is exactly where speed stability goes. Two ways out if you want A2 anyway: run the fast half of the window (12–15 mm/s travel, a smaller fillet, more wire feed), or put a 3:1 reduction between the positioner and the fixture plate, which drops it to 0.33–4 RPM and triples the torque. Both work. Neither is as clean as commanding the number.

### B — Turn the part, axis horizontal

Pipe turning rolls, or the part in a headstock. Standard practice for pipe butt welds, wrong here: with the axis horizontal the corner faces sideways at every clock position and the puddle wants to run out of it. It converts a flat fillet into a vertical one for no gain. A lathe headstock has the same problem plus the speed problem — the lowest back-gear speed on a hobby lathe is 40–70 RPM, thirty times too fast.

### C — Turn the head, part fixed

An arm carrying the weld head, swinging on a bearing centred on the tube axis. 380° of umbilical twist is nothing for a 3 m bundle, so the cable is not the objection. The objections are that the head weighs ~1.5 kg on a 62 mm radius with a 45° lean and has to hold R3 and R4 while swinging, and that the part still has to be centred under the arm — so you inherit every centring problem of family A *plus* a moving mass. Commercial orbital heads solve this properly, for tube-to-tube butt joints, at four figures.

### D — Trace the circle with a motion system

Mount the gun on a CNC gantry or a robot arm and run a 123.7 mm circle in G-code. The gun's mass and the umbilical's spring rate are beyond any hobby gantry or arm that costs less than the rotary options, and a gantry that could hold it is a machine tool. The interesting sub-case is that a "CNC 4th axis" sold for this family **is** option A1 — the rotary axis is the cheap part of a CNC, so buy just that.

## The pick

**A1: a 100 mm CNC 4th-axis rotary table, laid face-up, commanded by an ESP32.**

It wins on the requirement that is hardest to buy. Speed is a commanded number rather than a dial position, so R1 and R2 are satisfied by construction and unit 10 gets unit 1's weld. R5 (380° and stop) and R6 (45° index) are two more lines of the same program. The worm's reduction puts the motor at a comfortable step rate — 50:1 with a 1.8° NEMA 23 is 0.036° per full step, and [1.235 RPM](RPM_NOM) is 206 steps/s — and its self-locking mesh holds the part still while the head is set. It costs less than the positioner it beats.

And it lands where the rest of this repo lands: the rig's setpoints become constants in a file, the way `endcap_circular_dxf.py` owns the plate's and `_cold_core_interface.py` owns the core's. The weld recipe stops being prose.

**Prove it with A3 first.** An $18 synchronous motor and a lazy-susan bearing is an afternoon, and it answers the only question that matters before spending: does a continuous lap on this joint beat eight tacks and a fill? At 60 Hz the TYD-50 class runs ~2.4 RPM — [15.5 mm/s](V_TYD) travel, a [0.85 mm](LEG_15) leg at 12 mm/s wire — the fast end of the window, on one fixed speed, with no control at all. If the bead that comes off it is better than a hand bead, buy the 4th axis. If it is not, the $18 is the whole loss.

### What to buy

| Item | For | Note |
|---|---|---|
| CNC 4th-axis rotary, 100 mm chuck, 50:1 worm, NEMA 23 | The rotation | Confirm it is rated to run **face-up** (axial load on the table) and what its actual backlash is. The 100 mm chuck will not grip a 127 mm tube — plan on the fixture plate below, bolted to the chuck face or straight to the rotary's flange |
| Stepper driver (DM542 class) + 24 V supply | Driving it | An ESP32 and a step/dir driver is the whole controller; the firmware tree already exists |
| Laser-cut fixture ring, 316 or mild steel, 3 × M6 tapped at 120° | Holding the tube, R3 | SendCutSend, same path as the end caps. Set screws let the tube be indicated true rather than hoping a bore fits |
| Dial indicator + magnetic base | R3, R4 | **Not optional.** Runout is the rig's failure mode and there is currently no instrument in [`tools.md`](/hardware/ledger/tools.md) that reads it |
| 4040 aluminium extrusion column + brackets | Head holder, R8 | Bolted to the bench, arm reaching over the part's centre |
| Carbon motor brush + holder, or tinned copper braid | Ground, R7 | Rides the rotating fixture plate |
| 1/4" hose barb + fitting for the fixture plate | Back purge, below | Argon into the bore from underneath |
| CHANCS TYD-50 class synchronous motor + 4" lazy-susan bearing | The A3 proof | Only if the proof runs first |

Prices, Prime availability and ASINs get confirmed at order time and land in [`purchases.md`](/hardware/ledger/purchases.md) §16 beside the welder; nothing above is ordered yet.

## The five things around the rotation

The turntable is the easy half. These are the parts that decide whether the bead is any good.

### 1. How the tube is held

The tube stands on the fixture plate with its weld end up: at step 3 that is the future *bottom* end, at step 5 the vessel is inverted and it is the future *top*. Centre it on the **OD with three adjustable screws** and indicate it in, rather than on a fixed counterbore — a fixed bore inherits the tube's OD tolerance and its ovality, and the 0.065" wall will not survive being forced into one. Three screws at 120° in a laser-cut ring, a dial indicator on the OD near the weld, tap it true: R3 in about three minutes per setup, twenty times.

Do not clamp hard. The part weighs [2.01 kg](MASS_S5), nothing is cutting, and the only force is bearing drag — the screws are locating the tube, not gripping it.

### 2. Where the head stands, and why it leans in

**The head must lean inward.** The corner is [6.35 mm](RECESS) down a bore whose own rim stands at the same radius as the corner, so a beam tilted *outward* is cut off by the tube wall the instant it tilts. The only open approach is over the bore: the head sits above the plate, leaning in toward the axis, firing **down and outward** into the corner. At 45° from vertical the beam bisects the corner, the nozzle tip sits about 10 mm above the plate at a radius well inside the rim, and the gun's body rises clear over the tube's centreline. There is no clearance problem in that direction and no approach at all in the other.

The wire leads. The work travels one way under a fixed head, which means the torch travels the other way over the work, and the unwelded metal arrives from the side the bead has not reached yet. The wire guide sits ~15° upstream of the puddle on that side. **Reverse the table and the wire guide moves to the other side** — the two are one setting, not two. [`/spin`](https://homesodamachine.com/spin) draws that coupling: flip the direction button and the wire jumps.

The holder is a column, not an articulated arm. Magnetic-base arms droop, and 50 seconds of droop is 50 seconds of standoff drift.

### 3. The exit

R9 is the one requirement that comes from the machine's own behaviour rather than the joint's. The X1 Pro's retract/patch cycle fires when conductance breaks, so lifting the head straight up with the trigger *still held* snaps the wire clean instead of leaving it fused into a cooling puddle. On a hand weld that is a wrist move. On a rig it has to be designed in: the gun sits in a **cradle**, not a clamp — a 45° V-block it drops into and lifts straight out of, with a magnet or a single strap for retention. Your hand rests on the gun holding the trigger for the whole lap; at 380° you lift it out of the cradle.

That also gives the bead its taper. There is no programmable power ramp to reach for, so the overlap plus the lift *is* the crater fill.

### 4. Ground, turning

The interlock senses conductance and the part is moving, so the work clamp cannot go on the part. A bearing is a bad electrical path — grease, point contact, intermittent. Put a **sprung carbon brush or a strip of tinned copper braid** on the rotating fixture plate and clamp the work lead to that. Prove it with a meter while the table turns before the first weld: continuity must never blink.

(The clamp *can* be left off — [`dont-let-go.md`](/marketing/video/dont-let-go.md) is a record of what the machine does without it. Not for a pressure weld you intend to hydro.)

### 5. Argon, which the rig nearly gives away

A fixed head is a fixed gas cup: the nozzle's own shield sits over the puddle for the whole bead, which is already better coverage than a moving hand achieves. Two more become almost free, and both were previously listed as things to add only if the weld came out black:

- **A trailing shield.** A cup or a length of tube teed off the argon line and clamped to trail the puddle by 15–30 mm. Set once; the puddle comes to it.
- **A back purge, through the fixture.** Put a hose barb in the fixture plate. At step 3, argon fed under the tube fills the bore and vents through the two tapped ports in the plate being welded — heavier than air, so it fills from the bottom and pushes the air up and out. At step 5 the vessel is already closed at the bottom: feed a bottom-plate port, vent the top plate's two. That is a complete purge circuit for the price of one fitting, and it closes the "increase argon coverage or add an internal back-purge" branch in [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 3 before it is ever needed.

One safety note that falls out of the geometry: **the recessed corner is a beam trap.** A beam entering at 45° reflects off the plate face up-and-outward into the bore wall 6.35 mm above it, and off the bore wall down-and-inward onto the plate. Neither specular path leaves the tube. The fixed geometry also means the reflection direction is fixed and known rather than wherever a wrist happened to be — which is the argument for setting the head with the laser off and the part turning dry, every time.

## The setup, per weld

1. Fixture plate on the rotary, tube in, three screws snug.
2. Indicate the tube: **radial ≤ 0.25 mm** at the weld end, **face ≤ 0.3 mm** on the plate's outer face once it is seated. Tap and re-read. A tube end that will not come inside 0.3 mm is a tube end to square, not a weld to attempt.
3. Plate in, seated to its 1/4" recess against the depth stop, per [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 3.
4. Brush on the plate, work lead on the brush, meter it through one dry revolution.
5. Back purge on, ~30 s to sweep the bore.
6. Set the head: 45° lean, standoff, wire guide upstream of the puddle on the *arriving* side. Turn the table one dry revolution and watch the corner stay under the nozzle.
7. Index and fire the eight tacks — 0°, 180°, 90°, 270°, 45°, 225°, 135°, 315°.
8. Return to 0°, which is now a tack. Run **380° at the commanded RPM**, trigger held the whole way.
9. At 380°, lift the head straight out of the cradle with the trigger still held.
10. Purge off. PT per step 6.

## Open items

1. **Does the continuous lap beat the tacked fill?** Unanswered until A3 runs. Everything above assumes it does.
2. **Tube-end squareness.** The band saw's cut is the datum the plate's depth stop reads, and the rig turns any error in it into focus wander. Whether the 10-vessel stock needs facing, lapping, or nothing is unmeasured — measure it before choosing a rig, because a tube that will not come inside R4 wants a different fixture (one that seats the *plate* off the rotary's own datum rather than off the tube end).
3. **Wire feeder ceiling.** The 1.50 wire:travel ratio at 8 mm/s is the current recipe's. Holding that ratio at 15 mm/s needs 22.5 mm/s of feed, and the X1 Pro's maximum feed rate is unrecorded. It bounds the fast half of the window.
4. **Face-up service of a 4th-axis rotary.** These are sold for horizontal mounting on a mill table. Axial load rating, seal orientation and lubrication face-up all want confirming with the vendor before the order.
5. **Whether the tacks are also the rig's.** R6 says index them. It may be better to tack by hand off the rig — a tack is 2 seconds and the part is easier to reach — and use the rig only for the lap. Decide after the first lap, not before.
6. **Distortion, measured.** The eight-tack pattern exists to control it and nothing here has measured it. Indicate the plate's outer face before and after a lap and find out what the bead actually pulls.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_weld_rotation_rig_sync.py`
