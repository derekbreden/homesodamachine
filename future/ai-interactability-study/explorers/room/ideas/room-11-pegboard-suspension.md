# room-11: pegboard as the anchor lattice for Derek's rings and bungees

**Origin:** Derek's suspension example, taken through the room framing (the wall as the anchor grid and the ceiling as the long Z). **Scene:** none; numbers in `calc/suspension-stiffness.mjs`. **Depth:** sketch, done to establish what the wall can and cannot do, before any drawing.

## Picture it

A garage pegboard wall behind the bench, or a slatwall, or a French-cleat panel. Coated hooks in the grid hold cords and bungees; the cords run to rings on the gun's printed shell: one ring near the tip, one at the base around the umbilical and wire feed, a third somewhere between. The gun hangs from a line to the ceiling for height, and two bungees restrain it horizontally. The wall's hole grid means each anchor can be moved one hole at a time.

## The proposal

Derek's suspension as he wrote it, placed in a room. The wall supplies a lattice of anchor positions (a discrete family: which hole for each bungee, which ring), the ceiling supplies the length for Z, and the shell's rings and lugs supply the attachments. The lattice makes it cheap to try many geometries by hand.

## What carries, what establishes position, what is free

Carries: the ceiling line takes the weight; the bungees are lateral restraints. Position: nothing precisely; the arrangement is *compliant*, positions come from where the bungees leave it. Free: all axes not restrained by a bungee; the ring contacts on the shell (sliding, rolling, locked) decide which rotations are free. Driven: nothing unless an actuator moves an anchor or pulls a bungee.

## Software

Command: only if anchors are moved by actuators (a bungee end on a small winch). Observe: a camera on the dot. Manual: choosing the holes.

## Tried to break it

1. **"It will sway and lack precision"** made concrete: a 1.5 kg gun on a 1 m line has a lateral stiffness m·g/L of 0.015 N/mm (a 1 N tug moves it 68 mm; sway period 2 s); on 0.3 m, 0.049 N/mm (`calc/suspension-stiffness.mjs`). A bungee pair of pretension T and length L restrains the axis *perpendicular* to it with 2T/L: 0.007 to 0.2 N/mm for T of 5 to 50 N and L of 0.5 to 1.5 m; along its own axis it is the bungees' own soft rate (0.1 to 1.6 N/mm for 50 to 800 N/m bungees). Reaching 1 N/mm perpendicular needs 250 to 750 N of pretension. A gravity- or pretension-restored support cannot be made stiff by adding length or a third ring; a third ring changes which motions are free, not how stiff the restrained ones are.
2. **What the arrangement can do well:** carry the weight and the umbilical's weight from above; give a *soft, wide-range setup pose* (a hand or a small actuator can move the gun tens of millimetres with grams of force); reduce the load an actuator sees to the inertial and cable-tug loads.
3. **Then lock:** compliance is fine for setup; precision must come from a moment when the compliant support is temporarily restrained: a dock (room-02: feet on the table plane; room-05: a kinematic seat) or taut fixed-length lines (room-06: 190 to 380 N/mm). The bungees become the setup carrier and the taut lines or the dock become the weld-time stiffness. This is the idea I would carry forward from Derek's example.

## Branches and combinations

`room-02-ceiling-carries` (the ceiling carries, the table locates), `room-06-corner-cords` (replace bungees by fixed-length lines), `room-11b` (not drawn): wall-anchored bungees with a lock at the dock.

## Unresolved, questions for Derek

What Derek pictured the third ring doing (reducing range, increasing force, reducing weight): none of this note's numbers say. Pegboard hole pitch (1 in is the common pattern; not checked) against the finest anchor step wanted.

## Assumptions

Mass 1.5 to 2.5 kg and bungee rates 50 to 800 N/m: **[illustrative]**. Formulas: **[derived]**.

## Sourcing pointers

None: pegboard hooks and bungees are hardware-store items; sourcing 1 (spring balancer) is the Z-carrier.

## Scene

None.
