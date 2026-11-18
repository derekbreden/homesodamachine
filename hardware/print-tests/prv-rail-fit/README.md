# PRV rail fit

The paired coupons retain the west sliding rail and complete PRV chase from the
production back-top and back-bottom. Their source coordinates describe their seated
position. The upper crop prints ceiling-down and the lower crop prints floor-up, with
their cropped bases on the production layer phase.

Generate the current coupons from their declared production models.

```sh
tools/run -- cargo build --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-tooling --bin prv-rail-fit
tools/run -- tools/hsm/target/release/prv-rail-fit hardware/print-tests/prv-rail-fit/inputs.json hardware/print-tests/prv-rail-fit/parts
tools/run -- tools/hsm/target/release/enclosure-print-prep prv-rail-fit --printer Mark1 --bed 'Textured PEI Plate' --slice --review
```

The upper crop carries the production rail caps, including the vent-adjacent bearing
and its open edge. The lower crop uses cavity-floor trees. Its blocker follows the
actual open vent passage so the rail bearings beside that passage receive support.
The shared PET-GF recipe supplies the interface treatment and localized cooling.

After removing the supports, slide the upper crop onto the lower crop. The test
exposes both vent edges and the neighboring rail surfaces while they engage. Record
where motion catches, whether the flanks can align by hand, and any visible witness
marks with the print's photos.
