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

`_index.py` inverts the 94 sequence cards' `.tools` strips onto these thirteen,
and sorts every tools.md entry into one of four: claimed by a station, carried
to the part, consumed or worn, or unaccounted for. Only the last is a defect.

A station is one machine and the work that goes into it. A tool nobody stands
at — a hand deburrer, a caliper — is `CARRIED`, and lives on the sequence cards
that use it; it may still appear in a station's rack, because the rack is what
to have in hand, not what the card is about. Adopting a carried tool to empty
the report costs a card about two things, which is the one thing a card at a
machine cannot be.

```
tools/cad-venv/bin/python hardware/assembly/cards/tools/_index.py
tools/cad-venv/bin/python hardware/assembly/cards/tools/_index.py --drift
```

| Card | Station | Sequence cards it serves |
|---|---|---|
| DP | Drill press | PV-01 · PV-02 · PV-03 |
| BS | Band saw + cut-off | PV-05 |
| LW | Laser welder | PV-06 · PV-07 · PV-08 · PV-09 |
| HY | Hydro + pressure test | PV-11 |
| TB | Tube bench — cut, straighten, bend, flare | CC-01 · RL-03 · RL-05 |
| BZ | Braze bench | RL-03 · RL-04 · RL-05 |
| VC | Vacuum + charge | RL-02 · RL-06 · RL-07 · RL-08 |
| CR | Crimp bench | CA-01 · GT-03/04 · ES-02/05 · WR-01/02/04 · IP-04 |
| SO | Solder + heat-set bench | CC-05 · CC-07 · CC-09 · ES-01 · EN-01 · CA-01 · GT-05 |
| EL | Electrical test | ES-04/05/07 · WR-01/02/03/05 · FC-01…05 · RL-08 · CA-01 |
| PL | Plastic tube + fittings | FU-01 · GT-01/02 · IP-01…05 · CC-01 · CC-12 |
| PC | Pour + cure bench | CC-06 · CC-14 |
| PR | 3D printers | CC-08 · CC-13 · EN-05 · EN-06 |

A sequence card belongs to every station it draws on, and 38 of the 94 belong
to none — hand assembly, inspection, packing, and the edge work that travels
with a tool rather than waiting at a machine.

`img/tool/` holds the tool photographs the rack shows — the listing's own
image for each ASIN in [tools.md](/hardware/ledger/tools.md), trimmed and set
on a 480 × 320 white tile. A tile is the tool that station actually uses: the
laser welder's rack carries the RX Weld regulator, not the RHP400 that serves
the braze purge.

`img/` holds the CAD renders the cards annotate, posed with
[`render-step-posed.js`](/tools/render/render-step-posed.js) from the part's own
STEP. A callout's overlay shares the render's pixel grid, and the feature
coordinates come from the generator that built the part — the end-cap register
from `endcap_circular_step.py`, the J4/J7 wafers from `pcba.tsx`.

## Printing

ET-8550, letter premium gloss, **borderless**, photo quality, one card per
sheet from `out/*.png`. Media type `photographic-high-gloss` for the Koala RC
stock ([purchases.md §13](/hardware/ledger/purchases.md)); letter gloss feeds
from the `rear` tray. Borderless scales ~2–3 %, so nothing that matters lives
within 110 px of an edge.
