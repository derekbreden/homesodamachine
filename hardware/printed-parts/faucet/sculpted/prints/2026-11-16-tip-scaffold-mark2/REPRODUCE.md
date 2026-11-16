# Prepare the Mark2 plate with the tip's shoulder on a scaffold and roof

The plate is the Sculpted product plate of commit
[`6b77eba36`](https://github.com/derekbreden/homesodamachine/tree/6b77eba364d6ff4c80d3e115af3ca3a7493f8dd1).
Its meshes are the build's own outputs at that commit; the product report there,
`hardware/printed-parts/faucet/faucet-petgf.print.json`, names each mesh's sha256, and the
[editable project](sculpted-faucet-tip-scaffold-black-mark2.3mf) carries them.

```sh
git checkout 6b77eba364d6ff4c80d3e115af3ca3a7493f8dd1
tools/run -- hsm-print-build --
cargo_bin="$("$(command -v rustup || printf %s /opt/homebrew/bin/rustup)" which cargo)"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin faucet-plate --bin faucet-print-project \
  --bin sculpted-trial
mkdir -p "$PWD/.cache/runs"
run="$PWD/.cache/runs/sculpted-tip-scaffold-repro"
tools/run -- tools/hsm/target/release/faucet-plate sculpted "$run"
trial="$PWD/hardware/printed-parts/faucet/sculpted/prints/2026-11-16-tip-scaffold-mark2"
hsm-project compare "$trial/sculpted-faucet-tip-scaffold-black-mark2.3mf" "$run/editable.3mf"
hsm-project compare "$trial/sculpted-faucet-tip-scaffold-black-mark2.gcode.3mf" \
  "$run/sculpted-faucet-plate.gcode.3mf"
```

The editable project comes back the same by value. A fresh slice lays the same beads apart from
the slicer's own tree-support differences between runs, which the archive comparison lists; the
tip's scaffold and roof follow from the slice they are laid into.

The [verification](verification.json) readings come from the commands that answer them:
`sculpted-trial replay` on the plate's G-code, `hsm-gcode harm --object 1902` on the archive and
on the stopped plate's, and readings of the composed plate's beads, their widths and their
heights, for the tip's scaffold, roof and first shoulder course. The run's `open.json` gives the
[tip foundation record](tip-foundation.json).
