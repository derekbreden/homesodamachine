# Funnel guides

Two bench documents for the Zone C silicone funnel, published on `/drawings` and printed in the
shop.

| | |
|---|---|
| [`funnel-mold.pdf`](funnel-mold.pdf) | Build the tooling. Three prints, the finishing process, the four steel jacks. 21 pages. |
| [`funnel-cast.pdf`](funnel-cast.pdf) | Cast one funnel. Weigh, mix, degas, pour, close, vacuum, cure, jack, peel, trim, bake. 18 pages. |

8.5 × 11 in portrait, single sided, printed at 100 % and kept in a binder. Neither document
imposes, so page count is free. One HTML leaf is exactly one page: the renderer prints page 1 and
nothing else, and fails the run on `OVERFLOW`, `SPILL` or `CLIPPED` against
`.card > header|main|footer`.

## These are made by hand and stay out of the build

`_art.py` and `_build.py` are underscore-prefixed, so
[`web/dev-server/deps.js`](/web/dev-server/deps.js) does not run them as generators. This
directory is in no Bazel target, in no `BUNDLED_ART_DIRS` list, and in no `.gitignore` entry —
the PDFs, their covers and their sidecars are committed bytes. The site finds them by walking
`hardware/` for a `.pdf` beside a `.pdf.json`, so nothing registers them anywhere.

They carry the numbers the funnel mold's source files held on **2026-09-09**. A printed guide is
a snapshot; when the geometry moves, run both scripts again and commit the new PDFs.

```sh
tools/cad-venv/bin/python hardware/funnel-mold-guide/_art.py     # the pictures
tools/cad-venv/bin/python hardware/funnel-mold-guide/_build.py   # the documents
```

## What they draw from

The mold, its extraction hardware and the part are
[`printed-parts/zone-c/funnel-mold/`](/hardware/printed-parts/zone-c/funnel-mold/README.md) and
[`printed-parts/zone-c/funnel/`](/hardware/printed-parts/zone-c/funnel/README.md). Materials,
tools and what is owned come from [`ledger/`](/hardware/ledger/bom.md). The food-contact screen
is [`wetted-surface-test.md`](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md).

Every picture in `art/` is cut from the shipped STEP files by `_art.py`, through the same viewer
the assembly cards use. The extraction station's section is the one picture the guides do not
cut: they point at
[`extraction.png`](/hardware/printed-parts/zone-c/funnel-mold/extraction.png), which already
stands beside the geometry it describes.

Diagrams with no camera — the print-time bars, the finishing allowance, the coat-and-mask map,
the degassing cup, the trim shoulder — are inline SVG in the leaf that carries them.

## Where the guides speak for themselves

Four things the source names and does not specify. Each is drawn with a dashed grey rule and
labelled **the guide's call, not spec**, so it cannot be read as a value some file owns:

- the holding arrangement that keeps the core seated through the cure
- the catch tray under the mold
- which of the two owned coatings to try first
- what to cut the sacrificial tip with

Working time, cure and the post-cure are the silicone's own, and they stand beside the mold in
[`funnel-mold/silicone.md`](/hardware/printed-parts/zone-c/funnel-mold/silicone.md): 30 min at
23 °C, 5 h to demold, 24 h to full strength, the two places the maker's listing disagrees with
itself, and the post-cure it does not state at all. The guides print those and still leave a page
to log what a run actually did.

## Style

The palette is the mold's own — cavity teal, core ochre, steel grey — the colours
[`mold-structure.png`](/hardware/printed-parts/zone-c/funnel-mold/mold-structure.png) already
draws those bodies in. Coral is the install guide's cue colour, unchanged: it means act, or
attend, and it is never decoration. Type is IBM Plex from the bytes vendored in
[`../assembly/cards/fonts/`](/hardware/assembly/cards/README.md).

Every number on a page wears a monospace pill and is copied from the source procedure. Every page
that is a step ends with one observable **done when** sentence.
