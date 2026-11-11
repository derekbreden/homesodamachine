# Boolean engine

`hsm-manifold` supplies the Rust Manifold engine to construction, print finalization
and geometry queries. Mesh conversion retains the caller's precision, operand runs
and construction identities. Immutable results share their retained topology.

Batch operations use the port's CSG tree to group independent operands. Ordinary
booleans use its strict manifold engine; invalid operands return an error. The
kernel owns its coordinate agreement, surface records and fabrication rule.

The enclosure's retained-stage identity includes this crate's source and locked
dependencies. The geometry daemon's build identity includes this boundary too.

Cargo resolves the published [`manifold-rust`](https://crates.io/crates/manifold-rust)
crate. The workspace lockfile pins its source and checksum for builds and cache identities.
