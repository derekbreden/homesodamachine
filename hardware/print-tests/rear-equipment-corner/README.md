# Rear equipment corner fit

The article retains the complete ASSE, Pisco and meter receivers with the
surrounding enclosure roof, rear wall, flank and corner column. Its matching
covers are copied from the production meshes. [inputs.json](inputs.json) owns
the crop and source paths; [parts/geometry.json](parts/geometry.json) binds the
article and caps to the exported geometry. The design inputs retain Derek's
picked [column](design-inputs/corner-column.png) and
[wall](design-inputs/rear-wall.png).

The receiver article prints ceiling-down at the production roof datum. The
covers stand on their production axial ends so the springs bend within their
layers. The enclosure retains its ordinary wall and infill recipe; the covers
retain their solid spring recipe. Wing channels stay clear of supports. The
fitted meter body floors retain removable support through the open west face.

[The Mark2 job](prints/2026-11-18-mark2/print-job.json) records the accepted
print, exact editable project and sent archive, recipe, native review and
startup status. The enclosure crop and its covers match the published meshes.
Physical cleanup and assembly fit remain for this printed article.

Clear the accessible body-pocket supports before installing hardware. Try the
Pisco cover's angled X-entry with the meter and ASSE hardware out of the way,
checking the shortened leaves beside the raised column and wall. Fit the
Pisco, then the meter and its cover, then the ASSE chain and its cover. Check
seating, retention and release through the complete receiver channels.

Generate the current article and prepare its plate without contacting a printer:

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-tooling --bin rear-equipment-corner
tools/run -- tools/hsm/target/release/enclosure-print-prep rear-equipment-corner \
  --printer Mark2 --slice --review
```
