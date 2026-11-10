# Print build

`hsm-print-build` carries completed producers into the checkout and publishes them
while the remaining print build continues.

```sh
tools/run -- hsm-print-build
tools/run -- hsm-print-build //:enclosure-back-top //:installed-machine
```

The native planner selects declared producers and their prerequisites. The engine
reuses compiled programs and completed results by their actual source and input
bytes. A runtime input change keeps the compiled program; equal producer exports
keep downstream results reusable. Each producer runs with its declared runtime
files in a temporary stage. Completed files are carried atomically into the
checkout and their cache artifact paths enter the run receipt.

The driver reads each producer's progress checkpoints. The first completed view
is independent of later producers. Publication runs as
`hsm-publish --root ROOT`; concurrent requests coalesce behind the active publisher.
The driver waits for the last publication before returning. A failed build keeps
its independent completed producers, blocks dependents of failed producers, and
returns failure. A publication failure makes an otherwise successful run fail.

Placement-only changes can publish an early scene using the retained installed
machine program. A status-only checkpoint keeps the completed scene's identity.
File replacement is atomic, so a reader sees a complete retained file or its
complete replacement.

PCB models retain their raw GLBs and textures. Shared meshes replace raw GLBs
inside `hardware/assembly/scenes/glb/`.

Target names and source paths can follow `--`. A target selects its prerequisites;
a source selects the producers and dependents that use it. `//:target` remains a
target alias. The driver invokes the native engine directly.

`--root`, `--run-dir`, `--runner`, `--engine`, `--publisher` and `--progress` select
explicit paths for another checkout or an isolated fixture. `--no-publish` carries
completed files without starting publication. `--check-current` reads current
engine results without compilation, producer execution, checkout carries or
publication. It returns failure if a selected result is unavailable.

The run directory contains producer and publication logs, an atomically updated
`receipt.json`, and the completed `result.json`. Receipts name declared exports,
their stable cache artifact paths and each target's status. The result adds request
time, source commit, full-build selection, cache/compilation metrics and publication
timings. Per-target staging is removed after its files reach the checkout; the
engine retains the shared content-addressed artifacts.

Focused driver fixtures run on request:

```sh
tools/run -- cargo test --release --locked -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-build
```
