# Equipment clamps

The Teyleten relay PCB holes take M2 mounting screws. The
[received-board record](../../../reference/teyleten-relay/mounting-fit.json)
identifies that constraint. Integral printed pins locate those holes in the
installed mount. End clamps retain the board by fastening into separate wall
hosts outside the PCB; their screws pass through the printed clamps only.

The clamp's low bridge leaves the native wire entries open. Its raised head
land carries the screw on the wall-rooted host. The mounting datums live in
[`rear_wall.rs`](../enclosure/numbers/rear_wall.rs).

[`equipment_clamps.rs`](equipment_clamps.rs) writes the printable relay clamp and
installed equipment hardware. The PCB screws bear directly on the mounting
pads. Condenser screws bear through the selected flat washers on the donor
flanges. The compressor posts retain their grommet shoulders and washer
bearing planes. [`hardware/fasteners.rs`](/hardware/fasteners.rs)
owns the selected screw lengths and regular insert bodies.

Print the clamp flat in PET-GF with solid deposition and no supports. Its flat
bearing side goes on the bed. Fit each board over its locating pins with back-top
open on the bench, fit the end clamps, and seat their screws by hand. The
printed relay interfaces require a bench fit before physical acceptance.
