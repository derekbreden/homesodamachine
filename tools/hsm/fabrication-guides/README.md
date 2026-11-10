# Fabrication guides

`hsm-fabrication-guides` composes the maintained bench PDFs from authored procedures and typed part inputs. These manual deliverables stay outside the normal print build.

Build the optional command explicitly:

```sh
tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-fabrication-guides --bin fabrication-guides
```

Use the installed `fabrication-guides`, or the checkout's release binary:

```sh
tools/run -- tools/hsm/target/release/fabrication-guides assembly-letter
tools/run -- tools/hsm/target/release/fabrication-guides drill-and-cut-guide
tools/hsm/target/release/fabrication-guides data weld-position
```

`--root PATH` selects the source checkout for a book. `--out PATH` selects its output root; the default is the source root. Each book writes its PDF, cover and publication sidecar under its guide directory and its delivery PDF and source receipt under `output/pdf`.

`data weld-position` prints the current tube, cap and port dimensions as JSON. It reads typed rotator and endcap constants and writes no files. The existing weld-position browser test compares its pose inputs with this command.

The public [Letter API](src/letter.rs) exposes `Canvas`, `Art`, fonts, drawing primitives, paragraphs and PDF publication to the other manual builders. [Cut calculations](src/cuts.rs) call the faucet assembly's authored paths. Keep procedure inputs and dimensions with their owning sources.
