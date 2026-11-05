"""Dump manifold_layout's namespace: every name in order, its Python type and repr."""
import json, sys, os
from pathlib import Path
here = Path.cwd()
sys.path.insert(0, str(here / "hardware/manifold-layout"))
sys.path.insert(0, str(here / "hardware/scripts"))
import manifold_layout as ml
out = []
names = ml._compiled.names()
for n in names:
    try:
        v = ml._compiled.get(n)
        t = type(v).__name__
        if callable(v) and not isinstance(v, type):
            r = "<callable>"
        else:
            r = repr(v)
    except Exception as e:  # noqa
        t, r = "ERROR", repr(e)[:300]
    out.append([n, t, r])
target = os.environ.get("DUMP_OUT", "ns_dump.json")
Path(target).write_text(json.dumps(out, indent=0))
print("names", len(out))
