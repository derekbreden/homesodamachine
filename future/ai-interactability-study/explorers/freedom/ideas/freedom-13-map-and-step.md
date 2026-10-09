# freedom-13: map and step (a dry-turn map holds the periodic part; a step at bead start needs another corrector)

Scene: `scenes/freedom-13-map-and-step`. Origin: branch of `eyes-09-scan-then-weld` (developed) combined with `freedom-05-runout-table` (mine), drawn in wave 2 from the exchange `exchange/freedom--on--eyes-w2.md` (section 3). Depth: developed (a simulation with illustrative numbers; four break-and-repair entries). The compliance figures come from `calc/30-eye-support.cjs` and the cable numbers from `calc/31-cable-gauge.cjs`.

## Picture it

Two plots of the error at the dot along the bead: the whole lap, and the first 30 mm. Four traces: the map alone (grey), the map plus a force term (blue), the map plus the eye at the dot (amber), all three (green). At the start of the bead a step appears (the wire feeding, the gas starting, the fibre taking up a different bend) and only some of the traces take it out. A table gives rms, peak and the length of bead spent outside the tolerance.

## The proposal

eyes-09 and freedom-05 both replay a seam map keyed to the rotator's turned angle. That removes what repeats each lap. It cannot remove what differs between the dry turn and the bead, and one such difference is a **step in the support's position at bead start**: the support's compliance (mm at the dot per newton at the grip base) times the change of pull. Three correctors, each for the disturbance class it can see:

- the **map** (by angle): the periodic seam, tack bumps and ovality;
- a **force term** (by the reading of a load cell in the support): the step, as it lands, times a compliance table learned by nudging (borrowed-05's method);
- the **eye at the dot** (by the corner it sees): creep and whatever else is left, with its bias.

## What carries loads, what establishes position, what is free or restrained

Not a support scene; the support enters as its compliance per newton at the dot: 1.44 / 4.22 mm (r / z) for eyes-01's elastic with nothing holding rotation, 0.45 / 1.03 with a rigid base, about 5 / 5 for the friction arm, 0.10 / 0.01 for the nose seat at 70 mm. Position at each moment: the map by angle, the force term by the cell, the eye by the corner. The trim is one slow stage.

## What software could command, observe, and what stays manual

- **Command:** the trim axis as the sum of the three terms.
- **Observe:** turned angle (exists), the load cell (proposed), the eye's corner minus dot (proposed).
- **Manual:** the dry turn with the same hoses and cables present; learning the compliance table.

## What was tried to break it

**Entry 1. The step is bigger than everything the map removes.**
- Conflict: eyes-09's scan leaves 0.195 mm rms at the dot; 1 N of pull change on the drawn elastic is a 1.4 mm radial step, 4.2 mm vertical. On the nose seat it is 0.10 mm.
- Assumption (eyes-09's): the dry turn is representative of the bead. use-04 raised the same concern ("change since the dry lap") without a number; the number is force × compliance.
- Change: assign the step to a corrector that sees it.
- Leaves uncertain: the size of the step at bead start (Derek can measure it: laser disabled, dial gauge on the shell, jog the wire, open the gas).

**Entry 2. The eye takes a while.**
- Conflict: at gain 0.6 and 4 corrections a second an eye at the dot is back under a 0.15 mm tolerance after 6 mm of bead (peak 0.8 mm on the way; four corrections take 1.4 mm to 0.04 mm) and settles to its own bias (0.10 mm here), which it cannot see.
- Change: the force term acts as the step lands. With a compliance table 20 % wrong and 0.05 N of noise it removes 80 % of a 1 N step on the elastic (about 0.4 mm left over the first 30 mm, 0.29 of it from the table); together with the eye the error stays under the 0.15 mm tolerance.
- Leaves uncertain: whether the compliance table holds across poses; a cell in a soft support measures the support.

**Entry 3. Creep only the eye sees.**
- Conflict: bungee and printed-part creep (0.2 mm/min here, a slider) moves the dot over a lap; neither the map nor the force term sees it.
- Change: the eye. Or a support that does not creep (a stiff seat, not a stretched cord).
- Leaves uncertain: real creep, which was not measured.

**Entry 4. How much force there is to find.**
- Conflict: the pull is mostly the fibre's own recoil. A cable held to radius R pushes back about EI/R² (`calc/31`): 0.4 to 4 N at 350 mm and 0.9 to 8.7 N at 240 mm for EI 0.05 to 0.5 N·m². Opening a loop from 240 to 350 mm cuts it to 47 %. If the dry turn is taken with the fibre laid at the stored radius and the bead at the emitting radius, that alone is a step.
- Change: route to the largest practical radius, carry the weight by something other than the gun (travel-08's balancer, borrowed-11's festoon); lay the fibre the same way in the dry turn (the repo's disabled-laser rehearsal already asks for the same cables).
- Leaves uncertain: EI, weight per metre, hysteresis, and the wire conduit and gas hose beside it.

## Branches and combinations

- **freedom-15-pull-ledger:** what the sources of pull are and how to measure them.
- **eyes-11b (umbilical eyes):** the camera on the fibre as a pull gauge with a hysteresis flag (exchange section 4).
- **trials-02 (dock) and travel-08 (balancer line):** places a load cell already appears.

## Unresolved problems, and questions that need Derek's observation

- Does the gun's support or shell move when the wire is jogged or the gas opened, laser disabled? By how much?
- Does it move when the laser starts emitting (the fibre state)?
- The pull at the exit at the working pose (spring scale).

## Assumptions

- Runout 0.125 / 0.15 mm amplitudes and a 10 % second harmonic, tack bumps 0.06 mm, bead speed 5 to 15 mm/s, lap 388.6 mm plus a 20° overlap [repo]. Map residual 0.03 mm rms plus 0.05 mm scan bias; eye bias 0.10 mm, noise 0.03 mm, gain 0.6 at 4 Hz (eyes-01's numbers); step ramped over 3 mm; creep 0.2 mm/min; load-cell noise 0.05 N; compliance error 20 %: **illustrative**.

## Sourcing pointers

`sourcing/freedom.md`: load cell and HX711; the EISCO Newton force meter (spring scale) for the pull; a dial indicator is already in the shop (the 0.0005 in Neoteck, repo).

## Scene

`freedom-13-map-and-step`.

**Wave 3 note (from borrowed's exchange).** borrowed had nothing to add from its side on the map and the step. The step's size source is now a scene: `freedom-16-fibre-line` gives the change of torque and force at the release point for a far anchor that gives, a wire-feed push and a roll change, for four routes, so the bead-start step of this file can be read per route instead of assumed.
