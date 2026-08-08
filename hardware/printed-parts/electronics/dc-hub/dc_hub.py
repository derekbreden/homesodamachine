"""DC hub — the 12 V + / GND distribution block: two Wago 221-413 lever nuts on one
printed plate, the point every 12 V branch leaves from.

It is the AC hub's plate with a shorter row. `ac_hub.build_hub` takes a `Layout` and
builds the wells, the floor and the two hold-down pads from it, so the only thing this
module owns is the row: TWO poles here, three there. Nothing about the well, the press
fit, the plate thickness or the bore is restated — a change to the hub's plate reaches
both parts, which is the point of importing rather than copying.

Both rails are the same lever nut the AC hub stands, so the two printed parts and the
mains distribution all draw on one box of 221-413s.

WHY TWO WELLS AND NOT MORE. The block's ways are the 12 V branch list, and that list is
closed by the board: everything else on 12 V — ten valves, both peristaltic pumps, the
condenser fan, the display — hangs off the PCBA and draws through DC-4. What reaches
past the board is relay #2's contact circuit and the diaphragm pump it gates, so each
rail carries exactly three conductors and a 3-way nut fills it:

    + rail    DC-1 in (PSU +V) · DC-2 out (relay #2 COM) · DC-4 out (J10 V12)
    GND rail  DC-1 in (PSU -V) · DC-4 out (J10 GND)      · DC-3 out (SeaFlo -)

Local frame: X right, Y deep, Z up; origin at the floor's bottom-left corner,
Z = 0 the floor underside — the AC hub's frame, because it is the AC hub's plate.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "wago-221-413",
    _hw / "printed-parts" / "electronics" / "ac-hub",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import ac_hub as _hub

# The plate is the AC hub's, whole. Re-exported so a caller placing this part reads its
# geometry off this module rather than reaching through to the other one.
Layout = _hub.Layout
build_hub = _hub.build_hub
floor_t = _hub.floor_t
hold_dia = _hub.hold_dia

# --- Layout ---------------------------------------------------------------
# Two wells abreast on the AC hub's own pitch, neighbours sharing a wall face, one
# hold-down pad past the row at each end. `hold_places` derives from the row, so the
# shorter row carries its own bores in with it.
LAYOUT = Layout(
    wago_places=tuple(
        (_hub.end_margin + _hub.wago_slot_half + i * _hub.wago_pitch,
         _hub.margin + _hub.wago_slot_half_y)
        for i in range(2)
    ),
)

# The mount pattern in the hub's own frame, on the plate's underside — the two bores a
# boss under each stands the plate on.
holes = list(LAYOUT.hold_places())

# --- Stations, in the hub's own frame -------------------------------------
rails = ("+", "GND")             # the order the Wago row runs in


def lug(rail):
    """One lug's wire-entry face: `(position, outward axis)`. Each Wago bottoms on the
    floor in its well and stands its wire half proud, ports UP off the top of the
    standing body."""
    cx, cy = LAYOUT.wago_places[rails.index(rail)]
    return ((cx, cy, floor_t + _hub.stand_h), (0.0, 0.0, 1.0))


def build_dc_hub():
    return build_hub(LAYOUT)


def main():
    hub = build_dc_hub()
    bb = hub.val().BoundingBox()
    holds = LAYOUT.hold_places()
    print(f"   hub {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm — "
          f"{len(LAYOUT.wago_places)} Wago wells on a {floor_t:g} mm plate, held by "
          f"{len(holds)} Ø{hold_dia:g} bores {holds[1][0] - holds[0][0]:.1f} mm apart on the "
          f"row's centre line; a standing lug reaches "
          f"{floor_t + _hub.stand_h:.1f} mm up, ports at its top")
    export_step(hub, str(_here.parent / "dc-hub.step"))
    print("-> dc-hub.step")


if __name__ == "__main__":
    main()
