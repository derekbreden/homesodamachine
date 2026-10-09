# travel-18-signature-parity: the dry turn must be the weld turn

Scene: `scenes/travel-18-signature-parity`. Origin: combination of `datum-02-seam-signature` and my `travel-02-cascade` with `use-10-wire-first` (exchange wave 2, section 2). Depth: developed. Numbers: `calc/10-signature-assign.mjs` (`calc/10-signature-assign.out`).

## Picture it

Two dry turns of the same tube. In the first nothing is feeding, the rotator turns, the dot is on. In the second the wire feeder jogs at weld speed, the gas flows, the laser stays off. The two constant terms differ by a few hundredths of a millimetre. That difference is what the hold did when the weld's forces arrived, and the replay uses the second turn's fit, so the weld turn starts from where the gun will actually be.

## The proposal

datum-02 learns the seam by turning, replays it while welding, and is silent on what holds the gun. The replay applies the dry turn's constant term to a gun that has to be in the same place in the weld turn. Anything that moves it between the two adds a constant the fit never saw: the change of force times the compliance of the chain from gun to room (wire feeder and its conduit starting, gas hose, the hand leaving, the fibre emitting). `calc/10`:

- With `calc/06`'s holders: 6 micron per newton (20 mm steel post, 300 mm), 44 (12 mm steel rod), 128 (12 mm aluminium rod). A 1 N change against the 12 mm rod is 0.044 mm, twice datum-02's 0.022 mm fit residual, the same sign every lap. A friction-locked joint is not a spring: 0.02 degree of creep at 250 mm is 0.087 mm whatever the force.
- A stage carried in the gun's shell is in series: 20 N/mm adds 0.05 mm per newton. To keep the parity term under 0.02 mm at a 1 N change the chain must be under 20 micron per newton (stiffer than 50 N/mm), stage included.
- **Repair: measure it.** A second dry turn in the weld's mechanical state; the constants differ by exactly the parity term (`use-10-wire-first`'s wire-inclusive dry run, applied as a parity check). What stays unmeasured is what only an emitting head does (vibration of its motor, heat).
- **Which terms need a per-revolution stage at all.** From datum-02's default tube (constants 0.20 and -0.15, 1x 0.13 and 0.15, 2x 0.05 and 0.03): the constants are two thirds of the uncompensated rms (0.29 mm); a static trim leaves 0.146 rms with peaks 0.18 mm, inside a +-0.30 mm window everywhere; nest screws taking 90 percent of the radial 1x leave 0.114; a Z follow taking the vertical 1x leaves 0.043. A replay stage earns its place below a window of about 0.2 mm, vertical first.
- **Backlash on a horizontal axis** shows at every reversal of a sinusoid: b/2 either side once the mean is trimmed (0.025 mm at 0.05). A vertical axis is loaded one way by weight; a horizontal one wants a preload or a flexure.

## What carries the loads, what establishes position, what is free or restrained

- Not drawn as hardware. The chain from gun to room carries; the follow stage should sit under the work, where it is not in that chain (`travel-02` round 4: fine stages under the work, nothing soft on the gun side).

## What software could command, observe, and what stays manual

- **Command:** both dry turns, the fit, the assignment, the replay. **Observe:** dot versus seam per angle in each dry turn (any sensor); the difference of the two turns. Blind: the weld turn itself.
- **Manual:** nest screws (or the driver of `travel-06`); hand-aim into the stroke.

## What was tried to break it

1. **Assumption: the gun does not move between turns.** *What the scene shows:* it does by the parity term; the scene's warning shows when it exceeds 0.02 mm and disappears with the second dry turn. *Leaves:* the emitting head.
2. **Assumption: a follow stage is needed.** *What the scene shows:* only below about 0.2 mm; *leaves:* the real window (unknown).
3. **Assumption: hot drift is small.** 0.05 mm over the lap leaves a ramp in the radial residual that nothing observes.

**Wave 3 entries, from use's exchange ("Also noticed").** **Which dry turn is the weld turn, and where its angle zero comes from (use).** *Conflict:* the parity turn must be in the weld's mechanical state; in guide 46's order that is the revolution after step 5 (speed set, index returned, shielding on, wire placed), not the step-4 continuity revolution. *Assumption behind it:* any dry revolution in the weld setup will do. *What the change alters:* the label and the text now say so; the replay's zero is the index mark (see `travel-02`), and the angle-zero slider tests it (0.022 mm at 10 degrees, inside 0.02 mm to about 5 degrees over three harmonics). *What it leaves uncertain:* what only an emitting head does.

## Branches and combinations

- With `travel-15-touch-stack`: the touch signature is a dry turn whose parity the same second-turn check tests. With `travel-14-exact-crown`: the crown's chain has its own compliance (ring seat, boom), the parity term applies to it too.

## Unresolved problems and questions for Derek

- Does the wire feeder push or pull on the gun's bracket when it runs (a hand on the gun)? Does anything visibly shift when the gas starts?

## Assumptions

- datum-02's illustrative terms with fixed phases; holder compliances handbook beam formulas, force at the tip; change of force, split, drift, backlash: **unknown / illustrative**.

## Scene id

`travel-18-signature-parity`
