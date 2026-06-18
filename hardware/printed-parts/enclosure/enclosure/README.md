# Enclosure

A PETG box, 3 mm walls, sized live to the bounding box of the contents placed
by [`../enclosure-assembly/_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py),
**split into two printable halves** — `enclosure-front` and `enclosure-back` —
that telescope and screw together. The back half houses the cold core; the
front half's rear wall inserts into it.

`enclosure.py` exports the two printable halves (`enclosure-front.step`,
`enclosure-back.step`) plus `enclosure.step` — the two halves as separate solids
in assembled position, seams intact (mirrors `faucet/touch-flo-shell`).

## Split + bosses

The front half's full-wall rear lip telescopes into the back half over a 20 mm
overlap (the joint's X/Z registration). Four corner cross-pins — one at each
top/bottom corner of the ±X side walls, centered in the overlap and coaxial by
construction — fasten the halves with M3 screws driven from the ±X exterior.

Each cross-pin is sized to its job. Reading a screw outboard→inboard from the
±X exterior: a Ø6.15 mm head counterbore, then the **boss** — exactly one wall
(3 mm) of material the Ø3.9 mm shank crosses — then the heat-set, then a one-wall
cap.

- **Back half = plug**: a Ø9.9 mm cylinder (the shank + one wall each side, *not*
  the head — the head sits in the wall counterbore) from the exterior to the
  heat-set, fused to the side wall.
- **Front lip = socket**: a corner pod, integral with the top/bottom wall, bored
  Ø10.3 mm to take the plug as a slide fit, with the ruthex M3 heat-set
  (Ø4.0 × 5.25) capped at its deep inboard end and a +Y channel so the plug
  slides in as the lip telescopes home.

The back half is sized so the cold core seats behind the bosses (verified clear
at build time). Each printed half fits the H2C left-nozzle build envelope
(325 × 320 × 320 mm) even though the whole enclosure does not — that is the
point of the split.

## Display facet

A flat 45° **solid** surface is chamfered into the top-front-left corner for the
[Waveshare ESP32-S3-Touch-LCD-4.3B config display](/hardware/reference/waveshare-43b-display/)
(bezel 112.5 × 75 mm), facing up-and-forward (−Y front / +Z up) toward the
standing user, flush to the −X (left) edge so the whole top-front-left corner
comes off. It is a wall-thick mounting surface sized to the bezel + a 3 mm
buffer all around — [118.5 mm](DISPLAY_FACET_X) (X, lateral) ×
[81 mm](DISPLAY_FACET_SLOPE) (along the 45° slope).

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ `enclosure-front.step`, `enclosure-back.step`, `enclosure.step`. Wall, split,
boss, and facet constants are at the top of `enclosure.py`. Prints the facet
size, each half's envelope vs. the H2C bed, and the cold-core/boss clearance.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
