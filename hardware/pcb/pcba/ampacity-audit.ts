/**
 * Ampacity audit — for the web viewer's Board-checks panel (folded into picks.json by
 * pick-data.ts, rendered by web/public/js/viewer/pcb.js).
 *
 * The copper DRC checks how far apart traces are, never how much current one can carry. The power
 * rails here don't need it — V12 / V5 / GND are poured planes and pins pick them up at the barrel,
 * effectively unlimited copper. But a few SIGNAL traces carry real current: the peristaltic-pump
 * motor outputs (~0.8 A peak). The autorouter lays every trace at the board's 0.2 mm floor, so a
 * high-current path gets no more copper than a logic line — 0.2 mm on 1 oz is only ~0.7 A, less on
 * an inner 0.5 oz layer. This flags any declared current-carrying trace routed under its width.
 *
 * The board declares which paths carry current and the width they want (`ampacity` in pcba.tsx);
 * this measures the actual routed width. Like the decoupling budgets, the widths are rules of thumb
 * (IPC-2221, ~10 °C rise), not a full thermal model — enough to catch a fat path left on a thin
 * trace. AGNOSTIC: it matches whatever {pin, minWidthMm, role} rules it's handed against the traces.
 */

export type AmpacityRule = {
  pin: string          // an endpoint pin prefix that identifies the current-carrying path (e.g. "U11.OUT")
  minWidthMm: number   // the width that path wants for its current
  role: string         // human tag
}

export type AmpacityRow = {
  label: string        // "U11.OUT1 → J13.AM1"
  width: number        // narrowest routed width on the trace (mm)
  minWidth: number
  over: boolean        // routed narrower than wanted
  role: string
}
export type AmpacityAudit = { rows: AmpacityRow[]; flagged: number }

type Trace = { from?: string | null; to?: string | null; width?: number | null }

export function auditAmpacity(rules: AmpacityRule[], traces: Trace[]): AmpacityAudit {
  const rows: AmpacityRow[] = []
  for (const t of traces) {
    if (typeof t.width !== "number" || !t.from || !t.to) continue
    const rule = rules.find((r) => t.from!.startsWith(r.pin) || t.to!.startsWith(r.pin))
    if (!rule) continue
    rows.push({
      label: `${t.from} → ${t.to}`,
      width: Math.round(t.width * 1000) / 1000,
      minWidth: rule.minWidthMm,
      over: t.width < rule.minWidthMm,
      role: rule.role,
    })
  }
  rows.sort((a, b) => Number(b.over) - Number(a.over) || a.width - b.width)
  return { rows, flagged: rows.reduce((n, r) => n + (r.over ? 1 : 0), 0) }
}
