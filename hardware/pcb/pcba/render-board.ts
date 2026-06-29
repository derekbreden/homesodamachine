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
import { resolvePours } from "./resolve-pours"
import { singleflight } from "./run-lock"
import { convertSoupToGerberCommands, stringifyGerberCommandLayers, convertSoupToExcellonDrillCommands, stringifyExcellonDrill } from "circuit-json-to-gerber"
import { convertCircuitJsonToBomRows, convertBomRowsToCsv } from "circuit-json-to-bom-csv"
import { convertCircuitJsonToPickAndPlaceCsv } from "circuit-json-to-pnp-csv"
import { spawn, type ChildProcess } from "node:child_process"
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync, rmSync } from "node:fs"
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

// Write a board's composed views to out/ as SVG + PNG. Shared by the placement
// preview and the full render (extracted so both paint the views identically).
const writeViews = (svgs: Record<string, string>) => {
  for (const v of Object.keys(svgs)) {
    writeFileSync(path.join(outDir, `${board}.${v}.svg`), svgs[v])
    // PNG width tracks the board's aspect so neither view is squashed.
    writeFileSync(path.join(outDir, `${board}.${v}.png`), new Resvg(svgs[v], { fitTo: { mode: "width", value: 1600 } }).render().asPng())
  }
}

// PHASE 1 — placement preview (dev-server only). Paint where every pad, hole, and
// silk legend lands BEFORE the slow route passes, so an interactive save shows up
// in the viewer in ~3s. Strip the netlist traces + pours (nothing to autoroute, no
// pour to solve, and no flood to hide the pads) and export gerbers in one tsci boot,
// then compose the SAME views the full render does — identical styling AND viewBox,
// so the viewer keeps its pan/zoom across the swap. The full render below overwrites
// out/ with the routed copper and the watcher broadcasts again. Best-effort: any
// failure here just skips the preview; the full render still runs.
async function placementPreview() {
  const placementSrc = readFileSync(boardFile, "utf8")
    .replace(/<trace\b[\s\S]*?\/>/g, "")      // drop every netlist trace
    .replace(/<copperpour\b[\s\S]*?\/>/g, "") // drop every pour
  const name = `_build-${board}.placement.tmp`
  track(path.join(dir, `${name}.tsx`))
  writeFileSync(path.join(dir, `${name}.tsx`), placementSrc)
  const zipRel = path.join("out", `${name}.gerbers.zip`)
  track(path.join(dir, zipRel))
  await sh(tsci, ["export", "-f", "gerbers,circuit-json", "-o", zipRel, `${name}.tsx`], { cwd: dir })
  const cjAbs = track(path.join(dir, `${name}.circuit.json`))
  const scratch = track(mkdtempSync(path.join(tmpdir(), `pcb-${board}-place-`)))
  await sh("unzip", ["-o", "-q", path.join(dir, zipRel), "-d", scratch])
  const { top, bottom, overlay, inners, widthMm, heightMm } = await composeViews(scratch, scheme)
  writeViews({ top, bottom, overlay, ...inners })
  rmSync(scratch, { recursive: true, force: true })
  // Refresh picks from the placement circuit-json (pads only) so the pad picker
  // lands on the new positions during the preview, not the prior render's.
  try {
    const picksTmp = track(path.join(dir, `_build-${board}.place-picks.tmp.json`))
    writeFileSync(picksTmp, readFileSync(cjAbs, "utf8"))
    await sh("bun", [path.join(dir, "pick-data.ts"), `${board}.tsx`, picksTmp], { cwd: dir, inherit: true })
    rmSync(picksTmp, { force: true })
  } catch {}
  console.error(`[${board}] placement preview: ${widthMm} × ${heightMm} mm (no traces/pours)`)
}

