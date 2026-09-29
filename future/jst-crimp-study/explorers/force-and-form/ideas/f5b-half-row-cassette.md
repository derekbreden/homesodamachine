# f5b — Half-row cassette: crimp every other cavity at 5.0 mm, merge the two half-rows at 2.5 mm, insert once

Explorer: force-and-form. A combination: force-and-form's
[`f5`](f5-die-cassette-and-the-shop-press.md) (self-stopping steel cassette,
any press, inspection before force) with change-the-question's
[c1](../../change-the-question/ideas/c1-half-rows.md) (split into two planes,
half-rows at twice the housing pitch, real-wafer test), and for the insertion
ribbon-as-pallet's merged row (K4 in
[its reading of force-and-form](../../../exchange/ribbon-as-pallet--on--force-and-form-w3.md))
with into-the-housing's [i3](../../into-the-housing/ideas/i3-converging-shuttles-gang-push.md)
(the housing moved onto the whole row).
Sketch: [`../sketches/f5b-half-row-cassette.svg`](../sketches/f5b-half-row-cassette.svg) (schematic).
Numbers:
- [calc wave2 §9], [calc gang §n], [calc final §n], [calc FP §7], [calc on_ith §n]:
  force-and-form's [`wave2`](../calc/wave2.out.txt), [`gang`](../calc/gang.out.txt),
  [`final_w3`](../calc/final_w3.out.txt),
  [`exchange_procedure_w3`](../calc/exchange_procedure_w3.out.txt) and
  [`on_into_the_housing`](../calc/on_into_the_housing.out.txt) outputs;
- [RP w3 §n]: ribbon-as-pallet's
  [`exchange_on_force_and_form_w3.out.txt`](../../ribbon-as-pallet/calc/exchange_on_force_and_form_w3.out.txt);
- [change-the-question calc off §n]:
  [`on_force_and_form.out.txt`](../../change-the-question/calc/on_force_and_form.out.txt).

**[Prime]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.

## Picture it

- **The cassette.** f5's two-post steel die set with five stations at 5.0 mm,
  twice the XH pitch. The upper shoe carries one EDM-cut crimper plate with five
  B profiles; the lower shoe carries a ground anvil block and, in front of the
  anvils, five **steel pockets**: a slot the shape of the box, a relief for the
  lance, open on top. Two stop blocks set how far the shoes close. Each pocket's
  anvil is insulated from the shoe and wired.
