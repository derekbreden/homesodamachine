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

The front half's inner-half rear wall telescopes into the back half (slip-fit
lip). Four interlocking screw bosses — one at each top/bottom corner of the ±X
side walls — fasten the halves along the depth (+Y) axis:

- **Front boss = socket** (the faucet shell-bottom base-pod idiom): a Ø12.55 mm
  bore open toward the back, with a ruthex M3 heat-set pocket (Ø4.0 × 5.25) at
  its deep −Y end.
- **Back boss = plug** (the faucet mounting-plate boss idiom): a Ø12.15 mm
  cylinder that slides into the socket (0.40 mm slip), carrying an M3 SHCS
  through a Ø3.9 shank bore + Ø6.15 head counterbore.

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
