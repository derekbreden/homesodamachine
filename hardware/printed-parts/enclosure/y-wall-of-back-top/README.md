# Rear connection face

The rear connection face is part of `enclosure-back-top`, printed in PET-GF.
[above-core.json](/hardware/manifold-layout/above-core.json) supplies the native
fluid and dry-connector stations;
[_above_core_shell.py](/hardware/printed-parts/enclosure/enclosure/_above_core_shell.py)
cuts the wall and supports. The face manages connections. Each purchased
bulkhead seals the fluid around its tube; the printed wall carries its flange
and panel nut.

## Six fluid stations

Coordinates are enclosure-world millimetres. +Y is outward, toward the
customer's connections. Both columns use 32 mm vertical pitch.

| Row / Z | West / X37.25 | East / X77.5 |
|---|---|---|
| [328.000](GRID_TOP_Z) | TAP: PP010822E threaded inlet chain, white 1/4-inch | CO2: PISCO inlet neck, red 1/4-inch |
| [296.000](GRID_MIDDLE_Z) | OVER: ABU44M-E, white 4 mm vent | SODA: PP1208E, blue 1/4-inch outlet |
| [264.000](GRID_BOTTOM_Z) | FLAVOR: ABU44M-E, black 4 mm B outlet | FLAVOR: ABU44M-E, black 4 mm A outlet |

The main rear wall is 9 mm stock. The fluid field retains a 6 mm clamping
stack between Y465.3 and Y471.3. Each 1.8 mm identification tile stands in a
continuous side-rail channel at Y469.3–471.1, leaving 4 mm of printed wall
behind it and 0.2 mm below the fitting flange. The 32 mm-wide tiles share a
Z252 channel floor; the upper pair finish at Z355. TAP's bore follows the
scanned adapter axis rather than the nominal tile centre.

The water filter is upstream, on the customer's side of TAP. The threaded
PP010822E–GAGIRA–ASSE–PI4512F6S–PP061208W chain feeds the raised stem tee,
V-K and the flavor-water regulator. The ASSE vent points down into a TPU cup
with an aft-facing 4 mm OVER socket. PISCO's own inlet neck crosses the rear
wall; the ACVUS-44 check plugs directly into its outlet. OVER remains a
dedicated atmospheric return through the umbilical to its separate faucet
outlet above the bowl. See [internal plumbing](/hardware/assembly/internal-plumbing.md)
and [ASSE drain assembly](/hardware/assembly/asse-drain.md).

## Dry connections and nameplate

C14 is at X−68.5/Z330. Its native flange seats in a shallow outside pocket;
the body passes through the wall. Two short RX-M3S×4 inserts receive M3 × 10
socket-head screws through Ø7 × 0.5 mm washers. Each washer spans the native
flange countersink. The 3.25 mm flange/washer stack leaves 6.25 mm screw
projection; the 7.25 mm pilot retains 1 mm nominal tip air and 3 mm backing.
The C13 cord mates directly to the inlet's native rim and cavity.

The RiteAV RJ11 6P4C receptacle is at X−64/Z291.5. Its native tang and latch
engage the printed catches; the internal SIG-6 loom connects to its IDC
terminals. The RJ11 is the rectangular data connection, separate from the
six fluid ports.

The 104.53 × 38 mm nameplate sits below the ports at X−38/Z228. Its plain
field stands 2.2 mm beyond the main wall, placing the plate face at Y473.5.
This retains the accepted flat-wing interface, full 3.6 mm backing and 1.09 mm
nominal clearance to the core. The [nameplate acceptance](/hardware/printed-parts/enclosure/nameplate/README.md)
keeps its recorded material, orientation and artifact scope; the surrounding
host and its physical clearance remain subject to qualification.

The [rear identification generator](../rear-identification/rear_identification.py)
owns the compact chips, their matching wall pockets and the nameplate field.
None of these changes the fluid flange or nut seating planes.

## Tube identification and bundle

Blue identifies carbonated water, white identifies tap water and the separate
smaller OVER return, red identifies CO2, and black identifies both flavors.
The white TAP and OVER sockets take different tube diameters and carry their
own words. The same spool colors continue inside the enclosure.

The faucet umbilical carries soda, two flavors, OVER and the signal ribbon.
Connect the tail identified `flavor-a` to the east X77.5 socket and
`flavor-b` to the west X37.25 socket. Those identities continue inboard to
V-G and V-J respectively.
Only the soda tube receives the specified pipe insulation. PET braid covers
the prepared bundle; the organizer below the faucet mounting space keeps its
tubes in formation while allowing deliberate hand adjustment. Tube lengths,
insulation and braid preparation are specified in
[faucet and umbilical assembly](/hardware/assembly/faucet-and-umbilical.md).

## Evidence

Native checks cover the purchased bodies/nuts against the wall, compact-chip
row spacing and the nameplate field's clearance to the core. They do not
establish printed fit, tube insertion force, insert strength, pressure sealing
or lifetime. The selected components retain the limits in their part
references and the [mechanical qualification index](/hardware/mechanical-qualification/README.md).

## Sources

[value](NAME) texts are updated by `_y_wall_dimensions.py` from the production
rear grid. Color helpers in that module serve labels, tubing and installation art.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/y-wall-of-back-top/_y_wall_dimensions.py`
