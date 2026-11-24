# Print build

`hsm-print-build` carries completed producers into the checkout and publishes them
while the remaining print build continues.

## What the build preserves

The machine is the same when the site shows the same things and the same solids
print within the [kernel's rule](../kernel/src/rule.rs). Keep fabrication order
files generatable on demand. An output, check, report or costly site detail that
serves none of these can go.

The print build is the normal build for parts made here on the H2C and Mark2.
For orders, the cut build makes DXFs and drawings for SendCutSend and the PCB
build makes Gerbers, the parts list and the placement file for JLCPCB. Keep both
available on demand outside the normal build. Bought parts have no manufacturing
build. The website's model shows every part.

## Publishing a changed part

[Find the affected targets](../README.md#find-and-inspect-a-part). Include the
assembly when installation or membership changes. For enclosure geometry, take
the [before snapshot](../../../changes/README.md#recording-a-change) before rebuilding.

```sh
tools/run -- hsm-print-build --
tools/run -- hsm-print-build -- //:enclosure-back-top //:installed-machine
```

Share the first published part while the other targets and focused review continue.
Tell Derek what he can see, what geometry has been checked and what is ready to print.
After publishing a changed printed solid, [lint its STL](../mesh-review/README.md).
Fix the defect wherever it recurs or [record an anchored answer](../../../hardware/printed-parts/lint-answers/AGENTS.md).
Record an enclosure change from its before snapshot.

## Producer execution

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
