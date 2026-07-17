# Enclosure assembly

The [enclosure](/hardware/printed-parts/enclosure/enclosure/) wrapped around the contents in shared
coordinates — the internal subsystems placed by [`_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py), which the
enclosure is sized around, plus the through-wall connector bodies
(`_contents.panel_bodies()`), the display, and the hopper funnel. The contents
keep their per-part colors; the enclosure is translucent so the arrangement
reads through it.

The export prints the pack envelope and verifies every pair of placed solids
non-intersecting (and the connector bodies against the enclosure walls); a
clash fails the run.

## Regenerate

The enclosure sizes itself from the contents bbox and the funnel seats itself
against both, so rebuild in this order:

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py
tools/cad-venv/bin/python hardware/printed-parts/zone-c/hopper-funnel/hopper_funnel.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure-assembly/enclosure_assembly.py
```

→ `enclosure-assembly.step`. The contents are placed in-process by `_contents.py`
(shared with the enclosure); there is no separate contents STEP.
