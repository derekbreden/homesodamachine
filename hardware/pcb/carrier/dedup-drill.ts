/**
 * dedup-drill — strip mounting-hole coordinates that the tscircuit gerber
 * exporter writes into BOTH drill files from the PLATED one.
 *
 * Mechanical `<hole>` elements (module/board mounting holes) are non-plated, and
 * the exporter correctly emits them to drill_npth.drl. But it ALSO emits the same
 * coordinates into drill.drl (the plated/PTH file) at identical X/Y and diameter.
 * A coincident PTH+NPTH hit is a drill conflict: JLCPCB (and most fabs) will hold
 * the order for a DFM query, double-drill (oversized/torn hole), or plate a hole
 * meant to be unplated. The board's circuit-json carries these holes as NPTH only
 * (plated drills are 0.7/1.0 mm; the 2.0/2.4/3.0/4.2 mm tools in drill.drl exist
 * only because of this duplication), so the NPTH file is authoritative.
 *
 * `dedupDrill(dir)` rewrites `<dir>/drill.drl` in place: every coordinate present
 * in drill_npth.drl is removed from drill.drl, and any Excellon tool left with no
 * coordinates is dropped (its T-code definition + select). Defensive: on any
 * unexpected structure it leaves the file untouched and returns {removed:0}.
 */
import { readFileSync, writeFileSync, existsSync } from "node:fs"
import path from "node:path"

const coordRe = /^X(-?\d+(?:\.\d+)?)Y(-?\d+(?:\.\d+)?)$/
const toolSelRe = /^T(\d+)$/
const toolDefRe = /^T(\d+)C[\d.]+/

const key = (x: string, y: string) => `${Math.round(parseFloat(x) * 1e4)},${Math.round(parseFloat(y) * 1e4)}`

/** Collect the {x,y} coordinate keys listed in an Excellon body. */
function coordKeys(text: string): Set<string> {
  const s = new Set<string>()
  for (const line of text.split(/\r?\n/)) {
    const m = line.trim().match(coordRe)
    if (m) s.add(key(m[1], m[2]))
  }
  return s
}

export function dedupDrill(dir: string): { removed: number; droppedTools: number[] } {
  const pth = path.join(dir, "drill.drl")
  const npth = path.join(dir, "drill_npth.drl")
  if (!existsSync(pth) || !existsSync(npth)) return { removed: 0, droppedTools: [] }

  const npthSet = coordKeys(readFileSync(npth, "utf8"))
  if (!npthSet.size) return { removed: 0, droppedTools: [] }

  const lines = readFileSync(pth, "utf8").split(/\r?\n/)
  const pctIdx = lines.findIndex((l) => l.trim() === "%")
  if (pctIdx < 0) return { removed: 0, droppedTools: [] } // unexpected: leave untouched

  // --- pass 1: walk the body, drop duplicated coords, tally which tools survive
  const usedTool = new Set<string>()
  let cur = ""
  let removed = 0
  const bodyKeep: boolean[] = []
  for (let i = pctIdx + 1; i < lines.length; i++) {
    const t = lines[i].trim()
    const sel = t.match(toolSelRe)
    if (sel) { cur = sel[1]; bodyKeep[i] = true; continue } // decide tool-select lines in pass 2
    const co = t.match(coordRe)
    if (co) {
      if (npthSet.has(key(co[1], co[2]))) { removed++; bodyKeep[i] = false }
      else { usedTool.add(cur); bodyKeep[i] = true }
      continue
    }
    bodyKeep[i] = true // G-codes, M30, blanks, comments
  }
  if (!removed) return { removed: 0, droppedTools: [] }

  // --- rebuild header: keep only tool defs whose tool survived; carry each def's
  //     leading comment line(s) only when the def itself is kept.
  const droppedTools: number[] = []
  const header: string[] = []
  let pending: string[] = []
  for (let i = 0; i <= pctIdx; i++) {
    const raw = lines[i]
    const def = raw.trim().match(toolDefRe)
    if (def) {
      if (usedTool.has(def[1])) { header.push(...pending, raw) }
      else { droppedTools.push(parseInt(def[1], 10)) }
      pending = []
      continue
    }
    if (raw.trim().startsWith(";")) { pending.push(raw); continue } // buffer comments for the next def
    header.push(...pending, raw)
    pending = []
  }

  // --- rebuild body: drop removed coords; drop tool-selects whose tool didn't survive
  const body: string[] = []
  for (let i = pctIdx + 1; i < lines.length; i++) {
    if (!bodyKeep[i]) continue
    const sel = lines[i].trim().match(toolSelRe)
    if (sel && !usedTool.has(sel[1])) continue
    body.push(lines[i])
  }

  writeFileSync(pth, [...header, ...body].join("\n"))
  return { removed, droppedTools }
}

// CLI: `bun dedup-drill.ts <dir-with-drill-files>` — for testing on an unzipped set.
if (import.meta.main) {
  const dir = process.argv[2] || "."
  const r = dedupDrill(dir)
  console.log(`dedup-drill: removed ${r.removed} duplicated PTH coords; dropped tools [${r.droppedTools.join(",")}]`)
}
