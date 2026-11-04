# Build plan

`build-plan` owns generator grouping, action inputs, dependency rules and BUILD
rendering. `tools/bazel/gen_build.py` preserves its import and command interface;
its graph-projection command uses the smaller `build-data` support service.

The maintained implementation is the compiled Rust module
`src/compiled/modules/gen_build.rs`. Its loops, branches and calculations execute
in Rust. `src/compiled.rs` supplies native values, scopes and explicit library
callbacks; it does not parse or evaluate Python source.

The `build-data-runtime` filegroup declares the support service's compiled
sources, Cargo manifests and Python/runtime boundaries. Each generator action
retains its own declared source and output set.

The [conversion record](../conversion-results/build-final-2026-11-04.json)
includes the fixed-input whole-renderer comparison and combined-build result.
