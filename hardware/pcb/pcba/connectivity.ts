/**
 * Net-continuity (OPEN) analysis of a routed circuit-json, for the web viewer's board readout
 * (folded into picks.json `errors` by pick-data.ts). The clearance floor (clearance.ts) measures how
 * close two nets approach; this measures whether one net's own pads reach each other.
 *
 * Each intended net — grouped by source_port.subcircuit_connectivity_map_key, the netlist's grouping,
 * which holds whether or not the router realized the connection — must land in one connected
 * component of realized copper. The copper is a union-find:
 *   - a trace joins every pad/via a route vertex lands on, on that vertex's layer;
 *   - a via/hole joins any pad or via it overlaps — an SMD plane pad reaches its plane through a
 *     coincident stitch via — while two SMD rects never join directly, so the tightly-packed
 *     USB-C pill field stays distinct;
 *   - a pad/via inside a plane pour's outline and outside its antipad voids joins that plane; a
 *     foreign-net barrel sits in a void, so it stays out;
 *   - same-net pours that touch are one sheet; a gap leaves a pad on a pinched-off fragment alone.
 * A plated-hole barrel conducts on every layer in its vertical span (a top+bottom hole spans all
 * six), not just the outer layers where it flashes a pad. Pads are rotated rectangles.
 *
 * A net whose pads span more than one component is an open; the stranded pads name themselves.
 */

export type OpenNet = { stranded: string[]; connected: string[]; islands: number }

const STACK = ["top", "inner1", "inner2", "inner3", "inner4", "bottom"]
const EPS = 0.06 // mm slack for "touching"; below the cross-net clearance floor, so no foreign copper joins

type Terminal = { node: string; shape: "circle" | "rect"; x: number; y: number; r?: number; hw?: number; hh?: number; rot?: number; layers: string[]; rmax: number }

// distance from a point to a terminal's copper edge (rotated rect for a pad, circle for a via/hole)
function distToTerminal(px: number, py: number, t: Terminal): number {
  if (t.shape === "circle") return Math.hypot(px - t.x, py - t.y) - (t.r as number)
  const dx = px - t.x, dy = py - t.y
  const c = Math.cos(-(t.rot as number)), s = Math.sin(-(t.rot as number))
  const lx = Math.abs(dx * c - dy * s) - (t.hw as number)
  const ly = Math.abs(dx * s + dy * c) - (t.hh as number)
  return Math.hypot(Math.max(lx, 0), Math.max(ly, 0))
}

const inRing = (x: number, y: number, ring: number[][]): boolean => {
  let inside = false
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i], [xj, yj] = ring[j]
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside
  }
  return inside
}
const distPtSeg = (x: number, y: number, ax: number, ay: number, bx: number, by: number): number => {
  const dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy
  let t = L2 ? ((x - ax) * dx + (y - ay) * dy) / L2 : 0
  t = t < 0 ? 0 : t > 1 ? 1 : t
  return Math.hypot(x - (ax + t * dx), y - (ay + t * dy))
}

