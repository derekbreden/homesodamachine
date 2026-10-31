# hsm

`hsm` answers geometry questions from the same version 3 triangle payloads that `/3d` displays,
and draws pictures of them. One local Rust daemon serves the CLI, an MCP server and a Unix socket. Queries load a scene on
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

## Render

`hsm render` draws a payload as `/3d` draws it: the viewer's colours, `web/public/finishes.json`,
its studio light, x-ray, contact shadow and fog. The daemon draws with wgpu, on Metal here, and
starts no browser, server or STEP reader. Its device, pipelines and last scenes stay warm, so a
picture of the whole machine takes a fresh daemon about three seconds and a warm one about a
tenth of that.

```sh
hsm render manifold-layout/enclosure-assembly.step /tmp/machine.png
hsm render manifold-layout/enclosure-assembly.step /tmp/valve.png --highlight valve-v-a --xray '*'
hsm render manifold-layout/enclosure-assembly.step /tmp/cut.png --section=-81,343,315:1,-1,1
hsm render manifold-layout/enclosure-assembly.step /tmp/compressor.png --only compressor --look --views top,front
hsm render manifold-layout/enclosure-assembly.step --list
hsm render --jobs jobs.json --json
```

The camera looks at the framed box from `1,-1,1` with +Z up unless `--view`, `--cam`, `--up`,
`--target`, `--zoom`, `--span` or `--distance` says otherwise, and `--orbit` sweeps it. Bodies
are named by comma-separated `*` globs: `--only` keeps a subject and hands the rest to
`--context`, and `--xray`, `--ghost`, `--shell`, `--hide`, `--highlight` and `--select` each give
a set its look. `--clip` and `--section` cut, and the cut is filled flat. `--look` is
`tools/look.sh`'s frame, a hue per body with a legend, labels, grid and scale bar; `--pick`,
`--ray` and `--gap` measure in the picture and print what they found. `hsm render --help` lists
every option.

Lines run along B-rep face boundaries, from the face ranges in the payload, and along the viewer's
30° crease where a mesh states no faces. A `--jobs` file is an array of jobs whose keys are the
flags' names; a key a job leaves out takes the flag's value. Each picture is one request to the
daemon, so a long list never holds up a geometry query. `--json` gives each picture's report: the
camera with its view-projection, the bodies in each role, and the milliseconds each stage took.
The scenes kept warm hold up to 1 GiB between them, CPU and GPU; the least recently drawn goes
first.

[`tools/look.sh`](../look.sh), [`tools/changes/change.mjs`](../changes/change.mjs) and the guide
art scripts, by way of [`hardware/scripts/_hsm_render.py`](../../hardware/scripts/_hsm_render.py),
draw with it. The Bazel art rules, and the installation scenes that bring their own three.js
materials, draw with [`tools/render/render-step-posed.js`](../render/render-step-posed.js).

## Kernel

`hsm-kernel` (`tools/hsm/kernel`) builds solids as closed triangle meshes that record where
every face came from. Each triangle names a face record: the exact surface it lies on (plane,
cylinder, cone, sphere, torus, or a free surface), the builder that made it, the generator line
that called the builder (`#[track_caller]`) or the file it was read from, and the boolean that
brought it into the solid. A file names that line `path:line` from the checkout's root, as
meshcad does, so a part writes the same records from every worktree.

Profiles are drawn exactly with lines, arcs, circles, Béziers, corner fillets, offsets and the
hull round circles and points (`Loop`, `Pen`, `Profile`; `hull_loop` is CadQuery's
`Sketch.hull`) on a workplane (`Plane`) named as CadQuery names them. The builders
extrude (straight, both ways, drafted), revolve, sweep along lines and arcs or along a helix
(carried rigidly by the screw motion, or in a rotation-minimizing frame), loft sections ruled
or through OCCT's own smooth surface (`Solid::thru_sections`, CadQuery's `loft`),
set text from a font's outlines, and make boxes, cylinders, cones, spheres, tori, wedges and
hulls. All of them cut curves into points by one rule (0.005 mm chord, 0.05 rad, ring counts a
multiple of 8 from a canonical seam), so a surface gets the same vertices from any builder and
coincident faces meet point for point.

Union, cut, intersect and plane split run on Manifold. Each operand face goes in as a run of its
own, so the result keeps every face record. Coordinates of different operands within 10⁻⁸ mm
are one coordinate, and a component thinner than the rule is dropped. Volume, area, centroid,
inertia and bounds come from the mesh. The writers make binary STL, 3MF, GLB (face records in
its extras), the `.step.mesh` payload `hsm` reads, and the STEP meshcad writes: AP242
triangulated surface sets under each body's name and colour, with the model file a mesh-kernel
import reads beside it (`<name>.step.npz`). The same solid writes the same bytes on every run.
Without the `manifold` feature the kernel is pure Rust and builds for wasm32; its booleans
then return an error.

Bodies come back in from payloads (`import`). `import::payload(path)` reads every body of a
`.step.mesh`. `import::step(path)` reads a STEP's bodies through a payload cut from it. A STEP of
B-rep faces is read through `.cache/hsm/import/<SHA-256>.step.mesh` at the checkout's root,
OCCT's mesh of it at the kernel's rule, which `_rust_part.step` cuts. A STEP of triangles is
read through the payload its writer cut beside it, whose `src` is the STEP's SHA-256. Each body
is an `Imported` (`name`, `color`, `solid`). The solids a payload numbers
`name/1`, `name/2`, … come back as one body under its name, and `import::body(&bodies, name)`
picks one out. A payload holds no surfaces, so every face read is a free `MESH` record whose
source is the file asked for: `MESH import at hardware/reference/tee-connector/tee-connector.step`.
`Solid::from_mesh` makes a solid of any closed mesh. Corners at one point of the grid are one
vertex, and a mesh left open or folded is an error.

