# Card style

The design idioms every card follows. `style.css` implements them; this file
is the contract for writing a new card. Read three built cards
([pv-03](pv-03-rod-register.html), [pv-08](pv-08-weld-bottom-plate.html),
[cc-03](cc-03-transfer-the-coil.html)) alongside it.

## Canvas

1800 × 1200 px = 6 × 4 in at 300 dpi, landscape, full bleed. The final PNG
renders at 1.2× (2160 × 1440 = 360 dpi, the EcoTank's native grid). Borderless
printing scales ~2–3% — nothing that matters may live within 60 px of an edge;
the header band and footer rule already respect this.

## Anatomy

Every card is `header` / `main` / `footer` inside `.card`:

- **header** — `.code` chip (subsystem accent), `h1` title (uppercase, ≤ 2
  lines, imperative), `.deckpos` (subsystem name · NN/of, "Thin edition").
- **main** — two `.col`s: text left (`flex:1`), visuals right (fixed
  `width: 760px`–`800px`). A card that is mostly diagram may flip the ratio.
- **footer** — `.done` ("DONE WHEN" + one observable acceptance sentence) and
  `.src` (source doc §, generator files, `rev` date).

`<body class="pv">` picks the subsystem accent; codes and colors are in
`style.css` and the deck table in [README.md](README.md).

## Voice

- `.lede`: 1–2 sentences of mental model — *why* the step is shaped the way
  it is, not a restatement of the title.
- `ol.steps`: 3–5 steps, bold imperative lead phrase, ≤ 2 rendered lines each
  where possible. The step text carries the craft ("heat moving", "err
  short"), not just the action.
- Every number wears a `.dim` pill and is **copied verbatim from the source
  procedure** — no rounding, no unit conversions the doc doesn't make, no
  invented tolerances. If the doc gives the reasoning ("the 1 mm clearance is
  the whole budget"), the card may compress it but never extend it.
- Cross-reference other cards by code (PV-06), never by page.
- Bench language over axis names: "low / high", "inside face", "toward the
  slot wall" — an axis letter may appear only alongside its bench meaning.
- `.tools` strip: one line if at all possible. Amazon/SKU ids only when the
  bench needs them to grab the right box.

## Callouts

- `.safety` (yellow, ⚠) — personal harm: flame, refrigerant, mains, laser.
- `.critical` (dark red, ⛔) — part-integrity point of no return ("must not
  break through"). At most one per card; if everything is critical, nothing is.
- `.note` (accent bar) — a fact worth a pause (nesting arithmetic, stale-stock
  warnings).

## Visuals

- `.panel` (navy) holds CAD renders — generate with
  `tools/render/render-step-posed.js`, house navy `#1a1a2e` background, into
  `img/`. Pose the camera to show what the step touches.
- `.panel.light` holds line diagrams: inline SVG, ink `#1d1d26` outlines
  (3 px), steel fill `#eef0f3`, weld `#f0b429`, copper `#b8722c`, dimension
  lines + text in the subsystem accent, `Menlo` 25–26 px for dims, 24 px
  labels / 22 px subtext. Draw to scale when the geometry allows and say so
  once ("mm ·  schematic" caption line). Machinist tick dimensions, not
  arrowheads.
- `.settings` (navy grid) for machine parameters the builder dials in before
  pulling a trigger.
- `table.spec` for short fact tables; `.cap` under any panel for the one
  sentence the image needs.

## Verification

A card that does not print what it says is a build failure, not a judgment
call:

```
node tools/render/render-card.js --batch hardware/assembly/cards <out>
```

Three ways a card loses, all exit 2:

- `OVERFLOW` — an element is cut off by the canvas edge.
- `SPILL` — an element sits inside the canvas but inside another band's box:
  the tools strip printed across the DONE-WHEN rule. A band is header, main,
  or footer; the slack each leaves inside itself is breathing room, not a
  second canvas.
- `CLIPPED` — a panel is `overflow: hidden`, so what its box cannot hold is
  not printed over, it is not printed at all. This is the one that leaves no
  mark on the page to notice.

It also reports `squeezed:` — a render carrying less height than its aspect
ratio asks for, because the column it sits in is full. No content is lost (a
panel gives from the picture, never from the caption), so it does not fail the
build; it is the column saying the card is long.

Fix the card, not the check. Then look at the PNG.

## Printing

Epson EcoTank, 4 × 6 premium glossy, **borderless**, photo quality, one card
per sheet from `out/*.png` (or print the whole run from `out/deck.pdf`, page
size 6 × 4 in). Colors are sRGB; no color management surprises at draft
settings — use the printer's photo-paper profile.
