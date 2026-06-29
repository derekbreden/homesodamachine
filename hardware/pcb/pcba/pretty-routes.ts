/**
 * pretty-routes.ts — the build stage that turns declared intent into copper.
 *
 * A board declares 2nd-pass routing inline, by net identity:
 *
 *   <trace from=".U2 > .GPA0" to=".U4 > .IN8" pretty="clean:fanRowToColumn" />
 *
 * `pretty="clean:<fanType>"`. At build time applyPrettyRoutes() (called by render-board)
 * autoroutes the rest of the board, routes the pretty nets in-process against that field
 * (pretty-router.ts), and returns a FINISHED circuit-json — the autoroutes plus the
 * computed copper spliced in — which render-board converts straight to gerbers. No
 * throwaway .tsx, no second autoroute (see applyPrettyRoutes below).
 *
 *   clean:<fanType>  riser + 45° fan (fanRowToColumn | fanColumnToRow | fanColumnToColumn
 *                    | fanRowToRow — fan<sourceLine>To<targetLine>). variant IS the fan
 *                    type; `from` is the riser source.
 *
 * The point: routes regenerate every build from live geometry, so moving a part just
 * re-routes it. No coordinates are frozen into the source. The net list comes from the
 * .tsx, so adding a signal is one <trace ... pretty=...> line.
 */
import { cleanFanRoute, cleanPads, monoWarn, type FanType } from "./pretty-router"
import { readFileSync, writeFileSync, rmSync } from "node:fs"
import path from "node:path"

// clean-fan clearance (mm): the edge-to-edge gap a fan diagonal keeps from other copper
// when deciding whether to drop to the bottom layer.
const CLR = 0.25

// circuit-json exporter the caller supplies (render-board reuses its tsci runner).
export type ExportCircuitJson = (tsxBasename: string) => Promise<any[]>

type Pretty = { el: string; from: string; to: string; strategy: string; variant: string; viaLayer: string }

const attrOf = (el: string, name: string) => (el.match(new RegExp(`\\b${name}="([^"]*)"`)) || [])[1] || ""
// ".J5 > .IO25" -> "J5.IO25" (the form the router labels pads with)
const toDot = (sel: string) => sel.replace(/^\./, "").replace(/\s*>\s*\./, ".")

