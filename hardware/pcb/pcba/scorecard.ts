/**
 * The board's requirements as a single pass/fail scorecard — the one place the design's rules
 * are enumerated as executable checks, computed from the routed circuit-json and the audits
 * pick-data already runs. Printed on every build (what an agent sees in the terminal) and folded
 * into out/<board>.picks.json (what the modal's Board-checks panel shows), so both audiences read
 * the same verdict from the same geometry — a result no one can narrate around.
 *
 * Two kinds of check:
 *   - GATE — a manufacturability / electrical requirement that must hold to fab. Every gate passes
 *            today; a failing gate is a broken board, and (once gating is turned on) a red build.
 *   - GOAL — the manual-routing progress this whole effort exists to drive: every signal net
 *            hand-routed on outer copper with NO vias (the planes carry power/ground). Shown as
 *            progress toward 100%, not a gate — the board still fabs while it converts.
 *
 * The manual/auto split is structural, not a flag in the circuit-json: a signal net is "hand-clean"
 * when all its copper sits on one outer layer with no via. Poured plane nets (the <copperpour>
 * connectsTo nets, passed in as `planeNets`) are exempt — their vias are plane stitches, not routing.
 *
 * Canonical prose for these requirements — the why behind each — is in requirements.md.
 */
import type { FootprintAudit } from "./footprint-audit"
import type { ConnectorAudit } from "./connector-audit"
import type { AmpacityAudit } from "./ampacity-audit"
import type { CapAudit } from "./cap-audit"

export type CheckStatus = "pass" | "fail" | "warn"

/** One requirement, measured. `value` is what the board is; `target` is what it must be. */
export type Check = {
  id: string
  label: string           // the requirement, in words
  kind: "gate" | "goal"
  status: CheckStatus     // pass = met; fail = a gate is broken; warn = a goal still in progress
  value: string           // the measurement
  target: string          // the requirement
  detail?: string[]       // offending items (capped), for the panel + the terminal
}

export type Scorecard = {
  checks: Check[]
  gatesPass: boolean      // every gate check passes → fab-ready on the hard rules
  manualPct: number       // signal nets hand-clean / total, 0..100 — the headline progress number
  signalNets: number      // signal nets that carry discrete copper (the conversion universe)
  deferred: number        // connections commented out of source — routing work set aside, tracked
}

/** Everything the scorecard reads. The gate inputs are what pick-data already computed; the goal
 *  metrics are derived here from the raw circuit + the set of poured plane nets. */
export type ScorecardInput = {
  circuit: any[]
  planeNets: Set<string>
  deferred: { from: string; to: string }[]  // connections commented out of source (deferred work)
  floor: number | null
  clearanceErrors: { kind: string; text: string }[]  // clearance.ts DRC findings (overlap/courtyard/sliver)
  opens: { kind: string; text: string }[]            // connectivity.ts open nets
  footprints: FootprintAudit
  connectors: ConnectorAudit
  ampacity: AmpacityAudit | null
  capAudit: CapAudit | null
  fab: { partsSourced: { sourced: number; total: number }; minDrillMm: number | null; minViaAnnularMm: number | null; minPadAnnularMm: number | null; unsourced: string[] }
}

// Fab DFM floors (JLCPCB). Drill ≥ 0.2 mm. Annular splits by hole type: a THT/component pad wants
// ≥ 0.13 mm ring; a via is fine at JLCPCB's recommended 0.5/0.3 = 0.1 mm ring (a single floor would
// false-flag every via — the board's stitch + signal vias all sit at exactly 0.1).
const MIN_DRILL = 0.2
const MIN_VIA_ANNULAR = 0.1
const MIN_PAD_ANNULAR = 0.13
// Copper clearance gate — the board runs 0.155; 0.14 is the permission-to-proceed floor.
const CLEARANCE_FLOOR = 0.14
// Body-clearance advisory: a positive gap under this warns (tight), a negative gap is a real
// overlap and already rides in the clearance errors as a courtyard fault.
const BODY_WARN = 0.4
const DETAIL_MAX = 8

const INNER = new Set(["inner1", "inner2", "inner3", "inner4"])

/** Resolve a pcb_trace to its net name the same way pick-data does: connection_name if it's a
 *  source_net id, else the trace's source_trace's first connected net, else a readable fallback. */
