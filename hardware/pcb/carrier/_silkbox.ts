/**
 * _silkbox.ts — ground-truth silk geometry. Reads a circuit-json export and
 * prints, per top-level component (by designator), the bounding box of all its
 * silkscreen elements (paths/rects/lines/circles) AND its courtyard/pad extent.
 * This is the real DIM table — feed it into _place.ts so the grid model matches
 * what is actually drawn. Usage: bun _silkbox.ts [file.circuit.json]
 */
const file = process.argv[2] ?? "_gt.circuit.json"
const db = JSON.parse(await Bun.file(file).text()) as any[]

// pcb_component id -> source designator (R1, U6, J3, ...)
const srcName: Record<string, string> = {}
for (const e of db) if (e.type === "source_component" && e.name) srcName[e.source_component_id] = e.name
const compName: Record<string, string> = {}
for (const e of db) if (e.type === "pcb_component") compName[e.pcb_component_id] = srcName[e.source_component_id] ?? e.pcb_component_id
const compCenter: Record<string, { x: number; y: number }> = {}
for (const e of db) if (e.type === "pcb_component") compCenter[e.pcb_component_id] = e.center

type B = { x0: number; x1: number; y0: number; y1: number }
const grow = (b: B, x: number, y: number) => { b.x0 = Math.min(b.x0, x); b.x1 = Math.max(b.x1, x); b.y0 = Math.min(b.y0, y); b.y1 = Math.max(b.y1, y) }
const fresh = (): B => ({ x0: Infinity, x1: -Infinity, y0: Infinity, y1: -Infinity })
const silk: Record<string, B> = {}
const copper: Record<string, B> = {} // pads + smt + holes (the electrical extent)

const ensure = (m: Record<string, B>, id: string) => (m[id] ??= fresh())
for (const e of db) {
  const id = e.pcb_component_id
  if (!id) continue
  if (e.type?.startsWith("pcb_silkscreen")) {
    const b = ensure(silk, id)
    if (e.route) for (const p of e.route) grow(b, p.x, p.y)
    if (Array.isArray(e.points)) for (const p of e.points) grow(b, p.x, p.y)
    if (e.center && e.radius != null) { grow(b, e.center.x - e.radius, e.center.y - e.radius); grow(b, e.center.x + e.radius, e.center.y + e.radius) }
    if (e.center && e.size) { grow(b, e.center.x - e.size.width / 2, e.center.y - e.size.height / 2); grow(b, e.center.x + e.size.width / 2, e.center.y + e.size.height / 2) }
  }
  if (e.type === "pcb_smtpad" || e.type === "pcb_plated_hole" || e.type === "pcb_hole") {
    const b = ensure(copper, id)
    const w = e.width ?? e.outer_diameter ?? e.hole_diameter ?? e.radius * 2 ?? 0
    const h = e.height ?? e.outer_diameter ?? e.hole_diameter ?? e.radius * 2 ?? 0
    grow(b, e.x - w / 2, e.y - h / 2); grow(b, e.x + w / 2, e.y + h / 2)
  }
}

const rows = Object.keys({ ...silk, ...copper }).map((id) => ({
  name: compName[id] ?? id, c: compCenter[id], s: silk[id], k: copper[id],
})).filter(r => /^[A-Za-z]+\d+$/.test(r.name))
rows.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }))

const fmt = (b?: B) => b && isFinite(b.x0) ? `${(b.x1 - b.x0).toFixed(2)} x ${(b.y1 - b.y0).toFixed(2)}  [x ${b.x0.toFixed(2)}..${b.x1.toFixed(2)} y ${b.y0.toFixed(2)}..${b.y1.toFixed(2)}]` : "—"
console.log("designator  center        SILK w x h  [bounds]                              | COPPER w x h")
for (const r of rows) {
  const c = r.c ? `(${r.c.x.toFixed(1)},${r.c.y.toFixed(1)})` : "(?)"
  console.log(`${r.name.padEnd(5)} ${c.padEnd(13)} ${fmt(r.s).padEnd(54)} | ${fmt(r.k)}`)
}
