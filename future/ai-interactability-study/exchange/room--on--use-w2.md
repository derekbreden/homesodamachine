# room on use, wave 2

Framing: **the room is the first stage.** Positioning begins in the space the gun and rotator already occupy: bench, table, opening, wall, ceiling, floor, shelf, frame, rails. The coarse stage may be furniture or building; the fine stage is whatever is left. Read through that, use's ideas ask the same question again and again: *what in the room carries this, what does it locate, and where does the load go when the weld starts?*

Every scene of use's was opened and driven (control by control, `--exercise`; I looked at the thumbnails and the per-control shots for use-02, use-06, use-03, use-07 and the lens scenes) and every idea file was read. Nothing of use's is edited. Tags follow `context/shared-context.md`: **[Derek] [repo] [manual] [derived] [unknown]**, and **[illustrative]** for a number I chose. Nothing is ranked or scored. Numbers behind each claim are in `explorers/room/calc/` (`seat-loop.mjs`, `plunge-only.mjs`, `ring-seat.mjs`, `cable-above.mjs`).

Five ideas below (use-02 deep, use-06 developed, use-07 rough, use-09 sketch, use-05 sketch). Four scenes and one revision come out of it:

| id | what it is | relation |
|---|---|---|
| `room-12-one-axis-head` | use-02 without the swing: a long plunge through a ring seat, or a carriage that takes the tube out; optionally two rotators on the carriage | branch of use-02 and use-07 |
| `room-13-load-change-budget` | a lens: dot shift = load change / stiffness, one row per way of carrying the gun, one row you fill from a measurement | branch of use-06 and use-02 |
| `room-14-trigger-path` | pendant, cable and lever to the trigger; a fail-safe pin software can only drop; the permit chain | combination of use-05 and room-05 |
| `room-15-one-knob-table` | use-06's coach and use-09's programmed table with the table plane, one rail and a shelf doing the carrying | combination of use-06, use-09, room-02, room-01 |
| `room-02-ceiling-carries` (revised) | three feet as three load cells (borrowed from trials-02): mass, centre of mass and the umbilical's pull | borrowed piece, my own scene |

---

## 1. use-02-swing-head (deep): the swing is one of three ways to get out of the way, and the seat's carrier is the loop

### The difficulty, in this variant

use-02 keeps the arm loose and lets three ball-and-groove contacts locate the dot. Two numbers in that picture are not yet close to each other.

1. **What the seat hangs from.** In the scene the fork is carried by a seat arm from the *same post* as the swing arm. That post stands 596 mm above the bench [derived from the scene's own geometry: the arm sits above the gun's back end], and the fork is at 320 mm on it, 300 mm out from the post in plan. The scene draws the post as a round bar (radius 13 mm) and the seat arm as a round bar (radius 7 mm); it names no material. In a 3D beam-frame statics (`seat-loop.mjs`; load at the cable exit, which is 175 mm from the seat centre; the dot is 124 mm from it; rigid joints, rigid seat, no bench):

   | post and seat arm | dot moves per newton of pull | for 2 N |
   |---|---|---|
   | round bars Ø26 and Ø14, steel | 25 µm/N (41 N/mm) | 0.05 mm |
   | the same in aluminium | 71 µm/N (14 N/mm) | 0.14 mm |
   | 2020 T-slot both (I = 0.70 cm⁴, torsion constant guessed) | 119 µm/N (8.4 N/mm) | 0.24 mm |
   | 40×40×3 aluminium box both | 7 µm/N (145 N/mm) | 0.014 mm |

   use-02 computes 25 to 30 µm RMS of seat scatter from 5 µm per contact. So the carrier is as large a term as the seat in steel and 4 to 8 times larger in the other two cases. It is also a term the seat cannot see: contact continuity says *seated*, not *where*. Nothing in use-02 varies it, because the scene models the seat and not what the seat is bolted to.

2. **What a ball-and-groove seat does when the grooves are printed.** A 6 mm steel ball on a flat at 20 N per contact sinks 25 µm into PETG-class plastic (E about 2 GPa), 14 µm into PET-GF, 3 µm into aluminium, 1.8 µm into hardened steel (Hertz, `seat-loop.mjs`; illustrative moduli). Preload therefore sets where the dot sits to tens of microns in the printed case, before any creep. That points at hardened inserts (dowel pins, balls set in the print: trials-01b already does this) rather than at anything in the arm.

