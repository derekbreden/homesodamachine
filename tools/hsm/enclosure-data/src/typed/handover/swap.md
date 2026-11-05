# The final swap (orchestrator's checklist)

Once every module is typed and passes in the hybrid build:

1. `main.rs`: `mod compiled;` becomes `mod typed;`; the `op == "compiled"` branch calls
   `typed::rt::request(v)` and `typed::rt::register_io()?` (the op name is the boundary with
   `hardware/scripts/_rust_data.py`: it stays).
2. `nameplate_snap.rs`: `use hsm_documents::interop::Val;` and `numbers(numbers: Val, wing: &Val)`
   (the one `Env` use is `e.get("wing")`); `typed/nameplate.rs` calls it with the wing interface module.
3. `typed/`: drop every `#[cfg(feature = "hybrid")]` item (`import_generated`, `generated_base`,
   `adopting`, `Cx::generated`, `State::from_ns`, the fallback bodies) and every
   `#[cfg(not(feature = "hybrid"))]` attribute; the `TYPED` consts and `modules.rs`' generated entries go.
4. Delete `src/compiled.rs` and `src/compiled/` (44 files).
5. `BUILD.bazel` / `tools/bazel/graph.json`: the crate's source list names `src/typed/**` in place of
   `src/compiled*` (render BUILD.bazel from graph.json with `render_build()`).
6. Build at the crate's real profile (HEAD: opt-level 3, debug 1) as `bin/enclosure-data.final`;
   the baseline at the same profile is `bin/enclosure-data.base3` (`aws/base3`, HEAD's crate).
7. A/B every rule: baseline and final interleaved, labels of equal length, extended hashing
   (`batch.tree(work, extended=True)`); keep both trees of a rule that differs.
8. Measure: median CPU of 3 warm runs (`--timing`), wall, peak RSS: enclosure-dimensions,
   enclosure-box, cold-core-sync, enclosure, enclosure-assembly, install-guide-build; the recompile CPU
   after a one-line edit in the largest typed file; then the crate's profile lines in tools/hsm/Cargo.toml.
9. Record (`tools/hsm/conversion-results/typed-enclosure-data-2026-11-04.json`), conversion.md, commit
   path-scoped, push; clean `$R`.
