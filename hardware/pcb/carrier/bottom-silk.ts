/**
 * Synthesize the back-side silkscreen from the front.
 *
 * tscircuit draws every label and outline on the TOP silk only (F_SilkScreen);
 * the back is blank. For a hand-wired through-hole board you read the labels
 * from the solder side too, so we want the same legend mirrored onto the bottom
 * — and "mirrored" has to be *in place*: each label stays next to its own
 * through-hole pad (same x,y) but its glyphs flip left-right, so it reads the
 * right way round when you turn the board over. A whole-layer flip would move
 * every label to its mirror-image pad, which is wrong.
 *
 * So we read the structured silk out of the circuit JSON (exact pad-anchored
 * positions) and re-render each text with @tscircuit/alphabet — the same vector
 * font tscircuit uses — reflected about the text's own centre. Outlines (silk
 * paths) are component footprints, identical on both faces, so they copy across
 * unmirrored. The result is written as a Gerber the compositor and the fab set
 * both consume as B_SilkScreen.
 */
import { lineAlphabet, glyphAdvanceRatio, spaceWidthRatio, strokeWidthRatio } from "@tscircuit/alphabet"

type Seg = { x1: number; y1: number; x2: number; y2: number; w: number }

// Lay a string out left-to-right in em units (font_size = 1), then scale by F.
// Returns segments in a local frame whose origin is the layout start / baseline.
function glyphSegments(text: string, F: number): Seg[] {
  const w = strokeWidthRatio * F
  const segs: Seg[] = []
  let penX = 0
  for (const ch of text) {
    if (ch === " ") { penX += spaceWidthRatio; continue }
    const g = (lineAlphabet as Record<string, { x1: number; y1: number; x2: number; y2: number }[]>)[ch]
    if (g) for (const s of g) segs.push({ x1: (s.x1 + penX) * F, y1: s.y1 * F, x2: (s.x2 + penX) * F, y2: s.y2 * F, w })
    penX += (glyphAdvanceRatio as Record<string, number>)[ch] ?? (glyphAdvanceRatio as Record<string, number>).A ?? 0.692
  }
  return segs
}

// One silkscreen text -> world-frame segments, centred on its anchor, glyphs
// mirrored about the text's own vertical axis (so it reads from the back), then
// rotated by the text's rotation and dropped at the anchor.
function mirrorText(t: any): Seg[] {
  const F = t.font_size as number
  const segs = glyphSegments(t.text, F)
  if (!segs.length) return []
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
  for (const s of segs) {
    minX = Math.min(minX, s.x1, s.x2); maxX = Math.max(maxX, s.x1, s.x2)
    minY = Math.min(minY, s.y1, s.y2); maxY = Math.max(maxY, s.y1, s.y2)
  }
  const ox = (minX + maxX) / 2, oy = (minY + maxY) / 2
  const th = ((t.ccw_rotation || 0) * Math.PI) / 180
  const cos = Math.cos(th), sin = Math.sin(th)
  const ax = t.anchor_position.x, ay = t.anchor_position.y
  // local: centre at origin and mirror x (-(x-ox)); then rotate; then translate.
  const map = (x: number, y: number): [number, number] => {
    const lx = -(x - ox), ly = y - oy
    return [ax + (lx * cos - ly * sin), ay + (lx * sin + ly * cos)]
  }
  return segs.map((s) => {
    const [x1, y1] = map(s.x1, s.y1)
    const [x2, y2] = map(s.x2, s.y2)
    return { x1, y1, x2, y2, w: s.w }
  })
}

// A silk path (component outline) copies straight across — same footprint on
// both faces, nothing to mirror.
function copyPath(p: any): Seg[] {
  const w = p.stroke_width || 0.15
  const r = p.route || []
  const segs: Seg[] = []
  for (let i = 0; i + 1 < r.length; i++) segs.push({ x1: r[i].x, y1: r[i].y, x2: r[i + 1].x, y2: r[i + 1].y, w })
  return segs
}

const u = (mm: number) => Math.round(mm * 1e6) // 4.6 format: mm -> integer

// Emit a minimal RS-274X Gerber: one round aperture per distinct stroke width,
// each segment a move (D02) + draw (D01).
function toGerber(segs: Seg[]): string {
  const widths = [...new Set(segs.map((s) => +s.w.toFixed(4)))].sort((a, b) => a - b)
  const ap: Record<number, number> = {}
  const out: string[] = [
    "G04 B_SilkScreen synthesized from front silk (mirrored in place)*",
    "%FSLAX46Y46*%",
    "%MOMM*%",
    "%LPD*%",
  ]
  let d = 10
  for (const w of widths) { ap[w] = d; out.push(`%ADD${d}C,${w.toFixed(4)}*%`); d++ }
  out.push("G01*")
  let cur = -1
  for (const s of segs) {
    const a = ap[+s.w.toFixed(4)]
    if (a !== cur) { out.push(`D${a}*`); cur = a }
    out.push(`X${u(s.x1)}Y${u(s.y1)}D02*`)
    out.push(`X${u(s.x2)}Y${u(s.y2)}D01*`)
  }
  out.push("M02*")
  return out.join("\n") + "\n"
}

/** Build the back-silk Gerber from a board's circuit-json elements. */
export function bottomSilkGerber(circuit: any[]): string {
  const segs: Seg[] = []
  for (const e of circuit) {
    if (e.type === "pcb_silkscreen_text" && e.layer === "top" && e.text) segs.push(...mirrorText(e))
    else if (e.type === "pcb_silkscreen_path" && e.layer === "top") segs.push(...copyPath(e))
  }
  return toGerber(segs)
}
