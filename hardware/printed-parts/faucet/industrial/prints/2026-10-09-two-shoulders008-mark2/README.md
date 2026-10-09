# Industrial faucet with fine shoulder layers

This complete PET-GF plate contains the industrial shell base, shared shell tip,
industrial display cover and industrial above-counter plate. The base retains its
−15° X print rotation. Only the base receives 0.08 mm layers in the two bands
crossing the selected annular shoulders; normal layers are 0.24 mm and the bed
layer is 0.20 mm on every object.

| Selected CAD face | Complete face span in print Z | Base fine band in print Z |
| --- | --- | --- |
| Z14.0 mm, normal +Z | 13.87165–28.79329 mm | 13.40–29.00 mm |
| Z57.5 mm, normal +Z | 55.46309–67.83949 mm | 55.16–68.12 mm |

The bands cover the whole base cross-section at those heights, with a short guard
at each boundary so a coarse layer cannot cross a selected face. The other three
objects retain 0.24 mm layers throughout above their first bed layer.

The native estimate is 6 hours 2 minutes. The loaded PET-GF maps to the printer's
PET-CF left external slot 254 and fixed left hardened standard-flow 0.4 mm nozzle,
on Textured PEI. Mark2's requested +0.04 mm Z trim emits +0.02 mm. The existing
265/280°C nozzle temperatures, 80°C bed, two walls, 15% grid infill, tree supports
and three local six-wall solid insert-host modifiers are retained. Nozzle Clumping
Detection by Probing is disabled. The foreground Send options use Timelapse On,
Auto bed leveling On, Flow dynamic calibration Auto and Nozzle Offset Calibration
Auto.

[Preparation](preparation.json) binds the selected STEP faces, screenshot source,
source STL hashes, placement and project. [Native checks](native-check.json)
record the actual wall layers, mesh and placement retention, support stock near
the selected faces and the complete model/support/brim bed margin of 25.15 mm.
The shoulder spans have continuous 0.08 mm coverage. No sampled support midpoint
projects into either selected face's interior inset by 0.4 mm; the upper face's
near-boundary witnesses are in the internal lever opening below its plane.
These are commanded-path readings; surface finish remains a physical observation.

[Launch](launch.json) and [preflight](preflight.json) bind the single authorized
foreground transaction and its acceptance to the native archive.

Mark2 accepted task/job `1322263030` at 2026-10-09 00:18:36 CDT
(05:18:36 UTC) through one foreground Send. Native completion is forecast near
06:20 CDT. The acceptance was observed in PREPARE with print error 0 and no HMS
faults. Timelapse On was verified in the Send dialog; capture is not established
by that option alone.
