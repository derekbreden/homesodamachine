# Complete Sculpted faucet trial for Mark2

The [print-ready archive](sculpted-faucet-dispense-face-sloped-foot-black-mark2-ready.gcode.3mf)
contains the base, shared tip with the trial backing, display cover, above-counter plate and
side-down lever. It awaits its first print. It uses black Polymaker PET-GF
on Mark2's left hardened nozzle and textured PEI. Bambu identifies the external spool as PET-CF
under the saved Polymaker PET-GF preset.

Open the print-ready archive as a project in Bambu Studio Preview when printing it. The
[editable project](sculpted-faucet-dispense-face-sloped-foot-black-mark2.3mf) carries the five meshes,
support aids and settings. The executable archive comes from a temporary slicing precursor
that fills the space under the mounting face. The underside stage replaces that fill in the
toolpaths.

## Tip and cover

Two tapered shoulders back the leading corners of the display pocket from the inside of the
tip. The outlet plane, the snap grooves and the cover's approved print mesh stay at their
fitted geometry. The [geometry reading](head/dispense-face-review.json) binds the trial tip mesh
to its [sandbox source](head/faucet-dispense-corner.rs) and tests the added stock against the
display and cover along their nominal assembly path. The print answers whether the corner
opening is covered and the snap still seats as firmly as the
[approved fit](https://github.com/derekbreden/homesodamachine/blob/c8667107f964589be7dc69f8fb924f69a12729b3/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-underside-complete-mark2/physical-result/physical-result.json).

## Sloped foot

A scaffold and sloped roof carry the courses that form the underside and the insert shoulders.
The uphill side of each ring lands first so the fill can tie into it. The level courses feather
onto the sloped foot. Each support plug goes into the first counterbore and the pilot beyond it
stays clear. This plate uses the same underside preamble as the
[socket-plug plate](https://github.com/derekbreden/homesodamachine/tree/b6f0e6063170eeeb88f62527a1adeae12be4a3f6/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-foot-socket-plugs-mark2).
The print answers how the uphill side and feathered join finish and whether the plugs release.
The [underside receipt](sloped-underside.json) records the emitted courses and the feathered
paths.

## Readings

The [slice review](slice-review.json) identifies the archive and G-code hashes, native settings,
the full deposited-bead envelope and the Mark2 trim. The slicer's time and weight estimates
describe the filled-base slice. The underside receipt records the motion of the preamble
that takes the fill's place. The slice review also records the net extrusion in the executable
archive. The [head replay](head-replay.json) samples the exact archive
toolpaths near the base, including the remaining spiral lifts. It uses the photo-derived
[H2C toolhead](../../../../../reference/h2c-toolhead/README.md) model. The small modelled nozzle
flank overlap occurs while laying a sloped perimeter, and physical clearance remains to be
observed. The replay covers commanded print motion. The printer's own park, pause and resume
moves are outside its scope.

## Reproduce the plate

- Rebuild the tip, cover, faucet assembly and other rigid part exports from the source
  revisions in the geometry and print receipts, and check their input hashes. Put
  [the trial's Rust example](head/faucet-dispense-corner.rs) in the
  [sandbox](../../../../../../tools/hsm/sandbox/README.md) examples directory and run it into
  the trial's scratch directory to write the tip STL. Use the approved cover STL directly.
- The [socket-plug stage sources](https://github.com/derekbreden/homesodamachine/tree/b6f0e6063170eeeb88f62527a1adeae12be4a3f6/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-foot-socket-plugs-mark2/stage)
  regenerate the filled base with `make_union.py` and rasterize the left-active head with
  `headmap.py`. Use `tools/cad-venv/bin/python` for the stage.
- Prepare and slice offline with the
  [Sculpted preparer at the socket-plug revision](https://github.com/derekbreden/homesodamachine/blob/b6f0e6063170eeeb88f62527a1adeae12be4a3f6/hardware/printed-parts/faucet/sculpted/prepare_print_project.rs),
  [the two-mesh input patch](stage/trial-inputs.patch) and the
  [captured finish selection](stage/finish-selection.json). Use the patch on a scratch
  copy of the preparer beside its `rim_supports.rs` and point its `FINISH` constant to the
  captured selection. Link the print-prep libraries from the socket-plug revision. Pass
  `--printer Mark2`, `--filament-colour` from the slice review, `--filled-base` with the
  generated filled base, `--tip-mesh` with the trial tip, `--cover-mesh` with the approved
  cover and `--slice-output` with a scratch directory. Apply the
  [physical-base patch](stage/physical-base.patch) after the input patch to make the editable
  project. Use `--physical-base` in place of `--filled-base` and omit `--slice-output` on that
  invocation.
- Run the socket-plug `sloped.py` with the resulting cooled native slice, preparation report,
  original base STL and head map. Replay the output using the archived `check.py` with the
  [spiral lift patch](stage/replay-spirals.patch). Package the staged output with
  `hsm-printer archive` and compare its extracted G-code with the staged toolpaths.
