/**
 * pretty-routes.ts — the build stage that turns declared intent into copper.
 *
 * A board declares 2nd-pass routing inline, by net identity:
 *
 *   <trace from=".J5 > .IO25"  to=".U1A > .IO25" pretty="maze:j5" />
 *   <trace from=".U2 > .GPA0"  to=".U4 > .IN8"   pretty="clean:fanRowToColumn" />
 *
 * `pretty="<strategy>:<variant>"`. At build time applyPrettyRoutes() (called by
 * render-board) collects those traces, routes them with the in-process router
 * (pretty-router.ts), and writes a throwaway "routed" .tsx — the board with the
 * pretty attrs stripped and the computed <pcbtrace> copper injected — which the rest
 * of the build renders.
 *
 *   maze:<group>     obstacle-aware A*. variant names a MAZE_GROUPS window below.
 *   clean:<fanType>  riser + 45° fan (fanRowToColumn | fanColumnToColumn). variant
 *                    IS the fan type; `from` is the riser source.
 *
 * The point: routes regenerate every build from live geometry, so moving a part just
 * re-routes it. No coordinates are frozen into the source, and the coordinate carve
 * can never go stale (it is always fed routes that land on the current pads). The net
 * list comes from the .tsx, so adding a signal is one <trace ... pretty=...> line.
 */
import { mazeRouteNets, cleanPads, monoWarn, routedNetToJSX, type MazeSpec, type FanType } from "./pretty-router"
import { readFileSync, writeFileSync, rmSync } from "node:fs"
import path from "node:path"

// maze search windows. The region can be wider than the pads' bounding box where a
// route must detour (e.g. J5.IO19 swings right of BT1's clip). Params match COMMON.
const COMMON = { cell: 0.1, clr: 0.25, width: 0.2, viaCost: 60, startLayer: "top", turn: 12 }
const MAZE_GROUPS: Record<string, MazeSpec> = {
  j5: { ...COMMON, region: { x0: -44, x1: -13, y0: -47, y1: 14 } },
  faucet485: { ...COMMON, region: { x0: -52, x1: -12, y0: 6, y1: 45 } },
}

// circuit-json exporter the caller supplies (render-board reuses its tsci runner).
export type ExportCircuitJson = (tsxBasename: string) => Promise<any[]>

type Pretty = { el: string; from: string; to: string; strategy: string; variant: string }

const attrOf = (el: string, name: string) => (el.match(new RegExp(`\\b${name}="([^"]*)"`)) || [])[1] || ""
// ".J5 > .IO25" -> "J5.IO25" (the form the router labels pads with)
const toDot = (sel: string) => sel.replace(/^\./, "").replace(/\s*>\s*\./, ".")

// A circuit-json pcb_trace.route -> a fixed <pcbtrace>, so the obstacle pass's already
// routed copper can be frozen into the final build (eliminating the second autoroute).
const pcbTraceRouteToJSX = (route: any[]): string => {
  const body = route
    .map((p) =>
      p.route_type === "via"
        ? `{route_type:"via",x:${p.x},y:${p.y},from_layer:${JSON.stringify(p.from_layer)},to_layer:${JSON.stringify(p.to_layer)}}`
        : `{route_type:"wire",x:${p.x},y:${p.y},width:${p.width ?? 0.2},layer:${JSON.stringify(p.layer)}}`,
    )
    .join(",\n      ")
  return `    <pcbtrace route={[\n      ${body},\n    ]} />`
}

