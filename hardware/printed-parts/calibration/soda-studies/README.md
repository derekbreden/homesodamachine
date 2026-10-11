# The Pour

The Pour gathers the home soda machine's printed surfaces and interfaces into a
single reference sculpture. Real faucet sections spiral around three angle
blades, with their curved faces and seams exposed to the light. Sliding fits,
support windows, the complete grip insert and a faucet cover snap give the hands
as much to compare as the eyes. Removable samples come out for close comparison
and return to marked places in the sculpture.

The upright desk reference occupies about 179 × 147 mm and stands 127 mm tall.
Its 53 printed components include the basin, captive shutters, helix, specimens
and marked holders. Every feature has a question to answer in the
[feature guide](feature-guide.md).

[Explore the assembled model](https://homesodamachine.com/3d#step:printed-parts%2Fcalibration%2Fsoda-studies%2Fthe-pour.step).

![The Pour](the-pour.step.png)

## Print and assemble

The [print kit](print-kit.zip) contains STL meshes, STEP geometry, editable Bambu
Studio projects, source snapshots and the guide. Its basin and three captive ripple shutters share
one print assembly. The projects use the
saved black PET-GF recipe and Mark2's left 0.4 mm nozzle with a 0.20 mm first layer. The
project files identify the layer height, seam settings or support gap assigned
to each specimen. Printer-specific trim and material mapping belong to the
chosen printer; the included Mark2 projects use its +0.04 mm requested trim.

Print the basin assembly, helix and tactile components from the kit projects. Print the three
finish projects, the seam project and the three support projects to populate
the sculpture. Keep the marked identities with their samples. Use the
[feature guide](feature-guide.md) to assemble the parts and read each comparison.
Keep the sculpture upright. Its removable samples and cut-face holders let a
reference surface sit beside a complete machine part under the same light.

The complete set has thirteen editable projects: three kit plates, three finish
plates, one seam plate, three support plates and separate projects for the R6
round, faucet cover and groove section. Native slicing estimates a total of
about 19 hours and 408 g using the saved material profile. Complete
model/support/brim paths stay at least 34 mm inside the usable bed boundary.
These are planning estimates for the prepared projects.

Import the meshes at 100% scale. Use the combined basin print-assembly STL or its
editable project to preserve the captive shutters' positions and gaps. The
individual specimen meshes stand in their own print frames. The assembled STEP
arranges them for display; it is a view of the completed object. The editable
projects retain independent print schedules for the comparisons.

## What the object contains

| Family | Comparison |
| --- | --- |
| N08, N12, N24 | Actual faucet neck sections at 0.08, 0.12 and 0.24 mm layers |
| NR00, NR05, NR15 | Regular seam closure with 0%, 5% and 15% seam gaps |
| NS00, NS10, NS20 | Contour scarf closure with 0%, 10% and 20% scarf gaps; length and start height held fixed |
| A08, A12, A24 | Curves and slopes at the three layer heights |
| R30, R45, R60 | Requested 0.30, 0.45 and 0.60 mm support distances; nominal roof separations of 0.24, 0.48 and 0.72 mm in the native slices |
| S05, S15, S25, S35, S45 | Sliding feel at 0.05, 0.15, 0.25, 0.35 and 0.45 mm clearance per side |
| G, GR | The complete grip insert at 0.08 mm layers and its adapted retaining receiver |
| Q24, Q48, Q72 | Captive print-in-place shutters with 0.24, 0.48 and 0.72 mm top gaps, with other clearances held fixed |
| Source surfaces and snap | The expanding R6 show round, enclosure flutes, and complete faucet display cover with its original groove section |
| Small details | Tube bores, raised/recessed markings, first-layer finish and a writable reference identity |

An identifier establishes which specimen is in a slot. The saved print project
establishes its recipe. Keep filament and printer details with each completed
object when comparing different setups. Record the observed sample, the setting
it suggests trying, and the corresponding complete-part result. Its original
full-scale geometry and the application scope of each sample are in the feature
guide. A blank [reference card](reference-card.csv) keeps the reference ID,
recipe, initial observation and complete-part result together.

Physical assembly, support cleanup and surface results for this object are
unrecorded. Accepted appearances and
fits from the machine remain scoped to their identified source prints. Small
samples help select a finish or fit to investigate on the complete part; they
do not establish the machine's load capacity or lifetime.

## Source and outputs

`reference.py` generates the individually printable geometry, labeled assembly
and `manifest.json`. Its compressed geometry inputs preserve the actual faucet
sections and complete cover used by the reference. `source_features.py` provides
the source cover, groove section and expanding R6 surface; `mount_geometry.py`
provides its rear-face locator. `prepare_prints.py` builds the editable comparison
projects from the saved PET-GF profile. `viewer_payload.py` retains the print
triangles in the 3D viewer; `package_kit.py` gathers the current meshes, projects
and guide into the downloadable kit. These are manual tools for this object.

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/printed-parts/calibration/soda-studies/reference.py
tools/cad-venv/bin/python hardware/printed-parts/calibration/soda-studies/prepare_prints.py --slice
tools/cad-venv/bin/python hardware/printed-parts/calibration/soda-studies/package_kit.py
```

The manifest records each part's identity, print frame, display placement and
source geometry. The print-project metadata records the saved settings and
native slicing results. Native slices and estimates describe the prepared
projects; they are not print results.
