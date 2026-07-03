/**
 * Distill a board's pickable entities from its circuit JSON into
 * out/<board>.picks.json — the semantic layer the web viewer's pad picker
 * hit-tests against. The rendered copper SVGs are anonymous Gerber geometry;
 * this carries the identity (component ref, pin, net) and position for each
 * pad so a click can name what it landed on. It also carries the board readout the
 * viewer's dims chip shows — size, and (via clearance.ts) the copper clearance floor +
 * the genuine overlap/DRC errors.
 *
 *   bun pick-data.ts <board.tsx> [circuit.json]
 *
 * If a pre-exported circuit-json path is given (render-board passes the one it
 * already exported), it's read directly — no second build. Otherwise this
 * exports its own transiently.
 *
 * Positions are in board millimetres (circuit-json native). The viewer maps mm
 * onto the SVG by the same `scale(1,-1)` Gerber-unit frame the views use
 * (1 mm = 1000 SVG units), reading the transform straight off the SVG. Run by
 * render-board.ts after the views regenerate, so picks stay in lockstep with
 * the copper.
 */
import { execFileSync } from "node:child_process"
import { readFileSync, writeFileSync, rmSync } from "node:fs"
import path from "node:path"
import { pathToFileURL } from "node:url"
import { analyzeClearance } from "./clearance"
import { auditDecoupling, type DecouplingRule } from "./cap-audit"
import type { PicksFile, Pad, Via, Trace, PadIdentity } from "../../../web/contracts/picks-schema"

const arg = process.argv[2]
if (!arg) {
  console.error("usage: bun pick-data.ts <board.tsx>")
  process.exit(1)
}
const boardFile = path.resolve(arg)
const dir = path.dirname(boardFile)
const board = path.basename(boardFile).replace(/\.tsx$/, "")
const tsci = path.join(dir, "node_modules", ".bin", "tsci")

// Use a caller-supplied circuit-json if given (render-board already exported
// one); else export transiently. tsci resolves -o relative to cwd and mangles
// an absolute path (see render-board.ts), so a self-export stays cwd-relative.
const given = process.argv[3]
const cjRel = given ?? `.${board}.circuit.tmp.json`
const cjAbs = path.isAbsolute(cjRel) ? cjRel : path.join(dir, cjRel)
try {
  if (!given) {
    execFileSync(tsci, ["export", "-f", "circuit-json", "-o", cjRel, `${board}.tsx`], {
      cwd: dir,
      stdio: ["ignore", "pipe", "pipe"],
    })
  }
  const circuit = JSON.parse(readFileSync(cjAbs, "utf8"))
  const decoupling = await loadDecoupling(boardFile)
  const data = distill(circuit, decoupling)
  const outPath = path.join(dir, "out", `${board}.picks.json`)
  writeFileSync(outPath, JSON.stringify(data))
  console.log(`[${board}] wrote ${board}.picks.json — ${data.pads.length} pads`)
} finally {
  if (!given) rmSync(cjAbs, { force: true })
}

// A board may export a `decoupling` table (which support cap serves which part). Import it
// from the board module so the audit's intent lives with the design, not here — this distiller
// stays board-agnostic. Best-effort: a board that exports none simply gets no cap audit.
async function loadDecoupling(file: string): Promise<DecouplingRule[]> {
  try {
    const mod: any = await import(pathToFileURL(file).href)
    return Array.isArray(mod.decoupling) ? mod.decoupling : []
  } catch {
    return []
  }
}

