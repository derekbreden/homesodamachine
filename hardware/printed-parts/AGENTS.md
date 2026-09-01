# Printed parts

## Publish loop

    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py
    tools/cad-venv/bin/python tools/publish_now.py

The piece's own generator cuts its STEP, STL and payload (the pump cartridge has the dedicated
materializer above); `publish_now.py` grafts the changed payload into both viewer hosts — the
enclosure aggregate and the appliance assembly — and tells the site.

## What each file shows

The physical print is the part. The files answer different questions about it:

- CadQuery source and `.step` — the exact B-rep construction and analytic faces. On pieces
  with a mesh-only show skin the STEP is a smooth body.
- `.stl` — the tessellated geometry the slicer reads: the closest file to the print.
- `.step.mesh` — the payload `/3d` draws, cut from the STL at the viewer's tolerance
  (`hardware/scripts/flute_payload.py`). Picks arrive in this frame.
- `hardware/scripts/pick_text.py` composes pick text from geometry;
  `hardware/scripts/pick_read.py` answers pasted pick text from the STL.

## Supports

Every printable piece in the enclosure assembly follows **Support-removal strategy** in
[`enclosure/enclosure/README.md`](enclosure/enclosure/README.md#support-removal-strategy).