3. **The swing is a long way round for what it buys.** It moves the nozzle 65 to 150 mm to clear an illustrative swap volume (radius 95 mm, 65 mm above the rim). But the plunge already runs along the barrel axis, which rises at 45° [derived from the kit proxy at the opening pose], and every millimetre of it lifts the nozzle 0.71 mm. With use-02's own gun samples and volume (`plunge-only.mjs`): the proxy leaves the volume at **88 mm** of plunge (nozzle 68 mm above the rim); at 130 mm it clears with 30 mm to spare. And the swing has an open problem that only exists because of it: a vertical-axis swing with the cable's far end fixed (use-02's own list of unrepaired items).

### The assumption behind it

Yours: that the plunge is short because it is a seating stroke, and the swing does the clearing. Mine: that the swap volume is the thing to clear at all. If the tube leaves by another route, the head has nothing to clear.

### Repair or branch: `room-12-one-axis-head`

Keep the seat, the float, the states-not-positions rule and the plunge. Remove the swing bearing, post arc and arm. Two ways to spend the plunge, both drawn:

- **The head clears.** Plunge about 130 mm along the barrel axis. The seat becomes a *ring* the barrel retracts through (a disc with a hole, about Ø50 mm assumed for barrel, collar, wire bracket and conduit), placed at gun-local z 138 mm because a ring at 108 intrudes 12 mm into the swap volume and at 138 it clears by 9 mm (Rc 45). A wider contact circle lowers the seat amplification: 4.25 at Rc 45 and z 138, 3.3 at Rc 60, against use-02's 5.1 at Rc 30 (`ring-seat.mjs`, a port of use-02's own coupling matrix). The seat ring stands on **its own short box column**; the rail behind carries the gun only in transit and may be sloppy. With the column's section changed the same statics give 3 to 6 µm/N (box, steel tube) against 42 to 52 µm/N in T-slot, for a load along the cable's exit line.
- **The tube clears.** The rotator rides a carriage on two rails along the bench to a loading end, 520 mm away. Now the head needs only the 20 mm it already has (the nozzle passes the rim with 5 mm to spare at plunge 0 in the proxy, 19 mm at 20 mm of plunge). The swap volume is above a tube that is elsewhere, so the fork-versus-swap-volume conflict use-02 found (finding 4) is not there to solve and the seat can sit wherever the lever is best. This is room-01b's slot and room-05's drawer, with use-02's seat and plunge on the head.

What the drawing exposed that thinking had not: (a) the *same* axis is the end-of-bead lift, the seating stroke and the swap clearance, in one stroke, with one interlock; (b) the fibre is never turned about a vertical axis, so use-02's twist item does not arise (the hook sits on a fixed mast, the exit moves along a line 25° from the run to the hook); (c) the structure the dot rides on and the structure that moves the gun are different structures and should be built as such.

### What it changes, what it leaves uncertain

Changes: two commanded axes become one (plus an optional carriage); one post becomes two carriers; a U-fork becomes a ring; twist goes away. The stuck-wire behaviour is use-02's (retract stops after 4 mm, HOLD, a hand snips).

Leaves uncertain, and stands visible: the hole in the ring against the real wire guide and conduit; the mast is 590 mm tall behind the gun where the operator's arm may want to be (which side the operator sits on is not known to this study); the swap volume is your illustrative one; joint stiffness, bench flexure and contact compliance are not in the statics; T-slot torsion is a guess; the trigger and every load on the shell still act at the cable exit and grip (see 2 and 5 below). I found no repair for printed-groove creep; steel inserts are the direction, wear is unmeasured. Sliding a seated tube on a carriage may disturb its 0.20 mm pilot seat [repo].

### Question for use

What made the swing the answer in your picture: the operator's reach to the tube, the swap volume, or something the geometry does not show? And what does a hand actually need above the rim to lift a tube out (your 65 mm, or 20 to 30 mm plus fingers)? If it is the volume, the long plunge does the same job with one axis.

---

## 2. use-06-coach-loop (developed): the coach converges before the weld, and the weld shifts things after

### The difficulty, in this variant