export function findPrettyTraces(src: string): Pretty[] {
  // match each self-closing <trace .../> (non-greedy to the first "/>", since the
  // from/to selectors contain ">" e.g. ".J5 > .IO25"), then keep the pretty ones.
  const els = (src.match(/<trace\b[\s\S]*?\/>/g) || []).filter((el) => /\bpretty="/.test(el))
  return els.map((el) => {
    // pretty="<strategy>:<variant>[@<layer>]" — an optional @layer suffix forces a clean fan
    // onto a plane layer (e.g. clean:fanRowToColumn@inner1), routing its whole crossing there.
    const [strategy, spec] = attrOf(el, "pretty").split(":")
    const [variant, viaLayer] = (spec || "").split("@")
    return { el, from: attrOf(el, "from"), to: attrOf(el, "to"), strategy: strategy || "", variant: variant || "", viaLayer: viaLayer || "" }
  })
}

/**
 * The 2nd-pass router as a TWO-step pipeline, returning a finished circuit-json:
 *
 *   1. AUTOROUTER FIRST — export the board with every pretty <trace> removed, so the
 *      autorouter routes only the non-pretty nets and leaves the pretty corridors clear.
 *   2. OUR ROUTER AFTER — route the pretty nets against that autorouted field. Clean fans
 *      keep a FIXED straight → 45° → straight XY shape (no search), but are obstacle-aware
 *      in Z: a diagonal that would cross top copper (a trace or another part's SMD pad)
 *      drops to the bottom layer (a via at each end). Nothing overlaps, by construction.
 *   3. STOP — splice our copper (a pcb_trace + a pcb_via per layer change, per net) into
 *      the autorouted circuit-json and return it. The caller converts THIS straight to
 *      gerbers; the autorouter never runs again.
 *
 * Step 3 is the whole point. Re-exporting through tscircuit re-autoroutes the non-pretty
 * nets (it can't see injected copper) and the re-route crosses the pretty copper — that
 * was every short. Returning finished circuit-json avoids any second autoroute. With no
 * pretty traces, returns the board's own circuit-json (the autorouter routed everything).
 */
export async function applyPrettyRoutes(dir: string, board: string, exportCJ: ExportCircuitJson): Promise<any[]> {
  const src = readFileSync(path.join(dir, `${board}.tsx`), "utf8")
  const pretties = findPrettyTraces(src)
  if (!pretties.length) return exportCJ(board) // no 2nd-pass nets: autoroute everything, render that

  // ── STEP 1: autorouter first. Obstacle field = the board with every pretty <trace>
  // removed. A trace that is a .map() arrow body becomes `null`; a standalone child is cut. ──
  let obstacleSrc = src
  for (const p of pretties) {
    const i = obstacleSrc.indexOf(p.el)
    if (i < 0) continue
    const repl = obstacleSrc.slice(0, i).trimEnd().endsWith("=>") ? "null" : ""
    obstacleSrc = obstacleSrc.slice(0, i) + repl + obstacleSrc.slice(i + p.el.length)
  }
  const obsName = `_build-${board}.pretty-obstacle.tmp`
  writeFileSync(path.join(dir, `${obsName}.tsx`), obstacleSrc)
  let obstacle: any[]
  try {
    obstacle = await exportCJ(obsName)
  } finally {
    rmSync(path.join(dir, `${obsName}.tsx`), { force: true })
    rmSync(path.join(dir, `${obsName}.circuit.json`), { force: true })
  }

  // ── STEP 2: our router after, avoiding the autoroutes. ──
  for (const p of pretties) if (p.strategy !== "clean") throw new Error(`[pretty] unknown strategy "${p.strategy}" (${p.from} -> ${p.to}) — only clean fans are supported`)
  const routedNets: ReturnType<typeof cleanFanRoute>[] = []

  // clean fans: pure geometry, NOT a search. The autorouter ran first and left these
  // corridors clear, so each net draws straight → 45° → straight on one layer, no vias.
  const cleanNets = pretties.filter((p) => p.strategy === "clean")
  if (cleanNets.length) {
    const pads = cleanPads(obstacle)
    const fanGroups = new Map<string, Pretty[]>()
    for (const p of cleanNets) { const k = `${p.variant}@${p.viaLayer}|${toDot(p.from).split(".")[0]}->${toDot(p.to).split(".")[0]}`; (fanGroups.get(k) ?? fanGroups.set(k, []).get(k)!).push(p) }
    for (const [k, ps] of fanGroups) {
      const ft = ps[0]!.variant as FanType
      const pairs = ps.map((p) => ({ from: toDot(p.from), to: toDot(p.to) }))
      // monotonicity axes: source pads spread along their line (ROW→x, COLUMN→y), and the
      // target pads must track monotonically along theirs, or risers cross.
      const MONO: Record<FanType, ["x" | "y", "x" | "y"]> = {
        fanRowToColumn: ["x", "y"], fanColumnToRow: ["y", "x"],
        fanColumnToColumn: ["y", "y"], fanRowToRow: ["x", "x"],
      }
      const [sax, tax] = MONO[ft]
      monoWarn(pairs, pads, sax, tax, k)
      // Z-aware: pass the autoroutes so a fan diagonal that would cross top copper (a trace
      // or another part's SMD pad) drops to the bottom layer instead of shorting. XY stays
      // fixed. A viaLayer (from an @layer suffix) instead runs the whole crossing on a plane.
      const viaLayer = ps[0]!.viaLayer || undefined
      for (const { from, to } of pairs) routedNets.push(cleanFanRoute(pads, from, to, { fanType: ft, viaLayer, field: obstacle, clr: CLR }))
    }
  }

  // ── STEP 3: STOP. Splice our copper into the autorouted circuit-json — a pcb_trace per
  // net plus a pcb_via for each layer change — and return it. No re-export, no 2nd autoroute. ──
  const extra: any[] = []
  let vias = 0
  routedNets.forEach((rn, i) => {
    extra.push({ type: "pcb_trace", pcb_trace_id: `pcb_trace_pretty_${i}`, route: rn.route })
    rn.route.forEach((p, j) => {
      if (p.route_type !== "via") return
      vias++
      extra.push({ type: "pcb_via", pcb_via_id: `pcb_via_pretty_${i}_${j}`, pcb_trace_id: `pcb_trace_pretty_${i}`, x: p.x, y: p.y, hole_diameter: 0.3, outer_diameter: 0.5, layers: [p.from_layer, p.to_layer], from_layer: p.from_layer, to_layer: p.to_layer })
    })
  })
  console.log(`[pretty] step1 autoroute + step2 ${cleanNets.length} clean fan(s): spliced ${routedNets.length} net(s) (${vias} via) into the circuit-json — no 2nd autoroute`)
  return obstacle.concat(extra)
}
