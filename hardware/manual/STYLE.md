# Manual style

The idioms every page follows. [`style.css`](style.css) implements them; this file is
the contract for writing a new page. Read three built pages
([02](02-where-it-goes.html), [03](03-water.html), [06](06-umbilical.html)) alongside
it.

## Canvas

1650 × 2550 px = 5.5 × 8.5 in at 300 dpi, portrait, full bleed. The PNG renders at
1.2× (1980 × 3060 = 360 dpi); the PDF prints off the same layout at 96 CSS px to the
inch, which `render-card.js` scales for. Margins are 150 px top, 132 px side, 120 px
bottom — borderless letter scales the sheet 2–3% and the fold takes a couple of
millimetres more off the inner edge.

## Anatomy

`.page` is a column: kicker, `h1`, `.lede`, body, `.foot` pushed to the bottom by
`margin-top: auto`. An install page adds `.stepno` — the step's numeral, absolutely
positioned top-right, larger than the title.

`.page.bleed` drops the padding for a page whose ground runs to the edge; `.cover`
and `.back` carry the navy.

## Voice

- Second person, present tense, imperative in a step. "Close the angle stop", not
  "the angle stop should be closed".
- `.lede`: one or two sentences of what this page is for.
- `ol.steps`: 3–6 steps, bold imperative lead phrase, then the reason the step is
  shaped that way where a reader would otherwise get it wrong — *"Open the cylinder
  valve all the way. These valves seal at both ends of their travel; half open is
  the one position that leaks."*
- Numbers wear a `.dim` pill and come from the machine or from a procedure doc.
  Nothing rounds a figure the source does not round.
- Refer to a port by its colour, never by its position on the wall.
- No part numbers, no ASINs, no internal names. A customer holds one machine and one
  book; `WR1110` names nothing they can see.

## Callouts

- `.warn` (yellow, ⚠) — personal harm or an irreversible mess: stored gas, mains,
  water under pressure.
- `.note` (accent bar) — a fact worth a pause that is not a warning.
- `.keys` / `.key` — a station on the back wall, named by the ring it wears. The
  `.ring.water` swatch is drawn as an outline; the other three are filled.

## Figures

`figure` holds the picture, `figcaption` the one sentence under it. `figure.grow`
lets the picture take the slack in the column — it gives from the picture, never
from the caption. Line art is black on the paper, full column width, no box. Inline
SVG for anything drawn for one page; ink `#17171d`, the wayfinding colours from the
variables, `IBM Plex Sans` at 24 px for labels.

## Verification

```
node tools/render/render-card.js --batch hardware/manual <out> --size 1650x2550
```

Same three failures as the deck, same exit 2: `OVERFLOW` (past the canvas edge),
`SPILL` (into a neighbouring band), `CLIPPED` (inside an `overflow: hidden` box and
not printed at all). A page that does not fit is a page to shorten — fix the page,
not the check.

`_build.py` runs this and then binds, so a run that reports nothing is a book that
printed whole.

## Printing

Settings and the fold are in [README.md](README.md) "Printing".
