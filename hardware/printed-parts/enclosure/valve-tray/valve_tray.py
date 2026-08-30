"""A VALVE TRAY IS A PLATE OF VALVE SEATS, and it is a wall of the enclosure.

One `valve_seat` per valve — four blind sockets a corner post presses into — SUNK into a flat
plate that runs from side wall to side wall of `enclosure-front-top`. The plate is one socket
and one wall thick, so it is the boss: nothing stands off it, the valve lands on its face, and
the only thing it opens for is each valve's own port, on a channel out both ends. It is
that piece's own material, fused in the way the ASSE anchor, the flow-meter anchors and every
tube rib are: `enclosure._valve_trays` stands one per deck, off the stations
`enclosure_assembly.valve_tray_stations` reads off the placed valves. NO TRAY SHIPS AS A PART,
nothing bolts a valve to one and nothing is bonded — the posts in their sockets are the whole of
the retention, the same bargain the cold core's cap lid strikes under its three valves
(`_cold_core_interface.cap_cradles`).

    ACROSS  wall to wall. The plate is the piece, so it takes no slip and ends on the two
            interior faces
    ALONG   the seats' own reach off their valves' centres, and one `MARGIN` past that. The
            plate ends where the last boss does; the valves' collets and the tube butted into
            them hang past it

This module states the tray's own figures and draws one in its own frame; `enclosure` turns it
onto a deck and fuses it. The frame is `valve_seat`'s carried onto a plate:
  Z = out of the valve-side face, the direction a valve's own +Z runs. `z = 0` IS THAT FACE, so
      the plate spans z = −`THICK` to 0 and every seat is sunk from zero. That face is the plane
      the valve's own round body boss lands on, so a valve stands ON the plate and not on four
      boss tops — `SEAT` is negative here, and that is the whole of the difference.
  X = across the plate. Y = along it. Origin is the plate's centre in both.

A SEAT'S FOUR BOSSES ARE SQUARE, so a quarter turn carries one onto itself: a valve's yaw
locates it and never turns the print.

In the piece's own print orientation the plate stands vertical, wall to wall, and NOTHING
stands off it: the port channel is a notch that runs up the plate's own section, while
`enclosure._valve_socket_cutters` carries each horizontal socket's complete round post room into
a tangent teardrop roof. There is no unsupported crown and no support in the thirty-two sockets
to pick out — which is what the thickness and roof buy, a boss on a standing plate being a
cylinder cantilevered into air.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-tray/valve_tray.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-tray/valve_tray.py selftest
"""

import math
import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "valve-seat",
           _hw / "reference" / "beduan-solenoid"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
import beduan_solenoid as _valve                          # noqa: E402
import valve_seat as _seat                                # noqa: E402
from docgen import substitute_md                          # noqa: E402


# --- what the tray adds over the seats it carries ---------------------------
#
# THE SEAT IS SUNK IN THE PLATE AND NOT STOOD ON IT. A boss is material round a socket, and a
# plate thick enough to hold the socket is that material already — so this plate carries the
# holes and nothing else (`valve_seat.build_sockets`), and its own face is the plane the valve's
# round body boss lands on. What the plate spends is thickness, and what it buys back is the
# print: `enclosure-front-top` stands this plate vertical, so a boss on it is a Ø13.2 cylinder
# cantilevered off a wall into air, with its own underside to bridge and its root standing on
# nothing. The sunk socket has no external underside; enclosure gives its horizontal round
# crown the tangent roof that keeps the internal bore support-free.
#
# The plate's thickness: one socket, and one wall of floor behind it.
THICK = _seat.socket_depth() + _seat.wall
# Material carried past a socket's own boss circle, so the last seat is not a scallop in the
# plate's end. One wall, the same figure `valve_seat` puts around each socket.
MARGIN = 3.0
# The seat: the face IS where the valve lands, so its mounting plane stands `seat_top_z` UNDER
# the face and nothing protrudes. Negative, and that is the whole difference from a stood seat.
SEAT = -_seat.seat_top_z
# Air round the valve's PORT where the plate opens for it. The port hangs under the face the
# valve lands on (`port_drop`), so a solid plate would bury it: the plate takes a channel on its
# own Y instead, the port's barrel and this slip, straight across and out both ends. The barrel
# is longer than the plate is high, so the channel is open at both — in the piece's own print
# orientation it runs UP the standing plate and prints as a notch in the section, nothing
# bridged and nothing to pick out. One millimetre is the box's own figure for air round a body.
PORT_SLIP = 1.0


