# Mold operations

The illustrated shop guide covers casting the silicone funnel and insulating
the cold core. Each operation has a schematic, bench actions and a completion
check. [Shop guide](https://homesodamachine.com/read/mold-guide/mold-guide.pdf) · [Cold-core bench procedure](../assembly/cold-core.md)

## Operations and pages

| Page | Bench operation |
| --- | --- |
| 1 | Identify the funnel cast and both cold-core pours |
| 2 | Stage tooling, liquids, closure hardware and vacuum equipment |
| 3 | Clear bolt-pocket supports, drill infill breathers, finish forming faces and mask bare datums |
| 4 | Clean the stock 6 × 25 mm steel rod |
| 5 | Prove cure and release on the actual PETG/finish/pigment stack |
| 6 | Drop the rod into the cavity seat and lower the open core guide over it |
| 7 | Dry-close the bare parting lands with opposite flange stations |
| 8 | Apply and dry the release film |
| 9 | Measure A/B, pigment and the silicone batch |
| 10 | Degas mixed silicone with expansion room |
| 11 | Seat the rod, fill the cavity, lower the core and top up through the fill hole |
| 12 | Perform an optional equalized filled-mold vacuum cycle while fluid |
| 13 | Hold the assembled mold through room-temperature cure |
| 14 | Remove flange fasteners and open the tooling in alternating small movements |
| 15 | Pull the straight rod and trim outlet flash flush |
| 16 | Inspect and clean the funnel; check its installation |
| 17 | Prepare the bottom-cap and open-body pours |
| 18 | Bolt the bottom cap to the empty shell, mask the joint and invert the casing |
| 19 | Fill through the underside ports, cure, trim and patch |
| 20 | Prove buried components, seal the copper exits and dry-fit the B-fill locator |
| 21 | Protect the risers and dry passages and pour through the open body |
| 22 | Pull the locator, clear the approach, seat the lid and feed B-fill |

The bottom-cap pour uses the inverted empty shell. Return it upright with
the cap fastened before fitting the vessels. The body pour uses the upright
shell with its equipment lid on the bench.
The current reservoirs are printed PETG, and the floats are printed ASA Aero.
The [silicone reservoir concept](../printed-parts/cold-core/reservoir/silicone.md)
has no production mold or casting recipe; it does not supply a bench operation
in this guide.

## Process scope

The guide is an assembly aid, not a qualification receipt. Its diagrams are
vector schematics; dimensions named in the text govern. No figure is a drill,
cut or mold-finishing template.

Funnel tooling is two printed PETG mold bodies and one straight 6 × 25 mm steel rod. The
[mold procedure](../printed-parts/zone-c/funnel-mold/README.md),
[material record](../printed-parts/zone-c/funnel-mold/silicone.md),
[tool dimensions](../printed-parts/zone-c/funnel-mold/design.json)
govern its dimensions and handling order. Its
[physical print record](../printed-parts/zone-c/funnel-mold/print-log.md)
retains the recorded stock-dowel and printed-shell scopes.

The rod forms a uniform 6 mm cylindrical bore. The funnel grips the 6.35 mm
drain tube over its full 5.015 mm insertion. Clean the rod and apply release
agent. The PETG shells have a separate 0.30 mm normal finishing reserve.

Set the rod in the cavity's 6.4 mm seat, resting on its floor 1.5 mm below
the block-bottom face. Lower the core over it. The core's 6.4 mm guide is open
through the dry back and has 7.7 mm of bearing length. About 4.2 mm of rod
projects above it. Both seats have 0.20 mm nominal radial clearance.
The guide annulus is open during pouring; a small amount of silicone can
emerge there. Pull the straight rod after cure and trim outlet flash flush.

The section drawings show the 6 mm silicone collar and ramp beside the solid
mold stock. A flat cavity base and steep 63.4° corbel support the flange;
the core has a flat back with a tapered circular rod-access opening.
Print with six walls, six top/bottom layers and 15% gyroid. Drill the dry-side
infill breathers in the mold procedure after printing, leaving them bare.
The core's brim-finishing pocket has 4.7 mm backing. The lower socket has at
least a 5 mm floor. The flanges are 211 × 163.683 mm,
with 16 mm of margin around the funnel brim. The diagrams omit the thin
rod-seat clearance at full-mold scale; named dimensions and the finished
reference govern.

The native mold and M4 × 20 closing hardware fit within a 247.88 mm circle
and stand 70.35 mm high. The acquired chamber's recorded interior is
299.72 mm diameter and height, leaving 25.92 mm radial clearance. Keep the
fill, vents, rod access and drilled infill breathers open during slow cycling.

The purchased BBDINO 40A material record uses a conservative five-hour demold hold
and 24-hour full-use hold at 23 C. The direct manufacturer's current page gives
30 minutes of working time and a three-hour cure at that temperature. The guide
retains the project's five-hour hold, requires the actual batch instructions
and cured witness, and supplies no unqualified heating schedule. The finished
silicone/pigment/release/post-process mixture still needs the
[wetted-surface qualification](../printed-parts/cold-core/reservoir/wetted-surface-test.md).

### Foam pours

Use the FSD closed-cell PU kit specified in the BOM. Establish the measured
charge and distribution for each cavity from the foam-fill trials, and follow
the kit directions for handling and cure. Fill the inverted bottom cap through
its distributed ports with the vents open. In the upright body, keep the B-fill
approach, upper insert mouths and dry reed channels clear during the pour.
Pull the locator after cure. Seat the lid before feeding the final B-fill tube.
[Cold-core procedure](../assembly/cold-core.md) · [Foam-fill trials](../print-tests/foam-fill/README.md)

## Manufacturer sources

Reviewed 2026-10-04. Batch/container instructions govern the material actually used.

- [BBDINO 40A direct product page](https://bbdino.com/products/bbdino-40a-clear-silicone-mold-making-trial-kit-gp-platinum-cure-high-hardness): equal A/B by weight or volume, required degassing, and stated room-temperature working/cure windows.
- [Smooth-On Ease Release 200](https://www.smooth-on.com/products/ease-release-200/): clean tooling, light spray from six to eight inches, ventilation and handling protection.
- [Smooth-On sealer/release reference](https://www.smooth-on.com/page/sealers-releases/): light mist/brush/mist application. Application guidance does not establish the project's BBDINO/finish-stack compatibility.
- [Smooth-On vacuum-degassing example](https://www.smooth-on.com/tutorials/making-piece-cut-block-mold/vacuum-de-gassing/): expansion headroom above the mixed batch.
- [FSD 2 lb pour foam](https://fiberglasssupplydepot.com/Expandable-Polyurethane-Pour-Foam-2lb.html): acquired material family and equal-component description.
- [FSD pour-foam SDS](https://fiberglasssupplydepot.com/pour-foam-sds): dry handling, ventilation, skin and eye protection for the liquid components.

## Manual authoring and print

This document is hand-authored and committed. It is not a machine-build step,
CAD generator, card-sync target or publication derive operation. Its shared page
furniture lives in [letter.rs](../../tools/hsm/fabrication-guides/src/letter.rs); its
[native builder](../../tools/assembly-guides/guide.rs) reads the editable
[page records](pages.json) and selected source JSON for
dimensions and hashes the reviewed sources. It imports no geometry.

```sh
tools/run hsm-manual-guides build mold-guide
```

The builder writes the delivery PDF and source receipt in `output/pdf/`, then an
identical canonical PDF, cover and catalog sidecar here. Render and inspect every
page after editing.

Letter is 8.5 x 11 in. Content is centered at 98%; the cobalt top and coral right
bands extend 0.25 in beyond the page and 0.333 in inward. Print at 100% / no scaling
using the Epson rear photo feeder, Letter borderless, glossy photo media and
single-sided high-quality color. The 98% compensation is already in the file.