function netResolver(circuit: any[]) {
  const netName: Record<string, string> = {}
  const srcTrace: Record<string, any> = {}
  for (const e of circuit) {
    if (e.type === "source_net") netName[e.source_net_id] = e.name
    else if (e.type === "source_trace") srcTrace[e.source_trace_id] = e
  }
  return (t: any): string => {
    const byConn = t.connection_name ? netName[t.connection_name] : undefined
    if (byConn) return byConn
    const s = srcTrace[t.source_trace_id]
    const nid = s?.connected_source_net_ids?.[0]
    if (nid) return netName[nid] ?? nid
    return s?.display_name ?? t.pcb_trace_id
  }
}

export function buildScorecard(inp: ScorecardInput): Scorecard {
  const { circuit, planeNets } = inp

  // ── Manual-routing metrics (the goal) — per signal net, from raw copper geometry ──
  const traceNet = netResolver(circuit)
  const viaByNet = new Map<string, number>()
  const innerByNet = new Map<string, number>()
  const netHasTrace = new Set<string>()
  const netByTraceId: Record<string, string> = {}
  for (const e of circuit) {
    if (e.type !== "pcb_trace") continue
    const n = traceNet(e)
    netByTraceId[e.pcb_trace_id] = n
    netHasTrace.add(n)
    for (const r of e.route) if (INNER.has(r.layer)) innerByNet.set(n, (innerByNet.get(n) ?? 0) + 1)
  }
  for (const e of circuit) {
    if (e.type !== "pcb_via") continue
    const n = netByTraceId[e.pcb_trace_id] ?? "?"
    viaByNet.set(n, (viaByNet.get(n) ?? 0) + 1)
  }

  const signalNets = [...netHasTrace].filter((n) => !planeNets.has(n)).sort()
  const viaNets = signalNets.filter((n) => (viaByNet.get(n) ?? 0) > 0)
  const innerNets = signalNets.filter((n) => (innerByNet.get(n) ?? 0) > 0)
  const handClean = signalNets.filter((n) => (viaByNet.get(n) ?? 0) === 0 && (innerByNet.get(n) ?? 0) === 0)
  const signalVias = viaNets.reduce((s, n) => s + (viaByNet.get(n) ?? 0), 0)
  const manualPct = signalNets.length ? Math.round((100 * handClean.length) / signalNets.length) : 100

  const checks: Check[] = []
  const gate = (id: string, label: string, ok: boolean, value: string, target: string, detail?: string[]) =>
    checks.push({ id, label, kind: "gate", status: ok ? "pass" : "fail", value, target, detail: detail?.slice(0, DETAIL_MAX) })
  const goal = (id: string, label: string, done: boolean, value: string, target: string, detail?: string[]) =>
    checks.push({ id, label, kind: "goal", status: done ? "pass" : "warn", value, target, detail: detail?.slice(0, DETAIL_MAX) })

  // ── GATES — must hold to fab ──
  gate("continuity", "Every net fully connected in copper", inp.opens.length === 0,
    `${inp.opens.length} open`, "0 open", inp.opens.map((o) => o.text))

  gate("clearance", "Copper-to-copper clearance floor", inp.floor != null && inp.floor >= CLEARANCE_FLOOR,
    inp.floor != null ? `${inp.floor} mm` : "—", `≥ ${CLEARANCE_FLOOR} mm`)

  gate("drc", "No copper overlaps / courtyard faults / slivers", inp.clearanceErrors.length === 0,
    `${inp.clearanceErrors.length} error`, "0 error", inp.clearanceErrors.map((e) => e.text))

  const bf = inp.footprints.floor
  gate("bodies", "No part-body overlaps", bf == null || bf >= 0,
    bf != null ? `${bf} mm gap` : "—", "≥ 0 mm",
    bf != null && bf < BODY_WARN ? [`tightest body gap ${bf} mm (< ${BODY_WARN} advisory)`] : undefined)

  gate("connectors", "Connector bodies clear of edge & neighbours", inp.connectors.flagged === 0,
    `${inp.connectors.flagged} flagged`, "0 flagged",
    inp.connectors.rows.filter((r) => r.over).map((r) => `${r.ref}: ${r.clearance} mm to ${r.to}`))

  const { sourced, total } = inp.fab.partsSourced
  gate("sourcing", "Every placed part carries a JLCPCB #", sourced === total,
    `${sourced}/${total}`, `${total}/${total}`, inp.fab.unsourced)

  gate("drill", "Min drill meets JLCPCB DFM", inp.fab.minDrillMm != null && inp.fab.minDrillMm >= MIN_DRILL,
    inp.fab.minDrillMm != null ? `${inp.fab.minDrillMm} mm` : "—", `≥ ${MIN_DRILL} mm`)

  gate("pad-annular", "THT-pad annular ring meets JLCPCB DFM", inp.fab.minPadAnnularMm == null || inp.fab.minPadAnnularMm >= MIN_PAD_ANNULAR,
    inp.fab.minPadAnnularMm != null ? `${inp.fab.minPadAnnularMm} mm` : "—", `≥ ${MIN_PAD_ANNULAR} mm`)

  gate("via-annular", "Via annular ring meets JLCPCB DFM", inp.fab.minViaAnnularMm == null || inp.fab.minViaAnnularMm >= MIN_VIA_ANNULAR,
    inp.fab.minViaAnnularMm != null ? `${inp.fab.minViaAnnularMm} mm` : "—", `≥ ${MIN_VIA_ANNULAR} mm`)

  if (inp.ampacity)
    gate("ampacity", "Current-carrying traces wide enough", inp.ampacity.flagged === 0,
      `${inp.ampacity.flagged} narrow`, "0 narrow",
      inp.ampacity.rows.filter((r) => r.over).map((r) => `${r.label}: ${r.width} < ${r.minWidth} mm (${r.role})`))

  if (inp.capAudit)
    gate("decoupling", "Support caps within budget of their part", inp.capAudit.flagged === 0,
      `${inp.capAudit.flagged} flagged`, "0 flagged",
      [...inp.capAudit.rows.filter((r) => r.over).map((r) => `${r.cap}→${r.near}: ${r.gap ?? "?"} > ${r.budget} mm`),
       ...inp.capAudit.missing.map((m) => `${m.part}.${m.pin} has no decoupler`)])

  // ── GOALS — the manual-routing conversion (planes exempt; signal nets only) ──
  goal("manual-coverage", "Signal nets hand-routed on outer copper", handClean.length === signalNets.length,
    `${handClean.length}/${signalNets.length} nets (${manualPct}%)`, "100%",
    signalNets.filter((n) => !handClean.includes(n)))

  goal("signal-vias", "No vias on signal nets (planes stitch, signals don't)", signalVias === 0,
    `${signalVias} via on ${viaNets.length} net`, "0",
    viaNets.map((n) => `${n}: ${viaByNet.get(n)} via`))

  goal("outer-only", "No signal copper on inner layers (inner = planes)", innerNets.length === 0,
    `${innerNets.length} net`, "0",
    innerNets.map((n) => `${n}: ${innerByNet.get(n)} inner-layer pt`))

  goal("deferred", "No deferred connections (commented out of source)", inp.deferred.length === 0,
    `${inp.deferred.length} deferred`, "0",
    inp.deferred.map((d) => `${d.from} → ${d.to}`))

  const gatesPass = checks.every((c) => c.kind !== "gate" || c.status === "pass")
  return { checks, gatesPass, manualPct, signalNets: signalNets.length, deferred: inp.deferred.length }
}

