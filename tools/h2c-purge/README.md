# H2C left-nozzle PET-GF purge and wipe

This maintenance job runs the H2C's homing and nozzle checks, prepares the loaded
left external filament, extrudes into the purge chute, wipes the nozzle, parks and
turns the heaters off. Its archive contains no printable geometry and deposits no
model or prime line on the bed.

The supported trial configuration is **H2C's fixed left hardened 0.4 mm nozzle,
black PET-GF on external spool 254**, labelled PET-CF in the printer. The right
nozzle is unused. This is an idle-printer maintenance job, not a mid-print command.
Use a clear bed because the retained homing and detection sequence moves the bed
and toolhead. Keep the shared-circuit three-minute startup spacing.

## Build and run

From the repository root:

```sh
python3 tools/h2c-purge/prepare.py
```

The builder uses the checked-in G-code and package metadata, verifies the program
and checksum, and writes:

```text
.cache/h2c-purge-v1/h2c-left-petgf-purge-v1.gcode.3mf
.cache/h2c-purge-v1/preflight.json
```

Import a separate copy into Bambu Connect, choose **H2C**, and map **Left Nozzle**
to the black **Ext PET-CF** tile. Keep the usual launch options: Timelapse On, Auto
bed leveling On, Flow dynamic calibration Auto, and Nozzle Offset Calibration
Auto. The maintenance file contains no leveling or calibration blocks; it does
not change the standing launch options. Send once and verify the new job ID and
filename. Wait for FINISH, no print error/HMS, and zero heater targets.

The file is maintenance G-code packaged for Connect. Do not reslice it as a part
or copy its machine-start field into a production print profile.

## Program and source

[source.json](source.json) identifies the native H2C job and manufacturer's startup
sequence used to build [the program](h2c-left-petgf-purge.gcode). The explicit
chute purge is 45 mm of filament at 280°C and 449.008 mm/min, followed by a 3 mm
retraction and the native `G150.2`, `G150.1` and `G150 T265` wiping sequence.
The retained material-preparation routine uses the PET-GF profile's 300°C flush
and 265°C initial-temperature parameters; any extrusion inside that firmware
routine is additional to the explicit 45 mm.

Bed and chamber heat targets are zero. Cleanup turns both hotends off, ends any
active timelapse, restores soft endstops and releases the motors. There is no
print-end filament unload/cut command. Homing temporarily resets the live Z trim;
the next normal print applies its own established trim through its startup file.
No persistent calibration-save command is issued.

The six-minute duration and 0.14 g shown by Connect are packaging estimates;
0.14 g accounts only for the explicit purge. They are not a slicer measurement of
the complete maintenance routine.

## Trial status

H2C job **1298050950** reports FINISH at 100%, zero printed layers, no print error
and no HMS. The observed stages include homing, surface/nozzle checks, material
preparation and nozzle wiping. Connect confirms both nozzle heater targets, bed
target and chamber target are zero at completion.

[The trial record](trial-v1/result.json) separates command completion from physical
observation. Filament ejection and tip cleanliness need the user's observation;
the telemetry does not measure those outcomes. Prevention of the reported
idle-time extrusion overload is untested. This trial does not establish a
maintenance interval or compatibility with another nozzle/material combination.
