# V-B return tube clip

This coupon is a crop of the production cold-core lid. It carries the whole
curved seat, both pairs of wings and the lid underneath. It prints on the lid's
flat bed face with the same local solid infill through the wings and their roots.
The [geometry record](parts/geometry.json) identifies the lid export the coupon
comes from. The [Mark 1 print record](prints/2026-11-21-mark1/print-job.json)
identifies the plate sent to the printer.

Use an offcut of the black return tubing. Lay it along the curve and press it
into one pair of wings at a time. Let go and see whether the tube stays round
and seated all the way through the turn. Lift it out one half at a time and
check whether the wings spring back.

To crop the current lid and prepare the test plate locally, run

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin vb-return-clip-coupon
tools/run -- tools/hsm/target/release/enclosure-print-prep vb-return-clip \
  --printer Mark1 --slice --review
```