def reach() -> float:
    """How far a seat's material stands off the valve it holds, in plan — the corner post's
    inset and the boss around it. The plate's height is struck on this."""
    return _seat.corner_inset + _seat.boss_radius


def height() -> float:
    """The plate's height: what the seats reach, both ways, and one `MARGIN` past each."""
    return 2.0 * (reach() + MARGIN)


def seat_pitch_floor() -> float:
    """The closest two seats stand before their bosses meet."""
    return 2.0 * reach()


def port_drop() -> float:
    """How far the valve's PORT hangs under the face the valve lands on.

    The face is that landing plane (`valve_seat.seat_top_z`), and the port's barrel hangs
    `beduan_solenoid.port_center_z` over the mounting plane with `port_radius` of itself under
    that — so the barrel reaches this far inside a plate whose face is the landing plane. It is
    why the plate opens a channel and not why the plate is thick: the sockets set the thickness
    and the channel is cut back out of it."""
    return _seat.seat_top_z - (_valve.port_center_z - _valve.port_radius)


def port_channel_depth() -> float:
    """How deep that channel cuts below the face — the port's drop and its slip."""
    return port_drop() + PORT_SLIP


def extrusion(width) -> float:
    """The width of one bead of this plate, which is what a web is read against.

    A WEB IS WIDE OR IT IS NOTHING, and the figure that decides which is the nozzle, not zero.
    The doc-only `main` hands in `enclosure_assembly.EXTRUSION_W` — the same constant
    `tray-web` holds `web()` against — so the doc and the bound cannot come to differ about
    what one bead is."""
    return width


def web() -> float:
    """The plate left between a corner socket and the port channel, MEASURED.

    The two features run at right angles — the sockets down the valve's own axis, the channel
    across the plate on its Y. A socket's inner edge stands `corner_inset - socket_radius` off
    the centreline and the channel `port_radius + PORT_SLIP`, a tenth of a millimetre apart if
    they ever met at one height; the channel's widest station is above the sockets' mouths and
    never does. Anything that brings the two to one height spends that tenth at once, and
    nothing about a solid says it has been spent.

    NOT ARITHMETIC. The closest approach of the two axes lies above the socket's own top, so a
    figure struck off the radii answers for a cylinder that is not there. This reads the solids.

    Compare what comes back against the nozzle that lays it, not against zero: these plates are
    `enclosure-front-top`'s material, so the bead they come off is the enclosure exterior's own
    and `extrusion()` is where it is read. A web under one extrusion wide is a web the slicer
    does not lay, and the socket opens into the channel over the stretch it does not."""
    sockets = _seat.build_sockets().val()
    channel = build_port_channel(height() + 2.0).val()
    d = BRepExtrema_DistShapeShape(sockets.wrapped, channel.wrapped)
    d.Perform()
    return d.Value()


def grip() -> float:
    """How much of a corner post stands INSIDE the plate, with the valve at rest.

    THE POSTS IN THEIR SOCKETS ARE THE WHOLE OF THE RETENTION (`valve_seat`), so this is the
    whole of what holds a valve down. A still deck's face is the valve's own landing plane and
    the post is in the plate over its whole length, on every deck — the release moves the tee
    it butts and not the valve itself, so no plate on this machine is set off its valves."""
    return _seat.seat_top_z


def build_port_channel(length: float):
    """One valve's port channel, in the valve's own frame: the barrel and its slip, run `length`
    along the plate's own Y and open at both ends.

    A CYLINDER AND NOT A SLOT. The port is round and the channel closes on it all the way round
    at one slip, the way the flow-meter anchors take a barrel — a square slot to the same width
    would take the plate's whole depth at the corners for air the port is nowhere near."""
    return (cq.Workplane("XZ")
            .center(0.0, _valve.port_center_z)
            .circle(_valve.port_radius + PORT_SLIP)
            .extrude(length / 2.0, both=True))

