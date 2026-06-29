/**
 * resolve-pours.ts — re-solve every copper pour against the FINISHED circuit-json.
 *
 * tscircuit solves pours at `tsci export` time, on the obstacle board (the 2nd-pass pretty
 * <trace>s stripped to leave their corridors clear for the autorouter). pretty-routes then
 * splices the computed pretty copper (a pcb_trace + a pcb_via per layer change) into that
 * circuit-json AFTER the fact — so the pour breps never saw the pretty traces or their vias
 * and flood straight over them: a pretty trace shorts to its own plane, and every pretty
 * through-via shorts the planes it pierces. circuit-json-to-gerber doesn't solve pours, it
 * just renders the baked geometry, so the short rides all the way to the gerbers.
 *
 * This recomputes each pour brep with the SAME solver core uses (CopperPourPipelineSolver +
 * convertCircuitJsonToInputProblem, including the homesodamachine copper-pour-solver patch),
 * but on the MERGED circuit-json — so the autorouter's copper, the SMD stitch vias, AND the
 * pretty traces/vias are all present, and every foreign trace/via on each plane gets its
 * clearance / antipad. Run it after applyPrettyRoutes, before the gerber conversion.
 *
 * Net antipad/connect decisions come from the real circuit-json connectivity (preserved on
 * the merged elements), so a pour still connects to its own net and rings only foreign copper.
 */
import { readFileSync } from "node:fs"
import path from "node:path"
// untyped JS deps (the same ones @tscircuit/core drives at export time)
// @ts-ignore
import { convertCircuitJsonToInputProblem, CopperPourPipelineSolver, initializeManifoldGeometry } from "@tscircuit/copper-pour-solver"
// @ts-ignore
import { getFullConnectivityMapFromCircuitJson } from "circuit-json-to-connectivity-map"

type PourDecl = {
  name: string
  layer: string
  net: string
  boardEdgeMargin?: number
  clearance?: number
  padMargin?: number
  traceMargin?: number
  cutoutMargin?: number
  outline?: { x: number; y: number }[]
}

const mm = (s?: string) => (s == null ? undefined : parseFloat(String(s).replace("mm", "")))

// Parse the board's <copperpour .../> declarations the way pretty-routes parses <trace>s.
export function findCopperPours(src: string): PourDecl[] {
  const els = src.match(/<copperpour\b[\s\S]*?\/>/g) || []
  return els.map((el) => {
    const attr = (n: string) => (el.match(new RegExp(`\\b${n}="([^"]*)"`)) || [])[1]
    const net = (attr("connectsTo") || "").replace(/^net\./, "")
    let outline: { x: number; y: number }[] | undefined
    const om = el.match(/outline=\{(\[[\s\S]*?\])\}/)
    if (om) {
      try { outline = JSON.parse(om[1]!.replace(/([{,]\s*)(\w+)\s*:/g, '$1"$2":')) } catch {}
    }
    return {
      name: attr("name") || "", layer: attr("layer") || "", net,
      boardEdgeMargin: mm(attr("boardEdgeMargin")), clearance: mm(attr("clearance")),
      padMargin: mm(attr("padMargin")), traceMargin: mm(attr("traceMargin")), cutoutMargin: mm(attr("cutoutMargin")),
      outline,
    }
  })
}

export async function resolvePours(circuit: any[], dir: string, board: string): Promise<any[]> {
  const pours = findCopperPours(readFileSync(path.join(dir, `${board}.tsx`), "utf8"))
  if (!pours.length) return circuit
  // preserve each layer's original soldermask flag (the gerber tool opens a mask over a pour
  // only when covered_with_solder_mask === false — and an inner layer has no mask, so it must
  // match the stale value exactly, never get forced to false). Then drop the stale, pre-splice
  // pour breps; everything else (pads / vias / traces / board) stays.
  const coverByLayer = new Map<string, any>()
  for (const e of circuit) if (e.type === "pcb_copper_pour") coverByLayer.set(e.layer, e.covered_with_solder_mask)
  const out = circuit.filter((e) => e.type !== "pcb_copper_pour")
  const connectivity = getFullConnectivityMapFromCircuitJson(out)
  await initializeManifoldGeometry()
  let n = 0
  for (const p of pours) {
    const sourceNet: any = out.find((e) => e.type === "source_net" && e.name === p.net)
    const source_net_id = sourceNet?.source_net_id
    const clearance = p.clearance ?? 0.2
    const pourKey = (source_net_id ? connectivity.getNetConnectedToId(source_net_id) : undefined) || sourceNet?.subcircuit_connectivity_map_key || ""
    const inputProblem = convertCircuitJsonToInputProblem(out, {
      layer: p.layer,
      pour_connectivity_key: pourKey,
      pad_margin: p.padMargin ?? clearance,
      trace_margin: p.traceMargin ?? clearance,
      board_edge_margin: p.boardEdgeMargin ?? clearance,
      cutout_margin: p.cutoutMargin ?? clearance,
      outline: p.outline,
    })
    const { brep_shapes } = new CopperPourPipelineSolver(inputProblem).getOutput()
    const covered_with_solder_mask = coverByLayer.has(p.layer) ? coverByLayer.get(p.layer) : false
    for (const brep_shape of brep_shapes) {
      out.push({ type: "pcb_copper_pour", pcb_copper_pour_id: `pcb_copper_pour_resolved_${n++}`, shape: "brep", layer: p.layer, brep_shape, source_net_id, covered_with_solder_mask })
    }
    console.log(`[pours] re-solved ${p.name} (${p.layer}/${p.net}): ${brep_shapes.length} brep shape(s)`)
  }
  return out
}
