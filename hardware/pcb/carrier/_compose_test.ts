import { composeViews, SCHEMES } from "./gerber-compose"
import { writeFileSync } from "node:fs"
import { Resvg } from "@resvg/resvg-js"

const dir = "/tmp/gbprobe"
for (const name of Object.keys(SCHEMES)) {
  const v = await composeViews(dir, SCHEMES[name])
  console.log(`${name}: ${v.widthMm} x ${v.heightMm} mm | top ${v.top.length}B bottom ${v.bottom.length}B overlay ${v.overlay.length}B`)
  for (const [view, svg] of [["top", v.top], ["bottom", v.bottom], ["overlay", v.overlay]] as const) {
    writeFileSync(`/tmp/compose-${name}-${view}.svg`, svg)
    const png = new Resvg(svg, { fitTo: { mode: "width", value: 1400 } }).render().asPng()
    writeFileSync(`/tmp/compose-${name}-${view}.png`, png)
  }
}
console.log("done")