The kernel's tests hold every builder and boolean to OCCT's volume and bounds for the same model
within the rule (`tests/occt_reference.py` and, for the helix sweeps and lofts,
`tests/screw_reference.py` and `tests/thru_reference.py` write those with plain CadQuery), lofts
to every point sampled on OCCT's faces within the rule, hulls to the edges of CadQuery's
(`tests/sketch_hull_reference.py`), and booleans to Manifold run plainly on the same operands,
sixty holes in one cut among them. They hold the fuse clamp, cut from its numbers, to the
volume of its module's `build()` and to that B-rep's STL (`tests/fixtures/fuse-clamp.stl`), two
processes to the same bytes, a STEP and a model file to the triangles, names and colours they
were written from, and the crate to a wasm32 build. The text tests read the system's Arial and
Helvetica.

## Parts the kernel cuts

A part the kernel cuts keeps its numbers in Python and its geometry in Rust, side by side in its
folder. The fuse clamp (`hardware/printed-parts/refrigeration/fuse-clamp`) is one. The coil
mandrel and the magnetic float (`hardware/printed-parts/cold-core/coil-mandrel` and
`magnetic-float`, crate `tools/hsm/cold-core`) are two more.

`fuse_clamp.py` is its generator. It derives every number the part takes from the parts it
closes on, states its bounds and fills its README, as any generator does, and writes the numbers
the geometry takes (`numbers()`) to `fuse-clamp.numbers.json`, which is committed beside it.
`fuse_clamp.rs` is the program that cuts the part from them: a `[[bin]]` of its subsystem's crate,
`tools/hsm/refrigeration`, named `fuse-clamp`. It reads the file with `part::args` and
`Numbers` (`f`, `pair`, `list`, `color`, `text`), builds the solid, and hands its bodies to
`part::write_part`. That writes `fuse-clamp.step`, the model file beside it, the payload, whose
`src` is the STEP's SHA-256, and `fuse-clamp.stl`; leaves a file that holds the same bytes as it
is; and prints what the files hold. `part::write_shown` writes a set without the STL, for bodies
the page draws and nothing prints. A program that writes several sets prints each one's answer
on a line of its own, and its standard output carries nothing else. The magnetic float's program
writes seven: a set with an STL for each printed piece, and a set without one for the magnet and
for the assembly, section and exploded views.

The generator runs the program through
[`hardware/scripts/_rust_part.py`](../../hardware/scripts/_rust_part.py).
`_rust_part.cut("refrigeration", "fuse-clamp", numbers(), part_dir)` writes the numbers, builds
the program with cargo from the checkout's workspace (`HSM_WORKSPACE` in a Bazel action), runs
it, and returns the files and bodies it printed. `_rust_part.program(crate, name)` builds a
program and returns its path, for a run with arguments of its own: the float's `verify.py`
runs its program with `--check` for the volumes by which the pieces miss the design. Cargo
builds into the checkout's own target directory, `tools/hsm/target`, whatever
`CARGO_TARGET_DIR` says. The `cargo` it runs is the one on `PATH`, else Homebrew's rustup's,
else the one in `~/.cargo/bin`.

A program runs from the checkout's root, and its numbers name a STEP it reads by its path from
there. `_rust_part.step(path)` returns that path once a payload cut from the STEP is on disk. For
a STEP of B-rep faces with none in the import cache, OCCT meshes each solid of each body at the
kernel's rule, one face range per B-rep face, into the cache, under the CAD lock. `_rust_part`
hands the trace the STEP, and for a STEP of triangles the payload beside it.

`tools/bazel/trace_inputs.py` takes what rustc compiled into the program, off its dep-info file,
with the manifests and the lockfile, and every file the program wrote. The writer's entry in
`graph.json` names the Rust sources among its reads, so a publish moves the part's members when
its program or the kernel changes. `gen_build.py` runs a step that read a `Cargo.toml`
unsandboxed, in a work directory of its own, because cargo writes the checkout's target directory.
The page cannot read a STEP of triangles (occt-import-js 0.0.23), so the part's folder is in
`BUNDLED_PAYLOAD_DIRS` in [`tools/cad-artifacts/pack.py`](../cad-artifacts/pack.py), and in
`BUNDLED_MESH_DIRS` for its STL. The CI image ([`tools/ci-image/Dockerfile`](../ci-image/Dockerfile))
carries the toolchain and CMake.

A generator on meshcad seats the part off its STEP, whose solids an import takes from the model
file. `import_step` refuses that STEP on OCCT, so an OCCT generator that seats the part calls a
CadQuery `build()` in its module instead: the fuse clamp keeps one for `enclosure_assembly`.

```sh
tools/cad-venv/bin/python hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py
hsm --scene hardware/printed-parts/refrigeration/fuse-clamp/fuse-clamp.step.mesh where fuse-clamp
```

Its face records read `PLANE extrude at hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs:41`
and `PLANE box at hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs:42, cut at
hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs:43`.

## Explicit validation

```sh
cargo test --release --manifest-path tools/hsm/Cargo.toml
python3 -m unittest discover -s tools -p test_publish_manifest.py
```

These run only when requested. They do not join any build, edit or commit path.
