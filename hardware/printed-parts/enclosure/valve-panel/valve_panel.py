"""A VALVE PANEL IS A PLATE OF VALVE SEATS, and it is a wall of the enclosure.

One `valve_seat` per valve — four bosses, each with a blind socket a corner post presses into —
standing on a flat plate that runs from side wall to side wall of `enclosure-front-top`. It is
that piece's own material, fused in the way the tap-water trough, the meter's saddles and every
tube rib are: `enclosure._valve_panels` stands one per deck, off the stations
`enclosure_assembly.valve_panel_stations` reads off the placed valves. NO PANEL SHIPS AS A PART,
nothing bolts a valve to one and nothing is bonded — the posts in their sockets are the whole of
the retention, the same bargain the cold core's cap lid strikes under its three valves
(`_cold_core_interface.cap_cradles`).

    ACROSS  wall to wall. The plate is the piece, so it takes no slip and ends on the two
            interior faces
    ALONG   the seats' own reach off their valves' centres, and one `MARGIN` past that. The
            plate ends where the last boss does; the valves' collets and the tube butted into
            them hang past it

This module states the panel's own figures and draws one in its own frame; `enclosure` turns it
onto a deck and fuses it. The frame is `valve_seat`'s carried onto a plate:
  Z = out of the valve-side face, the direction a valve's own +Z runs. `z = 0` IS THAT FACE, so
      the plate spans z = −`THICK` to 0 and every seat stands on zero, the way a cradle stands
      on the cap lid's outer face.
  X = across the plate. Y = along it. Origin is the plate's centre in both.

A SEAT'S FOUR BOSSES ARE SQUARE, so a quarter turn carries one onto itself: a valve's yaw
locates it and never turns the print.

In the piece's own print orientation the plate stands vertical, wall to wall, and each boss is a
horizontal cylinder off it — the same cantilever the +X wall's mounting bosses print
(`enclosure._east_bosses`).

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-panel/valve_panel.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-panel/valve_panel.py selftest
"""

import sys
from pathlib import Path

import cadquery as cq

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


# --- what the panel adds over the seats it carries ---------------------------
#
# The plate's thickness, and it is the box's own wall.
THICK = 3.0
# Material carried past a boss's own outer edge, so the last boss is not a scallop in the
# plate's end. One wall, the same figure `valve_seat` puts around each socket.
MARGIN = 3.0
# The seat: every socket floor lands on the plate's own face, so a boss is the shortest column
# that still takes a post and the plate bores through nowhere.
SEAT = -_seat.socket_floor_z


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


def build_valve_panel(width: float, seats):
    """One panel: the plate, and one `valve_seat` standing on it per station in `seats`.

    `seats` is `(x, y)` per valve in the plate's own frame — where that valve's footprint centre
    lands. A station carries no yaw and no height: the seat is square, and every valve on one
    panel stands on one plane by construction."""
    if not seats:
        raise ValueError("a valve panel with no seats is a plate, and this machine prints none")
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
    panel = (cq.Workplane("XY")
             .workplane(offset=-THICK)
             .box(width, height(), THICK, centered=(True, True, False)))
    for x, y in seats:
        panel = panel.union(_seat.build_seat(SEAT).translate((x, y, SEAT)))
    return panel


def panel_volume(width: float, n_seats: int) -> float:
    """One panel's material, in closed form — the plate plus one seat apiece.

    A seat's four bosses stand clear of one another, each stands ON the plate's face rather than
    into it, and every socket floor lands on that same face: the fuse adds a plane and no
    volume, and the sockets take nothing out of the plate."""
    return width * height() * THICK + n_seats * _seat.seat_volume(SEAT)


def seat_face_gap() -> float:
    """The air between the plate's face and the valve's own port, at the port's lowest.

    The port hangs `beduan_solenoid.port_center_z` over the mounting plane and the plane stands
    `SEAT` over the face, so this is what a tube butted into a collet has under it."""
    return SEAT + _valve.port_center_z - _valve.port_radius


def depth() -> float:
    """The plate's whole run along its own Z — the plate under the face and the bosses over it.
    What the enclosure has to leave clear on a deck's plane."""
    return THICK + SEAT + _seat.seat_top_z