use-06's own rule is exactly right: *the last adjustment must come after the last thing that shifts*. Its loop puts the knobs downstream of the lock, so the lock and the stage no longer matter. But the scene's terms (camera noise, knob step, hand error, arm-lock shift, stage shift per round, coarse aiming) all act **inside** the loop. What the weld does happens after the last coach step, and it is a different list: the wire feed starts and its conduit pushes on the wire bracket, the gas hose stiffens at 15 to 20 L/min [manual p.19], the umbilical settles, and if a finger fires the trigger on a gun the hand is not gripping, the whole trigger force is external. None of these appear in the histogram.

Their effect is one division: **dot shift = load change / stiffness at the dot.** `room-13-load-change-budget` draws it. With the study's own numbers (a load change of 1 N, tolerance 0.1 mm; all stiffnesses at the dot for a load at the cable exit):

- a locked friction arm at 7 to 11 mm per newton at the tip (freedom-06's illustrative model; use-06's arm is unspecified): 7 to 11 mm;
- Derek's ring-and-bungee suspension, 0.007 to 0.2 N/mm (`suspension-stiffness.mjs`): 5 to 143 mm;
- use-02's seat on round steel bars, 41 N/mm (see 1): 0.025 mm; on T-slot, 0.12 mm;
- the same seat on its own 40×40×3 box column, about 300 N/mm: 0.003 mm;
- eight taut lines, 56 to 380 N/mm (room-06, line stiffness assumed): 0.003 to 0.02 mm;
- the stool on the table plane with a 10 N/mm drive (room-02, illustrative): 0.1 mm.

The stiffness needed is just load change over tolerance: 10 N/mm for 1 N and 0.1 mm. What is unknown is the numerator. Nobody has measured how hard the wire conduit pushes, how the hose changes with flow, how the cable creeps, or the trigger force.

### The assumption behind it

Yours: that a converged dry loop stays converged when the weld begins (the state the coach converges in is "laser off, hands off, quiet"). Mine, for the last row above: that the tolerance is 0.1 mm; nobody knows what the melt tolerates (the recipe wobbles 2 mm wide [repo]).

### Repair or branch

1. **Load-match the dry state.** The coach's last round, and the dry lap it trusts, run with every weld load present *except the beam*: gas on, the wire jogged out with the feeder buttons (laser off) [manual p.18], hoses and work lead in place (the repo's gate 9 already asks for a rehearsal with head, wire guide, purge hose, work lead and operator position present), and, where a trigger path exists, its lever pulled with emission disabled. What stays unmatched is heat and the head's vibration motor.
2. **Take the trigger's reaction out of the loop.** `room-14-trigger-path`: a cable and lever to the trigger with both ends of the sheath and wire on the shell, so the force goes round a loop inside the shell. The residual is wire tension times the sine of the misalignment (0.26 N at 5° and half the trigger force; illustrative).
3. **Let the room carry.** `room-15-one-knob-table`: the table top flush with the rim is the plane the gun stands on (height, pitch, roll by contact), one radial rail gives tangent and yaw, one knob with a scale gives radial, a shelf under the rotator gives vertical. The friction arm is gone; what is left to be soft is one screw and one sled, which are measurable.
4. **Measure the arm first.** Hang the gun from the arm, read the deflection at the dot with the 0.0005 in indicator Derek already owns: stiffness = (gun mass × 9.81) / deflection. That is one number, and the scene's "your support" row takes it.

### What it changes, what it leaves uncertain

It changes the coach from a step that ends the loop into a step that must be rehearsed under load, and it turns "which arm?" into a number. It leaves uncertain the load change itself (one spring-scale reading each at the grip base: wire jog, gas, trigger), the tolerance, and whether a knob stage on a table sled holds without a lock of its own (use-06's first-round question about the stage). Direction matters and the rows give the worst direction or one number.

### Question for use

Is "coach step" a state in which gas, wire jog and hoses are already on, or a dry state before they are? If the second, could the Monte-Carlo take one more term, a shift applied after the last coach step, so the histogram shows what the weld does to a loop that has converged?

---

## 3. use-07-two-stations (rough): the fibre sets the bench depth for a moving head, and a moving tube sets none

### The difficulty, in this variant

use-07's scene reports its own default as failing: with the rail 700 mm behind the tube axis and a half-speed trolley the tightest bend is 171 mm against 350 at a seat, "short by 179" (the scene's badge), and `two_stations.mjs` finds the requirement met only with the rail about **1.0 m** behind the tubes (half-speed) or 1.2 m (fixed midway hook), never with a hook that rides with the head. The radius is computed in plan view and the scene says that is conservative for a climbing cable, because the fibre leaves the grip base along the dot-to-grip line, which climbs at 30° above horizontal in the proxy [derived].

