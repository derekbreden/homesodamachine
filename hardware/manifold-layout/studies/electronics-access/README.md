# Empty electronics access panel

This separate assembly study adds one removable roof panel above the dry
electronics bay to the complete [quadrant arrangement](../funnel-gate/README.md).
The panel carries no equipment, wires, tubes or fittings. All existing
equipment keeps its pose and its mounting-parent assignment.

The C14 inlet remains on back-top's rear wall. The Mean Well remains on the
cold core, carried by back-bottom. Their final connection is made through this
opening before the empty panel is installed. The remaining ceiling, wet group,
funnel and frame stay assembled during that operation.

The plain panel is 100 × 126.55 × 9 mm, with R3 corners and 0.25 mm clearance
around its edge. A 6 mm bearing ledge belongs to the fixed ceiling and sits
below its ordinary underside. The closed panel is flush at Z355. Its illustrated
70 mm vertical lift moves only the panel. Retention hardware is outside this
access study; no fastener or equipment mount is implied on the panel.

[panel-plan.json](panel-plan.json) records the geometry and the empty attachment
list. [geometry-report.json](geometry-report.json) records two valid native
solids, zero closed overlap and clear sampled vertical removal against the
fixed ceiling. [arrangement-review.json](arrangement-review.json) records the
new parts and sampled lid lift against the complete stationary equipment.
Neither the panel nor its fixed perimeter seat intersects equipment. The seat
has 1.94 mm nominal vertical clearance above the C14 body's crown.

The whole-arrangement viewer retains the four quadrant colours and adds an
independent colour for the empty panel. The Lift access panel checkbox moves
only that panel. Highlight changes and panel movement preserve the camera.
Latest changes identifies the roof opening and its lid. The fixed roof and
walls are translucent so the retained equipment is visible.

Build the two study parts through the shared CAD queue, then generate the
inline viewer fragment without rebuilding or writing the parent scene:

```sh
PYTHONPATH=. tmp/takeover/cadq "Empty electronics access panel" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/electronics-access/build.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/electronics-access/viewer.py hardware/manifold-layout/studies/electronics-access/out/electronics-access.html
```

Native STEP and frozen NPZ meshes are in [parts/](parts/). This is an isolated
access concept; the production enclosure geometry is not changed by the study.
