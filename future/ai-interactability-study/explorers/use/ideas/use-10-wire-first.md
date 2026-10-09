# use-10-wire-first: the consumable as the probe

Scene: `scenes/use-10-wire-first/index.html`. Origin: swarm. Maturity: rough (arrangement A7 of the notebook).

## Picture it

Seen from above, the seam is a teal line, the plate above it and the tube wall below; a red dot sits on it and a gold wire comes in from the left and stops a millimetre or so upstream, on the plate side. Across the section the wire is a tiny gold circle resting on the plate a fraction of a millimetre from the corner. A green band marks the side the tube surface arrives from. Flip the rotation direction and the band jumps to the other side; the wire is now on the trailing side.

## The proposal

The dot says where the beam goes; the wire says where the filler lands; the study watches only the first. The feeder box has an **advance** and a **retract** button that run the wire with the laser off [manual p.18]. So a dry run can include the wire: jog it out until it touches, see where it landed relative to the dot, and correct the pose or the guide before any bead. Touching metal closes a circuit between wire and work lead: one bit, which says *on metal*, not *where*; a camera or the dot itself has to supply the where. The consumable becomes the probe.

The proposal does not want a new sensor first. It asks that the dry lap and the "contact and set-up" state of the day carry the wire, because "place the wire on the arriving side of the puddle" is a step [repo] that nothing else in the study observes.

## What carries the loads, what establishes position, what is free or restrained

The wire guide is a straight tube on a short leg from the barrel collar, aimed at the dot in the kit proxy (so the wire lands exactly at the dot by construction, which is why the offsets here are illustrative). The conduit runs beside the umbilical, off the gun's weight path. The wire is a springy 0.76 mm rod: pushed against the plate it buckles long before it can move a gun, so it carries no positioning load; its position is set by the guide's pose relative to the dot.

## What software could command, observe, and what stays manual

- **Command:** wire advance and retract (buttons today; the feeder's 6-pin connector carries power and signal lines [manual p.16] and nothing documents a protocol: how to drive it is unknown); the existing rotator. The retract-and-pullback settings sit on the welder's touch screen [manual p.23] and are not scriptable that we know.
- **Observe:** wire-to-work-lead continuity (touching); a camera on the dot and the tip (where).
- **Manual:** placing the wire on the arriving side, choosing the rotation direction, snipping.

## What was tried to break it

1. **Flip the rotation direction.** *Conflict:* the arriving side flips and the wire is on the trailing side; the guide is on the gun, and the gun is on one side. *Assumption:* direction is a parameter you can change per weld. *Change:* it is a **campaign-level state**: the pose (the side of the gun, the approach) is set for one direction, and changing it means a new pose. The repo already sets wire lead and trail only after the direction convention is true [repo]. *Leaves:* whether the same head could serve both directions (a mirrored mount); not drawn.
2. **Wire against the wall.** *Conflict:* a tip landing on the wall side of the corner buckles and sits in the beam's shadow. *Change:* the scene stops the wire at the wall and shows a LIMIT badge; the plate side is the only place it can land. *Leaves:* the real geometry of the corner and the guide.
3. **Touch is one bit.** *Conflict:* continuity cannot tell 0.2 mm from 2 mm off the corner. *Change:* a camera across the seam supplies the where; touch supplies contact. An insulated plate would separate wall from plate contacts, but a slip-fit plate (0.005 in radial slip) touches the bore [repo], so it is not drawn. *Leaves:* whether a usable camera view exists (the eyes explorer's question).
4. **Wire retract is not the head lift.** *Conflict:* the gun's pullback (its settings page) draws the tip away after the trigger is released; the repo's end of bead is a head lift with the trigger held, then release. *Change:* the dry run can test whether the pullback clears the bead but is not a substitute.

## Branches and combinations

- Combines with `use-02-swing-head` (the head's retract is what takes the guide away) and `use-05-gates` (a wire stuck in the bead is a hold state; wire-touch continuity can be a guard).
- The gauge (`use-11-setup-gauge`) could carry a printed line where the wire should land.

## Unresolved problems and questions for Derek

- How do you judge wire placement today, and how often is it wrong?
- Can the feeder's advance and retract be reached electrically (the 6-pin connector) without changing its safety behaviour, and does the wire feed run with the laser interlock open? Manual p.18 says the buttons advance and retract; whether that works with the laser disabled is implied, not stated.
- Whether the wire lands where the guide aims it, on your unit (a cheap test: jog it onto a sheet of paper).

## Assumptions

- **[repo]** place the wire on the arriving side of the puddle; recorded recipe: wire feed 12 mm/s, wobble 80 Hz x 2 mm; wire ER316L .030; slip-fit plate.
- **[manual]** wire jog buttons (p.18); pullback and patch length settings (p.23); feeder connector (p.16); the conduit is separate from the umbilical (p.16, 19).
- **[unknown]** the real landing offset of the guide; whether jog works with the interlock open.
- Illustrative: every offset, the guide pitch, the contact rule, the camera noise.

## Sourcing pointers

None needed for a sketch; a UVC camera is in `sourcing/use.md`.

Scene id: `use-10-wire-first`.
