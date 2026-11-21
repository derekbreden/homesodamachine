# Reservoir A aft tube snap fit print

The coupon is a crop of the production cold-core lid around reservoir A's two aft tube clips,
with the lid's full thickness under them. [`inputs.json`](inputs.json) sets the crop.
[`coupon.rs`](coupon.rs) exports the closed print mesh and the lid's solid-infill region that
reaches into the crop. [`parts/geometry.json`](parts/geometry.json) binds both to the production
lid.

It prints as the lid does: flat face down on textured PEI with the clips standing up, in the lid's
PET-GF wall recipe. A cooling tower gives the small spring sections time between layers.

The taller clip holds the draw line and has two free jaws. The lower clip holds the fill line.
One of its jaws is filled square and joined to the taller clip's root over the aft part of its
length, and its free jaw has the fit of back-top's east-wall fill seat. Each seat follows its line's level turn, so a tube enters bent
along the seat.

The [Mark1 fit print](prints/2026-11-20-mark1/print-job.json) carries the coupon on a textured
plate.

Press a length of quarter-inch tube down into each clip. Observe the push each one takes, the
free jaws during insertion and release, how the fill tube passes the fixed jaw's lip, and how
securely each tube stays seated. The physical fit awaits that observation.

Generate the coupon and prepare its plate without contacting a printer:

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin reservoir-a-aft-snaps
tools/run -- tools/hsm/target/release/enclosure-print-prep reservoir-a-aft-snaps \
  --printer Mark1 --slice --review
```
