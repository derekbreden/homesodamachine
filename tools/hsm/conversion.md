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
| Enclosure measurements | `enclosure-checks`; piece bounds and Box measurements | `hardware/printed-parts/enclosure/enclosure/enclosure_checks.rs` |
| Enclosure print surfaces | `enclosure-presentation`; reduction, shading and source records | `hardware/printed-parts/enclosure/enclosure/enclosure_presentation.rs` |
| Machine checks | `machine-checks`; fit, clearance, drain and scalar reports | `hardware/manifold-layout/machine_checks.rs` |
| Model exports | `machine-export`; physical models, display surfaces, wiring append and eleven scene GLBs | `hardware/assembly/scenes/machine_export.rs` |
| Model context | Plain facts, scene documents and numerical wiring context | `hardware/manifold-layout/_machine_reporting.py` |

The install guide's twelve plumbing scenes use Rust geometry with plain Python dimensions,
colours and render jobs. The optional hose and collet illustration builders load native CAD
only when those hand-run tools request them.

The equipment fixture preserves a documented limitation for two PVC cuff joining caps:
the authored construction, dimensions, bounds and material colours agree, while the internal
Boolean-cap triangulations differ. The retained comparison records those differences; it does
not state that every raw surface matches. The combined build retains its existing fit questions.

## What is left

A piece comes off this list when it lands on main. The current merged batch needs its normal
execution and publication; component comparisons are not a completed combined build.

1. **Cold-core and faucet print surfaces.** `flute_payload_cold_core.py` and
   `flute_payload_faucet.py` retain Python mesh simplification, shading and surface export.
   `enclosure_checks` owns their Rust presentation consumer. The enclosure producer owns its
   own print surfaces and aggregate; its redundant fluting co-writer is outside the normal path.
2. **Metadata-reader startup.** `cold_core_assembly` owns normal BOM, mechanical/plumbing,
   topology and dimension readers that import the legacy assembly only for scalar data or source
   dependencies. These readers keep their data and source edges without loading the CAD driver.
3. **Combined execution and publication.** The integration lead owns actual normal results,
   source/output bindings, artifact readback and main publication. The batch runs after merging
   to main; it adds no per-piece speed or whole-build gate.
4. **Any other step that loads CadQuery, OCP or meshcad at run time.** A generator that calls
   `_rust_part.start()` defers CadQuery, and still loads it on any path that reads a CadQuery
   name. Optional native design and manual review tools remain outside the normal build.
