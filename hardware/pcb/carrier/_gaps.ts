/**
 * _gaps.ts — report the real edge-to-edge gaps between component bodies
 * (courtyards) and to the board edge, to drive placement tightening toward a
 * target clearance. Bodies are the pcb_courtyard rects/outlines (the physical
 * keep-out), not the pad spans. Self-exports the board's circuit-json.
 *
 *   bun _gaps.ts [board=mini] [target_mm=2]
 *
 * Prints, per component, its nearest neighbour + that gap and its nearest
 * board-edge gap; then the overall tightest gaps and a TIGHTEN list (pairs
 * looser than target, where there's slack to pull in) and a CLOSE list
 * (already at/under target — leave or risk DRC).
 */
import { execFileSync } from "node:child_process"
import { readFileSync, rmSync } from "node:fs"

const board = process.argv[2] || "mini"
const target = Number(process.argv[3] || 2)
const tsci = "node_modules/.bin/tsci"
const j = `._gaps.${board}.json`

try {
  execFileSync(tsci, ["export", "-f", "circuit-json", "-o", j, `${board}.tsx`], { stdio: ["ignore", "ignore", "pipe"] })
} catch (e: any) {
  console.error(`export failed: ${String(e.stderr || e.status || e).slice(0, 200)}`)
  process.exit(1)
}
const c = JSON.parse(readFileSync(j, "utf8")) as any[]
rmSync(j, { force: true })
rmSync(`._gaps.${board}.circuit.json`, { force: true })

type Box = { name: string; x0: number; x1: number; y0: number; y1: number }

// name lookup: pcb_component -> source_component.name
const srcName: Record<string, string> = {}
for (const e of c) if (e.type === "source_component") srcName[e.source_component_id] = e.name
const compName: Record<string, string> = {}
for (const e of c) if (e.type === "pcb_component") compName[e.pcb_component_id] = srcName[e.source_component_id] || e.pcb_component_id

// AABB of a rotated rect (rotation in degrees, ccw)
const rectAABB = (cx: number, cy: number, w: number, h: number, deg: number) => {
  const r = (deg * Math.PI) / 180, co = Math.cos(r), si = Math.sin(r)
  const hw = w / 2, hh = h / 2
  let X = 0, Y = 0
  for (const [sx, sy] of [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]]) {
    X = Math.max(X, Math.abs(sx * co - sy * si))
    Y = Math.max(Y, Math.abs(sx * si + sy * co))
  }
  return { x0: cx - X, x1: cx + X, y0: cy - Y, y1: cy + Y }
}

// one body box per component, from its courtyard (rect or outline)
const boxes: Box[] = []
const byComp: Record<string, Box> = {}
for (const e of c) {
  if (e.type === "pcb_courtyard_rect") {
    const b = rectAABB(e.center.x, e.center.y, e.width, e.height, e.ccw_rotation || 0)
    byComp[e.pcb_component_id] = { name: compName[e.pcb_component_id], ...b }
  } else if (e.type === "pcb_courtyard_outline") {
    const pts: { x: number; y: number }[] = e.points || e.route || e.vertices || []
    if (!pts.length) continue
    const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y)
    byComp[e.pcb_component_id] = { name: compName[e.pcb_component_id], x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) }
  }
}
// Merge footprint sub-parts into one body per physical module: U2A/U2B/U2I are
// all the one MCP chip, U1A/U1B the one ESP, etc. Base designator = leading
// letters + number (U2A→U2, J10→J10, R1→R1); union their courtyard AABBs.
const baseDesig = (n: string) => { const m = /^([A-Za-z]+\d+)/.exec(n); return m ? m[1] : n }
const byBase: Record<string, Box> = {}
for (const k in byComp) {
  const bx = byComp[k], bn = baseDesig(bx.name)
  if (!byBase[bn]) byBase[bn] = { name: bn, x0: bx.x0, x1: bx.x1, y0: bx.y0, y1: bx.y1 }
  else {
    byBase[bn].x0 = Math.min(byBase[bn].x0, bx.x0); byBase[bn].x1 = Math.max(byBase[bn].x1, bx.x1)
    byBase[bn].y0 = Math.min(byBase[bn].y0, bx.y0); byBase[bn].y1 = Math.max(byBase[bn].y1, bx.y1)
  }
}
for (const k in byBase) boxes.push(byBase[k])

// board frame
const bd = c.find((e) => e.type === "pcb_board")
const B = { x0: bd.center.x - bd.width / 2, x1: bd.center.x + bd.width / 2, y0: bd.center.y - bd.height / 2, y1: bd.center.y + bd.height / 2 }

// box-to-box edge gap (0 if overlapping); also a signed overlap flag
const gap = (a: Box, b: Box) => {
  const dx = Math.max(b.x0 - a.x1, a.x0 - b.x1, 0)
  const dy = Math.max(b.y0 - a.y1, a.y0 - b.y1, 0)
  const overlap = dx === 0 && dy === 0
  return { d: Math.hypot(dx, dy), overlap }
}
const edgeGap = (a: Box) => Math.min(a.x0 - B.x0, B.x1 - a.x1, a.y0 - B.y0, B.y1 - a.y1)

// nearest neighbour per component + all pairs
const pairs: { a: string; b: string; d: number; overlap: boolean }[] = []
for (let i = 0; i < boxes.length; i++)
  for (let k = i + 1; k < boxes.length; k++) {
    const g = gap(boxes[i], boxes[k])
    pairs.push({ a: boxes[i].name, b: boxes[k].name, d: g.d, overlap: g.overlap })
  }
pairs.sort((p, q) => p.d - q.d)

const nearest: Record<string, { other: string; d: number; overlap: boolean }> = {}
for (const p of pairs) {
  if (!nearest[p.a] || p.d < nearest[p.a].d) nearest[p.a] = { other: p.b, d: p.d, overlap: p.overlap }
  if (!nearest[p.b] || p.d < nearest[p.b].d) nearest[p.b] = { other: p.a, d: p.d, overlap: p.overlap }
}

console.log(`# ${board}: body↔body / body↔edge gaps (target ${target}mm); board ${bd.width.toFixed(1)}×${bd.height.toFixed(1)}mm\n`)
console.log("per component — nearest neighbour, that gap, nearest board-edge gap:")
for (const b of boxes.slice().sort((x, y) => x.name.localeCompare(y.name))) {
  const n = nearest[b.name]
  const eg = edgeGap(b)
  const flag = n.overlap ? " ⚠OVERLAP" : n.d < target ? " ·tight" : ""
  const ef = eg < target ? " ·edge-tight" : ""
  console.log(`  ${b.name.padEnd(4)} → ${(n.other + "").padEnd(4)} ${n.d.toFixed(2)}mm${flag}   edge ${eg.toFixed(2)}mm${ef}`)
}
const overlaps = pairs.filter((p) => p.overlap)
console.log(`\ntightest 12 body↔body pairs:`)
for (const p of pairs.slice(0, 12)) console.log(`  ${p.a.padEnd(4)}↔${p.b.padEnd(4)} ${p.overlap ? "OVERLAP" : p.d.toFixed(2) + "mm"}`)
console.log(`\noverlaps: ${overlaps.length}   min body-edge gap: ${Math.min(...boxes.map(edgeGap)).toFixed(2)}mm`)
