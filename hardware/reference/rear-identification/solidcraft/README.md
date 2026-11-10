# Identification-chip clearance replay

The [isolated comparison](https://homesodamachine.com/labs/solidcraft/identification) replays the [approved identification-chip edge change](https://github.com/derekbreden/homesodamachine/commit/117ada0b44e4ef2e930ac93ad6a9ce5ca95007ce). It constructs the complete chips from the historical interfaces and compares native SolidCraft geometry with the original Rust recipe. It changes no production part and submits no print.

`inputs.json` owns the frozen interfaces and source revisions. The lettering SVGs retain the original line and Bézier contours, including counters. The native designs contain their imported sketches, extruded lettering, dimension-driven blanks, fitting bores and ink recesses. One favorite clearance parameter drives the chip edges; the original bore and word positions remain independent of it. Native components carry the ink appearance, with a body appearance on each chip blank. Their occurrences put the complete parts face-up in the comparison set.

The native JSON documents are editable SolidCraft designs. The producer constructs the historical baseline; its replay opens the evaluated native container, changes the clearance parameter and saves the edited design. Exports retain separate colored bodies in the multicolor project. A temporary native combine creates each fused single-material STL without changing the saved editable design.

The Rust replay uses the historical source with a frozen layout-file path and current checkout dependencies. Initial dependency compilation belongs to setup. The edit run installs the historical changed source, compiles its program and generates its ordinary fine models, display payloads and fused print solids. Compiler queues and host waits are included in process-wall observations.

Both implementations use the website's shared renderer, camera controls and part framing. The native display reads native mesh exports; the Rust display uses the production payload decoder. Display loading, CAD computation, source compilation, output export and publication have separate observations in the comparison's `evaluation.json`. Surface comparisons identify their sampled scope; they do not assert an exhaustive surface-distance bound or a new physical print qualification.

The trial runs manually, outside normal builds and commits:

```sh
chip_run=$(mktemp -d .cache/runs/solidcraft-identification-XXXXXX)
CARGO_BUILD_JOBS=2 python3 tools/run.py -- cargo build --release --manifest-path hardware/reference/rear-identification/solidcraft/producer/Cargo.toml --target-dir tools/hsm/target
python3 tools/run.py -- tools/hsm/target/release/solidcraft-identification-replay construct --out "$chip_run"
python3 tools/run.py -- tools/hsm/target/release/solidcraft-identification-replay export-before --out "$chip_run"
python3 tools/run.py -- node hardware/reference/rear-identification/solidcraft/replay.mjs rust-before --out "$chip_run"
python3 tools/run.py -- tools/hsm/target/release/solidcraft-identification-replay replay --out "$chip_run"
python3 tools/run.py -- node hardware/reference/rear-identification/solidcraft/replay.mjs rust-after --out "$chip_run"
node hardware/reference/rear-identification/solidcraft/replay.mjs publish --out "$chip_run"
```

The downloadable native project retains the native documents, evaluated containers, interfaces and original lettering. The comparison page retains reviewed printable and display outputs. Record concise measurements and hashes, then remove the run's temporary files after publication.
