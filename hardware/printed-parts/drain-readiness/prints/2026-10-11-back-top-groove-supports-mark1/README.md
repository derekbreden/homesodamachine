# Back-top next-print preparation — Mark1

The 23 complete insert-host, cap, seam and rail-root modifiers use **100% zig-zag infill** and inherit the ordinary wall settings. The original modifier volumes, source STL, mating geometry, pose and layer schedule are retained. The ordinary process uses two walls; the existing six-wall additive roof transition is a layer band.

The [native box-face reading](box-face-wall-review.json) checks all 17,890 qualifying outer-wall segments and finds **0 mm of artificial outer wall through material** at modifier faces. The [three wall sections](wall-path-comparison.png) show the interior and exterior paths through the reported electronics hosts. The [source reading](source-review.json) binds the unchanged product vertices, triangle indices and all 23 original modifier meshes. This is a preparation for a physical print trial; surface finish and support release are unassessed.

The native estimate is **25 h 5 min**, with 825.9 g at the saved profile density. The full model/support/brim bead envelope, including its own half-width and 0.1 mm padding, retains **20.12 mm** of usable-bed margin. Black PET-GF uses Mark1's left standard hardened 0.4 mm nozzle, Textured PEI, normal +0.18 mm requested/+0.16 mm emitted trim, 0.20 mm first layer and 0.24 mm ordinary layers. The historical **50 mm bridge limit** remains.

## Sliding-groove support exception

Three named disposable project-only ribbons support the fore-left, fore-right and aft sliding-catch roofs within their own grooves. Derek reports easy release of small local groove support on the other enclosure quadrants. These particular ribbons have no physical removal result. Each is 4.45 mm wide and 5.52 mm tall, inset 0.40 mm from the foot edges, with two normal walls; the overlapping solid-root regions fill its interior.

Only the six downward triangles of these three catch roofs suppress automatic support in favor of the ribbons. All ribbon faces suppress their own automatic support. Their native layers run from Z180.44 to Z185.72, with **0.24 mm below and 0.48 mm above**. The [ribbon reading](groove-ribbon-review.json) finds no automatic support inside them. The [large-contact reading](large-overhang-support-review.json) finds ribbon contact in the six original catch slabs and retains automatic interface contact in the other two large slabs.

Other overhangs use Bambu **Tree (auto), Default style**, 45° branch angle, 3 mm branch diameter and the existing 0.5° diameter growth for this footprint. The [23 tie-floor windows](tie-cavity-support-review.json) have no support bead crossings. All 256,175 automatic support roads clear the nine protected show faces in the [show-face reading](show-support-clearance-summary.json). The flat rear port retains its separately recorded scope.

## Deposition and print state

The [sampled host/root deposition](dense-region-review.json) records nominal own-width bead envelopes, including bridge and boundary slabs. Its 98% diagnostic threshold is not a load-capacity criterion; the minimum sampled envelope coverage is 77.6%. The modifier target is 100% infill. Actual material density, insert retention and strength are unmeasured.

The [reported article and photograph](../2026-10-10-current-back-top-bridge50-mark1/physical-result.json) retain the failed cleanup and both-face wall-track observations. The [launch plan](launch-plan.json) records **zero imports and zero Send clicks** for this preparation. Mark1 is reserved for the separately authorized Insert tool print. No monitor, automatic next print or resume is scheduled.
