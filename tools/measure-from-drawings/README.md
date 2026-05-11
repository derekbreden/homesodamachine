# Measure-from-Drawings — Workflow Guide

A reusable workflow for taking an off-the-shelf part from "we need its dimensions" to a CAD-ready `geometry-description.md`, using manufacturer drawings, distributor catalog images, and other published sources — without needing to hold the part.

The deliverable of this workflow is exactly the same shape of document that `hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md` and `hardware/off-the-shelf-parts/beduan-solenoid/extracted-results/geometry-description.md` already produce. Those are the canonical examples — when in doubt, mimic them.

---

## 1. When to use this workflow

**This is a primary path, not a fallback.** The user has explicitly noted: *"your guesses [from drawings] are often as good as my caliper measurements."* That is the operating assumption.

Use this workflow when:
- The part has not arrived yet (BOM is finalized but parts are still in transit).
- A CAD model is being authored *before* committing to a purchase, to verify clearances and mounting interfaces.
- A caliper measurement is ambiguous (e.g., the feature is internal, recessed, or curved) but the manufacturer drawing labels it.
- The part *is* in hand but the agent doing the modeling cannot physically access it.
- You want a second independent source to cross-check calipered numbers against catalog/drawing values.

Use caliper measurement (the existing `john-guest-union/`-style flow) when:
- No drawing exists for the exact variant in hand (common with no-name Amazon parts).
- The drawing exists but disagrees materially with the physical part — the part wins, but flag the discrepancy.
- The interface zone matters more than the published envelope (e.g., the exact OD of a fitting's center body that's never called out on the datasheet).

In practice, you will almost always do **both**: derive from a drawing first, then refine against the part once it arrives. The output document records both sources and flags disagreements.

---

## 2. Where the work lives

Match the existing layout exactly. Three real examples to mirror:

```
hardware/off-the-shelf-parts/<part-slug>/
├── datasheet/                          # optional, source PDFs
│   └── <product>-product-manual.pdf
├── raw-images/                         # source images (drawings, photos, screenshots)
│   ├── README.md                       # per-image source/view/license metadata
│   ├── 01-<feature>-<value>.png        # numbered, descriptive, value-in-filename
│   └── 02-...
└── extracted-results/
    └── geometry-description.md         # the deliverable
```

### Part-slug naming

Use `<manufacturer>-<distinguishing-id>`, all lowercase, hyphen-separated:

- `john-guest-union` (manufacturer + product family)
- `beduan-solenoid` (manufacturer + part type, when the SKU is generic)
- `kamoer-kphm400` (manufacturer + model number)

When in doubt, prefer the manufacturer+model pattern. Avoid generic slugs like `1-4-inch-fitting` — multiple manufacturers make those, and the slug should disambiguate.

### Image filename convention

The existing caliper photos encode the measurement in the filename:

```
01-body-od-side-view-15.10mm.jpeg
02-collet-end-od-end-on-14.96mm.jpeg
07-overall-length-white-body-39.13mm.jpeg
```

The same pattern works for drawing-derived measurements. For unlabeled drawings where you calibrated against a known reference, encode the *derived* value:

```
01-jg-pp1208e-datasheet-fig1.png                          # raw drawing, no measurement encoded
02-pp1208e-thread-major-od-13.85mm-calibrated-from-G1-2.png   # crop with derived value
```

Pattern: `NN-<short-feature-description>-<value><unit>.<ext>`. Two-digit prefix keeps them sorted. The value-in-filename is what lets `grep`/`find` and an agent reading the directory listing get oriented fast — it is **load-bearing**, do not skip it.

### Per-image README in `raw-images/README.md`

The existing parts don't currently have this file — they encode source in the photo itself (caliper visible). For *drawing-sourced* images, where the file's provenance isn't obvious from looking at it, write a `raw-images/README.md`:

```markdown
# Source images for <part>

| File | Source URL | View | Date pulled | License/notes |
|------|-----------|------|-------------|---------------|
| 01-pp1208e-datasheet-fig1.png | https://www.johnguest.com/.../PP1208E.pdf | side, dimensioned | 2026-05-11 | Manufacturer datasheet, fair use for engineering reference |
| 02-pp1208e-amazon-listing-spec.jpeg | https://www.amazon.com/dp/B0XXXX | top, callouts | 2026-05-11 | Distributor listing |
```

Date is important because manufacturer PDFs get silently re-versioned. The URL is important because the manufacturer may move/remove the file later — keep the originally-fetched copy in `raw-images/` and record where it came from.

---

## 3. Source-finding strategies

