# eyes-19 Touch cue: a stylus that says "wall" with no estimate behind it

No scene. Origin: wave 3 new direction, a branch of `eyes-05-touch-off-interlock` and `freedom-12-touch-trigger`, hand-held. Maturity: sketch.

## Picture it

The gun rests on its friction arm or hangs in a ring, and the hand holds it. On the shell a short stylus with a printed three-contact seat stands beside the nozzle, its tip at a chosen standoff from the dot. When the tip touches the wall a small lamp on the shell lights and a beep sounds; which of three contacts opened says which side (wall, plate, or rim). Nothing measures the seam; the seam is the thing that is touched.

## The proposal

Every feedback channel in `eyes-18` except this one needs an estimate from the eye, and inherits its bias, its blindness and its lag. A touch trigger needs none: it is a switch (freedom-12: 0.06 to 0.36 N sideways, 0.5 to 1.5 N axial, repeatable to hundredths for steel balls, unmeasured for a printed seat), and its state is one bit of direction. In a hand-held arrangement it can be a **cue**: the hand slides the gun toward the wall until the lamp lights, then backs off by feel or by the scales; and it can drive a **wall** that is real rather than estimated: the brake of eyes-17, clamped by the stylus's own contact, refuses further motion into the wall with a latency of a millisecond plus the clamp. It is also the independent third look that tells the eye's bias from the hand's (the log of eyes-17 reads the difference between them; a touch reads neither).

## What carries the loads, establishes position, is free or restrained, drives

As the hand-held arrangement it sits on (the friction arm and stage of eyes-17, a ring suspension, an encoded arm). The stylus carries only its own preload spring; position is the seam itself at the instant of contact, registered to the tip, and the tip-to-dot vector is a calibration (eyes-06 or the sectioned tube, eyes-07). Free: the hand. Restrained: only as much as the trigger force and the overtravel spring (about 0.5 N/mm after the trigger). Driven: nothing.

## What software could command, observe, what stays manual

Command: the lamp and beep, optionally a clamp. Observe: which of the three contacts is open (a resistor ladder can put three on one wire), the slide scales at the trigger. Manual: fitting the stylus and seat, the standoff, the hand.

## What was tried to break it

1. **It says "at the wall", not how far to go.** Conflict: a contact is an edge, not a gradient: it is a limit cue, not a guide. Assumption: that a hand-held gun needs to be guided more than fenced. What the change alters: it is a fence; the eye's bar or the scales carry the gradient. What it leaves uncertain: whether a fence is what Derek's hand is missing.
2. **The stylus fits beside the nozzle in a canyon 8 mm from the wall.** Unknown (freedom-12 leaves it open).
3. **Spatter fouls the contact.** A 316L bore, a burnt copper nozzle beside it, a stylus tip a few millimetres from the puddle: contact resistance changes; a debounce and a threshold do not fix a fouled seat. Unmeasured.
4. **A stylus touching a turning tube drags** (a sliding steel ball at μ 0.3 drags 0.054 N on the wall, freedom-12): so the touch cue is for the stopped tube (a dry approach) or as a shoe that leans lightly (freedom-07), not for a rotating bead.
5. **Path stiffness** (eyes-05, entry 6): the position at the trigger is read on the gun side of every soft element (a scale on the slide), or the touch reads the support.

## Branches and combinations

`eyes-05-touch-off-interlock`, `freedom-12-touch-trigger`, `freedom-07-floating-on-work` (the shoe that leans is the same contact at a higher preload), `datum-04-corner-follower` (a ball feeler in the corner); `eyes-17-lit-bar-brake-wall` (the stylus as the wall's trigger); `eyes-18-what-the-estimate-owes` (its row).

## Unresolved problems, questions for Derek

Where the stylus fits; whether a steel ball at a fraction of a newton marks the inside of a 316L bore; whether Derek would rather have a beep, a lamp or a click in the hand.

## Assumptions

Trigger forces and repeatability are freedom-12's illustrative figures. Hand and cue timing as eyes-18.

## Sourcing pointers

Three steel balls, three small tactile switches or a resistor ladder, a printed seat, a buzzer and an LED are commodity parts (none priced here). Nothing sourced this wave.

## Scene

None: `freedom-12-touch-trigger` is the nearest.
