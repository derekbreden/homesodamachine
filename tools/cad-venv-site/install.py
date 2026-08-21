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


def missing(executable=None):
    """The shim files THIS interpreter does not read, by name.

    Empty for an interpreter that reads them all. `sysconfig` answers for the interpreter
    running this module, so a caller asking on another one gets its own answer instead —
    which is why `affected.py` asks only when it is itself the CAD venv's python."""
    site = Path(sysconfig.get_paths()["purelib"])
    return [n for n in _FILES
            if not (site / n).exists()
            or (site / n).read_bytes() != (_HERE / n).read_bytes()]


def main(argv):
    site = Path(sysconfig.get_paths()["purelib"])
    if "--check" in argv:
        gone = missing()
        if gone:
            print("the CAD interpreter is missing this tree's import shim: "
                  + ", ".join(gone), file=sys.stderr)
            print(f"  {sys.executable} {Path(__file__)}", file=sys.stderr)
            return 1
        print("the interpreter reads this tree's shim")
        return 0
    for name in _FILES:
        shutil.copy2(_HERE / name, site / name)
        print(f"  {site / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
