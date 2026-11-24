# G-Ganen pump receiver and cover

Slide all four complete rubber foot assemblies off the real pump. Lower the bare
pump into the fixed rail seats, with its head over the shallow front recess.
Press the production cover over the barrel until both hooks engage. Hold the
receiver still and press alternately on the two sides of the cover. Watch the
motor against its fixed rail stops as well as the cover against the receiver.
Spread the exposed leaves and lift the cover straight up to test release.

The receiver is a crop of the production lid with both rail floors, both end
stops, the motor-head recess and both full-depth catch pockets. Its underside
is the lid's original Z0 print face. The production cover stands on its axial
end. Use the lid's PET-GF process for the receiver and the pump cap's solid,
three-loop process for the cover. [Crop](parts/geometry.json) · [Production recipes](../../printed-parts/enclosure/trial-preparation/pieces.json)

Each flat crest extends 0.40 mm farther toward the lid than the preceding
pointed tip. At the measured crest stop, about 0.17 mm of vertical clearance
remains with the pump resting on its rails. The centered spring model gives
2.11 mm of hook engagement on each flank. [Seating, roll and release](parts/fit-check.json)

The final Mark2 slice lays a straight outer wall on both crests in all 227 cap
layers. Its 226 regular layers reach the requested rise within 0.001 mm.
First-layer foot compensation draws the bed-contact edge in by 0.15 mm.
[Mark2 crest roads and sliced archive](parts/mark2-crest-roads.json)

After building the production lid, generate its crop from the repository root.

```sh
tools/run -- cargo run --release --locked --manifest-path tools/hsm/Cargo.toml -p hsm-foam-cap --bin pump-receiver-coupon
```
