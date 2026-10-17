# White Sculpted faucet display cover — Mark2

One current faucet display cover, printed on Mark2's right hardened standard-flow
0.4 mm hotend from white PET-GF in external slot 255. The printer identifies
PET-GF as PET-CF. [Launch](launch.json) binds the accepted file.

The unchanged current STL matches the cover embedded in the
[complete white Sculpted faucet](../../../sculpted/prints/2026-10-15-white-right-mark2/README.md).
It retains its −50° CAD X pose, automatic Tree/Default supports,
0.20 mm first bed layer and 0.24 mm nominal layers thereafter.
Its finish is Aligned/15% seam gap with scarf and wipe off.
Cooling, speed, bridge flow and all other material/process settings retain
the complete set's cover recipe. This single part is centered on the bed.

Mark2 retains +0.04 mm requested Z trim, emitting +0.02 mm on Textured PEI,
and its recorded right-nozzle XY registration. Timelapse and bed leveling
are On; flow dynamic and nozzle offset calibration are Auto.

The [native review](native-review.json) records one object, 77 layers,
24 min 42 s and 6.64 g using the saved profile density. Model, support and brim
beads retain 131.63 mm minimum clearance to the right nozzle's usable area.
[Packaging](packaging.json) retains byte-identical G-code in the print-only copy.
The [reported physical result](../2026-10-17-cooling-off-prepared-mark2/reported-failure.json)
rejects this cover for assembly: it breaks under the small spreading motion
needed to load the display. The initiating cause is unestablished.

The printer accepted this job as task **1345901173**.
The [startup observation](startup.json) reports the correct 77-layer
job running with no print error or HMS.
