# Owner's manual

The book that ships at the top of the appliance carton: twelve pages, 5.5 × 8.5 in,
printed two-up on three letter sheets, duplex, folded down the middle and stapled on
the fold. It covers what is in the carton, where the machine goes, the five install
steps, the first pour, everyday use, and what to do when something is wrong.

Design intent for what the customer meets on install day is
[`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md).
The bench's own deck — one card per hand operation, for whoever builds the machine —
is [`/hardware/assembly/cards/`](/hardware/assembly/cards/README.md).

## Layout

- One `.html` per page, `<nn>-<slug>.html`, against a fixed 1650 × 2550 canvas
  (5.5 × 8.5 in at 300 dpi, portrait). The leading number is the reading order and
  the printed page number.
- [`style.css`](style.css) — the page system. [`STYLE.md`](STYLE.md) — the idioms it
  implements, and the print settings.
- `out/` — one PNG and one PDF per page. Built rather than carried; `.gitignore`
  holds the directory out.
- `manual.pdf`, `manual-print.pdf`, `manual.cover.png`, `manual.pdf.json` — the book,
  the sheets, the cover the site shows, and the sidecar it lists the book by
  ([`web/contracts/documents.js`](/web/contracts/documents.js)). Carried: the pages
  are printed off the browser's layout rather than captured off it, so the book is
  vector and half a megabyte.
- [`_build.py`](_build.py) — renders, binds, imposes. Underscore-prefixed: the
  dev-server never runs it.

```
tools/cad-venv/bin/python hardware/manual/_build.py
```

## The pictures

The two iso views are the enclosure's own line art, cut by Blender's Freestyle from
the built appliance ([`../printed-parts/enclosure/drawings/line-art/`](/hardware/printed-parts/enclosure/drawings/line-art/)),
and the pages read them where they are cut. The cover inverts the front view to white
on the navy ground; page 7 shows the back view with the port rings it carries.

Everything else a page draws is inline SVG in the page itself.

## The colours the book points with

Four stations on the back wall, four colours, one table —
[`_back_panel_dimensions.py`](/hardware/printed-parts/enclosure/back-panel/_back_panel_dimensions.py)
states the scheme, the line art paints the rings from it, and `style.css` names the
same four so a ring on the wall and the word beside it on the page are one colour.

| | |
|---|---|
| blue | carbonated water — the insulated tube in the umbilical |
| black | flavor, two of them, either into either |
| white | tap water, teed in under the sink — drawn as its outline |
| red | CO₂, from the customer's cylinder |

## Printing

Epson EcoTank ET-8550, **Letter borderless** (`Letter.Fullbleed`), landscape, from
`manual-print.pdf` — six sides, three sheets. The stock has to take ink on both faces,
so the single-sided Koala RC gloss the two decks print on is not it; a double-sided
matte or satin photo/presentation paper in letter is.

1. Print sheets 1, 3, 5 (the fronts).
2. Reload the stack face-down, same leading edge.
3. Print sheets 2, 4, 6 (the backs).
4. Fold the stack down the middle together, staple twice on the fold.

Check sheet 1 before printing the rest: page 12 left, page 1 right on the front, and
page 2 left, page 11 right on the back. If the back comes out inverted, the reload
flipped the wrong axis.
