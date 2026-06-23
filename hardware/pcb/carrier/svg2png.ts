/**
 * Rasterize a tscircuit SVG export to PNG so the board can be eyeballed
 * directly (the Read tool renders PNGs, not SVGs). Headless — no browser.
 *
 *   bun svg2png.ts <in.svg> <out.png> [widthPx=1600]
 */
import { Resvg } from "@resvg/resvg-js"
import { readFileSync, writeFileSync } from "node:fs"

const [, , svgPath, pngPath, widthStr] = process.argv
if (!svgPath || !pngPath) {
  console.error("usage: bun svg2png.ts <in.svg> <out.png> [widthPx]")
  process.exit(1)
}
const svg = readFileSync(svgPath, "utf8")
const resvg = new Resvg(svg, {
  background: "white",
  fitTo: { mode: "width", value: Number(widthStr ?? 1600) },
})
writeFileSync(pngPath, resvg.render().asPng())
console.log(`wrote ${pngPath}`)
