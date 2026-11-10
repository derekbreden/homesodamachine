# Print build

`hsm-print-build` carries completed producers into the checkout and publishes them
while the remaining print build continues.

```sh
tools/run -- hsm-print-build
tools/run -- hsm-print-build //:enclosure-back-top //:installed-machine
```

The driver reads Bazel's build events and each producer's progress checkpoints.
The first completed view is independent of later producers. Publication runs as
`hsm-publish --root ROOT`; concurrent requests coalesce behind the active publisher.
The driver waits for the last publication before returning. A failed build keeps
its exit status, and a publication failure makes an otherwise successful run fail.

Placement-only changes can publish an early scene using the retained installed
machine program. A status-only checkpoint keeps the completed scene's identity.
File replacement is atomic, so a reader sees a complete retained file or its
complete replacement.

PCB models retain their raw GLBs and textures. Shared meshes replace raw GLBs
inside `hardware/assembly/scenes/glb/`.

`--root`, `--run-dir`, `--runner`, `--bazel`, `--publisher` and `--progress` select
explicit paths for another checkout or an isolated fixture. Bazel arguments can
follow `--`. The default run directory contains per-publication logs and a concise
result; the shared progress file retains the producer stream used by the viewer.

Focused driver fixtures run on request:

```sh
tools/run -- cargo test --release --locked -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-build
```
