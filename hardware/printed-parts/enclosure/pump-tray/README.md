# Pump tray

**The pump case with its cylinder cut off.** [`pump_case.py`](/hardware/printed-parts/enclosure/pump-tray/pump_case.py) draws a two-piece case for the Kamoer — the body this tray is cut from, and no part of its own; its base is a plate on the pump head's crown, a 45° ramp off that plate, an octagonal bore wall standing in the ramp, and a cylindrical tower over the bore that the motor can turns in. Cut the tower off above the bore, cut down to one [3](SHOULDER) mm shoulder over it, and what is left is the tray — the same four surfaces, conforming to the same pump.

**It is not a part.** It is the pump cartridge's own material (`enclosure.build_cartridge`), fused onto the deck that slides out of the front bay — one per pump, off the stations `enclosure_assembly.pump_tray_stations` reads off the placed pumps, rooted on the cartridge face's own pump relief. Nothing ships under a pump and nothing is billed for one.

The flavour manifold carries two KPHM400 peristaltic pumps, one per channel. Each gets a tray: [2](TRAY_COUNT) per machine.

| | |
|---|---|
| plate | [70](TRAY_W) across × [69.405](TRAY_L) mm |
| case footprint it is cut from | [70](CASE_W) mm square, ramp [18](RAMP_H) mm high |
| bore wall | the boss's own octagon, [53](SOCKET_SPAN) mm at the flats, [1.5](SOCKET_LEDGE) mm ledges, [21](BOSS_DEPTH) mm deep |
| shoulder over the boss's crown | [3](SHOULDER) mm of tower, bored Ø[37](CAN_BORE) for the can |
| whole run on the pump's axis | [24](TRAY_D) mm |
| head under it | [62.61](HEAD_W) mm square, hanging [48.88](HEAD_D) mm below |
| what holds it | the pump cap, screwed up onto the cartridge on the bracket's own plane |
| material, both trays | [89.96](TRAY_VOL) cm³ of the pump cartridge |

## What it covers

**Two storeys of the pump, not one.** That is the whole reason it is a case and not a plate — no plate reaches both.

- The **base plate** lands on the head's own +Z face and wraps its top edge all the way round, [3218](ON_HEAD) mm² of section on that face.
- The **ramp** climbs off that plate at 45°.
- The **bore wall** takes the boss on each of its eight faces and both its ledges, over the boss's whole [21](BOSS_DEPTH) mm.
- The **shoulder** the cut tower leaves lands on the boss's crown and wraps its top edge, [1752](ON_CROWN) mm² on that face.

The [35.73](CAN_DIA) mm can rises out of the tower's own bore and the tray never touches it.

## What holds a pump

The bore and the cap do different jobs, and only one of them carries weight.

**The bore holds it square.** It is `pump_case.bore_profile`, ledges included — the section `kamoer_kphm400.build_rotor_housing` extrudes the boss on — so the tray takes the pump in X, in Y and in yaw over 21 mm of engagement. Nothing about where a pump sits is a number this part chose.

**The cap holds it up.** A pump stands in its tray, and what carries it is **the pump's own stamped mounting bracket**: the steel plate at the head-to-motor junction, [68.6](BRACKET_W) mm across where the head is 62.61, standing ~3 mm proud all round *in the very plane the tray's plate lands on*. `kamoer_kphm400` states that bracket ([`geometry-description.md`](/hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md) §3) and draws none of it — the three solids it builds are a coarse keep-out, and the bracket is not among them.

That plane is where the cartridge parts from its cap (`enclosure.cap_split_z`), so the lip is captured between the two printed pieces: the tray reaches past it from above, the cap's top face laps it from below, and two M3 on the lane between the pumps close the case.

## Where the two go

Read off the placed pumps at every build, never stated. `pump_tray_seats` reads each pump's own depth axis off its motor can — the can stands on the boss and the boss on the head — and takes the head's face at the far end of it. How far a tray runs to the front wall is the box's own figure, and it has to reach one [3](TRAY_MARGIN) mm margin past the head there or the plate does not wrap that edge. The `trays-hold` gate reads each pump against the tray on it.

Plate on head's crown, shoulder on boss's crown, bore on the boss's flanks — every one of them a plane or a shared wall, so a tray and the pump it takes share no volume.

**What ties a tray to the rest of the piece is the cartridge's, not the tray's.** A tray reaches the cartridge's face and nothing else, so `enclosure._tray_webs` closes the gaps it leaves inside that piece — one web between the two trays and one across-run to each edge of the deck — each this plate thick and in this plate's own band. There is no web to a side wall and none aft onto a panel: the deck is a loose piece, and what carries it is the bay's own floor, which the whole cartridge rides. The storey comes out one plate jamb to jamb, and what lands on the collet plate is the cap's aft face one storey down.

## Print

Both trays come off the bed inside the pump cartridge, which prints face-down on its outer skin. The deck stands as a wall off the face and the ramp, bore wall and shoulder grow off the plate's own section — nothing of the tray hangs and nothing takes support. The pump is laid in on the bench with the cartridge face-down, the cap screwed on over both heads, and the whole cartridge slides into the bay with the pumps aboard. PETG, the piece's own stock ([`bom.md`](/hardware/ledger/bom.md) §7).

## Files

- `pump_tray.py` — what the tray adds over the case, and one drawn in the pump's frame for the wall to place

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads the tray against the pump it takes and the case it is cut out of, including the section it carries on each of the two crowns.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/pump-tray/pump_tray.py`
