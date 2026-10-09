# use-09-programmed-table: the tube follows a program, the hand holds the gun

No scene yet (arrangement A2 of the notebook). Origin: swarm. Maturity: sketch. It appears as a column in `use-01-day-lanes`.

## Picture it

The operator holds the gun on a plain rest and presses the pedal. Instead of turning until the pedal is released, the table runs a small program: index eight tack positions in the opposite-side order and stop at each for a tack, turn one dry lap at weld speed, then run a bead of 380 degrees and stop by itself. The console prints the degrees at each stop.

## The proposal

Software moves the tube and observes nothing but its own degrees. The rotator controller already has the pieces: a stored speed, a direction, a degrees readout, and a pedal deadman [repo firmware README]. Add **programs** that run only while the pedal is held: `index 8` (45 degree steps in the opposite-side pattern, waiting at each), `lap` (360 degrees at the stored speed), `bead 380` (380 degrees, then stop). The hand still carries and aims the gun; the pedal stays the live stop and never commands the laser.

The gain is not precision of the weld but repeatability of the day: the same tack angles, the same lap, the same bead length every time, recorded.

## What carries the loads, what establishes position, what is free or restrained

Unchanged: the hand and a rest carry the gun; the rotator carries the tube. The controller holds the motor while the table turns and for ten seconds after release [repo].

## What software could command, observe, and what stays manual

- **Command:** the table by degrees (existing motor, new firmware behaviour).
- **Observe:** degrees turned; the pedal state. Nothing else.
- **Manual:** everything the hand lanes show.

## What was tried to break it

1. **The repo's design rule.** *Conflict:* "the pedal is the whole of the control ... the lap length is a judgement made at the index mark, watching the puddle, not a number the controller enforces" [repo]. *Assumption:* the rule is settled. *Change:* the programmed table would enforce a bead length; that changes a choice Derek made deliberately, so it is offered as a *dry-run and tack* facility first (indexing and laps, where nothing is at stake) and the bead length remains the operator's judgement unless he decides otherwise. *Leaves:* his call.
2. **Indexing accuracy.** *Conflict:* stopping at 45 degree steps depends on the drive's step accuracy (0.025 degrees per pulse [repo]) and belt backlash and the plate's own slip on the nest. *Change:* nothing to do at the tack pattern's tolerance; verify with the degrees readout and a paper mark. *Leaves:* real stop accuracy.
3. **The hand still holds.** *Conflict:* nothing changes for the hand: 26 to 78 s of holding. *Change:* none: this arrangement changes time and angle, not the support (see `use-06-coach-loop`, `use-02-swing-head`). *Leaves:* it is a partial contribution.
4. **A program that starts by itself.** *Conflict:* an unwanted start is a hazard. *Change:* programs run only while the pedal is held and refuse to arm until the pedal has been seen released, as the controller does now [repo]. *Leaves:* nothing.

## Branches and combinations

- Combines with `use-08-flight-recorder` (the program's steps and degrees are the record's timeline) and with `use-04-the-lap` (a program that runs lap 1 slowly for a dry lap and lap 2 at weld speed is the replay idea's clock).

## Unresolved problems and questions for Derek

- Do you want the controller to know the lap length, or should it stay a judgement? (Your rule stands unless you change it.)
- Is the tack pattern the opposite-side bisecting one in the repo, and is each tack a fixed dwell?

## Assumptions

- **[repo]** the controller (speed window 5 to 15 mm/s, 14,400 pulses per table revolution, 0.025 degrees per pulse, pedal deadman, degrees readout, console at 115200 baud, hold for ten seconds after release), the tack pattern and the 20 degree overlap.
- Illustrative: the program names.

## Sourcing pointers

None: firmware only, on parts already owned.

Scene id: none yet.
