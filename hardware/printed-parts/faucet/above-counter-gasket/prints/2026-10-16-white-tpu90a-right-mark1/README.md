# White Sculpted above-counter mounting gasket — Mark1

One current above-counter gasket for the white Sculpted faucet, using Mark1's
fixed right hardened standard-flow 0.6 mm hotend and white TPU 90A in external
slot 255. Bambu Connect's Hotends Info identifies that right hotend directly.
The printer's material field reports TPU; hardness comes from the user's
loading report. [Launch](launch.json) binds the accepted file.

The current [gasket STL](../../above-counter-gasket.stl) supplies the shape.
It prints flat, centered on the bed, using the material and solid-seal process
from the [saved white TPU 90A preparation](../../../../prototype-gaskets-2026-10-08/white90-faucet/README.md).
The model geometry is unchanged.

The process retains 225°C nozzle, 35°C engineering plate, 2.8 mm³/s flow
limit, 100% cooling, 0.30 mm first layer, 0.18 mm ordinary layers, 0.62 mm
nominal line width, two Arachne walls, 100% zig-zag and three top/bottom
shells. No supports are enabled. Mark1 uses its normal +0.18 mm requested
trim, emitted as +0.18 mm on the engineering plate. The material is assigned
manually to the right hotend at project and plate scope.

Timelapse and bed leveling are On; flow dynamic and nozzle offset calibration
are Auto. [Native review](native-review.json) records one object, ten layers,
34 min 24 s and 5.77 g using the saved profile density. The complete bead
footprint retains 123.39 mm minimum usable-bed clearance.
[Packaging](packaging.json) retains byte-identical G-code in the print-only copy.
Physical fit and sealing performance remain pending.

The printer accepted this job as task **1345913800**.
The [startup observation](startup.json) reports the correct 10-layer
job running with no print error or HMS.