export function findPrettyTraces(src: string): Pretty[] {
  // match each self-closing <trace .../> (non-greedy to the first "/>", since the
  // from/to selectors contain ">" e.g. ".J5 > .IO25"), then keep the pretty ones.
  const els = (src.match(/<trace\b[\s\S]*?\/>/g) || []).filter((el) => /\bpretty="/.test(el))
  return els.map((el) => {
    const [strategy, variant] = attrOf(el, "pretty").split(":")
    return { el, from: attrOf(el, "from"), to: attrOf(el, "to"), strategy: strategy || "", variant: variant || "" }
  })
}

/**
 * Resolve a board's pretty-routes into a routed temp .tsx and return it alongside
 * the obstacle circuit-json (the board stripped of pretty nets). The caller reuses
 * that circuit-json for back-silk synthesis and pick-data so it doesn't need its
 * own tsci export. Returns the board unchanged when there are no pretty traces.
 */
export async function applyPrettyRoutes(dir: string, board: string, exportCJ: ExportCircuitJson): Promise<{ routedName: string; obstacleCircuitJson: any[] | null }> {
  const src = readFileSync(path.join(dir, `${board}.tsx`), "utf8")
  const pretties = findPrettyTraces(src)
  if (!pretties.length) return { routedName: board, obstacleCircuitJson: null }

  // Obstacle field: the board with every pretty <trace> removed, so the autorouter
  // leaves those corridors clear. (Non-pretty nets route identically here and in the
  // final routed render, since the pretty nets are carved there too.) A trace that is a
  // .map() arrow body becomes `null` (valid, renders nothing); a standalone child is cut.
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

  const jsx: string[] = []
  for (const p of pretties) if (p.strategy !== "maze" && p.strategy !== "clean") throw new Error(`[pretty] unknown strategy "${p.strategy}" (${p.from} -> ${p.to})`)

  // ── maze groups: route hardest(longest)-first, deterministically, accumulating
  // each group's copper into the field so later groups avoid it. ──
  const xy: Record<string, { x: number; y: number }> = cleanPads(obstacle)
  const len = (p: Pretty) => { const a = xy[toDot(p.from)], b = xy[toDot(p.to)]; return a && b ? Math.abs(a.x - b.x) + Math.abs(a.y - b.y) : 0 }
  const mazeGroups = new Map<string, Pretty[]>()
  for (const p of pretties) if (p.strategy === "maze") (mazeGroups.get(p.variant) ?? mazeGroups.set(p.variant, []).get(p.variant)!).push(p)
  let field = obstacle, obsId = 0
  for (const key of [...mazeGroups.keys()].sort()) {
    const ps = mazeGroups.get(key)!
    const cfg = MAZE_GROUPS[key]
    if (!cfg) throw new Error(`[pretty] no MAZE_GROUPS window for "${key}" (${ps.length} net(s): ${ps.map((p) => `${p.from}->${p.to}`).join(", ")})`)
    const ordered = [...ps].sort((a, b) => len(b) - len(a) || toDot(a.from).localeCompare(toDot(b.from)))
    const pairs = ordered.map((p) => ({ from: toDot(p.from), to: toDot(p.to) }))
    const routed = mazeRouteNets(field, pairs, cfg)
    if (routed.length !== pairs.length) throw new Error(`[pretty] maze group ${key}: routed only ${routed.length}/${pairs.length} nets — widen the region or check for obstacles`)
    for (const rn of routed) { jsx.push(routedNetToJSX(rn)); field = field.concat([{ type: "pcb_trace", pcb_trace_id: `_pretty_obs_${obsId++}`, route: rn.route }]) }
  }

  // ── clean fans: the SAME obstacle-aware router as the maze, in "fan" style — biased
  // toward a tidy riser + 45° landing, but it detours / dips to the other layer (via) to
  // dodge copper, so a fan never shorts an autoroute. Routed per group against the
  // accumulating field (which already carries the autoroutes + the maze copper); each
  // routed fan joins the field so the next group + the autorouter-free render avoid it. ──
  const cleanNets = pretties.filter((p) => p.strategy === "clean")
  if (cleanNets.length) {
    const pads = cleanPads(obstacle)
    const fanGroups = new Map<string, Pretty[]>()
    for (const p of cleanNets) { const k = `${p.variant}|${toDot(p.from).split(".")[0]}->${toDot(p.to).split(".")[0]}`; (fanGroups.get(k) ?? fanGroups.set(k, []).get(k)!).push(p) }
    for (const [k, ps] of fanGroups) {
      const ft = ps[0]!.variant as FanType
      const pairs = ps.map((p) => ({ from: toDot(p.from), to: toDot(p.to) }))
      if (ft === "fanRowToColumn") monoWarn(pairs, pads, "x", "y", k)
      else monoWarn(pairs, pads, "y", "x", k)
      const routed = mazeRouteNets(field, pairs, { ...COMMON, style: "fan", fanType: ft, margin: 5 })
      if (routed.length !== pairs.length) throw new Error(`[pretty] fan group ${k}: routed only ${routed.length}/${pairs.length} nets — corridor fully blocked`)
      for (const rn of routed) { jsx.push(routedNetToJSX(rn)); field = field.concat([{ type: "pcb_trace", pcb_trace_id: `_fan_obs_${obsId++}`, route: rn.route }]) }
    }
  }

  // ── collapse the second autoroute ──
  // The obstacle pass already routed every non-pretty net, and BOTH the maze and the
  // (now obstacle-aware) fans routed AROUND that copper — so nothing overlaps. Freeze
  // those routes in as fixed <pcbtrace> too: the final export then has nothing left to
  // autoroute. This is also what makes the result correct — the autorouter ignores
  // injected <pcbtrace>, so a second autoroute pass would re-route a net straight back
  // across the pretty copper (the SDA-over-fan short). One pass, no re-crossing.
  const frozen = obstacle.filter((e) => e.type === "pcb_trace")
  for (const t of frozen) jsx.push(pcbTraceRouteToJSX(t.route))

  // Routed render input: strip the pretty attrs (so the <trace>s are plain netlist +
  // the carve owns them) and inject the computed <pcbtrace> copper before </board>.
  let routedSrc = src.replace(/\s+pretty="[^"]*"/g, "")
  routedSrc = routedSrc.replace(/(\n\s*)<\/board>/, `\n${jsx.join("\n")}$1</board>`)
  const routedName = `_build-${board}.pretty-routed.tmp`
  writeFileSync(path.join(dir, `${routedName}.tsx`), routedSrc)
  console.log(`[pretty] routed ${mazeGroups.size} maze group(s) + ${cleanNets.length} clean fan(s) + froze ${frozen.length} autorouted net(s) -> ${routedName}.tsx (no 2nd autoroute)`)
  return { routedName, obstacleCircuitJson: obstacle }
}
