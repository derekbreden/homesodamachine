# Kitchen Edition enclosure assembly

The [enclosure shell](../enclosure/) wrapped around the
[contents](../enclosure-contents-assembly/), in shared coordinates. The
contents keep their per-part colors; the shell is translucent so the
arrangement reads through it.

## Regenerate

Rebuild contents then enclosure first (the shell sizes itself from the
contents bbox):

```
tools/cad-venv/bin/python hardware/enclosure-contents-assembly/enclosure_contents_assembly.py
tools/cad-venv/bin/python hardware/enclosure/enclosure.py
tools/cad-venv/bin/python hardware/enclosure-assembly/enclosure_assembly.py
```

→ `enclosure-assembly.step`.
