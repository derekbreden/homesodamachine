"""Foam-bag shell — the PETG enclosure for the cold core's pressure
vessel + copper evaporator coil + flavor bag pockets. See README.md
for the design intent and the layer-by-layer geometry."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_bag_geometry import build_full_shell


def main():
    foam_bag_shell, _inlet_plug, _outlet_plug = build_full_shell()
    export_step(foam_bag_shell, str(_here / "foam-bag-shell.step"))
    print("-> foam-bag-shell.step")


if __name__ == "__main__":
    main()
