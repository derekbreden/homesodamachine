# Pisco cover retention

These Pisco covers fit the rear enclosure corner Derek assembled. The regulator cover rocked the most in his video. Derek would like a slightly tighter fit on all the covers and selected the Pisco for the first comparison. Each sample adds material beneath both retaining hooks and keeps the production lead-ins, spring walls and regulator saddle. [Original bench result](https://github.com/derekbreden/homesodamachine/blob/5e6d64bf900d873c59c141b13b64fa9c34e123b3/hardware/print-tests/rear-equipment-corner/prints/2026-11-21-pisco-entry-mark2/physical-result/physical-result.json)

The recessed diamonds on the flat back identify the covers Derek tried in the same printed corner.

| Mark | Printer | Bench result |
| --- | --- | --- |
| One diamond | Mark2 | Hard to distinguish from the original by hand |
| Two diamonds | Mark2 | Rocks gradually with slightly less travel. Derek’s preferred sample |
| Three diamonds | Mark1 | Snaps between two firm positions |

The preload check describes a centered cover. The follow-up checks how a small roll changes the clearance above each pointed tip. The retaining ribs are hidden in the bench footage. [Cover geometry](parts/geometry.json) · [Entry check](fit-check.json) · [Centered preload](preload-check.json) · [Rib and pocket measurements](prints/2026-11-21-preload-mark1/physical-result/rib-seating-check.json)

The physical records include Derek’s observations and close-up motion clips. [Mark2 bench result](prints/2026-11-21-mark2/physical-result/physical-result.json) · [Mark1 bench result](prints/2026-11-21-preload-mark1/physical-result/physical-result.json)

Generate the covers and slice each plate from the project root.

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-rear-equipment-caps --bin pisco-cover-retention
tools/run -- tools/hsm/target/release/enclosure-print-prep pisco-cover-retention --printer Mark2 --bed 'Textured PEI Plate' --slice --review
tools/run -- tools/hsm/target/release/enclosure-print-prep pisco-cover-preload --printer Mark1 --bed 'Textured PEI Plate' --slice --review
```
