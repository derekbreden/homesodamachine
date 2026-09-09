"""Four blind sockets locating a Beduan valve on a printed face.

`build_sockets` supplies the cuts for the enclosure's valve trays. `build_seat`
supplies a raised plinth for the cold-core lid: one rectangular body with rounded
corners, four sockets and an open cylindrical port channel. The valve's round body
lands on the broad top faces beside that channel.

Geometry is in the valve's frame, with its mounting plane at Z0 and port axis on Y.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

from OCP.BRepExtrema import BRepExtrema_DistShapeShape

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hardware / "reference" / "beduan-solenoid"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

import beduan_solenoid as valve
from docgen import substitute_md


# --- what the valve brings ---------------------------------------------------
corner_inset = valve.corner_inset             # a corner post's centre off the footprint centre
corner_post_radius = valve.corner_boss_radius
# The valve's round body bears on this plane; the sockets hold its posts below it.
seat_top_z = valve.boss_z_range[0]

# --- what the seat adds ------------------------------------------------------
socket_clearance = 0.2   # radial, post to socket — the press fit
wall = 3.0               # minimum material outside a socket
socket_floor_z = -1.0    # the socket floor, under the post tips at z = 0, so a post bottoms out
                         # on nothing and the round boss alone sets the valve's height

socket_radius = corner_post_radius + socket_clearance
boss_radius = socket_radius + wall

seat_half = corner_inset + boss_radius
seat_corner_radius = wall
port_air = 1.0


def socket_depth():
    """How deep one socket runs: the post's whole grip over the mounting plane, and the
    millimetre of air under its tip. The same hole whether a boss carries it or a face does."""
    return seat_top_z - socket_floor_z


def build_sockets():
    """Four blind socket cuts in the valve frame, opening at its bearing plane."""
    sockets = None
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            socket = (
                cq.Workplane("XY")
                .workplane(offset=socket_floor_z)
                .center(sx * corner_inset, sy * corner_inset)
                .circle(socket_radius)
                .extrude(seat_top_z - socket_floor_z + 1.0)
            )
            sockets = socket if sockets is None else sockets.union(socket)
    return sockets


def build_seat(seat):
    """A plinth from Z=-seat to the valve's bearing plane, with four blind sockets."""
    assert seat >= -socket_floor_z - 1e-9, (
        f"seat {seat:g} leaves the socket floor below the supporting face")
    solid = (cq.Workplane("XY").workplane(offset=-seat)
             .rect(2.0 * seat_half, 2.0 * seat_half)
             .extrude(seat + seat_top_z)
             .edges("|Z").fillet(seat_corner_radius))
    return solid.cut(build_sockets()).cut(build_port_channel(2.0 * seat_half + 2.0))


def build_port_channel(length):
    """The valve barrel's circular clearance, open through both Y faces."""
    return (cq.Workplane("XZ").center(0.0, valve.port_center_z)
            .circle(valve.port_radius + port_air).extrude(length / 2.0, both=True))


def seat_volume(seat):
    """Plinth volume: rounded rectangle, four sockets and the circular port segment."""
    area = (2.0 * seat_half) ** 2 - (4.0 - math.pi) * seat_corner_radius ** 2
    r = valve.port_radius + port_air
    d = valve.port_center_z - seat_top_z
    channel_section = r * r * math.acos(d / r) - d * math.sqrt(r * r - d * d)
    return (area * (seat + seat_top_z)
            - 4.0 * math.pi * socket_radius ** 2 * socket_depth()
            - 2.0 * seat_half * channel_section)


def _distance(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value()


def port_clearance():
    """The distance from the finished plinth to the valve's port barrel."""
    return _distance(build_seat(-socket_floor_z).val(), valve.build_port().val())


def fouled_volume(seat):
    """Native overlap between the finished plinth and its seated valve."""
    solid = valve.build_beduan_solenoid().val()
    return sum(b.intersect(solid).Volume() for b in build_seat(seat).solids().vals())


def main():
    # The shallowest plinth puts the socket floors on its supporting face.
    shallowest = -socket_floor_z
    gap = port_clearance()
    foul = fouled_volume(shallowest)
    print(f"seat at {shallowest:g} mm: {seat_volume(shallowest):.1f} mm^3, "
          f"port clearance {gap:.4f} mm, fouls the valve by {foul:.6f} mm^3")
    assert math.isclose(gap, port_air, abs_tol=1e-6), f"port channel clearance {gap:g}"
    assert foul <= 1e-6, f"the plinth intersects its valve by {foul:.3f} mm^3"

    substitute_md(
        _here.parent / "README.md",
        variables={
            "POST_DIA": f"{2 * corner_post_radius:.4g}",
            "SOCKET_DIA": f"{2 * socket_radius:.4g}",
            "PLINTH_WIDTH": f"{2.0 * seat_half:.4g}",
            "PLINTH_CORNER": f"{seat_corner_radius:.4g}",
            "BOSS_DIA": f"{2 * boss_radius:.4g}",
            "SOCKET_CLEAR": f"{socket_clearance:.4g} mm",
            "WALL": f"{wall:.4g} mm",
            "CORNER_INSET": f"{corner_inset:.4g} mm",
            "SEAT_TOP_Z": f"{seat_top_z:.4g}",
            "SOCKET_FLOOR_Z": f"{socket_floor_z:.4g}",
            "SOCKET_DEPTH": f"{socket_depth():.4g}",
            "PORT_DIA": f"{2 * valve.port_radius:.4g}",
            "PORT_CLEARANCE": f"{gap:.3f} mm",
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
