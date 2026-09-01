"""Assembled PCBA tray (tray + main board seated), and the MAIN BOARD ALONE.

The main board alone is what the appliance carries: it bolts to four printed bosses
on the +X wall of back-top, struck off its own MH1-MH4 pattern
(`enclosure_assembly.wall_mounts`), and there is no tray floor under it.
`pcba-assembly.step` remains the bench view of main-board-on-tray for the tray's
own geometry checks."""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_here.parent))
from _cadq_export import export_assembly
from _materials import C_PCBA, one_body
import module_tray as mt
import pcba_tray as pt


def main():
    pt.stations_hold()
    export_assembly(mt.build_module_assembly(pt.MOUNTS, "pcba-assembly"),
                    str(_here.parent / "pcba-assembly.step"))
    print("-> pcba-assembly.step")
    # The board in its own pcb frame: PCB underside and mounting holes on Z = 0,
    # with the populated tail envelope reaching `pin_drop` below. The enclosure
    # seats that outer envelope by the wall and grows each boss to the Z = 0 plane.
    export_assembly(one_body(pt.board.build(), "pcba-board", C_PCBA), str(_here.parent / "pcba-board.step"))
    print("-> pcba-board.step")


if __name__ == "__main__":
    main()
