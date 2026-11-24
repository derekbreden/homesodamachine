# Individual equipment snap pairs

Each full-length production cover prints beside a separate receiver that accepts the actual component. The test transfers the raised, flat wing crests that held the Pisco cover steady in Derek’s [filmed comparison](https://github.com/derekbreden/homesodamachine/blob/2d7f9faac54a802877a41971e513dc0211d3475c/hardware/print-tests/pisco-raised-tip-cover/prints/2026-11-23-mark2/physical-result/physical-result.json).

| Plate | Matched parts | What the fixture retains |
| --- | --- | --- |
| Mark1 | ASSE cover and receiver | The roof, spring pockets, end walls and rear water bulkhead bore take the ASSE chain and its coupling. |
| Mark1 | Pisco cover and receiver | The regulator sits between the original shoulders, with its rear inlet bore and both roof pockets. This cover can also be tried in the original assembled corner. |
| Mark1 | Water-regulator cover and receiver | The roof carries the fore and aft catches and the seat for the regulator body and outlet. |
| Mark2 | Flow-meter cover and receiver | The flank carries the complete meter cup, both catches, the wire exit, port and screw-head channels and the backed shoulder. |
| Mark2 | Cold-core pump cover and receiver | The lid section retains both motor rails and end stops, the head opening, the spring pockets and the cover shoulders. |

The [Mark1 job](prints/mark1/print-job.json) and [Mark2 job](prints/mark2/print-job.json) identify the accepted files and their matching parts. The [rear cover and receiver paths](../../printed-parts/enclosure/rear-equipment-caps/crest-paths.json) and [pump crest paths](../pump-seated-snaps/parts/mark2-crest-roads.json) measure the deposited outlines in those files.

## At the bench

Remove the accessible trees, including those beneath the flow-meter fore shoulder and lip. Seat the actual component against its fixed bearing before fitting its cover. Press alternately near either wing and then each end of the cover. Movement that returns when released and a shift that stays in a second resting position are different observations. After release, look at both crests and the two receiver ledges for exposed strands or chipped edges. The flow meter’s aft shoulder grows from the side wall on a continuous slope.

## Geometry and plates

[Receiver inputs](inputs.json) define the individual rear cuts. [Their mesh record](parts/geometry.json) binds the exported seats to the production shell. The roof seats retain the original print bed. The flow-meter seat starts on its flank at an integral layer offset from that roof. Cropping the Pisco drops a detached piece of the adjacent meter and its matching support regions. The [pump receiver](../pump-seated-snaps/parts/geometry.json) retains the production lid’s print face.

The rear covers and pump cover come directly from the production STLs. Their springs stand on their axial ends. The water-regulator cap retains its nonplanar fitted roof. The [plate recipes](../../printed-parts/enclosure/trial-preparation/pieces.json) define the per-part support, spring and receiver settings.

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin equipment-snap-receivers
tools/run -- tools/hsm/target/release/enclosure-print-prep rear-snap-pairs \
  --slice --review --output hardware/print-tests/equipment-snap-pairs/prints/mark1
tools/run -- tools/hsm/target/release/enclosure-print-prep pump-meter-snap-pairs \
  --slice --review --output hardware/print-tests/equipment-snap-pairs/prints/mark2
```
