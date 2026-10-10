# Complete industrial faucet with fine shoulder layers

This is the complete physical reference for the
[queued 0.12 mm shoulder recipe](../2026-10-09-shoulders012-solid-foot-mark2/README.md).
Derek accepts variable layer height as the shipping compromise. Further
whole-faucet 0.08 mm iteration and research are deferred; this reference's
screw-point surface issue remains recorded below.

This single PET-GF plate contains all five rigid printed parts: industrial shell
base, shared shell tip, industrial display cover, industrial above-counter plate
and the accepted lever replica. The lever's side-down STL matches the geometry
identified in its [physical acceptance record](../../../lever-replica/physical-acceptance.json).
That record establishes fit and functional operation for the identified white
PET-GF article; the current plate uses the loaded black PET-GF.

The base retains its −15° X print rotation. Only the base receives 0.08 mm layers
in the bands crossing the two selected annular shoulder faces. Every object uses
a 0.20 mm first bed layer; the tip, cover, counter plate and lever use 0.24 mm
layers above that first layer. The base uses 0.24 mm elsewhere.

| Selected CAD face | Complete face span in print Z | Base fine band in print Z |
| --- | --- | --- |
| Z14.0 mm, normal +Z | 13.87165–28.79329 mm | 13.40–29.00 mm |
| Z57.5 mm, normal +Z | 55.46309–67.83949 mm | 55.16–68.12 mm |

The fine bands apply to the whole base cross-section at those heights, with a
short guard at each boundary. The native wall paths verify continuous 0.08 mm
coverage through both selected faces. All five native meshes match the prepared
project. The lever retains its accepted side-down orientation, with its broad
show face vertical.

The native estimate is 6 hours 13 minutes. The loaded material maps to PET-CF
external left slot 254 and the fixed left hardened standard-flow 0.4 mm nozzle
on Textured PEI. Mark2's normal requested +0.04 mm Z trim emits +0.02 mm. The
265/280°C nozzle temperatures, 80°C bed, two walls, 15% grid infill, tree supports
and three local six-wall solid base insert-host modifiers are retained. Nozzle
Clumping Detection by Probing is disabled. Foreground Send options are Timelapse
On, Auto bed leveling On, Flow dynamic calibration Auto and Nozzle Offset
Calibration Auto.

[Preparation](preparation.json) binds the selected faces, all source mesh hashes,
placement, settings and accepted lever geometry. [Native checks](native-check.json)
bind the actual wall layers, exact five-object inventory and commanded paths.
The complete model/support/brim envelope retains a 25.15 mm minimum bed margin.
The lever's conservative complete bead rectangle is separated from the base's
by 13.46 mm and from the counter plate's by 18.87 mm. No sampled support midpoint
projects into either selected face's interior inset by 0.4 mm. These are native
commanded-path observations; surface finish remains a physical observation.

[Launch](launch.json) and [preflight](preflight.json) bind the single foreground
transaction to the reviewed archive and fresh readings of both printers.

Mark2 accepted task/job `1322285082` at 2026-10-09 00:33:43 CDT
(05:33:43 UTC) through one foreground Send. The acceptance
reading is RUNNING at layer 0, with print error 0 and no HMS faults. Native
completion is forecast near 06:46 CDT. Timelapse On was verified in the Send
dialog; that option alone does not establish captured frames.

The [physical result](physical-result/physical-result.json) records the user's
beautiful 0.08 mm layers and successful removal of supports from the few thin
supported layers. Exterior lines/defects beside each screw point remain an open
finish issue. The [native screw-point comparison and all-fine time estimate](../2026-10-09-all008-estimate-mark2/README.md)
locate repeated outer-wall starts and stops at the rectangular insert-host
reinforcement boundaries.

The [complete 0.08 mm correction plate](../2026-10-09-all008-solid-foot-mark2/README.md)
uses one six-wall solid foot region and Arachne widths on the base. Its native
paths remove the repeated screw-region starts/stops and pass all three insert
backing reviews. Physical exterior finish on that article remains unevaluated.