- **The ribbon pallet** sits on three balls on the lower shoe, so the web
  clamp travels with the shoe from the loading bench to the press and back.
  Its clamp face is exactly the split root (ribbon-as-pallet a7's tear stop),
  so folding a plane back never peels the web further.
- **Loading plane A, at a bench under the ELP camera.**
  1. Loose contacts go into the pockets box-first: kit contacts by tweezers,
     pushed off a post bar in key order in one stroke (terminal-supply a4,
     procedure-is-the-machine's posts), or from a tapped pocket plate
     (machine-that-sees-and-learns v4b). The lance relief takes a contact one
     way round only; the camera checks each pocket.
  2. The ribbon end is split into two planes, odd conductors up and even down
     (change-the-question c1's jaws, or by hand). The even plane is folded down
     and back under the clamp.
  3. A **grooved fan block** comes down on the odd plane from the root. Its
     grooves start at the plane's own 3.4 mm pitch, where the conductors
     already lie, and open to 5.0 mm, so it captures each conductor where it
     lies and carries it outward. The capture's only limit is the ribbon's
     pitch stack at the root, 0.23–0.43 mm against 1.7 mm of half-pitch
     [RP w3 §2].
  4. The end is **stripped after the spread**, at the fan block's face
     (ribbon-as-pallet a8 rolls a row under two razors at any pitch), so every
     insulation edge is on one line. Stripping flat while webbed and then
     spreading pulls outer tips back: 0.02–0.11 mm for rows of 2–3 and
     0.14–0.42 mm for rows of 4–5 with straight diagonals over 12–20 mm
     [RP w3 §2]; force-and-form's S-bend model gives 0.03–0.13 and 0.17–0.51
     [calc FP §7]. Rows of 2–3 can take the webbed strip; rows of 4–5 cannot.
  5. A presser comb lays each conductor into its open barrels. J2's empty
     cavity 3 is an empty pocket.
  6. The camera looks down at every open barrel: strands in the U, none over a
     wing tip, insulation edge in the window. Each insulated anvil reads, through
     the far-end port (ribbon-as-pallet a6), which conductor lies in it.
- **Crimp plane A.** The cassette goes under the 1 t arbor press (rows up to
  three at the high force estimate, four and five at the central one), the shop
  press, or a motor screw, and closes to its stops.
- **Park plane A.** The pockets are open on top, so plane A's crimped contacts
  lift straight out, and the plane folds back over the clamp face.
- **Plane B.** The pockets are reloaded, the even plane unfolds, and steps 3–6
  and the stroke repeat.
- **Merge and insert.** Both crimped half-rows unfold into a printed 2.5 mm
  comb in front of the pallet. Each plane was spread about the ribbon's centre
  by 5.0/3.4, so the two interleave at exactly 2.5 mm [RP w3 §1], and crimped
  contacts fit side by side there (0.45–0.7 mm between insulation crimps
  [calc final §8]). A housing held in a nest on the same pallet is moved onto
  the whole row in one push (into-the-housing i3): every contact latches at the
  same distance from the web, as it was crimped, so no conductor needs stored
  feed.
- **Test.** The housing goes onto a board-type male XH wafer read by a
  microcontroller against the far-end port.
- **The person** loads pockets, splits and lays each half-row, pulls the press
  or starts the screw, parks and unparks the planes, and makes the housing
  move. Twenty strokes and about thirty calls per unit [calc wave2 §9;
  change-the-question calc off §7].

## Why the half-rows are merged, not pushed in turn

Every conductor of a ribbon end has the same length from the web, so every
latched contact sits at the same distance D from the web. A half-row pushed from
pockets at the housing's rear face travels the insertion stroke, 6–9 mm
[RP w3 §1]. A straight lay stores at most ~0.4 mm. So:
- with the web fixed, the first push pulls each crimp toward the web in the
  pull-out direction, or drags the ribbon through its clamp;
- with the web following the push, the other plane's contacts are carried to D
  with it, which is inside the housing, and can never reach their cavities'
  rear entries.

Pushing half-rows in turn needs 6–9 mm of stored feed in every conductor of the
second row: a hump 4.7–7.7 mm tall over a 10–20 mm chord [RP w3 §1], inside a
split that already holds the fan block and presser. That branch is recorded,
not developed.

## What locates what

- **Fixed** is the lower shoe. Its pockets locate the loose contacts
  (box slot and lance relief); the guide posts locate the crimper plate; the
  stop blocks set crimp height.
- **Conductors:** the grooved fan block laterally (±0.1 mm at its face), the
  strip line after the spread axially.
- **At the merge:** the 2.5 mm comb, then the housing's own cavities.

## Force and steel

| Row | Force at the stop (low / central / high) | 1 t arbor press (~8.9 kN) |
|---|---|---|
| 2 | 1.6 / 3.4 / 4.9 kN | yes |
| 3 | 2.3 / 5.0 / 7.3 kN | yes |
| 4 | 3.1 / 6.7 / 9.7 kN | central only |
| 5 | 3.9 / 8.4 / 12.2 kN | central only |

[calc wave2 §9]. Per unit: ten T4 rows of two, and J1 (5+4), J2 (2+3), J4
(4+3), J6 (3+2), J7 (4+3): twenty strokes for 53 crimps, 68 % of them in rows of
three or fewer.

- **One crimper plate, not five crimpers.** Five separate crimpers of
  3.5–4.4 mm outer width at 5.0 mm leave 0.6–1.5 mm of steel between them
  [calc gang §1]. Cut as one EDM plate with five channels, the web between
  channels is 5.0 − 2.0 = 3.0 mm at the insulation profile and 3.5 mm at the
  conductor profile.
- **Matched heights.** Station crimp heights must agree to ~0.01 mm. A plate
  from one program at a good shop holds that; one at ±0.05 mm does not, and
  then each anvil is a separate ground-stock blade on its own shim
  ([`f7`](f7-where-the-steel-comes-from.md)).
- **Unbalanced rows.** A row of two in a five-station cassette loads the shoes
  off-centre: ~100–200 N of side load on posts 60 mm apart, a few microns of
  tilt at the outer station [calc gang §3]. Unused stations close empty to the
  stop; crimp height is a positive gap, so their dies never touch.
- **Lance relief** in every pocket and at the front of every anvil.

## How it knows

- **Before the stroke:** the camera per station, and identity per station
  through the insulated anvils and the far-end port. A conductor in the wrong
  station, the fault the summed force cannot name, is caught here.
- **During:** the summed force, with the row's expected occupancy setting the
  band, so an empty J2 pocket is not read as a missing conductor. The sum sees a
  missing conductor in a row of two or three (a 13–20 % drop if an empty barrel
  keeps 40–60 % of its force [calc gang §4]).
- **After:** a sample crimp height by caliper or micrometer; the housing push's
  force trace (lance fold, snap, bottoming); the wafer test.

## Printed and bought

| Part | Printed or bought | Evidence |
|---|---|---|
| Crimper plate, five B profiles | wire EDM | Not priced; JLCCNC states ±0.05 mm, Xometry quotes "in days" [source, via f3] |
| Anvil block, pockets | ground stock on edge and EDM | [`f7`](f7-where-the-steel-comes-from.md) |
| Shoes, posts, bushings, stop blocks | steel, laser-cut and bought | SendCutSend [source]; [Prime: 10 mm rods $17.99, bronze bushings $11.99] |
| Press | 1 t arbor press, the shop press, or a motor screw | [Prime: VEVOR AP-1, $61.90, 150 mm opening, 281 ratings]; VEVOR 12 t on hand [repo] |
| Balls and magnets for the pallet seat | bought | [Prime: 6 mm chrome steel balls $6.65; N52 10 × 3 mm magnets $23.99] |
| Fan blocks, presser comb, 2.5 mm merge comb, housing nest, pallet | printed | — |

## Branches

- **Both half-rows in one shoe at housing pitch (the shoe as insertion
  pallet).** Pockets at 2.5 mm; plane A, once crimped, stays in the odd pockets
  while plane B is loaded into the even ones and crimped beside it; the whole
  row is then pushed straight out of the shoe into the housing. The crimper
  plate carries a relief groove over each of plane A's crimps: walls of 0.90 mm
  at the conductor step (channel 1.50, relief 1.70) and 0.57 mm at the
  insulation step (channel 1.85, relief 2.00) [calc final §6]. The conductor
  walls hold (the rule is 0.7–0.85 mm, [calc on_ith §3]); the insulation walls
  see only 30–130 N. What fails is catching plane B's **open** wings beside
  plane A's **crimped** barrels: the insulation flare's mouth must be as wide as
  the open wings, which leaves 0.22 mm of plate edge at 2.46 mm wings, 0.10 mm
  at 2.7 and nothing at 3.0, and 3.0 mm wings touch a 2.05 mm crimp. With
  JST-sized wings it works; with the widest clone wings it does not. Tacking
  plane B first (change-the-question c1c) narrows its wings and removes the
  conflict.
- **Store the stroke in humps** (two pushes kept): above; recorded, not
  developed.
- **Cut the planes to different lengths** with a two-level fan block: the
  finished loom would carry 6–9 mm of bow in half its conductors. Recorded,
  not developed.

## What each side brings

- **From f5:** the self-stopping cassette that makes any press a precision
  press; inspection of every barrel before any force; one push per row.
- **From c1:** the split into planes, crimping at twice the insertion pitch,
  and the wafer test.
- **From ribbon-as-pallet and into-the-housing:** the ribbon pallet as the
  travelling datum, stripping after the fan, the root-capturing fan block, the
  merged row and the housing moved onto it.
- **What the combination changes in f5:** the split is 12–20 mm long instead
  of 25–40 mm; loose kit contacts become usable with no strip.

## Contribution

- **Crimp at twice the insertion pitch, in steel that does not have to be
  thin**: 3 mm webs in a one-piece crimper plate.
- **Loose kit contacts in an automated gang.**
- **Per-station identity** in a gang, through insulated anvils.

## How it connects to the whole procedure

| Step | Who does it |
|---|---|
| Split into planes | c1's jaws, or the person |
| Strip | after the spread, at the fan block's face |
| Supply contacts | the person, or a post bar pushed into the pockets |
| Place conductors | the grooved fan block and presser, checked by camera and identity |
| Crimp | one press stroke per half-row |
| Merge, insert | the person parks and unparks; one housing move inserts the whole end |
| Test | a real XH wafer |

## Major unresolved problems

- **Split length** behind the housing (12–20 mm), Derek's call.
- **An EDM crimper plate** with five matched profiles, and its price.
- **The insulation step is fixed** for all five stations in a one-piece plate,
  so it is chosen once from [`f6`](f6-two-blades-two-drives.md)'s sweep.
- **Parking and unparking** the crimped planes, and whether a straight loom
  unparks into the 2.5 mm comb with no pick (J4 and J7 need into-the-housing
  i6's sort).
- **Lifting crimped contacts out of the pockets** when the box slot is only a
  little longer than the box (an ejector pin under each box).
- **Pocket loading time** for loose contacts.
- **Rows of four and five** at the high force estimate need more than 1 t.

## Which conclusions rest on assumptions

- **Forces** rest on the modelled family, 0.78–2.43 kN per contact.
- **The empty-barrel share** (40–60 %) that the summed-force check depends on
  is assumed.
- **Pocket orientation by lance relief alone** is unproven on kit contacts
  (ribbon-as-pallet a2c raises the same doubt).
