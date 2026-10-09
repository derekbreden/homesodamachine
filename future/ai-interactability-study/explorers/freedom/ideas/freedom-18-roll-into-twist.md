# freedom-18: roll about the grip axis turns into twist and swing (a lens on where the fibre's twist goes)

Scene: `scenes/freedom-18-roll-into-twist` (a lens, not an arrangement). Origin: swarm (wave 3, the new direction on the umbilical; first pointed at by the study's own remark that the grip-axis roll is a rotation about the cable's exit axis and the manual forbids twisting the fibre, p. 20). Depth: developed. Numbers from `calc/fibre-line.js` (`twistSwing`, `rollWrenchClamped`) and `calc/33-fibre-routes.cjs`; the fibre's EI and GJ are **[unknown]**, every value is **illustrative**.

## Picture it

Left, the end view along the roll axis: a small circle is the cone the fibre's exit tangent sweeps as the gun rolls, with the tip of the tangent before and after, and an amber arc for the roll. Under it the side view: the roll axis dashed and the tangent 30 degrees above it. Middle, three horizontal bars are the same fibre from the gun on the left to the laser unit 5 m away on the right, each with a green post where its rotation is held (a rubber-coated hook, a clip, a swivel with the laser end as the next hold) and a red fill for the twist spread over the length up to that post: short and dark for the hook, long and pale for the swivel. Below, three bars: the torque of the twist, the bending moment of the swing, and for comparison the gravity spring of freedom-08 over the same angle.

## The proposal

The gun rolls about the line from the dot to the grip base (the reference scene's grip-axis roll, a motor in the automated vision). If the fibre left along that line a roll would be a pure twist of the fibre. The kit's stub leaves along the grip's rake, about 30 degrees off, so the tangent rides a cone: 10 degrees of roll is 8.6 degrees of twist and 5.0 degrees of swing of the exit direction (30 degrees: 26.1 and 15.0). The swing bends the fibre, which puts a moment and a lateral force on the gun. The twist is not removed by a ring or a swivel; it is spread over the fibre between the gun and the first place that holds its rotation. Twist rate is roll divided by that distance.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the fibre, as a torsion spring about the roll axis (GJ/L) and a bending spring across it (EI/L).
- **Position:** nothing here locates anything; the roll axis passes through the dot, so the roll itself does not move the dot.
- **Free:** the fibre's rotation beyond a swivel or a free ring.
- **Restrained:** its rotation at a hook, a clip, a cable sock or the laser unit's connector.
- **Driven:** the roll (motor).

## What software could command, what it could observe, what stays manual

- **Command:** the roll.
- **Observe:** twist, by a stripe read by a camera (eyes-11b; it shows the sheath's twist, not the fibre's) or by an encoder on a swivel collar; the roll motor's torque, which reads twist and swing together.
- **Manual:** laying the fibre untwisted at a chosen roll; un-twisting after a roll change; choosing where the rotation is held.

## What was tried to break it

**Entry 1. Roll is not pure twist.**
- Conflict: the study's earlier scenes (freedom-01 and the wave 1 notes) called the grip-axis roll a rotation about the cable's own exit axis. In the kit the exit tangent is 30.2 degrees off the roll axis, so a roll swings it.
- Assumption: the fibre leaves along the roll axis.
- Change: the scene splits the roll into twist (about the tangent) and swing (the tangent turns). Only with a boot that lands the fibre on the axis (freedom-16 route D) is the roll all twist.
- Leaves uncertain: where the real fibre leaves the grip base.

**Entry 2. A swivel does not remove twist, it moves the hold.**
- Conflict: adding a ring or a swivel near the gun looks like a way to stop the fibre being twisted.
- Assumption: a joint that lets the fibre spin frees it. It frees it at that point; the rotation is still fixed at the laser unit's connector, so the twist appears between the swivel and the connector.
- Change: twist rate = twist / distance to the first hold: 83 degrees per metre at a rubber-coated hook 0.12 m out (a hook is a hold), 25 at a clip 0.4 m out, 14 at 0.7 m, 2.2 with a swivel and the laser end 4.6 m away (per 10 degrees of roll at an exit on the axis). The scene marks a slider for "comfortable" because the manual gives no number.
- Leaves uncertain: the maker's tolerance; whether a fibre lying on a bench holds its rotation by friction in a way the four holds do not model.

**Entry 3. The torque is small against gravity; the swing's bend is not.**
- Conflict: with EI 0.1 N·m² and GJ 0.08, 10 degrees over 0.4 m is 30 N·mm of twist torque (freedom-08's gravity spring would give 73 N·mm for the same angle), but the swing at 30 degrees adds a bending moment of 88 N·mm and a lateral force of 0.33 N on the gun.
- Assumption: twist is the cost of roll. The bend and the lateral force are what reach the dot.
- Change: with a hold at 4.6 m all three fall to 3 N·mm, 8 N·mm and 0.003 N.
- Leaves uncertain: the small-angle beam formulas (4EI·γ/L, 6EI·γ/L²) for a real curved route.

**Entry 4. Twist is a state, not a motion, if the roll is set once.**
- Conflict: an AI scanning roll as an axis changes the twist with every step.
- Assumption: roll is a run-time axis.
- Change: set roll at setup and lay the fibre untwisted there (a state, use-13 style), so the twist is zero at the weld. If roll is scanned, the twist rate is the number to bound, and the swivel plus a far hold is the only arrangement in the study that keeps it small.
- Leaves uncertain: whether the automated vision needs roll at run time (Derek's description has a motor on it).

## Branches and combinations

- **freedom-16:** the route that puts the fibre on the roll axis and a swivel collar on the rail is the arrangement this lens says makes roll cheap.
- **eyes-11b:** the stripe as the twist gauge.
- **use-13 and use-14 (states, handovers):** un-twisting after a roll change is a handover between states.
- **datum-03b (orbiting crown):** the fibre must follow 380 degrees of orbit; the same twist arithmetic applies to the rotation of the crown, not of the gun.

## Unresolved problems, and questions that need Derek's observation

1. **Where does the fibre leave the grip base and in which direction?** (Same photo as freedom-16, question 1.)
2. **Does the maker give a number for twist?** The manual says "strictly forbidden" (p. 20) and gives none.
3. **How big is the roll range the process needs?** The reference scene's roll dial and the beam's angle to the seam.
4. **How stiff is the fibre in torsion?** A one-metre length clamped at one end with a marked lever at the other: twist a known angle and feel it.

## Assumptions

- Exit tangent 30.2 degrees off the roll axis (kit proxy stub): **illustrative**. EI 0.1 N·m², GJ = 0.8 EI: **illustrative, [unknown]**. Laser end 4.6 m from the first hold (fibre 5 m **[manual p. 20]**).

## Sourcing pointers

`sourcing/freedom.md`, wave 3: the ball-bearing swivel and the cable sock grip (freedom-16).

## Scene

`freedom-18-roll-into-twist`.
