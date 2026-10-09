# freedom-15: the pull ledger (the umbilical, the wire conduit and the gas hose as the design driver)

No scene of its own; the numbers live in `scenes/freedom-11-eye-on-the-seat` (pull slider, mm per newton) and `scenes/freedom-13-map-and-step` (the step at bead start). Origin: swarm (the digest's thin region "the umbilical and the wire conduit as the design driver"); depth: sketch with numbers from `calc/29`, `30` and `31`. Every stiffness, mass and force is **illustrative**; the fibre's weight, stiffness and pull are **[unknown]**.

## Picture it

A list, not a machine. Three tethers leave the grip base: the 5 m QBH fibre umbilical, the wire conduit from the feeder box, the 6 mm gas tube. Each puts a force on the gun. The list says which ones are known, which are guessed, what changes at the start of a bead, and what each measurement costs Derek with things he has.

## The proposal

Every scene in this study has one force it cannot get rid of: the pull at the grip base. Treat it as the design driver and keep a ledger of where it comes from and what it costs at the dot, by arrangement (mm per newton, `calc/30`). Then choose arrangements, routes and measurements by that ledger.

| source | known | unknown | changes at bead start? | how Derek can measure it |
|---|---|---|---|---|
| weight of the hanging span of the fibre | span length (route) | weight per metre | no | kitchen scale on a metre |
| the fibre's own recoil from curvature | radii (manual: 350 mm emitting, 240 stored) | bending stiffness EI; hysteresis | yes, if the route differs between dry turn and bead | spring scale at the exit at three poses |
| the couple at the exit (a fibre clamped at the exit and leaving already bent) | up to EI/R: 0.14 to 1.4 N·m at 350 mm (EI 0.05 to 0.5) for an exact route | EI; the route; whether the exit is rigid | yes, if the route differs between the dry turn and the bead | hang the gun from a thread through the candidate pivot with the fibre laid as it will lie, read the tilt; two hangs with the fibre laid differently separate force and couple |
| the wire conduit (feeder push) | it exists | stiffness, friction, push while feeding | yes (feed starts) | dial gauge on the shell, laser off, jog the wire |
| the gas tube (6 mm, 15 to 20 L/min) | it exists | stiffness, pressure straightening | yes (gas opens) | dial gauge, gas on and off |
| the trigger, the hand's grip | none | all | yes | not a support question |

The cable's pull is mostly its own recoil: a cable held to radius R pushes back about EI/R² (`calc/31`): 0.4 to 4 N at 350 mm and 0.9 to 8.7 N at 240 mm for EI 0.05 to 0.5 N·m². It scales as 1/R²: opening a loop from 240 to 350 mm cuts it to 47 %; doubling the radius cuts it to a quarter. Its lateral stiffness at the grip is small (0.3 to 56 mN per mm of gun motion, for 0.3 to 0.8 m of free length), so it acts as a constant force whose value depends on the route, not on where the gun is within a few millimetres.

## What carries loads, what establishes position, what is free or restrained

Not a support idea. The ledger asks of each arrangement: through what does the pull pass, and what is the dot's movement per newton. The dot is moved 0.10 mm per newton by the nose seat with the tail bridle (collar at 70 mm), 0.45 / 1.0 mm by a rigid-based stage on an elastic, 1.4 / 4.2 mm by an elastic with nothing holding rotation, about 5 mm by a friction arm. The nose seat's tail wires (200 N/mm) take the pull at a lever that the collar's 70 mm shortens; that is why it is small.

## What software could command, observe, and what stays manual

- **Observe:** a load cell in the support (seat load, balancer line, a dock's three cells: trials-02, travel-08); the eye's shift when the pull changes; the IMU tilt of a hung gun (eyes-11), which reads the torque of the pull about the hang point when the gun is at rest.
- **Command:** nothing; a force term in `freedom-13` uses the reading.
- **Manual:** the route of the fibre, the conduit and the hose.

## What was tried to break it

**Entry 1. The axis of the exit passes through the dot.** In the kit, the direction from the dot to the grip base is the grip axis and the cable exit axis (`LOCAL_ROLL_AXIS`), so a pull along the exit axis has no torque about the dot and none about any pivot on that line (borrowed-01's rings and borrowed-02's gimbal turn about axes through the dot). A pull at δ to the axis has a torque F·sin δ × 279 mm about the dot: 0.1 N·m for 2 N at 10°. So route the fibre straight along the exit axis for a stretch, which the bend radius wants anyway; the cable that leaves along the axis is the cable a ring or gimbal at the dot does not feel. Assumption: the cable leaves along the roll axis; the manual does not say (travel-08's entry 2 says the same).

**Entry 2. Measuring the pull is a pull.** A spring scale hooked at the exit changes the route. Use the IMU on a hung gun or the dial gauge for changes, the scale for the level at a pose.

**Entry 3. The wire conduit and the gas hose are not on the fibre's ledger.** Their stiffness and friction are unknown and they may dominate the step at bead start.

**Entry 4 (wave 3, from borrowed's exchange, section 4). The ledger has a column missing: the couple. Decision: revised (a fifth row, and a scene: `freedom-16-fibre-line`).**
- Conflict: entry 1 says a pull along the exit axis has no torque about the dot or any pivot on that line, so route the fibre straight along it. That holds for the force. A fibre clamped at the exit and leaving already curved also applies a moment, up to EI/R (0.14 to 1.4 N·m for EI 0.05 to 0.5 and R 350 mm), and about 3 to 4 EIΔα/ℓ for an end-angle mismatch Δα over a free length ℓ. In borrowed-15, 0.05 N·m of couple alone moves the dot 6.3 mm with the cable's force anchored on the pivot. The solver of freedom-16 (`calc/cable-rod.js`) gives the whole wrench for a route: a designed arc (R 500 mm, 60 degrees) leaves 1.0 N and a couple of 0.22 N·m at EI 0.11; a clip 10 mm or 5 degrees off makes it 2.4 to 2.8 N; 20 mm of extra fibre 5.6 N. EI/R² is the floor for an exact route, not the general case.
- Assumption: the fibre is a force with a direction. It is a force and a couple, and the straight run that takes the bend out is what product designers do (a bend restrictor, a service loop, a strain relief).
- Change: the ledger has the couple row; the scene puts the couple inside a rigid boot (the bend is then internal to the shell) and shows what is left. Entry 1 needs a refinement, also from the drawing: the direction from the dot to the grip base is the roll axis, but the kit's fibre stub leaves along the grip's rake, 30 degrees off it, so "route the fibre along the exit axis" needs a boot to be true.
- Leaves uncertain: EI, the fibre's weight per metre, the conduit and the gas hose beside it (all unmeasured).

**Entry 5 (wave 3, from borrowed's exchange, section 4, the question). Is the thread-hang tilt the way to read the whole cable's torque at once? Decision: answered, yes.** Hanging the gun from a thread through the candidate pivot with the fibre attached and laid the way it will lie gives the tilt from plumb, hence the cable's total torque at that pose, force times lever and couple together (torque = tilt × the gravity spring M g ℓ; freedom-08 has the numbers). Two hangs with the fibre laid differently separate them. It needs a thread, a protractor photo and a kitchen scale.

## Branches and combinations

- `freedom-11`: mm per newton by support. `freedom-13`: the step and its correctors. eyes-11b: a camera on the fibre as a pull gauge with a hysteresis flag.
- travel-08 (cable on its own balancer and gallows) and borrowed-11 (festoon): the way to make the pull small and constant.

## Unresolved problems, and questions that need Derek's observation

1. Weigh the gun; hang it from a thread at two points for the centre of mass.
2. Pull along and across the fibre exit at three poses with the EISCO Newton force meter ($9.99, 10 N; graduation not read off the page).
3. Jog the wire and open the gas with the laser disabled: does a dial gauge on the shell move?
4. Does anything move when the laser starts emitting?

## Assumptions

EI, lengths, mass and the pull are **illustrative** (`calc/31-cable-gauge.cjs`). Exit axis through the dot: from the kit's `LOCAL_ROLL_AXIS` [repo/kit], itself illustrative geometry.

## Sourcing pointers

`sourcing/freedom.md`: the EISCO Newton force meter (Prime, 200+ bought in the past month), the load cell and HX711, the 3 mm balls.

## Scene

`freedom-16-fibre-line` is the scene of this ledger (wave 3): the wrench, its line, the couple and the steps for four routes. The numbers by support are still in `freedom-11-eye-on-the-seat` and the step at bead start in `freedom-13-map-and-step`.
