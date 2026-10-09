# Valve seat

Four blind sockets locate the Beduan valve's corner posts. The valve's round body
lands on the surrounding face; the socket floors leave air beneath the post tips.
The sockets set the valve's position and hand fit. The enclosure trays' zip-tie
paths provide their positive retention.

    tools/cad-venv/bin/python hardware/printed-parts/valve-seat/valve_seat.py

`build_sockets()` supplies the four cuts for a supporting face. The enclosure's
[valve trays](/hardware/printed-parts/enclosure/valve-tray/README.md) use these holes
in their continuous plate.

`build_seat(seat)` supplies a raised plinth for the cold-core lid. Each plinth is
[37.6](PLINTH_WIDTH) × [38.05](PLINTH_DEPTH) mm in valve X and Y, with
R[3](PLINTH_CORNER) mm outer corners. Its broad bearing face carries the valve
beside an open cylindrical channel for the port.
The plinth's height places that face on the installed valve's bearing plane.

| Feature | Dimension |
|---|---|
| valve corner post | ⌀[6.9](POST_DIA) mm, on [24.4](CORNER_PITCH_X) × [24.85](CORNER_PITCH_Y) mm centres in valve X and Y |
| socket | ⌀[6.9](SOCKET_DIA) mm; [0 mm](SOCKET_CLEAR) nominal radial clearance |
| socket depth | [6.2](SOCKET_DEPTH) mm |
| bearing face | valve-frame Z[5.2](SEAT_TOP_Z) mm |
| socket floor | valve-frame Z[-1](SOCKET_FLOOR_Z) mm |
| stock to the outer outline | at least [3 mm](WALL) |
| valve port | ⌀[15.2](PORT_DIA) mm, with [1.000 mm](PORT_CLEARANCE) radial channel clearance |

The port channel follows the valve's Y axis. A placed plinth turns with the valve.
`port_clearance()` reads the actual gap.

The [printed fit selection](../enclosure/enclosure/magnet-retention/fit-coupons/physical-fit-selection.json)
sets **V69 / 6.90 mm** as the default socket. **V70 / 7.00 mm** is an explicitly
selected alternate to try when a valve or print orientation does not fit V69
well; the builder never switches sizes automatically. The valve's catalog post
diameter and pitch remain the reference hardware dimensions. Holder outlines,
body bearing faces, port clearance, socket depth and blind floors stay on their
own dimensions when the bore changes.

The [selected geometry check](../enclosure/enclosure/magnet-retention/fit-coupons/selected-geometry-check.json)
verifies the native socket cuts, exterior envelope, bearing and blind-floor
datums, port clearance and shared cold-core stock datum.

The preferred hand fit belongs to the tested valve and upright enclosure-oriented
PET-GF panel. Shared cold-core plinths and other print orientations require their
own installed fit observation. No insertion force, retention load or lifetime
is established by the selected bore.

The [cold-core top cap lid](/hardware/printed-parts/cold-core/foam-cap/foam_cap.py)
carries three plinths at `_cold_core_interface.cap_cradles`. The reservoir-B fill
conduit has an open vertical passage along its neighbouring plinth's edge. The lid's
pour opening and vents remain accessible.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/valve-seat/valve_seat.py`
