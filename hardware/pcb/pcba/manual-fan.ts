/**
 * manual-fan.ts — declare a clean fan trace and let tscircuit route it as fixed copper
 * BEFORE the autorouter runs.
 *
 * A board opts a net into a manual fan by net identity, on the <trace> itself:
 *
 *   <trace from=".U4 > .OUT1" to=".J1 > .OUT1" pretty="columnToColumn" />
 *
 * `pretty="<orientation>"` — one of columnToColumn | rowToColumn | columnToRow | rowToRow,
 * read as <sourceLine>To<targetLine>. A COLUMN of pads (stacked in y, shared x) escapes ⟂
 * in x; a ROW (spread in x, shared y) escapes ⟂ in y. Every orientation draws the same
 * shape: a perpendicular escape stub, one 45° diagonal covering the offset, then a
 * perpendicular landing into the target pad — straight → 45° → straight.
 *
 * injectManualFans() computes each fan's bend points from live pad geometry and rewrites
 * the <trace> to carry them as a native `pcbPath`. tscircuit then renders that path as a
 * real pcb_trace in its manual-trace phase — before autorouting — so the copper is:
 *   - not re-routed (the autorouter drops any net that already has a pcb_trace),
 *   - an obstacle the rest of the board routes around, and
 *   - cleared by the copper pour (pours solve last, against every trace).
 * One render does it all; no post-hoc splice, no second autoroute.
 *
 * pcbPath points are expressed in the FROM component's local frame (a point {0,0} lands at
 * that component's center); geometry is computed in board coordinates and mapped back
 * through the component's center+rotation, so it holds under any rotation and regenerates
 * from live placement every build — nothing is frozen into the source.
 */
import { readFileSync, writeFileSync, rmSync } from "node:fs"
import path from "node:path"
import {
  compose,
  translate,
  rotate,
  inverse,
  applyToPoint,
  type Matrix,
} from "transformation-matrix"

// circuit-json exporter the caller supplies (render-board reuses its tsci runner).
export type ExportCircuitJson = (name: string) => Promise<any[]>

export type Orientation =
  | "columnToColumn"
  | "rowToColumn"
  | "columnToRow"
  | "rowToRow"
const ORIENTATIONS: Orientation[] = [
  "columnToColumn",
  "rowToColumn",
  "columnToRow",
  "rowToRow",
]

// Length (mm) of the perpendicular escape stub off the source pad and the perpendicular
// landing into the target pad. The 45° diagonal covers everything in between.
const STUB = 1

type Pt = { x: number; y: number }
type Fan = { el: string; from: string; to: string; orientation: string }

const attrOf = (el: string, name: string) =>
  (el.match(new RegExp(`\\b${name}="([^"]*)"`)) || [])[1] || ""
// ".J1 > .OUT1" -> "J1.OUT1" (the form pads are keyed by)
const toDot = (sel: string) => sel.replace(/^\./, "").replace(/\s*>\s*\./, ".")

