# Install guide artwork

`hsm-install-art` refreshes the owner's installation illustrations from current
machine meshes, adds the Fill display artwork in the current bezel, and registers
camera anchors and source hashes. It runs only when refreshing the guide.

Build the manual tools:

    tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-kit-art -p hsm-install-art --bin install-illustrations --bin hsm-install-art

Refresh the saved artwork:

    tools/run -- tools/hsm/target/release/hsm-install-art refresh

`--views NAME ...` selects individual illustrations. `--out DIR` selects the
scratch scene directory; its source manifest and concise result remain after
temporary payloads and renders are removed. `--assets DIR` writes candidate
artwork and registrations beside a review instead of replacing the guide's
saved assets. `--root DIR` selects the source checkout.

Review the selected pictures, then compose the native install guide and inspect
the rendered pages as described in its [README](../../../hardware/install-guide/README.md).
