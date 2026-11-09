# hsm

`hsm` answers geometry questions from the same triangle payloads and shared mesh references that `/3d` displays,
and draws pictures of them. One local Rust daemon serves the CLI, an MCP server and a Unix socket. Queries load a scene on
demand. A saved edit starts no build, query, watcher or check.

Build and install with Rust 1.89 or later, CMake and a C++17 compiler. The installer keeps each
build at an immutable path under `~/.local/lib/hsm/<build_id>/hsm` and puts a launcher at
`~/.local/bin/hsm`, which this Mac's shells have on `PATH`:

```sh
python3 tools/run.py -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm --bin hsm
python3 tools/hsm/install.py tools/hsm/target/release/hsm
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

## Find and inspect a part

`node tools/find-part.mjs "water regulator"` uses the material search that serves `/3d`.
Descriptions, aliases, brands and part numbers return the same ordered candidates locally
and in the browser. A spelling or incomplete-word suggestion is labeled; it does not rename
the part or turn different components into synonyms. An exact material ID selects its identity.
The local result adds source producers, declared build targets, part documents and assembly
body bindings from the catalog and build graph. `--json` retains those details for another tool.

An on-demand inspection draws the existing exported geometry and keeps its camera:

```sh
node tools/inspect-part.mjs HSM-0082 --output .cache/runs/pump-fit/before
node tools/inspect-part.mjs HSM-0082 --output .cache/runs/pump-fit/after \
    --reuse .cache/runs/pump-fit/before/render-job.json
