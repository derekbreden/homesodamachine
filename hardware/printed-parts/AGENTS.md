# Printed parts

## Publish loop

    tools/cad-venv/bin/python hardware/scripts/materialize_pump_cartridge.py
    tools/cad-venv/bin/python tools/publish_now.py

The piece's own generator cuts its STEP, STL and payload (the pump cartridge has the dedicated
materializer above); `publish_now.py` grafts the changed payload into both viewer hosts — the
enclosure aggregate and the appliance assembly — and tells the site.

After the publish is live — never before, and never as a gate in the build path — lint the
piece you changed and justify or fix what it flags while Derek is already looking:

    tools/cad-venv/bin/python hardware/scripts/geometry_lint.py <piece>.stl

Findings print as pick text: paste one into the /3d Find box, or feed it to `pick_read.py`.
A finding that is intentional is answered in `<piece>.lint-answers` beside the STL — a
`[class] reason` line, one `click:` per instance (format in `geometry_lint.py`). A defect
fixed at one station usually has siblings; the lint's job is to find them before Derek does.

## What each file shows

The physical print is the part. The files answer different questions about it:

- CadQuery source and `.step` — the exact B-rep construction and analytic faces. On pieces
  with a mesh-only show skin the STEP is a smooth body.
- `.stl` — the tessellated geometry the slicer reads: the closest file to the print.
- `.step.mesh` — the payload `/3d` draws, cut from the STL at the viewer's tolerance
  (`hardware/scripts/flute_payload.py`). Picks arrive in this frame, and the pick's `file:`
  line names it, with what the reduction cost and the digest it descends from.
- `hardware/scripts/pick_text.py` composes pick text from geometry;
  `hardware/scripts/pick_read.py` answers pasted pick text off all three surfaces at once,
  nearest first, and says which of them hold the window.

That last reading is a LOCATION AND NOT A VERDICT. The payload's tolerance is a distance
bound, so a feature shorter than it is collapsed and bridged while the reading never leaves
budget: a coordinate can be real on the payload alone and still be a real defect — that is the
payload reporting geometry it could not draw, and what cannot be drawn at that scale usually
cannot be printed at it either. A surface comparison says where a thing shows up. It never
settles whether what somebody saw in the viewer was there.

## Supports

Every printable piece in the enclosure assembly follows **Support-removal strategy** in
[`enclosure/enclosure/README.md`](enclosure/enclosure/README.md#support-removal-strategy).

User-visible top/bottom rounds print at 0.08 mm through the entire curve, without supports
contacting those rounded surfaces. Derek's tee-carrier print is the physical example:
[`enclosure/tee-carrier/physical-acceptance.json`](enclosure/tee-carrier/physical-acceptance.json).
Apply this to other parts, including back-top's roof edges. Use face-specific support blockers
where other features still need supports, and inspect emitted support paths, including short
bodies without interface labels. A fine layer band alone does not exclude supports.

## Filament use

Derek wants every spool used fully, with reloading during a print as needed. Remaining
spool quantity is not a launch condition: do not ask for its weight or an estimate, or
hold a ready print for a quantity confirmation. Use the correct material mapping and
ask for reloading only when an actual runout requires it.
