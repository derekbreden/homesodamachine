# Assembly

The [shell](../shell/) wrapped around the [contents](../contents-assembly/),
in shared coordinates. The contents keep their per-part colors; the shell is
translucent so the arrangement reads through it.

## Regenerate

Rebuild contents first, then the shell (which sizes itself from the contents
bbox), then this:

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/contents-assembly/contents_assembly.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/shell/shell.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/assembly/assembly.py
```

→ `assembly.step`. Engineering drawing in [`drawings/engineering-drawings/`](drawings/engineering-drawings/).