```

`--model` selects an existing assembly and `--body` selects its subject. `--against` measures
clearance to a named neighbour in that same assembly and draws that neighbour in x-ray;
unselected bodies are omitted. `--section` opens a section view.
Ambiguous searches return candidates for explicit selection. The inspection starts no build;
its image, measurements and source metadata bind to the exported payload digest. The renderer
runs through the shared scheduler, and the elapsed time includes admission waits.
Remove inspection images and intermediate records when the question is answered, retaining
concise results and artifact hashes.

Build the selected targets through the [print build](../../hardware/printed-parts/AGENTS.md#publish-loop).
Its completed producers reach the site while other work continues.
[`tools/iteration/`](../iteration/README.md) measures an actual request from its original receipt
through source edits, review attempts and reference-browser draws when a timing is requested.

## Construction features and installed instances

In `/3d`, selecting an enclosure quadrant selects the whole part. **Explore features** enables
surface picking within that part. Click a feature in the model to select it. Selecting the
parent returns to the whole component; **Select whole components** leaves feature picking.
Material search also finds these features and lists the individual installed instances of a
repeated component. A feature's **Copy feature link** action retains its installed owner.

The browser and local tools use the identities in the same exported payload:

```sh
hsm features enclosure-back-top
hsm where enclosure-back-top::relay-2-mount
hsm gap enclosure-back-top::water-regulator-receiver flow-regulator
node tools/find-part.mjs "relay mount" --json
node tools/inspect-part.mjs enclosure-back-top::wago-h-well --output .cache/runs/well-inspection
```

A feature inspection frames and clips its containing part around the measured feature bounds,
using a neutral surface color to make the local construction readable. Its image labels the
open clipping planes; nearby owner surfaces can remain inside the crop. The saved job retains
that camera and presentation for another attempt.

`body::feature` identifies authored surfaces of an installed body. Feature bounds, ray hits,
sections and surface distances use its existing triangle ranges and owner placement. Triangle
references retain their original viewer indices. A feature has no independent closed solid:
feature distance replies set `surface_only`, and volume queries require the containing part.
The replies retain the payload revision, so an unbuilt source edit cannot masquerade as a new
measurement. `hsm_features` exposes the same catalog through MCP; an already-open MCP session
needs to reconnect to discover an added tool.

The enclosure producer names stock and cut tools beside their construction with `Graph::feature`
or `Graph::scoped`. IDs describe their purpose and installed role rather than a face index or
list position. A scope names the primitives it constructs; it does not rename its incoming
whole part. Existing boolean, transform, retained-model and print conversion work carries the
identity. Viewer payloads store membership beside their existing triangles; no feature mesh or
separate manufacturing export is produced. Unnamed shell and finish surfaces remain selectable
as part of their owner. Mesh reduction drops feature metadata when it cannot retain membership;
the enclosure quadrant payloads preserve their print surfaces.

Feature lookup and inspection run on demand. The explicit `HSM_FEATURES_OFF` comparison switch
omits identity bookkeeping in enclosure generators; it is for manual production-cost measurements,
not publication. It adds no automatic benchmark or validation step.

## Geometry

`hsm-geometry` decodes viewer arrays without retessellation or simplification and builds a
Parry bounding-volume tree for geometric queries. `where` resolves names from the scene header
and scans matching position arrays for bounds without allocating that tree. Shared-scene
results also name each instance's source payload, source body, immutable asset and placement.
Selected gap, overlap, section and moves with an explicit `--against` decode only their selected
entries, retaining the original scene digest and global indices. `selected_triangles` describes
a lookup's selected geometry; `scene_triangles` is unknown for a subset. Broad rays and moves
against the entire machine use the full-scene geometry cache.

Distance, rays and triangle-plane sections use the tree. Ray hits
and section segments keep viewer triangle and face IDs. Sections are raw triangle segments
with coplanar triangles reported separately; they are not joined drawing outlines.
When a payload has aligned `face_sources`, each ray hit or section segment also reports that
face's complete contributor group. Missing or malformed metadata leaves attribution unknown.
Renderer pixel picks and ray annotations retain the actual mesh, triangle and face IDs, and
report the same contributors together with the payload digest. Body-centre labels and dimension
leaders without an authored feature binding have no source attribution.

A kernel mesh-validation failure identifies the failed edge in mesh-local coordinates and
prints incident triangles with their recorded source contributors. The diagnostic is produced
only on failure. Print-surface attribution identifies the calling print stage; unrecorded
upstream ownership remains unknown.

Intersection volumes use the Manifold C++ backend through `manifold-csg`. Coincident seam
vertices are joined before solid validation. Invalid solids return an error. These are
floating-point booleans; very small reported volumes can be numerical residue at a contact.
The service does not implement an exact boolean kernel.

`gap` reports both triangle surface distance and solid clearance. A body completely contained
in another can have positive surface distance and zero clearance. When overlapping bounds
require a solid query but conversion fails, clearance is unknown and the surface distance is
still available. Mesh results carry the original tessellation limits; they do not recover
analytic surfaces or infer missing source lines.

## Process and cache

The first CLI or MCP query starts the daemon. It survives its caller, is shared by all
worktrees for that user, and exits after 15 minutes without a query; `--idle-minutes` sets
that, and 0 keeps it running. The default socket `/tmp/hsm-<uid>/engine-<digest>.sock` names
the actual build and daemon configuration: cache, build and kept-run budgets, and the resolved
store directory. Root and scene remain per request. A long-lived MCP keeps its build's resolved executable path, so after an
update its idle restart still starts that build. `build_id` always names the source of the
process answering. `hsm endpoint` reports the installed build, socket and executable without
starting a daemon. Ping and status report the answering daemon's configuration. `--socket` or
`HSM_SOCKET` selects another service; a live daemon of another build or configuration is left
running and the caller gets an error. `--idle-minutes` configures a daemon this call starts.
`hsm daemon` runs it in the foreground.

The installed CLI and new MCP connections use the installed build. An already-open MCP server
retains its resolved executable. Use the installed CLI when that connection still reports an
older reader or whole-scene cache refusal; reconnecting the MCP server adopts the installed build.

The installer's launcher also retains the executable that earlier MCP clients restart on
`/tmp/hsm-<uid>/engine.sock`. Only a `daemon` invocation for that endpoint takes the retained
executable; ordinary commands use the installed build. `install.py --legacy-socket PATH`
retains additional endpoints for clients started with a custom socket. Its `--root` selects an
installation other than `~/.local`. Every daemon loads geometry only when asked for a scene.

Scene payloads can hold references to immutable mesh objects and their instance placements.
The cache in `.cache/meshes/scene-assets` retains these objects; missing objects are restored
from the published store by content hash. Assemblies and named views share the same surfaces.
Native archives supply construction and print preparation. A scene without a standalone STEP
reports its source digest without claiming it is a STEP digest.

Assemblies retain the source inventory and placement of each complete import. A completed
source reconciles added, renamed and removed bodies through those imports. Named views keep
their authored body selections. A new source gets its placement from the assembly definition;
the print build publishes those references when the assembly producer finishes.

Decoded query geometry lives in the daemon's memory, addressed by the payload digest. Unchanged files
reuse resident geometry by device, inode, size, mtime and ctime. Replaced payloads reload on
the next request. Two worktrees holding identical bytes share one resident entry.

The daemon executes geometry queries serially; a part run is answered on a thread of its own
("Part runs"). `--cache-mb` sets a conservative resident cache budget
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
its studio light, x-ray, contact shadow and fog. The daemon draws with wgpu, on Metal on a Mac
and on Vulkan elsewhere, and starts no browser, server or STEP reader. Its device, pipelines and
last scenes stay warm, so a picture of the whole machine takes a fresh daemon about three seconds
and a warm one about a tenth of that.

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

`hsm-render --jobs FILE|-` (`tools/hsm/render`'s program) draws the same jobs in its own process,
with no daemon. The CI image has no GPU, and Mesa's lavapipe answers Vulkan there on the CPU.
- On lavapipe a picture is the same bytes on every runner, whatever its CPU or thread count.
- Five pictures of the machine take 7–13 s on four vCPUs there, against about a second on Metal.
- Metal draws the same picture in different bytes: mean |Δ| under 0.3 of 255 a channel.

[`tools/look.sh`](../look.sh) and [`tools/changes/change.mjs`](../changes/change.mjs) draw with
it. The guide art scripts, and the Bazel rules for the plumbing art, the opening scene, cad art
and install art, draw with `hsm-render` by way of
[`hardware/scripts/_hsm_render.py`](../../hardware/scripts/_hsm_render.py), which builds it from
the checkout. The Fill, ice and insertion-action tools use the same renderer.

A JSON job can give solid bodies presentation `materials`. Each row's `names` are body globs or
numbered mesh names; the last matching row wins. Rows can set `color`, `roughness`, `metalness`,
`opacity`, `side` (`front`, `back`, `double`), `unlit`, `tone_mapped`, `depth_write`, `order`,
`clearcoat` and `clearcoat_roughness`. `vertex_colors` uses an optional `col` payload array of
linear RGB triples. `texture` names an sRGB PNG, mapped by an optional `uv` array of pairs; its
mipmaps filter in linear light. Ordinary CAD payloads allocate no vertex attributes.

## Kernel

`hsm-kernel` (`tools/hsm/kernel`) builds solids as closed triangle meshes that record where
every face came from. Each triangle names a face record: the exact surface it lies on (plane,
cylinder, cone, sphere, torus, or a free surface), the builder that made it, the generator line
that called the builder (`#[track_caller]`) or the file it was read from, and the boolean that
brought it into the solid. A file names that line `path:line` from the checkout's root, as
meshcad does, so a part writes the same records from every worktree.

