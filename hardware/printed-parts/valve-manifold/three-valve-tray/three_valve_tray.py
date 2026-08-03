"""Three-valve tray: the manifold's wide cradle, one off.

The [two-valve tray](../two-valve-tray/)'s own cell packing, one seat wider. Four of the
manifold's pairs ride the two-seat plate; this one carries the NOZZLE GATES — V-G and
V-J, whose outlets are the only lines that leave the machine — with V-K, the tap-water
fill valve, on its third seat. All three are the same Beduan solenoid.

The cell is `../single-tray/`'s, cut by that module's own `cut_cell`, and the pitch is
`two_valve_tray`'s — the valve's declared X keep-out, which is as close as two of these
pack. Both are read, not restated: a seat here cannot drift from a seat there. The
mount ears are the pair's too — same tongue, same hole — at this plate's own four
stations (`mount_stations`).

Origin = the plate's own center, on the middle seat. Z = 0 the valve mounting plane,
ports along Y.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/valve-manifold/three-valve-tray/three_valve_tray.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _hw / "printed-parts" / "valve-manifold" / "two-valve-tray",
):
    sys.path.insert(0, str(_p))
# `tools/` is shared machinery, so it anchors on the repo root that holds it —
# not on this edition's own root, which has no tools/ of its own.
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step
from docgen import substitute_md
import single_tray as cell
import two_valve_tray as pair

port_z = cell.port_center_z
top_z = cell.tray_top_z
bot_z = cell.tray_bottom_z
port_half = cell.valve.port_length / 2.0

# --- The three seats ------------------------------------------------------
# The pair's own pitch, one seat further. The plate keeps the single cell's whole reach
# beyond each outer center, so it is three cells sharing one floor and nothing more.
pitch = pair.pitch
seat_x = pitch
seats = {"xn": (-seat_x, 0.0), "xc": (0.0, 0.0), "xp": (+seat_x, 0.0)}

half_x = seat_x + cell.tray_half_x
half_y = cell.tray_half_y

# --- The mount ears -------------------------------------------------------
# The pair's own tongue, at this plate's four stations: a three-seat plate has no open
# centreline — every cell's port tube runs its full Y — so the ears stand midway BETWEEN
# the cells, the pair's own seat pitch either side of the middle seat, where tube, posts
# and spades are half a cell away by construction. Hole height, tongue section and hole
# size are the pair's (`two_valve_tray`), read rather than restated.
ear_y = pair.ear_y


def mount_stations():
    """All four M3 clearance holes in tray coordinates: ((x, y), ...). The carrier that
    bolts the plate reads these through its seat, so its bosses land under the holes
    wherever the plate stands."""
    return tuple((sx * pair.seat_x, sy * ear_y)
                 for sx in (-1.0, 1.0) for sy in (-1.0, 1.0))


def place_valve(cx, cy, rot=0.0):
    """Valve seated in the cell at ``(cx, cy)``, turned ``rot`` deg about Z. The cell is
    symmetric under a half turn, so 0 and 180 are the same seat with the flow arrow —
    the valve's local +Y — reversed."""
    return pair.place_valve(cx, cy, rot)


def port_collets():
    """Every port's bare collet tip in tray coordinates: {name: (position, outward
    axis)}. Keyed seat-then-end by sign — `xn-yp` is the −X seat's +Y collet, `xc-yn`
    the middle seat's −Y one. This is the whole boundary: six open collets, nothing
    turned onto any of them."""
    out = {}
    for nm, (cx, cy) in seats.items():
        for sy, tag in ((-1.0, "yn"), (+1.0, "yp")):
            out[f"{nm}-{tag}"] = ((cx, cy + sy * port_half, port_z), (0.0, sy, 0.0))
    return out


def build_three_valve_tray():
    tray = (
        cq.Workplane("XY")
        .box(2 * half_x, 2 * half_y, top_z - bot_z, centered=(True, True, False))
        .translate((0.0, 0.0, bot_z))
    )
    for cx, cy in seats.values():
        tray = cell.cut_cell(tray, cx, cy)
    return pair.add_mount_ears(tray, mount_stations())


def build_assembly():
    """The three valves on their seats, all flow arrows +Y. Turning one 180° is a
    seating choice, not a different tray — see `place_valve`."""
    return {nm: place_valve(*p) for nm, p in seats.items()}


def main():
    export_step(build_three_valve_tray(), str(_here.parent / "three-valve-tray.step"))
    print("-> three-valve-tray.step")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "PITCH": f"{pitch:.4g}",
            "PLATE_X": f"{2 * half_x:.4g}",
            "PLATE_Y": f"{2 * half_y:.4g}",
            "PLATE_Z": f"{top_z - bot_z:.4g}",
            "TRAY_BOT_Z": f"{bot_z:.4g}",
            "TRAY_TOP_Z": f"{top_z:.4g}",
            "PORT_Z": f"{port_z:.4g}",
            "SEAT_X": f"{seat_x:.4g}",
            "PORT_HALF": f"{port_half:.4g}",
            "COLLET_PROUD": f"{port_half - half_y:.4g}",
            "COIL_TOP": f"{cell.valve.coil_z_range[1]:.4g}",
            "EAR_X": f"{pair.seat_x:.4g}",
            "EAR_Y": f"{ear_y:.4g}",
            "MOUNT_HOLE_D": f"{2 * pair.mount_hole_radius:.4g}",
        },
        expected_counts={
            "PITCH": 1, "PLATE_X": 3, "PLATE_Y": 1, "PLATE_Z": 1,
            "TRAY_BOT_Z": 1, "TRAY_TOP_Z": 2, "PORT_Z": 1,
            "SEAT_X": 1, "PORT_HALF": 1, "COLLET_PROUD": 1, "COIL_TOP": 1,
            "EAR_X": 1, "EAR_Y": 1, "MOUNT_HOLE_D": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
