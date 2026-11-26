# Full Pisco snap fit on Mark2

This trial pairs a full-length cover and receiver with the real Pisco RVFUP1/4–1/4-0.3 regulator. They carry the wide, inward-curved wings and the one-notch receiver from the Mark2 comparison. Derek felt very little waggle in either coupon and thought the one-notch pair seated slightly better. The full cover has an 8 mm-wide, 2 mm-long contoured pad over the widest part of the molded housing. The neck lip, release-collet clearance, rear inlet passage and 3 mm upper bearing come from the fitted production assembly. [Filmed choice](../open-snap-section/prints/2026-11-25-mark2-flush/physical-result.json) · [Full parts and dimensions](parts/geometry.json)

## Two dots and a 0.20 mm closer saddle

The first full cover sat flush and stayed firm in hand while the regulator inside could wiggle and spin. This pair uses the 2.60 mm feet and neutral catches from the two-dot coupon. The inner cradle moves 0.20 mm toward the molded regulator body, measured at the same snap position. A short lead at the outlet end eases the transition into the raised cradle. [First full pair in hand](prints/2026-11-25-mark2/physical-result.json) · [Two-dot coupon in hand](../open-snap-section/prints/2026-11-25-mark1-solid-pairs/physical-result.json) · [Full-size trial geometry](parts/two-dot-drop/geometry.json)

With the regulator installed, compare motion at its white outlet while holding the receiver, then press each cover edge to see whether both feet still sit flush. Wiggling the outlet checks radial play. Turning it checks friction against the round housing. [Mark2 print](prints/2026-11-25-mark2-two-dot-drop/print-job.json) · [Plate layout](prints/2026-11-25-mark2-two-dot-drop/plate-key.png)

To reproduce this pair, pass `-- --two-dot-drop` to the Cargo command below and select `pisco-two-dot-drop` when slicing.

## Try the pair

1. Rest the receiver on its flat roof face with the channel facing up. Start the regulator about 16 mm forward of its final position, with its long inlet neck facing the rear bore. Lower it into the channel, then slide it back until the neck enters the bore. The short outlet and its release ring face the open end.
2. Point the cover’s raised saddle lip toward the short outlet. The longer solid tail goes toward the rear bore. Bring the cover straight down over the loose receiver and press above both wings until the hooks seat.
3. Look along each crest where it meets the roof. Press alternately over the two wings, then over the center. Feel whether the regulator moves under the cover, whether a crest lifts, and whether the cover returns to the same position. Spread the exposed spring edges to clear the catches and lift the cover off.
4. In an assembled corner, remove the ASSE and meter groups in the production sequence. Tip the Pisco cover in from the side past the meter shoulder, keeping the tail just clear of the rear wall. Square it over the regulator for the last straight push. Reverse this motion for removal. [Production service sequence](../../printed-parts/enclosure/rear-equipment-caps/README.md) · [Measured paths and hardware clearances](fit-check.json)

Both wings have 2.00 mm lands and 0.80 mm inward bias before assembly. They run 37.32 mm along a 41.70 mm cover. The printed toolpaths put the local pad and the regulator into light contact by the time the crests reach their roof. On the installed regulator mesh, first contact with the pad and the receiver leaves about 0.015 mm of modeled take-up at the roof stop. The contact follows the body across the pad. The fitting and collets remain free. [Full pair fit check](fit-check.json) · [Mark2 plate key](prints/2026-11-25-mark2/plate-key.png)

## Reproduce the parts

The generator takes the working end profiles directly from the two Mark2 coupon STLs and registers them to the full production spring and pocket ends. The cover prints on its forward axial end and the receiver prints on the original enclosure roof. [Generator](pair.rs) · [Receiver print features](parts/pisco-receiver.print-features.json)

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin pisco-wide-snap
tools/run -- tools/hsm/target/release/enclosure-print-prep pisco-wide-pair \
  --printer Mark2 --bed 'Textured PEI Plate' --slice --review
```
