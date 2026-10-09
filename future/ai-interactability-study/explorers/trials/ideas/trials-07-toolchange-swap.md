# trials-07-toolchange-swap: one positioner, three tools, no person between tubes

Scene: `scenes/trials-07-toolchange-swap/index.html` (rough sketch). Sourcing: zero-point plate and StealthChanger in `sourcing/trials.md`.

## Picture it

The gantry that carries the gun for a trial drops it into its dock, picks up a gripper, lifts the puck off the rotator into an empty rack slot, takes the next puck from the rack, lowers it onto the seats, parks the gripper, picks the gun back up, verifies the new tube and starts the next trial. The AI keeps a register of which puck sits where. A person is needed to load the rack and unload it, not for every tube.

## The proposal

Overnight and multi-day dry-run trials need the swap to stop being a person. Rather than a second robot, borrow the 3D-printer toolchanger: one positioner, several tools, each parked in a dock with a kinematic coupling. Here the tools are the gun in its shell, a puck gripper, and a third station (calibration board or camera). The puck (trials-01) makes the payload a defined object with a kinematic foot; the dock (trials-02) makes the gun tool a defined object with a kinematic seat.

The scene steps one exchange (eleven steps) and checks the one fact the idea stands on: **can the tool coupling hold a gun on a lever with its umbilical pulling?** Demand is gun weight times its lever plus the umbilical's pull times its height, times a dynamic factor. Three classes of capacity are compared: magnetic Kelvin (what printer toolchangers do), Kelvin with a latch, and a zero-point stud module (industrial). At 1.5 kg on 200 mm the demand is about 4.6 N·m with a factor of 1.5; magnets alone hold about 1.5 N·m (half the preload times the ball radius, illustrative). So the idea needs a mechanical lock, not just magnets.

## What carries the loads, what establishes position, what stays free

The gantry (unspecified) carries one tool at a time through the coupling; docks carry parked tools; the rack carries pucks. Position: each dock and rack slot is a seat; the gantry re-anchors on every change; three docks are three known points, enough to fit a linear scale and skew of the gantry's own axes (not drawn). Free: the umbilical follows the gun on an overhead hook.

## What software could command, observe, and what stays manual

- Command: gantry moves; couple/release; gripper open/close; which slot is next.
- Observe: coupling contacts (three closed per seat); puck present in the gripper (current or jaw switch); the rack register from tag reads; the dock cells (trials-02).
- Manual: loading and unloading the rack; jams.

## Tried to break it

1. **Magnets are not enough.** Conflict: a gun on a lever tips a magnetic coupling. Assumption: printer toolchanger practice scales. Change: latch or stud; the scene shows the margin. Leaves: how a stud module is unlocked automatically (pneumatic or a motor cam) and how it carries an umbilical is not designed; the one retail zero-point plate found lists 20 kN pull-in and 0.005 mm repeatability as seller claims with three reviews (`sourcing/trials.md`).
2. **One positioner must reach everything.** Rack, rotator and three docks span about 1.2 m in the scene; fine positioning at the corner and carrying a 2 kg puck are different requirements. Repair: nothing chosen; a coarse gantry for the exchange and a fine stage for the corner is the natural split, or a separate cheap pick-and-place for pucks (a printer gantry with a gripper). Leaves: cost of two mechanisms against one that is over-specified for both.
3. **The umbilical.** A 5 m fibre with a minimum bend radius **[manual p.20]** cannot be dragged across a bench. Repair: an overhead hook and dock positions that never make the cable cross the tube. Leaves: not modelled.
4. **Unattended.** A rig that changes tools alone needs guarding and an interlock. Leaves: Derek's decision; the idea is meant for the dry-run rig with a mule (trials-06).
5. **Rack repeatability.** The gripper must find a puck to a few millimetres; the slot is a seat. Leaves: rack accuracy over time.

## Branches and combinations

- Combines `trials-01-puck-swap` and `trials-02-dock-reset` (declared in the scene).
- A cheap variant for the same goal: a gravity or spring-fed chute that presents pucks to a lift (not drawn), or the hand.
- Borrowed from: StealthChanger (open source, 1.2k GitHub stars observed) and industrial zero-point workholding.

## Unresolved, and questions for Derek

- Q: How many different tubes are wanted in one unattended session? If it is five, a rack with a person is fine; if it is fifty, this idea earns its keep.
- Is the umbilical routing solvable without an overhead hook?

## Assumptions

Layout, station and slot positions, six-puck rack **[illustrative]**; masses **[repo]**/**[derived]** for tube and plates, puck 0.6 kg **[illustrative]**; capacities: magnetic 0.5 x 100 N x 30 mm, latch 15 N·m, stud 200 N·m **[illustrative]**; gun mass, lever, umbilical pull **[unknown]**.
