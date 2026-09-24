# Tee carrier: six walls through the lower curve

Mark2 task `1279390313` prints one unsupported carrier in black PET-GF. The
[sender receipt](sender-receipt.json) verifies acceptance, and the
[launch reading](mark2-launch.json) records the subsequent printer state.
Derek reports **no spaghetti failure**, with a lower surface that curves slightly inward
rather than forming the intended outward round. His assessment is **“probably good enough
for now.”** The [physical result](physical-result.json) is provisional: the
[printer reading](physical-feedback-reading.json) is RUNNING at 47/189 layers, with no error.
Whole-print completion and assembled fit are not assessed by that observation.

The lower **print-Z 0–6.1 mm** band requests **six walls**. The base setting remains
**two walls**, including the upper rounded band. Infill prints before the inner walls and
outer walls; Bambu retains its wall-first sequence on the first layer. **Infill/wall overlap
is 15%** and **all process and filament speed and acceleration settings are unchanged**.
The only global setting change is `is_infill_first = 1`; the lower range adds only
`wall_loops = 6` to its existing 0.08 mm layer height. [Preparation](preparation.json).

Derek observes edge failure between infill contacts; where infill meets the wall, the
outside edge appears to hold its position better. The
[stopped v13 result](../2026-09-24-tee-carrier-plate-mark2-v13/physical-result.json) records that observation.
This combined wall trial tests whether a thicker perimeter, deposited after the infill,
holds those intervening stretches. Its individual effects are not isolated.

The [emitted-path review](wall-review.json) reads six wall crossings at the left end on
every layer 1–76, two on layers 77–113, and infill before the walls in the observed failure
band. Native settings retain two walls above the lower band, subject to the inherited
top-surface wall reduction. The speed limits remain 200 mm/s outer and 300 mm/s inner,
with the inherited first-layer, overhang and volumetric limits.

![Actual wall paths below and above the band](wall-comparison.png)

All **189 layer heights** match v13: 76 at 0.08 mm to Z 6.08, 37 at 0.24 mm to Z 14.96,
and 76 at 0.08 mm to Z 21.04. Complete visible R6 rounds use 0.08 mm, including the first
layer. There are zero support paths/bodies and one plate object. Geometry and placement
are unchanged. Mark2's requested +0.04 mm trim emits +0.02 mm for Textured PEI.

Part cooling is 0% for layers 1–3 and 55% for model extrusion on layers 4–189; the auxiliary
fan stays off. Nozzle settings are 265°C first layer and 280°C thereafter, bed 80°C, with no
active chamber heat. [Native verification](verification.json).

Bambu Studio 02.08.02.61 reports no warnings, **2 h 40 m 16 s** and **54.60 g**.
The v13 estimate is 2 h 5 m 48 s; the additional estimated time is **34 m 28 s**.
Timelapse and bed leveling are On; flow and nozzle-offset calibration are Auto.
A fresh import and 20-second settling wait were accepted on the first send attempt.

Wall count belongs to the slicer's region settings, which height ranges and modifier
volumes can override. The band can therefore be confined to the required height on larger
parts, or a modifier can confine it spatially.
[Bambu Studio region options](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.hpp#L1063-L1147),
[height-range settings](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/slic3r/GUI/Tab.cpp#L4273-L4303).
