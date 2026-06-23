"""Assembled Lite logic tray (tray + boards seated). Reuses
``module_tray.build_module_assembly`` with the logic mounts."""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_here.parent))
from _cadq_export import export_assembly
import module_tray as mt
import logic_tray as lt


def main():
    export_assembly(mt.build_module_assembly(lt.MOUNTS, "logic-assembly"),
                    str(_here.parent / "logic-assembly.step"))
    print("-> logic-assembly.step")


if __name__ == "__main__":
    main()
