# trials-15-one-tube-many-poses: swaps are the outer loop

No scene. The numbers are in `explorers/trials/calc/swap_budget.py`.

## Picture it

The AI loads one tube and does not swap it. It runs hundreds of trials on it, varying the approach direction, the start pose, the rotator speed and the support's state, and only then asks for another tube. Swapping is treated as an experiment in itself: re-seat the same tube ten times and see what the judge says.

## The proposal

Rig learning has an inner loop (everything that can vary without a swap) and an outer loop (tubes). The inner loop is cheap; the outer loop costs a person or a tool. Amortise it: with 120 s trials and a 10 minute swap, 20 trials per load keeps the rig busy 80 % of the time, 100 trials 95 % (illustrative). And treat the swap as its own variable: the *same* tube re-seated ten times gives the swap noise directly, separate from tube-to-tube variation.

## Tried to break it

1. **Confounding.** Many trials on one tube tie pose effects to that tube's quirks. Repair: block by tube, include a golden reference tube every session, randomise pose order within a block. Leaves: the number of tubes needed to average out tube quirks is **[unknown]**.
2. **Drift over a long block.** Anything that creeps grows over hours. Repair: the dock re-anchors (trials-02); the dot probe re-finds the seam (trials-03). Leaves: real drift rate.
3. **Wear.** Nothing wears in a dry run except the umbilical and the belts. Leaves: the umbilical's cycles.

## Combinations

`trials-02` (cheap cycles), `trials-08` (the loop with a person), `trials-17` (the trial card).

## Unresolved

Q: Roughly how many different tubes do you have to hand, and are more available?

## Assumptions

Times **[unknown]**, illustrative.