def selftest() -> int:
    """The panel against the valve it holds and the seat it carries."""
    fails = []
    if seat_face_gap() <= 0.0:
        fails.append(f"the plate's face stands {seat_face_gap():.3f} mm under the valve's port "
                     f"— the plate is in the tube's way")
    if SEAT < -_seat.socket_floor_z:
        fails.append(f"a seat of {SEAT:g} mm bores its sockets out through the plate's back")
    if THICK <= -_seat.socket_floor_z:
        fails.append(f"a plate {THICK:g} mm thick is no deeper than the "
                     f"{-_seat.socket_floor_z:g} mm a socket floor drops below the face it "
                     f"stands on")
    # A synthetic row of four at the closest pitch the part takes, so the construction is
    # measured here as well as where the machine stands its valves.
    pitch = seat_pitch_floor() + 1.0
    seats = tuple((i * pitch, 0.0) for i in (-1.5, -0.5, 0.5, 1.5))
    width = pitch * 4.0
    try:
        built = build_valve_panel(width, seats).val()
        closed = panel_volume(width, len(seats))
        if abs(built.Volume() - closed) > 1e-6 * closed:
            fails.append(f"a four-seat panel measures {built.Volume():.3f} mm^3 against the "
                         f"{closed:.3f} its closed form says — a boss has met its neighbour or "
                         f"run off the plate")
        bb = built.BoundingBox()
        if abs(bb.ylen - height()) > 1e-6:
            fails.append(f"a panel stands {bb.ylen:.4f} mm high against the {height():.4f} "
                         f"`height` declares")
    except Exception as exc:                                     # noqa: BLE001
        fails.append(str(exc))
    for what, bad in (("two seats inside the boss pitch",
                       ((0.0, 0.0), (seat_pitch_floor() - 1.0, 0.0))),
                      ("two rows of seats on one plate",
                       ((0.0, 0.0), (0.0, seat_pitch_floor() + 1.0)))):
        try:
            build_valve_panel(100.0, bad)
            fails.append(f"{what} were accepted")
        except ValueError:
            pass
    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"ok  valve-panel  {height():g} mm high x {THICK:g} thick, seat {SEAT:g}, "
              f"reach {reach():g}, {seat_face_gap():.3f} mm under the port")
    return 1 if fails else 0


def panels_of_machine():
    """The panels the enclosure stands, as `{name: (width, seats)}` in each plate's own frame.

    `enclosure_assembly` groups the valves no cap cradle holds by the plane each stands on and
    hands back one panel per plane. Imported inside the call, because that module builds its box
    out of this one's figures."""
    sys.path.insert(0, str(_hw / "manifold-layout"))
    import enclosure_assembly as _ea                            # noqa: PLC0415
    return _ea.valve_panel_plans()


def main():
    panels = panels_of_machine()
    print(f"Valve panel — {len(panels)} stood in enclosure-front-top: "
          f"{', '.join(sorted(panels))}")
    total = 0.0
    for name, (width, seats) in sorted(panels.items()):
        solid = build_valve_panel(width, seats).val()
        total += solid.Volume()
        print(f"  {name}: {width:g} x {height():g} x {THICK:g}, {len(seats)} seats at "
              + ", ".join(f"({x:.3f}, {y:.3f})" for x, y in seats))
        print(f"    material {solid.Volume() / 1000.0:.2f} cm^3, closed form "
              f"{panel_volume(width, len(seats)) / 1000.0:.2f} cm^3, valid {solid.isValid()}")
    width, seats = next(iter(sorted(panels.values())))

    substitute_md(
        _here.parent / "README.md",
        variables={
            "PANEL_W": f"{width:g}",
            "PANEL_H": f"{height():g}",
            "PANEL_T": f"{THICK:g}",
            "PANEL_D": f"{depth():g}",
            "PANEL_SEAT": f"{SEAT:g}",
            "PANEL_MARGIN": f"{MARGIN:g}",
            "PANEL_REACH": f"{reach():g}",
            "PANEL_SEATS": f"{len(seats)}",
            "PANEL_COUNT": f"{len(panels)}",
            "PANEL_VOL": f"{total / 1000.0:.2f}",
            "PORT_GAP": f"{seat_face_gap():.2f}",
            "SOCKET_DIA": f"{2 * _seat.socket_radius:.4g}",
            "BOSS_DIA": f"{2 * _seat.boss_radius:.4g}",
        },
        expected_counts={
            "PANEL_W": 1, "PANEL_H": 1, "PANEL_T": 1, "PANEL_D": 1, "PANEL_SEAT": 1,
            "PANEL_MARGIN": 1, "PANEL_REACH": 1, "PANEL_SEATS": 1, "PANEL_COUNT": 1,
            "PANEL_VOL": 1, "PORT_GAP": 1, "SOCKET_DIA": 1, "BOSS_DIA": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