Profiles are drawn exactly with lines, arcs, circles, Béziers, corner fillets, offsets and the
hull round circles and points (`Loop`, `Pen`, `Profile`; `hull_loop` is CadQuery's
`Sketch.hull`) on a workplane (`Plane`) named as CadQuery names them, or read from a laser's
DXF (`dxf::read`, CadQuery's `importDXF`). The builders extrude (straight, both ways, drafted),
revolve, sweep along lines, arcs and cubics through points (`Path::spline_through`, CadQuery's
`makeSpline`; `Path::spline_to` between two end tangents) or along a helix (carried rigidly by
the screw motion, or in a rotation-minimizing frame), loft sections ruled
or through OCCT's own smooth surface (`Solid::thru_sections`, CadQuery's `loft`; a solid that
meets a smooth loft's end is built on the loft's own end ring, `SmoothLoft::end_region`),
set text from a font's outlines, and make boxes, cylinders, cones, spheres, tori, wedges and
hulls. All of them cut curves into points by one rule (0.005 mm chord, 0.05 rad, ring counts a
multiple of 8 from a canonical seam), so a surface gets the same vertices from any builder and
coincident faces meet point for point. `Solid::mapped` carries a solid by an affine map that need
not keep its shape, a shear or a stretch, as CadQuery's `transformGeometry` does: its planes stay
planes and every other face becomes a free surface.

