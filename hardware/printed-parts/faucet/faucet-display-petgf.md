# Faucet tip and complete display-cover print

[`faucet-display-petgf.3mf`](faucet-display-petgf.3mf) contains the production
tip and two instances of the same complete Sculpted cover STL. The cover
preload is 1.25 mm per wing. Keep the two covers identified by plate position
when removing them.

| Plate position | Part | CAD X rotation | Bed face |
|---|---|---:|---|
| Left | Production faucet shell tip | +40° | Dispense face |
| Middle | Complete Sculpted display cover | +40° | Front wall |
| Right | Same complete Sculpted display cover | −50° | Lower skirt and lip ends; bezel up |

The +40° pose makes local S the build direction. The groove floor/roof and
cover lip bearing planes are vertical. The right-hand cover presents its
bearing planes upward. Both covers use the exact same geometry and settings.

The native slice estimates **2 h 6 min 13 s and 50.43 g**, with 462 layers
and no slicer warnings. Slicer mass uses the saved profile's 1.29 g/cm³ density.
The audited support and brim toolpaths retain at least 40.89 mm of shared-bed
border and 42.92 mm between parts.

## Profile and preparation

The successful Sculpted PET-GF profile is preserved byte-for-byte from
`.cache/prints/2026-09-18-faucet-display-mark2/baseline-faucet-petgf.3mf`.
It uses a 0.4 mm nozzle, 0.24 mm layers, two walls and 15% grid infill;
265/280 °C nozzle temperatures, an 80 °C textured plate and 0–70% cooling
with the first three layers off. The support top gap is 0.45 mm with two
interface layers. The native file's emitted settings match the successful
job, including the resulting +0.02 mm Z trim.

To refresh the three-part project and the two editable full-part projects:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/prepare_display_print.py --refresh-production
```

The full Sculpted and Industrial plates are refreshed without slicing them.
Their readiness files state that their current full-plate slices are pending.

For one native slice, use a new directory:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/faucet/prepare_display_print.py \
  --slice-output .cache/prints/2026-09-18-faucet-display-mark2/native-slice
```

This runs the installed Bambu Studio CLI locally, with arrangement and
orientation disabled. It never connects to a printer. The native archive is
`native-slice/ready/faucet-display-mark2.gcode.3mf` under the job directory;
its SHA256 is `defdde770a54b0f22db742c291448d5238ae0a6fe6165c4670103c0786b3034e`.
`--review-existing` reads that directory again without another slice.

## Actual support contacts

The support audit reads the retained native G-code. Mesh rays begin at actual
labelled interface extrusion paths; their coordinates and normals are in
[`faucet-display-petgf.support-faces.json`](faucet-display-petgf.support-faces.json).
These samples identify contacted faces, not every contact boundary.

| Part | Retained supports and sampled function |
|---|---|
| Tip | One bed-rooted body and one small model-rooted patch. Five labelled islands reach the aft display-channel wall at S47.24, the outside of the neck-joint plug, the flavor passage and the signal lane near the open joint. The display-channel interface starts at Z46.28 after 46.08 mm of build-up and ends at Z46.76. The small patch starts at Z89 and shares the plug interface. The groove floor and roof have no sampled support contact. |
| Middle cover, front down | One bed-rooted body with two labelled islands at the rear display-window edge and rear inner closure. Interfaces start at Z44.12 and Z46.28, after 43.92 and 46.08 mm of build-up. The lip bearing faces and planar inner bezel have no sampled support contact. |
| Right cover, bezel up | One bed-rooted body with two labelled islands: the curved front inner bridge at Z12.44–13.16 and planar inner bezel at Z16.52–16.76. Build-up is 12.24 and 16.32 mm. The lip bearing faces have no sampled support contact. |

Every support body has labelled interface evidence. Remove the tip's supports
through its display opening and open neck joint before routing tubes and wire.
Preserve the groove working planes, joint surface and passages during removal.
Cover support removal is through the open underside before loading the display.
Removal effort, contact finish and retention remain physical print readings.

## Recorded checks

The [print report](faucet-display-petgf.print.json) records the source hashes,
bed transforms and exact embedded-mesh agreement. Both cover instances have
the same STL digest. The [readiness record](faucet-display-petgf.readiness.json)
records the native archive, profile, support audit, current geometry fit report
and printer submission status.

[`faucet-display-petgf.retention-toolpaths.json`](faucet-display-petgf.retention-toolpaths.json)
reads groove and lip height envelopes from the actual commanded extrusion
paths at twenty X/S columns per part. It includes line width and layer height;
lip internal infill voids are included within the outside height envelope.
The sampled groove gap is 3.478–3.556 mm. The front-down cover's lip envelope
is 2.998 mm; the bezel-up cover's is 3.078 mm. Subtracting each maximum lip
height from the minimum sampled groove gives 0.480 and 0.400 mm respectively.
It does not model bead shape, sag, shrinkage, roughness or elastic assembly.
The physical print establishes fit and retention.
