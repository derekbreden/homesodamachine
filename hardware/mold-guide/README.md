# Mold operations

[Illustrated shop guide](mold-guide.pdf): 22 Letter pages for casting the silicone
funnel and filling the cold core's two caps and body with polyurethane foam.
Each page has a large picture, short bench actions and a completion check or
process gate. It uses the [weld-rotator guide](../weld-rotator-guide/README.md)'s
one-picture-per-step approach and the approved Letter sheets' print calibration.

## Operations and pages

| Page | Bench operation |
| --- | --- |
| 1 | Identify the funnel cast and three cold-core pours |
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
| 17 | Stage the three 1:1 foam pours and the per-build quantity |
| 18 | Prepare and clamp the labeled top and bottom cap stacks |
| 19 | Mix each cap shot 1:1, pour, cure, trim and remove the fixture screws |
| 20 | Prove buried components, seat copper plugs and protect open paths |
| 21 | Mix the body shot 1:1 and pour it all at once through the open top |
| 22 | Trim after cure, fit reed columns/gaskets and close both caps |

The two cap pours are separate operations, with different depths and lid details.
Both use the shell's top face as their fixture. The body pour has no cap in place.
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
and [native tool check](../printed-parts/zone-c/funnel-mold/rod-check.json)
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
The core's brim-finishing pocket has 4.7 mm backing; ramp backing is at least
5 mm. The lower socket has at least a 5 mm floor. The flanges are 211 × 163.683 mm,
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

The acquired foam is FSD B08R7TX8QJ, two-part 2 lb density closed-cell PU,
mixed 1:1 in measured shots. Each cap pours bolted mouth-up to the shell's top
face, through its lid's 20 mm hole with air leaving by the two 6 mm vents. The
body pours all at once through its open top. A build fills about 5 L of risen
foam, about 4 L of cavity plus waste, which is about 1/7 of the 1 qt kit
([BOM](../ledger/bom.md)). The [cold-core procedure](../assembly/cold-core.md)
keeps the foam data-sheet details (pot life, cure time, pour temperature window)
and the trim method as open items. The body surrounds sealed components; no foam
enters the carbonator or reservoir liquid interiors. Reed channels, top conduits,
vents and the relief outlet remain open.

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
furniture lives in [common.py](../../tools/assembly-guides/common.py); its
[builder](../../tools/mold-guide/build.py) reads selected small source JSON for
dimensions and hashes the reviewed sources. It imports no geometry.

Requires Python 3 with ReportLab, Pillow and pypdf, plus Poppler's `pdftoppm`
available on `PATH` for covers and page rendering.

```sh
python3 tools/mold-guide/build.py
pdftoppm -r 110 -png output/pdf/mold-guide.pdf /tmp/mold-guide-proof
```

The builder writes the delivery PDF and source receipt in `output/pdf/`, then an
identical canonical PDF, cover and catalog sidecar here. Render and inspect every
page after editing; the builder rejects action text that exceeds its allotted box.

Letter is 8.5 x 11 in. Content is centered at 98%; the cobalt top and coral right
bands extend 0.25 in beyond the page and 0.333 in inward. Print at 100% / no scaling
using the Epson rear photo feeder, Letter borderless, glossy photo media and
single-sided high-quality color. The 98% compensation is already in the file.
