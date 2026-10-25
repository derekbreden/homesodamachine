# Sculpted display cover with front overlap — Mark2

Mark2 accepted **one black PET-GF cover**, task **1374330388**, at
**11:57:04 CDT on October 25**. The [launch receipt](launch.json) records one
Bambu Connect CUA Send and a successful printer reply. The job entered PREPARE;
Connect displays homing, 0/67 layers and the correct archive name. The
[startup reading](startup.json) at **11:58:51 CDT** reports RUNNING, 0/67
layers, 23 minutes remaining, no print error and no HMS.
Mark1's task 1374272357 was accepted at 11:39:30 CDT, satisfying the shared
circuit's three-minute start spacing. The existing preflight camera notification
has the same HMS code in the acceptance reading; the startup reading has no HMS.

The [front-corner study](../../corner-overlap-review/2026-10-25/README.md)
extends the two front skirt edges to overlap the tip ledge by 1.2 mm in side
projection. It addresses the visible opening in the
[accepted head's photographs](../../../industrial/prints/2026-10-24-buttons-sculpted-bands020-mark2/physical-result/physical-result.json).
The print retains that cover's glass gap, neck clearance, bezel and snap datums.
The tip and display have no changes. The
[physical result and five photographs](physical-result/physical-result.json)
record working fit and approval. A corner gap remains and is accepted as good
enough; no further iteration is requested. The complete production recipe uses
Bambu’s default 0.20 mm first bed layer and 0.24 mm later layers without fine
bands, with the remaining settings retained. This archived cover print used a
0.24 mm first layer. The [production selection](../../../industrial/production-selection.json)
binds the approved sources and subsequent print defaults.

The [complete settings export](all-settings.json) contains all 582 prepared and
583 native project settings, the embedded filament preset and object XML.
Prepared project settings and filament presets are byte-identical to the
accepted complete-faucet recipe. The cover's object overrides are retained.
The [native reading](native-review.json) binds the exact archive and G-code,
checksum, layer increments, cooling commands, speeds and deposited-bead bounds.

| Setting | Value |
| --- | --- |
| Printer / nozzle | Mark2 H2C / fixed left hardened 0.4 mm Standard flow |
| Material / mapping | Black Polymaker PET-GF / external 254, PET-CF `#161616` |
| Plate / bed | Textured PEI / 80°C |
| First / later nozzle temperature | 265 / 280°C |
| Requested / emitted Z trim | +0.04 / +0.02 mm; trim reset first |
| First / all later layer heights | 0.24 / 0.24 mm |
| Variable layer ranges / independent support heights | None / Off |
| Walls / infill / wall generator | 2 / 15% grid / Classic |
| Top / bottom shells | 4 layers, minimum 1 mm / 3 layers |
| Filament flow / volumetric limit | 0.9555 / 18 mm³/s |
| Bridge flow / speed | 125% / 15 mm/s |
| Overhang tiers / fully overhung | 15 / 15 / 15 / 10 mm/s / 10 mm/s |
| Ordinary / auxiliary fan | 0% / 0% |
| Bridges and qualifying overhangs | 70% fan at 50% unsupported-width threshold |
| First three bed layers | Fan off through Z0.72 |
| Retraction / Z hop / wipe | 0.8 mm at 30 mm/s / 0.4 mm Auto Lift / Off |
| Seam | Aligned, 15% gap, scarf Off |
| Automatic supports | Tree(auto), Default, 35° threshold |
| Support top / bottom / XY gaps | 0.45 / 0.30 / 0.40 mm |
| Top / bottom interfaces | 2 / 2 layers at 0.50 / 0.50 mm spacing |
| Brim | Auto, 5 mm, 0.1 mm gap |
| Orientation / placement | X −50°, centered |
| Timelapse / bed leveling | On / On |
| Flow / nozzle-offset calibration | Auto / Auto |

The warning-free native slice estimates **23 min 5 s / 5.85 g** at saved density,
with **67 layers**. Every layer increment is 0.24 mm. The minimum full-bead
clearance to the usable bed boundary is **131.0164 mm**. The support reading
contains one bed-rooted automatic support body and one interface island.
The native trim commands are `G29.1 Z0` and `G29.1 Z0.02`.

`prepare.py` writes the centered one-cover project. Slice with Bambu Studio
`--slice 0 --arrange 0 --orient 0 --outputdir <directory> --export-3mf <basename.gcode.3mf>`;
the export argument is a basename inside the output directory. `review.py`
reads the native archive. `observe_launch.py` only watches acceptance and does
not issue a print command. The imported Connect copy is separate from the
preserved native archive, with matching bytes at submission.
