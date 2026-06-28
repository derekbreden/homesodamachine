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
 *
 * Single-flight per board (run-lock): a fresh run supersedes an older run of the
 * same board. Subprocesses run async; a supersede signal interrupts the build in
 * progress.
 */
import { composeViews, SCHEMES } from "./gerber-compose"
import { backSilkBoardTsx } from "./bottom-silk"
import { dedupDrill } from "./dedup-drill"
import { applyPrettyRoutes } from "./pretty-routes"
import { singleflight } from "./run-lock"
import { spawn, type ChildProcess } from "node:child_process"
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

const outDir = path.join(dir, "out")
mkdirSync(outDir, { recursive: true })
const zip = path.join(outDir, `${board}.gerbers.zip`)
// tsci writes -o relative to cwd (and mangles an absolute path), so hand it a
// cwd-relative target; we keep the absolute `zip` for the unzip step.
const zipRel = path.join("out", `${board}.gerbers.zip`)
const tsci = path.join(dir, "node_modules", ".bin", "tsci")

// Temp files/dirs to remove on exit (normal OR superseded — process.exit fires
// the `exit` handler), tracked as they're created so cleanup needs no scope.
const temps = new Set<string>()
const track = (p: string) => (temps.add(p), p)
process.on("exit", () => { for (const p of temps) try { rmSync(p, { recursive: true, force: true }) } catch {} })

// Become the only running render for this board; if a newer run supersedes us it
// SIGTERMs us and our handler (in run-lock) kills the child below + exits.
let child: ChildProcess | null = null
const lock = singleflight(board, process.env.RENDER_SOURCE || "manual")
lock.setChildKiller(() => { try { child?.kill("SIGKILL") } catch {} })

// Async exec that mimics execFileSync's throw-on-nonzero (e.status/stdout/stderr)
// while keeping the event loop free, so a supersede signal lands immediately and
// `child` can be killed mid-run.
function sh(cmd: string, args: string[], opts: { cwd?: string; inherit?: boolean } = {}): Promise<string> {
  return new Promise((resolve, reject) => {
    const c = spawn(cmd, args, { cwd: opts.cwd, stdio: opts.inherit ? "inherit" : ["ignore", "pipe", "pipe"] })
    child = c
    let out = "", err = ""
    c.stdout?.on("data", (d) => (out += d))
    c.stderr?.on("data", (d) => (err += d))
    c.on("error", (e) => { if (child === c) child = null; reject(e) })
    c.on("close", (code) => {
      if (child === c) child = null
      if (code === 0) resolve(out)
      else reject(Object.assign(new Error(`${cmd} exited ${code}`), { status: code, stdout: out, stderr: err }))
    })
  })
}

// Resolve declared 2nd-pass routes: pretty="<strategy>:<group>" on a <trace> means
// "route this by net identity with the pretty router." applyPrettyRoutes routes those
// groups in-process against a fresh obstacle field and writes a throwaway routed .tsx
// (pretty attrs stripped, computed <pcbtrace> copper injected) that the rest of the
// build renders. So 2nd-pass routes regenerate from live geometry every build — never
// frozen into the source, never able to go stale. No-op (returns `board`) otherwise.
const exportCircuitJson = async (name: string) => {
  const out = `.${name}.cj.tmp.json`
  await sh(tsci, ["export", "-f", "circuit-json", "-o", out, `${name}.tsx`], { cwd: dir })
  const cj = JSON.parse(readFileSync(path.join(dir, out), "utf8"))
  rmSync(path.join(dir, out), { force: true }); rmSync(path.join(dir, `${name}.circuit.json`), { force: true })
  return cj
}
const renderName = await applyPrettyRoutes(dir, board, exportCircuitJson)
if (renderName !== board) track(path.join(dir, `${renderName}.tsx`))

