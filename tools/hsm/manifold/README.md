# Boolean engine

`hsm-manifold` supplies the Rust Manifold engine to construction, print finalization
and geometry queries. Mesh conversion retains the caller's precision, operand runs
and construction identities. Immutable results share their retained topology.

Batch operations use the port's CSG tree to group independent operands. Ordinary
booleans use its strict manifold engine; invalid operands return an error. The
kernel owns its coordinate agreement, surface records and fabrication rule.

The enclosure's retained-stage identity includes this crate's source and locked
dependencies. The geometry daemon's build identity includes this boundary too.

The upstream implementation is
[`manifold-rust`](https://github.com/larsbrubaker/manifold-rust).
The [pinned source](../../../vendor/manifold-rust/README.hsm.md) inlines its hot
intersection helpers into their callers. Its compiled source fingerprint binds
the geometry daemon and retained enclosure stages to that implementation.
