# PGFUN swivel and pivot fixture

The [build instructions](../../../gun-positioner/README.md) govern this
two-axis gun fixture on the existing rotator. `design.json` controls the
nominal print pose and received fits. `pgfun_positioner.rs` constructs the
printable solids with the hsm kernel and emits their files, viewer payloads,
the installed assembly and the downloadable `print-pack.zip`.

Build the native commands, then run this fixture when its outputs are needed:

```sh
tools/run -- cargo build --manifest-path tools/hsm/Cargo.toml --release --locked -j 2 -p hsm-pgfun-positioner
tools/run -- tools/hsm/target/release/pgfun-positioner
tools/run -- tools/hsm/target/release/pgfun-check
tools/run -- tools/hsm/target/release/positioner-view
```

`pgfun-check` checks sampled clearances against pinned gun/rotator references and
screens loads. The receipt describes those numerical limits. Assembly sweeps
and the specified loaded commissioning establish actual received behaviour.
All individual exports share their specified print frame; assembly exports
retain rotator coordinates. Geometry is distributed by the CAD publication
bundle. The print archive contains the STLs, design and part manifest.

The native library shares the typed design, gun transform and mesh readers with
the shop guide. The clamping contours come from the pinned reconstructed scan.
The reference reader verifies its retained gun meshes against their receipt and
reads the rotator's placed fine model. These commands remain outside the normal
print build.
