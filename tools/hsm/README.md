# hsm

`hsm` answers geometry questions from the same version 3 triangle payloads that `/3d` displays.
One local Rust daemon serves the CLI, an MCP server and a Unix socket. Queries load a scene on
demand. A saved edit starts no build, query, watcher or check.

Build and install with Rust 1.89 or later, CMake and a C++17 compiler. `--root ~/.local` puts
`hsm` in `~/.local/bin`, which this Mac's shells have on `PATH`:

```sh
cargo install --path tools/hsm/engine --locked --root ~/.local
hsm where tee-y-a
hsm gap compressor/1 condenser+fan
hsm overlap '#6' '#7'
hsm move tee-y-a --by 0 -17 0
hsm section tee-y-a --normal 0 0 1 --offset 250
hsm ray --origin 0 0 1000 --direction 0 0 -1
hsm --scene faucet where shell
hsm --scene enclosure where enclosure_front
hsm status
hsm stop
```

Run commands within the checkout or supply `--root /absolute/worktree`. `--scene` accepts
`machine` (the complete enclosure assembly), `faucet`, `enclosure`, or a payload path relative
to that root. A `.step` path resolves to its `.step.mesh` sibling; no STEP reader is started.

A checkout without the payload a query asks for, such as a fresh worktree, takes the one
[`hardware/cad-artifacts.json`](../../hardware/cad-artifacts.json) names: the main checkout's
copy when it holds those bytes, cloned, or else the published object from the store. Either is
held to the pointer's SHA-256 before it is renamed into place. A payload on disk is never
replaced, and nothing is built.

Names match case insensitively, with exact names preferred over substrings. `where` lists all
matches. Pair queries require one solid for each selector and explain an ambiguous selection.
`#index` identifies a solid within a specific payload digest; indices can change when a scene
is regenerated. `move` reports intersection volumes after the proposed translation and leaves
the original scene intact. Conversion failures appear in its `unknown` list.
`move --min-volume` selects the smallest reported penetration in mm³ (default `1e-6`);
the response states that threshold.

All coordinates are the payload's world frame, lengths are mm and volumes are mm³. Replies
carry the payload SHA-256, the recorded STEP digest, any recorded mesh reduction budget, load
time and total service time. Geometry queries describe the mesh on disk. A source edit reaches
them when its producer exports a new payload.

## Geometry

`hsm-geometry` decodes viewer arrays without retessellation or simplification and builds a
Parry bounding-volume tree. Distance, rays and triangle-plane sections use that tree. Ray hits
and section segments keep viewer triangle and face IDs. Sections are raw triangle segments
with coplanar triangles reported separately; they are not joined drawing outlines.

Intersection volumes use the Manifold C++ backend through `manifold-csg`. Coincident seam
vertices are joined before solid validation. Invalid solids return an error. These are
floating-point booleans; very small reported volumes can be numerical residue at a contact.
The service does not implement an exact boolean kernel.

`gap` reports both triangle surface distance and solid clearance. A body completely contained
in another can have positive surface distance and zero clearance. When overlapping bounds
require a solid query but conversion fails, clearance is unknown and the surface distance is
still available. Mesh results carry the original tessellation limits; they do not recover
analytic surfaces or source lines.

## Process and cache

The first CLI or MCP query starts the daemon. It survives its caller, is shared by all
worktrees for that user, and exits after 15 minutes without a query; `--idle-minutes` sets
that, and 0 keeps it running. A changed executable replaces the previous daemon on the next
query. The default socket is `/tmp/hsm-<uid>/engine.sock`, in a private directory. `--socket`
or `HSM_SOCKET` selects another service. `hsm daemon` runs it in the foreground.

Geometry lives only in the daemon's memory, addressed by the payload digest. Unchanged files
reuse resident geometry by device, inode, size, mtime and ctime. Replaced payloads reload on
the next request. Two worktrees holding identical bytes share one resident entry.

The daemon executes queries serially. `--cache-mb` sets a conservative resident cache budget
(default 768 MiB); least recently used scenes are evicted to make room. The estimate includes
lazy solid copies, but is not a hard process memory limit. Geometry query scratch can consume
additional memory. `daemon.log` in the store directory (`--store` or `HSM_STORE`; otherwise
`$XDG_CACHE_HOME/hsm`, `~/Library/Caches/hsm` on macOS, or `~/.cache/hsm` on Linux) records
startup errors and idle exits.

## MCP and socket

The tools are `hsm_where`, `hsm_gap`, `hsm_overlap`, `hsm_move`, `hsm_section` and `hsm_ray`.
`hsm mcp` serves them over newline-delimited JSON-RPC on stdio; diagnostic output never enters
that stream. The server holds no geometry and starts no daemon until a tool is called. Each
tool accepts an optional `root` and `scene`, so one server can query several worktrees. Without
`root`, a call measures the checkout the server started in, which its instructions name.

Claude Code reads [`.mcp.json`](../../.mcp.json), which runs `hsm mcp`, and
[`.claude/settings.json`](../../.claude/settings.json) enables that server and allows its tools.
A session starts its server in the session's directory, so a session in a worktree made by
`tools/worktree.py` measures that worktree. `claude mcp get hsm` shows the server.