Union, cut, intersect and plane split run on Manifold. Each operand face goes in as a run of its
own, so the result keeps every face record. Coordinates of different operands within 10⁻⁸ mm
are one coordinate, and a component thinner than the rule is dropped. Volume, area, centroid,
inertia and bounds come from the mesh. The writers make binary STL (leaving out a triangle that
has no area once its corners are f32), 3MF, GLB (face records in
its extras), the `.step.mesh` payload `hsm` reads, and the STEP meshcad writes: AP242
triangulated surface sets under each body's name and colour, with the model file a mesh-kernel
import reads beside it (`<name>.step.npz`). The same solid writes the same bytes on every run.
Without the `manifold` feature the kernel is pure Rust and builds for wasm32; its booleans
then return an error.

`Solid::gap(&other)` reports solid clearance in mm, zero for contact, penetration or
containment. `Solid::shared_volume(&other)` reports intersection volume in mm³, including
containment. Both use the fine f64 mesh through Manifold, without the fabrication simplifier
or boolean sliver filter.

For cylindrical manufacturing stock, `step::RoundStock` exports an analytic AP214 solid
with separate axial through or blind bores. Its planes, circles and cylinders form a closed
B-rep for machining quotes. `RoundStock::solid()` builds the fine model from the same
dimensions using the ordinary kernel builders. `part::write_shown_with_step` keeps that
fine model and its source records, and binds the viewer payload to the analytic STEP's
SHA-256. The carbonator tube and circular end-cap use this path.

`import::model(path)` reads an explicitly named `.step.npz`: f64 vertices, triangles, face
records, body names and linear colours. Stored and deflated NPZ files use maintained `npyz`
and `zip` readers. Coordinates and face indices keep their original order and precision.
Recorded surface parameters, source lines and boolean provenance survive import; an explicit
unknown source stays `null`. A model input is named directly by the consumer.

`import::payload(path)` reads every body of a
`.step.mesh`. `import::step(path)` reads a STEP's bodies through a payload cut from it. A STEP of
B-rep faces is read through `.cache/hsm/import/<SHA-256>.step.mesh` at the checkout's root,
OCCT's mesh of it at the kernel's rule, which `_rust_part.step` cuts. A STEP of triangles is
read through the payload its writer cut beside it, whose `src` is the STEP's SHA-256. Each body
is an `Imported` (`name`, `color`, `solid`). The solids a payload numbers
`name/1`, `name/2`, … come back as one body under its name, and `import::body(&bodies, name)`
picks one out. A payload's optional face records are retained. A range with no records gets a
free `MESH` record whose source is the file asked for:
`MESH import at hardware/reference/tee-connector/tee-connector.step`.
`Solid::from_mesh` makes a solid of any closed mesh. Corners at one point of the grid are one
vertex, and a mesh left open or folded is an error.

A solid's edges are CadQuery's (`Solid::edges(sel)`, `edge`): a run of mesh edges between two
faces, broken where a third face meets it, is one `Edge`, a LINE, CIRCLE or OTHER with CadQuery's
`Center()`. The selectors are CadQuery's strings with its precedence: `|D`, `#D`, `+D`, `-D`,
`>D`, `<D`, `>D[n]`, `>>D[n]`, `<<D[n]`, `%TYPE`, the named views, and `and`, `or`, `exc` and
`not` with parentheses. `Solid::face_edges(sel)` is `faces(sel).edges()`, `Edges::select`
narrows a selection as a chained `.edges(sel)` does, and `Edges::nearest(p)` is
`NearestToPointSelector`. `Solid::fillet(&edges, r)` and `Solid::chamfer(&edges, d)` round and
chamfer them (`round`), and every edge that runs on tangent from one of them, as OCCT does.
Each edge gets one tool: its section between the two faces and the round or chamfer, carried
straight along a line and turned about a circle's axis, cut from a convex edge and added to a
concave one. The tool's sides stand 0.001 mm off the faces (`round::STANDOFF`), so it reaches no
other wall of the solid. Where two rounds meet at a corner, both tools run past it and trim it
between them. The kernel rounds an edge between two planes, or between planes, cylinders and
cones about one axis, and refuses three rounds meeting at a corner, a round that ends on a
slanted face where it may not run on, and a round wider than a face it lies on.

