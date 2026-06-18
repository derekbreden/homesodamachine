# Enclosure assembly

The [enclosure](/hardware/printed-parts/enclosure/enclosure/) wrapped around the contents in shared
coordinates — the internal subsystems placed by [`_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py), which the
enclosure is sized around. The contents keep their per-part colors; the
enclosure is translucent so the arrangement reads through it.

## Regenerate

The enclosure sizes itself from the contents bbox, so rebuild it first, then this:

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py
```

→ `enclosure-assembly.step`. The contents are placed in-process by `_contents.py`
(shared with the enclosure); there is no separate contents STEP.