// Resolve declared 2nd-pass routes: pretty="<strategy>:<group>" on a <trace> means
// "route this by net identity with the pretty router." applyPrettyRoutes routes those
// groups in-process against a fresh obstacle field and returns a finished circuit-json
// (autoroutes + the computed copper spliced in) that we convert straight to gerbers —
// no throwaway .tsx, no second autoroute. So 2nd-pass routes regenerate from live
// geometry every build, never frozen into the source. No-op otherwise.
const exportCircuitJson = async (name: string) => {
  const out = `_build-${name}.cj.tmp.json`
  await sh(tsci, ["export", "-f", "circuit-json", "-o", out, `${name}.tsx`], { cwd: dir })
  const cj = JSON.parse(readFileSync(path.join(dir, out), "utf8"))
  rmSync(path.join(dir, out), { force: true }); rmSync(path.join(dir, `${name}.circuit.json`), { force: true })
  return cj
}
// Paint the placement preview first under the live watcher, then fall through to the
// full routed render below. build-all / manual stay single-pass, so the committed
// out/ artifacts are always trace-complete (never a placement-only view).
if (process.env.RENDER_SOURCE === "dev-server") {
  try {
    await placementPreview()
    console.log("RENDER_PHASE=placement") // the dev watcher broadcasts the preview on this line
  } catch (e: any) {
    console.error(`[${board}] placement preview failed — going straight to full render: ${e?.message || e}`)
  }
}

// The COMPLETE routed circuit-json: step 1 autoroutes the non-pretty nets, step 2 routes
// the pretty nets around them, spliced together. The autorouter does NOT run again — we
// convert this circuit-json straight to the fab set below (the whole 2-step point).
let circuit = await applyPrettyRoutes(dir, board, exportCircuitJson)
// The pour breps were baked at export time, before the pretty copper was spliced in — so
// they flood over every pretty trace + via (a short to the planes). Re-solve them against
// this finished circuit-json so each plane antipads the pretty copper it isn't on.
circuit = await resolvePours(circuit, dir, board)

