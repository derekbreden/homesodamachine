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
customer's connections. Viewed from behind, screen-left is +X. The row
pitches are 37.0 and 30.2 mm.

| Row / Z | Left / X76.5 | Right / X28.8 |
|---|---|---|
| | CO2: PISCO inlet neck, red 1/4-inch | TAP: PP010822E threaded inlet chain, white 1/4-inch |
| | SODA: PP1208E, blue 1/4-inch outlet | FLAVOR: ABU44M-E, black 4 mm A outlet |
| | DRAIN: ABU44M-E, white 4 mm vent | FLAVOR: ABU44M-E, black 4 mm B outlet |

The main rear wall is 9 mm stock. The fluid field retains a 6 mm clamping
stack between Y465.3 and Y471.3. Each 1.8 mm identification tile stands in a
continuous side-rail channel at Y469.3–471.1, leaving 4 mm of printed wall
behind it and 0.2 mm below the fitting flange. The 42 × 38 mm tiles share a
Z240.6 channel floor; 2 mm rail overlaps leave 38 × 38 mm visible faces.
The upper pair finish at Z355, with 0.2 mm seams between cards. The bottom
row carries its words below the fittings; the other words are above them. TAP's bore follows the
scanned adapter axis rather than the nominal tile centre.

The water filter is upstream, on the customer's side of TAP. The threaded
PP010822E–GAGIRA–ASSE–PI4512F6S–PP061208W chain feeds the raised stem tee,
V-K and the flavor-water regulator. The ASSE vent points down into a TPU cup
with its 4 mm DRAIN socket facing fore and clocked 15° toward the meter. PISCO's own inlet neck crosses the rear
wall; the neoFit ACHV44-E check plugs directly into its outlet. DRAIN remains a
dedicated atmospheric return through the umbilical to its separate faucet
outlet above the bowl. See [internal plumbing](/hardware/assembly/internal-plumbing.md)
and [ASSE drain assembly](/hardware/assembly/asse-drain.md).

## Dry connections and nameplate

The mains inlet loads from inside the enclosure. Its flange sits in an internal
pocket, with the raised rim bearing on the pocket floor. Washer-backed screws
enter the short inserts from inside; the washers spread the load on the moulded ears. The mounting stock joins the rear wall, west flank and ceiling.
Only the rounded cord passage opens on the outside. Its clearance includes the
cord plug's retention ribs, and the ceiling remains continuous above the pocket.
The [rear-wall recipe](../enclosure/back-top/rear.rs) owns the geometry and the
[hardware ledger](/hardware/ledger/bom.md) lists the screws, washers and inserts.

The RiteAV RJ11 6P4C receptacle is at X−64/Z291.5. Its native tang and latch
engage the printed catches; the internal SIG-6 loom connects to its IDC
terminals. The RJ11 is the rectangular data connection, separate from the
six fluid ports.

The 104.53 × 38 mm nameplate sits below the ports at X0/Z200. Its plain
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
smaller DRAIN return, red identifies CO2, and black identifies both flavors.
The white TAP and DRAIN sockets take different tube diameters and carry their
own words. The same spool colors continue inside the enclosure.

The faucet umbilical carries soda, two flavors, DRAIN and the signal ribbon.
Connect the two black tails to the right column’s FLAVOR sockets in either
order. The upper socket continues inboard to V-G; the lower socket to V-J.
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

`_y_wall_dimensions.py` reads its dimensions from the production rear grid. Color helpers in that module serve labels, tubing and installation art.
