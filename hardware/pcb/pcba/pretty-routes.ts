/**
 * pretty-routes.ts — the build stage that turns declared intent into copper.
 *
 * A board declares 2nd-pass routing inline, by net identity:
 *
 *   <trace from=".J5 > .IO25" to=".U1A > .IO25" pretty="maze:j5" />
 *
 * `pretty="<strategy>:<group>"`. At build time applyPrettyRoutes() (called by
 * render-board) collects those traces, routes each group with the in-process
 * router (pretty-router.ts) against a freshly-exported obstacle field, and writes a
 * throwaway "routed" .tsx — the board with the pretty attrs stripped and the
 * computed <pcbtrace> copper injected — which the rest of the build renders.
 *
 * The point: routes are regenerated every build from live geometry, so moving a
 * part just re-routes it. No coordinates are frozen into the source, and the
 * coordinate carve can never go stale (it is always fed routes that land on the
 * current pads). Per-group routing params live in GROUPS below; the net list comes
 * from the .tsx, so adding a signal is one <trace ... pretty=...> line.
 */
import { mazeRouteNets, routedNetToJSX, type MazeSpec } from "./pretty-router"
import { readFileSync, writeFileSync, rmSync } from "node:fs"
import path from "node:path"

// Per-group routing windows + params. The region is the A* search window (mm); it
// can be wider than the pads' bounding box where a route must detour (e.g. J5.IO19
// swings right of BT1's clip). Params match _maze.ts's COMMON.
const COMMON = { cell: 0.1, clr: 0.25, width: 0.2, viaCost: 60, startLayer: "top", turn: 12 }
const GROUPS: Record<string, { strategy: "maze" } & MazeSpec> = {
  j5: { strategy: "maze", ...COMMON, region: { x0: -42, x1: -13, y0: -47, y1: 14 } },
}

// circuit-json exporter the caller supplies (render-board reuses its tsci runner).
export type ExportCircuitJson = (tsxBasename: string) => Promise<any[]>

type Pretty = { el: string; from: string; to: string; strategy: string; group: string }

const attrOf = (el: string, name: string) => (el.match(new RegExp(`\\b${name}="([^"]*)"`)) || [])[1] || ""
// ".J5 > .IO25" -> "J5.IO25" (the form pretty-router labels pads with)
const toDot = (sel: string) => sel.replace(/^\./, "").replace(/\s*>\s*\./, ".")

export function findPrettyTraces(src: string): Pretty[] {
  // match each self-closing <trace .../> (non-greedy to the first "/>", since the
  // from/to selectors contain ">" e.g. ".J5 > .IO25"), then keep the pretty ones.
  const els = (src.match(/<trace\b[\s\S]*?\/>/g) || []).filter((el) => /\bpretty="/.test(el))
  return els.map((el) => {
    const [strategy, group] = attrOf(el, "pretty").split(":")
    return { el, from: attrOf(el, "from"), to: attrOf(el, "to"), strategy: strategy || "", group: group || strategy || "" }
  })
}

// label -> {x,y} for every pad in a circuit-json (plated holes + smd pads).
function padCoords(circuit: any[]): Record<string, { x: number; y: number }> {
  const sp: any = {}, pp: any = {}, sc: any = {}
  for (const e of circuit) {
    if (e.type === "source_port") sp[e.source_port_id] = e
    if (e.type === "pcb_port") pp[e.pcb_port_id] = e
    if (e.type === "source_component") sc[e.source_component_id] = e
  }
  const label = (pid: string) => { const p = pp[pid]; const o = p && sp[p.source_port_id]; return o ? `${sc[o.source_component_id].name}.${o.name}` : "" }
  const out: Record<string, { x: number; y: number }> = {}
  for (const e of circuit) {
    if (e.type !== "pcb_plated_hole" && e.type !== "pcb_smtpad") continue
    const l = label(e.pcb_port_id); if (l && !out[l]) out[l] = { x: e.x, y: e.y }
  }
  return out
}

/**
 * Resolve a board's pretty-routes into a routed temp .tsx and return its basename
 * (no extension), for the rest of render-board to render. Returns `board` unchanged
 * when there are no pretty traces (pure no-op — the normal build path).
 */
export async function applyPrettyRoutes(dir: string, board: string, exportCJ: ExportCircuitJson): Promise<string> {
  const src = readFileSync(path.join(dir, `${board}.tsx`), "utf8")
  const pretties = findPrettyTraces(src)
  if (!pretties.length) return board

  // Obstacle field: the board with every pretty <trace> removed, so the autorouter
  // leaves those corridors clear. (Non-pretty nets route identically here and in the
  // final routed render, since the pretty nets are carved there too.)
  let obstacleSrc = src
  for (const p of pretties) obstacleSrc = obstacleSrc.replace(p.el, "")
  const obsName = `._${board}.pretty-obstacle.tmp`
  writeFileSync(path.join(dir, `${obsName}.tsx`), obstacleSrc)
  let obstacle: any[]
  try {
    obstacle = await exportCJ(obsName)
  } finally {
    rmSync(path.join(dir, `${obsName}.tsx`), { force: true })
    rmSync(path.join(dir, `${obsName}.circuit.json`), { force: true })
  }
  const xy = padCoords(obstacle)

  // Group by the pretty group key; route each maze group hardest (longest)-first so
  // the tight runs claim the channel before the easy ones — deterministic given the
  // geometry, so routes don't flap between builds.
  const byGroup = new Map<string, Pretty[]>()
  for (const p of pretties) (byGroup.get(p.group) ?? byGroup.set(p.group, []).get(p.group)!).push(p)
  const jsx: string[] = []
  for (const [key, ps] of byGroup) {
    // Fail loud rather than silently fall back to the autorouter: a typo'd group, a
    // missing config, or an unroutable net is a build error, not bad copper.
    const cfg = GROUPS[key]
    if (!cfg) throw new Error(`[pretty] no GROUPS config for "${key}" (${ps.length} net(s): ${ps.map((p) => `${p.from}->${p.to}`).join(", ")})`)
    if (cfg.strategy !== "maze") throw new Error(`[pretty] strategy "${cfg.strategy}" not yet supported (group ${key})`)
    const len = (p: Pretty) => {
      const a = xy[toDot(p.from)], b = xy[toDot(p.to)]
      return a && b ? Math.abs(a.x - b.x) + Math.abs(a.y - b.y) : 0
    }
    const ordered = [...ps].sort((a, b) => len(b) - len(a) || toDot(a.from).localeCompare(toDot(b.from)))
    const pairs = ordered.map((p) => ({ from: toDot(p.from), to: toDot(p.to) }))
    const routed = mazeRouteNets(obstacle, pairs, cfg)
    if (routed.length !== pairs.length) throw new Error(`[pretty] group ${key}: routed only ${routed.length}/${pairs.length} nets — widen the region or check for obstacles`)
    for (const rn of routed) jsx.push(routedNetToJSX(rn))
  }

  // Routed render input: strip the pretty attrs (so the <trace>s are plain netlist +
  // the carve owns them) and inject the computed <pcbtrace> copper before </board>.
  let routedSrc = src.replace(/\s+pretty="[^"]*"/g, "")
  routedSrc = routedSrc.replace(/(\n\s*)<\/board>/, `\n${jsx.join("\n")}$1</board>`)
  const routedName = `._${board}.pretty-routed.tmp`
  writeFileSync(path.join(dir, `${routedName}.tsx`), routedSrc)
  console.log(`[pretty] routed ${jsx.length} net(s) across ${byGroup.size} group(s) -> ${routedName}.tsx`)
  return routedName
}
