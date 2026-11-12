# Pump locating profile source

[`pump_tray.rs`](/hardware/printed-parts/enclosure/pump-tray/pump_tray.rs) draws the
case-derived locating profiles used at both pump stations by front-top's integral upper
inverse and `enclosure-pump-retainer`. It is not a separate printed part.
[`pump_case.py`](https://github.com/derekbreden/homesodamachine/blob/a518a57a878f02d9ac5b8b638c1c5883cadf6669/hardware/printed-parts/enclosure/pump-tray/pump_case.py) supplies the fitted
head profiles, the boss's octagonal bore and the motor-can opening. The production
construction is in
[`_fixed_pump_mount.py`](https://github.com/derekbreden/homesodamachine/blob/a518a57a878f02d9ac5b8b638c1c5883cadf6669/hardware/printed-parts/enclosure/enclosure/_fixed_pump_mount.py).

The flavour manifold carries KPHM600-SW3B17 pumps.

| | |
|---|---|
| case-profile footprint | mm square |
| octagonal location | mm at the flats, mm ledges, mm deep |
| motor-can opening | Ø mm |
| pump envelope below it | mm head, mm deep |
| molded flange envelope | mm across, with an 8 mm skirt between bearing faces |
| rear stack axis | mm toward Y− from the head and lower-retainer datum |

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

The current snap geometry evidence is in the
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

- [pump_tray.rs](pump_tray.rs) defines the fitted head, skirt and rear-stack profiles used by the native enclosure pieces.
