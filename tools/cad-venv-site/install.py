#!/usr/bin/env python3
"""Put this directory's import shim where the CAD interpreter reads it at startup.

    tools/cad-venv/bin/python tools/cad-venv-site/install.py [--check]

`tools/cad-venv` is `.gitignore`d — it is one machine's, built where the machine's own
python is — so the shim is tracked HERE and copied THERE, the same way the venv itself is
made rather than committed. A checkout that has not run this builds solids that are
byte-identical and pays 145 MB and two seconds a process to do it.

NOT `sitecustomize.py`: homebrew's python ships one of its own on the stdlib path, which
comes before site-packages, so a second one there is shadowed and never runs — silently,
with `import cadquery` simply staying slow. `site` executes every `.pth` line beginning
`import` in every site directory, and shadows nothing.
"""

import shutil
import sys
import sysconfig
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FILES = ("_hsm_novtk.py", "_hsm_novtk.pth")


def main(argv):
    site = Path(sysconfig.get_paths()["purelib"])
    check = "--check" in argv
    missing = []
    for name in _FILES:
        src, dst = _HERE / name, site / name
        if check:
            if not dst.exists() or dst.read_bytes() != src.read_bytes():
                missing.append(name)
        else:
            shutil.copy2(src, dst)
            print(f"  {dst}")
    if check:
        if missing:
            print("the CAD interpreter is missing this tree's import shim: "
                  + ", ".join(missing), file=sys.stderr)
            print(f"  {sys.executable} {Path(__file__)}", file=sys.stderr)
            return 1
        print("the interpreter reads this tree's shim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
