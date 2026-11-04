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
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

from _materials import C_PCBA, M_PETG_BLACK, linear
import module_tray as mt
import pcba_tray as pt


def numbers():
    """The Rust board/fab reader and shared convex-floor construction recipe."""
    import _rust_part
    from _rust_data import request
    _rust_part._READ_TARGETS.add(pt._GLB.resolve().relative_to(_rust_part.ROOT.resolve()).as_posix())
    mounts = [{'name': m.ref.name, 'length': m.ref.length, 'width': m.ref.width,
               'holes': m.ref.holes, 'hole_dia': getattr(m.ref, 'hole_dia', 3.2),
               'center': m.c, 'rotation': m.rot} for m in pt.MOUNTS]
    return request('part-data', 'part-data', {'part': 'pcba-assembly', 'glb': str(pt._GLB),
        'mounts': mounts, 'board_color': linear(C_PCBA), 'tray_color': linear(M_PETG_BLACK)})


def main():
    import _rust_part
    result = _rust_part.cut("enclosure-components", "pcba-assembly", numbers(), _here.parent)
    for file in result["files"]:
        print(f"-> {file}")


if __name__ == "__main__":
    main()
