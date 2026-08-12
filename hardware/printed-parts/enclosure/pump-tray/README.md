# Pump tray

A plate with a hole for a Kamoer's motor can and an octagonal socket under it for that pump's
rear boss, standing inside `enclosure-front-top`. **It is not a part.** It is that piece's own
material, fused the way the tap-water trough, the flow meter's saddles and the valve panels are —
`enclosure._pump_trays` stands one, off the stations `enclosure_assembly.pump_tray_stations`
reads off the placed pumps. Nothing ships under a pump and nothing is billed for one.

The flavour manifold carries two KPHM400 peristaltic pumps, one per channel. Each gets a tray:
[2](TRAY_COUNT) per machine.

| | |
|---|---|
| plate | [82.262](TRAY_W) wide × [68.61](TRAY_L) × [3](TRAY_T) mm |
| can bore | Ø[37](CAN_BORE) — the can itself is Ø[35.73](CAN_DIA) |
| socket | the boss's own octagon, [53](SOCKET_SPAN) mm at the flats, [1.5](SOCKET_LEDGE) mm ledges |
| socket depth | [21](BOSS_DEPTH) mm, the boss's whole run off the head's face |
| whole run on the pump's axis | [24](TRAY_D) mm |
| head under it | [62.61](HEAD_W) mm square, hanging [48.88](HEAD_D) mm below |
| channels | 2, in the band [19](BAND_NEAR)–[24.83](BAND_FAR) mm off the pump's axis |
| strap | [4.826](STRAP_W) mm across, one per pump, [273.0](STRAP_LOOP) mm of loop |
| material, both trays | [48.93](TRAY_VOL) cm³ of `enclosure-front-top` |

## What holds a pump

The socket and the strap do different jobs, and only one of them carries weight.

**The socket holds it square.** The hole and the socket are the two-piece pump case's own bore:
`pump_case.cylinder_id` is the tower the can turns in, and `pump_case.bore_profile` is the octagon
that case seats the boss in, ledges included — the section `kamoer_kphm400.build_rotor_housing`
extrudes the boss on. The socket takes that boss in X, in Y and in yaw over its whole
[21](BOSS_DEPTH) mm. Nothing about where a pump sits is a number this part chose.

**The strap holds it up.** A pump hangs UNDER its tray, so the plate on its own holds nothing —
the same bargain the meter's saddles and the regulator's rib strike. One zip tie closes round the
pump and the plate together: down one channel, past the socket and down that flank of the head,
across the head's front face, up the far flank and back up the other channel. Pump and plate make
a [273.0](STRAP_LOOP) mm loop.

The two channels stand outside the head, so the run between them crosses the plate's own face.
That run has to clear the can and still land on the head, and what the can leaves of the head's
square is the band that is both.

## Where the two go

Read off the placed pumps at every build, never stated. `pump_tray_seats` reads each pump's own
depth axis off its motor can — the can stands on the boss and the boss on the head — and takes
the head's face at the far end of it. How far a plate runs to the front wall is the box's own
figure, one [3](TRAY_MARGIN) mm margin past the head at the other end. The `trays-hold` gate
reads each pump against the plate on it.

The plate lands on the boss's crown and the socket's rim on the head's face; both are planes, and
a tray and the pump it takes share no volume.

## Print

Both trays come off the bed inside `enclosure-front-top`, which prints ceiling-down. The plate
goes down first, wall to socket, and the socket's octagon walls grow off its underside — no
overhang anywhere in the socket. The plate itself is a horizontal soffit over the lane its pump
hangs in and takes print support the way the tap-water trough's block and the drip tray's rails
do. The pump is laid into it that way up, its strap threaded through both channels first — there
is no reaching under a seated pump afterwards. PETG, the piece's own stock
([`bom.md`](/hardware/ledger/bom.md) §7, in the front-pieces row).

## Files

- `pump_tray.py` — the tray's own figures, and one drawn in the pump's frame for the wall to place

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads the tray
against the pump it takes and the case it is bored like.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/pump-tray/pump_tray.py`
