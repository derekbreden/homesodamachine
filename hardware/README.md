# Hardware

The home soda machine's physical design — the integrated under-counter appliance that consolidates carbonator, refrigeration, flavor reservoirs, pumps, valves, and electronics into one enclosure.

**Start with [`future.md`](/hardware/future.md)** — the master design narrative. It describes the appliance subsystem by subsystem (carbonation, refrigeration, cold core, flavor, enclosure, power) and links out to every companion doc and part directory below.

## Layout

| Path | What's there |
|---|---|
| [`future.md`](/hardware/future.md) | The design narrative — the entry point and source of architectural intent. |
| [`design-pressures.md`](/hardware/design-pressures.md) | What the appliance is optimised for and what it is not. Placement decisions answer to this: volume and assemblability are optimised, field service and disassembly are not. |
| [`ledger/`](/hardware/ledger/) | Bookkeeping. [`purchases.md`](/hardware/ledger/purchases.md) is the source-of-truth capex ledger; [`bom.md`](/hardware/ledger/bom.md) (per-unit parts), [`tools.md`](/hardware/ledger/tools.md) (active tooling), and [`inventory.md`](/hardware/ledger/inventory.md) (spares / abandoned / donor / diagnostic stock) are views over it. |
| [`assembly/`](/hardware/assembly/) | Production procedures, one doc per subsystem, plus [`handwork.md`](/hardware/assembly/handwork.md) (the skilled-hand task summary). |
| [`service/`](/hardware/service/) | Procedures run on a finished appliance rather than a bench: [`pump-replacement.md`](/hardware/service/pump-replacement.md) and the dry cycle it runs first. |
| [`printed-parts/`](/hardware/printed-parts/) | FDM parts: CadQuery generators (`*.py`) + exported `*.step` + sidecars. Includes `cadlib/` (shared geometry helpers), `cold-core/`, `enclosure/`, `faucet/`, `flavor/`, `refrigeration/`, `valve-seat/`, `zone-c/`. |
| [`cut-parts/`](/hardware/cut-parts/) | Laser-cut sheet parts: `*.dxf` outlines + sidecars (carbonation end-caps, faucet plate). |
| [`off-the-shelf-parts/`](/hardware/off-the-shelf-parts/) | Reference geometry for purchased parts modelled into assemblies. |
| [`reference/`](/hardware/reference/) | Imported / harvested reference STEPs (factory faucet, solenoid, ice-maker, fittings). Not fabricated by this project — no sidecars. |
| [`topology/`](/hardware/topology/) | Fluid + valve topology, including the canonical valve-state truth table. |
| [`wiring/`](/hardware/wiring/) | Wiring schedules, pinouts, and power topology diagrams. |
| [`battery-backup/`](/hardware/battery-backup/) | Mains-outage dispense ride-through subsystem. |
| [`quickstart/`](/hardware/quickstart/) | Customer quick-start geometry + drawings. |
| [`snapshots/`](/hardware/snapshots/) | Dated, point-in-time records (build-readiness audit, first-tap plan). **Frozen, not living docs** — re-run produces a fresh dated file rather than editing these. |
| [`scripts/`](/hardware/scripts/) | Project Python tooling. The instruments: [`probe.py`](/hardware/scripts/probe.py) asks the placed machine a geometry question instead of reasoning about it — where a body is, how close two come, what a volume runs into, how far a line runs, where there is room for one, what a pick copied out of the viewer names, and where a piece of a routed line can stand; [`fit.py`](/hardware/scripts/fit.py) asks the same of a body that is not placed yet, carried to a candidate pose; [`lanes.py`](/hardware/scripts/lanes.py) enumerates every corridor a run could take between its two fixed mouths at a stated clearance floor, holding every body still, and reports each one's tube, corners, tightest clearance, lowest z and the sub-assembly its legs lie on without ranking them. Each carries a `selftest`. Then `_cadq_export.py` (the shared atomic STEP/DXF/PDF export helper imported tree-wide) and the doc-sync / totals generators that maintain the `ledger/` docs. |

