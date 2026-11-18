# Rear alignment fit

The paired east-side coupons retain the approved alignment key, receiver, rail and
the real fore face of each rear enclosure half. The crop includes the complete entry
and closed end. Their source coordinates describe the seated assembly.

Generate the coupons from the current production models, then prepare the Mark1 plate.

```sh
tools/run -- cargo build --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-tooling --bin rear-alignment-fit
tools/run -- tools/hsm/target/release/rear-alignment-fit hardware/print-tests/rear-alignment-fit/inputs.json hardware/print-tests/rear-alignment-fit/parts
tools/run -- tools/hsm/target/release/enclosure-print-prep rear-alignment-fit --printer Mark1 --bed 'Textured PEI Plate' --slice --review
```

The upper coupon prints ceiling-down on its flat crop plane, carrying its rail caps.
The lower coupon prints floor-up with its rail trees rooted on the cavity floor.
Both crop planes preserve the production layer phase. The upper alignment groove
stays clear of supports, and its corbel grows from the flank wall.

Remove the rail supports before mating the coupons. Start the upper piece aft of the
lower piece, then slide it fore. Compare the real fore faces as the rounded key enters
the receiver and the closed end approaches its stop. Record sliding force, lateral
alignment and any witness marks with the print's photographs.
