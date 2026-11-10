# Inclined support release

These prepared plates compare contact distance and roof spacing after the
[faucet lower-curve failure](../D-representative-mark2/physical-result.json).
Broken stems with contact material retained on the part count as a failed
release. The flat rail result does not qualify these surfaces.

Each coupon has a single anchoring wall and open remaining edges. A bed tab
carries its identifier; it does not anchor the roof's free edges. The underside
rises from the wall, exposing the first supported model courses to peeling.
The [matrix](matrix.json) owns the dimensions, angles and requested settings.
Angles are measured from the horizontal bed. Native support targets cover the
inclined underside so a nominally self-supporting slope still tests contact.

| Plate | Comparison | Files |
| --- | --- | --- |
| Gap | Solid roofs with different requested contact distances at matching inclines. | [Editable project](plates/inclines-gap/inclines-gap.3mf), [native machine archive](plates/inclines-gap/inclines-gap.gcode.3mf), [preparation and estimate](plates/inclines-gap/preparation.json) |
| Density | Different roof spacings at a common contact distance and matching inclines. The matching gap-plate row supplies the solid-roof comparison. | [Editable project](plates/inclines-density/inclines-density.3mf), [native machine archive](plates/inclines-density/inclines-density.gcode.3mf), [preparation and estimate](plates/inclines-density/preparation.json) |

The shared D bridge flow, bridge speed and localized cooling remain common.
Tree style, branch geometry and side clearance remain common across the
coupons. These comparisons test release and underside quality together;
easier removal alone does not establish a useful support recipe.

The [verification](verification.json) binds the geometry, material, calibration,
native slice and emitted support paths. The gap pairs have distinct interface
planes. The spacing pairs have distinct interface coverage. Requested values
remain slicer inputs, rather than measured physical clearances. Each archive
uses Mark2's calibration; a Mark1 preparation uses Mark1's own trim.

Both plates are prepared and unprinted. Start with the gap plate, then compare
roof spacing where a promising release/finish balance appears. Record whether
the mat releases, stems break, contact material remains, or a model course
peels away. Photograph the underside and removed mat together. A promising
planar condition next needs the actual faucet lower curve in its production
pose before it qualifies a complete faucet print.

The [support-material documentation](https://help.prusa3d.com/article/support-material_1698)
describes contact distance and roof spacing as removal/finish tradeoffs.
The installed slicer's [tree implementation](https://raw.githubusercontent.com/bambulab/BambuStudio/v02.08.02.61/src/libslic3r/Support/TreeSupport.cpp)
schedules discrete support courses. Its
[tree settings](https://raw.githubusercontent.com/bambulab/BambuStudio/v02.08.02.61/src/libslic3r/Support/TreeSupportCommon.hpp)
keep vertical and lateral clearance separate. Reduced clearance normal to a
slope is a geometric hypothesis; the photographs do not establish it as the
cause of the retained faucet contact material.

The [geometry source](samples.rs) runs as the `support-inclines` sandbox example.
The [plate preparer](prepare.rs) runs as the `incline-support-plates` binary in
`hsm-print-prep`, taking a run directory and optional `--slice`. Run either
through `tools/run` with the shared Cargo manifest. Neither contacts a printer.