def build_body_clearance():
    """The valve's own boss and top box (`beduan_solenoid.build_body`, less its four corner
    posts), grown by `PORT_SLIP` — the air a plate's own LATER fuse (a corbel, a rib, anything
    struck after the sockets and the port channel already answer for the posts and the port)
    still owes the round body and the box behind it, neither of which either existing cut was
    ever asked to clear.

    THE FOUR POSTS ARE LEFT OUT ON PURPOSE. They are exactly what `valve_seat.build_sockets`
    cuts its sockets to GRIP — a press fit at `socket_clearance` (0.2 mm), not this function's
    `PORT_SLIP` (1.0 mm) — over the whole length `valve_seat.grip` reads off this same body. A
    post-shaped cutter here, at any radius past the socket's own, reams every socket out to a
    free hole along that whole grip length and a valve seated in it is no longer held by
    anything. The boss and the box carry no such grip to protect, so growing them costs nothing
    a socket needs.

    Rebuilt from the same two primitives rather than a generic offset of their union — a grown
    cylinder and a grown box, independent of where their faces meet, so there is no seam for an
    offset to reason about. `PORT_SLIP` is reused rather than a second clearance figure: it is
    already this file's own answer for how much air a fused feature owes the valve's real
    geometry."""
    slip = PORT_SLIP
    body = (cq.Workplane("XY")
            .workplane(offset=_valve.boss_z_range[0] - slip)
            .circle(_valve.body_radius + slip)
            .extrude(_valve.boss_z_range[1] - _valve.boss_z_range[0] + 2.0 * slip))
    top_box = (cq.Workplane("XY")
               .workplane(offset=_valve.top_box_z_range[0] - slip)
               .box(_valve.body_width_x + 2.0 * slip, _valve.body_width + 2.0 * slip,
                    _valve.top_box_height + 2.0 * slip, centered=(True, True, False)))
    return body.union(top_box)


def build_valve_tray(width: float, seats):
    """One tray: the plate, with one `valve_seat`'s sockets and one port channel sunk into it
    per station in `seats`.

    `seats` is `(x, y)` per valve in the plate's own frame — where that valve's footprint centre
    lands. A station carries no yaw and no height: the seat is square, and every valve on one
    tray stands on one plane by construction."""
    if not seats:
        raise ValueError("a valve tray with no seats is a plate, and this machine prints none")
    ys = [y for _x, y in seats]
    for i, (xa, ya) in enumerate(seats):
        for xb, yb in seats[i + 1:]:
            if max(abs(xa - xb), abs(ya - yb)) < seat_pitch_floor() - 1e-9:
                raise ValueError(
                    f"two seats stand ({abs(xa - xb):.3f}, {abs(ya - yb):.3f}) mm apart and a "
                    f"seat reaches {reach():g} mm every way — their bosses meet, and four "
                    f"bosses that meet are a plate with scallops in it")
    if max(ys) - min(ys) > 1e-9:
        raise ValueError(
            f"the seats span {max(ys) - min(ys):.3f} mm along the plate — `height` is struck on "
            f"one row of seats, and these stand on more than one")
    tray = (cq.Workplane("XY")
             .workplane(offset=-THICK)
             .box(width, height(), THICK, centered=(True, True, False)))
    # A station is where the valve's own frame lands: `SEAT` under the face, which is where the
    # sockets and the channel are both struck from. Cut, not fused — the plate is the boss.
    for x, y in seats:
        tray = tray.cut(_seat.build_sockets().translate((x, y, SEAT)))
        tray = tray.cut(build_port_channel(height() + 2.0).translate((x, y, SEAT)))
    return tray


def _segment_area(radius: float, over: float) -> float:
    """The area a circle of `radius` whose centre stands `over` a plane leaves BELOW it."""
    if over >= radius:
        return 0.0
    return (radius ** 2 * math.acos(over / radius)
            - over * math.sqrt(radius ** 2 - over ** 2))


