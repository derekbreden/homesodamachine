"""Foam-cap stack — the three parts that close one end of the
foam shell during the pour-in-place foam cure: the cap tray, the
lid that sits atop the cap during pouring, and the TPU 90A gasket
that compresses between the cap and the outer-shell mating face.
Printed twice per build (one stack on each end of the shell)."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_shell_geometry import (
    build_foam_cap,
    build_foam_cap_lid,
    build_foam_cap_gasket,
)


def main():
    cap = build_foam_cap()
    lid = build_foam_cap_lid()
    gasket = build_foam_cap_gasket()
    export_step(cap, str(_here / "foam-cap.step"))
    export_step(lid, str(_here / "foam-cap-lid.step"))
    export_step(gasket, str(_here / "foam-cap-gasket.step"))
    print("-> foam-cap.step")
    print("-> foam-cap-lid.step")
    print("-> foam-cap-gasket.step")


if __name__ == "__main__":
    main()
