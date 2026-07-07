/**
 * Render the board's top and bottom faces as green-soldermask textures for the
 * 3D model (board-3d.py maps them onto the GLB board's faces). Reads the
 * fabrication Gerbers from out/<board>.gerbers.zip, composes them in the green
 * board3d scheme (gerber-compose), and rasterizes each to a PNG.
 *
 *   bun board-texture.ts [board]   (default board = this directory's name)
 *
 * Writes out/<board>.top3d.png and out/<board>.bottom3d.png, each covering the
 * board's Edge_Cuts bounding box (top-left = Xmin,Ymax) so a face plane sized to
 * that box maps 1:1.
 */
import { composeViews, SCHEMES } from "./gerber-compose"
import { Resvg } from "@resvg/resvg-js"
import { spawnSync } from "node:child_process"
import { mkdtempSync, writeFileSync, existsSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import path from "node:path"

const dir = process.cwd()
const board = process.argv[2] || path.basename(dir)
const zip = path.join(dir, "out", `${board}.gerbers.zip`)
if (!existsSync(zip)) {
  console.error(`[${board}] no ${path.relative(dir, zip)} — render the board first (render-board.ts)`)
  process.exit(1)
}

const scratch = mkdtempSync(path.join(tmpdir(), `tex-${board}-`))
try {
  spawnSync("unzip", ["-o", "-q", zip, "-d", scratch])
  const { top, bottom, widthMm, heightMm } = await composeViews(scratch, SCHEMES.board3d)
  const px = 2048 // texture width; height follows the board aspect
  for (const [name, svg] of [["top3d", top], ["bottom3d", bottom]] as const) {
    const png = new Resvg(svg, { fitTo: { mode: "width", value: px } }).render().asPng()
    writeFileSync(path.join(dir, "out", `${board}.${name}.png`), png)
  }
  console.log(`[${board}] wrote out/${board}.{top3d,bottom3d}.png — ${widthMm} × ${heightMm} mm`)
} finally {
  rmSync(scratch, { recursive: true, force: true })
}
