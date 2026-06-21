"""Assembled controller tray (tray + boards seated). Reuses
``module_tray.build_module_assembly`` with the controller mounts."""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_here.parent))
from _cadq_export import export_assembly
import module_tray as mt
import controller_tray as ct


def main():
    export_assembly(mt.build_module_assembly(ct.MOUNTS, "controller-assembly"),
                    str(_here.parent / "controller-assembly.step"))
    print("-> controller-assembly.step")


if __name__ == "__main__":
    main()
