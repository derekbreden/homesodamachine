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
| 22-24 | Care, connection checks, flow and power checks, machine information |

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

`install-guide.pdf` is the reading copy: 24 pages at 5.5 x 8.5 inches, in reading order, no bleed.
It is what the site publishes.

`press/` is what a printer is sent, and the composer writes it on every run:

| File | Size | Holds |
| --- | --- | --- |
| `press/cover.pdf` | 11.25 x 8.75 in, 1 page | Back cover left of the centre line, front cover right |
| `press/interior.pdf` | 5.75 x 8.75 in, 24 pages | Reading pages 2-23, then two blanks |

Both carry Lulu's 0.125 in bleed on every outside edge; the cobalt ground and the band at each
page's head run out into it. The cover has no spine: saddle stitch folds the cover around the
interior. Ordered as Print Book, Digest, paperback saddle stitch, premium colour, 80# coated
white, matte cover.

The two blanks carry 22 reading pages up to the multiple of four a saddle-stitched signature
takes. They land at the back, with the unprinted inside back cover after them. Printed folios
and the page references in the text agree with each other; the blank inside front cover carries
no number, so the reader's "page 9" is the page whose footer says 9.

The whole booklet cannot be printed on the ET-8550: its driver offers no borderless pass with
two-sided printing, and offers two-sided printing for plain paper only.

## Installation coverage

The guide describes the physical installation and the current Fill controls. First-use flavor-line
priming remains unresolved in appliance firmware: the Prime hold drives a pump without applying
a dispensing valve plan. The guide makes no automatic-priming claim. The controller path is
`firmware/src_appliance/machine.cpp` (`beginPrimePump`, `claimPump`, `pumpDrive`).

No owner support phone number, email address or dedicated support URL is configured.

The owner gas checks cover locating a leak and closing the supply. The gas disconnection
procedure is not published. External CO2 pressure release needs verification on the supplied Wellbom
B0G13P5PMY. The cylinder nut, gray flare connector and red tether/bulkhead joint all sit
upstream of the appliance's GASHER check valve. A verified procedure must establish the
cylinder-valve, outlet-shutoff and pressure-adjustment positions for manual relief, and
confirm zero pressure in the red tether as well as at both gauges before disconnection.
The exterior CAD does not show the regulator's internal gas paths or any outlet check valve.
Closing the cylinder alone is not a pressure-release procedure.

The refrigerant figure is the project's documented bound, under 40 g. A per-unit charge comes
from factory run-up. The manufacturing nameplate CAD still contains the glass mark; this guide's
power illustration uses the approved print faucet mark.
