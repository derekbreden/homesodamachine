# Empty electronics access panel

This separate assembly study adds one removable roof panel above the dry
electronics bay to the complete [quadrant arrangement](../funnel-gate/README.md).
The panel carries no equipment, wires, tubes or fittings. The C14 inlet belongs
to back-top's rear wall; the Mean Well belongs to the cold core and back-bottom.
Their final connection is made through this opening before the empty panel is
installed. The remaining ceiling, wet group, funnel and frame stay assembled.

The panel is 100 × 126.55 × 9 mm, with R3 corners and 0.25 mm clearance around
its edge. Its only bearing surfaces are four integral bosses on the
fixed roof. Each has a full-height root extending 9 mm into the adjacent front
or rear fixed roof. The rear roots also fill the 9 mm rear-wall thickness.
The −X pair are 18 mm wide and connect into the sidewall. The +X pair have
matching full-depth 9 mm roots into the adjacent +X roof, giving each boss
two substantial attachments. Those blocks span 25 mm in X. Their inner ends
stop 4.5 mm from the screw axis to clear the vent adapter, with at least
2.5 mm of radial stock around the pilot. Screw centres and the 9 mm front/rear
roots follow the same symmetric pattern.
There is no perimeter rim. The bosses form a symmetric screw
pattern, 6.75 mm from each panel edge. A 6 × 2 mm notch through the panel's
front edge admits a flat screwdriver for lifting the panel.

Each corner uses an M3×12 socket screw and an RX-M3×5.7 heatset. The panel has
an Ø3.4 mm clearance hole and an Ø6.2 × 3.2 mm head counterbore. The head is
0.2 mm below the flush Z355 show face. The blind Ø4 × 7.5 mm pilot leaves
3 mm of stock beneath it; screw-tip reserve is 1.3 mm. The complete nominal
insert length engages the screw. Pilot size and radial stock follow the
[enclosure heatset reference](../../../printed-parts/enclosure/enclosure/heat-set-review/README.md).
Native screw and insert models show the socket, exterior and thread-root
envelopes; the heatset's knurl bands are illustrative.

The C14 flange centre is X−61.75, Y471.3, Z323, with its rear-wall pocket and
mounting holes at the same pose. Its scanned flange has approximately equal
11.9 mm gaps to the inner sidewall and ordinary ceiling underside. All other
equipment retains the parent layout and mounting ownership. The inlet's full
rectangular mounting opening lies below the rear boss roots.

[panel-plan.json](panel-plan.json) defines the geometry and empty equipment
attachment list. [geometry-report.json](geometry-report.json) records the five
valid native solids, screw stack, each boss's volume overlap with the fixed
roof and rear wall, and zero panel/fixed-roof volume overlap.
[arrangement-review.json](arrangement-review.json) records the targeted
equipment fit and sampled vertical lid removal. These are geometric fit
queries; this study contains no physical strength or lifetime qualification.

The whole-arrangement viewer retains the four quadrant colours and adds an
independent colour for the empty panel. Lift access panel illustrates the lid
and its four removed screws; the inserts and bosses remain fixed. Remove the
screws before lifting the lid. Highlight and lift changes preserve the camera.
The native half-section view shows one complete screw/insert/boss stack.
Mesh packing retains every vertex and triangle at the viewer's 0.02 mm
coordinate resolution.

Build the native parts through the shared CAD queue. The manual arrangement
query and two viewer commands read the selected scene without writing it:

```sh
PYTHONPATH=. tmp/takeover/cadq "Electronics access panel fasteners" -- tools/cad-venv/bin/python hardware/manifold-layout/studies/electronics-access/build.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/electronics-access/review.py
tools/cad-venv/bin/python hardware/manifold-layout/studies/electronics-access/viewer.py hardware/manifold-layout/studies/electronics-access/out/electronics-access.html
tools/cad-venv/bin/python hardware/manifold-layout/studies/electronics-access/viewer.py --detail hardware/manifold-layout/studies/electronics-access/out/fastener-section.html
```

Native STEP and frozen NPZ meshes are in [parts/](parts/). The four section
meshes are actual native solid intersections through a screw axis. Boss
overlays in the whole view show the complete bosses and their roof roots
opaquely; the same stock is fused into the fixed roof. Production enclosure
geometry is outside this isolated study.
