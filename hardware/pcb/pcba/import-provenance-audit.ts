/**
 * Import-provenance gate — every part footprint must be the fab's REAL land pattern, pulled with
 * `tsci import <LCSC#>`, never a generic/hand-drawn one. The rule is stated three times in prose
 * (README, jlcpcb-parts.md, review-checklist.md §6) and agents keep skimming past it: a hand-drawn
 * land looks imported — it lives in imports/, wraps the same props, carries the right
 * supplierPartNumbers — so nothing pushes back until a board arrives with pads at the wrong pitch.
 * This measures provenance from the copper itself, so the rule fails a build instead of a review.
 *
 * The tell is coordinate PRECISION. `tsci import` transcribes EasyEDA/JLCPCB geometry verbatim, so a
 * real land carries raw sub-micron float mantissas — pads at 1.734947 mm, 7.499985 mm, courtyard
 * vertices like 0.9261348. A footprint typed by hand uses round human values (0.05 mm grid): 2.0,
 * 1.9, 0.65, 0.4. So: a footprint that has pad/hole geometry but NOT ONE coordinate with ≥4 decimal
 * places was hand-authored. Across this board's 37 imports the split is absolute — every genuine
 * import has ≥10 high-precision coordinates, every hand-drawn one has exactly zero. (The 3D cadModel
 * is NOT the signal: several real imports legitimately ship without a GLB.)
 *
 * Scoped to the footprint block so a cadModel URL's digits or a round modelOriginPosition can't
 * colour the count. A file with no pad/hole geometry (a string-footprint passive, a pure re-export)
 * has nothing to judge and is skipped.
 */
import { readdirSync, readFileSync } from "node:fs"
import { join } from "node:path"

export type ImportProvenanceRow = {
  file: string      // imports/<name>.tsx
  geom: number      // count of pad/hole/silk/courtyard geometry elements
  hiPrec: number    // coordinates carrying ≥4 decimal places (the import fingerprint)
  handDrawn: boolean
}
export type ImportProvenanceAudit = { rows: ImportProvenanceRow[]; flagged: number }

const GEOM_RE = /<(?:smtpad|platedhole|hole|silkscreenpath|courtyardoutline)\b/g
// A coordinate with ≥4 fractional digits — the raw-float fingerprint of a transcribed EasyEDA land.
const HIPREC_RE = /-?\d+\.\d{4,}/g

/** Scan an imports/ directory and flag any footprint that carries geometry but no high-precision
 *  coordinate — i.e. a land drawn by hand rather than pulled with `tsci import`. */
export function auditImportProvenance(importsDir: string): ImportProvenanceAudit {
  const rows: ImportProvenanceRow[] = []
  for (const name of readdirSync(importsDir)) {
    if (!name.endsWith(".tsx")) continue
    const src = readFileSync(join(importsDir, name), "utf8")
    // Judge only the footprint copper — scope out the cadModel/props so their digits can't leak in.
    let geom = 0, hiPrec = 0
    for (const m of src.matchAll(/<footprint>([\s\S]*?)<\/footprint>/g)) {
      const block = m[1] ?? ""
      geom += (block.match(GEOM_RE) ?? []).length
      hiPrec += (block.match(HIPREC_RE) ?? []).length
    }
    if (geom === 0) continue // no land to judge (string footprint / pure re-export)
    rows.push({ file: `imports/${name}`, geom, hiPrec, handDrawn: hiPrec === 0 })
  }
  rows.sort((a, b) => Number(b.handDrawn) - Number(a.handDrawn) || a.file.localeCompare(b.file))
  return { rows, flagged: rows.filter((r) => r.handDrawn).length }
}
