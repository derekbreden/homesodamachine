# travel-05-lever-map: ratio devices and where an angle lands

**Picture it.** A side view of the gun with a teal pivot and a purple actuator attachment you can drag along the shell. The red dot swings on an arc whose radius is the distance to the pivot. Below, bars show what one angular step or one bit of backlash is at the dot for a pivot at the grip base, the housing, the barrel, the dot, and wherever you put yours; beside them, three joints of a serial arm add their slop.

Scene: `scenes/travel-05-lever-map` (a calculator drawn on the gun, not an arrangement). Calculations: `calc/01-pose-and-levers.mjs`.

## The proposal

Put the reduction where the motion is made, on purpose. Any stage that is an angle has two levers: L from the pivot to the dot, and a from the pivot to where the actuator pushes. The dot moves L times the angle; the angle is push over a. So travel and backlash are multiplied by L/a at the dot. An actuator attached nearer the pivot than the dot amplifies; one attached beyond the dot reduces (and needs room that is not there over the recess). Reduction devices give the same trade inside the actuator:

- a **reducing lever** with a flexure pivot (no backlash, tenths of a millimetre of travel);
- a **micrometer head** or **differential screw** on a small stepper (0.5 mm per turn: 1/200 turn = 2.5 microns, before backlash);
- a **planetary gearbox** on an arc drive (50:1 turns 0.9 degree into 0.018);
- a **soft link**: a spring between the actuator anchor and the gun attenuates anchor motion by k1/(k1+k2) at the cost of stiffness; a hard lock can freeze the result (branch of Derek's suspension example; not drawn).

## What carries the loads, what establishes position, what is free or restrained

Nothing here carries anything; the point is that pivot, actuator attachment and the place the weight is carried are three different points on the shell (Derek's note). The position is the dot; the only reference is the motor's own step count.

## What software could command, observe, what stays manual

- **Commands:** an angle or an actuator push. **Observes:** a step count or an encoder on the pivot; the dot is computed, not observed. **Manual:** everything mechanical.

## What was tried to break it

**1. The grip pivot.** *Conflict:* 279 mm lever: 0.05 degree per step is 0.24 mm at the dot, 0.01 degree is 0.049 mm. *Change:* move the pivot toward the dot (barrel middle 93 mm: 0.081 mm per 0.05 degree) or reduce at the actuator. *Leaves:* the pivot near the dot cannot be a hinge in the recess (see travel-03).

**2. Reduction by geometry needs room.** *Conflict:* an actuator beyond the dot (a > L) sits over the recess where the tube, nozzle and wire are. *Change:* put the reduction inside the actuator. *Leaves:* backlash of the reduction (a 50:1 planetary gearbox on Amazon states a backlash figure whose unit was cut off in the title I read: `sourcing/travel.md` 14).

**3. The serial arm.** *Conflict:* three joints 0.1 degree loose at 600, 350, 200 mm from the dot: 1.05 + 0.61 + 0.35 = 2.0 mm worst case, 1.26 mm root-sum-square. *Assumption:* the slop and levers are illustrative, not a measured monitor arm. *Change:* the arm carries and roughly places; something else locates (`travel-01`). *Leaves:* actual arm joint play.

## Branches and combinations

- Supports `travel-02` (follow stage reduction), `travel-03` (arc drive reduction), `travel-01` (why the stack is on the work side).
- Soft link with a hard lock: a compliant drive that positions by anchor motion then a clamp freezes it. An idea to develop: it would show the free/restrained switch in software terms.

## Unresolved problems and questions

- Whether backlash of cheap reductions is small enough; nothing measured.
- The side plane hides the out-of-plane rotations.
- Question: which joints of a monitor-type arm does he expect to keep, and does he have one to measure its play?

## Assumptions

- Gun profile: kit proxy of the manual's 253 x 143 x 34 mm envelope **[manual]** (illustrative). Small-angle: dot travel = L x angle.

## Sourcing pointers

`sourcing/travel.md`: micrometer head (16), micrometer stage (15), planetary gearbox (14), MGN12 rail (5).

## Scene id

`travel-05-lever-map`
