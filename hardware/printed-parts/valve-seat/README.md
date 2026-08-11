# Valve seat

**Four bosses. There is nothing between them.**

How this machine holds a Beduan solenoid on a printed face: one boss under each of the valve's
four corner posts, each carrying a blind socket the post presses into. The posts in their
sockets are the whole of the retention — no screw, no insert, nothing bonded — and the valve's
round body boss lands on the boss tops, which is what sets its height.

    tools/cad-venv/bin/python hardware/printed-parts/valve-seat/valve_seat.py

`valve_seat.py` builds no part of its own. A seat is a FEATURE, cut into whatever face carries
the valve, and `build_seat(seat)` hands back the four bosses in the valve's own frame for that
face to fuse on.

| | |
|---|---|
| corner post | ⌀[6.8](POST_DIA) mm, [12.2](CORNER_INSET) mm inset from the footprint centre |
| socket | ⌀[7.2](SOCKET_DIA) mm — [0.2 mm](SOCKET_CLEAR) radial, the press fit |
| boss | ⌀[13.2](BOSS_DIA) mm — the socket plus [3 mm](WALL) of wall |
| boss top | z [6](SEAT_TOP_Z) mm, where the valve's round boss begins |
| socket floor | z [-1](SOCKET_FLOOR_Z) mm, under the post tips, so a post bottoms on nothing |

## The port

The valve's ⌀[15](PORT_DIA) port hangs **below** the boss tops and runs between them, on the axis
the two collets face along. The inboard shoulder of each ⌀[13.2](BOSS_DIA) boss stands
[0.210 mm](PORT_CLEARANCE) off it.

`port_clearance()` reads that gap and `main()` holds it against [0.2 mm](SOCKET_CLEAR), the same
clearance the sockets are cut on — a seat clears a valve as freely as it grips one.
`fouled_volume()` reads the whole of it: a seat and the valve it holds share **no volume**.

## Who prints one

Two parts. The cold core's top cap lid carries three: `_cold_core_interface.cap_cradles` is the
table of stations and [`foam_cap.add_cradles`](/hardware/printed-parts/cold-core/foam-cap/foam_cap.py)
stands them on the lid's outer face. The other eight stand on the two **valve panels**
([`../enclosure/valve-panel/`](/hardware/printed-parts/enclosure/valve-panel/README.md)) — a
plate of four seats under each of the flavour pack's two decks, printed into
`enclosure-front-top` wall to wall.

A seat is square, so a quarter turn carries it onto itself: a station's yaw locates the valve
and does not turn the print.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-seat/valve_seat.py`
