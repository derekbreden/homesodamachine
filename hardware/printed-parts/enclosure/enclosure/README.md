# Enclosure

A six-walled PETG box, 3 mm walls, sized live to the bounding box of the
contents placed by [`../enclosure-assembly/_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py).
Beyond the closed box it carries one feature — the angled display facet below.
Otherwise no penetrations are modelled (no faucet hole, no AC inlet, no BiB
adapter, no condenser grilles, no funnel hole) — just the box that proves the
contents fit a single-piece print inside the
[H2C left-nozzle build envelope](https://bambulab.com/en/h2c/specs)
(325 × 320 × 320 mm).

The production enclosure with all penetrations, panel splits, mounting bosses,
and door cutouts lives in the sibling [`back-panel/`](/hardware/printed-parts/enclosure/back-panel/),
[`front-panel/`](/hardware/printed-parts/enclosure/front-panel/), and [`nameplate/`](/hardware/printed-parts/enclosure/nameplate/) dirs. This
study is the bounding-box check that hands the production design its maximum
outer envelope.

## Display facet

A flat 45° facet is chamfered into the top-front-left corner for the
[Waveshare ESP32-S3-Touch-LCD-4.3B config display](/hardware/reference/waveshare-43b-display/)
(bezel 112.5 × 75 mm), facing up-and-forward (−Y front / +Z up) toward the
standing user. It is sized to the bezel plus a 3 mm buffer all around —
[118.5 mm](DISPLAY_FACET_X) (X, lateral) × [81 mm](DISPLAY_FACET_SLOPE) (along
the 45° slope) — so the panel seats on it with its body protruding back into
the cavity. Front is −Y, top is +Z, left is −X.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ `enclosure.step`. Wall thickness, interior clearance, and the display-facet
size are the constants at the top of `enclosure.py`. Prints the outer envelope
vs. the H2C bed and the measured facet size.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
