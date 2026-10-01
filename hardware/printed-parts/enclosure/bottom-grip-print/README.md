# Bottom enclosure print packages

These packages print the complete enclosure bottoms with the integrated grip
receivers. H2C prints front-bottom and Mark2 prints back-bottom, using black
PET-GF through each printer's left 0.4 mm nozzle.

The production meshes contain the receiver cuts checked in
[`production-integration.json`](../grip-cover/production-integration.json).
The grip receiver coupons passed physical support removal and assembled fit;
their evidence is in
[`physical-acceptance.json`](../grip-cover/physical-acceptance.json).

The shared [`petgf.3mf`](../../petgf.3mf) provides the temperatures, speeds,
wall order, 15% infill overlap, and automatic tree supports. The first layer is
0.20 mm. Ordinary layers and the expanding grip transitions are 0.24 mm. Six
walls are scoped to print Z 35.0–41.5 mm; the normal two walls apply elsewhere.
The inward flute runouts use 0.08 mm layers at print Z 41.5–44.3 mm.

Native support paint excludes both grip-wing slots in each bottom and the
exterior expanding transitions. Each slot's support exclusion extends 1 mm
onto the surrounding ceiling to keep wider tree-interface roads clear of the
slot mouth. The broad flat lifting ceilings retain tree
supports, inset 0.8 mm from the contact edge. The slot roofs bridge across
their 5.30 mm span. Support inspection includes extrusion without object
labels, not only slicer-tagged objects.

The back-bottom's seven nearby through-going branch roads have at least
0.308 mm of nominal air to the model's extrusion envelope. They continue
upward and have no interface or terminating tip on the exterior transition.
The retained support interfaces serve the flat lifting ceilings and seam
rail catches, with exits through the handhold openings and exposed rail
flanks. Physical removal on the complete bottoms remains a print check.

`prepare.py` builds an immutable native project and invokes Bambu Studio's
slicer. `verify.py` checks the source hashes, native archive, actual layer and
wall bands, slot bridge coverage, support intrusion, and plate margins. Each
printer's directory contains its preview, preflight report, support audit,
and launch status. An accepted job has a `launch.json` receipt with the
printer's task ID. The native projects and sliced archives live under
`.cache/prints/`; their exact paths and hashes are retained in the reports.

Mark2's submitted archive is a print-only copy for Bambu Studio. Its
[`print-only-package.json`](mark2/print-only-package.json) records the container
changes and byte-identical G-code verification. Editable model geometry is omitted
from that copy; the reviewed project and source meshes remain the preparation inputs.

Launch settings are Timelapse On, Bed Leveling On, Flow Calibration Auto, and
Nozzle Offset Calibration Auto. The requested Z trims are +0.18 mm on H2C
and +0.04 mm on Mark2; the textured-plate compensation produces +0.16 mm and
+0.02 mm respectively. Starts and resumes on the two printers are separated
by at least three minutes.
