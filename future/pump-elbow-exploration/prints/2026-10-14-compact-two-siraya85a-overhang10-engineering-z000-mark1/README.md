# Two elbows — Siraya Tech Flex TPU 85A Clear

Mark1 accepted task **1337964351** on **2026-10-14 at 01:59:43 CDT**.
The [launch receipt](launch.json) reports PREPARE, two objects and no errors.
Native estimate: **114 minutes / 7.83 g**. The
[physical result](physical-result.json) is pending.

Both objects duplicate the exact native mesh of the
[accepted single article](../2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/physical-result.json)
and retain its orientation. Derek reports that article as perfect, then
separately reports internal stringing. Its exterior acceptance and the earlier
Bambu article's manual-fit acceptance retain their separate scopes.

The material remains Siraya Tech Flex TPU 85A Clear, right fixed **0.6 mm**
nozzle, **215°C normal / 225°C first layer**, **35°C glued Engineering Plate**,
**zero user Z trim**, **0.12 mm normal / 0.20 mm first layers**, **0.96 flow**,
**2.2 mm³/s cap**, **0.8 mm retraction**, full part cooling and auxiliary off.
Six requested walls, 100% zigzag infill, inner/outer wall order, 5 mm outer
brim and supports off are retained. Only the seam position, wall-crossing
avoidance and process label differ from the accepted single's native settings.

The selected routing uses **Nearest seams** and **Avoid crossing wall**.
Object centres are (177.5,148.5) and (177.5,171.5) mm. The
[emitted-command review](emitted-command-review.json) finds **2.708 mm**
between the complete model/brim bead envelopes and **135.695 mm** minimum
inset within the right nozzle's usable bed area. It verifies both exterior
extremes at **10 mm/s on layers 17–33** and all normal-layer moves labelled
Outer wall at 10 mm/s. Each object retains one negligible separately labelled
Overhang wall move on layer 68 at 25 mm/s, E0.00004.

The [manual travel review](travel-review.json) covers all **367 inter-object
transfers over 184 layers**. At layer 28, the same-layer arrival is on the
gap-facing side of the front object, with a 23.09 mm route and 3.61 mm terminal
XY approach above planned solid stock. Nearest does not force every seam to
face the gap. Thin upper rims have shorter approaches. The 0.4 mm Z-hop and
the subsequent extrusion direction mean stock coverage alone cannot establish
that a string contacts the wall or becomes buried.

The linked [liner wall-start record](../../../../hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-12-liners-d775-mark1/wall-start-observation.json)
preserves the intermittent strand appearing when the nozzle arrives and starts
a wall. Derek identifies the second-object end on layer N to first-object
start on layer N+1 as the transition of concern. The current slice has both
same-layer transfers and next-layer returns. Standing **Timelapse On** adds
firmware movement through a photo-safe position; its departure is not expanded
into ordinary G-code moves. The review accounts for the visible return from
that position. This is a routing trial, without demonstrated string reduction
or an established cause of the earlier restart defect. Strings across an open
passage remain a quality issue even if the exterior is clean.

- [Editable project](2026-10-14-compact-two-elbows-siraya85a-overhang10-engineering-right06-z000-mark1.3mf)
- [Native sliced archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-14-compact-two-siraya85a-overhang10-engineering-z000-mark1/2026-10-14-compact-two-elbows-siraya85a-overhang10-engineering-right06-z000-mark1.gcode.3mf)
- [Native readback and exact recipe differences](native-readback.json)
- [Manual preparation script](prepare_mark1.py)
- [Startup spacing](startup-spacing.json)

The preparation script slices offline. Submission uses the standard sender,
Timelapse On, Bed Leveling On, Flow Calibration Auto and Nozzle Offset Auto.
No global printer preset is changed.