// Build + route + export the Gerbers. A routing/DRC failure surfaces on stderr.
console.log(`[${board}] exporting gerbers… (cwd=${dir})`)
try {
  await sh(tsci, ["export", "-f", "gerbers", "-o", zipRel, `${renderName}.tsx`], { cwd: dir })
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
const cjAbs = track(path.join(dir, cjRel))
let circuit: any[] | null = null
try {
  await sh(tsci, ["export", "-f", "circuit-json", "-o", cjRel, `${renderName}.tsx`], { cwd: dir })
  circuit = JSON.parse(readFileSync(cjAbs, "utf8"))
} catch {
  console.error(`[${board}] circuit-json export failed — back silk + picks skipped`)
}

// Unzip into a scratch dir, synthesize the back silk into it, compose, clean up.
const scratch = track(mkdtempSync(path.join(tmpdir(), `pcb-${board}-`)))
try {
  await sh("unzip", ["-o", "-q", zip, "-d", scratch])
  // Dedup the drill files: the tscircuit gerber exporter writes every mechanical
  // (NPTH) mounting hole into drill.drl (PTH) too, at identical coords — a fab
  // drill conflict. Strip the NPTH coords from drill.drl and re-zip the corrected
  // file so the fabrication set has each hole exactly once. (dedup-drill.ts.)
  try {
    const { removed, droppedTools } = dedupDrill(scratch)
    if (removed) {
      await sh("zip", ["-q", "-j", zip, path.join(scratch, "drill.drl")])
      console.log(`[${board}] drill dedup: removed ${removed} duplicate PTH holes (tools ${droppedTools.join(",")} were NPTH-only)`)
    }
  } catch {
    console.error(`[${board}] drill dedup failed — fab zip may carry duplicate PTH/NPTH holes`)
  }
  // Back silk: tscircuit only draws the front legend. Build a throwaway board of
  // layer="bottom" copies of every front silk element (same engine -> identical
  // font + per-size stroke) and lift its B_SilkScreen, so the bottom view and the
  // fab set carry a back legend that matches the front exactly. tscircuit mirrors
  // each glyph in place; the compositor's bottom view flips it readable, and the
  // gerber stays correct on the real board. Drop it into the scratch + gerber zip.
  if (circuit) {
    const bsTsx = `.${board}.backsilk.tmp.tsx`
    const bsZipRel = path.join("out", `.${board}.backsilk.tmp.zip`)
    track(path.join(dir, bsTsx))
    track(path.join(dir, bsZipRel))
    try {
      writeFileSync(path.join(dir, bsTsx), backSilkBoardTsx(circuit))
      await sh(tsci, ["export", "-f", "gerbers", "-o", bsZipRel, bsTsx], { cwd: dir })
      const bsScratch = track(mkdtempSync(path.join(tmpdir(), `pcb-${board}-bsilk-`)))
      await sh("unzip", ["-o", "-q", path.join(dir, bsZipRel), "-d", bsScratch])
      const bsilkPath = path.join(scratch, "B_SilkScreen.gbr")
      writeFileSync(bsilkPath, readFileSync(path.join(bsScratch, "B_SilkScreen.gbr")))
      await sh("zip", ["-q", "-j", zip, bsilkPath])
    } catch {
      console.error(`[${board}] back-silk render failed — bottom view shows no back legend`)
    }
  }
  const { top, bottom, overlay, inners, widthMm, heightMm } = await composeViews(scratch, scheme)
  // top/bottom/overlay always; plus one solo view per inner copper layer (4-layer+).
  const svgs: Record<string, string> = { top, bottom, overlay, ...inners }
  const views = Object.keys(svgs)
  for (const v of views) {
    const svg = svgs[v]
    writeFileSync(path.join(outDir, `${board}.${v}.svg`), svg)
    // PNG width tracks the board's aspect so neither view is squashed.
    const png = new Resvg(svg, { fitTo: { mode: "width", value: 1600 } }).render().asPng()
    writeFileSync(path.join(outDir, `${board}.${v}.png`), png)
  }
  console.log(`[${board}] ${widthMm} × ${heightMm} mm — wrote ${board}.{${views.join(",")}}.{svg,png} (${schemeName})`)
  // Surface the assembly BOM + CPL (they ride inside the gerber zip) as first-class
  // out/ files, so every render leaves a diffable BOM/CPL: the JLCPCB part numbers and
  // placements, checkable as each part is wired rather than discovered at fab time. The
  // wired count (parts carrying a JLCPCB #) is the coverage signal as modules convert.
  try {
    const bom = readFileSync(path.join(scratch, "bom.csv"), "utf8")
    writeFileSync(path.join(outDir, `${board}.bom.csv`), bom)
    writeFileSync(path.join(outDir, `${board}.cpl.csv`), readFileSync(path.join(scratch, "pick_and_place.csv")))
    const rows = bom.trimEnd().split("\n").slice(1).filter(Boolean)
    const wired = rows.filter((r) => r.split(",").pop()?.trim()).length
    console.log(`[${board}] wrote ${board}.{bom,cpl}.csv — ${wired}/${rows.length} parts carry a JLCPCB #`)
  } catch {
    console.error(`[${board}] BOM/CPL not found in the gerber export`)
  }
} finally {
  rmSync(scratch, { recursive: true, force: true })
}

// Distill the board's pickable entities (pads + identity) next to the views so
// the web viewer's pad picker has semantic data in lockstep with the copper.
// Reuses the circuit-json above. Best-effort: a render still ships its views.
try {
  await sh("bun", [path.join(dir, "pick-data.ts"), `${board}.tsx`, cjRel], { cwd: dir, inherit: true })
} catch {
  console.error(`[${board}] pick-data failed — picks.json not refreshed (views still written)`)
}

lock.release()
