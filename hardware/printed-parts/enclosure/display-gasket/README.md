# Display gasket

A TPU ring under the display cover plate's lap, between the plate and the display's
cover glass.

Material: Bambu TPU 90A (black), from the same per-unit-trivial stock as the
foam-cap and reservoir gaskets.

The plate's underside lies below the display plane and the glass's
front face below it. This fills what is between them, so the
snap-retained cover bears on the glass through the soft ring, and the face a
customer wipes closes at its edge.

## The ring

| | |
|---|---|
| outer | ×, the glass's own outline |
| inner | ×, the cover plate's window |
| width | all round — the plate's lap |
| corners | r, the glass's own |
| thickness | |

The thickness is derived rather than chosen: it is where the glass's front face
stands, less where the plate's underside sits. Change either and this follows.

## Print

Same plate as the machine's other soft seals. No supports; the ring lies flat.

## Regenerate

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/display-gasket/display_gasket.py
```
