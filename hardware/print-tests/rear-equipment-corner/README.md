# Rear equipment corner fit

The article retains the complete ASSE, Pisco and meter receivers with the
surrounding enclosure roof, rear wall, flank and corner column. Its matching
covers are copied from the production meshes. [inputs.json](inputs.json) owns
the crop and source paths; [parts/geometry.json](parts/geometry.json) binds the
article and covers to the exported geometry.

The receiver article prints ceiling-down at the production roof datum. The
covers stand on their production axial ends so the springs bend within their
layers. The enclosure retains its ordinary wall and infill recipe; the covers
retain their solid spring recipe. The catch pockets stay clear of supports. On the corner retained for this bench comparison, the
meter's fore shoulder, the lip its cover's upper leaf rides over, the open west
edge of its aft shoulder and its fitted body floors take removable support
through the open west face. The aft shoulder's first course bridges from its
west edge to the flank.

The Pisco cover tips past the recessed meter shoulder. The flow meter, Pisco
and ASSE fit together with all three covers installed. The original pointed
Pisco cover rocks in this corner. The production Pisco cover uses the full-length
raised flats that Derek fitted in the same quadrant.
[Fitted Pisco cover and comparative press test](https://github.com/derekbreden/homesodamachine/blob/2d7f9faac54a802877a41971e513dc0211d3475c/hardware/print-tests/pisco-raised-tip-cover/prints/2026-11-23-mark2/physical-result/physical-result.json) · [Assembled corner and bench observations](https://github.com/derekbreden/homesodamachine/blob/5e6d64bf900d873c59c141b13b64fa9c34e123b3/hardware/print-tests/rear-equipment-corner/prints/2026-11-21-pisco-entry-mark2/physical-result/physical-result.json)

Clear the removable support from the meter shoulders, upper lip and fitted
body passages. With the meter and ASSE hardware out, seat the Pisco and tip
its cover in from the side as in the photos. Check that it passes the
recessed shoulder and that both catches seat. Install the meter and its
matching cover, then the ASSE chain and cover. Check that the meter cover
holds and releases on both leaves.

The [individual snap pairs](../equipment-snap-pairs/README.md) use the current production receivers and covers, including the permanently backed meter shoulder. To regenerate the combined corner from current production and prepare its plate, run

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin rear-equipment-corner
tools/run -- tools/hsm/target/release/enclosure-print-prep rear-equipment-corner \
  --printer Mark2 --slice --review
```
