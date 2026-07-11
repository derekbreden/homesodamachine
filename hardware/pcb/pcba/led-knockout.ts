/**
 * LED name badges — knockout silk the gerber can't express, injected into F_SilkScreen.
 *
 * The indicator LEDs are named with a KNOCKOUT badge instead of plain text: a filled silk
 * background with the letters showing through as bare board (green-on-white, not white-on-green).
 * Each badge is a D — a flat WEST edge, a semicircular EAST cap — sized to sit in its 2.5 mm row
 * with a thin gap to its neighbours, and stretched WEST to wrap its own LED. The LED's two pads are
 * bare copper, so the fill is cut back around them (antipads): no silk prints on a pad.
 *
 * circuit-json has no filled-silk-with-holes primitive (only strokes and knockout-RECT text), so
 * this emits the badges directly as RS-274X into the front silk layer: one dark region for each D
 * (`G36…G37`), then a clear pass (`%LPC*%`) that knocks the vector text and the pad antipads out of
 * it. The vector font is the SAME Hershey table circuit-json-to-gerber draws with (read out of the
 * installed package), so the letters match every other silk glyph on the board. render-board.ts
 * splices the returned fragment in before `M02*`.
 *
 * Geometry is board-mm; the front silk gerber is 1:1 with board coords (no y-flip), same as every
 * other F_SilkScreen feature — verified against the fab strokes in silk-audit.py.
 */
