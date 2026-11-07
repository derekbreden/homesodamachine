# Regulator entry comparison

The comparison pairs the standard pointed regulator cover with a cover whose
free tips flare outward along the installed Y axis. The flared cover has a
longer planar lead-in. Its spring walls, roots, retaining faces and fitted
hardware bearings retain the standard cover's geometry. Both covers use the
same complete receiver, including its axial stops and enclosure roof stock.

The receiver is cropped from the production back-top solid. Its pocket clears
both covers. [geometry.json](geometry.json) records the tip dimensions, retained
lower profiles, seated overlaps and roof stock. Insertion force and directional
tolerance await the physical comparison.

Generate these actual print articles after rebuilding back-top:

```sh
python3 tools/run.py -- tools/hsm/target/release/rear-equipment-caps --regulator-entry-study
```

The `regulator-entry-comparison` recipe in
[pieces.json](../../trial-preparation/pieces.json) prints the common receiver,
standard pointed cover and flared cover on Mark2. The receiver retains
back-top's layer direction and prints without cavity supports. The caps stand
on their production axial ends. The plate uses a shared fine layer schedule
for the receiver, caps and native smooth-timelapse tower; the ordinary
production cap recipe retains its own layer schedule. Temperatures and
localized cooling follow the production PET-GF recipe.

The [prepared plate](prepared-print.json) records the native slice and cooling
interval. Printing awaits Derek's review of the proposed tip geometry.
