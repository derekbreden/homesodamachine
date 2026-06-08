# Shell

A six-walled PETG box, 3 mm walls, sized live to the bounding box of the
contents placed by [`../assembly/_contents.py`](/hardware/printed-parts/enclosure/assembly/_contents.py).
No penetrations modelled (no faucet hole, no AC inlet, no BiB adapter, no
condenser grilles, no funnel hole, no display pocket) — just the closed shell
that proves the contents fit a single-piece print inside the
[H2C left-nozzle build envelope](https://bambulab.com/en/h2c/specs)
(325 × 320 × 320 mm).

The production enclosure with all penetrations, panel splits, mounting bosses,
and door cutouts lives in the sibling [`back-panel/`](/hardware/printed-parts/enclosure/back-panel/),
[`front-panel/`](/hardware/printed-parts/enclosure/front-panel/), and [`nameplate/`](/hardware/printed-parts/enclosure/nameplate/) dirs. This
study is the bounding-box check that hands the production design its maximum
outer envelope.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/shell/shell.py`
→ `shell.step`. Wall thickness and interior clearance are at the top of
`shell.py`. Prints whether the outer envelope fits the H2C bed.