function distill(circuit: any[], decoupling: DecouplingRule[] = []): PicksFile {
  const compName: Record<string, string> = {}
  const srcPort: Record<string, any> = {}
  const pcbPort: Record<string, any> = {}
  const netByKey: Record<string, string> = {}
  const netById: Record<string, string> = {}

  for (const e of circuit) {
    if (e.type === "source_component") compName[e.source_component_id] = e.name
    else if (e.type === "source_port") srcPort[e.source_port_id] = e
    else if (e.type === "pcb_port") pcbPort[e.pcb_port_id] = e
    else if (e.type === "source_net") {
      netByKey[e.subcircuit_connectivity_map_key] = e.name
      netById[e.source_net_id] = e.name
    }
  }

  // Resolve a pcb pad's identity through pcb_port -> source_port -> component,
  // and its net through the port's shared connectivity key.
  const identify = (pcbPortId: string | undefined): PadIdentity => {
    const pp = pcbPortId ? pcbPort[pcbPortId] : null
    const sp = pp ? srcPort[pp.source_port_id] : null
    if (!sp) return { ref: null, pin: null, pinNum: null, net: null }
    return {
      ref: compName[sp.source_component_id] ?? null,
      pin: sp.name ?? null,
      pinNum: sp.pin_number ?? null,
      net: netByKey[sp.subcircuit_connectivity_map_key] ?? null,
    }
  }

  const pads: Pad[] = []
  for (const e of circuit) {
    if (e.type === "pcb_plated_hole") {
      const id = identify(e.pcb_port_id)
      pads.push({
        x: round(e.x), y: round(e.y),
        ...id,
        kind: "through-hole",
        hole: e.hole_diameter ?? e.hole_width ?? null,
        pad: e.outer_diameter ?? e.rect_pad_width ?? null,
        shape: e.shape ?? null,
      })
    } else if (e.type === "pcb_smtpad") {
      const id = identify(e.pcb_port_id)
      pads.push({
        x: round(e.x), y: round(e.y),
        ...id,
        kind: "smt-pad",
        pad: e.width ?? e.radius ?? null,
        shape: e.shape ?? null,
      })
    }
  }

  // Traces carry a net (connection_name is a source_net id) and, on their first
  // and last route points, the ports they run between → endpoint pads. The 2D
  // polyline is every route point; layer hops at vias are flattened away.
  const traceNet = (t: any) => netById[t.connection_name] ?? t.connection_name ?? null
  const traceNetByPcbId: Record<string, string | null> = {}
  const traces: Trace[] = []
  for (const e of circuit) {
    if (e.type !== "pcb_trace") continue
    traceNetByPcbId[e.pcb_trace_id] = traceNet(e)
    const wire = e.route.filter((r: any) => r.x != null && r.y != null)
    const startId = e.route.find((r: any) => r.start_pcb_port_id)?.start_pcb_port_id
    const endId = e.route.find((r: any) => r.end_pcb_port_id)?.end_pcb_port_id
    const a = startId ? identify(startId) : null
    const b = endId ? identify(endId) : null
    traces.push({
      net: traceNet(e),
      from: a && a.ref ? `${a.ref}.${a.pin}` : null,
      to: b && b.ref ? `${b.ref}.${b.pin}` : null,
      width: wire[0]?.width ?? null,
      points: wire.map((r: any): [number, number] => [round(r.x), round(r.y)]),
    })
  }

  // Vias are points; their net comes from the trace they belong to.
  const vias: Via[] = []
  for (const e of circuit) {
    if (e.type !== "pcb_via") continue
    vias.push({
      x: round(e.x), y: round(e.y),
      net: traceNetByPcbId[e.pcb_trace_id] ?? null,
      fromLayer: e.from_layer ?? null,
      toLayer: e.to_layer ?? null,
      outer: e.outer_diameter ?? null,
    })
  }

  // Board outer dimensions (mm), straight off the board element — the
  // authoritative size the viewer shows and the fab cuts to. Dynamic: it
  // tracks whatever the source declares, so a resize updates the readout.
  const boardEl = circuit.find((e) => e.type === "pcb_board")
  const size =
    boardEl && boardEl.width && boardEl.height
      ? { width: round(boardEl.width), height: round(boardEl.height) }
      : null

  // Discrete-copper clearance floor + the genuine DRC findings (clearance.ts), for the
  // viewer's board readout. Both derive from the same routed circuit-json.
  const { floor, tight, errors } = analyzeClearance(circuit)

  // Cap decoupling audit (cap-audit.ts): how close each declared support cap sits to the part
  // it serves, measured from the same placed pads. Advisory placement quality — kept separate
  // from the DRC `errors`, which are manufacturability.
  const capAudit = decoupling.length ? auditDecoupling(decoupling, pads) : null

  return { board, unitsPerMm: 1000, size, pads, vias, traces, clearance: { floor, tight }, errors, capAudit }
}

function round(n: number) {
  return Math.round(n * 1000) / 1000
}
