# Display receiver with wing-thickness and body-side relief

H2C accepted task **1295323504** at 2026-09-30T05:59:58.173292+00:00.
The native estimate is **2 h 49 min 41 sec**, **68.86 g** at the saved profile density.
This receiver takes the existing face-up display cover from task 1294550319.

| Interface | Clearance |
|---|---:|
| Body X, each side, through the full 3.84 mm seating depth | 0.30 mm |
| Body local Y, each end | 0.15 mm |
| Wing thickness to retaining roof | 0.60 mm |
| Wing tip in X, centered | 0.55 mm |
| Wing tip at full body X travel | 0.25 mm |
| Wing local Y end, each | 0.15 mm |
| Cover back seating datum | 0 mm |
| Minimum wing capture at full X travel | 3.00 mm |
| Retaining lip thickness | 1.80 mm |

The thickness direction is local Z here, corresponding to nameplate Y.
Its 0.60 mm gap comprises 0.15 mm static clearance, 0.25 mm for the supported
roof and 0.20 mm local fit relief. These local trial values do not change the
shared clearance rules. The body opening includes the lower seated corners;
inverted fit only checks partial depth, as described in the
[physical observation](../2026-09-29-display-open-wing-receiver-h2c-v2/physical-result.json).

The [geometry comparison](geometry-delta.json) verifies the existing cover STL
and records the changed receiver volume. The small added strip from moving
the sloped support exit lies entirely behind the cover back plane. Seated
pure-axis limits, capture and continuous support exits are checked in
[geometry-check.json](geometry-check.json). The ideal bend envelope clears
101 samples; physical force, bow and corner contact remain unmeasured.

The receiver prints in the enclosure's 30° pose with shared PET-GF tree supports,
0.40 mm support XY, 0.45 mm upper Z and 0.30 mm lower Z gaps. The native audit
finds one bed-rooted body and no model-rooted bodies. The wing pockets open
through the underside for support removal. Layers are 0.20 mm first and
0.24 mm above, with saved speeds, wall-first order and 15% overlap. H2C uses
the left black PET-GF spool and established +0.18 mm trim, emitted as +0.16 mm
on textured PEI. Ordinary startup options apply, including Auto nozzle offset.

[Verification](verification.json) binds source hashes, native checksum, layer
planes, filament and support checks. [Launch](launch.json) records the accepted
job and more than three minutes after Mark2's collar start. [Published artifacts](published-artifacts.json)
confirms the STEP and viewer payload match the live site. [Geometry lint](geometry-lint.log)
has no unaddressed findings.
