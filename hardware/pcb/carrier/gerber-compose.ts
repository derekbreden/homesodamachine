/**
 * Compose a board's copper layers into three aligned, high-visibility views —
 * Top (front copper), Bottom (back copper, seen through the board), and Overlay
 * (both at once, one warm hue and one cool, so you read which side a trace is on
 * by its colour). Built straight from the fabrication Gerbers, so the lines have
 * the real widths the board is made with.
 *
 * gerber-to-svg renders each layer with `fill="currentColor"` and flips it about
 * that layer's OWN vertical centre (`translate(0,Ty) scale(1,-1)`), so two layers
 * do not share a frame out of the box. We strip each layer's wrapper, collect the
 * raw (un-flipped) Gerber geometry, and re-wrap every layer under one flip about
 * the shared board centre — exact alignment, and `currentColor` lets a parent
 * `<g style="color:…">` paint each layer any colour we like.
 *
 *   import { composeViews, SCHEMES } from "./gerber-compose"
 *   const { top, bottom, overlay, width, height } = composeViews(dir, SCHEMES.copper)
 */
import gerberToSvg from "gerber-to-svg"
import { readFileSync } from "node:fs"

export type Scheme = {
  fr4: string // board substrate (the background)
  top: string // front copper
  bottom: string // back copper
  drill: string // drilled holes (painted over the copper so they read as holes)
  edge: string // board outline
  topOpacity: number // front copper opacity in the overlay
  bottomOpacity: number // back copper opacity in the overlay
}

// Bright copper-on-near-black, warm front / cool back. The default: thin traces
// stay legible because the copper is high-luminance, and the warm/cool split
// makes the overlay read at a glance.
export const SCHEMES: Record<string, Scheme> = {
  copper: {
    fr4: "#0b0e14",
    top: "#ffb04a",
    bottom: "#34d1e0",
    drill: "#0b0e14",
    edge: "#5a6478",
    topOpacity: 0.85,
    bottomOpacity: 0.8,
  },
  blueprint: {
    fr4: "#0a2540",
    top: "#aee4ff",
    bottom: "#ffcf6b",
    drill: "#0a2540",
    edge: "#4d7299",
    topOpacity: 0.85,
    bottomOpacity: 0.8,
  },
  ink: {
    fr4: "#f4f1ea",
    top: "#17191e",
    bottom: "#c4382c",
    drill: "#f4f1ea",
    edge: "#9aa0a6",
    topOpacity: 0.8,
    bottomOpacity: 0.8,
  },
}

// A layer rendered by gerber-to-svg, reduced to what we need to re-frame it:
// the aperture <defs>, the raw geometry (children of the flip group), and the
// per-layer flip offset Ty so we can recover raw Gerber bounds.
type Layer = { defs: string; body: string; ty: number; vb: [number, number, number, number] }

// gerber-to-svg parses the string on a stream and fires its callback on the
// async `end`, so the converter's viewBox is only ready inside the callback —
// hence the Promise.
function renderLayer(file: string, id: string): Promise<Layer | null> {
  return new Promise((resolve) => {
    let src: string
    try {
      src = readFileSync(file, "utf8")
    } catch {
      return resolve(null)
    }
    const conv: any = gerberToSvg(src, { id }, (err: any) => {
      if (err || !conv || !conv.viewBox) return resolve(null)
      const svg: string = gerberToSvg.render(gerberToSvg.clone(conv), id)
      const vb = conv.viewBox as [number, number, number, number]

      const defsMatch = svg.match(/<defs>([\s\S]*?)<\/defs>/)
      const defs = defsMatch ? defsMatch[1] : ""

      // The post-defs remainder is the single flip group. Pull Ty and the raw
      // geometry it wraps.
      const afterDefs = svg.slice(svg.indexOf("</defs>") + 7, svg.lastIndexOf("</svg>"))
      const gMatch = afterDefs.match(/<g\s+transform="translate\(0,(-?\d+(?:\.\d+)?)\)\s*scale\(1,-1\)"[^>]*>([\s\S]*)<\/g>\s*$/)
      if (!gMatch) return resolve(null)
      resolve({ defs, body: gMatch[2], ty: parseFloat(gMatch[1]), vb })
    })
  })
}

