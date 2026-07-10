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
 *   - GOAL — the manual-routing conversion this whole effort exists to drive: take every signal
 *            connection off the autorouter onto deliberate hand copper. Reported as a `score`, not a
 *            gate — the board still fabs while it converts.
 *
 * The split is by AUTHORSHIP, counted per rendered CONNECTION (a source_trace), not by geometry — the
 * circuit-json has no manual flag, so a clean-looking shape can't be trusted (the autorouter routes
 * most short nets clean by accident, and crediting that would count its work as progress toward
 * removing it). Authorship comes from source: a <trace> carrying pcbPath / pcbStraightLine (`path`)
 * or pcbComb (`comb`) is hand-authored (`authored`), matched to connections via source_trace.
 * display_name. Connections to a net ("X to net.Y") are plane stitches — outside the routing universe.
 *
 *   score = 100·(pcbPath + pcbComb) / (pcbPath + pcbComb + deferred + auto)
 *
 * pcbComb counts full: a comb is deliberate hand-authored routing, same as an explicit path — the
 * two are interchangeable forms (use whichever reads nicer / packs denser). deferred (commented
 * out) and auto (still autorouted) are the work left. Canonical prose for these requirements —
 * the why behind each — is in requirements.md.
 */
import type { FootprintAudit } from "./footprint-audit"
import type { ConnectorAudit } from "./connector-audit"
import type { AmpacityAudit } from "./ampacity-audit"
import type { CapAudit } from "./cap-audit"
import { CYE } from "./component-bodies"

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
  // The manual-routing conversion, counted by rendered connection (not net). The score is the
  // headline: done + half-done over everything still to do. See the `score` formula below.
  pcbPath: number         // explicit-path traces (pcbPath / pcbStraightLine) — done, weight 1.0
  pcbComb: number         // comb-strategy traces (pcbComb) — done, weight 1.0 (a comb is hand routing too)
  deferred: number        // connections commented out of source — routing work set aside
  auto: number            // live signal connections still on the autorouter — the work remaining
  score: number           // 100·(pcbPath + pcbComb) / (pcbPath + pcbComb + deferred + auto), 0..100
}

/** Everything the scorecard reads. The gate inputs are what pick-data already computed; the goal
 *  metrics are derived here from the raw circuit + the hand-authored connections read from source. */
