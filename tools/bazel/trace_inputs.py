#!/usr/bin/env python3
"""Run each generator once and write down every file it opened.

    tools/cad-venv/bin/python tools/bazel/trace_inputs.py            # every generator
    tools/cad-venv/bin/python tools/bazel/trace_inputs.py <gen.py>   # one

WATCHING A RUN READ IS ONE RUN. Asking the sandbox instead — name a seed, build, read the
failure, name one more — is a full build per file learned, and a generator reads dozens. So
this installs an audit hook, runs the generator the way its own `__main__` runs, and keeps
every path under this repo it opened. The answer lands in `extra_srcs.json`, which
`gen_build.py` folds into each target's `srcs`.

WHAT THE HOOK CANNOT SEE is a file opened by C++: OCCT reads a STEP itself, below Python. That
edge is recorded instead where it is made — `_cadq_export.import_step` is the one loader and
notes what it loaded — so between the two the reading is complete.

A generator that raises is still traced: what it read before it stopped is what it read, and a
build failing for its own reasons is not this file's business.
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
EXTRA = _HERE.parent / "extra_srcs.json"

RUNNER = r'''
import json, os, sys, runpy
ROOT = %r
GEN = %r
OUT = %r
seen = set()

def _hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        try:
            p = os.path.abspath(os.fspath(args[0]))
        except (TypeError, ValueError):
            return
        if p.startswith(ROOT + os.sep):
            seen.add(os.path.relpath(p, ROOT))

sys.addaudithook(_hook)
sys.argv = [GEN]
sys.path.insert(0, os.path.dirname(os.path.join(ROOT, GEN)))
try:
    runpy.run_path(os.path.join(ROOT, GEN), run_name="__main__")
except BaseException as exc:
    print(f"  (raised {type(exc).__name__}; keeping what it read)", file=sys.stderr)
finally:
    with open(OUT, "w") as fh:
        json.dump(sorted(seen), fh)
'''


def _tracked() -> set:
    return set(subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                              capture_output=True, text=True, check=True).stdout.split())


def trace(gen: str, files: set) -> list:
    """Every tracked file `gen` opened, plus the solids `import_step` recorded."""
    out = Path(os.environ.get("TMPDIR", "/tmp")) / f"hsm-trace-{Path(gen).stem}.json"
    env = dict(os.environ, HSM_NO_BUILD_LOCK="1", HSM_SKIP_VIEWS="1", HSM_SKIP_SCENES="1")
    subprocess.run([sys.executable, "-c", RUNNER % (str(_ROOT), gen, str(out))],
                   cwd=str(_ROOT), env=env, capture_output=True, text=True, timeout=1800)
    try:
        read = json.loads(out.read_text())
    except (OSError, ValueError):
        return []
    return sorted(p for p in read if p in files)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("gen", nargs="*", help="generator paths; default every one")
    args = ap.parse_args()

    sys.path.insert(0, str(_HERE.parent))
    sys.path.insert(0, str(_ROOT / "hardware" / "scripts"))
    from inventory import inventory

    files = _tracked()
    inv = inventory(sorted(files))
    gens = args.gen or sorted(inv)

    extra = json.loads(EXTRA.read_text()) if EXTRA.is_file() else {}
    for i, gen in enumerate(gens, 1):
        name = Path(gen).stem.replace("_", "-")
        read = trace(gen, files)
        extra[name] = sorted(set(extra.get(name, [])) | set(read))
        print(f"  [{i:3d}/{len(gens)}] {name:44s} {len(read):3d} file(s) read")
        EXTRA.write_text(json.dumps(extra, indent=2, sort_keys=True) + "\n")
    print(f"{len(extra)} target(s) traced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
