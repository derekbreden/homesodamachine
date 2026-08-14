# Display gasket

A TPU ring under the display cover plate's lap, between the plate and the display's
cover glass.

Material: Bambu TPU 90A (black), from the same per-unit-trivial stock as the
foam-cap and reservoir gaskets.

The plate's underside lies [2 mm](PLATE_UNDERSIDE) below the 45° face and the glass's
front face [3 mm](GLASS_FACE_DEPTH) below it. This fills what is between them, so the
two screws in the plate draw down onto the glass rather than over it, and the face a
customer wipes closes at its edge.

## The ring

| | |
|---|---|
| outer | [113.5 mm](OUTER_X) × [77 mm](OUTER_SLOPE), the glass's own outline |
| inner | [107.5 mm](INNER_X) × [71 mm](INNER_SLOPE), the cover plate's window |
| width | [3 mm](RING_W) all round — the plate's lap |
| corners | r[2.5 mm](CORNER_R), the glass's own |
| thickness | [1 mm](THICKNESS) |

The thickness is derived rather than chosen: it is where the glass's front face
stands, less where the plate's underside sits. Change either and this follows.

## Print

Same plate as the machine's other soft seals. No supports; the ring lies flat.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/display-gasket/display_gasket.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/display-gasket/display_gasket.py`
