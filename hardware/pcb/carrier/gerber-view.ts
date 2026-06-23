/**
 * Render a folder of Gerber/drill files to true-to-fab SVGs with pcb-stackup —
 * the actual copper, pads, soldermask, silk and outline at real thicknesses.
 * Two looks: `.real.*` (green soldermask, what's manufactured) and `.cu.*`
 * (soldermask pulled back so the copper traces show in copper).
 *
 *   bun gerber-view.ts <gerber-dir> <out-prefix>
 */
import pcbStackup from "pcb-stackup"
import { readdirSync, readFileSync, writeFileSync } from "node:fs"

const dir = process.argv[2]
const out = process.argv[3]
if (!dir || !out) {
  console.error("usage: bun gerber-view.ts <gerber-dir> <out-prefix>")
  process.exit(1)
}

const files = readdirSync(dir).filter((f) => /\.(gbr|drl|gtl|gbl|gts|gbs|gto|gbo|gko|drd|xln)$/i.test(f))
const contents = files.map((filename) => ({ filename, gerber: readFileSync(`${dir}/${filename}`, "utf8") }))
const fresh = () => contents.map((c) => ({ ...c }))

// what the fab makes
const real = await pcbStackup(fresh())
writeFileSync(`${out}.real.top.svg`, real.top.svg)
writeFileSync(`${out}.real.bottom.svg`, real.bottom.svg)

// copper view: transparent soldermask so the copper shows in copper
const cu = await pcbStackup(fresh(), {
  color: {
    fr4: "#0d1117",
    cu: "#c87533",
    cf: "#e6a45c",
    sm: "rgba(0,0,0,0)",
    ss: "#cfd8dc",
    sp: "rgba(0,0,0,0)",
    out: "#3a3a3a",
  },
})
writeFileSync(`${out}.cu.top.svg`, cu.top.svg)
writeFileSync(`${out}.cu.bottom.svg`, cu.bottom.svg)

console.log(`board ${real.top.width.toFixed(1)} x ${real.top.height.toFixed(1)} mm`)
console.log(`wrote ${out}.real.{top,bottom}.svg and ${out}.cu.{top,bottom}.svg`)