Codex takes its servers from `~/.codex/config.toml`:

```toml
[mcp_servers.hsm]
command = "/Users/derekbredensteiner/.local/bin/hsm"
args = ["mcp"]
tool_timeout_sec = 600
```

Codex names the turn's git workspaces in each call's `_meta`, and a call without `root`
measures the turn's workspace when it names one other than the server's checkout.
`tool_timeout_sec` leaves a cold scene and a payload fetch time to finish. `codex mcp list`
shows the server.

The socket uses one newline-terminated JSON request and response per connection:

```json
{"scene":"/absolute/path/enclosure-assembly.step.mesh","op":"gap","a":"compressor/1","b":"condenser+fan"}
```

The response has `ok`, `elapsed_ms`, and either `result` or `error`. A CLI caller can send the
same request with `hsm request '<json>'`. A failed query exits with status 1. `status`, `ping`
and `shutdown` need no scene.

## The local viewer

Off Render, the site's server (`npm start` in `web`) answers `/api/hsm` with the `hsm` on its
`PATH`, or `HSM_BIN` ([`web/lib/hsm.js`](../../web/lib/hsm.js)), and `/3d` uses it
([`web/public/js/viewer/hsm.js`](../../web/public/js/viewer/hsm.js)):

- Once a second while a model is open and the page is visible, the page asks again for the
  file it drew, under the ETag it came with. The server answers off a stat, and a new ETag that
  holds for another second redraws the model in place, camera kept. Nothing watches a file, so
  a payload redraws however it was written: by its producer, `sync_tree.py` or
  `fetch-cad-artifacts`.
- With **Measure** on in the component panel, a picked body shows its payload index and world
  bounds, and its clearance to the body picked before it, with the closest points drawn.

The deployed site answers `/api/hsm` with a 404, and its viewer does neither.

## Kernel

`hsm-kernel` (`tools/hsm/kernel`) builds solids as closed triangle meshes that record where
every face came from. Each triangle names a face record: the exact surface it lies on (plane,
cylinder, cone, sphere, torus, or a free surface), the builder that made it, the generator line
that called the builder (`#[track_caller]`), and the boolean that brought it into the solid.

Profiles are drawn exactly with lines, arcs, circles, Béziers, corner fillets and offsets
(`Loop`, `Pen`, `Profile`) on a workplane (`Plane`) named as CadQuery names them. The builders
extrude (straight, both ways, drafted), revolve, sweep along lines and arcs, loft ruled sections,
set text from a font's outlines, and make boxes, cylinders, cones, spheres, tori, wedges and
hulls. All of them cut curves into points by one rule (0.005 mm chord, 0.05 rad, ring counts a
multiple of 8 from a canonical seam), so a surface gets the same vertices from any builder and
coincident faces meet point for point.

Union, cut, intersect and plane split run on Manifold. Each operand face goes in as a run of its
own, so the result keeps every face record. Coordinates of different operands within 10⁻⁸ mm
are one coordinate, and a component thinner than the rule is dropped. Volume, area, centroid,
inertia and bounds come from the mesh. The writers make binary STL, 3MF, GLB (face records in
its extras) and the `.step.mesh` payload `hsm` reads, the same bytes for the same solid on every
run. Without the `manifold` feature the kernel is pure Rust and builds for wasm32; its booleans
then return an error.

`examples/fuse_clamp.rs` is the fuse clamp on the kernel:

```rust
let part = Plane::YZ.at(v3(-PART_X / 2.0, 0.0, 0.0)).extrude(&Profile::polygon(&profile()), PART_X)?;
let channel = Plane::XY.at(v3(0.0, 0.0, CHANNEL_Z / 2.0)).cuboid(PART_X + 2.0, CHANNEL_H, CHANNEL_Z);
let clamp = part.cut(&channel)?;
let body = Body { name: "fuse-clamp", color: Some([0.02, 0.02, 0.02]), solid: &clamp };
write_payload(out.join("fuse-clamp.step.mesh"), &[body], None, None)?;
```

```sh
cargo run --release --manifest-path tools/hsm/Cargo.toml -p hsm-kernel --example fuse_clamp -- <out dir>
hsm --root <out dir> --scene fuse-clamp.step.mesh where fuse-clamp
```

Its face records read `PLANE extrude at kernel/examples/fuse_clamp.rs:60` and `PLANE box at
kernel/examples/fuse_clamp.rs:61, cut at kernel/examples/fuse_clamp.rs:62`.

The kernel's tests hold every builder and boolean to OCCT's volume and bounds for the same model
within the rule (`tests/occt_reference.py` writes those with plain CadQuery), and booleans to
Manifold run plainly on the same operands, sixty holes in one cut among them. They hold the fuse
clamp to its published STEP's volume and STL's surface, two processes to the same bytes, and the
crate to a wasm32 build. The text tests read the system's Arial and Helvetica.

## Explicit validation

```sh
cargo test --release --manifest-path tools/hsm/Cargo.toml
python3 -m unittest discover -s tools -p test_publish_manifest.py
```

These run only when requested. They do not join any build, edit or commit path.
