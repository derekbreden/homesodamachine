# hsm

`hsm` answers geometry questions from the same triangle payloads and shared mesh references that `/3d` displays,
and draws pictures of them. One local Rust daemon serves the CLI, an MCP server and a Unix socket. Queries load a scene on
demand. A saved edit starts no build, query, watcher or check.

Build and install with Rust 1.89 or later, CMake and a C++17 compiler. The installer keeps each
build at an immutable path under `~/.local/lib/hsm/<build_id>/hsm` and puts a launcher at
`~/.local/bin/hsm`, which this Mac's shells have on `PATH`:

```sh
tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm --bin hsm
hsm-run --install-hsm "$PWD" tools/hsm/target/release/hsm
hsm where tee-y-a
hsm gap compressor/1 condenser+fan
hsm around relay-2/1 --within 12
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

Use `--against` for a move relative to a named obstacle. It reads only the selected pair:

```sh
hsm move pump-a-head --by 0 0 -10 --against enclosure-front-top
```

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
Remembered grip descriptions also find the authored handholds through the shared feature
matcher; exact feature identities retain priority.

For an exact feature, current source context is available without a build:

```sh
node tools/find-part.mjs enclosure-back-bottom::west-handhold --context
```

The context lists construction functions, dimension declarations, lexical references in the
compiler's recorded inputs, and other exported feature owners using that source file. The
returned build command selects those feature owners. Other source consumers are listed so a
shared helper or dimension edit can include its remaining affected pieces. References identify
code to read, rather than proving mechanical dependencies. The current source hash and exported anchor remain distinct;
an unbuilt edit can move a source line without updating its exported geometry.

An on-demand inspection draws the existing exported geometry and keeps its camera:

```sh
node tools/inspect-part.mjs HSM-0082 --output .cache/runs/pump-fit/before
node tools/inspect-part.mjs --output .cache/runs/pump-fit/after \
    --reuse .cache/runs/pump-fit/before/inspection.json
```

`--model` selects an existing assembly and `--body` selects its subject. `--against` measures
clearance to a named neighbour in that same assembly and draws that neighbour in x-ray;
unselected bodies are omitted. `--section` opens a section view.
`--ray` takes a point and direction in the same syntax as `--section`, and reads the containing
body so an obstruction cannot disappear merely because another feature owns its surface.
`--overlap` compares the containing parts as solids, so a feature surface cannot hide an
interference elsewhere in its owner. `--measure-only` records the selected clearances,
interferences and rays without drawing. Saved inspections and render jobs retain the selected
bodies, feature, neighbours, mates, rays, section and camera;
reuse repeats those questions against the latest exported payload. An explicit new query
reuses the camera without inheriting the other subject's measurement questions.
The command prints the focused answers and payload digest directly; `inspection.json`
retains the full measurement and source record.

`--model` also accepts a repository-relative or absolute local payload path. With an explicit
`--body`, it can inspect a completed part in a temporary output directory before its assembly
rebuilds, including a part not yet in the material catalog. This reads that export directly;
the normal print build remains the publication path.
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

In `/3d`, Component clicking selects whole parts in an assembly. **Open component** enters
the selected part; Component clicking then selects its named construction features directly
on the geometry. The parent breadcrumb selects the whole part. Returning to the assembly
returns picking to whole components.
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
executable; ordinary commands use the installed build. `hsm-run --install-hsm WORKSPACE BINARY --legacy-socket PATH`
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
Sessions measure the shared checkout. `claude mcp get hsm` shows the server.

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
  a payload redraws however it was written: by its producer, `hsm-build-plan sync-tree` or
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
it. Native guide and opening-scene artwork uses `hsm-render`. Optional install-art refreshes
use [`hsm-install-art`](install-art/README.md).

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

## Build and publication

The [print build](print-build/README.md) compiles and runs the selected native producers and
publishes each completed part while other producers continue:

```sh
tools/run -- hsm-print-build
tools/run -- hsm-print-build //:enclosure-back-top //:installed-machine
```

The [build planner](build-plan/README.md) owns the declared source/runtime split, targeted
Bazel rules, tracing and completed-output carry. [Cargo configuration](cargo-config/README.md)
separates compilation-relevant workspace settings from unrelated member edits.
[Publication](publication/README.md) uploads immutable geometry before its manifests,
commits the exact referenced records and asks the website to adopt them.
[Native Git landing](git-tools/README.md) preserves concurrent source and staged edits.
Saving source starts no build or check.

A part's typed numbers and construction live beside its source. Its native program reads the
runtime data and retained models it consumes, then writes its construction archive, printable
solids and viewer references together. A downstream assembly reads completed files rather than
reconstructing its parts. [conversion.md](conversion.md) describes those boundaries.
New studies use the [sandbox](sandbox/README.md).

## Surface source records

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
tools/run -- tools/hsm/target/release/geometry-lint \
    path/to/part.stl --sources path/to/part.step.npz
```

It adds contributor records to the findings without changing their geometry or ranking.
The explicit model must bind the exact STL bytes; missing, stale or unrecorded data stays
unknown. This source lookup runs only when requested.

## Part runs

The engine runs native producer programs and retains completed answers
([engine/src/build.rs](engine/src/build.rs)). The planner invokes it directly. A query or a
retained answer starts no compilation. New construction and rendering use the shared
[run-slots](run-slots/README.md) scheduler; compiler work shares its compiler lease.

```sh
tools/run -- cargo build --release --locked -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm --bin hsm
```

Each run is keyed by the executable's compiler inputs, arguments and recorded runtime reads.
The key uses content hashes; unchanged files reuse their digest by file identity and timestamps.
A completed answer restores only its recorded outputs, leaving identical bytes untouched.
Concurrent requests for the same key share one execution. A source written during compilation
prevents that program or run from entering the reusable cache.

The store holds immutable file blobs, completed run records and compiled programs under
`parts/`. `HSM_READS` records files read through native kernel readers. Runtime placements and
dimensions can change while reusing the compiled executable. The engine's request returns its
compiler sources, reads, writes, cache-hit status, compilation status, elapsed time and peak RSS.
The compiler runs in the checkout's own Cargo target directory.

The installed engine serves independent build requests and geometry queries. A producer runs
from its explicit root; its workspace selects the source checkout. Scene queries retain their
payload identity, so an unbuilt source edit cannot change a geometry answer.

## Optional tools

[Manual guides](manual-guides/README.md), [fabrication guides](fabrication-guides/README.md),
[install artwork](install-art/README.md), [marketing](marketing/README.md),
[wiring](wiring/README.md), [repository tools](repo-tools/README.md),
[device utilities](peripheral/README.md), [PCB tools](pcb-tools/README.md) and
[printer tools](printer-tools/README.md) run on request. They add no work to the normal print build.
Their READMEs give the command and the files it consumes.

Checks run when their question is asked. A focused crate fixture can be run through
`tools/run -- cargo test --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p PACKAGE`;
it adds no automatic build, edit or commit step.
