# The Rust conversion

[AGENTS.md](../../AGENTS.md#speed) states the goal: this Mac's CPU and memory stop limiting how
much the agents get done. This is the build's plan for it.

## Completion

No step of the normal build loads CadQuery, OpenCASCADE (OCP) or meshcad. Each generator keeps
its numbers in Python and has a Rust program cut its geometry on the kernel, as the
[parts the kernel cuts](README.md#parts-the-kernel-cuts) do, and the checks and exports that
read the geometry run in Rust or on `hsm`. The conversion converts what the build has: the same
parts, checks and outputs.

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

Python supplies dimensions, numeric construction recipes, file references and document data.
The Rust programs construct and measure the solids and compose their model/viewer files.

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
| Model context | Plain facts, scene documents and numerical wiring context | `hardware/manifold-layout/_machine_reporting.py` |
| Document readers | Scalar dimensions and facts with explicit source dependencies and numeric provider imports | BOM, assembly procedures, topology, enclosure dimensions and assembly instructions |

The install guide's twelve plumbing scenes use Rust geometry with plain Python dimensions,
colours and render jobs. The optional hose and collet illustration builders load native CAD
only when those hand-run tools request them.

The final machine report carries its existing construction questions from current scalar source
ledgers and Rust measurements, including handhold sections and supported sloping faces.

The equipment fixture preserves a documented limitation for two PVC cuff joining caps:
the authored construction, dimensions, bounds and material colours agree, while the internal
Boolean-cap triangulations differ. The retained comparison records those differences; it does
not state that every raw surface matches. The combined build retains its existing fit questions.

## Current coverage

The normal construction, placement, equipment, routes, checks, print surfaces and model exports
are converted and published on main. The combined local build and cloud build pass, including
the existing fit and drain checks, complete solid inventory, ledger and documentation.

The source reconciliation covers all 102 graph entrypoints and their 322 declared Python files,
alongside the retained piece comparisons that prohibit native CAD imports. It identifies no
remaining normal-build CadQuery, OCP or meshcad load. This is source and fixed-input evidence,
not dynamic coverage of every optional command.

Python remains for dimensions, numeric recipes, file readers and documents. Optional native
design and manual review tools remain outside the normal build. There are no identified normal
CAD conversion pieces awaiting an owner.

The CPU and memory goal still needs performance work in Rust. Component reductions and
incremental build measurements do not establish a matched whole-machine speed or memory gain;
a completed conversion does not by itself establish that this Mac is free of memory pressure.

## Speed work

Independent pieces run in parallel, beginning with the whole-machine assembly and enclosure.
Each finished speed piece is measured on its own program, before and after, using the same
fixed inputs and outputs: warm elapsed time from process start to exit, peak process memory
and peak RSS. Compilation is outside that elapsed time. A piece gets no full normal build;
the normal build follows a batch merged to main.

| Piece | Scope |
| --- | --- |
| Machine checks | Reuse bounded native search structures without changing fit or drain answers |
| Enclosure construction | Reuse identical panel construction expressions |
| Equipment | Reuse fittings and release imported models after their final use |
| Fluid routes | Read only equipment bodies used by insulation |
| Model exports | Reduce remaining physical and viewer file-writing work |
| Print presentation | Reuse topology and contributor preparation |
| Installed placement | Read reference names and bounds without retaining unrelated model data |
| Native fallback removal | Remove native-only code in `enclosure.py` and `enclosure_assembly.py`, retaining their scalar and Rust-driver interfaces |

The native removal covers those two drivers and code used only by their removed paths.
Other native hand-run tools remain pending Derek's individual decisions, including the hose
and collet illustration builders. Their files are outside this removal.