export type ScorecardInput = {
  circuit: any[]
  authored: { from: string; to: string | null; kind: "path" | "comb" }[]  // hand-authored <trace>s (to=null: dynamic pcbFan)
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
const DETAIL_MAX = 99

export function buildScorecard(inp: ScorecardInput): Scorecard {
  const { circuit } = inp

  // ── Manual-routing conversion (the goal) — counted per rendered signal CONNECTION, by authorship ──
  // The circuit-json has no manual flag, so authorship is read from source: each hand-authored <trace>
  // (`authored`, split into `path`/`comb`) and each rendered source_trace's endpoints (its
  // display_name, "<from> to <to>") normalise to an unordered pin-pair key and match. A pcbFan trace
  // has a dynamic `to`, so it's keyed by its `from` pin instead. Connections to a net (a plane stitch,
  // "X to net.Y") are outside the routing universe — planes carry power/ground, not signals.
  const norm = (s: string) => s.replace(/[\s.>]/g, "")
  const connKey = (a: string, b: string) => [norm(a), norm(b)].sort().join("|")
  const isNet = (s: string) => s.trim().startsWith("net.")
  const pathKeys = new Set<string>(), combKeys = new Set<string>(), pathFromPins = new Set<string>()
  for (const a of inp.authored) {
    if (a.to == null) { if (a.kind === "path") pathFromPins.add(norm(a.from)); continue }
    ;(a.kind === "comb" ? combKeys : pathKeys).add(connKey(a.from, a.to))
  }

  let pcbPath = 0, pcbComb = 0, auto = 0
  const autoList: string[] = []
  for (const e of circuit) {
    if (e.type !== "source_trace" || !e.display_name) continue
    const [a, b, ...rest] = String(e.display_name).split(" to ")
    if (!a || !b || rest.length) continue
    if (isNet(a) || isNet(b)) continue
    const k = connKey(a, b)
    if (combKeys.has(k)) pcbComb++
    else if (pathKeys.has(k) || pathFromPins.has(norm(a))) pcbPath++
    else { auto++; autoList.push(e.display_name) }
  }
  const deferredN = inp.deferred.length
  const routingTotal = pcbPath + pcbComb + deferredN + auto
  // Score: every hand-authored connection counts full — an explicit path and a comb are both
  // deliberate routing; deferred and auto both count as not-yet-done.
  const score = routingTotal ? Math.round((100 * (pcbPath + pcbComb)) / routingTotal) : 100

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

  gate("drc", "No overlaps / courtyard / slivers / pad shadows", inp.clearanceErrors.length === 0,
    `${inp.clearanceErrors.length} error`, "0 error", inp.clearanceErrors.map((e) => e.text))

  // Body clearance is measured as IPC-7351 keep-outs — copper envelope + courtyard excess CYE
  // (component-bodies.ts). A gap ≥ 0 clears IPC Nominal density; a small negative gap is sub-Nominal
  // packing where the copper still clears (not a collision). A true body overlap cuts past −2·CYE
  // (the copper itself overlaps) and independently fires a courtyard fault in the DRC gate above — so
  // fab-ready fails only on a real overlap here; the sub-Nominal pairs are surfaced as an advisory.
  const bf = inp.footprints.floor
  const subNominal = inp.footprints.tight.filter((p) => p.gap < 0)
  gate("bodies", "Part keep-outs clear (IPC-7351 courtyard)", bf == null || bf > -2 * CYE,
    bf != null ? `${bf} mm` : "—", "no overlap",
    subNominal.length ? subNominal.map((p) => `${p.a}–${p.b}: ${p.gap} mm — below IPC Nominal (${CYE} mm); copper clears`)
      : (bf != null && bf < BODY_WARN ? [`tightest keep-out ${bf} mm`] : undefined))

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

  // ── GOALS — the manual-routing conversion, by connection. The score is the headline; auto and
  // deferred are the actionable backlogs. pcbPath/pcbComb counts ride the score row's detail. ──
  goal("routing-score", "Signal routing hand-authored (pcbPath + pcbComb)", score === 100,
    `${score}%`, "100%",
    [`${pcbPath} pcbPath + ${pcbComb} pcbComb (both done) of ${routingTotal} — ${deferredN} deferred, ${auto} auto still to do`])

  goal("auto", "Signal connections still on the autorouter", auto === 0, `${auto}`, "0", autoList)

  goal("deferred", "Deferred connections (commented out of source)", deferredN === 0,
    `${deferredN}`, "0", inp.deferred.map((d) => `${d.from} → ${d.to}`))

  const gatesPass = checks.every((c) => c.kind !== "gate" || c.status === "pass")
  return { checks, gatesPass, pcbPath, pcbComb, deferred: deferredN, auto, score }
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
    // Show detail whenever present — offending items on a failing gate, and advisories (e.g. the
    // sub-Nominal body pairs) on a passing one. Passing gates without detail stay quiet.
    for (const d of c.detail ?? []) rows.push(`      – ${d}`)
  }
  rows.push(`── ${board} scorecard ${"─".repeat(Math.max(0, 44 - board.length))}`)
  rows.push(`GATES (fab-ready)      ${passed}/${gates.length} pass${sc.gatesPass ? "" : "   ✗ BOARD NOT FAB-READY"}`)
  gates.forEach(line)
  rows.push(`GOAL (100% converted)   ${sc.score}% score · ${sc.pcbPath} pcbPath · ${sc.pcbComb} pcbComb · ${sc.deferred} deferred · ${sc.auto} auto`)
  goals.forEach(line)
  rows.push("─".repeat(48))
  return rows.join("\n")
}
