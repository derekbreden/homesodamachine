# use-07-two-stations: two stations, one head

Scene: `scenes/use-07-two-stations/index.html`. Origin: swarm. Maturity: rough. Arrangement A6 of the notebook; a branch of `use-02-swing-head`.

## Picture it

From above: two tubes on two rotators side by side, a rail behind them carrying a head that slides between the two seats, a second rail farther back with a small trolley from which the umbilical hangs, and the laser unit's cart at the bottom. A white curve is the umbilical; when it bends too tightly it turns red. On the right a schedule shows two tubes' worth of coloured blocks in lanes for the person, the head and each station.

## The proposal

Two rotators, one head that **translates** (does not rotate) along a rail so the gun keeps the same pose at whichever tube it visits, one seat per station. While one tube is in a hands-free state, the person prepares the other. The umbilical follows the head on a hook that is fixed midway, rides at half the head's displacement (a festoon trolley), or rides with the head.

## What carries the loads, what establishes position, what is free or restrained

Rail and carriage carry the head between stations; the seat at each station carries it while there and fixes the pose (as in the swing head). The cable hook is carried by its own trolley and rail. Free: the carriage along the rail; restrained at each end by a seat. Software: one new axis (the carriage) and its end-stops; each rotator keeps its controller.

## What software could command, observe, and what stays manual

Command the carriage; run each rotator. Observe carriage position and seat contact. Manual: everything in the hand lanes of `use-01-day-lanes`. The schedule is a picture, not a plan.

## What was tried to break it

1. **The fibre's bend radius against a moving head.** *Conflict:* 350 mm emitting at each seat and 240 mm stored in transit [manual p.20]. In a plan-view Bezier (conservative, since a climbing cable has a larger true radius), spacing 520 mm and a cart 500 mm beyond the rail, the requirement is met only with a rail about 1.0 m behind the tubes for a half-speed trolley, about 1.2 m for a fixed midway hook, and not at any tested rail distance (600 to 1500 mm) for a hook that rides with the head, because the run from that hook to the cart then bends by the head's whole travel (a longer run to the cart would help) (`calc/two_stations.mjs`). *Assumption:* the cable can follow the head. *Change:* the half-speed trolley halves the sideways miss; a longer, straighter run is what actually meets the radius. *Leaves:* the Bezier stand-in has no stiffness, weight or twist.
2. **Does a second station double the day?** *Conflict:* preparation needs the person, and one person can prepare only one tube at a time. With illustrative durations (prep 14, dry lap 1, weld and retract 1.1, swap 1 min) four tubes finish at 68.4 min on one station and on two if the dry lap needs a person, and at 64.4 min on two if the dry lap may run alone: the second station recovers only the dry lap. *Assumption:* parallel stations mean parallel work. *Change:* the schedule is drawn so the reader sees the overlap is only the hands-free window. *Leaves:* the real durations, and cool-down and PT, which may be the hands-free window that actually matters.
3. **Two of everything.** *Conflict:* a second station needs its own nest, ground shoe and purge routing. *Change:* listed under unresolved; not drawn.
4. **A swing would rotate the gun between stations.** *Change:* the head translates on a rail parallel to the row of tubes so the tangent approach is unchanged.

## Branches and combinations

Branch of `use-02-swing-head`. Combines with `use-03-preset-cartridge` (preparation off-station, but by the same person) and `use-05-gates` (whether the dry lap may run without a person, the assumption that decides the overlap).

## Unresolved problems and questions for Derek

- How many tubes per session; how long PT and cool-down take before a tube can be handled.
- Whether the row layout leaves the operator reach to both nests, indicators and shoes.
- Whether purge and work-lead routing for two stations fit.

## Assumptions

- **[manual]** bend radii 350 / 240 mm (p.20). **[repo]** the rotator footprint 300 x 250 mm and tube geometry.
- Illustrative: the gun's plan position (kit proxy, opening pose), spacing, rail and cart distances, Bezier stiffness, all durations, the greedy scheduler.

## Sourcing pointers

Rails and carriages of the printer class (MGN and T8 screw, extrusion): see `sourcing/use.md`.

Scene id: `use-07-two-stations`. Numbers: `explorers/use/calc/two_stations.mjs`.
