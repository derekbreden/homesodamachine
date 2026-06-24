/**
 * Distill a board's pickable entities from its circuit JSON into
 * out/<board>.picks.json — the semantic layer the web viewer's pad picker
 * hit-tests against. The rendered copper SVGs are anonymous Gerber geometry;
 * this carries the identity (component ref, pin, net) and position for each
 * pad so a click can name what it landed on.
 *
 *   bun pick-data.ts <board.tsx>
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

const arg = process.argv[2]
if (!arg) {
  console.error("usage: bun pick-data.ts <board.tsx>")
  process.exit(1)
}
const boardFile = path.resolve(arg)
const dir = path.dirname(boardFile)
const board = path.basename(boardFile).replace(/\.tsx$/, "")
const tsci = path.join(dir, "node_modules", ".bin", "tsci")

// Export circuit JSON transiently to distill picks. tsci resolves -o relative
// to cwd and mangles an absolute path (see render-board.ts), so hand it a
// cwd-relative target inside the board dir, then read and remove it.
const cjRel = `.${board}.circuit.tmp.json`
const cjAbs = path.join(dir, cjRel)
try {
  execFileSync(tsci, ["export", "-f", "circuit-json", "-o", cjRel, `${board}.tsx`], {
    cwd: dir,
    stdio: ["ignore", "pipe", "pipe"],
  })
  const circuit = JSON.parse(readFileSync(cjAbs, "utf8"))
  const data = distill(circuit)
  const outPath = path.join(dir, "out", `${board}.picks.json`)
  writeFileSync(outPath, JSON.stringify(data))
  console.log(`[${board}] wrote ${board}.picks.json — ${data.pads.length} pads`)
} finally {
  rmSync(cjAbs, { force: true })
}

function distill(circuit: any[]) {
  const compName: Record<string, string> = {}
  const srcPort: Record<string, any> = {}
  const pcbPort: Record<string, any> = {}
  const netByKey: Record<string, string> = {}

  for (const e of circuit) {
    if (e.type === "source_component") compName[e.source_component_id] = e.name
    else if (e.type === "source_port") srcPort[e.source_port_id] = e
    else if (e.type === "pcb_port") pcbPort[e.pcb_port_id] = e
    else if (e.type === "source_net") netByKey[e.subcircuit_connectivity_map_key] = e.name
  }

  // Resolve a pcb pad's identity through pcb_port -> source_port -> component,
  // and its net through the port's shared connectivity key.
  const identify = (pcbPortId: string | undefined) => {
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

  const pads: any[] = []
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

  return { board, unitsPerMm: 1000, pads }
}

function round(n: number) {
  return Math.round(n * 1000) / 1000
}
