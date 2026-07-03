/**
 * Cap decoupling audit — for the web viewer's Board-checks panel (folded into picks.json
 * by pick-data.ts, rendered by web/public/js/viewer/pcb.js).
 *
 * A board declares WHICH cap decouples WHICH part and the ROLE it plays (`decoupling` in
 * pcba.tsx). This module measures, from the placed geometry, how close each cap actually
 * sits to its target — the smallest centre-to-centre gap between any pad of the cap and any
 * pad of the target — and flags any that drifted past `budget` mm. That's the whole failure
 * mode this catches: a support cap stranded from the pin it serves (e.g. a decoupler left
 * behind when its chip footprint changed), which no copper-clearance or DRC check would ever
 * notice because the connection is through a plane.
 *
 * AGNOSTIC. It knows nothing about specific ref-des — it resolves whatever {cap, near, role,
 * kind} rules it is handed against a flat pad list ({ref, pin, x, y}). Any board that exports a
 * `decoupling` table gets the audit; the intent lives with the board, the geometry comes from
 * the render, and the two are compared here. No coordinates are declared twice, so the audit
 * can't fall out of sync with a move — it re-measures every build.
 */

// Each cap's job — this, not a hand-picked number, sets how tight it must sit (BUDGETS below).
// A support cap shunts noise / holds charge at a frequency set by its value and what it feeds;
// the higher that frequency, the shorter the loop it needs, so the tighter its distance budget.
export type CapKind = "hf" | "bulk" | "rc" | "reservoir"

export type DecouplingRule = {
  cap: string        // the support cap's ref-des
  near: string       // the part it must sit close to
  role: string       // human tag: which rail/pin it serves
  kind: CapKind      // job class → its distance budget (BUDGETS)
  budget?: number    // explicit per-cap override (mm); omitted → BUDGETS[kind]
}

export type CapAuditRow = {
  cap: string
  near: string
  role: string
  gap: number | null   // nearest pad-to-pad centre gap (mm); null when a part isn't placed
  budget: number
  over: boolean         // gap exceeds budget (or a part is missing)
  note?: string         // set only for the missing-part case
}

export type CapAudit = { rows: CapAuditRow[]; flagged: number; budgets: Record<CapKind, number> }

type Pad = { ref?: string | null; x?: number; y?: number }

// Max pad gap by job (mm) before a cap reads as "drifted from its target". These are
// placement-tolerance rules of thumb, NOT computed impedance targets: on this plane-decoupled
// board the poured planes carry the current, so the exact millimetre is a soft constraint (the
// vertical pad→via→plane inductance dominates the loop, not the lateral distance). The budgets
// exist to catch a stranded cap, and are ranked by job so the ones that actually want a short
// loop are held tighter:
//   hf         0.1uF ceramic — shunts the fastest edges (~1–100 MHz); wants the shortest loop
//   bulk       10/22uF — a regulator/driver's mid-frequency reservoir; distance-tolerant
//   rc         a timing/reset RC node (not decoupling) — near its pin, but not critical
//   reservoir  the one big electrolytic — central by design, feeds a whole block
export const BUDGETS: Record<CapKind, number> = { hf: 5, bulk: 8, rc: 6, reservoir: 16 }
export const DEFAULT_BUDGET = 8.0 // fallback only, if a rule somehow carries no kind

export function auditDecoupling(rules: DecouplingRule[], pads: Pad[]): CapAudit {
  const byRef = new Map<string, Pad[]>()
  for (const p of pads) {
    if (!p.ref || typeof p.x !== "number" || typeof p.y !== "number") continue
    const list = byRef.get(p.ref) ?? (byRef.set(p.ref, []), byRef.get(p.ref)!)
    list.push(p)
  }

  const rows: CapAuditRow[] = []
  for (const r of rules) {
    const budget = r.budget ?? BUDGETS[r.kind] ?? DEFAULT_BUDGET
    const capPads = byRef.get(r.cap), nearPads = byRef.get(r.near)
    if (!capPads || !nearPads) {
      const miss = !capPads && !nearPads ? `${r.cap} & ${r.near}` : !capPads ? r.cap : r.near
      rows.push({ cap: r.cap, near: r.near, role: r.role, gap: null, budget, over: true, note: `${miss} not placed` })
      continue
    }
    let best = Infinity
    for (const a of capPads) for (const b of nearPads) {
      const d = Math.hypot((a.x as number) - (b.x as number), (a.y as number) - (b.y as number))
      if (d < best) best = d
    }
    const gap = Math.round(best * 100) / 100
    rows.push({ cap: r.cap, near: r.near, role: r.role, gap, budget, over: gap > budget })
  }

  // Worst first: flagged (or missing) ahead of clean, then by gap descending — so the
  // panel leads with whatever most wants attention. Missing parts (gap null) sort to the top.
  rows.sort((a, b) => Number(b.over) - Number(a.over) || (b.gap ?? Infinity) - (a.gap ?? Infinity))
  return { rows, flagged: rows.reduce((n, r) => n + (r.over ? 1 : 0), 0), budgets: { ...BUDGETS } }
}
