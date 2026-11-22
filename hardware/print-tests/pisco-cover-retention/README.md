# Pisco cover retention

Two Pisco covers fit the same rear enclosure corner. Each adds material to the underside of both retaining hooks. The lead-in points, springs and regulator saddle follow the tested cover. Derek demonstrated the play by rocking the installed cover with the meter and ASSE out. [Original bench result](https://github.com/derekbreden/homesodamachine/blob/5e6d64bf900d873c59c141b13b64fa9c34e123b3/hardware/print-tests/rear-equipment-corner/prints/2026-11-21-pisco-entry-mark2/physical-result/physical-result.json)

The flat back identifies each cover. One recessed diamond marks the first size. Two diamonds mark the tighter size. Tip each over the same seated regulator in the same corner, engage both catches and rock the cover by hand. Compare the movement and release effort using the usual side-entry approach. [Geometry](parts/geometry.json) · [Measured fit and insertion](fit-check.json) · [Mark2 plate](prints/2026-11-21-mark2/print-job.json)

Generate and slice the comparison from the project root.

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-rear-equipment-caps --bin pisco-cover-retention
tools/run -- tools/hsm/target/release/enclosure-print-prep pisco-cover-retention --printer Mark2 --bed 'Textured PEI Plate' --slice --review
```
