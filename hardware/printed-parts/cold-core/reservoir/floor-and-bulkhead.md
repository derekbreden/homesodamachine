# Reservoir floor + bulkhead port

The cavity floor is a Y-symmetric V swept across the full cavity X width: from each ±Y wall the floor slopes inward and down to a flat rectangular trough at y=0 that spans the full interior X width and hosts the bulkhead port. The floor is a single Y–Z section — slope down, flat, slope up — extruded straight across X; the only curved floor boundary is the cavity's existing centerward arc. The bulkhead — PureSec 1/4" RO push-to-connect 90° elbow bulkhead ([B0968K4JRN](https://www.amazon.com/dp/B0968K4JRN)), white PP, water/RO-rated — clamps vertically through the trough: its threaded barrel passes down through the trough floor and a locknut threads on from below in the bag-pocket cavity. The wet-side PTC port faces up into the cavity; the integral 90° elbow on the dry side turns the line laterally below the floor toward the bag-pocket +Y pass-through. A TPU face seal in a shallow counterbore on the wet-side trough floor seals the barrel-to-floor joint (the PureSec ships without a panel o-ring, so the printed TPU washer supplies it); the part wants a ⌀16 mm mounting hole.

The nut sits in a hex pocket below the floor in the bag-pocket cavity, reached from outside the reservoir during install (the bag pocket itself is open to the assembly side at this stage).

Syrup drains by gravity from anywhere in the cavity down the V to the central trough and into the bulkhead port. The lowest drainable line is the bulkhead's wet port axis; residual below that line stays in the bulkhead body itself.

## Open items

- [ ] The trough floor and walls are the reservoir's fluid barrier — the print has to hold syrup under working head with no weep. Tracked in [`print-log.md`](print-log.md).
- [ ] Whether the as-printed wetted surface stays clean under the software rinse cycle across repeated fills.
- [ ] Bulkhead port CAD tuned to the PureSec B0968K4JRN dimensions — ⌀16 mm hole, locknut, wet-side TPU-washer seat, below-floor elbow clearance — in `reservoir.py` / [`../_cold_core_interface.py`](../_cold_core_interface.py).
