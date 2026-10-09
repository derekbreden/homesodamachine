# room-03: wall port, the gun on a rod through the enclosure lid

**Origin:** swarm (room framing). **Scene:** `scenes/room-03-wall-port` (two orthographic views of one 3D model). **Depth:** worked through several rounds, with numbers.

## Picture it

A laser-safe cabinet, about half a metre tall, with the tube on the rotator in it. The gun is inside too, bolted to the end of a long rod. The rod leaves the cabinet through a ball in the lid and ends outside in a tail a metre long, with two small actuators pushing on it and a counterweight at its end. Slide the plate the ball sits in: the whole rod translates. Push the tail: the gun tilts about the ball and its tip moves half as far as the actuator did. Slide the rod: the tip goes along the barrel axis. Everything electrical is outside the cabinet.

## The proposal

Use the enclosure wall as the pivot and the room outside it as the lever. The dot, the barrel axis, the ball centre and the tail all lie on one line, because the dot is on the barrel axis. Hence:

- **Translation is a plate slide** (u, v in the lid plane) plus **rod insertion** s along the axis: a Cartesian XYZ stage in which one axis is oblique (0.71 mm down and 0.70 mm across per mm).
- **Trim tilt is the tail:** two actuators at distance Lt from the ball tilt the rod. The dot moves ρ = d / Lt of the actuator's travel (0.5 for d = 400 mm and Lt = 800 mm): a reduction.
- **Coarse orientation is set by where the ball sits** on the approach line: a hand-set wedge in the lid. The three rotations of the reference scene become "which wedge" and "how far the ball is".
- **Roll about the rod** is a hand-set lock.

## What carries, what establishes position, what is free and restrained

- **Carries:** the ball and lid carry the gun's weight through the rod (about 18 N total for a 1.5 kg gun with counterweight, illustrative); the tail counterweight balances gravity about the ball (0.17 to 0.54 kg at 800 mm for d = 300 to 500 mm).
- **Establishes position:** the ball centre in the plate (a fixed point) and the plate's slide; the dot is on the line from the tail through the ball.
- **Free / restrained / driven:** driven: plate u, v; rod s; tail pitch, yaw. Restrained: roll about the rod (lock), coarse tilt (wedge). Nothing free.
- **Escape at the end of a bead:** the retract stroke along the axis; the barrel then leaves along the line it entered on (up and back at 45° at the opening pose). About 130 mm of retraction clears the column above the tube (`calc/wall-port-lever.mjs`); allow 150 to 200 mm.

## What software could command, observe, and what stays manual

- **Command:** plate u, v; rod s; tail pitch and yaw; rotator speed. All outside the cabinet.
- **Observe:** cameras inside see the dot and the seam; step counts of five axes; door and lid interlocks. Wave 3 (eyes-14): the outside of the wall is clean air, so **scales or an inclinometer on the lid frame see the ball's play**, a **load cell or motor current at the tail actuators reads the rod's bending moment** (F d / Lt) for a beam model to subtract, and an **IMU on the tail** (dollar class, sourcing 22) reads its tilt. None of these sees the seam; only the camera inside does.
- **Manual:** fitting the wedge; the roll about the rod; loading the tube (rod retracted); snipping a stuck wire with the door open.

## What was tried to break it

1. **"A pivot far away amplifies error."** *Variant:* ball fixed to the lid, tail actuators on the frame. *Assumption:* both the ball's play and the actuators' error are amplified. *Finding:* the ball's play δ reaches the dot as δ(1 + d/Lt) if the tail is held (0.05 mm becomes 0.075 mm at d 400, Lt 800), but actuator travel and compliance are *reduced* by d/Lt. *Change:* mount the actuators on the same plate as the ball; then plate motion moves the tail with the ball and the dot moves exactly the plate's motion. *Leaves:* the ball's stick-slip and real clearance, unmeasured.
2. **The gun is not a rod.** *Assumption:* the pivot can be anywhere on the barrel axis. *Finding:* the gun's housing is 34 mm wide and the grip is 143 mm tall; the ball can only sit behind the housing's back end, so d is at least 269 mm (253 mm + 16 mm nozzle clearance) and in practice at least 300 mm. *Change:* the rod attaches to the back of the housing on the barrel axis; grip and umbilical exit stay inside. *Leaves:* the shell must carry the gun's side loads into that back-end socket; the centre of mass is 23 mm off the axis so gravity also twists the gun about the rod (roll lock).
3. **Cable pulls.** *Assumption:* the umbilical pull acts on the actuators at full size. *Finding:* the grip base sits 47 to 247 mm in front of the ball along the rod and 118 mm off it; 1 N of pull in the worst direction is 0.13 to 0.27 N·m about the ball and 0.16 to 0.34 N at a tail 800 mm out. *Leaves:* the pull is not measured; a stiff wire conduit and gas tube may add more.
4. **Gravity through the ball.** *Finding:* without a counterweight the actuators carry 1.2 to 3.7 N of gravity; with a counterweight of 0.17 to 0.54 kg they carry none. The pivot loads about 18 N. *Leaves (first version):* the rod's stiffness, since it is a long cantilever from the ball. *See item 9.*
5. **Tube swap.** The tube lifts straight up through the space the barrel occupies. *Change:* retract 150 to 200 mm or hinge the lid. *Leaves:* the rod's guide has to hold the ball's plane over the stroke.
6. **Orientation is no longer commanded.** The barrel direction follows from where the ball is relative to the dot; only ±1 to ±3° is trim. *Branch:* a tilt-and-lock ring under the plate for a handful of coarse settings.
7. **Seal.** A ball through a laser-safe lid needs a gaiter or a labyrinth that adds no friction. Not designed.
8. **Sight.** The operator sees the weld only through a camera and an OD-rated window (sourcing 14): a process change.

