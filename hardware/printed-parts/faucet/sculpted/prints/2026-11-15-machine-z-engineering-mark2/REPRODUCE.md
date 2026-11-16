# Prepare the Mark2 plate at the machine's Z feed on the Engineering Plate

The plate is the Sculpted product plate of commit
[`47ab7d77d`](https://github.com/derekbreden/homesodamachine/tree/47ab7d77d9e49efeaabb429c454e58c35ca09e8a).
Its five meshes are the build's own outputs at that commit; the product report there,
`hardware/printed-parts/faucet/faucet-petgf.print.json`, names each mesh's sha256, and the
[editable project](sculpted-faucet-machine-z-engineering-black-mark2.3mf) carries them.

```sh
git checkout 47ab7d77d9e49efeaabb429c454e58c35ca09e8a
tools/run -- hsm-print-build --
cargo_bin="$("$(command -v rustup || printf %s /opt/homebrew/bin/rustup)" which cargo)"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin faucet-plate --bin faucet-print-project
mkdir -p "$PWD/.cache/runs"
run="$PWD/.cache/runs/sculpted-machine-z-engineering-repro"
tools/run -- tools/hsm/target/release/faucet-plate sculpted "$run"
trial="$PWD/hardware/printed-parts/faucet/sculpted/prints/2026-11-15-machine-z-engineering-mark2"
hsm-project compare "$trial/sculpted-faucet-machine-z-engineering-black-mark2.3mf" "$run/editable.3mf"
hsm-project compare "$trial/sculpted-faucet-machine-z-engineering-black-mark2.gcode.3mf" \
  "$run/sculpted-faucet-plate.gcode.3mf"
```

The editable project comes back the same by value. A fresh slice lays the same beads apart from
the slicer's own tree-support differences between runs, which the archive comparison lists.

The [verification](verification.json) readings come from the commands that answer them:
`hsm-gcode recipe` against the restored plate's archive, `hsm-gcode harm` on the archive, the run's
`cooling.json`, and the acceleration planner's motion through `hsm_print_prep::motion`.