// Generate the fabrication set (gerbers + drill + BOM + CPL) from that circuit-json with
// the standalone converters — the SAME ones tscircuit's CLI uses, but with no autorouter
// in the loop. Write into a scratch dir for compose + back-silk, then zip to out/.
console.log(`[${board}] generating gerbers from circuit-json (${circuit.length} elements, no 2nd autoroute)…`)
const scratch = track(mkdtempSync(path.join(tmpdir(), `pcb-${board}-`)))
try {
  const layers = stringifyGerberCommandLayers(convertSoupToGerberCommands(circuit, { flip_y_axis: false }))
  for (const [name, txt] of Object.entries(layers)) writeFileSync(path.join(scratch, `${name}.gbr`), txt as string)
  const pth = convertSoupToExcellonDrillCommands({ circuitJson: circuit, is_plated: true, flip_y_axis: false })
  if (pth.length) writeFileSync(path.join(scratch, "drill.drl"), stringifyExcellonDrill(pth))
  const npth = convertSoupToExcellonDrillCommands({ circuitJson: circuit, is_plated: false, flip_y_axis: false })
  if (npth.length) writeFileSync(path.join(scratch, "drill_npth.drl"), stringifyExcellonDrill(npth))
  writeFileSync(path.join(scratch, "bom.csv"), await convertBomRowsToCsv(await convertCircuitJsonToBomRows({ circuitJson: circuit })))
  writeFileSync(path.join(scratch, "pick_and_place.csv"), convertCircuitJsonToPickAndPlaceCsv(circuit))

  // Dedup drill (defensive — the converter already splits PTH/NPTH into separate files,
  // but keep the guard against a coincident plated+non-plated hole).
  try {
    const { removed, droppedTools } = dedupDrill(scratch)
    if (removed) console.log(`[${board}] drill dedup: removed ${removed} duplicate PTH holes (tools ${droppedTools.join(",")})`)
  } catch {
    console.error(`[${board}] drill dedup failed — fab zip may carry duplicate PTH/NPTH holes`)
  }

  // Back silk: the converter only draws the front legend. Build a throwaway board of
  // layer="bottom" copies of every front silk element (same engine -> identical font +
  // per-size stroke) and lift its B_SilkScreen, overwriting the front-only one here so the
  // bottom view + fab set carry a back legend that matches the front. (Still a tiny tsci
  // export — silk only, no routing.)
  const bsTsx = `_build-${board}.backsilk.tmp.tsx`
  const bsZipRel = path.join("out", `_build-${board}.backsilk.tmp.zip`)
  track(path.join(dir, bsTsx))
  track(path.join(dir, bsZipRel))
  try {
    writeFileSync(path.join(dir, bsTsx), backSilkBoardTsx(circuit))
    await sh(tsci, ["export", "-f", "gerbers", "-o", bsZipRel, bsTsx], { cwd: dir })
    const bsScratch = track(mkdtempSync(path.join(tmpdir(), `pcb-${board}-bsilk-`)))
    await sh("unzip", ["-o", "-q", path.join(dir, bsZipRel), "-d", bsScratch])
    writeFileSync(path.join(scratch, "B_SilkScreen.gbr"), readFileSync(path.join(bsScratch, "B_SilkScreen.gbr")))
  } catch {
    console.error(`[${board}] back-silk render failed — bottom view shows no back legend`)
  }

  // Zip the fab set into out/ (fresh — drop any prior zip first).
  rmSync(zip, { force: true })
  await sh("zip", ["-q", "-j", zip, ...readdirSync(scratch).map((f) => path.join(scratch, f))])

  const { top, bottom, overlay, inners, widthMm, heightMm } = await composeViews(scratch, scheme)
  // top/bottom/overlay always; plus one solo view per inner copper layer (4-layer+).
  const svgs: Record<string, string> = { top, bottom, overlay, ...inners }
  writeViews(svgs)
  const views = Object.keys(svgs)
  console.log(`[${board}] ${widthMm} × ${heightMm} mm — wrote ${board}.{${views.join(",")}}.{svg,png} (${schemeName})`)
  // Surface the assembly BOM + CPL as first-class out/ files: the JLCPCB part numbers and
  // placements, diffable per render. The wired count (parts carrying a JLCPCB #) is the
  // coverage signal as modules convert.
  try {
    const bom = readFileSync(path.join(scratch, "bom.csv"), "utf8")
    writeFileSync(path.join(outDir, `${board}.bom.csv`), bom)
    writeFileSync(path.join(outDir, `${board}.cpl.csv`), readFileSync(path.join(scratch, "pick_and_place.csv")))
    const rows = bom.trimEnd().split("\n").slice(1).filter(Boolean)
    const wired = rows.filter((r) => r.split(",").pop()?.trim()).length
    console.log(`[${board}] wrote ${board}.{bom,cpl}.csv — ${wired}/${rows.length} parts carry a JLCPCB #`)
  } catch {
    console.error(`[${board}] BOM/CPL generation failed`)
  }
} finally {
  rmSync(scratch, { recursive: true, force: true })
}

// Distill the board's pickable entities (pads + identity) next to the views so
// the web viewer's pad picker has semantic data in lockstep with the copper.
// Reuses the circuit-json already in memory (from the obstacle field or the
// combined export above). Write it to a temp file for pick-data.ts — it's a
// separate process, so we can't share the in-memory object. Best-effort.
if (circuit) {
  const picksTmp = `_build-${board}.picks-input.tmp.json`
  writeFileSync(path.join(dir, picksTmp), JSON.stringify(circuit))
  try {
    await sh("bun", [path.join(dir, "pick-data.ts"), `${board}.tsx`, picksTmp], { cwd: dir, inherit: true })
  } catch {
    console.error(`[${board}] pick-data failed — picks.json not refreshed (views still written)`)
  }
  rmSync(path.join(dir, picksTmp), { force: true })
}

lock.release()