// Raw (un-flipped) Gerber bounds of a layer. The flip maps raw (x,y) to SVG
// (x, Ty - y); inverting the layer's viewBox recovers the raw extent.
function rawBounds(l: Layer) {
  const [vx, vy, vw, vh] = l.vb
  return { x0: vx, x1: vx + vw, y0: l.ty - (vy + vh), y1: l.ty - vy }
}

function fnum(n: number) {
  return Number.isInteger(n) ? String(n) : n.toFixed(3)
}

export async function composeViews(dir: string, scheme: Scheme) {
  // Layers we draw, by role. Edge_Cuts defines the board frame; copper is the
  // subject; drills punch holes back out of the copper.
  const [fcu, bcu, edge, drl, drlN] = await Promise.all([
    renderLayer(`${dir}/F_Cu.gbr`, "fcu"),
    renderLayer(`${dir}/B_Cu.gbr`, "bcu"),
    renderLayer(`${dir}/Edge_Cuts.gbr`, "edge"),
    renderLayer(`${dir}/drill.drl`, "drl"),
    renderLayer(`${dir}/drill_npth.drl`, "drln"),
  ])

  const present = [fcu, bcu, edge, drl, drlN].filter(Boolean) as Layer[]
  if (present.length === 0) throw new Error(`no renderable layers in ${dir}`)

  // Unified frame: the board outline if we have it, else the union of every
  // layer's raw extent (copper can spill a hair past the cut line).
  const frameLayers = edge ? [edge] : present
  let Xmin = Infinity, Xmax = -Infinity, Ymin = Infinity, Ymax = -Infinity
  for (const l of frameLayers) {
    const b = rawBounds(l)
    Xmin = Math.min(Xmin, b.x0); Xmax = Math.max(Xmax, b.x1)
    Ymin = Math.min(Ymin, b.y0); Ymax = Math.max(Ymax, b.y1)
  }
  const W = Xmax - Xmin
  const H = Ymax - Ymin
  const Tu = Ymin + Ymax // flip about the shared board centre

  // All apertures, once. Layer ids are prefixed by gerber-to-svg so no clash.
  const allDefs = present.map((l) => l.defs).join("")

  // Paint a layer: its raw geometry under the shared flip, in `color`. The
  // geometry inherits paint from its group — pads/regions fill, traces (drawn
  // fill="none") stroke — so the wrapper sets both. Setting literal fill/stroke
  // (rather than an inherited CSS color / currentColor) resolves in every
  // renderer, resvg included.
  const paint = (l: Layer | null, color: string, opacity = 1) =>
    l ? `<g fill="${color}" stroke="${color}"${opacity !== 1 ? ` opacity="${opacity}"` : ""}>${l.body}</g>` : ""

  const drillPunch = `${paint(drl, scheme.drill)}${paint(drlN, scheme.drill)}`
  const edgePaint = paint(edge, scheme.edge)
  const vb = `${fnum(Xmin)} ${fnum(Ymin)} ${fnum(W)} ${fnum(H)}`
  const wmm = (W / 1000).toFixed(3)
  const hmm = (H / 1000).toFixed(3)

  // Assemble one view from an ordered stack of painted copper groups. The FR4
  // rect lives in viewBox space (no flip needed — it's the whole frame); the
  // copper, drills and outline live under the single shared flip group.
  const view = (copper: string) =>
    `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ` +
    `width="${wmm}mm" height="${hmm}mm" viewBox="${vb}" ` +
    `stroke-linecap="round" stroke-linejoin="round" stroke-width="0" fill-rule="evenodd">` +
    `<defs>${allDefs}</defs>` +
    `<rect x="${fnum(Xmin)}" y="${fnum(Ymin)}" width="${fnum(W)}" height="${fnum(H)}" fill="${scheme.fr4}"/>` +
    `<g transform="translate(0,${fnum(Tu)}) scale(1,-1)">${copper}${drillPunch}${edgePaint}</g>` +
    `</svg>`

  const top = view(paint(fcu, scheme.top))
  const bottom = view(paint(bcu, scheme.bottom))
  const overlay = view(paint(bcu, scheme.bottom, scheme.bottomOpacity) + paint(fcu, scheme.top, scheme.topOpacity))

  return { top, bottom, overlay, width: W, height: H, widthMm: +wmm, heightMm: +hmm }
}
