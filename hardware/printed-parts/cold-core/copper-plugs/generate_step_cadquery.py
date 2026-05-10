"""Copper-line plugs — the two solids extracted from the foam-bag shell
when the inlet and outlet slits are cut. The shell builds against
their negative space, then these plugs print separately and seal
the slits after the copper evaporator coil is in place and the foam
has cured. Their geometry derives from the slit-and-shell boolean
intersection, so they're built alongside the shell (see
_foam_bag_geometry.build_full_shell) and exported from here."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_bag_geometry import build_full_shell


def main():
    _shell, copper_inlet_plug, copper_outlet_plug = build_full_shell()
    export_step(copper_inlet_plug, str(_here / "copper-inlet-plug.step"))
    export_step(copper_outlet_plug, str(_here / "copper-outlet-plug.step"))
    print("-> copper-inlet-plug.step")
    print("-> copper-outlet-plug.step")


if __name__ == "__main__":
    main()
