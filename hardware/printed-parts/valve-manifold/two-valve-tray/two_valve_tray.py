"""Two-valve tray: the manifold's one printed cradle, five off.

Every valve in the [fluid-topology](../../../topology/fluid-topology.md) manifold
rides one of these, and they are one part — same solid, printed five times:

    V-A · V-B    the two sources, merging at Y-A
    V-C · V-D    the channel selects, fed from Y-B
    V-E · V-F    bag A, across Y-E
    V-H · V-I    bag B, at the reservoir's own two mouths
    V-G · V-J    the nozzle gates

The tray is the cradle and its own mount: one floor plate carrying two of
`../single-tray/`'s cells, cut by that module's own `cut_cell` so the seats
cannot drift from it, and a mount ear off each port face on the centreline
(`mount_stations`) so a printed carrier under the plate can bolt it down.
No fitting seats on it — no groove, no wall, no boss reaching a divider or
a tee. Which fitting joins a pair is a question about where the pair's two
ports end up: a Y-divider takes two ports side by side, a Tee takes one
above the other, and that is the tray's pose in the enclosure rather than
anything the tray declares. So the geometry that would fix it is not here,
and `port_collets` hands out four open collets.

Each cell is symmetric under a half turn about Z — four sockets on a square,
one saddle down the middle — so a valve seats either way round and the tray
never fixes which end of a port is the inlet.

Origin = the tray's own center, midway between the seats. Z = 0 is the valve
mounting plane, ports along Y.
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
):
    sys.path.insert(0, str(_p))
# `tools/` is shared machinery, so it anchors on the repo root that holds it —
# not on this edition's own root, which has no tools/ of its own.
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_step
from docgen import substitute_md
import single_tray as cell

port_z = cell.port_center_z
top_z = cell.tray_top_z
bot_z = cell.tray_bottom_z
port_half = cell.valve.port_length / 2.0

# --- The two seats --------------------------------------------------------
# The valve declares its own X keep-out (`body_width_x` = its footprint plus a
# pad per side), and the two centers sit exactly that apart, which is as close
# as two of these pack: the modeled envelopes meet on their pads and the real
# bodies stand `body_gap` apart. Each seat then keeps the single cell's whole
# reach beyond its own center, so the plate is those two cells sharing one
# floor and nothing more.
pitch = cell.valve.body_width_x
body_gap = pitch - cell.valve.body_width
seat_x = pitch / 2.0
seats = {"xn": (-seat_x, 0.0), "xp": (+seat_x, 0.0)}

half_x = seat_x + cell.tray_half_x
half_y = cell.tray_half_y

# --- The mount ears -------------------------------------------------------
# One tongue off each port face on the tray's own centreline, each carrying an M3
# clearance hole — the plate's half of a bolted joint whose other half is a boss printed
# in whatever carries the tray (the foam cap's deck-mount table holds the aft stand's).
# The centreline is the one column the cells leave open the whole way up: the seated
# valves' port tubes, corner posts and spades all stand a seat's own geometry away from
# it, and the head and its key clear the top boxes because the ear stands past them in Y.
# Both figures are the part's own: the hole midway between the plate's edge and the
# collet tips, so the ear never reaches past the ports, and the tongue at one socket's
# section, turned solid.
mount_hole_radius = 1.7                   # M3 clearance
ear_radius = cell.socket_radius
ear_y = (half_y + port_half) / 2.0


def mount_stations():
    """Both M3 clearance holes in tray coordinates: ((x, y), ...). The carrier that
    bolts the tray reads these through the tray's seat, so its bosses land under the
    holes wherever the tray stands."""
    return ((0.0, -ear_y), (0.0, +ear_y))


def add_mount_ears(tray, stations):
    """Union one tongue per station onto ``tray`` and cut its hole. Shared with the
    one-seat plate, whose ears are the same section at its own stations."""
    for x, y in stations:
        sy = 1.0 if y > 0 else -1.0
        run = abs(y) - half_y + 1.0       # rooted one wall into the plate
        tongue = (
            cq.Workplane("XY")
            .workplane(offset=bot_z)
            .center(x, y)
            .circle(ear_radius)
            .extrude(top_z - bot_z)
            .union(
                cq.Workplane("XY")
                .workplane(offset=bot_z)
                .center(x, y - sy * run / 2.0)
                .rect(2.0 * ear_radius, run)
                .extrude(top_z - bot_z)
            )
        )
        hole = (
            cq.Workplane("XY")
            .workplane(offset=bot_z - 1.0)
            .center(x, y)
            .circle(mount_hole_radius)
            .extrude(top_z - bot_z + 2.0)
        )
        tray = tray.union(tongue).cut(hole)
    return tray


def place_valve(cx, cy, rot=0.0):
    """Valve seated in the cell at ``(cx, cy)``, turned ``rot`` deg about Z.
    The cell is symmetric under a half turn, so 0 and 180 are the same seat
    with the flow arrow — the valve's local +Y — reversed."""
    return (
        cell.valve.build_beduan_solenoid()
        .val()
        .rotate((0, 0, 0), (0, 0, 1), rot)
        .translate((cx, cy, 0.0))
    )


def port_collets():
    """Every port's bare collet tip in tray coordinates: {name: (position,
    outward axis)}. Keyed seat-then-end by sign — `xn-yp` is the −X seat's +Y
    collet. This is the whole boundary: four open collets, nothing turned onto
    any of them."""
    out = {}
    for nm, (cx, cy) in seats.items():
        for sy, tag in ((-1.0, "yn"), (+1.0, "yp")):
            out[f"{nm}-{tag}"] = ((cx, cy + sy * port_half, port_z), (0.0, sy, 0.0))
    return out


def build_two_valve_tray():
    tray = (
        cq.Workplane("XY")
        .box(2 * half_x, 2 * half_y, top_z - bot_z, centered=(True, True, False))
        .translate((0.0, 0.0, bot_z))
    )
    for cx, cy in seats.values():
        tray = cell.cut_cell(tray, cx, cy)
    return add_mount_ears(tray, mount_stations())


def build_assembly():
    """The two valves on their seats, both flow arrows +Y. Turning one 180°
    is a seating choice, not a different tray — see `place_valve`."""
    return {nm: place_valve(*p) for nm, p in seats.items()}


def main():
    export_step(build_two_valve_tray(), str(_here.parent / "two-valve-tray.step"))
    print("-> two-valve-tray.step")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "PITCH": f"{pitch:.4g}",
            "BODY_GAP": f"{body_gap:.4g}",
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
            "EAR_Y": f"{ear_y:.4g}",
            "EAR_TIP": f"{ear_y + ear_radius:.4g}",
            "EAR_D": f"{2 * ear_radius:.4g}",
            "MOUNT_HOLE_D": f"{2 * mount_hole_radius:.4g}",
        },
        expected_counts={
            "PITCH": 1, "BODY_GAP": 1, "PLATE_X": 1, "PLATE_Y": 1, "PLATE_Z": 1,
            "TRAY_BOT_Z": 1, "TRAY_TOP_Z": 3, "PORT_Z": 1,
            "SEAT_X": 1, "PORT_HALF": 1, "COLLET_PROUD": 1, "COIL_TOP": 1,
            "EAR_Y": 1, "EAR_TIP": 1, "EAR_D": 1, "MOUNT_HOLE_D": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
