# Installed wiring bench export

`hsm-wiring` writes the optional wiring manifest, conductor worksheet and standalone
native wiring exports from the normal build's retained physical machine and placement.
It resolves the current authored routes through the same typed sources as the machine.

Build the manual tools:

    tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-wiring -p hsm-machine --bin hsm-wiring --bin installed-wires

Export the saved machine's wiring:

    tools/run -- tools/hsm/target/release/hsm-wiring

`--output DIR` selects the bench destination. `--numbers-only` writes the recipe,
manifest and worksheet for inspection. `--root DIR` selects the checkout; `--work DIR`
selects its retained installed-machine work. Run the focused print build first when
the physical machine or its placements change.

The manifest names the physical model, route recipe and written geometry by digest.
It records the producer binaries and authored input hashes. Worksheet lengths are
modeled conductor centrelines; allowances and physical dressing belong to the assembly
instructions. This command runs on request and adds no work to the print build.
