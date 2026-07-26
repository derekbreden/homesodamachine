# Tool-station cards

One card per work area, printed full-bleed on 8.5" × 11" gloss (ET-8550,
`Letter.Fullbleed`). The sequence deck in [`../`](/hardware/assembly/cards/README.md)
walks the build in order; this deck holds still at one machine and collects
every operation that happens there, with the settings each one takes.

Both decks render the same procedure docs in
[`/hardware/assembly/`](/hardware/assembly/), which remain the source of truth.
A number printed here is copied verbatim from one of them or from
[`ledger/tools.md`](/hardware/ledger/tools.md), and
[`_index.py --drift`](_index.py) fails the build on any that is not.

## Layout

- One `.html` per station, named `<code>-<slug>.html`, authored against a fixed
  3300 × 2550 canvas (11 × 8.5 in at 300 dpi, landscape).
- [`tools.css`](tools.css) — the card system. Anatomy: `header` / `main`
  (`.machine` → `.ops` table → `.below`) / `footer`. Station accents are on
  `<body class="dp">`.
- `out/` — one PNG per card at 1.2× (3960 × 3060 = 360 dpi).

```
node tools/render/render-card.js --batch hardware/assembly/cards/tools \
  hardware/assembly/cards/tools/out --size 3300x2550 --dpr 1.2
```

The renderer's `OVERFLOW` / `SPILL` / `CLIPPED` checks are the same ones the
sequence deck is gated on — see [`../STYLE.md`](../STYLE.md) for what each means.

## The stations

`_index.py` inverts the 93 sequence cards' `.tools` strips onto these thirteen,
and reports any tools.md entry no station claims.

```
tools/cad-venv/bin/python hardware/assembly/cards/tools/_index.py
tools/cad-venv/bin/python hardware/assembly/cards/tools/_index.py --drift
```

| Card | Station | Sequence cards |
|---|---|---:|
| DP | Drill press | PV-01 · PV-02 · PV-03 |
| BS | Band saw + cut-off | 4 |
| LW | Laser welder | 7 |
| HY | Hydro + pressure test | 1 |
| TB | Tube bench — cut, straighten, bend, flare | 3 |
| BZ | Braze bench | 3 |
| VC | Vacuum + charge | 4 |
| CR | Crimp bench | 9 |
| SO | Solder + heat-set bench | 9 |
| EL | Electrical test | 14 |
| PL | Plastic tube + fittings | 10 |
| PC | Pour + cure bench | 2 |
| PR | 3D printers | 4 |

A sequence card belongs to every station it draws on, and 37 of the 93 belong
to none — hand assembly, inspection, packing.

## Printing

ET-8550, letter premium gloss, **borderless**, photo quality, one card per
sheet from `out/*.png`. Media type `photographic-high-gloss` for the Koala RC
stock ([purchases.md §13](/hardware/ledger/purchases.md)); letter gloss feeds
from the `rear` tray. Borderless scales ~2–3 %, so nothing that matters lives
within 110 px of an edge.