// Every self-closing <trace .../> that carries a pretty= attribute. Non-greedy to the
// first "/>", since from/to selectors contain ">" (e.g. ".J1 > .OUT1").
export function findFanTraces(src: string): Fan[] {
  return (src.match(/<trace\b[\s\S]*?\/>/g) || [])
    .filter((el) => /\bpretty="/.test(el))
    .map((el) => ({
      el,
      from: attrOf(el, "from"),
      to: attrOf(el, "to"),
      orientation: attrOf(el, "pretty"),
    }))
}

// "Comp.pin" -> global {x,y} (from smtpads + plated holes), and "Comp" -> its placement
// (center + rotation, for mapping board coordinates into the component's local frame).
export function padGeometry(circuit: any[]): {
  pads: Record<string, Pt>
  comps: Record<string, { center: Pt; rotation: number }>
} {
  const sp: any = {},
    pp: any = {},
    sc: any = {}
  for (const e of circuit) {
    if (e.type === "source_port") sp[e.source_port_id] = e
    if (e.type === "pcb_port") pp[e.pcb_port_id] = e
    if (e.type === "source_component") sc[e.source_component_id] = e
  }
  const pads: Record<string, Pt> = {}
  for (const h of circuit.filter(
    (e) => e.type === "pcb_smtpad" || e.type === "pcb_plated_hole",
  )) {
    const p = pp[h.pcb_port_id]
    if (!p) continue
    const o = sp[p.source_port_id]
    if (!o) continue
    const nm = o.name || (o.port_hints || []).find((x: string) => !/^\d+$/.test(x))
    if (nm)
      pads[`${sc[o.source_component_id].name}.${nm}`] = {
        x: +h.x.toFixed(4),
        y: +h.y.toFixed(4),
      }
  }
  const comps: Record<string, { center: Pt; rotation: number }> = {}
  for (const c of circuit.filter((e) => e.type === "pcb_component")) {
    const s = sc[c.source_component_id]
    if (!s) continue
    comps[s.name] = { center: { x: c.center.x, y: c.center.y }, rotation: c.rotation || 0 }
  }
  return { pads, comps }
}

const monotone = (vals: number[], sgn: number) =>
  vals.every((v, i) => i === 0 || sgn * (v - vals[i - 1]) >= -1e-6)

/**
 * The two bend points of a clean fan, in board coordinates — the escape corner (end of the
 * perpendicular stub) and the diagonal corner (end of the 45° run, start of the landing).
 * The source and target pads are the route's endpoints; tscircuit adds them itself, so only
 * the two interior corners go in the pcbPath.
 *
 * Returns null when the fixed shape can't reach the target without backtracking — e.g. a
 * diverging fan whose vertical offset exceeds its horizontal gap. The caller then leaves the
 * <trace> plain (autorouted) rather than emit overshooting copper.
 */
export function fanWaypoints(s: Pt, t: Pt, orientation: string, stub = STUB): Pt[] | null {
  const sgx = Math.sign(t.x - s.x) || 1
  const sgy = Math.sign(t.y - s.y) || 1
  let p1: Pt, p2: Pt
  if (orientation === "columnToColumn") {
    // escape x, land x — diagonal spans y
    const x1 = s.x + sgx * stub
    p1 = { x: x1, y: s.y }
    p2 = { x: x1 + sgx * Math.abs(t.y - s.y), y: t.y }
  } else if (orientation === "rowToRow") {
    // escape y, land y — diagonal spans x
    const y1 = s.y + sgy * stub
    p1 = { x: s.x, y: y1 }
    p2 = { x: t.x, y: y1 + sgy * Math.abs(t.x - s.x) }
  } else if (orientation === "rowToColumn") {
    // escape y, land x
    const y1 = s.y + sgy * stub
    p1 = { x: s.x, y: y1 }
    p2 = { x: s.x + sgx * Math.abs(t.y - y1), y: t.y }
  } else if (orientation === "columnToRow") {
    // escape x, land y
    const x1 = s.x + sgx * stub
    p1 = { x: x1, y: s.y }
    p2 = { x: t.x, y: s.y + sgy * Math.abs(t.x - x1) }
  } else {
    throw new Error(
      `[manual-fan] unknown orientation "${orientation}" (expected ${ORIENTATIONS.join(" | ")})`,
    )
  }
  // A clean fan never backtracks: x and y must each progress monotonically source→target
  // across pad → escape → diagonal → land. If not, the fixed shape doesn't fit here.
  const xs = [s.x, p1.x, p2.x, t.x]
  const ys = [s.y, p1.y, p2.y, t.y]
  if (!monotone(xs, sgx) || !monotone(ys, sgy)) return null
  return [p1, p2]
}

// board point -> the FROM component's local frame (global = center + R(rot)·local).
const toLocal = (Tinv: Matrix, p: Pt): Pt => {
  const q = applyToPoint(Tinv, p)
  return { x: +q.x.toFixed(4), y: +q.y.toFixed(4) }
}

/**
 * Rewrite the board source so every `pretty=` fan carries a native `pcbPath`, and return
 * the basename of the .tsx to render. With no fan traces, returns `board` unchanged (the
 * caller renders the original). A fan whose pads/placement can't be found, or whose fixed
 * shape doesn't fit, is left plain (a warning, then the autorouter handles it).
 *
 * The pad geometry comes from one fast placement export (traces + pours stripped), so the
 * bend points track live placement; moving a part re-fans it next build.
 */
export async function injectManualFans(
  dir: string,
  board: string,
  exportCJ: ExportCircuitJson,
): Promise<string> {
  const src = readFileSync(path.join(dir, `${board}.tsx`), "utf8")
  const fans = findFanTraces(src)
  if (!fans.length) return board

  // Placement export: strip every trace + pour so only pad/footprint geometry is computed
  // (no routing, no pour solve) — fast, and all we need to place the fans.
  const placeSrc = src
    .replace(/<trace\b[\s\S]*?\/>/g, "")
    .replace(/<copperpour\b[\s\S]*?\/>/g, "")
  const placeName = `_build-${board}.fan-place.tmp`
  writeFileSync(path.join(dir, `${placeName}.tsx`), placeSrc)
  let circuit: any[]
  try {
    circuit = await exportCJ(placeName)
  } finally {
    rmSync(path.join(dir, `${placeName}.tsx`), { force: true })
    rmSync(path.join(dir, `${placeName}.circuit.json`), { force: true })
  }
  const { pads, comps } = padGeometry(circuit)

  let out = src
  let placed = 0
  for (const fan of fans) {
    const fromKey = toDot(fan.from)
    const toKey = toDot(fan.to)
    const s = pads[fromKey]
    const t = pads[toKey]
    const comp = comps[fromKey.split(".")[0]]
    if (!s || !t || !comp) {
      console.error(
        `[manual-fan] ${fan.from} -> ${fan.to}: missing ${!s ? "from pad" : !t ? "to pad" : "from component"} — left plain (autorouted)`,
      )
      continue
    }
    const wps = fanWaypoints(s, t, fan.orientation)
    if (!wps) {
      console.error(
        `[manual-fan] ${fan.from} -> ${fan.to} (${fan.orientation}): fixed fan doesn't fit (offset exceeds gap) — left plain (autorouted)`,
      )
      continue
    }
    const Tinv = inverse(
      compose(
        translate(comp.center.x, comp.center.y),
        rotate((comp.rotation * Math.PI) / 180),
      ),
    )
    const local = wps.map((p) => toLocal(Tinv, p))
    const pcbPath = `pcbPathRelativeTo="${fan.from}" pcbPath={${JSON.stringify(local)}}`
    const rewritten = fan.el.replace(/\s*pretty="[^"]*"/, ` ${pcbPath}`)
    // function replacer: the rewritten element is literal text, never a $-pattern
    out = out.replace(fan.el, () => rewritten)
    placed++
  }

  if (!placed) {
    // Every fan fell back to plain — nothing rewritten; render the original board.
    return board
  }
  const outName = `_build-${board}.manual-fan.tmp`
  writeFileSync(path.join(dir, `${outName}.tsx`), out)
  console.log(
    `[manual-fan] placed ${placed}/${fans.length} fan(s) as pre-autoroute pcbPath copper`,
  )
  return outName
}