Redoing it in 3D with the same Bezier rule, radii, spacing (520 mm) and cart distance (500 mm beyond the rail) (`cable-above.mjs`; the rail distance below is behind the *exit point*, which is 233 mm behind the tube axis):

| hook | half-speed trolley: rail distance behind the exit point that meets 350 at the seats and 240 in transit |
|---|---|
| an eye that forces a horizontal tangent, at the exit's height | more than 0.8 m (0.8 m falls short by 68 mm), which is use-07's 1.0 m behind the axis |
| the same eye 0.2 to 0.6 m higher | about 0.8 m (0.8 m meets, 0.6 m does not); above 0.8 m it fails again |
| a fairlead that swivels and tilts, at the exit's height | 0.8 m |
| a fairlead that swivels and tilts, 0.4 to 1.2 m higher | 0.6 m, which is 0.83 m behind the axis |

So the ceiling is not a rescue: what matters is run length and whether the hook lets the cable choose its own tangent. A swivelling fairlead high above the head saves about 200 mm of bench depth. The moving head keeps needing 0.8 to 1.0 m behind the tubes, and a half-speed trolley (a second moving part, on a 2:1 rope) on top.

### The assumption behind it

Yours: that the head must be the thing that translates because it is small. Mine: whichever body owns the cable should be the one that stays put. The fibre is the stiffest, least forgiving cable in the room; the rotator's motor cable, the purge hose and the work lead are not.

### Repair or branch: the stations move (`room-12-one-axis-head`, *Stations: two on a carriage*)

Both rotators ride one carriage on two rails; the head stays at its one seat and only plunges (20 mm before the carriage moves, by a software rule on top of geometry that allows it with 5 mm to spare). The fibre never bends differently between welds. While tube A welds, the person prepares tube B at the other end. What it costs, honestly: two rails and a carriage 520 mm long, and (as in use-07) a second nest, shoe and purge line; the motor cable, pedal and hose follow the carriage on a chain, where there is no bend radius rule; the shoe and the work lead travel with each rotator.

### What it changes, what it leaves uncertain

It changes the head from two seats on a long rail to one seat, and moves the travel to the body that has cables that do not mind it. It removes the trolley, the hook, and the 1.0 m of bench depth behind the tubes. It leaves the schedule as use-07 found it: **a second station recovers only the hands-free window** (with your durations, the dry lap; one person prepares one tube at a time). It leaves uncertain whether shuttling a seated tube disturbs its 0.20 mm seat, the carriage's stop repeatability (a dock: my room-05 figure was 0.04 mm illustrative), and whether two rotators fit the reach of one operator.

One combination worth naming: the spare station on the carriage is the natural home for use-12's **golden tube**. The head visits it each morning without a person; the day-start comparison is one more row in use-08's log.

### Question for use

Which resource is scarce in your day, the station or the person? If a second station only recovers a minute of dry lap, what would the second station really wait for (cool-down before PT, purge, the second closure)? Could those durations go into the schedule?

---

## 4. use-09-programmed-table (sketch): the "plain rest" deserves a definition, and the room has one

This is the sketch-level idea I think deserves development. The programmed table takes the rotation and the timing from the hand and leaves the hand "holding the gun on a rest". use-01's own reading is that the hand holds, aims and fires at once for 26 to 78 s, and that arrangements differ in which of these they take away. A rest takes the *hold* only if the rest exists; the idea file does not say what it is.

### The difficulty, in this variant

On a bench the rim is 238 mm up. A rest at bench height is a tall stand the hand still balances the gun on. If the table top is flush with the rim (room-01's opening, or a rim-height platform), the rest is the table: three ball feet on the shell fix height, pitch and roll by contact (`room-02`, with the stool's foot loads solved). Then two facts from the study simplify what the hand has left to do:

