#!/usr/bin/env python3
"""Run each generator once and write down every file it read and every file it wrote.

    tools/cad-venv/bin/python tools/bazel/trace_inputs.py            # every generator
    tools/cad-venv/bin/python tools/bazel/trace_inputs.py <gen.py>   # one

An audit hook watches the run, which happens the way the generator's own `__main__` runs. Every
path under this repo it opens is kept, on the side its mode names — reads on one, writes on the
other, and an atomic write on the rename that lands it. The answer is `graph.json`, which
`inventory.py` and `gen_build.py` both read.

OCCT READS A STEP BELOW PYTHON, where no audit hook reaches. `_cadq_export.import_step` is the
one loader and keeps the list; this takes it at the end of the run, so a generator that cuts no
solid of its own still names the ones it stood the machine off.

A WRITE THAT LANDS ON THE BYTES ALREADY THERE PERFORMS NO WRITE. `_cadq_export._atomic_write`
skips the rename and `docgen` skips the `write_text`, and both keep the target they were
handed in `_WRITE_TARGETS`, which this takes the same way.

A generator that raises is traced to where it stopped. What it read is what it read; what it
had not yet written is absent from its outputs, and the copy at the end of its action finds
nothing there.
"""

import argparse
import json
import os
import runpy
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
GRAPH = _HERE.parent / "graph.json"

RUNNER = r'''
import json, os, sys, runpy
ROOT = %r
GEN = %r
OUT = %r
read, wrote = set(), set()

def _keep(into, path):
    try:
        p = os.path.abspath(os.fspath(path))
    except (TypeError, ValueError):
        return
    if p.startswith(ROOT + os.sep):
        into.add(os.path.relpath(p, ROOT))

def _hook(event, args):
    # `open` is most of it, and its mode says which side of the edge it is. `import` is the
    # rest of the reading: a module loaded by path through importlib — `_bom_sync` takes a
    # dozen generators that way — is read by the loader, not by open().
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        mode = args[1] if len(args) > 1 and isinstance(args[1], str) else "r"
        _keep(wrote if set(mode) & set("wxa+") else read, args[0])
    # AN ATOMIC WRITE LANDS AS A RENAME. `_cadq_export._atomic_write` writes a sibling temp
    # and moves it over the target, so the name the tree carries is never opened for writing.
    elif event in ("os.rename", "os.replace") and len(args) > 1:
        _keep(wrote, args[1])
    elif event == "import" and len(args) > 1 and args[1]:
        _keep(read, args[1])
    elif event == "exec" and args:
        code = getattr(args[0], "co_filename", None)
        if code:
            _keep(read, code)

sys.addaudithook(_hook)
sys.argv = [GEN]
sys.path.insert(0, os.path.dirname(os.path.join(ROOT, GEN)))
try:
    runpy.run_path(os.path.join(ROOT, GEN), run_name="__main__")
except BaseException as exc:
    print(f"  (raised {type(exc).__name__}; keeping what it read)", file=sys.stderr)
finally:
    # THE SOLIDS OCCT OPENED BELOW PYTHON. `import_step` is the one loader and keeps the list;
    # a generator that cuts nothing of its own has no stamp to carry it, so it is taken here.
    read |= set(getattr(sys.modules.get("_cadq_export"), "_STEP_READS", ()))
    for mod in ("_cadq_export", "docgen"):
        wrote |= set(getattr(sys.modules.get(mod), "_WRITE_TARGETS", ()))
    with open(OUT, "w") as fh:
        json.dump({"reads": sorted(read), "writes": sorted(wrote)}, fh)
'''


def _tracked() -> set:
    return set(subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                              capture_output=True, text=True, check=True).stdout.split())


def trace(gen: str, files: set) -> dict:
    """Every tracked file `gen` read and every one it wrote, plus the solids OCCT loaded."""
    out = Path(os.environ.get("TMPDIR", "/tmp")) / f"hsm-trace-{Path(gen).stem}.json"
    env = dict(os.environ, HSM_NO_BUILD_LOCK="1", HSM_SKIP_VIEWS="1", HSM_SKIP_SCENES="1")
    subprocess.run([sys.executable, "-c", RUNNER % (str(_ROOT), gen, str(out))],
                   cwd=str(_ROOT), env=env, capture_output=True, text=True, timeout=1800)
    try:
        seen = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"reads": [], "writes": []}
    return {side: sorted(p for p in seen.get(side, ()) if p in files)
            for side in ("reads", "writes")}


def _generators(files: set) -> list:
    """Every `.py` under `hardware/` with a `__main__` — what this tree can run."""
    out = []
    for f in sorted(files):
        if not f.endswith(".py") or f.startswith("tools/"):
            continue
        try:
            if '__name__ == "__main__"' in (_ROOT / f).read_text():
                out.append(f)
        except OSError:
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("gen", nargs="*", help="generator paths; default every one")
    args = ap.parse_args()

    files = _tracked()
    gens = args.gen or _generators(files)

    graph = json.loads(GRAPH.read_text()) if GRAPH.is_file() else {}
    for i, gen in enumerate(gens, 1):
        seen = trace(gen, files)
        # `probe.py`, `fit.py` and `lanes.py` are instruments: they answer and write nothing.
        if not seen["writes"]:
            graph.pop(gen, None)
        else:
            graph[gen] = seen
        print(f"  [{i:3d}/{len(gens)}] {gen:60s} "
              f"{len(seen['reads']):3d} read {len(seen['writes']):3d} written")
        GRAPH.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
    print(f"{len(graph)} generator(s) in the graph")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
