# The Rust conversion

[AGENTS.md](../../AGENTS.md#speed) states the goal: this Mac's CPU and memory stop limiting how
much the agents get done. This is the build's plan for it.

## Destination

The build runs no Python. Every build step is a Rust program that the native engine runs, and what
the website shows and what prints come from it. Its recipes are typed Rust: structs, functions
and constants the compiler checks, calling the kernel in-process. Each program is built from
what its outputs are made from ([What an output is made from](#what-an-output-is-made-from)),
so an edit recompiles and reruns only what it changes, and it compiles in a step of its own,
ahead of the steps that run it.
[What Counts](../../AGENTS.md#what-counts) is the whole test;
every other file, report and intermediate format can change or go. Speed is measured on the
full build ([Speed work](#speed-work)).

The enclosure's steps are Rust programs the native engine runs: one for each printed piece, compiled
from its own recipe and the numbers it takes, and one for the enclosure model, built from the
pieces' files. So is the installed machine: one program places the pack, the equipment, its
tubes and the installed parts from the written-down design and the parts' own files, and writes
the machine's native model, shared scene references and facts. So is the install
guide: one program draws the kit page's items from their models, one renders the counter
opening, and one composes the booklet from its artwork and writes the reading copy the site
shows and, for an order, the print files. So are the flavor manifold, the rear equipment caps,
the plumbing charts and the ledgers: the bill of materials with the attended labor, the print
farm's time and the purchases. So are the cold core's: one program for each printed part, from its
own numbers crate and the numbers it takes by name, and one for each of its two assemblies,
built from the parts' files. Geometry and generated-document producers run as Rust programs.
The native print driver, publisher and build planner carry these outputs to the website.
`hsm-cargo-config` produces the compilation configuration. `hsm-build-plan trace-inputs`
records each program's compiler sources and runtime reads without importing a Python recipe.

## What an output is made from

An output reruns only when something it is made from changes. What each output is made from is
written down for its part, and it is these and nothing else:

1. **The part's own numbers.**
2. **The numbers it takes from other parts, by name.** The end cap takes the carbonator tube's
   inside diameter and the float rod's offset from the tube wall.
3. **The code that makes that kind of output:** the kernel for a solid, the drawing code for a
   drawing.
4. **For an output built from other outputs,** such as an assembly or a picture, those outputs'
   files, not the code that made them.

Other parts' recipes, code that shares a program with the part's, and the bookkeeping that
records outputs after they are made are not among them.

In Rust it is written down in the code. A part's numbers are in a crate of their own.
A part's program depends on the numbers crates of the parts it takes from and names each number
it uses, and it is compiled from its own recipe, those crates and the kernel or the drawing code.
A step that builds from other outputs lists their files. The bookkeeping runs in steps of its
own, over the outputs. A program whose inputs come out the same as before, such as one whose
binary is unchanged after an edit to a number it does not use, does not rerun.

A converted part meets this when these edits do what is predicted:

- An edit to the foam shell reruns the foam shell and the parts that use its numbers, and not
  the end cap.
- An edit to the tube's length leaves the end cap's outputs as they are: the end cap uses only
  the tube's inside diameter.
- An edit to the drawing code reruns drawings and nothing else.
- An edit to the kernel reruns solids, and an output built from a solid reruns only if that
  solid came out different.
- An edit to the bookkeeping reruns only the bookkeeping's own outputs.

The edits are tried once, when a part is converted, not on every commit.

What each step read when its recipe was Python is its ceiling. The
[archived dependency graph](https://github.com/derekbreden/homesodamachine/blob/d6a0b281d2866a4435ffaf056850efe960a74f1f/tools/bazel/graph.json)
lists every step's reads, and the Python modules at that revision name each number
a part takes in their `from … import` lines. A converted part is made from no more than its step
read there, with each Python file replaced by the Rust that took its place.

## How the work runs

- **Delete, declare, convert, in that order.** Before a step is converted:
  - what it makes that feeds neither the website nor a print goes
    ([What Counts](../../AGENTS.md#what-counts)), and the files a part is ordered from leave
    the normal build;
  - what it works out that could be written down is written down: where a part sits, where the
    enclosure is cut for it, which runs a diagram draws. A search for a good arrangement is a
    tool someone runs when they rearrange the machine, and its answer is written down;
  - only what is left is converted.
- **True dependencies come first** ([What an output is made from](#what-an-output-is-made-from)).
  A step whose outputs come out the same stops the reruns after it. A native step's
  recorded inputs include its compiled sources and
  `tools/hsm/cargo-config.json`, the part of the workspace manifest and lock file that can change
  a program (`tools/hsm/cargo-config`). The job runner is not among them: each step copies
  the checkout's runner files in when it runs. Of a generated recipe crate, a step takes only the
  modules it reaches from the stubs it calls, so an edit to one recipe module reruns the steps
  that reach it. A hand-written crate is taken whole, and an edit to the kernel or the
  bookkeeping reruns every step that uses them.
- **One step at a time, biggest first:** the graph's entries by CPU. Steps whose files are
  separate run in parallel.
- **A step is converted** when the native build runs its Rust program and no Python. The Python only that
  step used is deleted in the same change, which lands on main on its own with the step's share
  of the full build before and after.
- **The machine's clash checks are off until the parts they read are in Rust.** A conversion
  keeps every solid within the kernel's rule, so nothing it does changes the fit. The checks
  then come back in Rust, written from what the `/3d` checks panel shows.
- **Typed recipes are written from what the website shows and what prints.** The current code
  shows how a step makes those; it is not the specification, and it is not translated line by
  line. No Python interface, `Val` value or name looked up at run time stays inside the Rust.
- **The bet is on Rust.** A step moves as soon as its Rust program makes the outputs it
  replaces. One that is slower on its first try lands anyway; making it faster is
  [speed work](#speed-work).
- **A step is converted whole** before anything in it is verified.
- **A step is verified once, at its end, on fixed inputs:** what the website shows and what
  prints, against what the code it replaces makes from the same inputs. The same solids within
  the kernel's rule (`tools/hsm/kernel/src/rule.rs`); the same names, placements and colours.
  Other files, checks and reports can differ or go. No full normal build, whole-build memory
  sample or old-against-new timing gates a single change. A normal build runs when a batch
  merges to main.
- **Memory is cut in the Rust programs** and verified the same way. The Python side of a program
  being converted gets no tuning.
- **Mechanical changes keep landing.** One that reaches main while its step is being converted
  is carried into the Rust version before that step merges. Once a step is in Rust on main,
  its mechanical edits are made there.

## The normal geometry programs

The Rust programs construct and measure solids and compose their model/viewer files. Their
explicit input recipes come from Rust data providers.

| Piece | Rust program or data boundary | Source |
| --- | --- | --- |
| Machine placement | `machine-layout`; installed transforms and model selections | `hardware/manifold-layout/machine_layout.rs` |
| Equipment | `machine-equipment`; fittings, clamps, bulkheads and mounting hardware | `hardware/manifold-layout/machine_equipment.rs` |
| Fluid and refrigeration tubes | `machine-routes`; sweeps, insulation and developed lengths | `hardware/manifold-layout/machine_routes.rs` |
| Wire curves | `wire-route-samples`; interpolation, lengths and curvature | `hardware/wiring/installed/wire_route_samples.rs` |
| Installed wires | `installed-wires`, which `installed-machine` runs in its own process; each conductor swept along its segments and each termination and jacket cut from its shape | `hardware/wiring/installed/wire_geometry.rs`, `hardware/wiring/installed/wire_request.rs` |
| Enclosure pieces | `enclosure-front-bottom`, `enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top`, `enclosure-pump-retainer`, `enclosure-pump-tube-setting-jig`; each printed piece's files from the declared Box through its typed recipe | `hardware/printed-parts/enclosure/enclosure/enclosure_*.rs` |
| Enclosure model | `enclosure`; the shown pieces in place from their fine models, with the dock's tees and stem elbows | `hardware/printed-parts/enclosure/enclosure/enclosure.rs` |
| Enclosure measurements | `enclosure-checks`; piece bounds and Box measurements | `hardware/printed-parts/enclosure/enclosure/enclosure_checks.rs` |
| Print surfaces | `print-payload` and the library the enclosure, cold-core and faucet piece programs link; reduction, shading and source records | `tools/hsm/print-payload/` |
| End cap | `endcap-circular-step`; the machined cap's files from the numbers crates of the tube, the float and the cap | `hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_step.rs` |
| End cap drawing and laser file | `endcap-circular-drawing`, `endcap-circular-dxf`; the cut build's sheet and DXF, run when an order needs them | `hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_drawing.rs`, `hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.rs` |
| Cold-core parts | `prv-shroud`, `reservoir`, `foam-shell`, `foam-cap`, `magnetic-float`, `all-aero-float`, `coil-mandrel`, `reed-bridge`; each printed part's files from its numbers crate, its payloads cut in process | `hardware/printed-parts/cold-core/*/` |
| Cold-core assemblies | `foam-assembly`, `cold-core-assembly`; the casing and the core in place from the parts' files, with the carbonator, its fittings, the coil and the lines inside the casing from their numbers crates | `hardware/printed-parts/cold-core/foam-assembly/foam_assembly.rs`, `hardware/cold-core-layout/cold_core_assembly.rs` |
| Cold-core numbers | `hsm-cold-core-interface`, `hsm-cold-core-catalog`, `hsm-cold-core-layout`, `hsm-coil-numbers`, `hsm-carbonator-numbers` and each part's numbers crate; the casing's interface, the fits and colours, the cap's frame and the inside lines, the coil and the vessel | `hardware/printed-parts/cold-core/`, `hardware/cold-core-layout/` |
| Faucet parts | `tpu-o-ring`, `umbilical-organizer`, `faucet-shell`, `above-counter-plate`, `above-counter-gasket`, `faucet-display-cover`, `industrial-faucet`, `lever-replica`, `tube-collar`; each part's files from its own numbers crate and the faucet's, each printed piece's payload cut from its STL | `hardware/printed-parts/faucet/*/*.rs` |
| Faucet assemblies | `faucet-assembly`, `faucet-industrial-assembly`; the faucet and its umbilical as the bench bags them, from the assembly's numbers crate, each printed piece drawn with its own surface | `hardware/faucet-layout/faucet_assembly.rs`, `hardware/faucet-layout/faucet_industrial_assembly.rs` |
| Zone C | `funnel`, `funnel-frame`, `elbow-cradle`, `funnel-cover`, `funnel-mold`; the cast funnel, its frame, cradle and cover, and the mold it is cast in, from zone C's numbers crate, with the numbers the installed machine places the funnel, frame and cradle by and the mold's design record | `hardware/printed-parts/zone-c/*/*.rs` |
| Installed machine | `installed-machine`; the placements, equipment, tubes, installed parts and wiring in one process, written as the machine's STEP, viewer payload, facts and scene GLBs | `hardware/manifold-layout/installed_machine.rs` |
| Machine checks | `machine-checks`; fit, clearance and scalar readings, off during the conversion | `hardware/manifold-layout/machine_checks.rs` |
| Flavor manifold | `manifold-layout`; the manifold's valves, tees, pumps and stem elbows from their reference models and its tubes swept, written as the model and the construction the installed machine seats it by; its arrangement is written down in `hsm-manifold-numbers` | `hardware/manifold-layout/manifold_layout.rs`, `hardware/manifold-layout/manifold/` |
| Rear equipment caps | `rear-equipment-caps`; the snap caps and their installed set from the receivers' stations and the parts' measured profiles | `hardware/printed-parts/enclosure/rear-equipment-caps/rear_equipment_caps.rs` |
| Display cover and status plate | `display-cover`; the display's bezel, the status plate beside it, their screws and inserts, and the mount dimensions, from the enclosure's display numbers | `hardware/printed-parts/enclosure/display-cover/display_cover.rs` |
| Display gasket | `display-gasket`; the TPU ring between the display's glass and its cover, from the same numbers | `hardware/printed-parts/enclosure/display-gasket/display_gasket.rs` |
| Rear identification tiles | `rear-identification`; the six port tiles from the above-core layout's rear grid and the bulkhead rings' words, and the numbers the installed machine places them by | `hardware/printed-parts/enclosure/rear-identification/rear_identification.rs` |
| Nameplate | `nameplate`; the serial plate, its artwork read from the wordmark and brand mark, each unit's QR code, and with the first unit its receiver, fasteners and the receiver's dimensions | `hardware/printed-parts/enclosure/nameplate/nameplate.rs` |
| Plumbing charts | `fluid-topology`; the manifold and carbonator charts' labels, checked against the installed machine's runs and the manifold's connections | `hardware/topology/fluid_topology.rs` |
| Bill of materials and labor | `bom`; bom.md's printed-part masses from the fine models, its hardware counts and figures from the machine's facts and the parts' numbers, its totals, and labor.md's runs and totals | `hardware/ledger/bom.rs` |
| Print-farm time | `machine-time`; machine-time.md's occupancy from bom.md's masses and the native slices | `hardware/ledger/machine_time.rs` |
| Purchases | `purchases`; purchases.md's totals and sidecar, and its JSON and CSV views | `hardware/ledger/purchases.rs` |
| Install guide | `install-guide`; the booklet's pages from its artwork, kit drawings and the faucet plate's DXF, written as the reading copy, cover picture and sidecar, and with `HSM_PRESS` the Lulu interior, cover and order bundle | `hardware/install-guide/install_guide.rs` |
| Kit drawings | `kit-art`; each supplied item's hidden-line view from its model and the faucet's numbers | `hardware/install-guide/kit_art.rs` |
| Counter opening | `opening-scene`; the faucet's tails over the counter's hole, rendered, and the parts' outline in the same frame | `hardware/install-guide/opening_scene.rs` |
| Page drawing | the `hsm-pages` library; PDF, type and line breaking, outlined pictures, pixels and line drawings of models | `tools/hsm/pages/` |
| Model exports | the `hsm-model-export` library; physical models, display surfaces, wiring append and scene GLBs | `hardware/assembly/scenes/model_export/` |
| Model context | `installed-machine`'s equipment recipes and stations, fine-model metadata reads, facts and scene documents | `tools/hsm/machine-data/src/` |
| Document readers | Rust ledger programs, with explicit source dependencies | `tools/hsm/ledger/` |

The final machine report carries its existing construction questions from current scalar source
ledgers and Rust measurements, including handhold sections and supported sloping faces.

The equipment fixture preserves a documented limitation for two PVC cuff joining caps:
the authored construction, dimensions, bounds and material colours agree, while the internal
Boolean-cap triangulations differ. The retained comparison records those differences; it does
not state that every raw surface matches.

## The installed machine's hand-overs

`installed-machine` runs its stages in one process, and each stage hands the next its result.

The wiring's hand-overs are typed.
[`wire_request.rs`](../../hardware/wiring/installed/wire_request.rs) defines the `Request` the
wiring stage builds and the installed-wires program cuts from: a `Wire` of `Segment`s for each
conductor, and a `Part` with one `Shape` for each termination and jacket. The routing in
[`assembly-docs/src/wiring`](assembly-docs/src/wiring/) holds the terminals, poses and cable
passages as a `State`, a conductor as a `Connection` and its course as a `Route`, a shared cable
as a `Bundle`, a saved course as a `Saved` with its `Station`s, and the wire stock as a `Stock`.
It takes each value it needs from a named method of `Sources`. The review that `hsm-wiring`
writes is a JSON document built from those.

The mechanical stages hand each other JSON documents: the pack and the placement plan, the
equipment request and its result, the tube routes and the facts request. The stage programs
[`machine_layout.rs`](../../hardware/manifold-layout/machine_layout.rs),
[`machine_equipment.rs`](../../hardware/manifold-layout/machine_equipment.rs) and
[`machine_routes.rs`](../../hardware/manifold-layout/machine_routes.rs) read theirs through
`hsm_kernel::part::Numbers`. They call the layout data's functions by name. Typing these
documents is open work.

Two record encodings remain in what the mechanical stages read.
[`enclosure-box.json`](../../hardware/manifold-layout/enclosure-box.json) writes its records as
`__hsm_namedtuple__`, `__hsm_dict__` and `__hsm_list__` objects, which `design::plain`, the
enclosure's `numbers/spec.rs`, the facts' `reporting.rs` and the publisher each read back as
plain objects and lists. `shared-data`'s `common.rs` reads a non-finite number from a
`_hsm_float` record.

## Current coverage

The normal geometry, generated-document, configuration, supervision, publication and tracing
programs execute in Rust. Their normal build loads no Python, CadQuery, OCP or meshcad.

`tools/hsm/build-plan/graph.json` records the maintained producers and their inputs and outputs. Cargo's
dependency records describe each Rust program's compiled sources. Retained comparisons cover
complete pieces on fixed inputs; the combined normal build exercises their integration.

The cut and PCB builds, manual books and artwork, PGFUN fixture and controller tools,
printer operations and firmware releases run only when requested. They remain separate from
the normal print build. Their package READMEs name their native entrypoints.

Python application adapters remain where an external host requires that language: Blender's
`bpy` bridge and PlatformIO's SCons pre-build hook delegate to native tools. Independent Python kernel reference generators produce the saved OCCT fixtures used by
explicit comparison tests. Git retains retired recipes and closed studies. Current purchased
reference models and the source data their native replicas consume remain in their owning locations.

## Scalar, recipe and document programs

Typed commands own maintained build, inspection and optional authoring work.

| Program | Converted work |
| --- | --- |
| `hsm-documents` | The ledger's managed markers, Sources blocks and figure sidecars, tables, formatting, placement and PDF/DXF normalization |
| `ledger-analysis` | Purchase evidence, exact decimal reconciliation, validation, CSV/JSON and reports, for the synthetic ledger tests |
| `assembly-docs/src/wiring` | The installed wiring model, routing and readers, which `installed-machine` compiles |
| `cold-core-data` | Typed carbonator rod requirements and jet interfaces for native fabrication tools |
| `shared-data` | Materials, finishes, colour arithmetic and the PET-GF cooling policy |
| `layout-data` | Appliance frames, fitting names, native tube construction and sampling, reservoir routes and soda inlet/holder recipes |
| `hsm-manual-guides`, `hsm-fabrication-guides`, `hsm-install-art` | Optional books, fixture art, engineering reference sheets and selected install illustrations |
| `hsm-build-data`, `hsm-build-plan` | Mesh and artifact identity, native producer inventory, dependency tracing, BUILD rendering, affected targets and completed-output carry |
| `hsm-cargo-config`, `hsm-print-build`, `hsm-publication`, `hsm-git-tools` | Compilation configuration, progressive delivery, immutable member uploads and path-scoped landing |
| `hsm-wiring`, `hsm-mesh-review`, `hsm-repo-tools` | Explicit wiring exports, geometry lint and repository readings |
| `hsm-marketing`, `hsm-peripheral`, `hsm-pcb-tools`, `hsm-printer-tools` | Optional artwork/media, device utilities, detailed board models and printer operations |
| `hsm-pgfun-positioner`, `hsm-pgfun-host`, `hsm-pgfun-observation` | Fixture geometry, offline review, controller host and saved-image measurements |
| `hsm-run`, `hsm-run-slots` | Host admission, inherited run/CAD/compiler leases, process execution and runtime installation |
| `hsm-print-prep` | Print preparation: each printed part's Bambu project from its meshes and a saved or system printer recipe, the localized PET-GF cooling stage, enclosure print regions, offline slices, and the print review and support audit that read them |

Geometry producers use their typed recipe and numbers crates.

## Fixed-input evidence

The [earlier geometry and provider record](conversion-results/2026-11-04.json) retains its
fixed-input source revisions, hashes and geometric differences, including the existing pump
profile tolerance and PVC cuff triangulation limitation.

The final conversion records retain the baseline and native source hashes, raw input and
artifact hashes, comparison counts, numerical differences and public type boundaries:

- [Enclosure](conversion-results/enclosure-final-2026-11-04.json)
- [Cold core and seven drawings](conversion-results/cold-core-final-2026-11-04.json)
- [Machine providers and readers](conversion-results/machine-final-2026-11-04.json)
- [Faucet](conversion-results/faucet-final-2026-11-04.json)
- [Reference parts and fixtures](conversion-results/parts-final-2026-11-04.json)
- [Shared helpers and ledger](conversion-results/shared-final-2026-11-04.json)
- [Installed wiring](conversion-results/wiring-final-2026-11-04.json)
- [Guide documents and artwork](conversion-results/guides-final-2026-11-04.json)
- [Bookkeeping and carry](conversion-results/bookkeeping-final-2026-11-04.json)
- [Publication](conversion-results/publication-final-2026-11-04.json)
- [Host runtime](conversion-results/runtime-final-2026-11-04.json)
- [Build support and combined build](conversion-results/build-final-2026-11-04.json)
- [Generated modules: run and compile cost](conversion-results/generated-runtime-2026-11-04.json)
- [Native workflows and live integration](conversion-results/native-workflows-2026-11-10.json)
- [Deferred Python callers and adapter retirement](conversion-results/python-tail-2026-11-10.json)

The conversion is complete and its [speed work](#speed-work) is closed. These records are
component reductions and incremental build measurements: they establish no matched
whole-machine memory gain, and a completed conversion does not by itself establish that this
Mac is free of memory pressure.

## Speed work

The [boolean engine workload record](conversion-results/manifold-cpp-cargo-2026-11-11.json)
compares both native backends through the normal producer graph with identical recipes and
fixed external inputs. Each backend supplies its own new exports to dependent steps. The
record separates elapsed execution, CPU time and producer memory; compilation, result-cache
lookup and publication are outside that comparison.

The [enclosure edit record](conversion-results/enclosure-edit-2026-11-07.json) measures an
authored band dimension change with fresh construction and retained stages. The enclosure
evaluator retains exact intermediate solids; the band and mechanical body receive their
openings and joint limits separately. Back-top and the bottom quadrants retain the body's
completed print surface. The part payload keeps the printed triangles, and publication
grafts the finished part into the existing viewers. These are part-edit measurements;
compilation, publication, print preparation and the full build have separate costs.

Exterior dimensions are runtime inputs in
[`exterior.json`](../../hardware/printed-parts/enclosure/enclosure/exterior.json).
Changing them reruns the affected quadrant generators and reuses their compiled programs.
Each quadrant generator writes its native model, print STL and viewer references together.
Publication replaces that producer's references in the existing machine and named views while
other producers continue. Print-region generation, preparation and slicing run separately.

`hsm-print-build` carries each completed native producer into the checkout and requests
publication immediately. Immutable body meshes are shared across the machine, enclosure,
named views, the pretty viewer and geometry queries. Their manifests own names, colours,
placements and source bindings. Placement changes reuse the geometry object. Enclosure and
installed-machine producers retain native archives for construction and print preparation;
they generate no standalone STEP or combined GLB exports. The browser keeps unfinished parts'
last available surfaces and mounts each ready replacement while preserving its camera and
local visibility choices.

Publication freezes only the files being sent, compresses changed objects with bounded
workers, uploads objects before their references, then advances the committed pointer. The
website adopts changed members and notifies open viewers. Manufacturing exports remain
separate consumers of the generated solids. Viewer references advance before manufacturing
uploads and input-proof bookkeeping. A publication includes the completed members captured
for its reference refresh; later completions advance in the next publication.

The [live-publication record](conversion-results/progressive-publication-2026-11-07.json)
retains source-to-visible timings, per-producer delivery costs, print hashes and consumer
checks. It records the startup and deployment outlier alongside the warmed measurements.

Whole-machine throughput is measured with the normal print build on fixed inputs. Its run
receipt records the selected producers, cache answers, compilation, execution and completion
times. An unchanged build reuses retained answers. An edit runs the affected programs; a
downstream program reuses its answer when its input files retain their contents.

A converted step or speed piece is measured by its share of the full build, before and after,
on the same fixed inputs: its programs' CPU seconds computing every result afresh, client and
`hsm` engine together, as the median of three runs, plus the CPU seconds to recompile after an
edit to its recipes. Wall time and peak memory are recorded beside it. Other agents' load
barely moves CPU seconds, so it needs no quiet Mac. A change within 10% either way is neither faster nor slower; the work aims at large
improvements. A piece gets no full normal build; the normal build follows a batch merged to
main. Independent pieces run in parallel.

No speed piece is open. The [runtime-input record](conversion-results/runtime-iteration-2026-11-08.json)
and the [live-publication record](conversion-results/progressive-publication-2026-11-07.json)
put an authored edit on the live website in seconds, so the build is not the long part of the
time from Derek's request to a change he can see. Speed work opens again from a
[measured request](../iteration/README.md) in which the build is the long part, and its
pieces are then measured as above.

An explicit local build uses the same native producer targets and progressive publication as
the print build. Saving source starts no build. Manual fine-model probes read saved exports.

The exporter stages physical and installed drawings as separate files. The physical fine model
names the drawing with the same body identities; generated wiring is appended to the installed
drawing. Cached results restore the files the caller consumes.

A component tradeoff is reported with its own CPU seconds, warm elapsed time, physical footprint and RSS; it
is not a whole-machine speed or memory-pressure result.