/** Render the scorecard as an aligned terminal block — the build's closing verdict. */
export function formatScorecard(board: string, sc: Scorecard): string {
  const mark = { pass: "✓", fail: "✗", warn: "•" } as const
  const gates = sc.checks.filter((c) => c.kind === "gate")
  const goals = sc.checks.filter((c) => c.kind === "goal")
  const passed = gates.filter((c) => c.status === "pass").length
  const w = Math.max(...sc.checks.map((c) => c.label.length))
  const rows: string[] = []
  const line = (c: Check) => {
    rows.push(`  ${mark[c.status]} ${c.label.padEnd(w)}  ${c.value}  (want ${c.target})`)
    for (const d of c.detail ?? []) if (c.status !== "pass") rows.push(`      – ${d}`)
  }
  rows.push(`── ${board} scorecard ${"─".repeat(Math.max(0, 44 - board.length))}`)
  rows.push(`GATES (fab-ready)      ${passed}/${gates.length} pass${sc.gatesPass ? "" : "   ✗ BOARD NOT FAB-READY"}`)
  gates.forEach(line)
  rows.push(`GOAL (100% hand-routed)   ${sc.manualPct}% of ${sc.signalNets} routed nets${sc.deferred ? ` · ${sc.deferred} deferred` : ""}`)
  goals.forEach(line)
  rows.push("─".repeat(48))
  return rows.join("\n")
}
