# Assembly

The [shell](../shell/) wrapped around the contents in shared coordinates — the
internal subsystems placed by [`_contents.py`](_contents.py), which the shell is
sized around. The contents keep their per-part colors; the shell is translucent
so the arrangement reads through it.

## Regenerate

The shell sizes itself from the contents bbox, so rebuild it first, then this:

```
tools/cad-venv/bin/python hardware/printed-parts/enclosure/shell/shell.py
tools/cad-venv/bin/python hardware/printed-parts/enclosure/assembly/assembly.py
```

→ `assembly.step`. The contents are placed in-process by `_contents.py` (shared
with the shell); there is no separate contents STEP.
