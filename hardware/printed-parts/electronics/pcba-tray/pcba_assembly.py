"""Assembled PCBA tray (tray + board seated). Reuses
``module_tray.build_module_assembly`` with the PCBA mount."""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_here.parent))
from _cadq_export import export_assembly
import module_tray as mt
import pcba_tray as pt


def main():
    export_assembly(mt.build_module_assembly(pt.MOUNTS, "pcba-assembly"),
                    str(_here.parent / "pcba-assembly.step"))
    print("-> pcba-assembly.step")


if __name__ == "__main__":
    main()
