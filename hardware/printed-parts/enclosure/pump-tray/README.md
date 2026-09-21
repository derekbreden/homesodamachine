# Pump clamp collar source

[`pump_tray.py`](/hardware/printed-parts/enclosure/pump-tray/pump_tray.py) draws the
case-derived collar used twice in `enclosure-pump-cap`. It is not a separate printed part.
[`pump_case.py`](/hardware/printed-parts/enclosure/pump-tray/pump_case.py) supplies the fitted
surfaces: a plate and 45° ramp at the holder station plane, the boss's octagonal bore wall,
and one shoulder around the motor can.

The flavour manifold carries two KPHM600-SW3B17 pumps, so the top clamp contains
[2](TRAY_COUNT) collars.

| | |
|---|---|
| source footprint | [70](TRAY_W) across × [70.909](TRAY_L) mm |
| case footprint | [70](CASE_W) mm square, ramp [18](RAMP_H) mm high |
| octagonal location | [53](SOCKET_SPAN) mm at the flats, [1.5](SOCKET_LEDGE) mm ledges, [21](BOSS_DEPTH) mm deep |
| shoulder | [3](SHOULDER) mm over the boss, bored Ø[37](CAN_BORE) for the can |
| complete collar rise | [24](TRAY_D) mm |
| pump envelope below it | [62.61](HEAD_W) mm head, [47.88](HEAD_D) mm deep |
| molded flange envelope | [62.61](BRACKET_W) mm across, with an 8 mm skirt between bearing faces |
| rear stack axis | [1](REAR_AXIS_Y_SHIFT) mm toward Y− from the head and lower-cradle datum |

## How it becomes the clamp

`enclosure._pump_clamp_gross` uses the case-derived octagon and can openings on the reference
pump's offset rear-stack axis. Its broad underside, locating profiles and screw seats share
the physically accepted holder datums. Two top-access M3 screws close the cap onto the pumps
while the lower cradle takes the load. The surrounding crown reaches the cartridge's top edge;
two wider terminal wells leave the motor ends open.

The pump's front rim clears the continuous bay floor; the floor is not a competing pump seat.
The physical pump pose includes the holder's seated drop, and the four outlet paths read that
same pose. Short inserted 1/4-inch LLDPE stubs in the scans are external tubing in silicone;
they do not define the rigid pump envelope.

## Verification

`pump_tray.py selftest` checks the case-derived source solid, locating profiles and reference
clearances. Independent physical observations and native cap/cradle contact checks are in
[the scan review](/hardware/reference/kamoer-kphm400/scan-review.md) and
[check_pump_contacts.py](/hardware/reference/kamoer-kphm400/check_pump_contacts.py).
The new cap and relieved floor still require a dry assembly check with the physical pumps.

## Print

Both collars print inside the top clamp. Their ramps and octagonal walls grow from the
pressing plate; the two screw heads remain accessible from above. Black PET-GF, the clamp's own stock
([`bom.md`](/hardware/ledger/bom.md) §7).

## Files

- `pump_tray.py` — the conformal collar source and dimensional selftest
- `pump_case.py` — the fitted pump-case geometry from which the collar is cut

Run with `tools/cad-venv/bin/python` per the hardware context file.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/pump-tray/pump_tray.py`
