# V-H entry clip on the pump bulkhead

This coupon comes from the front-top quadrant’s production STL. It keeps the
sloping shelf, the bulkhead behind it and the entire split seat. A flat foot
below the shelf keeps the wall upright on the bed and on the bench. The jaws
print in the quadrant’s orientation and at the same layer heights. The coupon
uses the small-part bed trim and a cooling tower for the short courses.

Press the black reservoir draw tube down into the saddle one wing pair at a
time. Let go and check that the tube rests in the groove through the turn.
Lift one end to release it and look at the split and the wing roots as the
jaws spring back. On the machine this is done through the opening with the
funnel frame out.

The [geometry record](parts/geometry.json) identifies the quadrant mesh.
The [Mark 1 job](prints/2026-11-21-mark1/print-job.json) identifies the
physical print. Its [slice detail](prints/2026-11-21-mark1/wing-courses.png)
shows the final courses on the wings.

To prepare the coupon from the current production mesh, run

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin vh-entry-clip-coupon
tools/run -- tools/hsm/target/release/enclosure-print-prep vh-entry-clip \
  --printer Mark1 --slice --review
```
