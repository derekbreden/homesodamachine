# Home Soda Machine install guide

A 24-page, half-letter booklet following the owner quick start's seven steps. Published on
[Drawings](https://homesodamachine.com/drawings) and at
[install-guide.pdf](https://homesodamachine.com/docs/install-guide/install-guide.pdf).

| Pages | Content |
| --- | --- |
| 2-4 | Route, kit, counter opening and cabinet space |
| 5-6 | 1. Mount the faucet |
| 7-11 | 2. Add the cold-water tee: plastic tube or braided hose |
| 12-13 | 3. Match the rear connections |
| 14-15 | 4. Prepare the cylinder |
| 16-18 | 5. Water, then gas, then power |
| 19-20 | 6. Fill both flavors |
| 21 | 7. Chill. Choose. Pour. |
| 22-24 | Care, first checks, machine information and help |

The booklet is complete on its own. Its step numbers match the
[quick start](../quickstart-codex/README.md), whose braided-hose link opens pages 9-11.
The Fill spread shows the Big Blue screen inside the enclosure display's frame, with its
**Start filling** control. The same screen appears on the appliance in the bottle illustration.

## Artwork

The [On tap identity](../../brand/README.md) supplies cobalt, navy, ice and orange. Instructional
scenes use white paper, 0.6 pt slate contours (`#46515b`) and coral arrows with white outlines.
Tube and connector colors match the hardware. The power scene carries the white faucet mark on
its black nameplate. The glass contains dark cola and rounded ice cubes packed from the base to
just above the liquid, with a visible rim and no falling streams. The first-pour instructions
call for a glass filled with ice. The illustration is a snapshot of the quick start's
`ice_scene.py` render.

The concentrate bottle has a rounded PET body, tapered shoulders, an open ribbed neck, dark
liquid and a wrapped COLA concentrate label. The bottle and framed display are snapshots from
`tools/quickstart-codex/fill_scene.py`; `assets/fill-screen.svg` and its PNG supply the interface.
The cover shares the enclosure's matte black PET-GF appearance. Both Fill views use the same
exposure, and the complete frame has an uninterrupted outline.

The PDF, cover, fonts and illustration snapshots are committed here. `assets/` contains the
booklet's artwork, including its Fill-screen illustration and hose-removal scene. Manual page
composition lives in [`tools/install-guide/`](../../tools/install-guide/). `_install_art.py`
supplies shared CAD scene builders used by illustration tools; its output is in `art/`.

## Compose and review

From the repository root:

```sh
tools/cad-venv/bin/python tools/install-guide/build.py
pdftoppm -scale-to 1000 -png hardware/install-guide/install-guide.pdf hardware/install-guide/out/page
```

The composer writes the PDF, cover, document metadata and a copy in `output/pdf/`. It checks text
boxes against the footer and generates page-space contours from the saved artwork. `out/` holds
local renders and layout measurements. Review every rendered page at reading size before publishing.

## Print

The PDF contains 24 pages at 5.5 x 8.5 inches, in reading order. Print on US Letter at 100%,
two-sided, using the printer driver's booklet layout. This makes six folded sheets. Fold the
stack once and staple through the fold. Keep the print-production instructions with this source;
the owner pages carry the installation.

## Installation coverage

The guide describes the physical installation and the current Fill controls. First-use flavor-line
priming remains unresolved in appliance firmware: the Prime hold drives a pump without applying
a dispensing valve plan. The guide makes no automatic-priming claim. The controller path is
`firmware/src_appliance/machine.cpp` (`beginPrimePump`, `claimPump`, `pumpDrive`).

The refrigerant figure is the project's documented bound, under 40 g. A per-unit charge comes
from factory run-up. The manufacturing nameplate CAD still contains the glass mark; this guide's
power illustration uses the approved print faucet mark.
