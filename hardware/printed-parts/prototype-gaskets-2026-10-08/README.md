# Prototype gasket plates

Mark2 uses the loaded TPU 85A through the fixed right 0.6 mm nozzle and external
slot 255. Its requested +0.04 mm trim emits `G29.1 Z0.02` on Textured PEI.
Timelapse and bed leveling are on at Send; probing clump detection is off.

The separate [tube gasket](ready/2026-10-08-touch-flo-tube-gasket-tpu85a-right06-mark2.gcode.3mf)
uses the unchanged mesh and core process from
[the accepted Touch-Flo / 3/8 LLDPE fit project](../faucet/tpu-o-ring/tpu-o-ring-85A-6mm.3mf).
Its [May 30 fit record](../faucet/tpu-o-ring/print-log.md) establishes that combined
seat. The old print's physical nozzle diameter is not established. The native
[review](tube-native-review.json) records all 86 deposition heights and a
147.09 mm complete bead inset. The estimate is 11 minutes including startup.
[tube-launch.json](tube-launch.json) binds the single accepted transaction.

The [flat plate](ready/2026-10-08-prototype-flat-gaskets-tpu85a-right06-mark2.gcode.3mf)
contains two reservoir cap perimeter gaskets, two dry bulkhead washers, two vent
filter retaining rings, the machine display gasket, and one counter gasket for
the printed September 18 white Sculpted faucet. That counter gasket retains the
printed foot's openings and footprint through source revision `14594f74e`.
The reservoir perimeter gasket is symmetric in Y; flip one to fit the opposite
reservoir. The wet bulkhead washer is purchased silicone.

The flat plate retains [the saved solid TPU process](../gaskets.3mf): 225 °C,
35 °C bed, 2.2 mm³/s limit, 0.30 mm first layer, 0.18 mm normal layers,
0.62 mm width, two Arachne walls, 100% zig-zag, three top/bottom shells,
and no supports. The [native review](flat-native-review.json) records eight
complete models with a 36.21 mm complete bead inset and a 2 hour 5 minute
estimate. The current native slicer disables layer-change retraction for TPU;
the retained temperature, flow, geometry and core recipe are recorded separately.
The [flat launch receipt](flat-launch.json) binds the accepted eight-part job.
Its [preflight](flat-preflight.json) records the clear bed, fresh readings of
both printers, right external TPU mapping and shared-circuit startup spacing.

The 283 × 181 mm foam-cap gasket is outside this plate. Its complete footprint
exceeds Mark2's required 20 mm usable-bed inset even before brim. Its source
binding is retained in [flat-source-binding.json](flat-source-binding.json).

These records qualify preparation, native deposition and the source dimensions.
Physical seal performance for this print remains a separate observation.
