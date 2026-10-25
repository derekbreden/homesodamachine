# Cold-core shell — Mark2 native preparation

Prepared for **Mark2, fixed left 0.8 mm High Flow**, with black Polymaker PET-GF
on external spool 254, reported as PET-CF `#161616`. **Not submitted.** The last
accepted Mark2 job used the left 0.4 mm nozzle; nozzle choice is pending.

The current fluted `foam-shell.stl` matches SHA256
`7d01002e13fcd3415ec89a60073545eed7a2b48703c7ad40f676efcdbd794b3d`.
It stands upright, floor down, centered at X162.5 / Y160 mm. Its envelope is
283 × 181 × 213.4 mm. Structural material behind the flutes and the floor
are 2 mm; slicer wall loops are a separate setting.

The warning-free native slice estimates **32 h 50 min 13 s**, **533 layers**
and **1251.8 g at the saved 1.29 g/cm³ accounting density**. The emitted bead
envelope leaves **20.87 mm** to the nearest usable bed edge. It has no support
or brim roads. Native trim resets with `G29.1 Z0`, then emits `G29.1 Z0.02`,
retaining Mark2’s requested +0.04 mm trim.

| Setting | Value |
| --- | --- |
| First / later layers | 0.40 / 0.40 mm |
| Line width | 0.82 mm |
| Walls / infill | 2 Classic / 15% gyroid |
| Top / bottom shells | 4 / 3 layers; 0.8 mm minimum top thickness |
| First / later nozzle temperature | 265 / 280°C |
| Plate / bed / chamber | Textured PEI / 80°C / unheated |
| Filament flow / maximum volume rate | 0.9555 / 18 mm³/s |
| Ordinary / auxiliary part cooling | 0% / 0% |
| Bridge / qualifying overhang cooling | 70% at 50% unsupported-width threshold |
| First three bed layers | Fan off |
| Supports / brim | Off / Auto configured, none emitted |
| Timelapse / bed leveling | On / On at launch |
| Flow / nozzle-offset calibration | Auto / Auto at launch |

[Settings](settings.json) records the native profile values, including speed
arrays. Emitted outer walls range from 10 to 61.29 mm/s, inner walls from
30 to 61.29 mm/s, bridges at 30 mm/s and labelled overhang walls at 10 mm/s;
the volume-rate limit constrains the nominal process speeds. Startup contains
its own native purge, temperature and cooling commands.

[Preparation](preparation.json) binds the geometry, editable project, native
archive and G-code hashes, with the command to reproduce the preparation.
[Native review](native-review.json) records the checksum, trim, placement and
first-to-second-layer overlap. These are commanded paths and bead envelopes;
physical finish, fit and load capacity remain observations of the printed part.

At launch, verify the left nozzle diameter and flow type, external-spool mapping,
standing calibration options and at least 180 seconds since a start or resume
on Mark1. No additional bed-clear confirmation is required by the print request.
