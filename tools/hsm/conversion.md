# The Rust conversion

[AGENTS.md](../../AGENTS.md#speed) states the goal: this Mac's CPU and memory stop limiting how
much the agents get done. This is the build's plan for it.

## Completion

The complete conversion puts the normal build's dimensions, numeric recipes, file readers,
document generation, geometry, checks and exports in Rust. No step loads CadQuery,
OpenCASCADE (OCP) or meshcad. The conversion keeps the same parts, names, placements,
colours, check answers and outputs.

An unconverted caller can use a thin Python import or command adapter for a finished Rust
piece. That adapter supplies raw provider inputs, restores its caller's Python object types
and registers source and output paths; the calculations and file transformations belong to
Rust. The remaining Python algorithms below are conversion work.

## How the work runs

- **The bet is on Rust.** A piece moves as soon as its Rust program makes the outputs it
  replaces. One that is slower on its first try lands anyway and is made faster in Rust
  afterwards. One that stays slower after that goes to Derek to re-examine, and holds up nothing
  else.
- **Pieces run in parallel.** The integration lead splits what is left into pieces with separate
  files, and one agent takes each piece, as many at once as the thread limit allows.
- **A piece is converted whole** before anything in it is verified.
- **A piece is verified once, at its end, on fixed inputs:** its outputs against the ones they
  replace, from the same inputs. The same solids within the kernel's rule; the same names,
  placements and colours; the same check answers. No full normal build, whole-build memory
  sample or old-against-new timing gates a single change. A normal build runs when a batch
  merges to main.
- **Memory is cut in the Rust programs** and verified the same way. The Python side of a program
  being converted gets no tuning.
- **Mechanical changes keep landing.** One that reaches main while its piece is being converted
  is carried into the Rust version before that piece merges. Once a piece is in Rust on main,
  its mechanical edits are made there.

## The normal geometry programs

The Rust programs construct and measure solids and compose their model/viewer files. Their
explicit input recipes come from Rust data providers or the Python providers awaiting conversion.

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

The install guide's twelve plumbing scenes use Rust geometry. Their dimensions, colours and
render-job providers include Python pieces awaiting conversion.

The final machine report carries its existing construction questions from current scalar source
ledgers and Rust measurements, including handhold sections and supported sloping faces.

The equipment fixture preserves a documented limitation for two PVC cuff joining caps:
the authored construction, dimensions, bounds and material colours agree, while the internal
Boolean-cap triangulations differ. The retained comparison records those differences; it does
not state that every raw surface matches. The combined build retains its existing fit questions.

## Current coverage

The normal construction, placement, equipment, routes, checks, print surfaces and model exports
use Rust. Each merged speed batch runs the combined normal build with the existing fit and drain
checks; source/output bindings, artifact readback and publication belong to that combined batch.

The source graph covers 101 entrypoints and 329 declared Python source and adapter files,
alongside the retained piece comparisons that prohibit native CAD imports. It identifies no
remaining normal-build CadQuery, OCP or meshcad load. This is source and fixed-input evidence,
not dynamic coverage of every optional command.

The inventoried native generator options, hose and collet illustration builders, and their
native-only manual review callers are absent. Print preparation retains its slicer, project
and report options; historical print records bind retired generator sources through Git.

## Scalar, recipe and document programs

`hardware/scripts/_rust_data.py` is the temporary JSON transport for Python callers. One Rust
process serves each program during an interpreter's lifetime. Cargo's dep-info supplies the
compiled source dependencies; adapters also register the data files Rust reads and the authored
files it maintains with the existing build trace registries.

| Program | Converted work |
| --- | --- |
| `hsm-documents` | Managed markers, Sources blocks, figure sidecars, Python comment/string scopes, Mermaid comments, table cells, numeric formatting, atomic placement and PDF/DXF normalization |
| `ledger-data` | BOM arithmetic and mass readers, build timing windows, machine and labor estimates, tool purchase resolution and funnel casting |
| `assembly-docs` | Assembly procedure figures, electrical budgets and schedules, fluid topology and marketing dimension readers |
| `cold-core-data` | Carbonator stock, float and rod datums, bond, coil paths and lengths, mandrel, Aero float and shared casing base dimensions |
| `faucet-data` | Scalar interface and tube paths, countertop seals/plates, organizer, display covers, industrial composition, lever stations and under-counter DXF |
| `enclosure-data` | Trim/display/nameplate datums, rear labels, pump-case profiles and pump/valve tray recipes and figures |
| `machine-data` | Facts and Box readers, fine-archive metadata, scalar report and scene composition, and equipment recipe providers |
| `part-data` | Drain adapters, cuffs, press and cutting fixtures, pump sleeve, PCBA readers/trays, valve seat and zone-C recipes |
| `layout-data` | Appliance frames, selected fitting names, native tube construction and sampling, reservoir routes and soda inlet/holder recipes |

## Remaining Python pieces

- Core enclosure sizing, construction recipes and scalar interface/datums.
- Main manifold/assembly placement, route and check input construction, mounting ledgers,
  rear snap datums and installed wiring providers.
- Cold-core cap mount/conduit queries, reservoir and foam recipes, core assembly providers,
  reed/shroud/hybrid-float recipes and carbonator/end-cap drawings.
- Faucet shell and full assembly recipes and their remaining provider modules.
- Shop storage, refrigeration and remaining fixture recipes.
- Purchased-reference dimension providers, shared CAD scalar helpers, materials and routing stock.
- Purchase-evidence ledger reconciliation and analysis.
- Install-guide artwork/document composition and build, cache, artifact and publication glue.

The scalar providers in those pieces remain live inputs to the converted programs. Their
current computed values are not stored as replacement constants.

## Fixed-input evidence

The [2026-11-04 comparison record](conversion-results/2026-11-04.json) retains the source
revision, input and artifact hashes, measured differences and completed comparisons for the
data and document programs. The comparison source is `d6a0b281d`; inputs are fixed for each
piece. It includes document byte comparisons, scalar and recipe comparisons, real archive/STL
readers and complete native route sets. Pump profiles retain differences below the kernel's
0.005 mm chord rule; their names, colours, bounds and source records agree.

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

`enclosure.py` and `enclosure_assembly.py` retain their scalar and Rust-driver interfaces without
native CAD builders or native-mode switches. The automatic local back-top preview uses fresh
Rust/scalar sizing and Rust scene export. Part drivers retain the numeric recipes and default
Rust programs used by the build. Manual fine-model probes use their existing saved-model reader.

The exporter stages physical and installed drawings as separate files. The physical fine model
names the drawing with the same body identities; generated wiring is appended to the installed
drawing. Cached results restore the files the caller consumes.

A component tradeoff is reported with its own CPU seconds, warm elapsed time, physical footprint and RSS; it
is not a whole-machine speed or memory-pressure result.