def tray_volume(width: float, n_seats: int) -> float:
    """One tray's material, in closed form — the plate, less one seat's four sockets and one
    port channel apiece.

    Exact, and that is a reading and not a convenience: the four sockets stand clear of one
    another and clear of the channel between them (`selftest` measures both), the channel runs
    straight out of both ends of the plate, and neither reaches the plate's back. So every cut
    is a whole prism of known section, and a tray that measures anything else has a socket in
    its channel or a channel out of its back."""
    socket = math.pi * _seat.socket_radius ** 2 * _seat.socket_depth()
    channel = height() * _segment_area(_valve.port_radius + PORT_SLIP,
                                       _valve.port_center_z - _seat.seat_top_z)
    return width * height() * THICK - n_seats * (4.0 * socket + channel)


def channel_floor() -> float:
    """What the plate keeps under a port channel at its deepest. The channel's own floor is the
    thinnest section on the plate — thinner than the socket floors, or the channel would be the
    thing that sets `THICK`."""
    return THICK - port_channel_depth()


def depth() -> float:
    """The plate's whole run along its own Z — what the enclosure has to leave clear on a
    deck's plane. Nothing stands over the face, so it is the plate and only the plate."""
    return THICK


def selftest() -> int:
    """The tray against the valve it holds and the seat it carries."""
    fails = []
    if THICK - _seat.socket_depth() < _seat.wall - 1e-9:
        fails.append(f"a plate {THICK:g} mm thick keeps "
                     f"{THICK - _seat.socket_depth():.3f} mm behind a socket "
                     f"{_seat.socket_depth():g} deep, under the {_seat.wall:g} mm wall every "
                     f"socket in this machine is floored on")
    if channel_floor() <= _seat.wall - 1e-9:
        fails.append(f"a port channel {port_channel_depth():.3f} mm deep leaves "
                     f"{channel_floor():.3f} mm of plate under it, under one {_seat.wall:g} mm "
                     f"wall — the channel is what sets the plate's thinnest section and it has "
                     f"outrun the sockets")
    if port_drop() <= 0.0:
        fails.append(f"the valve's port stands {-port_drop():.3f} mm CLEAR of the face it lands "
                     f"on, so the plate needs no channel and this one cuts a groove for air")
    # The channel's own half-width where it opens on the face, against the nearest socket's.
    open_half = math.sqrt(max((_valve.port_radius + PORT_SLIP) ** 2
                              - (_valve.port_center_z - _seat.seat_top_z) ** 2, 0.0))
    if open_half >= _seat.corner_inset - _seat.socket_radius - 1e-9:
        fails.append(f"the port channel opens {open_half:.3f} mm either side of the valve's centre "
                     f"and the nearest socket wall stands at "
                     f"{_seat.corner_inset - _seat.socket_radius:.3f} — the channel is in the "
                     f"socket, and a socket open down its side holds no post")
    # A synthetic row of four at the closest pitch the part takes, so the construction is
    # measured here as well as where the machine stands its valves.
    pitch = seat_pitch_floor() + 1.0
    seats = tuple((i * pitch, 0.0) for i in (-1.5, -0.5, 0.5, 1.5))
    width = pitch * 4.0
    try:
        built = build_valve_tray(width, seats).val()
        closed = tray_volume(width, len(seats))
        if abs(built.Volume() - closed) > 1e-6 * closed:
            fails.append(f"a four-seat tray measures {built.Volume():.3f} mm^3 against the "
                         f"{closed:.3f} its closed form says — a boss has met its neighbour or "
                         f"run off the plate")
        bb = built.BoundingBox()
        if abs(bb.ylen - height()) > 1e-6:
            fails.append(f"a tray stands {bb.ylen:.4f} mm high against the {height():.4f} "
                         f"`height` declares")
    except Exception as exc:                                     # noqa: BLE001
        fails.append(str(exc))
    for what, bad in (("two seats inside the boss pitch",
                       ((0.0, 0.0), (seat_pitch_floor() - 1.0, 0.0))),
                      ("two rows of seats on one plate",
                       ((0.0, 0.0), (0.0, seat_pitch_floor() + 1.0)))):
        try:
            build_valve_tray(100.0, bad)
            fails.append(f"{what} were accepted")
        except ValueError:
            pass
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"ok  valve-tray  {height():g} mm high x {THICK:g} thick, seat {SEAT:g} (sunk), "
              f"reach {reach():g}, port channel {port_channel_depth():.3f} deep on "
              f"{channel_floor():.3f} of floor")
    return 1 if fails else 0


