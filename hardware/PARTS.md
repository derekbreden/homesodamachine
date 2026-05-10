# Parts metadata sidecars

Every fabricated part in `hardware/` has a JSON sidecar next to it that
records material + thickness + process. The dev viewer reads these to
extrude DXF outlines into real 3D plates; tooling and future agents
should use them as the source of truth for material/thickness queries.

## Naming

`<full-filename>.json`, sitting in the same directory as the part:

```
hardware/cut-parts/foo/foo.dxf
hardware/cut-parts/foo/foo.dxf.json     ← sidecar

hardware/printed-parts/bar/bar.step
hardware/printed-parts/bar/bar.step.json ← sidecar
```

The sidecar filename always carries the original extension (`.dxf.json`,
`.step.json`) so a directory with both a `.dxf` and `.step` of the same
basename has no collision.

## Format

```json
{
  "thickness_mm": 1.524,
  "material": "304 stainless steel",
  "process": "laser-cut",
  "notes": "optional free-form context"
}
```

Fields:

- **`thickness_mm`** (number) — required. For DXF cuts this drives the
  viewer's `ExtrudeGeometry` so the flat outline becomes a real plate.
  For STEP prints / shells / tubes this is the wall thickness, kept for
  documentation and future tooling (BOM generators, manufacturing quotes,
  blog post images) — the STEP geometry itself already has full 3D shape.
- **`material`** (string) — free-form. Use the spec language you'd put in
  a quote or order: "304 stainless steel", "316 stainless steel", "PETG",
  "PETG-CF", "Bambu TPU 90A", etc.
- **`process`** (string) — free-form. Common values today: `laser-cut`,
  `3D-print`, `tube-bend`. Add new values as needed; this is for the
  human reader more than the renderer.
- **`notes`** (string, optional) — anything else worth knowing: stock
  size, supplier, why the spec was chosen, tap-engagement counts.

Pull values from the generator script's docstring (`generate_dxf.py`,
`generate_step_cadquery.py`) when one exists. Otherwise, use the spec you
ordered or printed against.

## When to update

- **Adding a new part:** also add the matching `.json` sidecar in the
  same commit. The dev viewer treats DXFs without a sidecar as having
  zero thickness and falls back to wireframe rendering.
- **Changing thickness or material:** update the sidecar in the same
  commit as the geometry change. The dev server's chokidar watcher picks
  up sidecar changes too — the viewer hot-reloads with the new thickness
  immediately, no page refresh needed.
- **Renaming or moving a part:** rename/move the sidecar alongside the
  geometry file.

## Harvested parts (reference geometry)

`hardware/harvested/` contains imported reference STEPs (factory faucet
body, valve internals) that this project is not fabricating. These don't
get sidecars — they're multi-material, externally-spec'd parts kept only
for spatial reference.

## Where this is consumed

- `tools/dev-server/templates/viewer-body.html` — DXF extrusion uses
  `thickness_mm` from the sidecar. STEP rendering ignores the sidecar
  (the STEP file is already 3D).
- `lib/viewer-routes.js` — `/api/dxf` returns each DXF's path alongside
  its sidecar fields so the client can render in one round-trip.
- Future tooling (BOM, render-dxf, etc.) should read the sidecar rather
  than re-parsing docstrings.
