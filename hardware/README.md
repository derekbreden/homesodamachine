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

Wall clock on the owner's machine at `081a1bee` — warm caches, no other build running, one
run each unless a range is given.

`enclosure_assembly.py` has two costs. The stamp beside the STEP decides which one a run
pays: a run whose STEP hashes to what the stamp holds draws no elevations, and a run that
moved the STEP draws three and a thumbnail.

| `enclosure_assembly.py` | wall |
|---|---|
| STEP unchanged | 47 s |
| STEP moved | 67 s — taken on the run that renumbered the whole file, so it is a ceiling |

Inside one run:

| phase | wall |
|---|---|
| derive + audit — `build_enclosure_assembly`, then the card | 20.1 s |
| OCCT STEP write, 21 MB | 1.3 s |
| canonicalise — renumber 382,700 entities | 3.7 s |
| tessellate the `.mesh` payload | 1.6 s |
| three ortho elevations, x-ray, 1600×1200 | 3 s |
| one thumbnail, drawn off the payload | 3 s |
| one thumbnail, drawn off the STEP with no payload beside it | 16 s |

Every generator that stands the whole machine, plus the instruments' selftests:

| | wall | | wall |
|---|---|---|---|
| `_enclosure_mechanical_sync.py` | 41–42 s | `_bom_sync.py` | 18–20 s |
| `render_scenes.py`, four scenes | 39–44 s | `_appliance_model.py` | 19 s |
| `enclosure.py` | 29–30 s | `_cards_sync.py` | 19–22 s |
| `lanes.py selftest` | 24 s | `_internal_plumbing_sync.py` | 15 s |
| `probe.py selftest` | 22 s | `valve_panel.py` | 15 s |
| `_enclosure_dimensions.py` | 20–21 s | `_back_panel_dimensions.py` | 14 s |
| `_fluid_topology_sync.py` | 19–20 s | `cold_core_assembly.py` | 12–14 s |
| `manifold_layout.py` | 12 s | `_scorecard.py selftest` | 2 s |

The benchtop syncs that stand no machine — `_acceptance_and_burn_in_sync.py`,
`_cold_core_sync.py`, `_electronics_shelf_sync.py`, `_firmware_and_commissioning_sync.py`,
`_handwork_sync.py`, `_pressure_vessel_sync.py`, `port_ring.py`, `valve_seat.py` — are 1–2 s
each, and `_lines.py selftest` is 1 s.

Twenty generators end to end, which is what a commit touching a widely-imported module owes:
**268–282 s**.

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
