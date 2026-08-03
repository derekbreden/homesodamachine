"""Single-valve tray — one Beduan solenoid on one printed plate.

The family's smallest member. `../two-valve-tray/` is two of `../single-tray/`'s
cells sharing a floor and `../three-valve-tray/` is three; this is ONE, and the
plate is that cell's own reach and nothing more. It carries the same mount ears
at the same section, so whatever bolts a two-valve plate bolts this one.

It exists because a tray with a seat left empty is not a smaller tray — the
assembly scripts seat a valve in every seat they are given, so an unused seat
renders a valve that is not in the machine and not in the BOM. A row that
carries one valve gets this part.

Its plate is [38.25](PLATE_X) x [40](PLATE_Y), against the two-valve's 72.5 x 40.
The saving is in X, so a row that is turned a quarter turn about Z spends it in
Y instead — which is what the aft stand's V-K row does, to leave the electronics
their depth.

Frame: the seat on the origin, ports out both ±Y faces, plate top at
`tray_top_z`. Same as every other tray in the family.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/valve-manifold/single-valve-tray/single_valve_tray.py
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
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step
from docgen import substitute_md
import single_tray as cell
import two_valve_tray as pair

port_z = cell.port_center_z
top_z = cell.tray_top_z
bot_z = cell.tray_bottom_z
port_half = cell.valve.port_length / 2.0

# --- The one seat ---------------------------------------------------------
# On the origin. There is no pitch here — a pitch is what separates two seats,
# and the plate is the cell's own reach either side of this one.
seats = {"xc": (0.0, 0.0)}

half_x = cell.tray_half_x
half_y = cell.tray_half_y

# --- The mount ears -------------------------------------------------------
# The family's, unchanged: one tongue off each port face on the plate's own
# centreline, at `two_valve_tray.ear_y` — which is struck off `half_y` and
# `port_half`, both of which this plate shares. So the ears stand where they do
# on every other tray and a carrier's boss pitch is the same part to part.
ear_y = pair.ear_y


def mount_stations():
    """Both M3 clearance holes in tray coordinates: ((x, y), ...)."""
    return ((0.0, -ear_y), (0.0, +ear_y))


def port_collets():
    """Every port's bare collet tip in tray coordinates: {name: (position, outward
    axis)}. Keyed the family's way — the seat's name, then the end by sign. This
    seat is `xc`, the same key the three-valve plate's middle seat carries, so a
    valve moved between the two keeps its collet names."""
    out = {}
    for nm, (cx, cy) in seats.items():
        for sy, tag in ((-1.0, "yn"), (+1.0, "yp")):
            out[f"{nm}-{tag}"] = ((cx, cy + sy * port_half, port_z), (0.0, sy, 0.0))
    return out


def build_single_valve_tray():
    tray = (
        cq.Workplane("XY")
        .box(2 * half_x, 2 * half_y, top_z - bot_z, centered=(True, True, False))
        .translate((0.0, 0.0, bot_z))
    )
    for cx, cy in seats.values():
        tray = cell.cut_cell(tray, cx, cy)
    return pair.add_mount_ears(tray, mount_stations())


def build_assembly():
    """The one valve on its seat, flow arrow +Y."""
    return {nm: pair.place_valve(*p) for nm, p in seats.items()}


def main():
    export_step(build_single_valve_tray(), str(_here.parent / "single-valve-tray.step"))
    print("-> single-valve-tray.step")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "PLATE_X": f"{2 * half_x:.4g}",
            "PLATE_Y": f"{2 * half_y:.4g}",
            "PLATE_Z": f"{top_z - bot_z:.4g}",
            "PORT_SPAN": f"{2 * port_half:.4g}",
            "TRAY_TOP_Z": f"{top_z:.4g}",
            "EAR_PITCH": f"{2 * ear_y:.4g}",
        },
        expected_counts={"PLATE_X": 1, "PLATE_Y": 1, "PLATE_Z": 1,
                         "PORT_SPAN": 1, "TRAY_TOP_Z": 1, "EAR_PITCH": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