export function analyzeConnectivity(circuit: any[]): OpenNet[] {
  const by = (t: string) => circuit.filter((e) => e.type === t)
  const scById: Record<string, string> = {}
  for (const s of by("source_component")) scById[s.source_component_id] = s.name
  const spName: Record<string, string> = {}, spKey: Record<string, string | null> = {}
  for (const sp of by("source_port")) {
    spName[sp.source_port_id] = (scById[sp.source_component_id] ?? "?") + "." + (sp.name ?? "?")
    spKey[sp.source_port_id] = sp.subcircuit_connectivity_map_key ?? null
  }
  const portToSp: Record<string, string> = {}
  for (const pp of by("pcb_port")) portToSp[pp.pcb_port_id] = pp.source_port_id
  const nameOf = (pid: string) => spName[portToSp[pid]] ?? "?"
  const keyOf = (pid: string) => spKey[portToSp[pid]] ?? null

  const spanLayers = (layers: string[] | undefined): string[] => {
    const idx = (layers ?? []).map((l) => STACK.indexOf(l)).filter((i) => i >= 0)
    if (!idx.length) return STACK.slice()
    return STACK.slice(Math.min(...idx), Math.max(...idx) + 1)
  }

  const terminals: Terminal[] = []
  const padNodesByPort: Record<string, string[]> = {}
  for (const p of by("pcb_smtpad")) {
    const node = "S:" + p.pcb_smtpad_id
    terminals.push({ node, shape: "rect", x: p.x, y: p.y, hw: (p.width || 0) / 2, hh: (p.height || 0) / 2, rot: ((p.ccw_rotation || 0) * Math.PI) / 180, layers: [p.layer], rmax: Math.max(p.width || 0, p.height || 0) / 2 })
    if (p.pcb_port_id) (padNodesByPort[p.pcb_port_id] ??= []).push(node)
  }
  for (const h of by("pcb_plated_hole")) {
    const r = (h.outer_diameter ?? h.hole_diameter ?? 0.5) / 2
    const node = "H:" + h.pcb_plated_hole_id
    terminals.push({ node, shape: "circle", x: h.x, y: h.y, r, layers: spanLayers(h.layers), rmax: r })
    if (h.pcb_port_id) (padNodesByPort[h.pcb_port_id] ??= []).push(node)
  }
  for (const v of by("pcb_via")) {
    const r = (v.outer_diameter ?? 0.5) / 2
    terminals.push({ node: "V:" + v.pcb_via_id, shape: "circle", x: v.x, y: v.y, r, layers: spanLayers(v.layers), rmax: r })
  }

  const parent: Record<string, string> = {}
  const find = (a: string): string => { while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a] } return a }
  const union = (a: string | null, b: string | null) => { if (a == null || b == null) return; parent[a] ??= a; parent[b] ??= b; const ra = find(a), rb = find(b); if (ra !== rb) parent[ra] = rb }
  for (const t of terminals) parent[t.node] = t.node
  const shareLayer = (la: string[], lb: string[]) => la.some((x) => lb.includes(x))

  // a trace vertex lands on the pads/vias it touches; the whole route is one copper piece
  for (const tr of by("pcb_trace")) {
    let anchor: string | null = null
    const touched = new Set<string>()
    for (const pt of tr.route ?? []) {
      if (pt.x == null) continue
      const hw = (pt.width || 0.2) / 2
      for (const term of terminals) {
        if (pt.layer && !term.layers.includes(pt.layer)) continue
        if (Math.abs(pt.x - term.x) > term.rmax + hw + EPS || Math.abs(pt.y - term.y) > term.rmax + hw + EPS) continue
        if (distToTerminal(pt.x, pt.y, term) <= hw + EPS) touched.add(term.node)
      }
    }
    for (const n of touched) { if (anchor == null) anchor = n; else union(anchor, n) }
    for (const v of by("pcb_via")) if (v.pcb_trace_id === tr.pcb_trace_id) { const n = "V:" + v.pcb_via_id; if (anchor == null) anchor = n; else union(anchor, n) }
  }

  // a via/hole overlapping a pad or another via/hole joins it; a shared circle carries the join, so
  // two SMD rects (neighbour pads) never merge on their own
  for (let i = 0; i < terminals.length; i++) {
    const a = terminals[i]
    for (let j = i + 1; j < terminals.length; j++) {
      const b = terminals[j]
      if (a.shape !== "circle" && b.shape !== "circle") continue
      if (Math.abs(a.x - b.x) > a.rmax + b.rmax + EPS || Math.abs(a.y - b.y) > a.rmax + b.rmax + EPS) continue
      if (!shareLayer(a.layers, b.layers)) continue
      const d = a.shape === "circle" ? distToTerminal(a.x, a.y, b) - (a.r as number) : distToTerminal(b.x, b.y, a) - (b.r as number)
      if (d <= EPS) union(a.node, b.node)
    }
  }

  // a plane pour joins each terminal on its layer that lies inside the outline and outside every
  // antipad void; same-net pours within touching distance are one sheet
  const pours = by("pcb_copper_pour").map((p, idx) => ({
    node: "POUR:" + idx, net: p.source_net_id, layer: p.layer,
    outer: (p.brep_shape?.outer_ring?.vertices ?? []).map((v: any) => [v.x, v.y] as number[]),
    voids: (p.brep_shape?.inner_rings ?? []).map((r: any) => (r.vertices ?? r).map((v: any) => [v.x, v.y] as number[])),
  }))
  for (const pr of pours) parent[pr.node] = pr.node
  const ringGap = (A: number[][], B: number[][]): number => {
    let m = Infinity
    for (const [x, y] of A) for (let i = 0, j = B.length - 1; i < B.length; j = i++) { m = Math.min(m, distPtSeg(x, y, B[j][0], B[j][1], B[i][0], B[i][1])); if (m <= EPS) return m }
    return m
  }
  for (let i = 0; i < pours.length; i++) for (let j = i + 1; j < pours.length; j++) {
    const a = pours[i], b = pours[j]
    if (a.net !== b.net || a.layer !== b.layer || a.outer.length < 3 || b.outer.length < 3) continue
    if (ringGap(a.outer, b.outer) <= EPS) union(a.node, b.node)
  }
  for (const pr of pours) {
    if (pr.outer.length < 3) continue
    for (const term of terminals) {
      if (!term.layers.includes(pr.layer)) continue
      if (!inRing(term.x, term.y, pr.outer)) continue
      if (pr.voids.some((v: number[][]) => v.length >= 3 && inRing(term.x, term.y, v))) continue
      union(term.node, pr.node)
    }
  }

  const netPads: Record<string, { node: string; name: string }[]> = {}
  for (const [portId, nodes] of Object.entries(padNodesByPort)) {
    const key = keyOf(portId)
    if (!key) continue
    ;(netPads[key] ??= []).push({ node: nodes[0], name: nameOf(portId) })
  }
  const opens: OpenNet[] = []
  for (const pads of Object.values(netPads)) {
    if (pads.length < 2) continue
    const comps = new Map<string, string[]>()
    for (const pad of pads) { const root = find(pad.node); if (!comps.has(root)) comps.set(root, []); comps.get(root)!.push(pad.name) }
    if (comps.size <= 1) continue
    const groups = [...comps.values()].sort((a, b) => b.length - a.length)
    const [connected, ...rest] = groups
    opens.push({ connected, stranded: rest.flat(), islands: groups.length })
  }
  return opens
}

// One board-error row per open net, for the viewer's error list.
export function connectivityErrors(opens: OpenNet[]): { kind: string; text: string }[] {
  return opens.map((o) => {
    const anchor = o.connected[0] + (o.connected.length > 1 ? ` +${o.connected.length - 1}` : "")
    return { kind: "open", text: `Open net: ${o.stranded.join(", ")} not connected to ${anchor} (${o.islands} copper islands)` }
  })
}
