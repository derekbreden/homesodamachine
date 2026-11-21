# Equipment mounting hardware

The Teyleten relays fasten directly to the west wall through their PCB corner
holes. Seat the ruthex RX-M2x4 inserts flush with the bearing faces before
placing each board. Fit the Sutemribor M2 × 6 socket-head screws with back-top
open and the relay terminals accessible. The [received-board record](../../../reference/teyleten-relay/mounting-fit.json)
identifies the hole size. The [mount datums](../enclosure/numbers/rear_wall.rs)
place the wall pilots and installed hardware from the same scanned holes.

[`equipment_clamps.rs`](equipment_clamps.rs) places the mounting hardware for the
main PCB, condenser, compressor and mains inlet. The PCB screws bear directly
on the mounting pads. Condenser screws bear through flat washers on the donor
flanges. The compressor posts retain their grommet shoulders and washer
bearing planes. [`hardware/fasteners.rs`](/hardware/fasteners.rs) owns those
screw lengths and regular insert bodies.
