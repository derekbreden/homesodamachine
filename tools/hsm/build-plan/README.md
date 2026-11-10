# Native build plan

`hsm-build-plan` resolves the machine's native producers, their prerequisites and
the files each program reads while running. `graph.json` records observed producer
inputs and outputs; `programs.json` names traceable native entrypoints;
`inventory.json` classifies generated exports and rewritten authored media.

`planning::Plan` is the shared graph used by the print executor, affected-source
selection and receipt carrying. Target selectors request a target and its
prerequisites. A source or input path requests its declared readers, downstream
consumers and their prerequisites. Empty selection and `everything` select the
normal print graph. `//:target` and `:target` are aliases for the native name.

```sh
tools/run -- hsm-build-plan plan installed-machine
tools/run -- hsm-build-plan actions hardware/manifold-layout/installed_machine.rs
tools/run -- hsm-build-plan affected --artifacts --why
tools/run -- hsm-build-plan trace-inputs hardware/manifold-layout/installed_machine.rs
```

`Program.sources` is the compiler closure. `Plan::runtime_inputs` retains runtime
data and explicitly recorded `Program.runtime_inputs`, including source files or
Cargo manifests a program reads while running. Optional authored media is staged
when present. Declared JavaScript entrypoints retain relative module imports and
their package metadata. Installed package directories are reused by the executor.

`HSM_REPO_ROOT` names the staged repository. `HSM_WORKSPACE` names the host checkout
used for compilation and retained geometry. Graph readers receive their own stable
classification projection at the declared graph path. `GraphProjection::render`
supplies the same bytes for staging and input identity.

`receipt.rs` defines native run results. Each target records its status, declared
outputs and completed export paths. Receipts retain execution metrics without
requiring the planner to interpret them. Failed, blocked and non-current targets
contribute no carried outputs. Shared artifact blobs retain every destination.

The print executor carries completed producers as they finish. `sync-tree
--receipt FILE` explicitly rereads that recorded run; `sync-tree --derived-only
--stage` stages declared generated Git changes while preserving the publisher's
model cohort. Adding `--receipt FILE` admits only usable targets' recorded output
destinations. `failed-targets FILE` reads unavailable target names from a receipt.

```sh
tools/run -- hsm-build-plan sync-tree --receipt .cache/runs/example/result/receipt.json
tools/run -- hsm-build-plan sync-tree --derived-only --stage
tools/run -- cargo test --release --locked -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-build-plan
```

`inventory`, `plan` and `actions` print metadata without building geometry.
`trace-inputs --all`, `cycles`, receipt carrying and derived restoration run only
when requested. `project-graph-file GENERATOR INPUT OUTPUT` writes a projection
from its explicit graph input.
