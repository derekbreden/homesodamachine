# Display receiver with 0.50 mm body X clearance

H2C accepted task **1296307760** at 2026-09-30T14:37:28.426282+00:00.
The native estimate is **2 h 49 min 30 sec**, **68.87 g** at the saved profile density.
This receiver takes the existing face-up cover from task 1294550319.

| Interface | Clearance |
|---|---:|
| Body X, each side, through the full 3.84 mm seating depth | 0.50 mm |
| Total body X travel | 1.00 mm |
| Body local Y, each end | 0.15 mm |
| Wing thickness to retaining roof | 0.60 mm |
| Wing tip in X, centered | 0.55 mm |
| Wing tip at full body X travel | 0.05 mm |
| Wing local Y end, each | 0.15 mm |
| Cover back seating datum | 0 mm |
| Minimum wing capture at full X travel | 2.60 mm |
| Retaining lip thickness | 1.80 mm |

The [solid comparison](geometry-delta.json) isolates the main-body X pocket:
70.1035 mm³ is removed entirely inside its full-depth opening, with no added
material. Wing pockets, thickness gap, glass and cover seating datums, and the
existing cover are held. The wing-thickness direction is local Z, corresponding
to nameplate Y. These local trial clearances do not change the shared fit rules.

[Geometry checks](geometry-check.json) verify seated pure-axis limits, capture
and open support exits. The ideal bend envelope clears 101 samples. Printed
corner contact, bow, insertion force and retention require the physical fit.

The receiver uses the enclosure's 30° print pose and shared PET-GF tree supports:
0.40 mm XY, 0.45 mm upper Z and 0.30 mm lower Z gaps. One support body is bed-rooted;
none starts on the model. Wing pockets open through the underside for removal.
Layers are 0.20 mm first and 0.24 mm above, with saved speeds, wall-first order
and 15% overlap. H2C uses the left black PET-GF spool and established +0.18 mm
trim, emitted as +0.16 mm on textured PEI. Usual startup options apply,
including Auto nozzle offset.

[Native verification](verification.json) binds source hashes, checksum, layer
planes, filament and support checks. [Launch](launch.json) records the accepted
job; [postlaunch status](postlaunch.json) confirms RUNNING without errors.
Mark2's preceding launch was more than three minutes earlier.
[Published artifacts](published-artifacts.json) match the live STEP and viewer
payload. [Geometry lint](geometry-lint.log) has no unaddressed findings.
