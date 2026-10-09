# Home Soda Machine install guide

A 9 × 7 inch landscape booklet with **32 numbered interior pages** and seven illustrated
installation steps. The 34-page reading PDF includes the front and back covers. Published
on [Drawings](https://homesodamachine.com/drawings) and at
[install-guide.pdf](https://homesodamachine.com/docs/install-guide/install-guide.pdf).

| Numbered interior pages | Content |
| --- | --- |
| 1–4 | Welcome, route, kit and cabinet space |
| 5–8 | 1. Prepare the opening and mount the faucet |
| 9–16 | 2. Add the cold-water tee: plastic tube or braided hose |
| 17–18 | 3. Match the rear connections |
| 19–21 | 4. Prepare the cylinder |
| 22–24 | 5. Water, then gas, then power |
| 25–27 | 6. Fill both flavors |
| 28–29 | 7. Chill. Choose. Pour. |
| 30–32 | Care, water connections, gas and first-pour checks |

The booklet covers installation and care. Braided-hose instructions begin on numbered page 13
(PDF page 14). Connection checks begin on numbered page 31 (PDF page 32).
The faucet has four attached tubes, including the small white 4 mm OVER tail.
Numbered pages 7–8 (PDF pages 8–9) show the seated plate from below, with a shared
rear narrow slot for both black flavor tubes, white OVER and the flat display ribbon.
The front wide slot carries the shank; the blue SODA tube connects beneath it.
The vector slot map follows the purchased steel DXF and production line positions.
Its washer and nut are omitted to expose both openings; the adjacent mounting scene
shows their assembled order.
The mounting-hole center sits at most 2 inches behind the bowl edge, with the faucet
aimed within 10 degrees of straight into the bowl and its complete drain opening exposed
above the bowl. OVER keeps its factory length and connects to its own labeled metric port.
Numbered page 3 shows every supplied kit item as a vector line drawing, with a compact
customer-supplied checklist in the sidebar. Each item sits inside a light panel with its caption
centered just beneath the drawing. A towel catches residual water at a loosened fitting.
The Fill pages show the Big Blue screen inside the machine display's frame, with its
**Start filling** control. The same screen appears on the machine in the bottle illustration.
The owner lifts the funnel cover by its front edge before the bottle goes in and presses it
back down after **Filled**. Page 30 has the funnel and both faces of its cover washed by hand.
The cabinet dimensions include the seated 3 mm funnel-cover plate.

The mounting illustrations use a nominal 30 mm countertop and approximate retained
washer and nut envelopes. Complete clamp engagement and maximum supported countertop
thickness remain open in the [mechanical concerns](../concerns.md). The 19–38 mm
geometric routing envelope measures tube and plate clearance.

## Artwork

The [On tap identity](../../brand/README.md) supplies cobalt, navy, ice and orange. Instructional
scenes use white paper, 0.72 pt slate contours (`#46515b`) and coral arrows with white outlines.
Tube and connector colors match the hardware: each bulkhead ring and tube collar is drawn in
its PET-GF spool color with its raised word. The power scene carries the white faucet mark on
its black nameplate. The glass contains dark cola and rounded ice cubes packed from the base to
just above the liquid, with a visible rim and no falling streams. The first-pour instructions
call for a glass filled with ice. The illustration comes from
`tools/install-guide/ice_scene.py`.

The concentrate bottle has a rounded PET body, tapered shoulders, an open ribbed neck, dark
liquid and a wrapped COLA concentrate label. The bottle and framed display are snapshots from
`tools/install-guide/fill_scene.py`, whose funnel and display positions follow the current
enclosure assembly. The funnel is drawn without its lift-off cover, as it stands during a fill.
`assets/fill-scene-inputs.json` records the source hashes and motion cue;
`assets/fill-screen.svg` and its PNG supply the interface. The display cover shares the
enclosure's matte black PET-GF appearance. Both Fill views use the same exposure, and the
complete frame has an uninterrupted outline.

The PDF, cover, fonts and illustration snapshots are committed here. `assets/` contains the
booklet's artwork, including its Fill-screen illustration and hose-removal scene.
`assets/print-resolution.json` registers crop and arrow coordinates against the native artwork
dimensions. The back face, rear connections and bottle scene use higher-resolution snapshots
from their registered cameras; each entry identifies its native coordinate reference by hash.
`assets/reference/` retains the native Fill views, and `assets/kit/` holds the kit SVGs.
[`kit_art.py`](../../tools/install-guide/kit_art.py) exports hidden-line views of the component
models with a common 0.68 pt pen at page size. Small machine surface details and dial lettering
are suppressed; the cord, washer, bag and booklet are illustration props.
`assets/opening-faucet-outline.svg` supplies the faucet shank and tube silhouette in the
counter-opening scene. Its dimensions and source hash register it to `opening.png`; the contour
compositor adds the component boundary where it meets the counter.
[`opening_scene.py`](../../tools/install-guide/opening_scene.py) renders the current opening,
four tube tails and display cable, then registers the component silhouette from the same pose.
Manual page composition lives in [`landscape.py`](../../tools/install-guide/landscape.py),
with the build entry point and print exporter in [`tools/install-guide/`](../../tools/install-guide/).
`_install_art.py` supplies shared CAD scene builders used by illustration tools; its output is
in `art/`.

## Compose and review

From the repository root:

```sh
tools/cad-venv/bin/python tools/install-guide/fill_scene.py --publish
tools/cad-venv/bin/python tools/install-guide/fill_scene.py --scale 2 --publish
tools/cad-venv/bin/python tools/install-guide/kit_art.py
tools/cad-venv/bin/python tools/install-guide/opening_scene.py
tools/cad-venv/bin/python tools/install-guide/build.py
tools/cad-venv/bin/python tools/install-guide/preflight.py --json hardware/install-guide/out/landscape/preflight.json
pdftoppm -scale-to 1000 -png hardware/install-guide/install-guide.pdf hardware/install-guide/out/landscape/page
```

The composer writes the reading PDF, print PDFs, thumbnail and document metadata. Copies for
ordering are in `output/pdf/`. It checks text boxes against the footer and generates page-space
contours from the saved artwork. Native illustration resolution must be at least 300 PPI at
the placed size. The preflight checks the finished PDFs' dimensions, page order,
fonts, images and reading links. `out/` holds local renders and layout measurements. Review every
rendered page at reading size before publishing.

The composer and preflight use the CAD Python environment with ReportLab, Pillow, pypdf and
pdfplumber, plus Poppler's `pdftoppm` and `pdfimages` commands.

## Print

`install-guide.pdf` is the reading copy: front cover, interiors numbered 1–32, then back cover,
all trimmed to 9 × 7 inches without bleed. PDF page labels match the printed interior numbers;
bookmarks and the route page link to each installation step.

`press/` holds the two Lulu upload files, written on each build:

| File | Size including bleed | Holds |
| --- | --- | --- |
| `press/interior.pdf` | 9.25 × 7.25 in, 32 pages | Numbered interiors 1–32, one page per PDF page |
| `press/cover.pdf` | 18.382072 × 7.25 in, one spread | Back cover left, 0.132072 in spine, front cover right |

The full-bleed interiors and outside cover have Lulu's 0.125 in bleed on every outer edge. The
cobalt ground and each page's head band extend through it. The plain cobalt spine uses Lulu's
perfect-bound formula `(32 / 444) + 0.06` inches and carries no small text. Inside covers are blank.

Lulu settings are **Print Book, Small Landscape 9 × 7, Paperback Perfect Bound, Premium Color,
80# White — Coated, Matte**, quantity **3**. Lulu uses a fixed 100# laminated paperback cover.
The 32-page count is the interior upload count; the outside cover is uploaded separately.

The interior retains embedded vector text and flattened RGB illustrations. The outside cover
is flattened at 600 PPI. An embedded sRGB profile calibrates both PDFs. Critical text is at
least 0.5 in from the trim; print files contain no links or printer marks.

[Order instructions](press/ORDER.md) identify the two upload files, configured Lulu project,
page arrangement and production-preview checks. The order bundle in `output/pdf/` includes
those instructions, both upload PDFs, the reading copy and SHA-256 checksums.

The whole booklet cannot be printed on the ET-8550: its driver offers no borderless pass with
two-sided printing, and offers two-sided printing for plain paper only.

## Installation coverage

The guide describes physical installation and the current Fill controls. It makes no
automatic-priming claim. The Prime controller path is in
`firmware/src_appliance/machine.cpp`; controller checks are documented in
[`firmware/test/README.md`](../../firmware/test/README.md).

No owner support phone number, email address or dedicated support URL is configured.

The counter page sends a stone counter to a spare 1-3/8 in sink or counter hole, or to a 1-3/8 in
diamond core bit kept wet. No stone-drilling procedure (bit speed, backing, chip control) is
verified.

The owner's regulator steps are attaching it and opening the cylinder valve: it comes set to
75 psi at the factory with the red tether already in its outlet
([`reference/taprite-3741-regulator`](../reference/taprite-3741-regulator/README.md)), and the
guide tells the owner to leave its adjusting screw alone. The owner gas checks cover locating a
leak and closing the supply. The gas disconnection procedure is not published. The cylinder nut,
the regulator's outlet push-fit and the red tether/bulkhead joint all sit upstream of the
machine's GASHER check valve, and the regulator has no outlet shutoff or manual relief. A verified
procedure must establish how the red tether is brought to zero pressure, confirmed at both gauges,
before disconnection, without touching the factory setting. Closing the cylinder alone is not a
pressure-release procedure.

The refrigerant figure is the project's documented bound, under 40 g. A per-unit charge comes
from factory run-up.
