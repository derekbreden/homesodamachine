# Prepare the small PET-GF plate

The preparer writes the plate from the parts' exported meshes and the `small-petgf` piece in
[`pieces.json`](../../../trial-preparation/pieces.json), at the commit that records this print. The
[preparation record](preparation.json) binds each mesh by its digest; the organizer's mesh is a
build output of its generator and is not tracked.

```sh
cargo_bin="$(/opt/homebrew/bin/rustup which cargo)"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin enclosure-print-prep
mkdir -p .cache/runs/small-petgf
tools/run -- tools/hsm/target/release/enclosure-print-prep small-petgf --slice --review \
  --output .cache/runs/small-petgf
```

Preparing the committed piece writes the [editable project](2026-11-15-small-petgf-mark2-39847f01.3mf)
byte for byte. `--slice` runs the installed Bambu Studio command line and the standing cooling
stage, and restores the regulator cap's contact courses; `--review` reads the archive back. A fresh slice lays the
same beads as the [sent archive](2026-11-15-small-petgf-mark2-39847f01.gcode.3mf) apart from the
slicer's own tree-support differences between runs, which `hsm-gcode compare` shows.
