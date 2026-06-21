# Narrow enclosure

A PETG box, 3 mm walls, sized live to the bounding box of the contents placed by
[`../narrow-enclosure-assembly/_contents.py`](/hardware/printed-parts/enclosure/narrow-enclosure-assembly/_contents.py),
**split into two printable halves** — `narrow-enclosure-front` and
`narrow-enclosure-back` — that telescope and screw together.

Same machinery as the wide [enclosure](/hardware/printed-parts/enclosure/enclosure/)
(telescoping seam, four corner cross-pins, the 45° display facet, the hopper
opening), wrapped around the **narrow** contents: the cold core, compressor
shroud, and hopper funnel are each rotated 90° about Z, trading X width for Y
depth. The box comes out much narrower (it follows the rotated cold core's 181 mm
footprint and the refrigeration row) and correspondingly longer front-to-back.

`narrow_enclosure.py` exports the two printable halves
(`narrow-enclosure-front.step`, `narrow-enclosure-back.step`) plus
`narrow-enclosure.step` — the two halves as separate solids in assembled
position, seams intact.

## Split + bosses

The front half's full-wall rear lip telescopes into the back half; four corner
cross-pins — one at each top/bottom corner of the ±X side walls — fasten the
halves with M3 screws driven from the ±X exterior, exactly as in the wide build.

The one substantive difference is **where** the seam falls. The wide enclosure
splits just behind the display housing, leaving a shallow front cap and a back
half that holds everything else (cold core included). Here the longer Y would put
that back half far over the H2C bed, so the seam moves to the middle — just ahead
of the cold core. The **front half** holds the front block (refrigeration, the
two flavor pumps, the display, the hopper); the **back half** houses the cold
core and the valve-manifold trays above it. Both halves then fit the H2C
left-nozzle build envelope (325 × 320 × 320 mm), which the whole enclosure does
not — that is the point of the split.

## Display housing

A flat 45° facet is chamfered into the top-front-left corner for the
[Waveshare ESP32-S3-Touch-LCD-4.3B config display](/hardware/reference/waveshare-43b-display/),
facing up-and-forward (−Y front / +Z up) toward the standing user, flush to the
−X (left) edge. The facet surface is sized to the bezel + a 3 mm buffer all
around — [119.5 mm](DISPLAY_FACET_X) (X, lateral) × [83 mm](DISPLAY_FACET_SLOPE)
(along the 45° slope) — identical to the wide build (same display hardware). The
display reference is seated in the housing in `../narrow-enclosure-assembly/`.

## Hopper opening

A rectangular opening is punched through the top wall to the right of the display
housing and flush to the front, where the removable silicone hopper funnel
([`../../zone-c/hopper-funnel/`](/hardware/printed-parts/zone-c/hopper-funnel/))
drops in. The funnel is rotated 90° about Z here, so the opening is the transpose
of the wide build's: narrow in X (80 mm nominal), deep in Y (150 mm). Its +X edge
is clamped clear of the top-right corner pod.

## Regenerate

The box sizes itself from the contents bbox, so rebuild it first, then the
assembly:

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/narrow-enclosure/narrow_enclosure.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/narrow-enclosure-assembly/narrow_enclosure_assembly.py
```

→ `narrow-enclosure-front.step`, `narrow-enclosure-back.step`,
`narrow-enclosure.step`. Wall, split, boss, facet, and hopper constants are at
the top of `narrow_enclosure.py`. Prints the facet size, each half's envelope vs.
the H2C bed, and the cold-core/boss clearance.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/narrow-enclosure/narrow_enclosure.py`
