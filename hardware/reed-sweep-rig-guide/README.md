# Reed sweep rig build guide

The illustrated Letter guide follows the float calibration fixture from the print
plates to the first bench sweep. The [website reader](https://homesodamachine.com/read/reed-sweep-rig-guide/reed-sweep-rig-guide.pdf)
opens the same PDF that prints single-sided on Letter at actual size.

The [rig procedure](../assembly/reed-sweep-rig.md) owns setup and wiring. The
[fixture directory](../printed-parts/fixtures/reed-sweep-rig/README.md) owns the
print files, design datums and physical fit status. The
[float calibration procedure](../printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration)
owns the acceptance readings.

## Rebuild

The numbered HTML leaves are editable and share the weld rotator's page
furniture. The native binder renders the leaves, creates the PDF bookmarks,
and writes the PDF, cover, document sidecar and source receipt beside them.
The site serves those committed files.

```sh
tools/run -- cargo build --manifest-path tools/hsm/Cargo.toml --release --locked -j 2 -p hsm-manual-guides
tools/run -- tools/hsm/target/release/hsm-manual-guides bind reed-sweep-rig-guide
```

The drawings use the fixture's own mesh payloads. Re-export the fixture when
its geometry changes, using the fixture README's command. Render the guide
poses with the current payloads, then bind again.

```sh
tools/run -- hsm render --jobs hardware/reed-sweep-rig-guide/art/render-jobs.json \
  --size 1800x1050 --bg '#f5f8ff' --no-fog --no-ground --edges
```

Coral identifies the part being handled or the direction of motion. Brass
identifies inserts, and blue locates a datum or a gauge. A translucent tube
reveals the parts it covers. The wiring and meter views are schematics.
