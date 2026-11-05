# The Rust conversion

[AGENTS.md](../../AGENTS.md#speed) states the goal: this Mac's CPU and memory stop limiting how
much the agents get done. This is the build's plan for it.

## Completion

The normal build's dimensions, numeric recipes, file readers, document generation, geometry,
checks and exports execute in Rust. No normal step loads CadQuery,
OpenCASCADE (OCP) or meshcad. The conversion keeps what the website shows and what prints
([What Counts](../../AGENTS.md#what-counts)): the same parts, names, placements and colours.

An unconverted caller can use a thin Python import or command adapter for a finished Rust
piece. That adapter supplies raw provider inputs, restores its caller's Python object types
and registers source and output paths; the calculations and file transformations belong to
Rust. Python library backends provide rendering and document primitives; authored calculations,
layout and file transformations execute in Rust. Native recipe modules use compiled Rust
control flow and values; they do not evaluate Python source at runtime.

## How the work runs

- **The bet is on Rust.** A piece moves as soon as its Rust program makes the outputs it
  replaces. One that is slower on its first try lands anyway and is made faster in Rust
  afterwards. One that stays slower after that goes to Derek to re-examine, and holds up nothing
  else.
- **Pieces run in parallel.** The integration lead splits what is left into pieces with separate
  files, and one agent takes each piece, as many at once as the thread limit allows.
- **A piece is converted whole** before anything in it is verified.
- **A piece is verified once, at its end, on fixed inputs:** what the website shows and what
  prints, against what the code it replaces makes from the same inputs. The same solids within
  the kernel's rule; the same names, placements and colours. Other files, checks and reports can
  differ or go. No full normal build, whole-build memory
  sample or old-against-new timing gates a single change. A normal build runs when a batch
  merges to main.
- **Memory is cut in the Rust programs** and verified the same way. The Python side of a program
  being converted gets no tuning.
- **Mechanical changes keep landing.** One that reaches main while its piece is being converted
  is carried into the Rust version before that piece merges. Once a piece is in Rust on main,
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
| Enclosure generation | Panel kernels, `enclosure-dock`, numeric Box and model references | `hardware/printed-parts/enclosure/enclosure/` |
| Selected enclosure pieces | Existing Rust part and print programs; STEP, fine model, STL and bound viewer payload | `hardware/scripts/materialize_pump_cartridge.py` |
| Enclosure measurements | `enclosure-checks`; piece bounds and Box measurements | `hardware/printed-parts/enclosure/enclosure/enclosure_checks.rs` |
| Print surfaces | `enclosure-presentation`; enclosure, cold-core and faucet reduction, shading and source records | `hardware/printed-parts/enclosure/enclosure/enclosure_presentation.rs` |
| Machine checks | `machine-checks`; fit, clearance, drain and scalar reports | `hardware/manifold-layout/machine_checks.rs` |
| Model exports | `machine-export`; physical models, display surfaces, wiring append and eleven scene GLBs | `hardware/assembly/scenes/machine_export.rs` |
| Model context | `machine-data`; facts, scene documents and numerical wiring context | `tools/hsm/machine-data/` |
| Document readers | Rust ledger and procedure programs, with explicit source dependencies and remaining raw provider inputs | `tools/hsm/ledger/`, `tools/hsm/assembly-docs/` |

The install guide's twelve plumbing scenes use Rust geometry, dimensions, colours and
render-job providers. Native guide composition calls the existing ReportLab, Pillow and
pypdf library primitives through opaque object handles.

The final machine report carries its existing construction questions from current scalar source
ledgers and Rust measurements, including handhold sections and supported sloping faces.

The equipment fixture preserves a documented limitation for two PVC cuff joining caps:
the authored construction, dimensions, bounds and material colours agree, while the internal
Boolean-cap triangulations differ. The retained comparison records those differences; it does
not state that every raw surface matches. The combined build retains its existing fit questions.

## Current coverage

The normal build's dimensions, numeric recipes, readers, document generation, geometry,
checks, exports, build planning, caches and publication transformations execute in Rust.
Thin Python modules retain import names, public record and container types, command entrypoints,
source/output registration and calls to library primitives. The normal build loads no
CadQuery, OCP or meshcad.

The source graph and shared runtime inputs cover 101 entrypoints, 341 Python source and adapter
files, and 426 Rust sources, alongside Cargo manifests and raw files. The retained comparisons cover complete pieces on fixed inputs;
the combined normal build exercises their integration and the existing fit and drain checks.
This is evidence for the maintained build, not dynamic coverage of every optional command.

Historical print records, dated studies and optional native CAD probes retain their recorded
sources. Dormant fine-model BREP readers, manual wiring review/search/drawing commands and
native-only review callbacks are outside the normal build. Print preparation keeps its slicer,
project and report options. No optional native CAD path supplies a normal-build result.

## Scalar, recipe and document programs

`hardware/scripts/_rust_data.py` carries JSON between compatibility modules and resident Rust
programs. Reentrant callbacks retain native object identities. Interrupted requests discard
their worker; objects from that process cannot be used after a restart. Cargo dep-info supplies
compiled source dependencies, and the adapters register raw data and maintained output paths
with the existing build trace registries.

| Program | Converted work |
| --- | --- |
| `hsm-documents` | Managed markers, Sources blocks, figure sidecars, Python comment/string scopes, Mermaid comments, tables, formatting, placement, PDF/DXF normalization and native value/library interoperation |
| `ledger-data`, `ledger-analysis` | BOM arithmetic, mass/timing/cost readers, purchase evidence, exact decimal reconciliation, validation, CSV/JSON and reports |
| `assembly-docs` | Assembly procedure figures, electrical budgets, schedules, fluid topology and the installed wiring model, routing and readers |
| `cold-core-data` | Complete cold-core dimensions, recipes, assembly, reservoir/foam/float/mandrel providers and maintained fabrication drawings |
| `faucet-data` | Complete faucet shell and assembly recipes, scalar interfaces, tube paths, seals, collars, lever, plumbing scenes and DXF |
| `enclosure-data` | Complete enclosure sizing, interface/datums, panel/dock/tray/cap/nameplate recipes, measurement graph and document providers |
| `machine-data` | Manifold and assembly placement recipes, equipment/routes/check inputs, mounting ledgers, facts, Boxes, fine archives, reports and scene composition |
| `part-data` | Purchased reference providers, storage catalogues, refrigeration/printing fixtures, drain adapters, cuffs, press, sleeve, trays and zone-C recipes |
| `shared-data` | Materials, finishes, colour arithmetic, stock routing and shared fit/snap/reeding/cooling helpers |
| `layout-data` | Appliance frames, fitting names, native tube construction and sampling, reservoir routes and soda inlet/holder recipes |
| `guides` | Install and faucet guide layout, artwork, camera/mask/shading calculations, plumbing render plans and document composition |
| `build-data`, `bookkeeping-data` | Mesh payloads, projection, source hashes, fine-asset adoption, print/graft planning, artifact identity/caches, inventory, source stripping, carry/selection/pointers and publication archives |
| `build-plan` | Generator action planning, dependency rules, graph projections and BUILD rendering |
| `hsm-run`, `hsm-run-slots`, `hsm-run-native` | Host admission, inherited run/CAD/compiler leases, process execution, viewer notifications and runtime installation |

The recipe, reader and document modules of `enclosure-data`, `machine-data`, `cold-core-data`
and `guides` are Rust generated from their Python modules, about 37,700 authored lines. Each
generated module is one `initialize` function over `hsm_documents::interop::Val`: Python
names resolve at run time through `Env` scopes, and a module outside the compiled set is
imported through the Python adapter's callback. No generator is retained, so edits go into
the generated files.

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

The CPU and memory goal still needs performance work in Rust. Component reductions and
incremental build measurements do not establish a matched whole-machine speed or memory gain;
a completed conversion does not by itself establish that this Mac is free of memory pressure.

## Speed work

Independent pieces run in parallel, beginning with the whole-machine assembly and enclosure.
Each finished speed piece is measured on its own program, before and after, using the same
fixed inputs and outputs. The deciding number is CPU seconds, client and `hsm` engine
together, as the median of three warm runs: other agents' load barely moves it, so it
needs no quiet Mac. Wall time and peak memory are recorded beside it. Compilation is
outside the measurement. A change within 10% either way is neither faster nor slower; the
work aims at large improvements. A piece gets no full normal build; the normal build
follows a batch merged to main.

| Piece | Scope |
| --- | --- |
| Machine checks | Bounded future-use search reuse preserves fit and drain answers |
| Enclosure construction | Identical panel construction expressions share their result |
| Equipment | Repeated fittings share construction and imported models release after final use |
| Fluid routes | Insulation reads only its referenced equipment bodies |
| Print presentation | Topology, contributor records and reduction scratch share storage |
| Enclosure measurements | Model selections from the same file share one import pass |
| Installed placement | Reference names and bounds avoid unrelated model data |
| Fine-model reading | Typed array values decode directly into final vertex and triangle rows |
| Generated recipe modules | Typed Rust functions and values in place of the generated `Val` modules of `enclosure-data`, `machine-data`, `cold-core-data` and `guides` |

`enclosure.py` and `enclosure_assembly.py` retain their scalar and Rust-driver interfaces without
native CAD builders or native-mode switches. The automatic local back-top preview uses fresh
Rust/scalar sizing and Rust scene export. Part drivers retain thin numeric interfaces to the
Rust recipes and programs used by the build. Manual fine-model probes use their existing saved-model reader.

The exporter stages physical and installed drawings as separate files. The physical fine model
names the drawing with the same body identities; generated wiring is appended to the installed
drawing. Cached results restore the files the caller consumes.

A component tradeoff is reported with its own CPU seconds, warm elapsed time, physical footprint and RSS; it
is not a whole-machine speed or memory-pressure result.
