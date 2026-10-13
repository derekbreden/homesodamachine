# Complete Industrial faucet with default corner seams — Mark2, 2026-10-13

The five-part Industrial faucet uses A2 on the base, tip and above-counter plate:
Aligned, a 60 mm scarf with 0% scarf gap, and 150% seam gap. The display cover and
lever inherit the shared petgf.3mf seam defaults: Aligned, 15% seam gap and scarf off.
Wipe is off. The source geometry, placements, eight coarse lip layers, 0.12 mm bands,
and infill-only foot match the reviewed complete faucet.

[The native trace](corner-seam-review.json) places the cover's 80 main-contour starts
in approximately 90° corners. The lever's 52 main-contour starts lie at channel and
ledge transitions, at approximately 86–140° turns, rather than along its long show
face. Both parts have no lowered outer-wall scarf moves and a 0.06 mm ordinary seam
gap. These measurements describe commanded paths; physical seam visibility is
unassessed. The [map](corner-seams.png) marks actual starts on all closed outer-wall
contours, including smaller window and channel contours.

Mark2 accepted task **1334704608** after one Send click. Native estimate:
**5 h 59 min 39 s**, **161.35 g**. Timelapse and bed leveling are on; flow and nozzle
calibration are automatic. [launch.json](launch.json) binds the hashes, settings,
source geometry and startup spacing. The working recipe is unchanged.

Derek reports that the base and tip seams did not follow the expected continuous
rear line. His reference is complete-faucet task **1329852853**, whose base and
tip object overrides use **Seam position: Back**; this trial uses **Aligned**.
This is placement feedback, without a scarf-finish or complete-faucet acceptance.
