# Weld-rotator build guide

48 pages, 8.5 × 11 in, one picture per step: print, heat-set inserts, base, bearing, drive,
nest, copper contact, controller, and six commissioning gates. Served at
[homesodamachine.com/guides](https://homesodamachine.com/guides) and printed one-up on
Letter.

The fixture is [`fixtures/weld-rotator/`](/hardware/printed-parts/fixtures/weld-rotator/README.md),
the rig it belongs to is [`weld-rotation-rig.md`](/hardware/assembly/weld-rotation-rig.md), and
the controller is [`src_weld_rotator/`](/firmware/src_weld_rotator/README.md). Every number here
comes from one of those three; what this document adds is the order and the pictures.

## THIS DOCUMENT IS NOT A STEP OF THE BUILD. LEAVE IT THAT WAY.

It was drawn once, by hand, and committed. No bazel target builds it, no `graph.json` entry
names it, no publish or derive lane touches it. Wiring it in would put a browser, 48 page
renders and 37 CAD renders on every publish.

What stands as it stands:

- [`build.py`](/tools/weld-rotator-guide/build.py), under `tools/`, binds the book from the
  committed pictures. `tools/bazel/trace_inputs.py` names `tools/` in `ELSEWHERE`.
  [`rotator_art.py`](https://github.com/derekbreden/homesodamachine/blob/7877f6193ead05647b529972ee9f50de305c8d44/tools/weld-rotator-guide/rotator_art.py),
  which drew the pictures, is in Git history.
- `build.py` keeps no `note_read` / `note_write` bookkeeping.
- `web/dev-server/server.js` discovers generators under `CONTENT_ROOTS`, which is
  `[HARDWARE_DIR]`.
- `art/*.png`, `weld-rotator-guide.pdf`, its cover and its `.pdf.json` are in the git index.
  This directory is absent from `pack.py`'s `BUNDLED_ART_DIRS`; `out/` is in its
  `NOT_BUNDLED_DIRS` and in `.gitignore`.
- `render.yaml`'s `buildFilter` names this directory, so a commit here deploys the site and the
  new PDF reaches the served disk.

The guide goes stale when the fixture moves: `build.py` rebinds the pages, and the pictures
stand as committed.


## What is here

| | |
|---|---|
| `NN-name.html` | 48 pages, in bound order. `build.py` reads the numbers and refuses a gap. |
| `style.css` | The page system. 2550 × 3300 px = 8.5 × 11 in at 300 dpi. |
| `art/*.png` | 37 pictures, drawn from the fixture's own CadQuery by `rotator_art.py` and committed. |
| `weld-rotator-guide.pdf` | The bound book. |
| `weld-rotator-guide.cover.png` | The cover thumbnail the guides page shows. |
| `weld-rotator-guide.pdf.json` | The sidecar `web/lib/walk.js` finds the PDF through. |
| `out/` | Page renders and staged STEPs. Regenerable, gitignored, unbundled. |

## The picture conventions

Page 3 declares them to the reader; `rotator_art.py` painted them.

- **Coral** is the part or fastener the step in hand adds. Everything already standing keeps the
  stock's own black.
- **Brass** is a heat-set insert.
- **Blue** is a gauge, a probe, a packing block or the dial indicator.
- **Fasteners stand off their own holes**, along the axis they go in on.

Screws, inserts, feeler blades, blocks and the indicator are proxies `rotator_art.py` built
to catalogue head and length. Nothing in a picture is a dimension.

## The motor screw

The fixture README and `NAMES.md` both name two **M5 × 20** countersunk screws that rise through
the carriage arms and the 23HS30-2804S's rear flange holes into **M5 square nuts** in the motor's
open corner channels. `_rotator_interface.py` states the motor's four flange holes as **Ø5.2 mm**
clearance, and `ledger/purchases.md` records the stack: 8 mm arm, 5 mm flange ear, 4 mm nut,
3 mm proud. Page 24 gives that route and says the nut's seat in the channel is recorded from the
catalogue, not from the bench.

## Rebuilding it

```bash
tools/cad-venv/bin/python tools/weld-rotator-guide/build.py
```

`build.py` renders every page through `tools/render/render-card.js`, which reports any page whose content
overflows the canvas or spills out of its `header` / `main` / `footer` band. The renderer prints
page 1 of each leaf and nothing else.
