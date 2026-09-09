# Home Soda Machine install guide

Twenty half-letter leaves, saddle-stapled, published as `install-guide.pdf` on `/drawings` and
packed face up in the install kit. The quick start lies on top of the packing and draws the six
actions; this guide carries everything those actions stand on. What each document owns is
[`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md).

## The contract with the sheet

**The guide never redraws an action the sheet draws.** Where the two meet the guide names the
step by the numeral it wears there, on a round of that sheet's field, and stops. One fact has one
home, so the two documents cannot drift apart, and a buyer holding both is never told the same
thing twice in two voices.

That makes the sheet's six clusters this booklet's spine. Everything here is either before
`1`, alongside a step, or after `6`:

| Leaves | |
|---|---|
| 2–7 | before the first action: how to read the two documents, the kit, what the buyer brings, the whole path, the opening, the cabinet |
| 8 | alongside `1` `2` — the seat the sheet cannot show, and why the tubes stay long |
| 9–11 | alongside `3` `4` `5` — which kitchen the buyer has, and the older path the sheet does not draw |
| 12–15 | the four things the sheet has no scene for: the filter, the cylinder, the ports read by name, the cord |
| 16–20 | after the last push: the first hour, keeping it, the ratings, what to check, and where service lives |

## How it is drawn

The palette is the quick start's, unchanged, because the two are read in the same hour. Warm
stone `#ded7cd` is the sheet's field, so a stone disc on a page here is a step on that sheet, and
nothing else in the booklet is round. Coral `#d64050` is the sheet's cue color: here it rules the
lockup and marks the one thing on a leaf that will bite, and it is never decoration. Blue, red,
white and black name fluids and nothing else — the four the bulkhead rings wear.

**This guide draws no CAD of its own.** Every picture in it is a view
[`../quickstart/`](/hardware/quickstart/README.md) has already cut, from the same solids, so a
change to the machine reaches both documents through one set of renders. The older-kitchen spread
is the four registered scenes in
[`../quickstart/plumbing/`](/hardware/quickstart/plumbing/README.md); the appliance, faucet and
rear-panel plates are `../quickstart/art/`. The one drawing made here is the path map on leaf 5,
an inline SVG, because the thing it shows — seven crossings on one face, and where each one comes
from — has no camera.

Art is a background on an empty box, never an `<img>`. A crop is then a background rectangle
rather than an element hanging out of a clipped parent, which is the one shape the renderer's clip
gate cannot tell from a mistake.

Every leaf wears `.card > header|main|footer`, which is the anatomy the renderer's spill gate
measures: a leaf whose text outgrows its page fails the build rather than printing short.

## The words

The words in this booklet are the words on the parts — `TAP`, `CO2`, `SODA`, `FLAVOR`, the
nameplate, the collar flags. [`/NAMES.md`](/NAMES.md) governs what this tree calls its own
geometry; where the tree's name is not a word the buyer can see, this guide uses what they can see.
"The back of the appliance" is the +Y wall of back-top, and a buyer holding the booklet against
the machine can find it.

## Build

From the repository root:

```sh
tools/cad-venv/bin/python hardware/install-guide/_build.py
```

One page per HTML file: the renderer prints page 1 of each and nothing else, so a leaf that
paginates loses its tail. The bound order is the `PAGES` tuple in `_build.py`, and it stays a
multiple of four because the booklet folds in fours.

## Print

The PDF is in reading order; the imposition is the printer driver's. Print on US Letter, plain
stock, at 100 %, **two-sided with the driver's own booklet layout** — that is the setting that
puts leaves 20 and 1 on one side of the first sheet and folds twenty half-letter pages onto five
letter ones, and it sets the duplex flip itself. Fold the stack once down the middle and put two
staples in the fold.

Check the fold falls between spreads and not through one, that the older-kitchen pair (10 and 11)
lands on a single opening, and that a grayscale copy still separates the coral callouts from the
artwork behind them.

## What this guide does not yet state

Every leaf here says only what the tree knows. These are the places a buyer would want a sentence
and there is no sentence to give, listed so the booklet is not mistaken for complete:

- **The wrench spec on the older-kitchen tee.** Its two threaded joints are the only ones the buyer
  makes, and no wrench size, tightening figure or PTFE-tape policy is stated for them anywhere in
  the tree. Leaf 11 says snug and a little more, which is what a compression nut on its own washer
  wants and is the most that is true today.
- **A kitchen whose stop is not 3/8 inch.** The kit holds one older-path tee and it is 3/8". Leaf 11
  sends anyone else to the consultation, and no second adapter is specified.
- **Mounting the regulator on the cylinder.** No CGA-320 make-up is written. Leaf 13 hands the job
  to the shop that fills the cylinder, which is true advice and not a procedure.
- **CO2 cylinder handling.** No standing, restraint, storage or valve guidance exists in the tree.
  The line on leaf 13 is the minimum a shipped document can responsibly carry, not a stated policy.
- **The filter.** Flow direction and mounting are unstated; leaf 12 leans on the run shipping made
  up, so direction is never the buyer's choice. No flush-before-first-use procedure exists.
- **The outlet.** No dedicated circuit, GFCI receptacle or extension-cord rule is stated. Leaf 15
  says what the bonding actually depends on and no more.
- **The charge mass.** "Under 40 g" is what [`regulatory.md`](/business/regulatory.md) supports;
  the per-unit figure comes off the first run-up
  ([`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)). Leaf 18 prints the bound.
- **The flame symbol and the flammable-refrigerant marking.** Both are SNAP conditions on the
  *unit*, and the [nameplate](/hardware/printed-parts/enclosure/nameplate/README.md) letters
  neither. Leaf 18 carries the refrigerant and charge-mass statement, which is the condition on
  *instructions*; where the two on-unit markings go is owned by nothing.
- **The first hour.** Leaf 16 describes the appliance as designed. What of it runs today is not
  settled in one place: [`firmware/src_appliance/README.md`](/firmware/src_appliance/README.md)
  carries the funnel fill, the clean cycle and the dry cycle as glass-facing operations, while
  [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md) open item 1
  says `src_appliance/` runs one flavor pump and nothing else. One of the two is stale. Nothing
  drives the compressor either way, so the chill behind that leaf is not exercised.
- **Service.** Leaf 20 sends the buyer to the link the nameplate letters. No warranty term, RMA
  path, support address or `/u/NNNN` route exists.
- **The CO2 setpoint band.** Leaf 13 repeats the tree's own customer guidance verbatim —
  [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) "CO2 supply": set the primary
  anywhere in 70–100 PSI, because the in-appliance WR1110 holds the appliance side at 90 PSI
  "regardless of where the primary is set". A fixed 90 PSI regulator can only reduce, so a primary
  left at 70 gives the carbonator 70 and not 90. Either the band or the "regardless" wants
  revisiting upstream; the leaf follows whichever the tree lands on.
- **The CO2 station's bulkhead ring.** Leaf 13 tells the buyer to find a red-ringed port.
  [`bulkhead-ring/README.md`](/hardware/printed-parts/enclosure/bulkhead-ring/README.md) gives that
  ring its colour and the rear-panel render draws it, while
  [`y-wall-of-back-top/README.md`](/hardware/printed-parts/enclosure/y-wall-of-back-top/README.md)
  open items still say the ring waits on its own bulkhead. One of the two is stale.
- **The cold kit's own guide.** Named on leaf 17, in [`bom.md`](/hardware/ledger/bom.md) §14 and in
  the pack-out, and not written.