def trays_of_machine(facts):
    """The trays the enclosure stands, as `{name: (width, seats)}` in each plate's own frame.

    `enclosure_assembly` groups the valves no cap cradle holds by the plane each stands on and
    hands back one tray per plane, and the artifact carries what that grouping came to — so a
    plate is drawn off a machine the assembly's own run already stood.

    The doc-only `main` hands in the artifact and imports the assembly that decides it. Keeping
    those run dependencies in `main` leaves the shape functions' source closure at this part."""
    return facts.valve_trays


def main():
    sys.path.insert(0, str(_hw / "manifold-layout"))
    import enclosure_assembly as _ea                            # noqa: PLC0415
    import _facts                                               # noqa: PLC0415

    trays = trays_of_machine(_facts.read())
    print(f"Valve tray — {len(trays)} stood in enclosure-front-top: "
          f"{', '.join(sorted(trays))}")
    total = 0.0
    for name, (width, seats) in sorted(trays.items()):
        solid = build_valve_tray(width, seats).val()
        total += solid.Volume()
        print(f"  {name}: {width:g} x {height():g} x {THICK:g}, {len(seats)} seats at "
              + ", ".join(f"({x:.3f}, {y:.3f})" for x, y in seats))
        print(f"    material {solid.Volume() / 1000.0:.2f} cm^3, closed form "
              f"{tray_volume(width, len(seats)) / 1000.0:.2f} cm^3, valid {solid.isValid()}")
    width, seats = next(iter(sorted(trays.values())))
    print(f"  a post stands {grip():.3f} mm in the plate of {_seat.seat_top_z:g} mm")
    _ext = extrusion(_ea.EXTRUSION_W)
    print(f"  socket to port channel: {web():.4f} mm — "
          f"{100.0 * web() / _ext:.0f}% of a {_ext:g} bead")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "TRAY_W": f"{width:g}",
            "TRAY_H": f"{height():g}",
            "TRAY_T": f"{THICK:g}",
            "TRAY_D": f"{depth():g}",
            "TRAY_SEAT": f"{SEAT:g}",
            "TRAY_MARGIN": f"{MARGIN:g}",
            "TRAY_REACH": f"{reach():g}",
            "TRAY_SEATS": f"{len(seats)}",
            "TRAY_COUNT": f"{len(trays)}",
            "TRAY_VOL": f"{total / 1000.0:.2f}",
            "SOCKET_DIA": f"{2 * _seat.socket_radius:.4g}",
            "SOCKET_DEPTH": f"{_seat.socket_depth():g}",
            "SOCKET_FLOOR": f"{THICK - _seat.socket_depth():g}",
            "CHANNEL_DIA": f"{2 * (_valve.port_radius + PORT_SLIP):.4g}",
            "CHANNEL_DEPTH": f"{port_channel_depth():.2f}",
            "CHANNEL_FLOOR": f"{channel_floor():.2f}",
            "PORT_DROP": f"{port_drop():.2f}",
            "PORT_SLIP": f"{PORT_SLIP:g}",
            "TRAY_POST": f"{_seat.seat_top_z:g}",
            "TRAY_GRIP": f"{grip():.3f}",
            "TRAY_WEB": f"{web():.3f}",
            "TRAY_PORT_SLIP": f"{PORT_SLIP:g}",
            "TRAY_EXTRUSION": f"{_ext:g}",
            "TRAY_WEB_PCT": f"{100.0 * web() / _ext:.0f}",
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
