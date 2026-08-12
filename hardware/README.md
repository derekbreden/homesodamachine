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

Wall clock on the owner's machine at `94aa493a` — warm caches, no other build running, one
run each.

**What an edit that moves no code owes is nothing.** A file is named by its parsed code
(`_realized.code_digest`), so a comment, a blank line or a reflowed docstring renames nothing
and stales nothing: `owed.py` reports every doc, card and scene current and runs no generator.

| | wall |
|---|---|
| a comment-only edit to a file in every closure | nothing owed |
| `enclosure_assembly.py`, nothing moved | 17 s |
| `enclosure_assembly.py`, three elevations drawn | 27–30 s |
| `render_scenes.py`, four scenes, geometry unchanged | 19 s |
| `render_scenes.py`, four scenes redrawn | 30 s |

A picture is the same picture every run. Both posed renderers read the frame back off the
canvas in the task that drew it, so nothing here is a race and a redraw of unmoved geometry
lands byte-identical — eight runs of one scene, six of another, one hash each.

Inside one run:

| phase | wall |
|---|---|
| derive + audit — `build_enclosure_assembly`, then the card | 8.7 s |
| — of which `_boxes.boxed`, 1372 calls against the disk-kept six | 0.55 s |
| OCCT STEP write, 21 MB | 1.3 s |
| canonicalise — renumber 382,700 entities | 3.7 s |
| tessellate the `.mesh` payload | 1.6 s |
| three ortho elevations, x-ray, 1600×1200 | 3 s |
| one thumbnail, drawn off the payload | 3 s |
| one thumbnail, drawn off the STEP with no payload beside it | 16 s |

The export and render rows are timed at `081a1bee`; the two derive rows at `c813264b`.

A scene carries the hash of the STEP it was drawn of, so a run agreeing on that and on the
scene's own tuple leaves the picture standing and boots no browser. What is left in the 24 s
is the four scene STEP exports and their `.glb`s.

What a chain of eighteen came to, each generator in it:

| | wall | | wall |
|---|---|---|---|
| `enclosure.py` | 26 s | `manifold_layout.py` | 10 s |
| `cold_core_assembly.py` | 19 s | `reservoir.py` | 5 s |
| `pump_tray.py` | 10 s | `foam_shell.py` | 5 s |
| `valve_panel.py` | 4 s | `_enclosure_mechanical_sync.py` | 4 s |
| `_fluid_topology_sync.py` | 3 s | every other doc sync | 2 s |

The doc syncs read `enclosure-assembly.facts.json` and stand no machine, so they are 2–4 s
whether or not they name a figure the pack decides.

Eighteen generators end to end: **106 s**. That is what a commit owes when it moves a figure
those generators write. A commit that touches a widely-imported module without changing what
it computes owes none of them.

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
