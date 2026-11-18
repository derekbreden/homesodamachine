# Funnel-frame seating coupon

The front corner is cropped from the production frame. Its flange, vertical guide,
screw seat, lower foot and corbel keep their production shape and print direction.
The crop retains the complete production print height so the flange starts on the
same layer. Its project takes the frame's material, nozzle, plate, trim and supports.

Set the coupon in the front-top's right-hand funnel corner, with the screw opening
over the existing insert ledge. Compare the top with the enclosure roof and check
whether it seats with hand pressure after support removal.

The [full-frame seating observation](https://github.com/derekbreden/homesodamachine/blob/e4d1024ea/hardware/printed-parts/zone-c/funnel/prints/2026-11-16-textured-z004-mark2/physical-result/physical-result.json)
keeps Derek's photographs and report with the completed print.

The source runs through the Rust sandbox.

```sh
cp hardware/print-tests/funnel-frame-seating/coupon.rs tools/hsm/sandbox/examples/funnel_seating.rs
tools/run -- cargo run --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-sandbox --example funnel_seating -- hardware/print-tests/funnel-frame-seating/parts
tools/run -- tools/hsm/target/release/enclosure-print-prep funnel-frame-seating-coupon \
  --printer Mark2 --bed 'Textured PEI Plate' --slice --review
```