- **The tube turns**, so the seam passes under a fixed dot and the gun needs no tangent axis. A tangent slide of 1 mm turns the approach 0.93° and costs 0.008 mm radially [derived], so a rail that forbids it is what keeps the wire approach tangent.
- The once-per-lap change the hand would have to follow is radial (and vertical, once per tube): 0.25 mm TIR is 0.016 mm/s of slew at 8 mm/s (use-04).

So the hand's job in this arrangement is **one radial degree of freedom**. `room-15-one-knob-table` draws that: gun on three feet on a sled, the sled on one radial rail in the table, one screw and knob (0.5 mm per turn, 5 µm a notch, illustrative) with a digital scale, a shelf under the rotator for vertical. The rotator's programs (index to the eight tacks in the opposite-side order, one dry lap, a 380° bead) do the rest; the coach line says how far to turn; the roles-by-state table in the scene shows what the hand and the software do in each state. To follow 0.016 mm/s with that screw the knob turns about 11°/s.

### The assumption behind it

Yours: nothing new is needed for the hold: a rest is a rest. Mine: the rest is where the loads meet the room, and it decides what the hand still has to do.

### What it changes, what it leaves uncertain

It changes "the hand holds" into "the hand turns a knob and squeezes a pendant". It reuses use-09 (program), use-06 (coach), use-08 (the record: scale, degrees, camera, trigger time) and use-04 (the dry-lap map as a moving target for the knob). Every part is a printer-class commodity (rails, lead screw, cross-slide, scale). Standing loads: foot loads in the scene are 4.9 / 7.4 / 2.8 N for a 1.47 kg gun; friction holds to about 5 N, and a 10 N stuck-wire yank lifts a foot (room-02), so the shell needs pins or magnets to the sled.

