# Rear equipment corner fit

The article retains the complete ASSE, Pisco and meter receivers with the
surrounding enclosure roof, rear wall, flank and corner column. Its Pisco
cover is copied from the production mesh. [inputs.json](inputs.json) owns
the crop and source paths; [parts/geometry.json](parts/geometry.json) binds the
article and cover to the exported geometry. The ASSE and meter covers come from
[the first plate](https://github.com/derekbreden/homesodamachine/blob/2280aec49910075cbd4cb7280585c954d8206eb9/hardware/print-tests/rear-equipment-corner/prints/2026-11-18-mark2/print-job.json).

The receiver article prints ceiling-down at the production roof datum. The
cover stands on its production axial end so the springs bend within their
layers. The enclosure retains its ordinary wall and infill recipe; the cover
retains its solid spring recipe. The catch pockets stay clear of supports. The
meter's fore shoulder, the lip its cover's upper leaf rides over and its fitted
body floors take removable support through the open west face. The lip bridges
from that support to the aft shoulder, which stands on its corbel.

The [first plate's physical result](https://github.com/derekbreden/homesodamachine/blob/2280aec49910075cbd4cb7280585c954d8206eb9/hardware/print-tests/rear-equipment-corner/prints/2026-11-18-mark2/physical-result/physical-result.json)
holds Derek's photos and words on the article this one answers.

Clear the supports under the meter's fore shoulder and lip and in its body
pockets before installing hardware. Try the Pisco cover's angled X-entry with
the meter and ASSE hardware out of the way, checking the shortened leaves
beside the corner column. Fit the Pisco, then the meter and its cover, then the
ASSE chain and its cover. Check seating, retention and release through the
complete receiver channels.

Generate the current article and prepare its plate without contacting a printer:

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin rear-equipment-corner
tools/run -- tools/hsm/target/release/enclosure-print-prep rear-equipment-corner \
  --printer Mark2 --slice --review
```
