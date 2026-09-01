# Pump clamp collar source

[`pump_tray.py`](/hardware/printed-parts/enclosure/pump-tray/pump_tray.py) draws the
case-derived collar used twice in `enclosure-pump-cap`. It is not a separate printed part.
[`pump_case.py`](/hardware/printed-parts/enclosure/pump-tray/pump_case.py) supplies the fitted
surfaces: a plate and 45° ramp at the pump's bracket plane, the boss's octagonal bore wall,
and one shoulder around the motor can.

The flavour manifold carries two KPHM400 pumps, so the top clamp contains
[2](TRAY_COUNT) collars.

| | |
|---|---|
| source footprint | [70](TRAY_W) across × [69.405](TRAY_L) mm |
| case footprint | [70](CASE_W) mm square, ramp [18](RAMP_H) mm high |
| octagonal location | [53](SOCKET_SPAN) mm at the flats, [1.5](SOCKET_LEDGE) mm ledges, [21](BOSS_DEPTH) mm deep |
| shoulder | [3](SHOULDER) mm over the boss, bored Ø[37](CAN_BORE) for the can |
| complete collar rise | [24](TRAY_D) mm |
| pump envelope below it | [62.61](HEAD_W) mm head, [48.88](HEAD_D) mm deep |
| stamped bracket | [68.6](BRACKET_W) mm square, stated by the pump reference and added to assembly checks |
| rear stack axis | [1](REAR_AXIS_Y_SHIFT) mm toward Y− from the head and lower-cradle datum |

## How it becomes the clamp

`enclosure._pump_clamp_gross` places the broad pressing field on each pump's head datum and the
case-derived collar on the reference pump's offset rear-stack axis. The pump reference does not
draw the stamped bracket, so the enclosure builder starts the complete clamp field on that
bracket's measured upper face. The field supplies the pressing section there, re-cuts the
boss's exact octagon, and joins both collars with two centre screw bridges.

The finished clamp therefore has three distinct contacts:

- the pressing annulus closes on the bracket's top face;
- the octagonal wall locates the white boss in X, Y and yaw above the bracket;
- the shoulder surrounds the motor can at the boss crown.

The lower cradle bears under the bracket. Two top-access M3 screws draw the clamp onto that
cradle, so no collar or screw hidden below the pumps carries their weight.

## Verification

`pump_tray.py selftest` checks that the source is one valid solid, clears the drawn pump bodies,
covers the bracket footprint, and retains material on both case-derived axial storeys. The
enclosure assembly adds the omitted bracket to the pump drop and clamp drop sweeps, reads the
octagonal contact against each boss, and probes printed bearing above and below three bracket
sides.

## Print

Both collars print inside the top clamp. Their ramps and octagonal walls grow from the
pressing plate; the two screw heads remain accessible from above. PETG, the clamp's own stock
([`bom.md`](/hardware/ledger/bom.md) §7).

## Files

- `pump_tray.py` — the conformal collar source and dimensional selftest
- `pump_case.py` — the fitted pump-case geometry from which the collar is cut

Run with `tools/cad-venv/bin/python` per the hardware context file.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/pump-tray/pump_tray.py`
