# Valve seat

**Four sockets. There is nothing between them.**

How this machine holds a Beduan solenoid on a printed face: one blind socket under each of the
valve's four corner posts, the post pressed into it. The posts in their sockets are the whole of
the retention — no screw, no insert, nothing bonded. The valve's round body boss lands on
whatever the sockets open in, and on every seat but one that is what sets its height.

    tools/cad-venv/bin/python hardware/printed-parts/valve-seat/valve_seat.py

`valve_seat.py` builds no part of its own. A seat is a FEATURE on whatever face carries the
valve, and **the face decides which of two forms it takes**:

- **Sunk** — `build_sockets()` hands back the four holes for a face to CUT. A boss is material
  round a socket, and a face [7](SOCKET_DEPTH) mm deep plus a wall behind is that material
  already. The valve lands on the face itself. Both valve trays take this form
  ([`../enclosure/valve-tray/`](/hardware/printed-parts/enclosure/valve-tray/README.md)),
  and a valve seats the same way on either of them.
- **Stood** — `build_seat(seat)` hands back the four bosses for a face to FUSE, for a face
  thinner than a socket is deep. The valve lands on the four boss tops. The cold core's cap
  lid takes this form.

One seat, one socket, two ways to carry it.

| | |
|---|---|
| corner post | ⌀[6.8](POST_DIA) mm, [12.2 mm](CORNER_INSET) inset from the footprint centre |
| socket | ⌀[7.2](SOCKET_DIA) mm — [0.2 mm](SOCKET_CLEAR) radial, the press fit |
| socket depth | [7](SOCKET_DEPTH) mm, boss top to socket floor — the same hole either way |
| boss (stood only) | ⌀[13.2](BOSS_DIA) mm — the socket plus [3 mm](WALL) of wall |
| boss top | z [6](SEAT_TOP_Z) mm, where the valve's round boss begins, and where a sunk seat's face is |
| socket floor | z [-1](SOCKET_FLOOR_Z) mm, under the post tips, so a post bottoms on nothing |

## The port

The valve's ⌀[15](PORT_DIA) port hangs **below** the boss tops and runs between them, on the axis
the two collets face along. The inboard shoulder of each ⌀[13.2](BOSS_DIA) boss stands
[0.210 mm](PORT_CLEARANCE) off it. A SUNK seat has no boss for it to run between — its face is
at the boss tops, so the port hangs inside that face and whatever carries the seat opens a
channel for it (`valve_tray.build_port_channel`).

`port_clearance()` reads that gap and `main()` holds it against [0.2 mm](SOCKET_CLEAR), the same
clearance the sockets are cut on — a seat clears a valve as freely as it grips one.
`fouled_volume()` reads the whole of it: a seat and the valve it holds share **no volume**.

## Who prints one

Two parts. The cold core's top cap lid carries three: `_cold_core_interface.cap_cradles` is the
table of stations and [`foam_cap.add_cradles`](/hardware/printed-parts/cold-core/foam-cap/foam_cap.py)
stands them on the lid's outer face. The other eight are sunk into the two **valve trays**
([`../enclosure/valve-tray/`](/hardware/printed-parts/enclosure/valve-tray/README.md)) — a
plate of four seats under each of the flavour pack's two decks, printed into
`enclosure-front-top` wall to wall.

A seat is square, so a quarter turn carries it onto itself: a station's yaw locates the valve
and does not turn the print.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-seat/valve_seat.py`
