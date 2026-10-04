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
| 3 | Remove supports, finish the shell forming faces and mask bare datums |
| 4 | Finish and measure the short contoured PETG pin's wet profile |
| 5 | Prove cure and release on the actual PETG/finish/pigment stack |
| 6 | Seat the pin in the cavity and dry-close its blind core seat |
| 7 | Dry-close the bare parting lands with opposite flange stations |
| 8 | Apply and dry the release film |
| 9 | Measure A/B, pigment and the silicone batch |
| 10 | Degas mixed silicone with expansion room |
| 11 | Seat the pin, fill the cavity, lower the core and top up through the fill hole |
| 12 | Perform an optional equalized filled-mold vacuum cycle while fluid |
| 13 | Hold the assembled mold through room-temperature cure |
| 14 | Remove flange fasteners and open the tooling in alternating small movements |
| 15 | Trim both blind-seat flash collars; withdraw the short pin toward -Z |
| 16 | Inspect and clean the funnel; check its installation |
| 17 | Record the actual foam-batch recipe for all three pours |
| 18 | Prepare and clamp the labeled top and bottom cap stacks |
| 19 | Mix/pour each cap shot, cure, trim and remove the fixture screws |
| 20 | Prove buried components, seat copper plugs and protect open paths |
| 21 | Mix/pour the body shot through the open top and connected foam zone |
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

Funnel tooling is the current cavity, core and short contoured PETG pin. The
[mold procedure](../printed-parts/zone-c/funnel-mold/README.md),
[material record](../printed-parts/zone-c/funnel-mold/silicone.md),
[tool dimensions](../printed-parts/zone-c/funnel-mold/forming-mandrel-design.json)
and [native tool check](../printed-parts/zone-c/funnel-mold/forming-mandrel-check.json)
govern its dimensions and handling order. Its
[physical print record](../printed-parts/zone-c/funnel-mold/print-log.md)
retains the recorded stock-dowel and printed-shell scopes. Those results do not
qualify the current finished pin, coated closure, vacuum cycle or full cast.

The pin is 20.765 mm long. Its finished wet profile forms the 8.4 mm entry,
6.7 mm relief, 6.0 mm by 3.0 mm sealing land and 6.35 mm upper throat.
A straight 6.35 mm steel dowel cannot form that 6.0 mm land. The pin's first
pilot millimetre and upper locating shank remain bare; its wet finishing reserve
is 0.05 mm normal to the surface. The mold shells use their separate 0.30 mm
reserve.

Set the pin in the cavity's 6.75 mm blind pilot seat, resting on its floor
1.5 mm below the block-bottom face. Lower the core over the pin. Its 6.75 mm
blind upper seat takes 7.7 mm of bare shank, with 0.20 mm axial roof clearance.
Its 1 mm tapered mouth guides the pin during lowering. If the pin binds,
lift the core and clear the seat before continuing.
Both seats have 0.20 mm nominal radial clearance. Their annuli breathe back
toward the casting as the core lowers; no pin passage opens into the dry back.
Any cured silicone in those seats is removable flash. Trim the bottom collar
flush with the block face and the upper collar at the throat before withdrawing
the pin toward -Z. Preserve the 6.0 mm sealing land.

The section drawings show the 6 mm silicone collar and ramp beside the roughly
5 mm PETG backing at sensible proportions. The core's brim-finishing pocket has
4.7 mm backing; its ramp uses the 5 mm minimum. The blind-seat hosts have
5 mm radial walls and caps away from their opening transitions. The short
pin and its closed boss sit inside the bowl height. The diagrams omit the thin
pin-seat clearance at full-mold scale and enlarge the flash in the trimming
sequence; named dimensions and the finished reference govern.

The purchased BBDINO 40A material record uses a conservative five-hour demold hold
and 24-hour full-use hold at 23 C. The direct manufacturer's current page gives
30 minutes of working time and a three-hour cure at that temperature. The guide
retains the project's five-hour hold, requires the actual batch instructions
and cured witness, and supplies no unqualified heating schedule. The finished
silicone/pigment/release/post-process mixture still needs the
[wetted-surface qualification](../printed-parts/cold-core/reservoir/wetted-surface-test.md).

### Foam recipe gate

The acquired foam is FSD B08R7TX8QJ, two-part 2 lb density closed-cell PU.
Its official product page describes equal parts but does not establish a
complete batch-specific processing recipe. The
[cold-core procedure](../assembly/cold-core.md) leaves mix details, pot life,
cure, pour temperature and trim method open. No calibrated liquid shot sizes
for the top cap, bottom cap and body are recorded.

Before mixing, the batch record must identify its ratio and measurement basis,
liquid/room temperature, measured A/B amounts for each pour, mixing and working
window, expansion allowance, release/cure hold and trim method. The preparation
and pour sequence is illustrated; mixing and pouring are held until this recipe
is available. The nominal cavity volume or foam density alone does not select
the liquid dose. The body surrounds sealed components; no foam enters the
carbonator or reservoir liquid interiors. Reed channels, top conduits, vents
and the relief outlet remain open.

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
