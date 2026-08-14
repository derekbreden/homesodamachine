# Pump tray

**The pump case with its cylinder cut off.** [`../../flavor/pump-case/`](/hardware/printed-parts/flavor/pump-case/) draws a two-piece case for the Kamoer; its base is a plate on the pump head's crown, a 45° ramp off that plate, an octagonal bore wall standing in the ramp, and a cylindrical tower over the bore that the motor can turns in. Cut the tower off above the bore, cut down to one [3](SHOULDER) mm shoulder over it, and what is left is the tray — the same four surfaces, conforming to the same pump.

**It is not a part.** It is `enclosure-front-top`'s own material, fused the way the tap-water trough, the flow meter's saddles and the valve panels are — `enclosure._pump_trays` stands one, off the stations `enclosure_assembly.pump_tray_stations` reads off the placed pumps. Nothing ships under a pump and nothing is billed for one.

The flavour manifold carries two KPHM400 peristaltic pumps, one per channel. Each gets a tray: [2](TRAY_COUNT) per machine.

| | |
|---|---|
| plate | [82.262](TRAY_W) across × [80.305](TRAY_L) mm |
| case footprint it is cut from | [70](CASE_W) mm square, ramp [18](RAMP_H) mm high |
| bore wall | the boss's own octagon, [53](SOCKET_SPAN) mm at the flats, [1.5](SOCKET_LEDGE) mm ledges, [21](BOSS_DEPTH) mm deep |
| shoulder over the boss's crown | [3](SHOULDER) mm of tower, bored Ø[37](CAN_BORE) for the can |
| whole run on the pump's axis | [24](TRAY_D) mm |
| head under it | [62.61](HEAD_W) mm square, hanging [48.88](HEAD_D) mm below |
| channels | 4 — a pair either side of the can, each band [25](BAND_NEAR)–[30.83](BAND_FAR) mm off the pump's axis |
| straps | 2 per pump, [4.826](STRAP_W) mm across, [143](STRAP_LOOP) mm of loop apiece |
| material, both trays | [99.56](TRAY_VOL) cm³ of `enclosure-front-top` |

## What it covers

**Two storeys of the pump, not one.** That is the whole reason it is a case and not a plate — no plate reaches both.

- The **base plate** lands on the head's own +Z face and wraps its top edge all the way round, [4829](ON_HEAD) mm² of section on that face.
- The **ramp** climbs off that plate at 45°.
- The **bore wall** takes the boss on each of its eight faces and both its ledges, over the boss's whole [21](BOSS_DEPTH) mm.
- The **shoulder** the cut tower leaves lands on the boss's crown and wraps its top edge, [1752](ON_CROWN) mm² on that face.

The [35.73](CAN_DIA) mm can rises out of the tower's own bore and the tray never touches it.

## What holds a pump

The bore and the straps do different jobs, and only one of them carries weight.

**The bore holds it square.** It is `pump_case.bore_profile`, ledges included — the section `kamoer_kphm400.build_rotor_housing` extrudes the boss on — so the tray takes the pump in X, in Y and in yaw over 21 mm of engagement. Nothing about where a pump sits is a number this part chose.

**The straps hold it up.** A pump hangs UNDER its tray, so the tray on its own holds nothing — the same bargain the meter's saddles and the regulator's rib strike. Two ties close round the tray's plate and **the pump's own stamped mounting bracket**: the steel plate at the head-to-motor junction, [68.6](BRACKET_W) mm across where the head is 62.61, standing ~3 mm proud all round *in the very plane the tray's plate lands on*. `kamoer_kphm400` states that bracket ([`geometry-description.md`](/hardware/off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md) §3) and draws none of it — the three solids it builds are a coarse keep-out, and the bracket is not among them.

Each tie runs across the plate's face, down a channel at either end of that run, and back under the lip. **It never reaches the head's depth**, which is why plate and bracket make a [143](STRAP_LOOP) mm loop and the 8" tie the tap-water trough already takes closes it, rather than a length of its own.

The band each strap lies in is clear of the can where the run crosses the shoulder, and carried out to the head's edge where the lip stands: inboard of the can's radius the run lies against the can, and outboard of the bracket's half-width the legs come down off the lip they reach under.

## Where the two go

Read off the placed pumps at every build, never stated. `pump_tray_seats` reads each pump's own depth axis off its motor can — the can stands on the boss and the boss on the head — and takes the head's face at the far end of it. How far a tray runs to the front wall is the box's own figure, and it has to reach one [3](TRAY_MARGIN) mm margin past the head there or the plate does not wrap that edge. The `trays-hold` gate reads each pump against the tray on it.

Plate on head's crown, shoulder on boss's crown, bore on the boss's flanks — every one of them a plane or a shared wall, so a tray and the pump it takes share no volume.

**What ties a tray to the rest of the piece is the box's, not the tray's.** A tray reaches the front wall and nothing else, so `enclosure._tray_webs` closes the four gaps around it — one web to each side wall, one between the two trays, one aft onto the valve panel — each this plate thick and in this plate's own band. The storey comes out one plate wall to wall.

## Print

Both trays come off the bed inside `enclosure-front-top`, which prints ceiling-down. The plate goes down first and everything above it — ramp, bore wall, shoulder — grows off its underside, so the only face that hangs is the plate's own. It is a soffit over the lane its pump hangs in, anchored along its whole width where it meets the wall, and it takes print support the way the tap-water trough's block and the drip tray's rails do. The pump is laid into it that way up, both straps threaded through their channels first — there is no reaching under a seated pump afterwards. PETG, the piece's own stock ([`bom.md`](/hardware/ledger/bom.md) §7, in the front-pieces row).

## Files

- `pump_tray.py` — what the tray adds over the case, and one drawn in the pump's frame for the wall to place

Run with `tools/cad-venv/bin/python` per the hardware context file. `selftest` reads the tray against the pump it takes and the case it is cut out of, including the section it carries on each of the two crowns.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/pump-tray/pump_tray.py`
