# use-06-coach-loop: software watches, a hand moves

Scene: `scenes/use-06-coach-loop/index.html`. Origin: swarm. Maturity: developed. Arrangement A3 of the notebook, with instrumented manual axes.

## Picture it

The gun rests in its shell on a small two-knob stage on the end of a magic-arm-class friction arm, locked. Each knob carries a digital scale. A camera looks at the dot and the seam; a screen says "knob X plus 4 notches, knob Z plus 1 notch". A hand turns the knobs, the camera looks again, and a small chart shows the error stepping down inside a band. Beside it a histogram says how many rounds 200 simulated loops took.

## The proposal

Where a motor would go, put a person, and give the person a measuring instrument. A manual axis with a digital scale is, to software, an axis whose motor is a hand: it can be *instructed* ("go to X = +0.40") and *witnessed* (the scale reads back), and every setting becomes a number in a log. The arm gets the gun into the working neighbourhood by eye and locks; the fine stage, **downstream of the lock**, trims two axes (radial and vertical) by a few millimetres while a camera estimates the dot's offset from the seam and the software rounds the advice to the knob step. Orientation (the three rotations) is set once per campaign by the shell adjusters and is not in this loop. Nothing here is motor-driven and no new actuator is bought.

It is the cheapest arrangement that gives an AI a repeatable way to set, record and re-set a pose, and it is the natural stepping stone to motors: the same error signal (camera estimate) can drive a motor later.

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** gun, shell, fine stage, friction arm (two links and a ball joint or two), post, bench. The stage carries only the gun's small offset relative to the arm's end.
- **Position:** the arm's locked joints set the neighbourhood; the two knob screws set the fine position; the camera's estimate of the dot against the seam is the reference the loop closes on.
- **Free / restrained:** the arm is free until locked; each stage axis is free under its knob and restrained by the screw (with whatever backlash it has).
- **Driven:** nothing. **Manual:** coarse aiming, knob turning, locking, trigger.

## What software could command, observe, and what stays manual

- **Command:** nothing that moves; the existing rotator turns the tube for the lap the camera watches.
- **Observe:** the camera estimate of the dot against the seam (with its noise), each knob's scale, the pose after the arm lock (only through the camera).
- **Advise:** which knob and how many notches.
- **Manual:** coarse arm aiming, turning, locking, the trigger.

## What was tried to break it

1. **Lock shift.** *Conflict:* the first version locked the arm every round; a lock shift comparable to the window (0.20 mm against a 0.10 mm window) left 39 percent of loops unconverged after nine rounds (`calc/coach_loop.mjs`). *Assumption:* aim, lock, verify is the loop. *Change:* put the fine axes downstream of the lock: the arm is locked once and the knobs trim after it. Then a 0.40 mm arm lock shift barely matters (2.1 rounds either way) and what limits the loop is the camera noise and any shift the stage itself suffers each round (a stage that shifts by as much as the window each time it is locked never converges: 38 percent unconverged at 0.20 mm). *Leaves:* whether a real micrometer-type stage holds without a lock of its own.
2. **Camera noise against the knob step.** *Conflict:* advice chases noise if the camera's error exceeds the knob step. Illustrative figures: 0.02 mm noise gives 1.3 rounds; 0.05 gives 2.1; 0.10 gives 3.7 with 14 percent unconverged; 0.20 gives 4.6 with 59 percent unconverged. *Change:* average frames (costs seconds); or a coarser advice step. *Leaves:* the real camera error at the seam, which a dot in a 6 mm recess against a wall may make large or impossible from any convenient viewpoint (the eyes explorer's question).
3. **By eye only.** *Conflict:* with no camera and no scales the same loop needs about five rounds and fails 85 percent of the time at a 0.35 mm eye error; 59 percent at 0.15 mm. Shown as a branch, not a verdict: an experienced hand may do better than these guesses.
4. **Per-tube re-aiming.** *Conflict:* the arm has no seat, so after each swap it is moved and must be re-aimed (the coarse-error slider is what the hand leaves each time). This is the running cost of a supported gun without a seat. *Change:* none inside this idea; `use-02-swing-head` is the branch that removes it. *Leaves:* how long re-aiming takes per tube.
5. **Payload.** A magic arm is sold as a camera arm; the X1 Pro gun's mass is unknown, so whether the arm holds it without creep is unknown (`sourcing/use.md`).

## Branches and combinations

- Branch of the same idea with digital scales replaced by AS5600 encoders on the knobs (`sourcing/use.md`) or by a linear-scale DRO strip.
- Combines with `use-03-preset-cartridge` (the screw advisor for the tube's centring is the same loop on different axes) and with `use-02-swing-head` (the swing head's campaign trim is exactly this loop, once per campaign instead of once per tube).
- The by-eye branch is today's practice with a rest.

## Unresolved problems and questions for Derek

- How long does aiming take now, per tube and per campaign?
- The gun's mass (a kitchen scale is enough).
- Whether the operator can see, or a camera can be placed to see, both the dot and the corner line in the recess.

## Assumptions

- **[unknown]** camera error at the seam, hand accuracy, lock shift, stage backlash, arm creep.
- Illustrative: every noise number in the scene and in `calc/coach_loop.mjs`; the 0.05 mm knob step; the coarse aiming error.
- **[repo]** the accepted runout limits and the three-screw centring are the source of the tube-centring version of the same loop (`calc/screw_advisor.mjs`).

## Sourcing pointers

`sourcing/use.md`: SMALLRIG 9.8 inch magic arm kit (3K+ bought in past month; camera-class payload), XYZ 60 mm micrometer stage, Neoteck indicators, AS5600 encoders, a 150 mm 5 micron DRO scale kit, Arducam UVC camera.

Scene id: `use-06-coach-loop`. Numbers: `explorers/use/calc/coach_loop.mjs`.
