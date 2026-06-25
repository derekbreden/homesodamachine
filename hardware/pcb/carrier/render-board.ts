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
import { backSilkBoardTsx } from "./bottom-silk"
import { execFileSync } from "node:child_process"
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from "node:fs"
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
  execFileSync(tsci, ["export", "-f", "gerbers", "-o", zipRel, `${board}.tsx`], {
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

// Export the board's circuit-json once: the back-silk synthesis and the pick
// distiller both need the structured entities (texts, pads, nets), not just the
// anonymous copper Gerbers. tsci mangles an absolute -o, so keep it cwd-relative
// inside the board dir; pick-data reuses it so this is the only extra build.
const cjRel = `.${board}.circuit.tmp.json`
const cjAbs = path.join(dir, cjRel)
let circuit: any[] | null = null
try {
  execFileSync(tsci, ["export", "-f", "circuit-json", "-o", cjRel, `${board}.tsx`], { cwd: dir, stdio: ["ignore", "pipe", "pipe"] })
  circuit = JSON.parse(readFileSync(cjAbs, "utf8"))
} catch {
  console.error(`[${board}] circuit-json export failed — back silk + picks skipped`)
}

// Unzip into a scratch dir, synthesize the back silk into it, compose, clean up.
const scratch = mkdtempSync(path.join(tmpdir(), `pcb-${board}-`))
try {
  execFileSync("unzip", ["-o", "-q", zip, "-d", scratch])
  // Back silk: tscircuit only draws the front legend. Build a throwaway board of
  // layer="bottom" copies of every front silk element (same engine -> identical
  // font + per-size stroke) and lift its B_SilkScreen, so the bottom view and the
  // fab set carry a back legend that matches the front exactly. tscircuit mirrors
  // each glyph in place; the compositor's bottom view flips it readable, and the
  // gerber stays correct on the real board. Drop it into the scratch + gerber zip.
  if (circuit) {
    const bsTsx = `.${board}.backsilk.tmp.tsx`
    const bsZipRel = path.join("out", `.${board}.backsilk.tmp.zip`)
    const bsZipAbs = path.join(dir, bsZipRel)
    try {
      writeFileSync(path.join(dir, bsTsx), backSilkBoardTsx(circuit))
      execFileSync(tsci, ["export", "-f", "gerbers", "-o", bsZipRel, bsTsx], { cwd: dir, stdio: ["ignore", "pipe", "pipe"] })
      const bsScratch = mkdtempSync(path.join(tmpdir(), `pcb-${board}-bsilk-`))
      try {
        execFileSync("unzip", ["-o", "-q", bsZipAbs, "-d", bsScratch])
        const bsilkPath = path.join(scratch, "B_SilkScreen.gbr")
        writeFileSync(bsilkPath, readFileSync(path.join(bsScratch, "B_SilkScreen.gbr")))
        execFileSync("zip", ["-q", "-j", zip, bsilkPath])
      } finally {
        rmSync(bsScratch, { recursive: true, force: true })
      }
    } catch {
      console.error(`[${board}] back-silk render failed — bottom view shows no back legend`)
    } finally {
      rmSync(path.join(dir, bsTsx), { force: true })
      rmSync(bsZipAbs, { force: true })
    }
  }
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

// Distill the board's pickable entities (pads + identity) next to the views so
// the web viewer's pad picker has semantic data in lockstep with the copper.
// Reuses the circuit-json above. Best-effort: a render still ships its views.
try {
  execFileSync("bun", [path.join(dir, "pick-data.ts"), `${board}.tsx`, cjRel], { cwd: dir, stdio: "inherit" })
} catch {
  console.error(`[${board}] pick-data failed — picks.json not refreshed (views still written)`)
} finally {
  rmSync(cjAbs, { force: true })
}
