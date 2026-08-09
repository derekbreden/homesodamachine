"""A VALVE SEAT IS FOUR BOSSES. There is nothing between them.

One boss under each of the Beduan solenoid's four corner posts, each carrying a blind socket
the post presses into. THE POSTS IN THEIR SOCKETS ARE THE WHOLE OF THE RETENTION — nothing
bolts a valve down in this machine, nothing is bonded, and the valve's own round body boss
lands on the boss tops, which is what sets its height.

The valve's PORT hangs below those tops and runs between them, and the bosses stand off it by
more than the clearance their own sockets are cut on. `port_clearance` reads that gap;
`fouled_volume` reads the whole of it, and a seat and the valve it holds share no volume.

Built in the VALVE'S OWN FRAME — origin at the footprint centre, z = 0 the mounting plane its
four corner posts stand on — so a consumer turns and drops one onto its own face. A square of
four round bosses is carried onto itself by a quarter turn, so a station's yaw locates the
valve and does not turn the print.

The seat's numbers are the valve's own (`hardware/reference/beduan-solenoid/`) plus two
clearances and a wall. The cold core's cap lid prints these seats
(`_cold_core_interface.cap_cradles`, `foam_cap.add_cradles`); every other valve in the machine
is butted collet to collet down a limb of the flavour pack and stands on nothing.

    tools/cad-venv/bin/python hardware/printed-parts/valve-seat/valve_seat.py
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
# The round body boss begins here, so this is where a seat's boss tops land: the valve rests on
# them, and everything below is the posts-only band the sockets reach into.
seat_top_z = valve.boss_z_range[0]

# --- what the seat adds ------------------------------------------------------
socket_clearance = 0.2   # radial, post to socket — the press fit
wall = 3.0               # material around a socket, which IS the boss
socket_floor_z = -1.0    # the socket floor, under the post tips at z = 0, so a post bottoms out
                         # on nothing and the round boss alone sets the valve's height

socket_radius = corner_post_radius + socket_clearance
boss_radius = socket_radius + wall

# The four bosses stand clear of one another, so a seat is four separate posts.
assert corner_inset >= boss_radius, (
    f"a boss of r{boss_radius:g} on a {corner_inset:g} mm inset touches its neighbour — four "
    f"bosses that meet are a plate with scallops in it, and this seat has no plate")


def build_seat(seat):
    """The four bosses of one valve seat, in the valve's own frame.

    `seat` is how far the valve's mounting plane stands over the face the bosses grow from, so
    each boss runs from z = −`seat` up to `seat_top_z` and the whole of it is that one face's
    material. The socket is cut through the top, which is what makes it blind from above and
    open to nothing below."""
    assert seat >= -socket_floor_z - 1e-9, (
        f"a seat of {seat:g} mm stands the valve's mounting plane closer to the face than the "
        f"{-socket_floor_z:g} mm its socket floor drops below that plane — the socket would "
        f"bore out through whatever the boss is standing on")
    bosses = None
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            boss = (
                cq.Workplane("XY")
                .workplane(offset=-seat)
                .center(sx * corner_inset, sy * corner_inset)
                .circle(boss_radius)
                .extrude(seat + seat_top_z)
            )
            socket = (
                cq.Workplane("XY")
                .workplane(offset=socket_floor_z)
                .center(sx * corner_inset, sy * corner_inset)
                .circle(socket_radius)
                .extrude(seat_top_z - socket_floor_z + 1.0)
            )
            boss = boss.cut(socket)
            bosses = boss if bosses is None else bosses.union(boss)
    return bosses


def seat_volume(seat):
    """One seat's material, in closed form — four cylinders less four sockets.

    Exact, because the bosses stand clear of one another and every socket floor is above the
    face (both settled above). A consumer holds the material its face GAINED against this sum,
    which is what says every boss stands where it was put and on nothing that was already
    open."""
    return 4.0 * math.pi * (boss_radius ** 2 * (seat + seat_top_z)
                            - socket_radius ** 2 * (seat_top_z - socket_floor_z))


def _distance(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value()


def port_clearance():
    """The gap between a boss and the valve's PORT.

    Read at a boss's inboard top edge, its nearest material to the port, and so independent of
    the seat height: a boss's top is at `seat_top_z` whatever it stands on, and the port hangs
    at the same place over it either way."""
    boss = (cq.Workplane("XY")
            .center(corner_inset, corner_inset)
            .circle(boss_radius)
            .extrude(seat_top_z))
    return _distance(boss.val(), valve.build_port().val())


def fouled_volume(seat):
    """How much of the valve a seat stands inside — 0 mm³, or a boss is in the valve's way.

    Zero is not a near miss rounded down. A socket is cut `socket_clearance` wider than the post
    it takes and its floor drops below the post's tip, so the posts hang in their sockets
    touching nothing; the round boss lands flat on the boss tops, which is contact across a
    plane and no volume at all."""
    solid = valve.build_beduan_solenoid().val()
    return sum(b.intersect(solid).Volume() for b in build_seat(seat).solids().vals())


def main():
    # A seat at the shallowest height there is: its socket floors land ON the face, and it bores
    # nothing into the part under it. Every deeper seat only lifts the same four bosses.
    shallowest = -socket_floor_z
    gap = port_clearance()
    foul = fouled_volume(shallowest)
    print(f"seat at {shallowest:g} mm: {seat_volume(shallowest):.1f} mm^3, "
          f"port clearance {gap:.4f} mm, fouls the valve by {foul:.6f} mm^3")
    # The floor is the seat's own press fit: a boss stands off the valve's port by at least what
    # its socket is cut wider than the post, so a seat clears a valve as freely as it grips one.
    assert gap >= socket_clearance - 1e-9, (
        f"a boss stands {gap:.4f} mm off the valve's port, inside the {socket_clearance:g} mm "
        f"its own socket is cut on")
    assert foul <= 1e-6, (
        f"the seat stands {foul:.3f} mm^3 inside the valve it holds — a seat and its valve "
        f"share the socket walls' clearance and the boss tops' plane, and no volume")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "POST_DIA": f"{2 * corner_post_radius:.4g}",
            "SOCKET_DIA": f"{2 * socket_radius:.4g}",
            "BOSS_DIA": f"{2 * boss_radius:.4g}",
            "SOCKET_CLEAR": f"{socket_clearance:.4g} mm",
            "WALL": f"{wall:.4g} mm",
            "CORNER_INSET": f"{corner_inset:.4g}",
            "SEAT_TOP_Z": f"{seat_top_z:.4g}",
            "SOCKET_FLOOR_Z": f"{socket_floor_z:.4g}",
            "PORT_DIA": f"{2 * valve.port_radius:.4g}",
            "PORT_CLEARANCE": f"{gap:.3f} mm",
        },
        expected_counts={
            "POST_DIA": 1, "SOCKET_DIA": 1, "BOSS_DIA": 2, "SOCKET_CLEAR": 2,
            "WALL": 1, "CORNER_INSET": 1, "SEAT_TOP_Z": 1, "SOCKET_FLOOR_Z": 1,
            "PORT_DIA": 1, "PORT_CLEARANCE": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