9. **"The rod bends more than the ball plays" (eyes, wave 2 exchange: `eyes-14-wall-as-window`).** *Variant:* the rod as a beam through the ball, the tail actuators holding the tail point. *Assumption (mine):* with the counterweight the rod carries no load and is a stiff line. *Finding:* the moment F d passes through the ball and bends both segments, and the tangent at the ball tilts. I re-derived eyes's beam model (`calc/rod-under-tilt.mjs`): with F = 1.47 kg x g x sin 45 degrees + 2 N = 12.2 N at the dot end, d 400 mm, Lt 800 mm, a 20 x 2 mm aluminium tube gives tip flex 0.81 mm plus a tilt of 4.07 mrad at the ball: **the dot ends 2.44 mm off the commanded line**, about thirty times the ball's play (0.075 mm at the dot). Rod by rod: 25 x 2 mm 1.18 mm; **38 x 3 mm (the 1-1/2 in tube) 0.22 mm**. The counterweight balances the actuators, not the rod. What a calibration absorbs is the constant part; what stays is the cable's pull: 0.20 mm per newton at OD 20, 0.02 at OD 38. *Change:* (i) the rod is a choice and the first fix is a stiffer rod, not a better ball (the scene's default is 38 x 3; a slider takes it down to 12); (ii) the scene gets a bend panel and a readout, the counterweight includes the rod's own weight, and the outside observers above are listed; (iii) the tail actuators hold a **point** (the tail end at its commanded place), which is what makes the ball's tangent tilt. *Leaves:* the real gun is a rigid body 270 mm long on the rod's end, the cable pulls at the grip, the rod's ends are clamps, the ball sticks and slips; the Prime tubes are short (12 to 13 in) and the only 4 ft round tube of that size seen has a 0.083 in wall, 24 % less stiff than 3 mm (sourcing 25).
10. **Orientation: gravity along the rod (wave 3, from the new direction).** *Finding:* the gravity part of the bend is the gun's weight across the rod. With the tube tipped 30 degrees and the gun in the radial plane (room-17) the barrel, and so the rod, is plumb and the weight goes down the rod; only the centre of mass's 23 mm offset remains as a couple. The same beam: 0.59 mm at 20 x 2 mm and 0.05 mm at 38 x 3 mm, with the cable's 2 N still acting (`calc/rod-under-tilt.mjs`). Tipping alone with the reference gun (32.4 degrees from plumb at best) gives 1.95 mm and 0.18 mm. *Leaves:* a plumb rod through a ceiling ball is named here, not drawn; the wire is then off the gun.

## Branches and combinations

- `room-03b-tilt-and-lock-ring` (not built): coarse orientation by a locking ring instead of a wedge.
- Combination with `room-05-drawer-cell`: the same cabinet; the drawer brings the tube and the ball port replaces the small fine stage.
- **Combination `eyes-14-wall-as-window`** (adopted): outside scales, a tail load cell and a beam model make the wall a window; eyes's scene draws it, this scene now carries the bend panel. Named by eyes and taken as part of the idea: room-03 + an IMU on the tail (eyes-11) and room-03 + room-06's self-calibration (fit the ball's centre and the constant flex together from looks at many poses).
- Transferable to any arrangement: put the actuators on a long lever behind a pivot to reduce their error and their loads.

## Unresolved, questions for Derek

- Ball type, clearance and friction: a spherical plain bearing (30 mm bore units exist; their tilt and clearance were not readable), a printed gimbal on four 608 bearings, or a ball head.
- **What the tail actuator holds** (eyes's question): a point. Whether a real actuator pair holds a point or a tangent is a design choice; holding a point is what the bend panel assumes.
- **Which rod is meant** (eyes's question): a 38 x 3 mm aluminium tube or stiffer, so that the ball's play (0.075 mm at the dot) is not the smaller term.
- Can Derek live without direct sight of the weld? Does the cabinet's 0.5 m height and the tail's 1 m sweep fit anywhere?
- Gun mass, centre of mass, umbilical pull.

## Assumptions

Proxy gun at the opening pose; 45° barrel elevation and 50° plan azimuth at that pose: **[illustrative]** (kit). Mass 1.5 kg, cable pull 2 N, play 0.05 mm, d 300 to 550 mm, Lt 300 to 950 mm: **[illustrative]**. Gun length 253 mm: **[manual]**. Nozzle clearance 16 mm: **[illustrative]**.

## Sourcing pointers

`sourcing/room.md` entries 5 (GE30C spherical plain bearing), 14 (OD6+ window), 12 (2020 extrusion), 15 (Klipper for the five axes).

## Scene

`scenes/room-03-wall-port`
