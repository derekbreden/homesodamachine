# Enclosure display interface variations

Sixteen visual directions for the enclosure display, each drawn across the same five screens at
the panel's own 800 × 480, against the current design transcribed to the pixel as a control.

`sheets/screen-*.png` is the comparison: every direction's take on one screen, side by side.
`sheets/direction-*.png` is one direction across all five, which is how a direction is checked
for holding up.

This study changes **colour, type, material, mark system, and the devices that carry state**.
It does not propose new functions, and it holds every screen to the same facts.
[`../../../../future/enclosure-display-studies/`](/future/enclosure-display-studies/) is the
companion study that varies **composition** — where the picture, the controls and the
reservoirs sit — and holds colour and type still. The two vary opposite axes on purpose.

## THIS DOCUMENT IS NOT A STEP OF THE BUILD. LEAVE IT THAT WAY.

It was drawn once, against the interface as it stood that day, and committed. No bazel target
builds it, no `graph.json` entry names it, no publish or derive lane touches it. Nothing here
is compiled into an image or shipped on a machine. Its `node_modules` is the renderer's and is
not in the index.

## What every direction draws

[`BRIEF.md`](BRIEF.md) is binding on all of them: the five screens, the facts each must carry,
and the rules for how a page is written. [`PRESSURES.md`](PRESSURES.md) is the read of the
current design the directions answer — where the surface does not carry the thinking behind
it, and what the panel already gets right and must not lose. [`CURRENT.md`](CURRENT.md) is the
firmware's own geometry, palette and strings, which is what `00-current` is built to.

| Screen | What it is |
|---|---|
| `choose` | the machine's home, both flavors, one selected |
| `flavor` | one flavor's own page — its ratio, and the row of faces it can wear |
| `pick` | fill a flavor — the two-up pick that opens a service action |
| `lock` | the operation lock, mid clean cycle |
| `settings` | system status, and the areas beside it |

## The directions

[`directions.json`](directions.json) carries each one's full brief — thesis, palette,
typography, layout move, selection device, face treatment, lock treatment and risks — and the
four that were proposed and set aside as another's near-twin.

They came from four independent lenses, each asked for five directions without seeing the
others': a premium built-in kitchen appliance, a beverage fountain and bar, an instrument, and
a light domestic interior.

## Rebuilding it

```sh
npm i playwright                       # once; the renderer finds Chromium on PLAYWRIGHT_BROWSERS_PATH
node render.mjs --dpr 2 --out renders pages/<key>/*.html
node sheet.mjs
```

`render.mjs` shoots a page at the panel's own grid — `--dpr 1` is 800 × 480 exactly, `--dpr 2`
the same layout at twice the sampling, for reading type on a desk display. It exits non-zero
and names any page whose content spills past the panel. `sheet.mjs` lays the renders out.
