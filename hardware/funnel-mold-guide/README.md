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

## THESE ARE MADE BY HAND AND ARE NOT A STEP OF THE BUILD. LEAVE THEM THAT WAY.

The two generators live at [`tools/funnel-mold-guide/`](/tools/funnel-mold-guide/), which is
where a hand-run pair has to sit for that to be true — the same place
[`weld-rotator-guide`](/hardware/weld-rotator-guide/README.md) keeps its own.

Three readings hold them out, and all three answer to the directory the scripts sit in:

- `trace_inputs.py`'s `_generators` takes every tracked `.py` that holds the literal
  `__name__ == "__main__"` **outside** `ELSEWHERE = ("tools/", "hardware/pcb/pcba/")`. Under
  `tools/`, a full sweep does not trace them, so `gen_build.py` gives them no rule.
- `affected.py`'s `artifact_unknown` answers no for a `tools/` path outside its own machinery
  list. Under `hardware/`, an untraced `.py` is a path it cannot scope, and one such file
  widens the artifact slice to **all 73 rules** — a whole-tree CAD cut, on the lane
  `tools/publish_now.py` runs, for a document the tree does not build.
- [`web/dev-server/deps.js`](/web/dev-server/deps.js) does not run an underscore-prefixed file
  as a generator.

This directory is in no Bazel target and in no `BUNDLED_ART_DIRS` list. The PDFs, their covers
and their sidecars are committed bytes, and the site finds them by walking `hardware/` for a
`.pdf` beside a `.pdf.json`. They reach the served disk on the deploy
[`render.yaml`](/render.yaml)'s build filter names for this directory.

They carry the numbers the funnel mold's source files held on **2026-09-09**. A printed guide is
a snapshot; when the geometry moves, run both scripts again and commit the new PDFs.

```sh
tools/cad-venv/bin/python tools/funnel-mold-guide/_art.py         # cameras on the solids
tools/cad-venv/bin/python tools/funnel-mold-guide/mold_scenes.py  # staged scenes
tools/cad-venv/bin/python tools/funnel-mold-guide/_build.py       # the documents
```

## Two kinds of picture

`_art.py` puts a camera on a solid that already exists — what the cavity looks like off the
bed, what the rod socket looks like from below. It answers *what is this*.

[`mold_scenes.py`](/tools/funnel-mold-guide/mold_scenes.py) builds a picture for a step:
only the bodies that step touches, standing in the mold's own frame, with the one thing the
step moves lifted off its seat along the axis it travels and painted coral. It answers *what do
I do*. The offset is the arrow, so those pages carry no annotation — one displacement constant
everywhere, and the gap reads as a direction of assembly rather than as framing.

The colour is the legend and both documents declare it on their second leaf: coral is the body
this step moves, the cavity is teal, the core ochre, the silicone dark, and blue-grey is a thing
on the bench rather than part of the mold.

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