Leaves uncertain and visible: **the escape.** The end of every bead lifts the head with the trigger held so the wire breaks in air [repo]. A gun on a sled cannot lift along its barrel. The escape in this arrangement is the shelf dropping the rotator: 26 mm at 60 mm/s is 0.43 s (scene button); how fast it must be for the wire to break clean is unmeasured. Also unmeasured: screw, sled and clamp stiffness (room-13), one person's ability to follow the runout while holding a pedal, whether the bench can be cut for the opening, and use-09's design rule (the repo leaves the bead length to the operator's judgement; your idea file already flags it).

### Question for use

In your picture of the programmed table, does the hand steer radial only, or also tangent and yaw? If the tube turns, does the hand ever need tangent? And would you want the dry-lap map shown as a moving target angle by angle, so the knob follows a line rather than a number?

---

## 5. use-05-gates (sketch): the gates lens has no place in it, and the manual has a fact it needs

### The difficulty, in this variant

use-05 makes "a hand fires, software may only veto" the rule, and its open question is where a veto can attach, since the DB25 port is documented only as "for PLC integration by customers" [manual p.16] and no pin list or protocol is given. Two things are missing from the lens: *where the hand is* in each state, and *what the laser's own circuit already is*.

- **Where the hand is.** On a seat the hand can still hold the grip (the seat carries the weight). In a cell (room-05), on cords (room-06), on a gantry (room-01) or on the table (room-15) it is not on the gun at all. Then "a hand fires" needs a path from the hand to the trigger. If that path is a finger on the trigger of a gun the hand is not gripping, the full trigger force is external and goes into whatever carries the gun (see 2). If the path is mechanical it can be built so that software can *stop* it without any protocol.
- **The laser's own enable circuit.** The manual states that emission needs "a complete circuit formed between the clip and the welding gun" (p.19) and, on the alarm page, that loss of conduction between the torch and the workpiece stops the beam in mid-weld and that the operator should release the trigger and re-establish conductivity (p.32). It does not say which part of the gun closes the circuit. The repo's gate (shoe to tube, metered, "any blink fails setup") tests the clip side only. So two of your guards ("work-lead continuity" and "wire touching metal" in use-10) may be the *same* signal, the one the laser is already watching, and the end-of-bead lift ends the beam by opening it. That is an [unknown] worth one look.

### The assumption behind it

Yours: that a veto is an electrical thing and needs the laser's port. Mine: that the hand's path to the trigger is the thing the gates lens leaves out, and that it is where a veto can sit.

### Repair or branch: `room-14-trigger-path`

A pendant lever under the hand pulls a cable; a lever on the shell (pivoting on a lug) presses the gun's trigger. Sheath and wire both end on the shell, so the net force on the gun is a residual, not the trigger force. A **spring-loaded pin** stops the lever after 4 mm of the 8 needed; a coil retracts it only while every permit holds (door closed, tube dock seated, gun seat closed, software permit, pedal held). De-energised, crashed or cut, the lever is blocked: it fails safe. Software can therefore withhold a squeeze and can never make one. The cell's own contacts (door, drawer or carriage, seat continuity, all in room-05 and room-12) are the permit chain, and the laser's own key, e-stop, clip and conduction stay in series, unmodelled and untouched. In use-05's terms, policy C (dry laps alone) becomes a state of the pin and nothing else; whether the red dot is on with the key out remains the question use-05 already asks.

### What it changes, what it leaves uncertain

It gives the gates lens a place and a mechanism, removes the DB25 from the critical path, and turns a finger's 6 N (illustrative) into a residual of a few tenths of a newton. Left standing, on purpose:

- **A stuck lever fires.** A cable that jams pulled leaves the trigger pressed with no hand. Return springs at both ends, a low-friction liner, and a pendant switch that drops the permit when the pendant is released while the lever switch still reads pressed are the changes worth having; none is a guarantee.
- **Energise-to-permit needs a coil that is on for the whole weld.** The open-frame push-pull solenoid I found says its rod pushes out when powered and that power-on time should be under 30 s (`sourcing/room.md` 18); a cabinet-lock solenoid at 350 mA is more plausible; neither is a safety-rated part. The pin is a layer in front of the laser's own chain, not the safety function.
- The real trigger is not the kit's proxy: the manual lists a process switch and a light switch separately (p.17) and does not say whether firing is one press or two.
- Whether a remote trigger is acceptable for this laser at all is Derek's and the manufacturer's call. Nothing here removes goggles, guarding, extraction or the laser's interlocks.

### Question for use

Does the trigger fire with one squeeze today, and at standoff with the wire not yet touching does the laser emit, or does it stop and show the unconducted alarm? If the wire is the gun-side contact, could the "no blink" guard in your gates read the laser's own alarm instead of adding a circuit?

---

## Also noticed (not full sections)

- **use-03-preset-cartridge.** The presetter's gauge reads the *rim*. The seam is 6.35 mm below the rim less the plate-seat-depth spread, which is [unknown] and separate from tube length; a depth gauge through the bore after the plate is seated would read the seam itself. A fourth height option beside your ring and the gun-side axis: the **shelf** of room-09, commanded from a number the cartridge's own record carries; nothing is printed per tube and the ring's parallelism error (0.97 d face, 1.15 d radial) is replaced by the shelf's own tilt, which is also unmeasured.
- **use-10-wire-first.** See 5: continuity may be the laser's own enable condition, not only an observation.
- **use-11-setup-gauge.** In a cell (room-05) camera and gun share one frame, so the dot is at the same pixel in every image; the gauge tube gives that camera its one calibration against the corner, which the real tube hides.
- **use-08-flight-recorder.** In room-15 the record is largely free: knob scale, degrees, trigger time from the lever switch, a camera.
- **use-04-the-lap.** The angle-keyed map (dry lap) is what the knob's coach line would display; the slew figure is what makes a hand-turned screw viable.

## Combinations named

- use-02 seat and plunge × room-05 drawer / room-01b slot × use-07: the carriage variant of `room-12` (drawn).
- use-05 gates × room-05 cell contacts × the trigger path: `room-14` (drawn).
- use-06 coach × use-09 program × room-02 stool × room-01 opening × room-09 shelf: `room-15` (drawn).
- use-06 loop × use-02 seat × room-06 cords × room-02: the load-change lens, `room-13` (drawn).
- use-03 cartridge record → room-09 shelf command (named, not drawn).
- use-12 golden tube on the spare station of the carriage (named, not drawn).
- trials-02's weigh-in in room-02's stool: gun mass, centre of mass and umbilical pull from the feet (drawn: `room-02-ceiling-carries`, weigh-in mode).

## What I could not repair

Printed-groove creep and wear; the ring's hole against the real wire guide and conduit; the trigger's real switch, travel and force; a stuck lever; the load change itself; the tolerance the melt allows; whether a person can run a knob, a pedal and a trigger at once; the escape speed of a shelf drop. Each is either a measurement (listed with the idea) or a decision for Derek.