The kernel's tests hold every builder and boolean to OCCT's volume and bounds for the same model
within the rule (`tests/occt_reference.py` and, for the helix sweeps, lofts and rounds,
`tests/screw_reference.py`, `tests/thru_reference.py` and `tests/round_reference.py` write those
with plain CadQuery), lofts and rounds to every point sampled on OCCT's faces within the rule
(the rounds include one beside a fin 0.3 mm away, fills in the corners of 1 mm and 0.8 mm walls,
and rounds and chamfers along the edges an earlier round made), hulls to the edges of CadQuery's
(`tests/sketch_hull_reference.py`), splines to the point and direction of OCCT's through the
same points and a tube swept along one to OCCT's sweep (`tests/spline_reference.py`), a DXF
outline to what `importDXF` reads from it (`tests/dxf_reference.py`), a sheared solid to every
point sampled on the faces of CadQuery's (`tests/mapped_reference.py`), and booleans to Manifold
run plainly on the same operands, sixty holes in one cut among them. They hold the fuse clamp, cut from its numbers, to the
volume of its module's `build()` and to that B-rep's STL (`tests/fixtures/fuse-clamp.stl`), two
processes to the same bytes, a STEP and a model file to the triangles, names and colours they
were written from, and the crate to a wasm32 build. The text tests read the system's Arial and
Helvetica.

## Parts the kernel cuts

A part the kernel cuts keeps its numbers in Python and its geometry in Rust, side by side in its
folder. The fuse clamp (`hardware/printed-parts/refrigeration/fuse-clamp`) is one; the coil
mandrel and the magnetic float (`hardware/printed-parts/cold-core/coil-mandrel` and
`magnetic-float`, crate `tools/hsm/cold-core`) are others. The faucet's parts and its two
assemblies keep their numbers in typed crates instead: each part's `numbers.rs` beside its
program, what they share in `hardware/printed-parts/faucet/numbers` (crate `hsm-faucet-numbers`),
and the assemblies' in `hardware/faucet-layout/numbers.rs`.

A part moves onto the kernel as soon as its program makes the outputs its generator made, faster
on the first try or not; [`conversion.md`](conversion.md) is the plan. The commit that moves it
carries the program's warm time, from its process's start to its exit, and the most memory it
held.

`fuse_clamp.py` is its generator. It derives every number the part takes from the parts it closes
on, states its bounds and fills its README, as any generator does, and writes the numbers the
geometry takes (`numbers()`) to `fuse-clamp.numbers.json`, which is committed beside it.
`fuse_clamp.rs` is the program that cuts the part from them: a `[[bin]]` of its subsystem's crate,
`tools/hsm/refrigeration`, named `fuse-clamp`. It reads the file with `part::args` and `Numbers`
(`f`, `pair`, `list`, `color`, `text`), builds the solid, refuses one that the fuse's case, grown by
the contact tolerance, does not touch, and hands its bodies to `part::write_part`. That writes
`fuse-clamp.step`, the model file beside it, the payload, whose `src` is the STEP's SHA-256, and
`fuse-clamp.stl`; leaves a file that holds the same bytes as it is; and prints what the files hold.
The STEP and the STL take each solid simplified once, at the kernel's rule. `part::write_shown`
writes a set without the STL, for bodies the page draws and nothing prints, and
`part::write_printed` one without the payload, for a printed piece whose payload
`hardware/scripts/flute_payload.py` cuts from its STL. A program that writes several sets prints
each one's answer on a line of its own, and its standard output carries nothing else. The magnetic
float's program writes seven: a set with an STL for each printed piece, and a set without one for
the magnet and for the assembly, section and exploded views. The faucet's printed pieces cut
their own payloads from their STLs, every triangle kept (`hsm_print_payload::printed`): the shell
its two prints, the display cover its print and the industrial faucet its four, and each display
cover writes itself as it sits on the tip with `write_shown`. Each faucet program is a crate of
its own, and `tools/hsm/faucet` is the library they share: the gooseneck, the display's frame at
its tip, `shell`, the shell's stock and the cutters the industrial faucet also cuts its own round
stock with, `display`, the lips and the relaxed print both display covers are cut with, and
`counter`, the plate and gasket under each base. The two assemblies are the programs of
`tools/hsm/faucet-assembly`: the faucet and its umbilical as the bench bags them.

