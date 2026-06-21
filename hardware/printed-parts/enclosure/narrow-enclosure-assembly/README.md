# Narrow enclosure assembly

The [narrow enclosure](/hardware/printed-parts/enclosure/narrow-enclosure/)
wrapped around the contents in shared coordinates — the internal subsystems
placed by [`_contents.py`](/hardware/printed-parts/enclosure/narrow-enclosure-assembly/_contents.py),
which the enclosure is sized around. The cold core, compressor shroud, and hopper
funnel are each rotated 90° about Z relative to the wide build, trading X width
for Y depth. The contents keep their per-part colors; the enclosure is
translucent so the arrangement reads through it.

## Regenerate

The enclosure sizes itself from the contents bbox, so rebuild it first, then this:

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/narrow-enclosure/narrow_enclosure.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/narrow-enclosure-assembly/narrow_enclosure_assembly.py
```

→ `narrow-enclosure-assembly.step`. The contents are placed in-process by
`_contents.py` (shared with the enclosure); there is no separate contents STEP.
A pairwise overlap audit lives in [`_audit.py`](/hardware/printed-parts/enclosure/narrow-enclosure-assembly/_audit.py).
