# freedom-01b: seat, not loop (a ball collar in a cone at the nose, tail on a bridle)

Scene: `scenes/freedom-01b-nose-seat`. Origin: branch of freedom-01 (Derek's rings). Depth: developed (four break-and-repair entries). Numbers from `calc/11-nose.cjs`, `14-nose-gain.cjs`, `17-nose-checks.cjs`, `18-nose-liftoff.cjs`, `19-nose-threshold.cjs`; parameters **illustrative**.

## Picture it

Near the nozzle the shell carries a small sphere (a collar). Under it a cup ring with a conical bore catches the sphere the way a cup holder catches a cup: gravity and a light spring hold it down, nothing holds it sideways except the cone. The cup rides on three small axes. At the tail, a light spreader bar carries two lugs a hand-span either side of the grip base, each on its own wire, and a bungee pair pulls sideways. Three axes place the dot; three lines at the far end tilt the gun about the sphere.

## The proposal

Keep Derek's loop idea but change the contact at the tip from a loop to a **seat**: three translations of the collar centre fixed by weight and preload (unilateral: it can lift out), all three rotations free. The pivot is now the collar, 30 to 130 mm from the dot instead of 279 mm at the grip base. The original loop at the tip stays as freedom-01. The tail loop becomes a **bridle**: two vertical wires to lugs on a spreader bar (pitch and roll) and a horizontal bungee pair perpendicular to the barrel's plan direction (yaw). With the seat's three constraints that is six, and each of the six mostly acts along one motion: **exact constraint** rather than a loop-and-hope.

## What carries the loads, what establishes position, what is free or restrained

- **Weight**: the seat carries about 10 N of the 11.8 N (default), the tail wires the moment about the collar (0.7 and 4.4 N).
- **Position of the dot**: the cup, through the collar. Actuators at the cup move the dot about 1:1 (gain 1.06 to 1.35 depending on the collar station; a translation of the cup rotates the gun about the tail a little, hence more than 1).
- **Orientation**: the tail lines. A tilt about the collar moves the tail (279 − ℓ) mm for every ℓ mm the dot moves.
- **Free**: rotations about the collar until the tail lines hold them; the seat is unilateral, so any pull up and out is unrestrained.
- **Driven**: nose stage X, Y, Z (small linear axes), tail wire A and B lengths (two winches), one bungee anchor (yaw).
- **When constraints change**: engage by lowering the collar into the seat, retract by lifting the cup: that is also the tube swap.

## What software could command, observe, and what stays manual

- **Command**: six axes (three at the nose, two winches, one anchor).
- **Observe**: seat load by a cell under the cup (does the collar sit, how much sideways load is it taking: the seat's sideways capacity is vertical load × cot(half-angle)); wire tension; the dot by camera. The scene builds the **actuator table** a software loop would learn by nudging each axis: at collar station 70 mm, nose X/Y/Z → dot 1.2 mm per mm in its own direction, tail pitch → 0.34 mm per mm in total.
- **Manual or unresolved**: dropping the collar in; fitting the spreader; routing the cable.

## What was tried to break it

**Entry 1. Two ball joints leave a hinge.**
- Conflict: a seat at the nose plus a single tail point is two ball joints in line; the gun rolls about the seat-tail line until its COM hangs beneath it. With the illustrative COM 35 to 60 mm off that line, lugs 40 to 60 mm either side let the gun settle at a different equilibrium about 100° away; from 90 mm each side it holds within 0.3° (`calc/17-nose-checks.cjs`).
- Assumption: that a tail support at the grip base holds roll. It holds only what its lever allows.
- Change: a spreader bar whose lugs are 90 to 200 mm each side (a bar of about 200 to 400 mm over the tube). Alternatives: a counterweight (freedom-01), a keyed collar.
- Leaves uncertain: the bar's size and clearance over the tube; the real COM.

**Entry 2. The seat is unilateral; the cable pulls it out.**
- Conflict: a pull along the cable exit (up and back) pushes the collar sideways up the cone wall. With a 40° half-angle and no preload it climbs out at about **6.7 N**; 3 N of preload raises that to 8.7, 6 N to 10.4, 12 N to 14.4. A steeper 30° cone: 8.1 → 18.1 N over the same preloads; a shallower 55° cone: 4.6 → 8.9 N (`calc/19-nose-threshold.cjs`). A straight-down pull cannot lift it.
- Assumption: that gravity alone holds a seat. It holds against sideways loads up to (vertical load × cot half-angle).
- Change: a preload spring pulling the collar down, a steeper cone, and a cable route that pulls down rather than back.
- Leaves uncertain: the real umbilical pull (unknown), and how much preload the tail and the arm tolerate.

**Entry 3. Where the cup can physically be.**
- Conflict: a collar 16 mm behind the nozzle puts the cone apex 4 mm above the plate face and inside the bore. From about 60 mm the cup sits over the rim (apex 35 mm above the plate at 60, 71 mm at 110); the collar is then 76 to 126 mm from the dot (`calc/17-nose-checks.cjs`).
- Assumption: a pivot 16 mm from the dot is available. The tube is in the way.
- Change: put the collar 60 to 110 mm back; the lever ratio is then (279 − ℓ) / ℓ = 2.9 : 1 at 70 mm behind.
- Leaves uncertain: whether the cup and its stalk clear the wire guide, the beam and the tube rim.

**Entry 4. Numerical note (not a physical finding).**
- An ideal cone has a kink at its apex line that made the solver stall; the model regularises it by 0.05 mm, equivalent to a contact ring of finite stiffness. If a real printed cone is stiffer or softer laterally the compliance numbers move.

**Entry 5 (wave 3, from borrowed's exchange, "smaller remarks"). Decision: answered and left standing.**
- Conflict: the cone seat is unilateral (the fibre pulls it out at about 6.7 N, entry 2). A snap-in ball socket (the kind on RC ball links) is bilateral; borrowed-13's hexapod ring is bilateral too, at 0.097 / 0.096 / 0.017 mm per newton (radial / tangent / vertical, six legs of 20 N/mm, a ring 18 mm above the dot) against this seat's 0.10 / 0.01, at the price of six actuators and a gap for the gun's body (clock the gap to within about 8 degrees of the tail).
- Assumption: a cone seat with a preload is the way to get a spherical contact.
- Change: recorded as alternatives, not drawn. freedom-16 adds a second reason to care: a rail force along the roll axis has a vertical component F sin 30 degrees upward (1.5 N for 3 N), which cuts the seat's margin by a fifth; the routes there default to no rail force.
- Leaves uncertain: the snap-in socket's play and pull-out force; nothing measured.

**Entry 6 (wave 3, a mistake of the scene, fixed).** The readout "Learned actuator table" showed "tail NaN" when the perturbed solve for the tail pitch did not converge from a cold start (the slack tail wire), and the softness ellipsoid's default scale (25) was too small to see, so the checker reported its toggle as having no effect. The solves are now warm-started from the current pose, a failed one says "no equilibrium at +1 mm", and the ellipsoid default is 60.

## What the seat buys

With the bridle as modelled, compliance at the dot (dot mm per newton; radial / tangent / vertical; `calc/14-nose-gain.cjs`): collar 16 mm: 0.03 / 0.02 / 0.03; 40 mm: 0.09 / 0.06 / 0.03; 70 mm: 0.24 / 0.18 / 0.04; 110 mm: 0.71 / 0.55 / 0.05. The rigid arm of freedom-01 gave 0.3 to 0.9 mm/N. The tail lines' effect on the dot is attenuated to about 0.07 to 0.36 mm per mm of line depending on the station: an orientation trim 3 to 14 times finer than the tail actuator. These follow from the illustrative seat stiffness (100 N/mm) and the geometry.

## Branches and combinations

- Combines with freedom-05: a vernier at the nose stage for the per-tube offset.
- Combines with freedom-03: the tail bridle is two of freedom-03's lines.
- Original stays: freedom-01.

## Unresolved problems, and questions that need Derek's observation

- A printed sphere in a printed cone: contact stiffness, stick-slip, wear (nothing measured). A steel ball pressed into a printed collar is cheap ([sourcing](../../../sourcing/freedom.md): 1 inch chrome balls).
- Whether a tube swap is one motion (lift the cup, lower the tube).
- Measure the umbilical's pull at the exit, and gun mass and COM (as freedom-01).

## Assumptions

- Seat stiffness 100 N/mm, collar radius 12 mm, cone half-angle 40° from vertical: **illustrative**. Tail wires 200 N/mm, 300 mm; bungee pair 0.15 N/mm, 3 N preload: **illustrative**.
- Everything else as freedom-01. Tube, plate, bore: **[repo]**. Cable limits: **[manual]** p. 20.

## Sourcing pointers

`sourcing/freedom.md`: 1 inch chrome steel balls (12 pack), servo winches, magnetic encoders, load cells.

## Scene

`freedom-01b-nose-seat`.

## Wave 2 (after the exchange with eyes)

- **The seat and a camera on the barrel want the same place.** With the collar at 70 mm the cone blocks the top and +side of the barrel from 70 to 130 mm (34 of 66 camera stations clear against 47 of 66 with a rigid lug); ahead of the collar (30 to 55 mm) every clock angle is clear. Drawn in `scenes/freedom-11-eye-on-the-seat` (idea `freedom-11-eye-on-the-seat`). The collar radius of 12 mm clears the printed shell at stations up to 100 mm (shell radius 8.5 to 11.5 mm); at stations above 100 mm the sleeve is 15 mm in radius and needs a bigger collar.
- **The tail loop has no observer here.** The scene marks tilt "blind"; eyes-11's IMU sees pitch and roll from gravity (named in the exchange, not drawn). The vertical-axis turn stays unobserved.
- **Per newton of umbilical pull change** (calc/30): 0.03 / 0.01 mm (radial / vertical) at a 40 mm collar, 0.10 / 0.01 at 70 mm, 0.31 / 0.01 at 110 mm; an elastic with nothing holding rotation moves the dot 1.4 / 4.2 mm.