`part::write_part` and `part::write_shown` include optional `face_sources` in each
payload mesh: one contributor array per displayed `fac` range, emitted by
`write::payload_bytes_with_sources`.
Contributors carry `src`, `op`, and an optional `via` operation/source pair. A source
explicitly recorded as unknown stays `null`; a wholly unknown record is a null contributor.
A displayed face can join triangles from
several builders, so the list includes every contributing source. The picker carries
these records into its copied face text. The fine model retains each triangle's own
record. Older payloads remain readable. `write::payload_bytes` emits the header without
contributor metadata; both encoders emit identical geometry arrays.

Payload imports retain each displayed range's complete contributor set. The analytic
surface stays intact, and no member becomes its primary owner. Fine model records can
carry that set in `contributors`, with `src:null` and an empty primary `op`; wholly null
records stay null. Transforms preserve the set. Repeated imports share one immutable
allocation per distinct complete set for the process lifetime.

`write::PrintOutput` captures prepared print bodies as STL bytes with the exact record
index of each emitted facet. Its `model_bytes` stores `print-F<i>.npy` and
`print-records.npy` in the existing fine archive, with an STL path and digest in
`document.printed`. Fine arrays/records and caller document fields stay intact. A reader
uses the map only for those bound STL bytes; an absent or stale binding supplies no
attribution. The shared writer includes this binding when it emits an STL.

The linter can read those recorded facet IDs on demand:

```sh
python3 tools/run.py -- tools/cad-venv/bin/python hardware/scripts/geometry_lint.py \
    path/to/part.stl --sources path/to/part.step.npz
```

It adds contributor records to the findings without changing their geometry or ranking.
The explicit model must bind the exact STL bytes; missing, stale or unrecorded data stays
unknown. This source lookup runs only when requested.

A generator that cuts a part begins its own run before it imports anything else:

```python
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
```

`start` starts the run's clock at the process's own start and defers CadQuery: the modules a
part's numbers come from import it to build other parts, and the run uses none of it. The CAD lock
is taken when CadQuery or OCP loads, or before the program runs in the generator's own process
("Part runs"), so a run the part engine answers that loads neither waits behind no OCCT build.
The `cadquery` it puts in `sys.modules` loads the first time a name is read off it, except
`Color` and `Plane`, which shared modules call as they import and which make stand-ins. A
stand-in colour answers `toTuple`, `==`, `hash` and `_materials.linear` with OCCT's bits, as
`linear` of a `#RRGGBB` string does (`hardware/scripts/_occt_color.py`). If CadQuery loads, each
stand-in becomes the value it stands for, in place, and whenever OCP loads, its loops end in
Python as `_cadq_export` ends them. So a part's run ends with neither `cadquery` nor `OCP.OCP`
loaded.
`hardware/scripts/test_rust_part.py` holds the template to all of it.

The generator runs the program through
[`hardware/scripts/_rust_part.py`](../../hardware/scripts/_rust_part.py).
`_rust_part.cut(crate, name, numbers(), part_dir)` writes the numbers, has the
part engine run the program from the checkout's workspace (`HSM_WORKSPACE` in a Bazel action;
"Part runs" below), and returns the files and bodies it printed.
`_rust_part.check(crate, name, numbers)` runs
`<program> <numbers.json> --check`, which measures the part and writes nothing, and returns its
JSON: the fuse clamp's selftest asks it for the case's touch, and the magnetic float's `verify.py`
for the volumes by which the pieces miss the design. `_rust_part.run(crate, name, *args)`
runs a program with arguments of its own and returns what it printed, and
`_rust_part.program(crate, name)` builds one and returns its path. Each run prints the program's
seconds and the most memory it held, or that the part engine kept it. Cargo builds into the
checkout's own target directory, `tools/hsm/target`, whatever `CARGO_TARGET_DIR` says. A worktree made by `tools/worktree.py` starts
with a clone of the main checkout's target directory less the workspace's own crates, so its first
build compiles those and not Manifold. `_rust_part` runs the `cargo` on `PATH`, else Homebrew's
rustup's, else the one in `~/.cargo/bin`.

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
CadQuery `build()` in its module instead: the fuse clamp keeps one for `enclosure_assembly`, and
the faucet's modules keep their builders for the hand-run checks and reviews that stand them. A
program on the kernel reads the STEP with `import::step`, as the faucet assemblies read the
shell's two pieces off `faucet-shell-base.step` and `faucet-shell-tip.step`.

