# Full two-dot Pisco saddle

Derek could hold the previous full cover firmly while the regulator inside it still wiggled and spun. This Mark2 pair uses the two-dot snap he preferred on the Mark1 comparison. The molded-body saddle sits 0.20 mm closer to the Pisco. Both pieces have two recessed dots on the outside. [Previous full-pair hand test](../../prints/2026-11-25-mark2/physical-result.json) · [Two-dot coupon hand test](../../../open-snap-section/prints/2026-11-25-mark1-solid-pairs/physical-result.json)

## Try the regulator

1. Press the empty cover into the loose receiver. Feel both hooks catch, sight along the two broad feet, and check how much either edge lifts when you press the opposite edge. Spread the wings to release the cover.
2. Rest the receiver on its flat roof with the channel facing up. Point the long inlet neck toward the rear bore and the short outlet with its release ring toward the open end. Start the regulator about 16 mm forward, lower it into the channel, and slide it back until the long neck enters its seat.
3. Face the cover's raised neck lip toward the short outlet. Press straight down over both wings. Compare how fully the feet seat with the empty fit. Hold the two printed parts together, then rock and turn the molded regulator body by hand. Watch the outlet ring and the two feet so you can tell housing movement from cover lift.
4. Check that each release ring is accessible. Spread the exposed wings and lift the cover to remove the regulator. In the assembled corner, remove the ASSE and meter groups first, then tip the cover past the meter shoulder and square it for the last push. [Production service sequence](../../../../printed-parts/enclosure/rear-equipment-caps/README.md)

The submitted outer wall moves 0.198 mm toward the widest part of the housing at the saddle center. The fixed receiver reaction and both collars keep their fitted positions. With the modeled housing against that fixed seat, the broad saddle contacts it about 0.19 mm before the first foot edge reaches its roof. The hooks already have about 1.37 mm of radial capture there. The housing is round, so resistance to spinning depends on contact force and friction. The hand comparison measures that result. [Mesh and native toolpath measurements](fit-check.json)

## Reproduce

From the repository root, run the generator with the two-dot option. The cover STL stands on its short-outlet end. The receiver STL uses the machine frame and the Mark2 plate turns it roof-down. [Geometry and registration](geometry.json) · [Receiver print features](receiver.print-features.json)

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin pisco-wide-snap -- --two-dot-drop
```
