# borrowed-01-ring-pivots: turn about the dot with nothing on the axis

Origin: swarm (framing: mass-produced products already do this). Maturity: worked deeply. Scene: `scenes/borrowed-01-ring-pivots/index.html`. Companion analysis: `borrowed-04-axis-map`.

## Picture it

A short stack of three bearing rings around the corner. A small ring sits just above the tube rim with the gun's barrel passing through it; a bigger ring stands outside the tube wall like the altitude bearing of a telescope; a third ring sits at the base of the grip where the cable leaves. Each ring turns about an empty axis that passes through the laser dot, so the gun tips and turns about the dot while the dot stays on the seam. A post from the bench carries all of it, and a small stage under the post nudges the whole frame.

## The proposal

Photo pano heads, gimbals and goniometers assume free air around their pivot; the dot is on a corner of metal (the 1.65 mm wall meets the endcap's top face), so a shaft on any axis through it starts inside metal on one side (see borrowed-04). A Dobsonian telescope solves the same shape of problem with big arcs and rings that turn about a point where nothing is: no shaft on the axis. So: one ring per rotation of the reference gun. Yaw ring (vertical axis) above the rim, with the barrel in its bore. Trunnion ring (the level hole axis) outside the wall. Roll ring (the line from the dot to the cable exit) at the grip base. Ring drives are belts, friction wheels or worm gears on printed rings; rings can be the printed 165 mm ball race the rotator already uses ([repo] `hardware/assembly/weld-rotation-rig.md`) or lazy-susan style bearings (sourcing/borrowed.md).

## What carries the loads, what establishes position, what is free, restrained, driven

- Load path: gun, then roll ring rotor (a collar on the grip), roll ring stator, rod A2, trunnion rotor, trunnion stator, rod A1, yaw rotor, yaw stator, frame arm (or an overhead arm with a strut), post, lift block, slab, bench.
- Position: the three ring axes meet at the dot by construction, so the three rotations leave the dot fixed. Where that point sits relative to the seam is set by where the frame was placed (by hand, once per setup), then trimmed by the two-axis stage under the frame, sized by runout and tube-to-tube variation, not by the rings.
- Driven: three ring angles, two trim axes. Free: nothing intentionally free; the gun rides in the roll rotor. Restrained: the yaw range (by the frame route), the hole range (by the barrel reaching the yaw ring and by the tube), the roll range (barrel reaching the yaw ring).
- Not solved: weight about the ring axes.

## Software: command, observe, manual

- Could command: yaw, hole and roll ring angles; trim radial and vertical; rotator speed (existing).
- Could observe: ring encoder angles (encoder type not chosen; AS5600-class modules and hollow-shaft gimbal motors with them are on Prime, sourcing/borrowed.md); the dot against the seam only through a camera, which the scene shows blocked at some azimuths. The scene's "Let software null the camera's estimate" button shows a fixed camera bias turning into a fixed bead offset.
- Stays manual or unresolved: placing the frame so the axes meet at the dot; aligning ring axes to meet at one point; laying the umbilical; balancing the gun about the rings.

## What was tried to break it

1. **Shafts on the axes (pano head, gimbal).** Conflict: the yaw axis lies on the wall face for the first 6.35 mm above the dot; the hole axis lies on the endcap face and its far half runs into the plate; only the roll axis has free air and there its shaft coincides with the umbilical. Assumption: the donor head has free air around its pivot. Change: none possible with a shaft; a needle-thin cantilever is the limit. Numbers (calc/free_directions.py, geometry from the repo dimensions, shaft starts 12 mm from the dot, runs 150 mm): the share of directions where a one-sided shaft fits is 64 % at 2 mm radius, 38 % at 5 mm, 1.6 % at 10 mm; a shaft through the dot fits in 38 %, 12 % and 0 % of directions respectively. Left uncertain: nothing about the geometry; the real gun's thickness near the nozzle.
2. **Rings, frame arm at ring height.** Conflict: the arm from the post passes through the trunnion ring's bore and the ring swings into it as yaw grows: collision-free yaw at the opening pose is -37 to +37 degrees. Assumption: the load path can reach the yaw ring at ring height. Change: a second frame route (overhead arm, strut down inside the swept ring) gives -89 to +89 at default sizes. Uncertain: it collapses back to +-39 with a trunnion ring at distance 120, radius 105; all ranges are from the scene's own contact tests on drawn geometry, not a structural check.
3. **The yaw bore.** Conflict: the barrel is not concentric with the yaw ring; it swings inside it, so hole and roll are limited by the barrel reaching the ring. At bore radius 62 the hole dial cannot go below 18 degrees or roll above 71; at radius 100, 12 and 79, but the overhead strut then sits outside the trunnion ring's minimum reach and yaw falls to +-25; moving the trunnion ring outward runs it into the post. Assumption: ring size can be chosen for one range without the others. Change: none found that gives wide yaw, low hole and high roll together. Uncertain: whether the needed ranges are as wide as the scene's sliders (they have never been specified; the encoded-arm scene is a way to record them).
4. **Continuity.** A slider jump across a blocked band is not a motion. The scene checks the straight path in dial space between the last valid pose and the new one and holds the last valid pose with a LIMIT badge if the path touches anything.
5. **The fibre.** Conflict: the umbilical leaves along the roll axis, so a roll turns the cable about its own axis; manual p. 20 says twisting is strictly forbidden [manual]. Assumption: the cable's twist tolerance is zero. Change: none drawn; options are a swivel nobody has, roll set once by hand and locked, or a roll ring that lets the fibre exit off the axis. Uncertain: the real tolerance per metre.
6. **Setup accuracy.** Conflict: three axes meet at one point only as accurately as the frame is placed. A frame error puts the dot off the seam at every pose. Change: the trim stage plus a camera, which nulls the camera's estimate, bias included. Uncertain: whether any camera sees the dot in the corner well enough (eyes and datum explorers).
7. **Weight.** Not repaired. The gun's centre of mass is 150 to 250 mm from the dot [derived from the proxy; unknown for the real gun]; a mass m at 0.2 m from an axis needs m x 9.81 x 0.2 N m: 2.4 N m for a 1.2 kg gun (illustrative mass). Counterweights on the free side would sit inside the tube; springs or drive torque remain. Left standing.

## Branches and combinations

- Same scene: pivot type radio (shafts on the axes vs rings); frame route radio (arm at ring height vs overhead arm with a strut).
- borrowed-04-axis-map: the analysis behind round 1 and the case for rings.
- Combines with borrowed-05-guide-star (calibrate the trim stage against a camera) and borrowed-03-encoded-arm (record the hole, roll and yaw ranges a hand actually uses, before sizing rings).
- Contrast with borrowed-02-gimbal-on-gantry: that one gives up rotating about the dot and lets a gantry cancel the swing.

## Unresolved problems and questions that need Derek

- How the three axes are made to meet at one point to a fraction of a millimetre (printed race, three-ball contact, indicator alignment).
- Roll ring placement and how the cable leaves without a twist.
- Ring drives, holding torque, counterweights.
- Questions for Derek: the gun's mass and where it balances on a finger; the range of hole, roll and yaw angles he actually uses when welding these tubes by hand; the twist the fibre visibly tolerates.

## Assumptions

- Gun proxy: 253 x 143 x 34 mm envelope [manual p. 17]; three-rotation dial model, 60 degree pitch, 16 mm clearance, opening pose 45 / 30 / -15 [repo scene, illustrative].
- Tube and endcap dimensions [repo]. Ring radii, distances, rod radii, post position, slider ranges: illustrative.
- Contact tests sample points on the drawn proxy against drawn rings, rods and the analytic tube [derived].
- Camera estimate bias 0.3 / -0.2 mm: made up. Runout limits 0.25 / 0.30 mm TIR [repo].
- The gun's mass, centre of mass, umbilical pull, fibre twist tolerance: [unknown].

## Sourcing pointers

sourcing/borrowed.md: 12 in lazy susan bearings (Prime, $12.99 to $22.99, next-day to two-day, thousands of ratings; bore and runout unchecked); hollow-shaft 2804 gimbal motor kit with AS5600 (Prime, $34.88); AS5600 modules (Prime, $7.99 for three).

## Scene

`borrowed-01-ring-pivots`

## Wave 2

- **A hexapod removes the axis problem in software.** Three bearing rings whose axes must meet within a fraction of a millimetre (open thread: how) are replaced in `borrowed-13-hexapod-pivot` by a centre of rotation that is a coordinate; the price is a cage of six legs, a gap for the gun's body, and a calibration of the pivot to the dot (trials-13). In that scene a 10 degree tilt about the dot leaves the dot at 0.00 / 0.00 / 0.00 mm with the legs moving by up to 5.5 mm (ring 18 mm above the dot).