```sh
tools/cad-venv/bin/python hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py
hsm --scene hardware/printed-parts/refrigeration/fuse-clamp/fuse-clamp.step.mesh where fuse-clamp
```

Its face records read `PLANE extrude at hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs:41`
and `PLANE box at hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs:42, cut at
hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs:43`.

## Part runs

The daemon runs the programs that cut parts, for every checkout, and keeps what each run wrote
([`engine/src/build.rs`](engine/src/build.rs)). `_rust_part.run` asks it over the socket.

New part builds and renders use the host-wide
[`run-slots`](run-slots/README.md) scheduler before taking compiler or memory
locks. A kept answer and an ordinary geometry query need no new heavy slot.
Use `python3 tools/run.py -- <command>` for standalone Cargo, Bazel, slicing
and rendering commands; `--cad` adds the native CAD lock and `--timing` reserves
the machine for a measurement. Verified child leases carry admission through
Python, the engine and Bazel actions.

`_rust_part` asks `hsm endpoint` once per generator process for the installed build's socket.
An executable without that command uses the legacy endpoint. `HSM_SOCKET` selects an explicit
endpoint. Without `hsm`, or with `HSM_NO_ENGINE=1`, the generator runs cargo and the program in
its own process.

```json
{"op":"run","workspace":"/checkout","root":"/checkout","crate":"<crate>","name":"<name>","args":["/checkout/<part dir>/<name>.numbers.json","/checkout/<part dir>"]}
```

`workspace` is the checkout whose `tools/hsm` holds the program, and `root` is where it runs from,
the action's directory in a Bazel action. The result carries what the program printed (`stdout`,
`stderr`), the sources it was compiled from (`sources`, which `_rust_part` hands the trace), the
files it read and wrote, whether a kept run answered (`hit`), whether cargo ran (`compiled`), the
program's seconds and peak, and the ask's own seconds. Each ask is answered on a thread of its
own, so a run holds up no geometry query.

A run's key is its program's code and its arguments. The code is the toolchain, as `rustc -vV`
names it from the workspace, and the SHA-256 of every workspace source rustc compiled into the
program, off its dep-info, with the manifests and the lockfile. An argument naming a file counts by
its bytes, the one naming a directory is where the files go, and any other counts as text. The
kernel lists each file a program reads in the file `HSM_READS` names (`kernel/src/reads.rs`): a
payload, a STEP and the payload it is read through, a DXF, a font. A kept run answers only while
each of those holds the bytes it read. A program whose kernel has no `reads.rs` lists nothing, and
none of its runs is kept.

The store is `parts/` in the store directory:

- `blobs/<sha256>`: each file a run wrote, once by its content;
- `runs/<key>.json`: up to four runs of a key, which differ in what they read;
- `programs/<code>/<name>`: each built program, by its code, with the checkout that built it in
  `built-in`, and `programs/<crate>.<name>.json`, the sources it was last compiled from, so a
  checkout whose target directory has no dep-info for it still knows its code;
- `peaks.json`: the most memory each program, and each crate's cargo, last held.

A kept run's files are cloned into the output directory, each under a name that ends as the file
does and renamed onto it, and a file already holding the bytes is left as it is, as
`part::write_part` leaves it. A program writes into a scratch directory, and its files are kept
before they are placed. Two asks for one key run it once. Digests are kept by device, inode, size,
mtime and ctime, so a hit reads no file again until it changes.

