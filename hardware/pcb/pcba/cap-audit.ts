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
 * budget?} rules it is handed against a flat pad list ({ref, pin, x, y}). Any board that
 * exports a `decoupling` table gets the audit; the intent lives with the board, the geometry
 * comes from the render, and the two are compared here. No coordinates are declared twice, so
 * the audit can't fall out of sync with a move — it re-measures every build.
 */

export type DecouplingRule = {
  cap: string        // the support cap's ref-des
  near: string       // the part it must sit close to
  role: string       // human tag: which rail/pin it serves
  budget?: number    // max acceptable pad gap (mm); omitted → DEFAULT_BUDGET
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

export type CapAudit = { rows: CapAuditRow[]; flagged: number; budget: number }

type Pad = { ref?: string | null; x?: number; y?: number }

// Default max pad gap before a cap reads as "drifted from its target". Sized above the
// board's tightest legitimate flanks (a buck/LDO input+output pair straddling a wide SIP
// lands ~5.5 mm) so a clean board stays clean, but below the ~6.5 mm+ a genuinely stranded
// decoupler shows. Per-rule `budget` overrides it (e.g. a central bulk reservoir).
export const DEFAULT_BUDGET = 6.0

export function auditDecoupling(rules: DecouplingRule[], pads: Pad[]): CapAudit {
  const byRef = new Map<string, Pad[]>()
  for (const p of pads) {
    if (!p.ref || typeof p.x !== "number" || typeof p.y !== "number") continue
    const list = byRef.get(p.ref) ?? (byRef.set(p.ref, []), byRef.get(p.ref)!)
    list.push(p)
  }

  const rows: CapAuditRow[] = []
  for (const r of rules) {
    const budget = r.budget ?? DEFAULT_BUDGET
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
  return { rows, flagged: rows.reduce((n, r) => n + (r.over ? 1 : 0), 0), budget: DEFAULT_BUDGET }
}
