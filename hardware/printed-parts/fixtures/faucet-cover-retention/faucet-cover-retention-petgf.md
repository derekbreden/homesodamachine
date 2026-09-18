# Faucet cover retention print trial

The six engraved covers fit the unchanged printed Sculpted faucet tip. The
letters identify the test pieces after removal from the plate. Preload is the
inward offset per wing at the shared local N6.30 reference plane.

| ID | Preload per wing | Lip normal height | Print pose |
|---|---:|---:|---|
| A | 1.00 mm | 3.00 mm | Bezel down; CAD X +130° |
| B | 1.25 mm | 3.00 mm | Bezel down; CAD X +130° |
| C | 1.00 mm | 3.00 mm | Bezel up; CAD X −50° |
| D | 1.25 mm | 3.00 mm | Bezel up; CAD X −50° |
| E | 1.00 mm | 3.10 mm | Bezel up; CAD X −50° |
| F | 1.25 mm | 3.10 mm | Bezel up; CAD X −50° |

A/C and B/D compare print orientation. A/B, C/D and E/F compare preload.
The retained 0.24 mm slice gives C/E and D/F the same retaining top layer:
E/F are repeat specimens for print and fit consistency. Their 0.10 mm CAD
height increase does not produce an additional retaining layer. The letters are recessed
0.25 mm into the outer bezel, leaving 1.05 mm of local bezel stock.

The project places A, B and C in the front row, and D, E and F in the rear row,
each ordered left to right. Both row and column pitch are 90 mm. The same
STLs are used for the intended PET-GF color.

## Preparation

The CAD generator writes assembly-frame STLs and `trial-geometry.json`.
`prepare_print_project.py` checks that report's source and mesh hashes, copies
the successful Sculpted project's complete PET-GF settings, and calls the
shared faucet 3MF writer with the six named parts and their explicit poses.
The production Sculpted and Industrial projects and reports remain unchanged.

To prepare the editable project:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/fixtures/faucet-cover-retention/prepare_print_project.py
```

To produce the native printer archive and audit it, use a new output directory:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 tools/cad-venv/bin/python \
  hardware/printed-parts/fixtures/faucet-cover-retention/prepare_print_project.py \
  --slice-output .cache/prints/2026-09-18-faucet-cover-retention-mark2
```

This performs one local Bambu Studio slice with automatic rearrangement and
reorientation disabled. It exports `ready/faucet-cover-retention-mark2.gcode.3mf`
and the same emitted G-code used for the support audit. The staged input uses
the successful Mark2 job's external-spool metadata. The native validator checks
the archive, object identities, exact source meshes, emitted settings and Z trim
against that successful job, and records the known Bambu settings normalizations.
It does not connect to a printer or submit a job.

The preserved process uses a 0.4 mm nozzle, 0.24 mm layers, two wall loops and
15% grid infill. PET-GF uses 265 °C for the first layer and 280 °C thereafter,
an 80 °C textured plate, and 0–70% part cooling with the first three layers off.
The support top gap is 0.45 mm, with two top interface layers. The successful
job's requested +0.04 mm trim combines with the stock textured-plate correction
to emit +0.02 mm after the initial reset.

## Reading the result

The native six-cover plate estimates **1 h 38 min 22 s and 35.52 g** using
the saved density. It has 77 layers and no slicer warnings. The audited
toolpaths retain at least 45.85 mm of shared-bed border and 34.91 mm between
parts. The printer archive is
`.cache/prints/2026-09-18-faucet-cover-retention-mark2/ready/faucet-cover-retention-mark2.gcode.3mf`;
its SHA256 is `4ac5802ae1a4ee1c6f22f5048af6fd668cf114938616f39500505daf723ae251`.

`faucet-cover-retention-petgf.print.json` records each trial's identity, parameters,
STL digest, exact bed transform and embedded-mesh agreement. The native archive
and its validation are linked from `faucet-cover-retention-petgf.readiness.json`.

`faucet-cover-retention-petgf.support-audit.json` reads connected support bodies,
separate labelled interface islands, bed or model roots and build-up heights
from the native G-code. It also checks support and brim bounds for at least
15 mm of shared-bed border and 10 mm between parts. Time and grams are slicer
estimates; grams use the preserved profile's 1.29 g/cm³ density.

`faucet-cover-retention-petgf.support-faces.json` traces vertical rays from actual
labelled support-interface extrusion paths to the print mesh. It records the
sampled display coordinates and surface normals. These samples locate supported
faces; they do not prove the complete contact boundary.

| Pieces | Support topology and actual sampled contact |
|---|---|
| A/B, bezel down | Two bed-rooted bodies, one for each lip-bearing face at local N6.30. Both interfaces begin at print Z14.84, after 14.64 mm of build-up, and finish at Z15.08. |
| C–F, bezel up | One connected bed-rooted body with two labelled islands. The first supports the curved front inner bridge: Z12.44–13.16, with 12.24 mm of build-up. The second supports the planar inner bezel at local N20.55: Z16.52–16.76, with 16.32 mm of build-up. |

Every support body has labelled interface evidence. The flipped pose places the
gripping surfaces upward and moves these contacts to the inside of the cover.
Removal and the resulting surface finish still require physical inspection.

`faucet-cover-retention-petgf.retaining-layers.json` reads the actual model
toolpaths at three transverse stations within the lips. C, D, E and F all
finish their lip top-surface paths at commanded print Z3.08; the Z3.32 paths
return to the narrower side wall. C/E and D/F have minor path-placement
differences, but this slice does not preserve a distinct 0.10 mm height step.
The commanded layer positions are not a measurement of printed dimensions.

Keep the engraved IDs with the parts while comparing assembly force, retention
and contact finish on the printed tip. Those are physical test results.
