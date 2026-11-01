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
    """The board stock, hole datums and bench mount, from their native builders' figures."""
    above, below = pt.component_stock()
    board = {
        "slab": ((-pt.board.length / 2.0, -pt.board.width / 2.0, 0.0),
                 (pt.board.length, pt.board.width, pt._thickness)),
        "bores": [(hx - pt._centre[0], hy - pt._centre[1], -0.5,
                   pt._hole_dia / 2.0, pt._thickness + 1.0) for hx, hy in pt._holes_pcb],
        "above": above, "below": below,
        "tail_keepouts": [((hx - pt._centre[0] - pt._hole_reach,
                            hy - pt._centre[1] - pt._hole_reach, -pt.pin_drop - 0.5),
                           (2.0 * pt._hole_reach, 2.0 * pt._hole_reach, pt.pin_drop + 1.0))
                          for hx, hy in pt._holes_pcb],
        "joints": [(px - pt._centre[0], py - pt._centre[1], -pt.pin_drop,
                    dia / 2.0, pt.pin_drop) for _pin, (px, py), dia in pt._hole_joints],
        "pin_drop": pt.pin_drop,
    }
    points, bosses, mounts = [], [], []
    for i, mount in enumerate(pt.MOUNTS):
        points += mt._rect_corners(*mount.c, mount.ref.length, mount.ref.width, mount.rot)
        boss_d, bore_d, depth = mt._boss_spec(getattr(mount.ref, "hole_dia", 3.2))
        radius = boss_d / 2.0
        for px, py in mt._posts(mount):
            points += [(px - radius, py - radius), (px + radius, py - radius),
                       (px + radius, py + radius), (px - radius, py + radius)]
            bosses.append({"stock": (px, py, mt.floor_t, radius, mt.board_standoff),
                           "bore": (px, py, mt.floor_t + mt.board_standoff - depth,
                                    bore_d / 2.0, depth + 1.0)})
        mounts.append({"name": f"{mount.ref.name}{i}", "rotation": mount.rot,
                       "translation": (*mount.c, mt.floor_t + mt.board_standoff)})
    return {"board": board,
            "tray": {"hull": mt._convex_hull(points), "floor_t": mt.floor_t, "bosses": bosses},
            "mounts": mounts, "board_color": linear(C_PCBA), "tray_color": linear(M_PETG_BLACK)}


def main():
    import _rust_part
    result = _rust_part.cut("enclosure-components", "pcba-assembly", numbers(), _here.parent)
    for file in result["files"]:
        print(f"-> {file}")


if __name__ == "__main__":
    main()
