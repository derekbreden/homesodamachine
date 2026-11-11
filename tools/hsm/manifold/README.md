# Boolean engine

`hsm-manifold` supplies Manifold to construction, print finalization and geometry
queries. Mesh conversion retains the caller's precision, operand runs and
construction identities. Immutable results share their retained topology.

Native builds use the C++ engine through [`manifold-csg`](https://crates.io/crates/manifold-csg).
WebAssembly builds use [`manifold-rust`](https://crates.io/crates/manifold-rust).
Batch operations group independent operands, and invalid operands return an
error. The kernel owns its coordinate agreement, surface records and fabrication
rule.

The enclosure's retained-stage identity includes this crate's source and locked
dependencies. The geometry daemon's build identity includes this boundary too.

Cargo resolves the published crates. The workspace lockfile pins their sources and
checksums for builds and cache identities.
