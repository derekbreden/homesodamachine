"""Assembled narrow power tray (tray + parts seated). Reuses
``power_assembly.build_assembly`` with the narrow Layout."""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics" / "power-tray"))
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_here.parent))
from _cadq_export import export_assembly
import power_assembly as pa
import narrow_power_tray as nt


def main():
    export_assembly(pa.build_assembly(nt.NARROW, "narrow-power-assembly"),
                    str(_here.parent / "narrow-power-assembly.step"))
    print("-> narrow-power-assembly.step")


if __name__ == "__main__":
    main()
