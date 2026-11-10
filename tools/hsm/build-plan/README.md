# Build plan

`hsm-build-plan` owns native producer grouping, action inputs, dependency rules,
graph projections and BUILD rendering. `src/planning.rs` shares typed declarations
with affected-target discovery. `inventory.json` classifies inputs and outputs;
`programs.json` names the native producer entrypoints used by tracing.

Rust program rules take their compiler inputs from Cargo's dependency records.
The producer rule stages the files the program reads at runtime, including
editable placements and dimensions. Changing runtime data reruns its producer
while reusing the compiled program. Data embedded with `include_str!` or
`include_bytes!` belongs to the compiler rule as well; its filename does not
decide whether it is code or runtime data.

`program.runtime_inputs` retains explicitly logged runtime reads that are also
compiler sources, including a producer that reads Cargo manifests while running.
The producer reads its staged repository through `HSM_REPO_ROOT`; compilation and
retained geometry use the host checkout through `HSM_WORKSPACE`.

The commands run on request:

```sh
tools/run -- tools/hsm/target/release/hsm-build-plan render --only installed-machine
tools/run -- tools/hsm/target/release/hsm-build-plan write
tools/run -- tools/hsm/target/release/hsm-build-plan affected --artifacts --manifest
tools/run -- tools/hsm/target/release/hsm-build-plan trace-inputs hardware/manifold-layout/installed_machine.rs
tools/run -- tools/hsm/target/release/hsm-build-plan sync-tree --help
```

`render` prints without writing. `write` updates BUILD.bazel and this checkout's
`.bazelrc.paths`; `--root` selects an explicit repository. `project-graph-file
GENERATOR INPUT OUTPUT` writes a reader projection using only its named graph
input. `inventory`, `actions` and `dependency-rules` expose the same native
metadata as JSON. `check` and `cycles` are explicit questions, never build hooks.

The compiler/runtime split, producer edges and maintenance commands are checked
on demand:

```sh
tools/run -- cargo test --release --locked -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-build-plan
```
