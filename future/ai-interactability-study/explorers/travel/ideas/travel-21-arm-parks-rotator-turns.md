# travel-21-arm-parks-rotator-turns: one closure, joint by joint

Origin: wave 3's new direction, with `travel-20` and `use-13-work-states` (the states are use's). Depth: developed (a lens). Scene: `scenes/travel-21-arm-parks-rotator-turns`.

**Picture it.** A table of eleven columns, one per state of a closure, and rows for the hand, the rotator and each of the six joints of an arm. Read across the joint rows: the arm is at its weld pose (0 degrees) in every state where the rotator turns, and away from it (a few tens of degrees) only when it parks, comes back, or leaves at the end of a bead. Below the joints: who makes the last trim, what the AI commands and what it reads.

## The proposal

Where do an arm's joints and the tube's rotation share the work? They do not share it in time: the rotator turns in the tack, dry-lap and weld states and the arm holds; the arm moves in the gaps. Three consequences:

1. **Park replaces the shuttle and the drop tier.** The tube stays on the rotator; the recess opens because the arm leaves (at the default, J1 21 degrees, J2 38, J3 1, J4 13, J5 0.4, J6 56).
2. **The maker's repeatability figure is the figure the closure asks for.** Two approaches, before and after the face check, each a return to the taught pose; the last trim after the second. What the arm holds (stiffness, drift) is what no datasheet states.
3. **Following the runout is possible and not needed.** A first-harmonic table of 0.125 mm is at most 16 micrometres a second at 8 mm/s, a few to some tens of counts a second at a 0.4 to 3 micrometre step; the arm can do it on paper (ServoCart accepts 60 to 1000 Hz). Nobody has measured whether a harmonic-drive joint moves smoothly at 16 micrometres a second.

## What carries the loads, what establishes position, what is free or restrained

- As `travel-20`. The rotator carries the tube and turns it; the arm carries the gun and is still; a stack under the rotator exists only if the last trim is made there.

## What software could command, observe, what stays manual

- **Commands:** four large moves per closure (`moveJ` to park and back, twice), two trims, an escape retract if asked (force-limited), an optional streamed follow table keyed by the rotator angle (pulse input or console).
- **Observes:** the six encoder angles in every state; the flange force where fitted; the rotator's angle (a hall pulse per turn makes its zero readable). **Blind:** the dot, the arm's hold.
- **Manual:** loading, indicating, seating the plate; firing; cutting a fused wire and saying so.

## What was tried to break it

1. **Own break: the approaches.** The guide's order (tack, check the face with a dial, weld) gives two approaches per closure unless the dial can stand opposite the gun. *Change:* the last trim after the second; the second approach is a fresh draw of the return repeatability. *Leaves:* the dial question for Derek.
2. **Own break: the escape.** Zero is the sequence as written (release the trigger, then the pedal). Above zero the arm retreats along the beam, force-limited; a fused wire stops it and the HOLD state inhibits every axis until a hand has cut the wire and says so. *Leaves:* whether there is a lift at all.
3. **Own break: park is a pose the room has to allow.** At the default base (300 mm out, 150 mm up) the arm reaches only part of the up-and-out range; the badge says when it cannot. The fibre goes with the arm, and J6's 56 degrees is a twist the fibre may not take. *Leaves:* routing; a joint-limit rule for J6.
4. **Own break: follow the runout.** *Assumption:* the arm's small joint moves are smooth. *Leaves:* stick-slip at 16 micrometres a second; the table's angle zero.

## Branches and combinations

- Combines `travel-20` (the arm) and `use-13` (the states); the stack branch is `travel-19`'s fine tier without the drop tier.

## Unresolved problems and questions for Derek

- How do you end a bead and how far does the head go before the wire is free? Can the dial stand opposite the gun? How far out of the way must the gun be for you to seat the plate?

## Assumptions

- Durations from use-01 and use-15 (illustrative); park distances, escape and joint speed illustrative; UR3e link lengths **[manual]**; the states and their order **[repo]** as read by use (the lift-away is not in guide 46).

## Scene id

`travel-21-arm-parks-rotator-turns`
