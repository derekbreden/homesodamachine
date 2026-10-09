# room-02: ceiling carries the load, table locates the gun

**Origin:** swarm (room framing), a branch of the table opening. **Scene:** `scenes/room-02-ceiling-carries`. **Depth:** developed, with a solver behind the foot loads.

## Picture it

A room, not a bench. Overhead, a track runs along the ceiling; a small trolley rolls freely on it, carrying a spring balancer whose single line goes down to a lug on the gun's housing. The umbilical bundle hangs from the same track in loops and drops to the grip base. On the table below, the printed shell has three splayed legs ending in ball feet, so the gun stands on the table like a stool tilted at 45°. A planar drive (mechanism open) pushes it sideways. Nothing stiff holds the gun up.

## The proposal

Divide the roles between two surfaces. The **ceiling carries**: a share of the gun's weight (a setpoint) and the whole umbilical, so the fibre's weight and its 350 mm bend radius are the room's problem. The **table locates**: three feet on a flat plane fix height, pitch and roll by contact; a planar drive fixes x, y and yaw. The shelf under the tube (room-01) sets the plate-to-dot height.

## What carries, what establishes position, what is free

- **Carries:** balancer line (a chosen share) and legs (the rest). Umbilical from the trolley track.
- **Establishes position:** the table plane by contact for Z, pitch, roll; the planar drive for x, y, yaw. The stance (leg lengths and foot spread) is printed.
- **Free:** the ceiling trolley (passive, follows the gun), the ball feet on the table. **Driven:** the planar drive, the balancer lift.
- **Escape at the end of a bead:** the balancer's lift; a spring balancer cannot do it fast. A motorised hoist or a lift stage at the drive is the open part.

## Software

- **Command:** planar drive X, Y; balancer lift; balancer share (line-tension setpoint).
- **Observe:** three foot-contact switches or load cells, line tension by a load cell. It cannot see the dot in this scene (the camera of room-01 applies).
- **Manual:** printing the stance, hanging the bundle on its trolleys, loading the tube.

## Tried to break

1. **"The ceiling positions the gun."** *Variant:* gun on one balancer line, bungees restraining X or Y. *Assumption:* room height gives a stiff long pendulum. *Finding:* a pendulum's lateral stiffness is m·g/L; 1.5 kg on 1 m is 0.015 N/mm, so a 1 N tug moves it 68 mm, and longer is softer (`calc/suspension-stiffness.mjs`). A bungee pair adds 0.01 to 0.2 N/mm depending on pretension; 1 N/mm would need 250 to 750 N of pretension. *Change:* the ceiling only carries. *Leaves:* the balancer line tilts by dx/L and pushes sideways by F·dx/L (readout), small but not zero.
2. **The first tripod was unstable.** *Variant:* feet at the shell's lugs, 16 mm either side of the centre line. *Assumption:* three contact points under the lugs make a stool. *Finding:* the centre of mass projected outside the foot triangle (foot B at −1.6 N with no balancer, no cable) (`calc/stool-feet.mjs`). *Change:* splayed legs on outriggers, feet 100 to 200 mm apart (stance slider). *Leaves:* the stance must clear the hole, the tube and the cable.
3. **Weight relief costs stability.** *Assumption:* the more the balancer takes the better. *Finding (scene defaults, hanging umbilical):* foot A carries 2.3 N at 30 % relief, 0.7 N at 50 %, and is unloaded (−0.9 N) at 70 %; with the umbilical lying on the table (0.8 N drag at 133 mm height) foot A is 0.5 N already at 50 %. The centre of mass sits 25 mm inside the front edge of the foot triangle whatever the stance width, because the front pair defines that edge. *Change:* about a third; keep the umbilical's horizontal component near zero by hanging it; move the front feet forward if more margin is needed. *Leaves:* a 10 N stuck-wire pull lifts a foot at any share (a hold-down is missing).
4. **Umbilical route decides the sideways force.** Lying on the table: friction about 0.9 N of drag (illustrative) that flips with the motion; hanging from a following trolley: weight plus 0.1 N rolling resistance; hanging from a fixed hook: a sideways force that grows with travel. *Leaves:* the cable's bending stiffness, unmeasured, may dominate all three.
5. **Contact needs a smooth plane.** *Leaves:* table flatness and ball-transfer feet friction; feet must stay outside the hole.

## Wave 3 note (from eyes, wave 2)

The three foot contacts (switches or load cells) are a **pose sensor** as well as a scale: height, pitch and roll by touch, before any camera. In weigh-in mode the same three cells give the gun's mass and plan centre of mass; in operation their contact state says "seated" and their load balance says which way the umbilical is pulling. Added to the software list; not a new arrangement.

## Branches and combinations

`room-01-table-opening` (same table); `room-06-corner-cords` (a different way to carry from above); `room-03-wall-port` (a different way to carry weight: the ball carries).

## Unresolved, questions for Derek

- Weigh the gun. Hold the cable end on a spring scale with the cable laid out and read its pull at three positions.
- The planar drive: a printer-style gantry pushing a pin (yaw stiffness is the open part), a magnetic drive under the table, or cords.
- The hold-down for the end-of-bead yank.
- Ceiling: where a 1.2 m track can be fastened.

## Assumptions

Mass 1.47 kg, CoM, umbilical 0.3 kg/m, friction 0.35, rolling resistance 0.1 N, ceiling at 1.05 m, drive stiffness 10 N/mm: **[illustrative]**. Statics only. Gun mass, umbilical bending stiffness, table flatness: **[unknown]**. Bend radii: **[manual]**.

## Sourcing pointers

`sourcing/room.md` entries 1 (spring balancers, $16.97 to $42, 29 to 47 ratings), 2 (ball transfer units).

## Scene

`scenes/room-02-ceiling-carries`

## Wave 2

- **Weigh-in (borrowed from `trials-02-dock-reset`).** With the balancer detached, the three feet are three load cells. The gun alone gives its mass and plan centre of mass; the same feet with the umbilical hung on give its weight (the change in the total) and, from the change in the moments at the grip base's known height, its sideways pull. The scene has a *Weigh-in mode* and a cell-resolution slider: at 1 g the readouts recover the mass, the centre of mass, the cable's 247 g and 0.10 N in the drawing. This is how the stool can answer the study's recurring unknowns (gun mass, centre of mass, umbilical pull). The height of the centre of mass is not available from one attitude. Real feet roll or slide: friction corrupts the moment-based pull estimate. Cells: `sourcing/trials.md` (5 kg bar cell and HX711 kit).
- The stool is also the rest of `room-15-one-knob-table` (on a sled on a radial rail) and the hold-down question (a 10 N stuck-wire yank lifts a foot) returns there.