## What a build costs

    bazelisk build //:everything                          # every generator whose inputs moved
    tools/cad-venv/bin/python tools/bazel/sync_tree.py    # what the tree does not carry yet

ONE ACTION PER STEP, EACH HOLDING WHAT IT DECLARED AND NOTHING ELSE. What it declared is what
a run of it was watched reading — `tools/bazel/trace_inputs.py` installs an audit hook, runs
the generator once, and keeps every path under this repo it opened, including the ones handed
to a tool it starts. The median step declares nine files; `_cable_assemblies_sync` declares
six, and the assembly syncs that import the machine to reach its constants declare eighty. The
graph is `tools/bazel/graph.json`; `tools/bazel/gen_build.py` writes `BUILD.bazel` from it.

A step is usually one generator. Four are several: `docgen` lets more than one script keep a
doc's `[value](NAME)` figures, each managing its own names, so `touch_flo_shell.py` and
`touch_flo_under_counter_plate.py` both write `ASSEMBLY.md` and are one action. `bazel` needs
one action per file, and `inventory._together` is what groups them.

`bazel-bin/` is where a build lands and this repo commits its solids and its docs, because a
reader at `/3d` and a shop printing a part both take them off the tree. `sync_tree.py` is what
carries them over, and a tree it has nothing to say about is a tree holding the artifacts its
sources make.

WHAT AN EDIT COSTS IS THE STEPS THAT DECLARED THE FILE, and that is a count, not a guess:

| a comment added to | steps it reruns |
|---|---|
| a doc sync's own driver | **1** |
| `_boxes.py` | 21 |
| `_measuring.py` | 25 |
| `_realized.py` | 57 |
| `_cadq_export.py`, which every generator imports | 95 |

| | wall |
|---|---|
| the whole tree, nothing moved | **0.24 s**, no action run |
| whether anything is owed — `--check_up_to_date` | **0.04 s**, no action run |
| the whole tree from nothing, 101 steps | 491 s of critical path |

The first two are what a commit pays. The third is measured under five other builds on the
same machine and is a ceiling rather than a reading; the actions themselves ran at roughly
half speed for want of cores.

A BYTE IS WHAT DECIDES A RERUN, so a comment moves a file and its steps run again. They come
back with the same bytes and nothing downstream of them runs, but they do run — a whole-tree
digest taken over parsed code rather than text is what would make a comment free, and there
is none here.

A SOLID ONE GENERATOR CUTS AND THE NEXT LOADS IS AN EDGE LIKE ANY OTHER HERE. `foam_assembly`
reads `foam-cap-top.step` off the disk and `enclosure_assembly` reads `foam-assembly.step`;
neither is an import, and OCCT opens the file below Python where no audit hook reaches.
`_cadq_export.import_step` is the one loader and records what it loaded, so both edges are in
the graph — and an action that names too little does not read a stale solid, it does not find
the file at all.

A picture is the same picture every run. Every renderer in `tools/render/` reads the frame
back off the canvas in the task that drew it (`browser.js` `frameBuffer` carries why), so
nothing here is a race and a redraw of unmoved geometry lands byte-identical — eight runs of
one scene and eight of one part, one hash each.

A view of any STEP, from any angle, is `tools/look.sh` — drawn when someone asks for one, so
there is none of it in the tree to go stale.

WHAT THE ACTIONS RUN WITH IS THE MACHINE'S, not the tree's. `tools/cad-venv` holds the
interpreter and its packages, `node_modules` the renderer's, and `rsvg-convert` and `blender`
come off the brew prefix — `.gitignore` holds the first two and the last two are not in the
repo at all. `.bazelrc` names both roots as mounts and puts them on every action's PATH. A
checkout on another machine builds when those are installed there and not before.

TWO THINGS THE BUILD DOES NOT GUARANTEE, both named where they stand:

