# Equipment clamps

The relay end clamps retain the boards on back-top's wall posts. Integral pins
locate their existing corner holes. Each clamp bears across a board end and
fastens beside the board into a regular heat-set insert. Its low bridge leaves
the native wire entries open; the raised head land carries the screw on the
wall-rooted host. The mounting datums live in
[`rear_wall.rs`](../enclosure/numbers/rear_wall.rs).

The screw spacers bear on the condenser mounting flanges and on the main PCB.
The PCB sleeves follow the screw-head footprint to clear adjacent components.
Their thickness lets the common screw stock reach the regular inserts without approaching the
exterior floor or the lid's underside. The PCB and tubing retain their placement. The compressor posts retain their
grommet shoulders and washer bearing planes, with deeper blind relief for the selected screws.

[`equipment_clamps.rs`](equipment_clamps.rs) writes the printable parts and their
installed models, including the compressor, condenser and mains-inlet hardware.
[`hardware/fasteners.rs`](/hardware/fasteners.rs) owns the selected screw lengths
and insert bodies.

Print the clamps and spacers flat in PET-GF with solid deposition and no supports.
The clamp's flat bearing side goes on the bed. Fit the boards over their locating
pins with back-top open on the bench, fit the end clamps, and seat the screws by
hand. Install spacers between the condenser flanges and screw heads, and between
the main PCB and its screw heads.
The revised printed interfaces require a bench fit before physical acceptance.
