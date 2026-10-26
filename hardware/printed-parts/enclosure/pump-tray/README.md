# Pump locating profile source

[`pump_tray.py`](/hardware/printed-parts/enclosure/pump-tray/pump_tray.py) draws the
case-derived locating profiles used at both pump stations by front-top's integral upper
inverse and `enclosure-pump-retainer`. It is not a separate printed part.
[`pump_case.py`](/hardware/printed-parts/enclosure/pump-tray/pump_case.py) supplies the fitted
head profiles, the boss's octagonal bore and the motor-can opening. The production
construction is in
[`_fixed_pump_mount.py`](/hardware/printed-parts/enclosure/enclosure/_fixed_pump_mount.py).

The flavour manifold carries [2](TRAY_COUNT) KPHM600-SW3B17 pumps.

| | |
|---|---|
| case-profile footprint | [70](CASE_W) mm square |
| octagonal location | [53](SOCKET_SPAN) mm at the flats, [1.5](SOCKET_LEDGE) mm ledges, [21](BOSS_DEPTH) mm deep |
| motor-can opening | Ø[37](CAN_BORE) mm |
| pump envelope below it | [62.61](HEAD_W) mm head, [47.88](HEAD_D) mm deep |
| molded flange envelope | [62.61](BRACKET_W) mm across, with an 8 mm skirt between bearing faces |
| rear stack axis | [1](REAR_AXIS_Y_SHIFT) mm toward Y− from the head and lower-retainer datum |

## How production uses the profiles

`boss_room` supplies the octagonal cut on each pump's offset rear-stack axis.
Front-top's upper inverse adds the motor and terminal room inside one broad body continuous
to the display housing and roof. `drop_well` supplies the lower retainer's fitted head well
and flat skirt-support lands. Production reads the pump's seated drop for the actual flange
and lower land datums.

The prepared pump/retainer unit enters motor-first from underneath loose front-top.
Two full-depth integral wings snap into front-top’s flank receivers, capturing the molded
skirts between the fitted faces. The four tube stubs rise through bottom-open tee-wall
gates. The [integral mount description](/hardware/printed-parts/enclosure/enclosure/README.md#integral-pump-mount)
and [bench procedure](/hardware/assembly/internal-plumbing.md) define the complete assembly.

## Verification

`pump_tray.py selftest` checks the case-derived source solid, locating profiles and reference
clearances. The current snap geometry evidence is in the
[pump-snap review](/hardware/printed-parts/enclosure/enclosure/pump-snap-review/README.md).
The [pump-mount receipts](/hardware/printed-parts/enclosure/enclosure/pump-mount-review/README.md)
bind their identified three-screw articles.

The [accepted physical observation](/hardware/reference/kamoer-kphm400/physical-fit.json)
records firm holding without observed vertical play in its identified separate cradle and
cap. It does not identify the actual load-bearing contact surfaces or qualify the integral
upper/lower skirt capture. The [scan review](/hardware/reference/kamoer-kphm400/scan-review.md)
retains its measured-surface and registration scope. Physical assembly force, retention,
vibration and lifetime of the integral mount remain unqualified.

Short inserted 1/4-inch LLDPE stubs in the scans are external tubing in silicone; they do not
define the rigid pump envelope. Actual tube insertion marks and joint checks belong to the
bench procedure.

## Print

The upper profiles print within `enclosure-front-top`; the lower profiles print within
`enclosure-pump-retainer`, both in PET-GF. Their print preparation and support access belong
to those production pieces ([`bom.md`](/hardware/ledger/bom.md) §7).

## Files

- `pump_tray.py` — the fitted profile source, source collar builder and dimensional selftest
- `pump_case.py` — the case-derived geometry supplying the head, skirt and rear-stack profiles

Run with `tools/cad-venv/bin/python` per the hardware context file.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/pump-tray/pump_tray.py`