Drawings are scattered. Try sources roughly in this order; stop as soon as you have one orthographic, dimensioned drawing of the variant you actually intend to buy.

### 3.1 Manufacturer official site
First-best. Search `"<manufacturer> <part number> datasheet"` or `"... drawing"` or `"... technical drawing"`. Most plumbing/fluid/electromechanical manufacturers post PDFs.

- John Guest: johnguest.com publishes PDF datasheets per part family; the URL pattern is stable enough to guess.
- SMC, Festo, Parker, Swagelok: full CAD libraries with per-part STEP + PDF.
- Kamoer, Aquatec, Shurflo (pumps): product pages usually have a PDF link near the bottom.

If the manufacturer site returns 403, requires login, or hides the PDF behind JS:
- Try the direct PDF URL if you can guess it (often `/sites/default/files/<part>.pdf` or `/downloads/<part>.pdf`).
- Try `web.archive.org/web/*/<manufacturer-domain>/*<part-number>*` — Wayback often has the file.
- Try Google's cached/indexed version: `site:<manufacturer-tld> <part-number> filetype:pdf`.

### 3.2 Distributor catalog pages
Second-best. Distributors mirror manufacturer drawings and often include their own dimensioned diagrams.

Distributors that reliably attach technical drawings:
- **McMaster-Carr** — drawing-quality CAD next to every product, downloadable PDF and STEP/DXF.
- **DigiKey / Mouser** — electromechanical parts: PDF datasheet linked from product page.
- **RS Components / Allied / Newark** — similar to DigiKey.
- **U.S. Plastic / Cole-Parmer / Grainger** — fluid/plumbing parts.
- **AutomationDirect / SMC USA / Bimba** — pneumatics, valves, actuators.

### 3.3 3D CAD libraries
When a manufacturer or distributor offers a STEP/IGES, the model itself is dimensionally authoritative — you can `tools/step_validate.py`-style measure it directly.

- **TraceParts** (traceparts.com) — huge, manufacturer-curated.
- **GrabCAD** (grabcad.com) — community uploads, sometimes user-modeled approximations. Check provenance.
- **3DContentCentral** — SolidWorks-affiliated, manufacturer-uploaded.
- **McMaster-Carr** — STEP next to every product, manufacturer-grade.

If you get a STEP, use that as a measurement target (load in CadQuery or FreeCAD, extract dimensions) rather than going through pixel measurement at all. Note this in `geometry-description.md` as the source.

### 3.4 Patent databases
For older or off-brand parts where the geometry is patented:
- Google Patents (`patents.google.com`) — searchable by part name + manufacturer.
- USPTO PatFT/AppFT.

Patent figures are *always* dimensioned (sometimes nominally) and are orthographic. The catch: the patented geometry is often a *family*, not the specific SKU.

### 3.5 Marketplace listings
Amazon, eBay, AliExpress gallery images sometimes include the manufacturer's spec drawing as one of the listing photos. The user has Chrome MCP access to Amazon Prime — when working on Amazon-sourced parts, check the gallery images. (Per project memory: only Prime listings count.)

The marketplace photo-of-a-spec-sheet is a recurring pattern: the listing reproduces the manufacturer's drawing as a JPEG. Quality is usually fine for calibration even though it's been resaved.

### 3.6 Reverse image search
When you have a photo of an unidentified part and want to find the manufacturer:
- Google Lens (`lens.google.com`) — best for product matching.
- TinEye (`tineye.com`) — best for finding the same image elsewhere on the web.

Once you have a manufacturer/SKU, return to 3.1.

### 3.7 Hand-measured stand-in
If nothing exists for the exact variant, but a similar variant from the same family does, use the similar variant's drawing as a *first-pass* with confidence MEDIUM, and flag every dimension as "from similar variant, refine on arrival."

---

## 4. What makes a drawing usable

Not every drawing is measurable. Filter aggressively before you spend time on calibration.

