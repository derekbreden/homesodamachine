# Quick start guide

Two visual 11 x 17 in sheets ship at the top of the Home Soda Machine carton:

1. `00-install.html` - faucet, water, placement, umbilical, CO2 and power.
2. `01-first-glass.html` - choose, fill, prime, select and pour.

They are separate single-sided sheets so they can be printed and replaced independently on an
Epson 11 x 17 in printer. `quick-start.pdf` binds them in that order for download or duplex
printing. The PDF sidecar puts it on `/drawings` beside the assembly card deck.

The recognizable product details are generated or referenced from their production sources:

- the exact faucet assembly STEP, rendered to `art/faucet-install.svg`;
- the exact laser-cut under-counter plate DXF;
- the exact front and rear enclosure line art;
- the rear port and umbilical-collar renders;
- the faucet display images compiled into its firmware;
- the rear-panel port color table.

Build from the repository root:

```sh
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

`out/` contains the full-resolution PNG and vector-PDF render of each authored sheet. The bound
PDF, cover image and `.pdf.json` sidecar beside this README are committed outputs.
