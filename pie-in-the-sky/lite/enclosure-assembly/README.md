# Lite enclosure assembly

The [enclosure shell](../enclosure/) wrapped around the contents in their
shared coordinates — the internal subsystems placed by [`_contents.py`](_contents.py).
The whole Lite Edition as one model: a translucent PETG box and everything
inside it.

The contents keep their per-part colors; the shell is translucent so the
arrangement reads through it.

## Regenerate

`tools/cad-venv/bin/python pie-in-the-sky/lite/enclosure-assembly/enclosure_assembly.py`
→ `enclosure-assembly.step`. The contents are placed in-process by `_contents.py`
(shared with the shell); there is no separate contents STEP.