### 4.1 Orthographic vs perspective
Only **orthographic** views (true front/side/top, no foreshortening) are measurable. A 3/4 perspective render is decoration. If the only available view is perspective, fall back to dimension labels (transcribe what's printed) and skip pixel measurement.

### 4.2 Dimension labels present
A drawing with explicit dimension labels at every relevant feature is the easy case: **transcribe the labels**. Pixel measurement is a backup for unlabeled features. Note any ambiguity in *which feature* the label applies to (arrow target).

### 4.3 To-scale but unlabeled
The hardest common case. You can pixel-measure if you can find at least one **calibration reference** (see §5). If no calibration is possible, the drawing is not usable.

### 4.4 Resolution & file format
- Vector (PDF, SVG): preferred — convert to high-res PNG with `pdftoppm -r 300 source.pdf out` for measurement.
- Raster ≥ 1000 px on the longest dimension: usable.
- Raster < 500 px: probably not usable. Find a better source.
- JPEG artifacts at edges add ~1-2 px of measurement noise — for parts at typical drawing scale (~3 px/mm) that's ~0.5mm of slop. Acceptable; record confidence MEDIUM.

### 4.5 Watermarks, distortion, crop issues
- Watermarks that obscure features: try a different source.
- Drawings photographed at an angle (common on marketplace listings): if the perspective distortion is small (rectangles still look like rectangles), proceed but note confidence LOW for any dimension perpendicular to the apparent tilt.
- Cropped drawings where one edge falls outside the frame: usable only for features fully visible.

---

## 5. Calibration recipes

A drawing is "to scale" if and only if the relative pixel distances reflect the physical ratios. To convert pixels to mm you need at least one known dimension.

### 5.1 The basic conversion

```
unknown_mm = unknown_pixels × (known_mm / known_pixels)
```

That ratio `(known_mm / known_pixels)` is the **scale factor**. Compute it once per image and reuse it for every measurement on that image.

### 5.2 Picking the calibration reference

In rough order of preference:

1. **An explicit dimension label on the same drawing.** Sometimes a drawing labels only one or two features but is otherwise to scale. Use the label.
2. **A catalog spec value for a well-defined feature of the same part.** E.g., for John Guest 1/4" fittings, the tube ID is nominally 6.35 mm — find the tube-port circle on the drawing, measure its pixel diameter, derive the scale.
3. **A standardized thread or fitting size.** G 1/2 BSPP threads have a nominal major diameter of 20.955 mm. NPT, UNF, metric ISO — all have published nominal dimensions. If the drawing shows a threaded section, you have a calibration reference even without a label.
4. **A drawing-internal scale bar or grid.** Rare but unambiguous when present.

### 5.3 Multiple calibration references

If different regions of a drawing imply different scale factors, the drawing is **not uniformly to scale** — usually because a detail inset is at a different magnification than the main view. Compute one scale factor per view/inset, not per image. Annotate which view/inset each measurement came from in `geometry-description.md`.

If two calibration references on the *same* view disagree:
- Within ±2%: average, record confidence MEDIUM.
- Within ±5%: prefer the more authoritative reference (catalog spec > thread nominal > tube nominal), record confidence LOW.
- Beyond ±5%: the drawing is probably perspective-distorted or cropped/rescaled. Don't trust it.

### 5.4 Pixel-measurement tools

You usually don't need scripts. Several approaches work:

- **Eyeball with image viewer**: Open the image in macOS Preview, use the rectangle/line selection — the inspector shows pixel coordinates. Two clicks gives you a delta. Fast for ~5 measurements.
- **`pdftoppm` + ImageMagick `identify`**: Convert PDF to PNG, use ImageMagick to crop and inspect coordinates. Reasonable for batch work.
  ```bash
  pdftoppm -r 300 part-datasheet.pdf page
  # page-1.png is now ~300dpi, measure with any image tool
  ```
- **Browser DevTools on a PNG**: Open as `file:///...` in Chrome, inspect — cursor coordinates show in the elements panel.
- **Scripted (Python + Pillow / OpenCV)**: Only worth it when you have dozens of features on the same drawing and want a reproducible record. Don't go here on a first pass.

### 5.5 The photo-with-caliper calibration (the existing pattern)

The existing `raw-images/*.jpeg` files use a different calibration approach: the **caliper itself is the scale reference**. The digital readout in the photo records the measurement, and the photo serves as visual confirmation of *what* was measured (which two surfaces the jaws were touching). The filename then encodes that value.

This is hybrid measurement — physical caliper, visual verification. It is the right primary approach when the part is in hand. The drawing-based workflow in this document is for when it isn't.

When you transition from "drawing-derived" to "in-hand caliper-verified", add caliper photos in the same `raw-images/` directory with the standard naming, and update `geometry-description.md` to mark those features as `caliper-verified` instead of `calibrated-from-drawing`.

---

## 6. Measurement techniques

### 6.1 When dimension labels are visible — transcribe

```
- Read the label.
- Identify the arrow target (which two surfaces, edges, or axes the dimension spans).
- Transcribe exactly: include the tolerance if printed, e.g., "20.95 ± 0.1 mm".
- Note in geometry-description.md: source = "label, page 2 fig 1", method = "label-read", confidence = HIGH.
```

Watch for ambiguous arrow targets — long extension lines sometimes pass through several features. When unclear, mark confidence MEDIUM and note "arrow target ambiguous between feature A and B".

### 6.2 When labels are absent — pixel-measure

```
- Pick the calibration reference (§5.2). Record its assumed mm value.
- Measure its pixel span (the same two points you'd put a caliper on).
- Scale factor = mm / pixels.
- For each unknown feature: measure its pixel span, multiply by the scale factor, round to 2 decimals.
- Record in geometry-description.md: method = "pixel-measured, calibrated against <reference>", confidence = MEDIUM (or LOW if calibration was approximate).
```

### 6.3 Cross-checking

Every drawing-derived value should be checked against at least one independent source before it's used to size CAD geometry:

| Drawing-derived value | Cross-check against |
|----------------------|---------------------|
| Outside envelope (W × D × H) | Manufacturer text spec (often elsewhere on the same product page) |
| Thread sizes | Published nominal of the thread standard (G, NPT, UNF, metric ISO) |
| Mounting hole patterns | Other distributors carrying the same part |
| Tube/hose connector sizes | The mating tube/hose nominal (1/4" = 6.35 mm, etc.) |
| Anything load-bearing | Eventual caliper measurement after the part arrives |

Disagreements are not failures — they are signal. Record both, flag the discrepancy in `## Uncertainties and TODOs`, and choose the more authoritative source for the CAD-ready summary.

---

## 7. The `geometry-description.md` template

Mirror `hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`. The sections, in order, are:

### 7.1 Title and purpose
```
# <Manufacturer> <Part Number> — Geometry Description

## Purpose of This Document
This document describes the physical geometry of the <part> in enough detail that an
agent generating engineering drawings or designing a 3D-printed mount can model every
surface and interface — without holding the part.

Reference images: see `../raw-images/`. Image numbers in this document (e.g. "image 03")
correspond to numbered files in that directory.
```

### 7.2 CAD-ready summary (at the top, for fast import)

A flat list of `(name, value_mm, confidence)` triples or a Python-importable table. Put this **first** — it is what a CAD-generating agent reads.

```markdown
## CAD-Ready Summary

| Parameter             | Value (mm) | Confidence | Source        |
|-----------------------|-----------:|-----------:|---------------|
| overall_length        |     41.80  |       HIGH | caliper photo 08 |
| body_center_od        |      9.31  |       HIGH | caliper photo 06 |
| collet_ring_od        |     15.10  |       HIGH | caliper photo 01 |
| thread_major_od       |     20.96  |     MEDIUM | drawing image 02, calibrated from G 1/2 nominal |
| ...                   |            |            |               |
```

Or as a Python dict for direct import:

```python
# Auto-importable. Update from drawing/caliper as values are verified.
PP1208E = {
    "overall_length_mm":     41.80,  # HIGH, caliper photo 08
    "body_center_od_mm":      9.31,  # HIGH, caliper photo 06
    "thread_major_od_mm":    20.96,  # MEDIUM, drawing 02, calibrated from G1/2
}
```

### 7.3 Overall form
A few sentences describing the gross shape — what the part *is*, how it's oriented in use, where the major sub-assemblies sit. See the John Guest union's "barbell" description and the Beduan solenoid's "T-shape" description for tone and level of detail.

### 7.4 Axis convention
Declare X/Y/Z (or L/R for axially symmetric parts) and state what is along which axis. Without this convention, every subsequent dimension is ambiguous.

### 7.5 Dimensional profile by zones
Walk through the part feature by feature. For axially symmetric parts (fittings, motors), walk along the long axis. For block-shaped parts (valves, pumps), walk through named sub-assemblies. Use ASCII-art profiles where they clarify the layout — the John Guest barbell diagram is a good example.

### 7.6 Measurement table
A row per measurement with source image, method, and confidence. See the "Caliper Measurements Summary" table in the existing examples and adapt the column headers when the source is a drawing rather than a caliper photo:

```markdown
| Image | Reading | What's Being Measured | Method | Confidence |
|-------|---------|-----------------------|--------|------------|
| 01    | 41.80mm | overall length        | label-read, datasheet fig 1 | HIGH |
| 02    | 20.96mm | thread major OD       | pixel, calibrated from G1/2 nominal | MEDIUM |
| caliper-04 | 9.57mm | collet OD | caliper-verified | HIGH |
```

### 7.7 Cross-referencing with catalog / datasheet
A table comparing drawing/calculation-derived values against any text specs the manufacturer publishes. Disagreements get noted, with a chosen "controlling" value.

### 7.8 Critical design implications
The "so what" — what does this geometry mean for the parts that interface with it? Bore sizes, mounting hole clearances, port axis offsets. See the John Guest doc's "Rear Wall Pocket Bore" section for the level of synthesis to aim for.

### 7.9 Geometry for 3D modeling agents
A short, imperative section addressed directly to whatever agent or human will produce the CAD next. Numbered points, action-oriented. The John Guest doc ends with one of these; mimic it.

### 7.10 Uncertainties and TODOs
Things flagged for refinement. Every confidence-MEDIUM or LOW value should appear here with a note on how to resolve it:

```markdown
## Uncertainties and TODOs

1. Thread major OD (20.96mm) is calibrated from drawing against G 1/2 nominal — confirm
   with a thread gauge once part arrives. Refine to ±0.05 mm and update CAD if it
   diverges from 20.96.
2. Mounting hole center-to-center: drawing implies 50.0 mm but datasheet says 49.5 mm.
   Drawing was assumed controlling — verify with calipers.
3. Internal bore at the seal face: not visible on any drawing. Defer until part in hand.
```

---

## 8. Iteration

This is a first-pass tool. The user has explicitly accepted: *"guesses are often as good as my caliper measurements"* — bias hard toward shipping a best-guess `geometry-description.md` with confidence flags, rather than waiting for perfect data.

The expected lifecycle of a part's `geometry-description.md`:

1. **Drawing-derived first pass** (this workflow). All values flagged HIGH/MEDIUM/LOW based on source and method.
2. **CAD authored against the first pass**. Clearances generous around any MEDIUM/LOW value.
3. **Part arrives. Caliper-verify any value the CAD depends on.** Promote confidence to HIGH, downgrade to LOW any value that contradicts the drawing.
4. **CAD updated**, geometry-description revised. Add caliper photos to `raw-images/` alongside any drawing-sourced images.
5. **Fit-test the printed part against the real fitting.** Any further disagreement gets folded back into the doc with a dated note.

When you update a `geometry-description.md` after a fit-test, do not delete the old drawing-derived value silently — note it as superseded:

```markdown
| body_center_od_mm | 9.31 | HIGH | caliper photo 06, supersedes drawing-derived 9.50 |
```

The historical value is useful when debugging why a CAD design that previously worked doesn't anymore.

---

## 9. Worked example: where to look in the repo

These are the canonical examples — when authoring a new `geometry-description.md`, open these and mimic structure, tone, and level of detail:

- `hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md` — symmetric inline fitting, barbell profile, ASCII art, full measurement table, design-implications synthesis, modeling-agent section. The longest and most complete example.
- `hardware/off-the-shelf-parts/john-guest-union/raw-images/` — caliper-with-display-visible photo convention, filename-encodes-reading naming.
- `hardware/off-the-shelf-parts/beduan-solenoid/extracted-results/geometry-description.md` — T-shape block part with mounting holes, multiple sub-assemblies. Shorter than JG. Has explicit "Remaining Unknowns" section worth copying.
- `hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md` — pump assembly with both caliper measurements **and** a manufacturer datasheet PDF in a sibling `datasheet/` directory. The cross-referencing-with-datasheet section is the example to follow when you have both sources.
- `hardware/off-the-shelf-parts/kamoer-kphm400/datasheet/KPHM400-product-manual.pdf` — example of a manufacturer PDF kept locally next to the extracted data.

When in doubt, the JG union doc is the gold standard for what "CAD-ready" means in this repo.

---

## 10. Quick reference — the workflow in seven steps

1. **Slug the part.** `<manufacturer>-<id>`, all-lowercase, hyphenated. Create `hardware/off-the-shelf-parts/<slug>/raw-images/` and `extracted-results/`.
2. **Find a drawing.** Manufacturer site first, distributors second, CAD libraries third, marketplace listings as last resort. Save the original file to `raw-images/` and record its source URL in `raw-images/README.md`.
3. **Triage the drawing.** Orthographic? Labeled? Resolution adequate? If not, find another source.
4. **Transcribe labels.** Direct read of any explicit dimension label, into the measurement table.
5. **Calibrate and pixel-measure** any unlabeled but to-scale features. Use catalog specs or thread/tube nominals as the calibration reference.
6. **Cross-check** every value against the manufacturer's text spec and against any second source. Flag disagreements.
7. **Write `extracted-results/geometry-description.md`** following the template in §7. Put the CAD-ready summary at the top. Use HIGH/MEDIUM/LOW confidence consistently. List uncertainties.

The output is ready to drive a CAD-generating agent the moment step 7 is committed. Refinement against the physical part happens later, when it arrives, and updates the same document in place.
