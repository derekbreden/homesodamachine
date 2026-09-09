# Valve seat

Four blind sockets locate the Beduan valve's corner posts. The valve's round body
lands on the surrounding face; the socket floors leave air beneath the post tips.
The sockets retain the valve without screws or inserts.

    tools/cad-venv/bin/python hardware/printed-parts/valve-seat/valve_seat.py

`build_sockets()` supplies the four cuts for a supporting face. The enclosure's
[valve trays](/hardware/printed-parts/enclosure/valve-tray/README.md) use these holes
in their continuous plate.

`build_seat(seat)` supplies a raised plinth for the cold-core lid. Each plinth is
[37.6](PLINTH_WIDTH) mm square with R[3](PLINTH_CORNER) mm outer corners. Its broad
bearing face carries the valve beside an open cylindrical channel for the port.
The plinth's height places that face on the installed valve's bearing plane.

| Feature | Dimension |
|---|---|
| valve corner post | ⌀[6.8](POST_DIA) mm, centres [12.2 mm](CORNER_INSET) from each centreline |
| socket | ⌀[7.2](SOCKET_DIA) mm; [0.2 mm](SOCKET_CLEAR) radial clearance |
| socket depth | [7](SOCKET_DEPTH) mm |
| bearing face | valve-frame Z[6](SEAT_TOP_Z) mm |
| socket floor | valve-frame Z[-1](SOCKET_FLOOR_Z) mm |
| stock to the outer outline | at least [3 mm](WALL) |
| valve port | ⌀[15](PORT_DIA) mm, with [1.000 mm](PORT_CLEARANCE) radial channel clearance |

The port channel follows the valve's Y axis. A placed plinth turns with the valve.
`port_clearance()` reads the actual gap, and `fouled_volume()` checks the plinth
against the complete seated valve.

The [cold-core top cap lid](/hardware/printed-parts/cold-core/foam-cap/foam_cap.py)
carries three plinths at `_cold_core_interface.cap_cradles`. The reservoir-B fill
conduit has an open vertical passage along its neighbouring plinth's edge. The lid's
pour opening and vents remain accessible.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-seat/valve_seat.py`
