/**
 * Render a board's three copper views from its source. Exports the fabrication
 * Gerbers, then composes Top / Bottom / Overlay (gerber-compose) into out/ as
 * both SVG (what the site viewer shows) and PNG (a quick look without the site).
 *
 *   bun render-board.ts <board.tsx> [scheme]
 *
 * scheme is a key of SCHEMES in gerber-compose (default "copper"). This is the
 * generator the dev watcher runs on every save of a board under pcb/, the same
 * way a CadQuery .py regenerates its .step.
 */
import { composeViews, SCHEMES } from "./gerber-compose"
import { execFileSync } from "node:child_process"
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs"
import { tmpdir } from "node:os"
import path from "node:path"
import { Resvg } from "@resvg/resvg-js"

const arg = process.argv[2]
const schemeName = process.argv[3] || "copper"
if (!arg) {
  console.error("usage: bun render-board.ts <board.tsx> [scheme]")
  process.exit(1)
}

const boardFile = path.resolve(arg)
const dir = path.dirname(boardFile)
const board = path.basename(boardFile).replace(/\.tsx$/, "")
const scheme = SCHEMES[schemeName] || SCHEMES.copper
const VIEWS = ["top", "bottom", "overlay"] as const

const outDir = path.join(dir, "out")
mkdirSync(outDir, { recursive: true })
const zip = path.join(outDir, `${board}.gerbers.zip`)
// tsci writes -o relative to cwd (and mangles an absolute path), so hand it a
// cwd-relative target; we keep the absolute `zip` for the unzip step.
const zipRel = path.join("out", `${board}.gerbers.zip`)

// Build + route + export the Gerbers in one step. The local tscircuit CLI runs
// under bun via its shebang; stderr inherited so a routing/DRC failure surfaces.
const tsci = path.join(dir, "node_modules", ".bin", "tsci")
console.log(`[${board}] exporting gerbers… (cwd=${dir})`)
try {
  execFileSync(tsci, ["export", "-f", "gerbers", "-o", zip, `${board}.tsx`], {
    cwd: dir,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  })
} catch (e: any) {
  console.error(`[${board}] gerber export failed (status ${e.status})`)
  if (e.stdout) console.error("stdout:", String(e.stdout).slice(-1000))
  if (e.stderr) console.error("stderr:", String(e.stderr).slice(-1000))
  throw e
}

// Unzip into a scratch dir, compose, clean up.
const scratch = mkdtempSync(path.join(tmpdir(), `pcb-${board}-`))
try {
  execFileSync("unzip", ["-o", "-q", zip, "-d", scratch])
  const { top, bottom, overlay, widthMm, heightMm } = await composeViews(scratch, scheme)
  const svgs = { top, bottom, overlay }
  for (const v of VIEWS) {
    const svg = svgs[v]
    writeFileSync(path.join(outDir, `${board}.${v}.svg`), svg)
    // PNG width tracks the board's aspect so neither view is squashed.
    const png = new Resvg(svg, { fitTo: { mode: "width", value: 1600 } }).render().asPng()
    writeFileSync(path.join(outDir, `${board}.${v}.png`), png)
  }
  console.log(`[${board}] ${widthMm} × ${heightMm} mm — wrote ${board}.{${VIEWS.join(",")}}.{svg,png} (${schemeName})`)
} finally {
  rmSync(scratch, { recursive: true, force: true })
}
