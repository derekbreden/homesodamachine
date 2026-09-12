# Quick start with words · Claude

One single-sided, borderless 19 x 13 in sheet, the six install actions with a sentence or two
beside each, published as `quick-start-claude.pdf` on
[homesodamachine.com/drawings](https://homesodamachine.com/drawings). It stands beside the
wordless [quick start](/hardware/quickstart/README.md) as a second attempt at the same sheet,
and beside `hardware/quickstart-codex/`, a third drawn the same day by another agent.

The palette, type, numerals and motion cues are the wordless sheet's, unchanged; the words are
the [install guide](/hardware/install-guide/README.md)'s, cut to what a person propping the sheet
against a cabinet door can read with both hands busy. Figures are the buyer's: inches, pounds and
PSI carry them.

## THIS DOCUMENT IS NOT A STEP OF THE BUILD. LEAVE IT THAT WAY.

It was drawn once, by hand, and committed. No bazel target builds it, no `graph.json` entry
names it, no publish or derive lane touches it. Wiring it in would put a browser render on every
publish for a sheet that is not the shipped one.

What stands as it stands:

- The binder lives under `tools/` —
  [`build.py`](/tools/quickstart-claude/build.py) renders the page and binds the PDF.
  `tools/bazel/trace_inputs.py` names `tools/` in `ELSEWHERE`.
- It keeps no `note_read` / `note_write` bookkeeping.
- `art/*.png`, `quick-start-claude.pdf`, its cover and its `.pdf.json` are in the git index.
  This directory is absent from `pack.py`'s `BUNDLED_ART_DIRS`; `out/` is in its
  `NOT_BUNDLED_DIRS`, in `.gitignore`, and in `web/contracts/parts-tree.js`'s `EXCLUDED_DIRS`.
- `render.yaml`'s `buildFilter` names this directory, so a commit here deploys the site and the
  PDF reaches the served disk.

## What is here

| | |
|---|---|
| `quick-start-claude.html` | The sheet. |
| `style.css` | The page system. 5700 x 3900 px = 19 x 13 in at 300 dpi. |
| `art/*.png` | The scenes, copied from the wordless sheet's renders on the day this was drawn; the valve pair is cropped to the valve. |
| `quick-start-claude.pdf` | The bound sheet. |
| `quick-start-claude.cover.png` | The cover the drawings shelf shows. |
| `quick-start-claude.pdf.json` | The sidecar `web/lib/walk.js` finds the PDF through. |
| `out/` | The page render. Regenerable, gitignored, unbundled. |

## Rebuilding it

```bash
tools/cad-venv/bin/python tools/quickstart-claude/build.py
```

`build.py` renders the page through `tools/render/render-card.js`, which reports content that
overflows the canvas or spills out of its `header` / `main` / `footer` band, and then binds the
PDF, writes the cover and the sidecar.

## Print

Print on an Epson ET-8550 from the rear feed, landscape, page size **13x19 borderless**, media
type premium semigloss, photo quality, and 100 %. Stock: A-SUB satin RC photo paper, 260 gsm,
13 x 19 in, single-sided. The outer half inch holds nothing essential, so the printer's
borderless expansion cannot cut an action.
