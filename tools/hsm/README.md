# hsm

`hsm` answers geometry questions from the same version 3 triangle payloads that `/3d` displays.
One local Rust daemon serves the CLI, an MCP server and a Unix socket. Queries load a scene on
demand. A saved edit starts no build, query, watcher or check.

Build and install with Rust 1.89 or later, CMake and a C++17 compiler:

```sh
cargo install --path tools/hsm/engine --locked
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

The first CLI or MCP query starts the daemon. It survives its caller and is shared by all
worktrees for that user. A changed executable replaces the previous daemon on the next query.
The default socket is `/tmp/hsm-<uid>/engine.sock`, in a private directory. `--socket` or
`HSM_SOCKET` selects another service. `hsm daemon` runs it in the foreground.

Geometry is addressed by the payload digest and a digest of the geometry reader and dependency
lock. Serialized BVHs persist across restarts in `$XDG_CACHE_HOME/hsm`, `~/Library/Caches/hsm`
on macOS, or `~/.cache/hsm` on Linux. `--store` or `HSM_STORE` selects a shared store. Unchanged
files reuse resident geometry by device, inode, size, mtime and ctime. Replaced payloads reload
on the next request. Two worktrees holding identical bytes share one resident entry.

The daemon executes queries serially. `--cache-mb` sets a conservative resident cache budget
(default 768 MiB); least recently used scenes are evicted to make room. The estimate includes
lazy solid copies, but is not a hard process memory limit. Geometry query scratch can consume
additional memory. The store's `daemon.log` records startup and cache-write errors.

## MCP and socket

Configure an MCP client to launch the installed executable with the repository root:

```json
{
  "mcpServers": {
    "hsm": {
      "command": "hsm",
      "args": ["--root", "/absolute/path/to/homesodamachine", "mcp"]
    }
  }
}
```

The tools are `hsm_where`, `hsm_gap`, `hsm_overlap`, `hsm_move`, `hsm_section` and `hsm_ray`.
Each accepts an optional `root` and `scene`, so one MCP server can query several worktrees.
MCP uses newline-delimited JSON-RPC over stdio; diagnostic output never enters that stream.

The socket uses one newline-terminated JSON request and response per connection:

```json
{"scene":"/absolute/path/enclosure-assembly.step.mesh","op":"gap","a":"compressor/1","b":"condenser+fan"}
```

The response has `ok`, `elapsed_ms`, and either `result` or `error`. A CLI caller can send the
same request with `hsm request '<json>'`. A failed query exits with status 1. `status`, `ping`
and `shutdown` need no scene. The web viewer does not yet subscribe to this service.

## Explicit validation

```sh
cargo test --release --manifest-path tools/hsm/Cargo.toml
python3 -m unittest discover -s tools -p test_publish_manifest.py
```

These run only when requested. They do not join any build, edit or commit path. The kernel's
analytic profiles, exact booleans, native/browser equivalence, Rust part generators, renderers
and drawing writers are separate work from this payload query service.
