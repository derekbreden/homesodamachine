# use-08-flight-recorder: every hand-held weld is an experiment record

No scene yet (arrangement A1 of the notebook). Origin: swarm. Maturity: sketch. It appears as a column in `use-01-day-lanes`. A candidate for a wave-2 scene.

## Picture it

The operator welds exactly as today. A small camera on a bracket watches the seam, the ESP32 in the rotator prints its degrees line, and a tap on the trigger circuit (or a light sensor on the gun's status LED) time-stamps when the laser was on. After the PT and hydro result is typed in, one row exists: speed, direction, degrees at release, the dot-versus-seam trace against angle, how long the trigger was held, the result. Nothing moves and nothing is commanded.

## The proposal

Software observes and moves nothing. Every weld, hand-held as today, is logged as an experiment: what the hand did (camera trace of the dot against the seam, per degree of rotation), what the machine did (rotator degrees and speed, from the controller that already reports them [repo]; trigger and laser-on time), and what came out (PT, hydro, later a section). The log is what an AI can read today and what any later mechanism has to beat or reproduce. A hand-aimed dry lap becomes worth doing because it is recorded and joined to the result.

It is the cheapest arrangement and uses only what is owned or cheap: the rotator's serial console at 115200 baud [repo], a UVC camera (`sourcing/use.md`), an ESP32 for the trigger tap.

## What carries the loads, what establishes position, what is free or restrained

Unchanged: the hand carries and aims the gun. The camera bracket carries the camera on a post (the position of the camera is the reference for the trace; it must not be moved between welds without recording it).

## What software could command, observe, and what stays manual

- **Command:** nothing new; the existing rotator.
- **Observe:** rotator degrees and speed; camera view of the dot and the seam; trigger or laser-on times; the result, typed in.
- **Manual:** everything a hand does today, plus typing the result.

## What was tried to break it

1. **The camera cannot see the dot in the recess.** *Conflict:* the dot at a 6 mm recess against a wall is hidden from outside viewpoints (see the reference scene's line-of-sight test and `use-11-setup-gauge`). *Assumption:* one camera position gives the dot and the seam. *Change:* place the camera above the far rim looking down and across, as the reference scene's proposed camera does; or use the gun-borne view of another explorer (`eyes-01-gun-borne-eye` exists by name; not read). *Leaves:* real fume, light and reflection.
2. **A trace without a result is noise.** *Assumption:* results are available. *Change:* the joined row needs PT and hydro (the repo already does them [repo]); the recorder makes the record automatic but the result is still typed. *Leaves:* how many welds until the pose trace says anything about defects; a handful of coupons would not.
3. **Nothing changes the day.** *Conflict:* the recorder adds no actuation, so the hand-held sequence still has the hand holding for 26 to 78 s. *Change:* none, deliberately: this is the baseline that the other arrangements are measured against and the source of the pose distributions a later mechanism should meet. *Leaves:* it is a partial contribution and says so.
4. **The trigger tap.** *Conflict:* tapping the trigger circuit could interfere with the welder's safety chain. *Assumption:* an external, non-invasive sense exists. *Change:* prefer a light sensor on the gun's status LED or a current clamp on the mains lead (non-invasive); modifying the gun's electronics is not proposed. *Leaves:* whether the status LED is a reliable indicator of emission.

## Branches and combinations

- Combines with `use-05-gates` (the observation half of the decision half) and `use-04-the-lap` (the recorded dry-lap trace is the map that a later replay would use).
- Combines with `use-09-programmed-table` (the table's program is the record's other half).

## Unresolved problems and questions for Derek

- Would you type the result into a log after each PT? (The record needs it.)
- Is there a viewpoint from which you can see the dot when you weld now, and could a camera sit there?

## Assumptions

- **[repo]** rotator console (status, speed, direction, degrees); PT and hydro after each weld; step 8 already asks for speed, direction, degrees at release and runout to be recorded by hand.
- **[unknown]** whether a status LED or current sense is reliable for emission timing.
- Illustrative: nothing numeric.

## Sourcing pointers

`sourcing/use.md`: Arducam UVC camera (Prime, 100+ bought in past month); the rotator's ESP32 is already owned [repo].

Scene id: none yet.
