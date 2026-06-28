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
import { mazeRouteNets, cleanPads, cleanFanRoute, monoWarn, routedNetToJSX, type MazeSpec, type FanType } from "./pretty-router"
import { readFileSync, writeFileSync, rmSync } from "node:fs"
import path from "node:path"

// maze search windows. The region is the A* search window (mm), wider than the pads'
// bounding box where a route must detour. Params match COMMON; io4u8 hugs the dense ESP
// pin row so it holds the full board clearance.
const COMMON = { cell: 0.1, clr: 0.25, width: 0.2, viaCost: 60, startLayer: "top", turn: 12 }
const MAZE_GROUPS: Record<string, MazeSpec> = {
  j6: { ...COMMON, region: { x0: 2, x1: 21, y0: 20, y1: 44 } },
  j5: { ...COMMON, region: { x0: -41, x1: -13, y0: -47, y1: 14 } },
  i2c: { ...COMMON, region: { x0: -24, x1: 18, y0: -35, y1: 38 } },
  io4u8: { ...COMMON, clr: 0.45, region: { x0: -58, x1: -36, y0: -26, y1: -10 } },
  faucet485: { ...COMMON, region: { x0: -52, x1: -12, y0: 9, y1: 45 } },
  divider: { ...COMMON, region: { x0: -27, x1: -7, y0: 9, y1: 46 } },
}

// circuit-json exporter the caller supplies (render-board reuses its tsci runner).
export type ExportCircuitJson = (tsxBasename: string) => Promise<any[]>

type Pretty = { el: string; from: string; to: string; strategy: string; variant: string }

const attrOf = (el: string, name: string) => (el.match(new RegExp(`\\b${name}="([^"]*)"`)) || [])[1] || ""
// ".J5 > .IO25" -> "J5.IO25" (the form the router labels pads with)
const toDot = (sel: string) => sel.replace(/^\./, "").replace(/\s*>\s*\./, ".")

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
  // final routed render, since the pretty nets are carved there too.) A trace that is a
  // .map() arrow body becomes `null` (valid, renders nothing); a standalone child is cut.
  let obstacleSrc = src
  for (const p of pretties) {
    const i = obstacleSrc.indexOf(p.el)
    if (i < 0) continue
    const repl = obstacleSrc.slice(0, i).trimEnd().endsWith("=>") ? "null" : ""
    obstacleSrc = obstacleSrc.slice(0, i) + repl + obstacleSrc.slice(i + p.el.length)
  }
  const obsName = `._${board}.pretty-obstacle.tmp`
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

  // ── clean fans: each net routes independently from its two pads. Warn (don't fail)
  // if a fan's pin mapping isn't monotone, grouping by fan type + source component. ──
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
    }
    for (const p of cleanNets) jsx.push(routedNetToJSX(cleanFanRoute(pads, toDot(p.from), toDot(p.to), { fanType: p.variant as FanType })))
  }

  // Routed render input: strip the pretty attrs (so the <trace>s are plain netlist +
  // the carve owns them) and inject the computed <pcbtrace> copper before </board>.
  let routedSrc = src.replace(/\s+pretty="[^"]*"/g, "")
  routedSrc = routedSrc.replace(/(\n\s*)<\/board>/, `\n${jsx.join("\n")}$1</board>`)
  const routedName = `._${board}.pretty-routed.tmp`
  writeFileSync(path.join(dir, `${routedName}.tsx`), routedSrc)
  console.log(`[pretty] routed ${jsx.length} net(s): ${mazeGroups.size} maze group(s) + ${cleanNets.length} clean fan(s) -> ${routedName}.tsx`)
  return routedName
}
