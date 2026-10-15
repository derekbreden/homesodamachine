# Bottom enclosure print packages

The current bottom pieces have integral printed handholds. Their lifting ceilings and
inner corner returns retain the saved automatic Tree/Default support decisions.
The exterior R6 transition uses the additive 0.24 mm treatment with six local walls and
its existing show-surface support exclusion. The first layer is 0.20 mm.

`prepare.py` builds a fresh immutable project from the production bottom STL and invokes
Bambu Studio's slicer. `verify.py` reads the exact archive, source hashes, layer/wall bands,
bead overlap, exterior support clearance and plate margins. Preparation does not establish
support cleanup, finger comfort or load capacity. The current integral handholds have no
physical acceptance for those properties.

The stored [H2C](h2c/preflight.json) and [Mark2](mark2/preflight.json) reviews and their
launch receipts bind the receiver-cut geometry identified in each record. Their grip-wing
support exclusions and bridge checks apply only to those source meshes. The
[receiver/cover coupon result](../grip-cover/physical-acceptance.json) retains its scope.

The shared [`petgf.3mf`](../../petgf.3mf) supplies temperatures, speeds, wall order,
15% infill overlap and automatic tree supports. The production layer bands and complete
insert-host modifiers are described in the
[enclosure layer policy](../enclosure/layer-policy-correction/README.md).
A fresh native slice identifies the current mesh and its actual support contacts.

Current launches use the saved printer-specific trim and material mapping. Starts and
resumes on the two printers observe the shared-circuit startup spacing in
[printer guidance](../../../../tools/bambu-printers.md#shared-circuit-startup-spacing).
