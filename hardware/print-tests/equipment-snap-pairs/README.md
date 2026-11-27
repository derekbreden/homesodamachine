# Individual equipment snap pairs

## Full-size bench corrections

Derek accepted the full three-dot Pisco and ASSE pairs and the YZMSZ water
regulator with its revised saddle. The earlier regulator cover allowed the body
to rock in its fixture. His photos of the Digiten receiver show loose
roads in the short catch beside the continuous courses on the previous design.
[Pisco and ASSE](prints/2026-11-26-mark2-pisco-asse/physical-result.json) ·
[Water regulator](prints/2026-11-26-mark1-meter-water/physical-result.json) ·
[Flow-meter comparison photos](prints/2026-11-26-mark1-meter-water/physical-result/physical-result.json)

The replacement Digiten receiver mates with the three-dot cover already printed
on Mark1. Its short upper guide faces down on the plate. That face is recessed
0.25 mm to allow for the texture left by support removal. The long hook bears
on an upward-facing surface at its original height. A dense interface on
removable trees supports the exposed underside of that cheek. The two blind
seams where the catches join the receiver are filled. Clear the trees through the open side before
installing the meter. [Receiver fit](parts/supported-meter/fit-check.json)

The replacement YZMSZ cover mates with the existing three-dot water-regulator
receiver. Its fitted saddle reaches 0.40 mm farther toward the regulator body at
the same wing position. With the housing centered, the rigid model gives
1.53 mm of engagement at each hook and leaves the feet 0.23 mm short of their
stops. Derek reported that the revised cover fit very well.
[Hand-fit result](prints/2026-11-26-mark1-firm-regulator/physical-result.json) ·
[Cover measurements](parts/firm-regulator/fit-check.json)

`equipment-snap-receivers --supported-meter` and `--firm-regulator` produce the
two replacements. The `supported-meter-receiver` and `firm-regulator-cap`
recipes print one full part each in its enclosure or cover orientation.

## Full-size three-dot pairs

Derek preferred the three-dot pair for its easy start and steadier hold in the
[C037 hand comparison](../pisco-wide-snap/prints/2026-11-26-mark2-easy-entry/physical-result.json).
The [full ASSE, flow-meter and water-regulator pairs](parts/three-dot) carry both
working sides of that snap on their fitted hardware seats. The
[full Pisco pair](../pisco-wide-snap/parts/three-dot) also carries its short-outlet bearing and end stops.

| Hardware | Fit the hardware into its receiver | Fit the cover |
| --- | --- | --- |
| ASSE and threaded inlet coupling | With the drain sleeve off, place the chain 16 mm forward and slide the inlet into the rear bore. | Align the drain opening with the vent and the extended end with the coupling. Press toward the fixture roof. |
| Digiten flow meter | Dress its flexible leads into the wire exit. Enter 16 mm forward and slide aft under the fixed shoulders. | Put the shorter upper wing toward the Pisco side. Press straight from the west toward the flank. |
| YZMSZ water regulator | Place the housing and smaller outlet into their fitted bores. | Align the cover’s outlet relief with the collet and press toward the fixture roof. |

Clear the accessible supports first. At each station, press on the rigid spine with the
component seated. Check the start, the click on both sides, and whether the rigid
component or the cover can move separately. Spread the exposed wings to release
the cover. The ASSE retains the wrench flats, inlet-adapter shoulders and vent opening.
The meter retains the relieved saddle, wire passage and backed upper shoulder.
The water regulator retains its fitted body-to-outlet transition and collet access.

The six hooks have 1.68 mm of modeled radial capture near the seated stop. The
complete hardware enters all three fixtures along the original loading paths.
The [mesh and loading measurements](parts/three-dot/fit-check.json) and
[print frames](parts/three-dot/geometry.json) identify each checked file.
The ASSE, meter and regulator covers stand on their production axial ends.
Their separate receivers retain the enclosure’s ceiling-down print orientation.

To reproduce these historical specimens, build the back-top and installed covers at the
[trial source revision](https://github.com/derekbreden/homesodamachine/tree/244e007084db110e1637030c3bfadb8474e4de12)
before running the command below. The trial measures the preceding straight wings and
transfers the selected section onto them. Current production draws that section directly.

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin equipment-snap-receivers -- --three-dot
```

## Raised-crest pairs

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
