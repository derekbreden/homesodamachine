# trials-10-human-labelled-jog: the human is the judge until a camera can be

No scene.

## Picture it

Motors move the dot in small steps. Derek stands where he stands to weld, watches the dot near the corner, and taps a keypad: good, or nudge up / down / left / right. Each tap is a label attached to the command that produced it and to the camera frames at that instant. After a few hundred labels a camera-based judge can be trained and tested against the human; when it agrees, the human steps out and returns for spot checks.

## The proposal

Command only, no automatic judge at first. The idea takes the hardest part of "an AI judges its own work" (what counts as on the seam) and gets it from the one person who currently defines it, in the same view he uses today. The pairs (frame, command, label) are the training set; the notch tube (trials-05) gives independent ground truth to check the human labels themselves.

## Carries, locates, free

Not chosen: any motorised positioner. The judge is the human eye plus the keypad.

## Software

- Command: small dot moves (jog), a request for a label.
- Observe: the keypad; cameras (recorded); later the trained judge's agreement rate.
- Manual: the labelling.

## Tried to break it

1. **The human cannot see the dot at the corner either.** Assumption: the hand-held view over the rim works. It is the view used to weld today, from above and to the side; it needs to be verified with the rig's own camera A. Leaves: the operator's line of sight with a gun in a support is not the same as with a gun in the hand.
2. **Label noise and drift.** A person's "good" wanders over an hour. Repair: repeat some poses at intervals; compare with the notch view. Leaves: how large the human's own scatter is.
3. **Fatigue and safety.** A person beside a moving rig. Repair: jog speeds low, deadman on the keypad (like the rotator's pedal **[repo]**). Leaves: not designed.
4. **What "good" means.** The label is "dot on the seam", which is not "weld is good" (`trials-11-arrangement-yardstick` for the relation).

## Combinations

`trials-11` uses the same labels as a benchmark; `trials-03` and `trials-05` replace the human where they can.

## Unresolved

Q: Would you accept 200 taps as the price of a trained judge?

## Assumptions

All **[illustrative]**.
