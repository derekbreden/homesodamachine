# Pisco cover retention

These Pisco covers fit the rear enclosure corner Derek assembled. The regulator cover rocked the most in his video. Derek would like a slightly tighter fit on all the covers and selected the Pisco for the first comparison. Each sample adds material beneath both retaining hooks and keeps the production lead-ins, spring walls and regulator saddle. [Original bench result](https://github.com/derekbreden/homesodamachine/blob/5e6d64bf900d873c59c141b13b64fa9c34e123b3/hardware/print-tests/rear-equipment-corner/prints/2026-11-21-pisco-entry-mark2/physical-result/physical-result.json)

The recessed diamonds on the flat back identify the covers.

| Mark | Printer | Fit at rest |
| --- | --- | --- |
| One diamond | Mark2 | A little clearance at both catches |
| Two diamonds | Mark2 | Nearly touching at both catches |
| Three diamonds | Mark1 | Both spring walls stay flexed against the catches after the saddle takes up the play against the regulator |

Tip each cover over the same regulator in the printed corner and engage both hooks. Compare how much it rocks with your hands off the release edges, then compare the effort to release it. The model predicts spring displacement. The bench test establishes how each cover feels. [Cover geometry](parts/geometry.json) · [Mark2 entry and fit check](fit-check.json) · [Mark1 seated spring and entry check](preload-check.json)

[Mark2 comparison print](prints/2026-11-21-mark2/print-job.json) · [Mark1 preload print](prints/2026-11-21-preload-mark1/print-job.json)

Generate the covers and slice each plate from the project root.

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-rear-equipment-caps --bin pisco-cover-retention
tools/run -- tools/hsm/target/release/enclosure-print-prep pisco-cover-retention --printer Mark2 --bed 'Textured PEI Plate' --slice --review
tools/run -- tools/hsm/target/release/enclosure-print-prep pisco-cover-preload --printer Mark1 --bed 'Textured PEI Plate' --slice --review
```
