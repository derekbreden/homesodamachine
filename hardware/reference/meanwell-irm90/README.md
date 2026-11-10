# Mean Well IRM-90-12ST reference

The appliance's encapsulated screw-terminal supply mounts beneath the
[electronics-bay ceiling](/hardware/assembly/electronics-bay.md). Its mounting
base faces the roof, AC enters at the aft end, and DC leaves toward the front.
The integral ceiling hosts carry the supply independently of the cold-core lid.

`meanwell_irm90.rs` cuts a clean exterior from
[`replica-parameters.json`](replica-parameters.json). The
[manufacturer's mechanical drawing](https://www.meanwell.com/Upload/PDF/IRM-90/IRM-90-spec.pdf)
owns the nominal envelope, mounting-hole pattern and mounting-ear height. The
[manufacturer's CAD archive](https://www.meanwell.com/upload/pdf/IRM-90/IRM-90-3D.zip)
supplies the contact outline, case draft, broad top shoulders, terminal profiles,
screw stations and wire-entry mouths. The parameters retain the source hashes,
selected exterior bodies and coordinate transform.

The model retains the broad straight sides, diagonal end transitions, rounded
mounting ears, terminal clearances and sloping insulating guards. The case is
filled. Hidden electronics, internal case ribs, lettering, screw-drive detail and
small terminal interlocks are omitted. The broad top is flat, with ideal
cylindrical shoulders around it.

The frame centers the footprint on the mounting plane: X spans the width, Y the
length and positive Z rises into the module. The AC terminal row lies toward
positive Y. `ac_in()` and `dc_out()` expose the actual screw-access rows;
`wire_entry()` exposes the separate outward-facing wire-mouth rows. These
helpers read the same parameters as the Rust geometry. In the appliance, the
screw-access axes point downward.

Generate the reference through the shared run wrapper:

```sh
python3 tools/run.py -- cargo run --release --locked -j2 \
    --manifest-path tools/hsm/Cargo.toml -p hsm-sandbox \
    --example meanwell-irm90-replica -- hardware/reference/meanwell-irm90
```

The [assembly-fit review](../../printed-parts/enclosure/enclosure/assembly-fit-review/README.md)
records the module placement and installed-wire fit scope. The
[conditional electrical Plan B](/future/carbonation-plan-b.md) depends on
measured current and voltage under the intended load schedule.
