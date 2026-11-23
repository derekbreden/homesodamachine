# Pisco cover rocking

These receiver-and-cover pairs test what lets the cover roll around the Pisco outlet after the catches engage. Each receiver is a section of the enclosure with its regulator passage, adjacent meter shoulder, pocket ceilings and end walls. Fit the regulator through the front and slide it home. In the receiver with rear stops, bring the regulator in below the west post, then lift diagonally toward the center before sliding it aft.

The cover has recessed bars on its back. The matching receiver has the same count of notches in its cut roof edge. The older covers have diamond marks.

| Pair | Marks | Contact under test |
| --- | --- | --- |
| A | One bar | Deeper wing-tip pockets and lightly sprung chamfered catches |
| B | Two bars | The A catches with flat stops at both ends of the rigid cover |
| C | Three bars | Short, closely spaced flat catch sections with matching teeth |
| D | Four bars | Longer, more widely spaced flat catch sections with matching teeth |

Start with the old three-diamond cover in base A. See whether the same side-to-side pressure can still toggle it between resting positions. This keeps the original cover and changes the headroom above its wing tips. Try A/A and B/B next. If B settles more firmly, the A cover in base B tests the rear stops alone and the B cover in base A tests the outlet-end stops alone.

Compare C and D as matched pairs. Look along the underside of each ledge before assembly for a drooping strand that would lift a tooth. Seat the regulator and try rocking each cover with the same fingertip pressure. A single stable seat tests whether both rows of teeth bear together. A remaining toggle with sound bridge surfaces would point back to how the wings and body locate in the receiver. D also has more flat tooth contact because fewer entry ramps share the available length.

The [bench measurements](bench/evidence.json) link the source video and earlier physical prints. [Part dimensions](parts/geometry.json) and [fit measurements](parts/fit-check.json) describe the manufactured pairs and their modeled paths. The [Mark1](prints/2026-11-22-stops-mark1/print-job.json) and [Mark2](prints/2026-11-22-bridges-mark2/print-job.json) records identify the exact plates.

Rebuild the trial meshes with `tools/run -- cargo run --release --offline -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-rear-equipment-caps --bin pisco-cover-rocking`. The plate recipes are `pisco-rocking-stops` and `pisco-rocking-bridges` in the enclosure's native print preparation.
