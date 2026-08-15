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
read, wrote, scanned = set(), set(), set()

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
    # A TOOL THIS RUN HANDS A PATH TO opens it out of Python's sight. `render-step-posed.js`
    # is named on node's command line and `_blender_scene.py` on blender's; both are read.
    elif event == "subprocess.Popen" and len(args) > 1:
        for a in (args[1] or ()):
            try:
                if os.path.isfile(os.fspath(a)):
                    _keep(read, a)
            except (TypeError, ValueError):
                pass
    # A DIRECTORY THIS RUN GLOBS names its files without opening one. `_build.py` asks its
    # own directory for `*.html` to know which cards there are; `Path.glob` scans and nothing
    # is read until node opens them, out of sight.
    #
    # A DIRECTORY THE IMPORT MACHINERY SCANS IS NOT ONE THIS RUN GLOBBED. Python lists every
    # `sys.path` entry to find the module it is about to load, and a scan is read below as an
    # input area whole — so the entries a generator inserts arrived as every tracked file
    # beneath them: `tools/` for `docgen`, 61 files into 77 of the hundred targets, `flash.sh`
    # and sixteen animation frames among them; `hardware/scripts/` for the shared machinery,
    # 29 into 103; and the run's own directory, which for a doc sync is `hardware/assembly/`
    # entire, 401 files. What an import reads is the module, which the `import` event below
    # names outright, and `exec` names the ones loaded by path.
    elif event in ("os.scandir", "os.listdir") and args and args[0]:
        try:
            by = sys._getframe(1).f_code.co_filename
        except ValueError:
            by = ""
        if by != "<frozen importlib._bootstrap_external>":
            _keep(scanned, args[0])
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
        json.dump({"reads": sorted(read), "writes": sorted(wrote),
                   "scanned": sorted(scanned)}, fh)
'''


def _tracked() -> set:
    return set(subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                              capture_output=True, text=True, check=True).stdout.split())


def trace(gen: str, files: set) -> dict:
    """Every tracked file `gen` read and every one it wrote, plus the solids OCCT loaded."""
    out = Path(os.environ.get("TMPDIR", "/tmp")) / f"hsm-trace-{Path(gen).stem}.json"
    # ONE GENERATOR AT A TIME IS WHAT THIS ALREADY DOES, so each run takes the global lock
    # the way a hand run does. Two traces on one machine are two pileups otherwise, and the
    # lock is what everything outside `bazel` shares.
    #
    # AND NEVER FOLLOWS SOMEBODY ELSE'S. `_run_lock` attaches a second run of the same script
    # to the one already going and hands back ITS exit status, so the generator's own `main`
    # never runs and the trace watches a process that opened nothing. A reading needs the run
    # to happen, so this one asks for the lock and refuses the shortcut.
    env = dict(os.environ, HSM_SKIP_VIEWS="1", HSM_SKIP_SCENES="1",
               HSM_BUILD_SOURCE="trace", HSM_NO_BUILD_ATTACH="1")
    subprocess.run([sys.executable, "-c", RUNNER % (str(_ROOT), gen, str(out))],
                   cwd=str(_ROOT), env=env, capture_output=True, text=True, timeout=1800)
    try:
        seen = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"reads": [], "writes": []}
    out = {side: {p for p in seen.get(side, ()) if p in files}
           for side in ("reads", "writes")}
    # A SCANNED DIRECTORY IS AN INPUT AREA, and what it holds below the top counts. `_build.py`
    # globs its own directory for `*.html` and hands each card to a browser, which resolves
    # `tools.css` and `img/tool/*.png` against it — reads no scan and no `open` here sees.
    here = tuple(d + "/" for d in seen.get("scanned", ()))
    if here:
        out["reads"] |= {f for f in files if f.startswith(here)}
    return {k: sorted(v) for k, v in out.items()}


#: WHAT THE BOARD READS IS NOT IN THIS REPO. `hardware/pcb/pcba/package.json` pins seven
#: `@tscircuit/*` packages to commits of `github:derekbreden/*`, resolved at install from
#: outside the tree, and `board-3d.py` runs `tsci` through them. An action cannot hold what
#: it reads, so the board is built by `bun render-board.ts` and its GLB carried by the hook.
#: Vendoring the forks is what would let it join the graph.
ELSEWHERE = ("tools/", "hardware/pcb/pcba/")


def _generators(files: set) -> list:
    """Every `.py` with a `__main__` this tree builds through — see `ELSEWHERE`."""
    out = []
    for f in sorted(files):
        if not f.endswith(".py") or f.startswith(ELSEWHERE):
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
        # `probe.py`, `fit.py` and `lanes.py` are instruments: they answer and write nothing,
        # and a generator this has never watched write is not a step of the build.
        #
        # A RUN THAT DID NOT HAPPEN IS NOT A GENERATOR THAT MAKES NOTHING. Attached, superseded,
        # killed, timed out — each comes back the way an instrument does, with no writes, and
        # dropping the entry on that reading takes the generator out of `graph.json`, out of
        # `inventory`, out of `BUILD.bazel`, and its solids stop being cut against a green
        # build. So an entry already standing is left standing, and the line below says the
        # reading failed rather than writing a verdict over it.
        if seen["writes"]:
            graph[gen] = seen
        elif gen in graph:
            print(f"  [{i:3d}/{len(gens)}] {gen:60s} wrote nothing — keeping what it had")
            continue
        else:
            graph.pop(gen, None)
        print(f"  [{i:3d}/{len(gens)}] {gen:60s} "
              f"{len(seen['reads']):3d} read {len(seen['writes']):3d} written")
        GRAPH.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
    print(f"{len(graph)} generator(s) in the graph")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
