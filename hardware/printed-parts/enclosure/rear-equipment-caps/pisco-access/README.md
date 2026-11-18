# Pisco cover access concepts

The separate L cover closes the lower west quarter of the Pisco seat. The
receiver carries the lower east quarter. The cover keeps the fitted body and
neck surfaces and the angled west wing catch. The channel opens around the
spread wing, including the tip's room under the ceiling. The fixed cheek's
lower bore grows at the shell's corbel slope in the ceiling-down print.

Remove the meter and its cover before inserting or withdrawing the separate
Pisco cover from below. The sampled cap path clears the complete back-top
receiver, the Pisco and its connected stem check. The source retains the
angled catch accepted in the [physical result](../prints/2026-11-17-single-pisco-mark2/physical-result.json).
The Pisco hardware enters axially through the open fore end, with its stem
check disconnected. The passage keeps a fitted ring at the body's widest
station. The single-wing cover's retention remains to be tried in hand. This
is the preferred cover concept.

The shared cover joins the Pisco back to the meter back and keeps the meter's
lower wing. Its seated geometry clears the receiver. Its sampled release
moves intersect the receiver and meter, so it needs a coordinated receiver
and latch layout before an insertion path can be proposed.

The exploded models separate the pieces for viewing. Their offsets describe
the illustration, not an installation move. Orange identifies the removable
cover, blue the fixed receiver and teal the independent meter cover.

- [Separate L cover, seated](https://homesodamachine.com/parts#step:printed-parts%2Fenclosure%2Frear-equipment-caps%2Fpisco-access%2Fseparate-l-cover-seated.step)
- [Separate L cover, exploded](https://homesodamachine.com/parts#step:printed-parts%2Fenclosure%2Frear-equipment-caps%2Fpisco-access%2Fseparate-l-cover-exploded.step)
- [Shared cover, seated](https://homesodamachine.com/parts#step:printed-parts%2Fenclosure%2Frear-equipment-caps%2Fpisco-access%2Fcombined-cover-seated.step)
- [Shared cover, exploded](https://homesodamachine.com/parts#step:printed-parts%2Fenclosure%2Frear-equipment-caps%2Fpisco-access%2Fcombined-cover-exploded.step)

The [native source](../pisco_access_study.rs) reads the current part exports.
[access.numbers.json](access.numbers.json) records the sampled translations
and intersections. The wing deflection is a geometric envelope with its
root fixed; it does not predict force.

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-rear-equipment-caps --bin pisco-access-study
tools/run -- hsm render --jobs hardware/printed-parts/enclosure/rear-equipment-caps/pisco-access/render.json
```
