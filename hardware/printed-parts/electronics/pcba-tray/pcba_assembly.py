"""Assembled PCBA tray (tray + board seated), and the BOARD ALONE.

The board alone is what the appliance carries: it bolts to four boss columns of
the cold core's top foam cap (`_cold_core_interface.deck_mounts`), and there is no
tray floor under it. `pcba-assembly.step` remains the bench view of board-on-tray
for the tray's own geometry checks."""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_here.parent))
from _cadq_export import export_assembly, export_step
import module_tray as mt
import pcba_tray as pt


def main():
    export_assembly(mt.build_module_assembly(pt.MOUNTS, "pcba-assembly"),
                    str(_here.parent / "pcba-assembly.step"))
    print("-> pcba-assembly.step")
    # The board in its own pcb frame, underside on Z = 0 — the enclosure seats it
    # on the cap's boss tops, so Z = 0 is the boss-top plane.
    export_step(pt.board.build(), str(_here.parent / "pcba-board.step"))
    print("-> pcba-board.step")


if __name__ == "__main__":
    main()
