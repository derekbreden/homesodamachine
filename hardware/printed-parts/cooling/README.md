# PET-GF cooling

Ordinary PET-GF paths print with part cooling off. High cooling belongs to the
bridges, unsupported underside paths and their fresh foundation courses. A short layer time does
not turn cooling on for an entire part or layer. Auxiliary part cooling is off.

| Bambu setting | Current value |
| --- | ---: |
| Minimum / maximum part fan speed | 0% / 0% |
| Force cooling for overhangs and bridges | On |
| Overhang fan threshold | 50% unsupported bead width |
| Overhang / bridge fan speed | 70% |
| Keep fan always on | Off |
| Fan pre-start time | 0 s |
| Auxiliary part fan | 0% |
| First three bed layers | Fan off |

Up to 100% cooling is acceptable for a feature whose underside needs it. Apply
that choice to the qualifying overhang/bridge paths and their foundations. Ordinary walls, infill and
support paths retain their native cooling outside those foundations. Exhaust
and hotend heatsink fans serve other purposes and retain their machine settings.

Bambu Studio's **0% overhang threshold means all exterior walls**, even walls
with no overhang. It does not mean cooling is restricted to overhangs. The
[installed-version configuration definitions](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp)
describe the threshold and fan-always-on behavior. Fan pre-start is zero so a
bridge does not request cooling on preceding ordinary paths. The native G-code
still needs a reading for a particular plate: the physical fan takes time to
change speed, and a setting does not establish mechanical strength.

The [successful fan-off display cover](../faucet/faucet-display-cover/prints/2026-10-17-cooling-off-prepared-mark2/physical-result.json)
passed normal display loading and cover installation. Derek also reports other
faucet parts breaking during that installation. These observations support
removing general cooling. They do not establish strength, endurance or a
single cause for every fracture. Polymaker's
[PET-GF15 printing guidance](https://wiki.polymaker.com/polymaker-products/polymaker-filaments/fiberon-tm/fiberon-tm-pet-gf15)
specifies fan off and suggests slower printing for layer-adhesion trouble.
The faucet's existing bridge flow and bridge/overhang speeds remain selected
for underside finish. Recovery courses use their filament's bridge speed limit;
ordinary process speeds and temperatures retain their selected values.

## Recovery foundations

The shared output stage follows the model footprint of native-cooled bridge
and overhang paths into the immediately following courses. Within that
footprint it retains underside cooling and limits deposition to the selected
bridge speed. The depth and footprint resolution belong to the shared
[cooling catalog](../../../tools/hsm/shared-data/catalog/scalars.json).
The rule follows each object's actual paths, including curved paths and
filament changes. A floating-shell label alone does not request cooling.
Travel speeds, extrusion amounts, supports and other device commands retain
their native settings.

The [rail command reading](../enclosure/enclosure/prints/2026-11-05-back-top-smooth-corners-mark2/rail-cooling.json)
records the photographed print's native cooling and the foundation correction.
The [prepared-output reading](recovery-preparation.json) records the current
enclosure and pump outputs, command preservation and scope exercises. Finish
and strength remain physical observations.

## Selected stretches

A part's recipe may name one stretch of its model paths for part cooling. The
Sculpted tip's [finish selection](../faucet/sculpted/finish-selection.json) cools
its paths by the dispense face. The preparer adds the fan commands as its last
G-code stage, which changes no motion or extrusion; paths outside the stretch
keep the cooling above.

## Small individual parts

Time spent printing the rest of a batch is part of the PET-GF recipe. Derek
identifies that interval as necessary for the complete faucet and batches of
snap covers, and expects an isolated small cover to overheat without it. This
is a printing constraint; it does not call for general part cooling or a
change to the approved snap geometry.

A batch uses the time spent on its other articles. Measure each small part's
actual return intervals before adding a tower or an away-from-part wait.
Preserve each article's production layer schedule; a receiver's fine layers
do not require fine layers on the covers. The
[regulator comparison](../enclosure/rear-equipment-caps/prints/2026-11-07-taller-tips-mark2/job.json)
records the separate article schedules and return times on its tower-free plate.

The `single-regulator-cap` recipe in
[`pieces.json`](../enclosure/trial-preparation/pieces.json) uses native smooth
timelapse and a prime tower to keep the hot nozzle away between cap layers,
then reprime before returning. Its cap pose, deposition recipe, temperatures
and localized cooling follow production. Select Timelapse On when sending.
The declared tower width is retained with rib-wall mode disabled: the
[installed slicer's tower planner](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/GCode/WipeTower.cpp)
otherwise resizes a single-colour smooth-timelapse tower. Enabling a tower
alone does not establish a useful interval.

The [individual-regulator print record](../enclosure/rear-equipment-caps/prints/2026-11-07-single-regulator-mark2/job.json)
holds the selected settings, emitted timing, archive identity and launch.
Derek reports that the print turned out fine. Its timing is commanded motion
time, and no separate strength result is reported. That successful finish
applies to the recorded cap and recipe; it is not a qualified thermal limit
for every small part. Read the actual emitted tower paths when preparing
another shape or height.

[Cura's minimum-layer-time and Lift Head settings](https://support.ultimaker.com/articles/Knowledge/1667417947135)
provide slowdown and an away-from-part wait. A
[Bambu user's cooling approach](https://forum.bambulab.com/t/park-hotend-for-minimum-layer-time/70222/2)
uses smooth timelapse for the same purpose. These describe ways to schedule
cooling time, rather than transferable PET-GF temperatures or fan settings.

## Current projects

[petgf.3mf](../petgf.3mf) contains the selected values in both the project
settings and embedded filament preset. The `petgf-cooling` program
([`petgf_cooling.rs`](../cadlib/petgf_cooling.rs)) applies them when a print preparer
lays PET-GF out from a source profile, including a retained historical profile. It
leaves other materials alone. The Industrial and Sculpted faucet preparers also apply
the selected localized recipe explicitly. A prepared project registers the program as
its Bambu Studio post-processing script, as do the editable projects in the inventory
below. Native command-line preparation uses
an input copy without the GUI hook and applies the shared output stage after
slicing. The editable source project retains its hook. The preparers package
the processed native paths, checksum and preparation
record. Repeated preparation retains the already processed paths. This output
stage runs during print preparation.

The [editable-template inventory](current-projects.json) identifies the updated
enclosure, label, tool, lever, vent-tool and organizer projects and their
hashes. Their mesh and build members are unchanged. Re-slice these editable
projects to obtain the current cooling commands. Native archives of completed
prints retain the exact commands used for their reported physical results;
they are historical evidence, not the current production recipe. Older
identified trial projects, including the September display trial, retain their
original hashes too. The current complete faucet recipes are
[Industrial](../faucet/industrial/faucet-industrial-petgf.md) and
[Sculpted](../faucet/sculpted/README.md).
