# use-14-handover-shift: where the millimetres go

Scene: `scenes/use-14-handover-shift/index.html`. Origin: combination of `travel-05b-soft-drive-hard-lock` and `freedom-01c-master-per-axis` (branch of travel-05b and freedom-01). Maturity: developed. Numbers: `explorers/use/calc/w2_handover.mjs` (same model as the scene).

## Picture it

One axis at the dot, followed through the states of a closure. In each arrangement the gun changes owner a few times and each change shifts it: hand to arm, arm to clamp, arm to bungees, arm to seat. The scene draws the gun's position after each state, what moved it, and the distribution of the final position over 2000 closures.

## The proposal

**The last look must come after the last handover.** use-06 found it for a lock; every handover is one. Four arrangements: **A** an arm that grips and stays; **B** travel-05b's soft drive and clamp; **C** Derek's rings and bungees once the arm lets go; **F** a three-ball seat for comparison. Two toggles carry the argument (look again after the clamp; a dry state that carries the weld loads) and a third the AI's advantage (learn the mean shift over many closures and subtract it).

## What carries the loads, what establishes position, what is free or restrained

- **Carries and locates:** the last stiff element engaged in each state: the arm, the clamp, the seat; the bungees only carry and hold a neighbourhood.
- **Free / restrained / driven:** the arm axis or soft-drive anchor is driven in steps; the clamp is closed by software; bungee anchors move to null the arm force in case C.

## What software could command, observe, and what stays manual

- **Command:** arm axis or anchor, clamp, bungee anchors. **Observe:** dot vs seam by camera with noise; arm force by a load cell in case C. **Manual:** the hand's first placement; choosing springs, clamps, seats.

## What was tried to break it

1. **B with no look after the clamp:** 81 percent inside +-0.10 mm; with a look-and-relock loop 95 percent. With a clamp bias of 0.08 mm: 49, 82, and 81 (learned, no look).
2. **The friction dead band costs rounds, not accuracy** (median two rounds; 15 percent use five or six).
3. **A on a 5 N/mm arm:** the weld load change (1 N) is 0.19 mm at the dot: 1 percent inside; with the dry state carrying the loads 93 percent; 20 N/mm 87 percent.
4. **C:** the release shifts the gun 0.77 mm RMS; nulling the arm force first cuts it to 0.11 mm, but a soft spring cannot be nulled better than 0.05 N / 0.15 N/mm = 0.33 mm, and 1 N then moves it 6.7 mm. Stiff bungees (3 N/mm) give 0.33 mm, at which point they are an arm.
5. **F:** one handover wipes the hand's error out; 99 percent inside.

## Branches and combinations

- `room-13-load-change-budget` (the load change divided by stiffness) is the partner: this scene is the same division inside a sequence. `travel-18-signature-parity` (a second dry turn in the weld state) is the same rule for the signature. `freedom-06-lock-and-release` is the family. Borrowed from `borrowed-05-guide-star`: the idea of learning a bias by nudging and watching.

## Unresolved problems and questions for Derek

- What does a clamp, cam or magic-arm knob do to a dot when tightened (indicator on the shell, tighten, read)?
- What does the gun move by when the wire feed starts and the gas comes on (spring scale at the grip base, before and after)?
- What window does the weld tolerate?

## Assumptions

- All shifts, stiffnesses, friction, noise, load change and window are illustrative; the soft-drive and clamp figures are travel-05b's defaults, the arm and bungee figures freedom-01's. Coulomb friction; no creep or heat.

## Sourcing pointers

None needed.

Scene id: `use-14-handover-shift`.
