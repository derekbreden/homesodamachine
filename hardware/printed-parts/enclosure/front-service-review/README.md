# Front display mounting and pump wall review

The display bezel, its shallow visible-head seats and the matching blind insert
pilots belong to the production enclosure. The flat gasket spreads light clamp
pressure along the glass border. The cover and receiver share the
[display mount source](../enclosure/numbers/display_mount.rs) and
[mount dimensions](../display-cover/mount-dimensions.json).

The pump wall has closed tube bores. Flexible pump stubs pass through them during
loading. The fitted pump seats and retainer retain their approved geometry.

The pump space view is a layout study. Orange marks the span between the rigid
pump flange and the current wall, including existing retainer stock. Blue marks a
possible wall plane. Moving the wall requires a coordinated retainer, tee-stack
and valve-support revision. The production wall stays in its current position.

`review.py` reads the production meshes and writes the assembled, separated and
full-context GLBs under `hardware/assembly/scenes/glb`. It also writes the manual
clearance and backing readings in [review.json](review.json). Run it through
`tools/run.py` with the CAD virtual environment. It starts no printer.

[Manufacturing readings](manufacturing-review.json) bind the native slices to
the revised meshes and print recipes. The front-top cavity supports use Tree
Slim; the flat bezel prints without supports.
