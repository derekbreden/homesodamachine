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

## What is left

A piece comes off this list when it lands on main. The box and the machine are most of the
build's critical path: a change to the box runs both steps, one after the other, and a change to
any part in the machine runs the machine's.

The active pieces have separate file owners:

| Piece | Scope | Owner |
| --- | --- | --- |
| Machine placement | `enclosure_assembly.py`, fine-model references, installed frames and scalar layout | `machine_placement` |
| Equipment | Above-core fittings, clamps, bulkheads, mounting hardware and numerical route providers | `faucet_assembly` |
| Tube geometry | Warm fluid/gas sweeps and their insulation, from the equipment route specifications | `plumbing_scenes` |
| Enclosure generation | `enclosure.py`, `enclosure_box.py`, numeric datums, shell assembly and pump dock | `enclosure_geometry` |
| Enclosure measurements | Piece bounds, vent/handhold/ceiling readings and Box measurements | `enclosure_checks` |
| Machine checks | `_scorecard.py`, `check_asse_drain.py`, fit/clearance queries and scalar reports | `machine_checks` |
| Model exports | Physical STEP/fine models, display surfaces, wiring append and eleven scene GLBs | `model_exports` |
| Model context | Cold-core presentation, float integration and plain machine facts/scene/wiring context | `cold_core_assembly` |

The install guide's twelve plumbing scenes use Rust geometry with plain Python dimensions,
colours and render jobs. The optional hose and collet illustration builders load native CAD
only when those hand-run tools request them.

After these pieces land:

1. **Any other step that loads CadQuery, OCP or meshcad at run time.** A generator that calls
   `_rust_part.start()` defers CadQuery, and still loads it on any path that reads a CadQuery
   name.
2. **The CadQuery path itself.** Once the rest lands, meshcad, the Python builders nothing on the
   build calls, and CadQuery leave the normal build.
