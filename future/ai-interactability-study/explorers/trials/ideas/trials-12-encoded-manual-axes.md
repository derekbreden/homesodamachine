# trials-12-encoded-manual-axes: software observes the hands, commands nothing

No scene. Sourcing: DRO scale and micrometer stage in `sourcing/trials.md`.

## Picture it

The stages that position the gun are turned by hand: micrometer heads or leadscrews with knobs. Each axis has a cheap digital scale or a magnetic encoder that the software reads. The AI tells the person what to do ("radial 0.30 mm up, height 0.10 mm down"), the person turns the knob, the AI sees the number change and the camera sees the dot move, and both are logged.

## The proposal

A partial version with **no motors**. Every hand move is a command-response pair that teaches the AI the Jacobian of the arrangement: how a millimetre on this knob moves the dot, in which direction, with what backlash. It also makes the human and the software into one system: the AI reads, advises, and is corrected. It is a way to start the study before any motor exists.

## Carries, locates, free

Hand stages (for example a 60 mm micrometer XY stage, `sourcing/trials.md`) between a fixed support and the shell; digital scales read position; a person supplies motion.

## Software

Observe: axis positions (scales), the dot (cameras). Command: nothing; advice on a screen. Manual: all motion.

## Tried to break it

1. **Humans are slow and cannot run overnight.** True: it is a stepping stone and a calibration source, not the goal.
2. **Encoders and scales read the axis, not the dot.** Backlash, deflection and tilt hide between axis and dot. Repair: the dot itself is measured by the judge; the axis reading is the input, not the truth.
3. **Micrometer stages are small.** A 60 x 60 mm stage is for fine adjustment, not for carrying a shell with its umbilical load. Leaves: how stiff the assembly is under cable pull.

## Combinations

`trials-08` (human in the loop), `trials-13` (the pivot trial by hand), `trials-10` (labels by hand).

## Assumptions

Prices and listings from `sourcing/trials.md` (one has two ratings: thin). Everything else **[illustrative]**.
