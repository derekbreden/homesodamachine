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
| 2–7 | before the first action: the two documents, the kit, the opening, the cabinet, the whole path |
| 8 | alongside `1` `2` — the seat the sheet cannot show, and why the tubes stay long |
| 9–11 | alongside `3` `4` `5` — which kitchen the buyer has, and the older path the sheet does not draw |
| 12–15 | the four things the sheet has no scene for: the filter, the cylinder, the ports read by name, the cord |
| 16–20 | after the last push: the first hour, keeping it, the ratings, and where service lives |

## How it is drawn

The palette is the quick start's, unchanged, because the two are read in the same hour. Warm
stone `#ded7cd` is the sheet's field, so a stone disc on a page here is a step on that sheet, and
nothing else in the booklet is round. Coral `#d64050` is the sheet's cue colour: here it rules the
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

Print `install-guide.pdf` on US Letter, plain stock, **duplex, flip on short edge**, at 100 %,
with the driver's own booklet imposition — the PDF is in reading order and the driver puts the
leaves on the sheets. Five sheets. Fold the stack once across the short axis and put two staples
in the fold. Check the fold falls between spreads, that the older-kitchen pair stays on one
opening, and that a grayscale copy still separates the coral callouts from the artwork behind
them.

## What this guide does not yet state

Every leaf here says only what the tree knows. These are the places a buyer would want a sentence
and there is no sentence to give, listed so the booklet is not mistaken for complete:

- **The older-kitchen tee's 1/4-inch joint.** No ferrule, nut or tube insert is called out for the
  HAOCHEN's compression outlet anywhere in [`bom.md`](/hardware/ledger/bom.md) — the one stiffener
  the build buys is spoken for at the Westbrass. Leaf 11 describes the joint without naming its
  parts, which is the most that is true today. Wrench sizes, tightening spec and whether PTFE tape
  belongs on any customer joint are equally unstated.
- **Which stops scenario B fits.** `bom.md` "External / user-supplied" says a 3/8" *or 1/2"* angle
  stop; the part and [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) say 3/8"
  only. Leaf 11 sends a buyer with anything else to the consultation.
- **How the white run reaches a scenario-B tee.** [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md)
  §6 ties that run into the PP0208E's branch at the bench, and the older kitchen does not use that
  tee.
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
- **The first hour.** Leaf 16 describes the appliance as designed. `src_appliance/` runs one
  flavour pump and nothing else today
  ([`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md)), so no
  fill, chill or pour behind that leaf is exercised yet.
- **Service.** Leaf 20 sends the buyer to the link the nameplate letters. No warranty term, RMA
  path, support address or `/u/NNNN` route exists.
- **The cold kit's own guide.** Named on leaf 17, in [`bom.md`](/hardware/ledger/bom.md) §14 and in
  the pack-out, and not written.