import { readFileSync, readdirSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const HERE = path.dirname(fileURLToPath(import.meta.url))

// The label on each LED, west→east down the column. Positions come from the LEDs themselves
// (read from circuit-json), so the badges ride with D2–D6 if the column moves.
const LABELS: { text: string; led: string }[] = [
  { text: "ERR", led: "D2" },
  { text: "RUN", led: "D3" },
  { text: "ACT", led: "D4" },
  { text: "PWR", led: "D5" },
  { text: "5V", led: "D6" },
]

// Badge shape (board mm).
const FONT = 1.4          // label cap size (matches the old plain labels)
const WEST = -41.3        // flat west edge — wraps the LED (pads to -40.9), clears the R to its west (-42.05)
const EAST = -33.4        // rightmost point of the round cap
const HEIGHT = 2.2        // badge height; row pitch is 2.5, so ~0.3 mm of board shows between badges
const PAD_CLEAR = 0.15    // silk pulled back this far from every LED pad edge
const STROKE = 0.15       // knockout letter stroke width
const STROKE_APERTURE = 70 // a fresh D-code for the knockout stroke (added in the fragment)

const CAP = 0.7 // circuit-json-to-gerber CAP_HEIGHT_SCALE

// ---- Hershey stroke font, straight from the gerber generator (stays in lock-step with the fab) --
function loadHershey(): Record<string, { w: number; s: number[][][] }> {
  const dist = path.join(HERE, "node_modules/circuit-json-to-gerber/dist")
  for (const f of readdirSync(dist)) {
    if (!f.endsWith(".js")) continue
    const s = readFileSync(path.join(dist, f), "utf8")
    const i = s.indexOf("const HERSHEY = {")
    if (i < 0) continue
    const lit = s.slice(i + "const HERSHEY = ".length, s.indexOf("};", i) + 1)
    return (0, eval)("(" + lit + ")")
  }
  throw new Error("led-knockout: HERSHEY font not found in circuit-json-to-gerber")
}

type Seg = [[number, number], [number, number]]

// Lay out `text` as Hershey stroke segments, reproducing renderVectorText, then translate so the
// segments' true bounding-box centre sits at (cx, cy) — i.e. optically centred, both axes.
function centeredStrokes(HERSHEY: ReturnType<typeof loadHershey>, text: string, cx: number, cy: number): Seg[] {
  const fs = FONT * CAP, ls = fs * 0.3, space = HERSHEY[" "]!.w * fs
  const glyph = (ch: string) => HERSHEY[ch] ?? HERSHEY["?"]!
  let x = 0
  const raw: Seg[] = []
  for (const ch of text.toUpperCase()) {
    if (ch === " ") { x += space + ls; continue }
    const g = glyph(ch)
    for (const stroke of g.s) {
      for (let i = 0; i + 1 < stroke.length; i++) {
        raw.push([[x + stroke[i][0] * fs, stroke[i][1] * fs], [x + stroke[i + 1][0] * fs, stroke[i + 1][1] * fs]])
      }
    }
    x += g.w * fs + ls
  }
  let minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity
  for (const [a, b] of raw) for (const p of [a, b]) {
    minx = Math.min(minx, p[0]); maxx = Math.max(maxx, p[0]); miny = Math.min(miny, p[1]); maxy = Math.max(maxy, p[1])
  }
  const dx = cx - (minx + maxx) / 2, dy = cy - (miny + maxy) / 2
  return raw.map(([a, b]) => [[a[0] + dx, a[1] + dy], [b[0] + dx, b[1] + dy]])
}

// ---- gerber helpers (FSLAX46, mm, absolute, 1:1 with board coords) ----
const u = (v: number) => Math.round(v * 1e6)
const at = (x: number, y: number) => `X${u(x)}Y${u(y)}`

// LED pad centres/sizes, by component name, from circuit-json.
function ledPads(circuit: any[]): Record<string, { x: number; y: number; w: number; h: number }[]> {
  const compName: Record<string, string> = {}, pcbToSrc: Record<string, string> = {}
  const srcPort: Record<string, any> = {}, pcbPort: Record<string, any> = {}
  for (const e of circuit) {
    if (e.type === "source_component") compName[e.source_component_id] = e.name
    else if (e.type === "pcb_component") pcbToSrc[e.pcb_component_id] = e.source_component_id
    else if (e.type === "source_port") srcPort[e.source_port_id] = e
    else if (e.type === "pcb_port") pcbPort[e.pcb_port_id] = e
  }
  const nameOf = (pcbPortId?: string) => {
    const sp = pcbPortId && pcbPort[pcbPortId] ? srcPort[pcbPort[pcbPortId].source_port_id] : null
    return sp ? compName[sp.source_component_id] : undefined
  }
  const out: Record<string, { x: number; y: number; w: number; h: number }[]> = {}
  for (const e of circuit) {
    if (e.type !== "pcb_smtpad") continue
    const n = nameOf(e.pcb_port_id)
    if (!n) continue
    ;(out[n] ??= []).push({ x: e.x, y: e.y, w: e.width, h: e.height })
  }
  return out
}

/** RS-274X fragment for the five LED knockout badges, to splice into F_SilkScreen before M02*. */
export function ledKnockoutGerber(circuit: any[]): string {
  const HERSHEY = loadHershey()
  const pads = ledPads(circuit)
  const r = HEIGHT / 2, arcX = EAST - r // straight part runs to arcX, then a semicircle of radius r
  const L: string[] = []

  // 1) the dark D fills (default LPD)
  L.push("%LPD*%")
  const rows: { cy: number; text: string; pads: { x: number; y: number; w: number; h: number }[] }[] = []
  for (const { text, led } of LABELS) {
    const p = pads[led]
    if (!p || !p.length) { console.error(`[led-knockout] no pads for ${led} — skipping its badge`); continue }
    const cy = p.reduce((s, q) => s + q.y, 0) / p.length
    rows.push({ cy, text, pads: p })
    L.push(
      "G36*",
      `${at(WEST, cy + r)}D02*`,          // NW
      `${at(WEST, cy - r)}D01*`,          // ↓ flat west edge to SW
      `${at(arcX, cy - r)}D01*`,          // → bottom edge to the cap
      "G03*",                              // CCW: bottom → east → top, in two quadrant arcs
      `${at(arcX, cy)}I0J${u(r)}D01*`,    //   SE quadrant to the east point (centre offset 0,+r)
      `${at(arcX, cy + r)}I${u(-r)}J0D01*`, //   NE quadrant to the top (centre offset -r,0)
      "G01*",
      `${at(WEST, cy + r)}D01*`,          // ← top edge back to NW
      "G37*",
    )
  }

  if (!rows.length) return ""

  // 2) knock the letters + LED-pad antipads out of the fills
  L.push("%LPC*%", `%ADD${STROKE_APERTURE}C,${STROKE.toFixed(6)}*%`, `D${STROKE_APERTURE}*`)
  const padEast = Math.max(...rows[0].pads.map((q) => q.x + q.w / 2)) + PAD_CLEAR
  const textCx = (padEast + arcX) / 2 // centre the label between the LED and the round cap
  for (const { cy, text } of rows) {
    for (const [a, b] of centeredStrokes(HERSHEY, text, textCx, cy)) {
      L.push(`${at(a[0], a[1])}D02*`, `${at(b[0], b[1])}D01*`)
    }
  }
  for (const { pads: ps } of rows) {
    for (const q of ps) {
      const hw = q.w / 2 + PAD_CLEAR, hh = q.h / 2 + PAD_CLEAR
      L.push(
        "G36*",
        `${at(q.x - hw, q.y - hh)}D02*`,
        `${at(q.x + hw, q.y - hh)}D01*`,
        `${at(q.x + hw, q.y + hh)}D01*`,
        `${at(q.x - hw, q.y + hh)}D01*`,
        `${at(q.x - hw, q.y - hh)}D01*`,
        "G37*",
      )
    }
  }
  L.push("%LPD*%")
  return L.join("\n")
}