- **A `.step.png` is not a declared output.** `_cadq_export` draws a thumbnail best-effort —
  "a thumbnail must never break export" — and a Bazel output is one the action must produce or
  fail. The two are opposite promises. The thumbnails are still drawn by every run.
- **`//:render-scenes` carries `local` and is not sandboxed.** `render-step-posed.js` stands
  the viewer on loopback and photographs it with a headless browser, and that page loads
  `occt-import-js` off a CDN — so drawing a scene reaches the public network for a library this
  tree does not carry. Vendoring it is what would make the action hermetic. It is the one
  action here whose inputs are not all declared.

Inside one run:

| phase | wall |
|---|---|
| derive + audit — `build_enclosure_assembly`, then the card | 8.7 s |
| — of which `_boxes.boxed`, 1372 calls against the disk-kept six | 0.55 s |
| OCCT STEP write, 21 MB | 1.3 s |
| canonicalise — renumber 382,700 entities | 3.7 s |
| tessellate the `.mesh` payload | 1.6 s |
| one thumbnail, drawn off the payload | 3 s |
| one thumbnail, drawn off the STEP with no payload beside it | 16 s |

The export and render rows are timed at `081a1bee`; the two derive rows at `c813264b`.

## Part metadata sidecars

Every fabricated part has a JSON sidecar next to it recording material + thickness + process. The dev viewer reads these to extrude DXF outlines into real 3D plates; tooling and future agents should treat them as the source of truth for material/thickness queries.

### Naming

`<full-filename>.json`, in the same directory as the part:

```
cut-parts/foo/foo.dxf
cut-parts/foo/foo.dxf.json       ← sidecar

printed-parts/bar/bar.step
printed-parts/bar/bar.step.json  ← sidecar
```

The sidecar filename always carries the original extension (`.dxf.json`, `.step.json`), so a directory holding both a `.dxf` and a `.step` of the same basename has no collision.

### Format

```json
{
  "thickness_mm": 1.524,
  "material": "304 stainless steel",
  "process": "laser-cut",
  "notes": "optional free-form context"
}
```

- **`thickness_mm`** (number, required) — for DXF cuts this drives the viewer's `ExtrudeGeometry` so the flat outline becomes a real plate. For STEP prints / shells / tubes it is the wall thickness, kept for documentation and future tooling (the STEP geometry itself already carries full 3D shape).
- **`material`** (string) — free-form, in the spec language you'd put in a quote or order: `"304 stainless steel"`, `"316 stainless steel"`, `"PETG"`, `"PET-CF"`, `"Bambu TPU 90A"`, etc.
- **`process`** (string) — free-form. Common values: `laser-cut`, `3D-print`, `tube-bend`. Add new values as needed.
- **`notes`** (string, optional) — anything else worth knowing: stock size, supplier, why the spec was chosen, tap-engagement counts.

Pull values from the part's generator-script docstring when one exists; otherwise use the spec you ordered or printed against.

### When to update

- **Adding a part:** add the matching `.json` sidecar in the same commit. The viewer treats a DXF without a sidecar as zero-thickness and falls back to wireframe.
- **Changing thickness or material:** update the sidecar in the same commit as the geometry. The dev server's watcher picks up sidecar changes and hot-reloads with the new thickness, no page refresh needed.
- **Renaming or moving a part:** rename/move the sidecar alongside the geometry file.

### Harvested reference parts

[`reference/`](/hardware/reference/) holds imported reference STEPs (factory faucet body, valve internals) this project does not fabricate. These get no sidecars — they're multi-material, externally-spec'd parts kept only for spatial reference.

### Where this is consumed

- The dev viewer (`web/`) extrudes DXF outlines using `thickness_mm`; STEP rendering ignores the sidecar (the STEP is already 3D). See `web/lib/viewer-routes.js` (`/api/dxf` returns each DXF's path alongside its sidecar fields).
- Future tooling (BOM generators, render-dxf, manufacturing quotes) should read the sidecar rather than re-parsing docstrings.
