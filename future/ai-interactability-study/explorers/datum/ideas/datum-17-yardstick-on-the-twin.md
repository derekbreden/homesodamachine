# datum-17-yardstick-on-the-twin: the hand measured on a clear twin, machines touched at rest

Scene: `scenes/datum-17-yardstick-on-the-twin/index.html`. Depth: developed. Origin: combination of `trials-11-arrangement-yardstick` (idea), `datum-10-clear-twin` (idea) and `trials-05-artefact-ladder` (notch rung; scene). Exchange: `exchange/datum--on--trials-w2.md` section 3.

## Picture it

Two small sections of the same corner: a steel tube, where an outside camera cannot see the dot (the wall hides it), and a clear twin with a printed plate at the real recess, where it can, all the way round. Below, a lap of one arrangement (the hand, a friction arm, a map replay, a rigid stand): the true dot-to-seam error dashed, what the judge reads solid, and for machines the touches at rest as dots. A table of verdicts against the requirement, with the ones that disagree with the truth marked.

## The proposal

`trials-11` scores any way of holding the gun with one judge and one script and starts with Derek's hands, so that the requirement is what a competent hold delivers. That is the right instrument with a circle in it: the judge is a camera over the bore that sees the dot on the plate a millimetre from the wall; whatever it gets wrong that repeats with table angle reads as seam. An arrangement built on the judge (a map learned from its readings and replayed) reproduces that error, and the judge reads the replay at its own noise floor.

Three sources answer three different questions:

- **The clear twin** (see-through wall, printed plate at the recess): an outside camera sees the corner. The **hand is scored on the twin with no judge in the number**: this is the requirement. A tremor and a drift are properties of the hand, not of the tube.
- **A notch tube** (`trials-05` rung 3, a 34 degree window): the same for about five seconds of a 49 second lap. Enough to calibrate a judge's gain by jogging the dot to known offsets; too little to score a hold.
- **K touches at rest** (a stylus or the wire, `datum-07`, `datum-14`): a machine arrangement's true error on the real tube at K azimuths. A moving hand cannot be touched.

The judge stays dense in time. It is used for what it can see (comparisons that do not depend on what it is built on), never alone for an arrangement built on it.

## What carries the loads, what establishes position, what is free or restrained

Nothing carries the gun here; whatever holds it is what is scored. Position is read from the twin's outside camera and printed corner (truth), from touches (truth at K angles) and from the judge.

## What software could command, observe, and what stays manual

- **Command:** the rotator; the touch sequence at rest; the scoring script (the same for every arrangement).
- **Observe:** the judge every 0.25 s; on the twin the outside camera; K touches.
- **Manual:** holding the gun for ten laps over the twin; making the twin; deciding whether the hand's number is the requirement.

## What was tried to break it

Error models are illustrative shapes (hand: follows 85 per cent of the wobble, drift 0.045 mm with a 6 s memory, tremor 0.02; friction arm: none of the wobble, steps of 0.04 mm every 7 s; replay: the judge's bias imprinted plus 0.012; rigid stand: the wobble). What the yardstick is for is measuring them.

1. **The requirement read by the judge includes the judge.** At a bias of 0.04 mm (harmonics 1 and 3) and a 15 per cent gain error the hand's true rms of 38 micrometres reads as 68; at 0.10 mm bias, 109.
2. **An arrangement built on the judge cannot be scored by it.** The replay's true error is the bias: 36 micrometres at 0.04, 52 at 0.06, 85 at 0.10; the judge reads it at 33 to 35 (its noise floor). The hand's true error is 38. At a bias of 0.06 mm the judge passes a replay the truth fails, whatever source measured the requirement. With K = 8 touches at rest the replay scores 67 and fails correctly.
3. **A notch tube is a window, not a lap.** 34 degrees is 17 of 196 samples and about one memory time of the hand's drift; the hand's rms from it has a 10 to 90 per cent band of 21 to 40 micrometres (true 38 over the lap); the twin's band over a full lap is 35 to 60 over 80 draws.
4. **The twin is not this tube.** A clear wall and a printed plate do not reproduce glare on polished 316L, fume or a hot bead; the twin fixes the requirement and the judge's geometry, not this tube's surface. *Neighbour:* `eyes-07` (sectioned tube) gives a static section view at one gun pose; the twin gives every azimuth of a turning tube with the hand in the loop.
5. **Refraction.** Through a 2.5 mm acrylic wall a point appears shifted 0.145 mm at 10 degrees off the wall normal, 0.48 at 30 (`datum-10`); view along the wall normal.
6. **Left standing:** a dry-run hold is not a weld hold (the eye follows the puddle and the wire); a raw rms may overstate the tremor if the puddle averages errors faster than about 4 Hz; touching cannot score the hand.

## Branches and combinations

- Uses `trials-11`, `datum-10`, `trials-05`, `datum-14` (the touch check on the judge's bias), `datum-07` (the touch). Related: `use-12-golden-tube` (a reference tube each morning), `eyes-07`, `trials-17` (trial card).

## Unresolved problems and questions for Derek

- Would you hold the gun for ten laps over a clear twin, in a dry run, with the camera watching? How far off the seam can the dot be and still weld well? Can you see the dot from where you stand through clear acrylic?
- Twin: the shelf tube (125 mm ID, 130 mm OD, 6 in) has a bore 1.3 mm larger than the steel's; a printed twin with a clear wall could match the bore exactly. Which?

## Assumptions

Lap 49 s at 8 mm/s `[repo]`, 196 samples; wobble 0.125 mm at once per turn and 0.03 at twice (rig limits `[repo]`; phases illustrative); the models above; touch noise 0.02 mm.

## Sourcing pointers

`sourcing/datum.md`: clear acrylic tube (125 mm ID, 130 mm OD, Prime, 76 ratings) and the wave 1 camera and probe entries.

## Scene id

`datum-17-yardstick-on-the-twin`.