cargo runs only for code no kept program has: in the asking checkout's `tools/hsm`, into that
checkout's target directory, one cargo there at a time, with `CARGO_BUILD_JOBS=2`. A program and
its run are not kept when one of its sources was written while cargo ran. A kept program runs for
any checkout whose sources hash the same, and reads that checkout's import cache, which
`HSM_IMPORT_DIR` names; one whose kernel has no `reads.rs` runs only for the checkout that built
it. The program runs from `root` with `HOME`, `PATH=/usr/bin:/bin`, `HSM_READS`,
`HSM_IMPORT_DIR` and the verified run-lease descriptors and environment.

Runs and builds start in turn within `--build-mb` (default 1024 MiB), each counted at the peak it
last reached, a program not yet measured at 512 MiB and a cargo at 700 MiB. While macOS reports
critical memory pressure, one starts only when nothing else runs. Every ten minutes, a run unused
for `--keep-hours` (default 2) retires out of lookup's reach; ten minutes later it is deleted, and
with it the blobs no other run names. At an idle exit, so are the programs no run names.

Where no `hsm` is installed, or `HSM_NO_ENGINE` is set, `_rust_part` takes shared admission, builds the
program with cargo and runs it itself, and the files hold the same bytes. Native imports also take the CAD lock. A daemon too old to know `run` is replaced
once by starting the installed `hsm`; when that one doesn't know it either, `_rust_part` runs the
program itself.

### Declared generator actions

`hsm generate TARGET` runs an enrolled Python generator through the same part store.
The enrolled targets are `elbow-cradle` and `funnel-mold`.
`--root` selects its checkout; `--python /path/to/cad-venv/bin/python` supplies
the interpreter when that worktree has no `tools/cad-venv`. `--output DIRECTORY` places
the target's declared outputs under that directory's repository-relative paths; its default
is the checkout. Other actions remain with the normal build.

`tools/bazel/gen_build.py::action_plan` supplies both BUILD and this action's declarations:
generator entrypoints, inputs, optional inputs, producer edges and outputs.
`tools/hsm/generate.py` stages those files as the tree holds them and executes each
existing script entrypoint in order, in a separate Python interpreter as BUILD does.
Co-writers share the staged files. Their Rust calls use `_rust_part.run`. The action key
binds the declarations, staged input bytes, worker code, Python executable and version, and
installed CAD package versions. An optional input's absence is part of the key.
Only declared files are staged; no appliance is composed or copied.

The engine completes producer dependencies before their consumer. A producer-backed input
binds the completed action's output hash and is staged from that individual content blob.
The checkout's copy cannot supply it. The consumer key binds those output bytes, so an
unchanged producer result can reuse a kept consumer. `funnel-mold` uses the ordered
elbow-cradle/funnel/frame group this way. The answer's `actions` list describes every
completed action; `hit` and `receipt` describe the requested action. Only the requested
target's outputs are placed.

Declared graph support uses the same `gen_build.support_argv` materializer as BUILD.
It runs as a preceding action in the part store. Its completed output blob is staged
at the consumer's original input path, and nested read bindings name that provider
and output. A changed full graph can rerun the support action while identical
projected bytes reuse the consumer. Node runtime groups remain with the normal build.

The worker shares its verified host lease with the nested Rust request. It holds no outer
engine memory or compiler reservation while waiting for that request. Nested runtime reads
are bound to staged inputs, the action's own outputs, or validated external files. The answer's
`receipt` describes the captured execution: a cache hit starts neither the generator nor its
nested Rust program. The same blobs and kept-run budget serve both kinds of run.

Placement uses `sync_tree.carried` for rewritten Markdown, Mermaid and Python, preserving
current authored text while updating generated markers. Declared whole rewritten media are
placed whole. Other outputs are cloned from their individual content-addressed blobs; equal
files stay untouched. Neither this command nor its worker joins a build or commit hook.

## Explicit validation

```sh
cargo test --release --manifest-path tools/hsm/Cargo.toml
python3 -m unittest discover -s tools -p test_publish_manifest.py
tools/cad-venv/bin/python hardware/scripts/test_rust_part.py
```

These run only when requested. They do not join any build, edit or commit path.
