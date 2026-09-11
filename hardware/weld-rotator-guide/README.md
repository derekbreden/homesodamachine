# Weld-rotator build guide

48 pages, 8.5 × 11 in, one picture per step: print, heat-set inserts, base, bearing, drive,
nest, copper contact, controller, and six commissioning gates. Served at
[homesodamachine.com/drawings](https://homesodamachine.com/drawings) and printed one-up on
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

- Both scripts live under `tools/` —
  [`rotator_art.py`](/tools/weld-rotator-guide/rotator_art.py) draws the pictures,
  [`build.py`](/tools/weld-rotator-guide/build.py) binds the book. `tools/bazel/trace_inputs.py`
  names `tools/` in `ELSEWHERE`.
- Neither script keeps `note_read` / `note_write` bookkeeping.
- `web/dev-server/server.js` discovers generators under `CONTENT_ROOTS`, which is
  `[HARDWARE_DIR]`.
- `art/*.png`, `weld-rotator-guide.pdf`, its cover and its `.pdf.json` are in the git index.
  This directory is absent from `pack.py`'s `BUNDLED_ART_DIRS`; `out/` is in its
  `NOT_BUNDLED_DIRS` and in `.gitignore`.
- `render.yaml`'s `buildFilter` names this directory, so a commit here deploys the site and the
  new PDF reaches the served disk.

The guide goes stale when the fixture moves, until a person runs the two commands below.


## What is here

| | |
|---|---|
| `NN-name.html` | 48 pages, in bound order. `build.py` reads the numbers and refuses a gap. |
| `style.css` | The page system. 2550 × 3300 px = 8.5 × 11 in at 300 dpi. |
| `art/*.png` | 37 pictures, drawn from the fixture's own CadQuery by `rotator_art.py`. |
| `weld-rotator-guide.pdf` | The bound book. |
| `weld-rotator-guide.cover.png` | The cover thumbnail the drawings shelf shows. |
| `weld-rotator-guide.pdf.json` | The sidecar `web/lib/walk.js` finds the PDF through. |
| `out/` | Page renders and staged STEPs. Regenerable, gitignored, unbundled. |

## The picture conventions

Page 3 declares them to the reader; `rotator_art.py` paints them.

- **Coral** is the part or fastener the step in hand adds. Everything already standing keeps the
  stock's own black.
- **Brass** is a heat-set insert.
- **Blue** is a gauge, a probe, a packing block or the dial indicator.
- **Fasteners stand off their own holes**, along the axis they go in on.

Screws, inserts, feeler blades, blocks and the indicator are proxies built in `rotator_art.py`
to catalogue head and length. Nothing in a picture is a dimension.

## The motor screw

The fixture README and `NAMES.md` both name two **M5 × 12** countersunk screws threading into
the motor's own tapped flange holes. `_rotator_interface.py` states the 23HS30-2804S's four
flange holes as **Ø5.2 mm** clearance. `ledger/purchases.md` records the M5 × 12 measured short,
retired to spare stock, and replaced by **M5 × 20 through an M5 square nut** in the motor's
corner channel: 8 mm arm, 5 mm flange ear, 4 mm nut, 3 mm proud. Page 24 gives that route and
says the nut's seat in the channel is recorded from the catalogue, not from the bench.

## Rebuilding it

```bash
tools/cad-venv/bin/python tools/weld-rotator-guide/rotator_art.py   # the pictures
tools/cad-venv/bin/python tools/weld-rotator-guide/build.py         # then the book
```

`rotator_art.py` takes scene names to redraw one picture; `--list` names them all. `build.py`
renders every page through `tools/render/render-card.js`, which reports any page whose content
overflows the canvas or spills out of its `header` / `main` / `footer` band. The renderer prints
page 1 of each leaf and nothing else.
