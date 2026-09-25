# Display-cover snap fit trial — Mark2

Printing on Mark2 since 2026-09-25 17:50 UTC, task 1282164977, with no startup errors. One complete display cover with each retaining skirt **1.2 mm inward** from the original receiver datum, another 0.3 mm inward from the preceding 0.9 mm trial. The outer bezel, window, complete skirt shape and fixed housing receivers retain their geometry.

The centered catch overlap is **0.3 mm per hook**. At the full 0.3 mm lateral float, one hook has zero overlap and the opposite hook has 0.6 mm. Both catch when centered; a straight outward pull is caught at either lateral limit by the remaining hook. Resistance to peeling or repeated use has not been established. The physical trial checks bowing and retention together.

Black PET-GF on the left 0.4 mm nozzle, 0.24 mm layers, 0.20 mm first layer, two walls, original wall order and speeds, 15% overlap, automatic brim, and Mark2 +0.04 mm requested Z trim.

Native estimate: **24 min 8 sec** including startup, **8.69 g** at the saved profile density.

The [geometry check](geometry-check.json) measures each skirt's exact 0.30 mm translation, verifies the unchanged bezel and fixed housing, and records each hook's catch contact at centered and full lateral positions. The [actual toolpath comparison](actual-toolpath-comparison.json) confirms the same movement in emitted wall paths and identical native print settings.

The [native verification](verification.json) covers all 56 model wall layers, source hashes, archive checksum, material mapping and bed bounds. The [support review](support-removal-review.json) covers both removable bed-rooted trees beneath the flat catch faces. The [manifest](manifest.json) binds the native archive and these readings.

![Complete display cover](preview.png)

The [launch receipt](launch.json) identifies the accepted archive and printer task. Post-publication geometry lint reports zero open findings and six intentional faces answered at their new coordinates.
