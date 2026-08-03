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
import { ledKnockoutGerber } from "./led-knockout"
import { innerRingGerber, assertInnerRinged } from "./inner-rings"

const spliceInnerRings = (circuit: any[], layers: Record<string, string>) => {
  for (const [ref, name] of [["inner1", "In1_Cu"], ["inner2", "In2_Cu"]] as const) {
    const frag = layers[name] ? innerRingGerber(circuit, layers[name]!, ref) : ""
    if (frag) layers[name] = layers[name]!.replace(/M02\*/, `${frag}\nM02*`)
  }
}
import { dedupDrill } from "./dedup-drill"
import { widenPourVoids, findPourClearanceRules, antennaKeepout, dropPourSlivers, widenFastenerAnnuli, findFastenerAnnuli } from "./pour-clearance"
import { singleflight } from "./run-lock"
import { convertSoupToGerberCommands, stringifyGerberCommandLayers, convertSoupToExcellonDrillCommands, stringifyExcellonDrill } from "circuit-json-to-gerber"
import { convertCircuitJsonToBomRows, convertBomRowsToCsv } from "circuit-json-to-bom-csv"
import { convertCircuitJsonToPickAndPlaceCsv } from "circuit-json-to-pnp-csv"
import { spawn, type ChildProcess } from "node:child_process"
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync, rmSync, utimesSync } from "node:fs"
import { tmpdir } from "node:os"
import path from "node:path"
import { Resvg } from "@resvg/resvg-js"

/**
 * Every plated via on this board is one full-stack through drill — JLCPCB standard assembly
 * drills no blind/buried holes (pcba.tsx says so at the top).
 *
 * A `routeInner` via declares the span it uses ELECTRICALLY — `top->inner1`, `top->inner2`,
 * `inner2->top` — while the drill converter emits only the holes whose span equals the one
 * asked for, and the caller asks for the default `top->bottom`. A via declaring anything
 * narrower is dropped from drill.drl while its pads stay on every copper layer: copper on
 * four layers with no barrel joining them, and a gerber set that looks complete.
 *
 * Restating each via's span as the drill it physically gets is what makes the two agree.
 * `assertFullyDrilled` is the floor under that — the drill file is the one fab artifact whose
 * omissions are invisible in every other view.
 */
const throughDrilled = (circuit: any[]) =>
  circuit.map((e) => (e.type === "pcb_via"
    ? { ...e, from_layer: "top", to_layer: "bottom", layers: ["top", "bottom"] }
    : e))

/**
 * Excellon hits, each pill/slot (`G85`) reduced to the centre its pad declares — a slot's
 * record carries the routed run's two endpoints, so its own coordinates sit half the travel
 * off the pad (the four USB-C shield ears land 0.3-0.4 mm out).
 */
type DrillHit = { x: number; y: number; d: number }
const drillHits = (drl: string): DrillHit[] => {
  const tool = new Map<string, number>()
  for (const m of drl.matchAll(/^T(\d+)C([\d.]+)/gm)) tool.set(m[1]!, Number(m[2]))
  const hits: DrillHit[] = []
  let d = 0, at: { x: number; y: number } | null = null
  const land = () => { if (at) hits.push({ ...at, d }); at = null }
  for (const raw of drl.split("\n")) {
    const line = raw.trim()
    let m: RegExpExecArray | null
    if ((m = /^T(\d+)$/.exec(line))) { land(); d = tool.get(m[1]!) ?? 0 }
    else if ((m = /^G85X(-?[\d.]+)Y(-?[\d.]+)/.exec(line)) && at) {
      hits.push({ x: (at.x + Number(m[1])) / 2, y: (at.y + Number(m[2])) / 2, d }); at = null
    } else if ((m = /^X(-?[\d.]+)Y(-?[\d.]+)/.exec(line))) { land(); at = { x: Number(m[1]), y: Number(m[2]) } }
  }
  land()
  return hits
}

/**
 * Every plated feature claims its own hit, matched on position and drilled diameter, and every
 * hit is claimed by a feature — the file drills nothing the board doesn't ask for. Two vias
 * stack at one coordinate on this board and take two hits.
 */
const assertFullyDrilled = (circuit: any[], drl: string, types: string[], file: string) => {
  const hits = drillHits(drl)
  const taken = hits.map(() => false)

  // refdes.pin for a pad; for a via, the connection it carries ("U1.IO21 to J8.SDA") — only the
  // five poured nets carry a source_net, so a signal via is named by its trace.
  const comp: Record<string, string> = {}, sPort: Record<string, any> = {}
  const pPort: Record<string, any> = {}, net: Record<string, string> = {}
  const pTrace: Record<string, any> = {}, sTrace: Record<string, any> = {}
  for (const e of circuit) {
    if (e.type === "source_component") comp[e.source_component_id] = e.name
    else if (e.type === "source_port") sPort[e.source_port_id] = e
    else if (e.type === "pcb_port") pPort[e.pcb_port_id] = e
    else if (e.type === "source_net") net[e.subcircuit_connectivity_map_key] = e.name
    else if (e.type === "pcb_trace") pTrace[e.pcb_trace_id] = e
    else if (e.type === "source_trace") sTrace[e.source_trace_id] = e
  }
  const label = (e: any) => {
    if (e.type === "pcb_via") {
      const on = sTrace[pTrace[e.pcb_trace_id]?.source_trace_id]?.display_name
        ?? net[e.subcircuit_connectivity_map_key]
      return on ? `via on ${on}` : "via"
    }
    const sp = sPort[pPort[e.pcb_port_id]?.source_port_id]
    return sp ? `${comp[sp.source_component_id] ?? "?"}.${sp.name ?? "?"}` : e.type.slice(4).replace(/_/g, " ")
  }
  const where = (e: any) => `${label(e)} @ (${e.x.toFixed(3)}, ${e.y.toFixed(3)})`

  const POS = 0.02, DIA = 0.01   // mm; coordinates round to µm, tool diameters carry ~2e-5 of slop
  const undrilled: string[] = [], wrongSize: string[] = []
  for (const e of circuit) {
    if (!types.includes(e.type)) continue
    const want = e.hole_diameter ?? Math.min(e.hole_width ?? Infinity, e.hole_height ?? Infinity)
    let exact = -1, near = -1
    for (let i = 0; i < hits.length; i++) {
      if (taken[i] || Math.abs(hits[i]!.x - e.x) > POS || Math.abs(hits[i]!.y - e.y) > POS) continue
      if (Math.abs(hits[i]!.d - want) <= DIA) { exact = i; break }
      if (near < 0) near = i
    }
    const best = exact >= 0 ? exact : near
    if (best < 0) { undrilled.push(where(e)); continue }
    taken[best] = true
    if (exact < 0) wrongSize.push(`${where(e)} wants ⌀${want.toFixed(3)}, drilled ⌀${hits[best]!.d.toFixed(3)}`)
  }
  const orphan = hits.filter((_, i) => !taken[i])
    .map((h) => `⌀${h.d.toFixed(3)} @ (${h.x.toFixed(3)}, ${h.y.toFixed(3)}) claimed by no ${types.join("/")}`)
  if (undrilled.length || wrongSize.length || orphan.length)
    throw new Error([
      `${file} does not cover the board — ${undrilled.length} undrilled, ${wrongSize.length} mis-sized, ${orphan.length} orphan:`,
      ...undrilled.map((s) => `    UNDRILLED   ${s}`),
      ...wrongSize.map((s) => `    WRONG SIZE  ${s}`),
      ...orphan.map((s) => `    ORPHAN HIT  ${s}`),
    ].join("\n"))
}

/**
 * JLCPCB's BOM importer folds any row with an empty Comment up into the row above
 * it — merging that part's designator into the previous line and discarding its own
 * JLCPCB #. The stock converter fills Comment only for resistors/capacitors (their
 * value), so every chip/module/connector lands blank and gets swallowed: the ESP32
 * (U1) disappeared into a 100 nF cap (C6), both bucks and a DRV8870 into their
 * neighbours, the 470 µF bulk (C3) into another cap. Give every row a non-empty,
 * ASCII Comment — keep the R/C value, else the part's MPN, else its JLCPCB # — and
 * fold the micro sign to "u" so JLCPCB's CSV decode can't mojibake "10µ".
 */
function fillBomComments(csv: string, circuit: any[]): string {
  const label = new Map<string, string>() // designator -> MPN, else JLCPCB #
  for (const e of circuit) {
    if (e.type !== "source_component" || !e.name) continue
    const id = e.manufacturer_part_number || e.supplier_part_numbers?.jlcpcb?.[0]
    if (id) label.set(e.name, id)
  }
  const ascii = (s: string) => s.replace(/µ/g, "u") // micro sign -> u
  const lines = csv.split("\n")
  const header = lines[0].split(",")
  const ci = header.indexOf("Comment")
  const vi = header.indexOf("Value")
  const pi = header.findIndex((h) => /JLCPCB Part/i.test(h))
  const out = [ascii(lines[0])]
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) { out.push(lines[i]); continue }
    const cols = lines[i].split(",")
    if (ci >= 0 && !cols[ci]?.trim()) {
      const fill = label.get(cols[0]?.trim()) || (pi >= 0 ? cols[pi]?.trim() : "") || cols[0]?.trim()
      cols[ci] = fill
      if (vi >= 0 && !cols[vi]?.trim()) cols[vi] = fill
    }
    out.push(ascii(cols.join(",")))
  }
  return out.join("\n")
}

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

// Temp files/dirs to remove on clean exit, tracked as they're created so cleanup
// needs no scope. Best-effort only — the dev watcher supersede-kills a render on the
// next save (by design, and often) and a kill skips this handler, so the authoritative
// cleanup is the start-of-render sweep below: it runs regardless of how the prior run died.
const temps = new Set<string>()
const track = (p: string) => (temps.add(p), p)
process.on("exit", () => { for (const p of temps) try { rmSync(p, { recursive: true, force: true }) } catch {} })

// Become the only running render for this board; if a newer run supersedes us it
// SIGTERMs us and our handler (in run-lock) kills the child below + exits.
let child: ChildProcess | null = null
const lock = singleflight(board, process.env.RENDER_SOURCE || "manual")
lock.setChildKiller(() => { try { child?.kill("SIGKILL") } catch {} })

// Sweep this board's build scratch left by a dead prior run. Every dir-scratch this
// script writes is _build-<board>.*-prefixed (the placement + back-silk boards, the
// circuit-json exports, the picks input) in dir/ and out/. We now hold the single-flight
// lock, so any leftover is a superseded run's orphan, not a live peer's — clear it before
// we write. The real artifacts (out/<board>.*) and any other-named scratch are untouched.
for (const base of [dir, outDir]) {
  let names: string[] = []
  try { names = readdirSync(base) } catch {}
  for (const f of names) if (f.startsWith("_build-")) try { rmSync(path.join(base, f), { recursive: true, force: true }) } catch {}
}

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
  // Drop every netlist trace + pour so the preview has nothing to route. `[^<]` (not `[\s\S]`)
  // keeps the match from spanning across real code: a doc comment or string that MENTIONS an open
  // `<trace from={…}>` (no `/>`) would otherwise let the non-greedy `*?` run to the next `/>`
  // anywhere below and swallow whatever sits between. Real trace/pour elements carry no `<` between
  // their tag and `/>`, so `[^<]*?` matches them exactly and stops a stray comment cold. Replace
  // with an empty fragment, not "", so a trace returned from an arrow — `.map((b) => (<trace/>))`
  // (logoRoutes) — collapses to `(<></>)` and stays valid instead of an empty `() => ()`.
  const placementSrc = readFileSync(boardFile, "utf8")
    .replace(/<trace\b[^<]*?\/>/g, "<></>")
    .replace(/<copperpour\b[^<]*?\/>/g, "<></>")
  const name = `_build-${board}.placement.tmp`
  track(path.join(dir, `${name}.tsx`))
  writeFileSync(path.join(dir, `${name}.tsx`), placementSrc)
  // Gerbers in-process from the circuit-json — the SAME standalone converter the full
  // render uses below, NOT `tsci export -f gerbers`. tsci's bundled gerber converter
  // throws on pill-shaped SMD pads ("Unsupported shape pill", e.g. the DRV8870 land
  // pattern), which would fail the export and skip the whole preview; circuit-json-to-gerber
  // handles them. Keeps the preview alive for any footprint the full render can gerber.
  const circuit = await exportCircuitJson(name)
  const scratch = track(mkdtempSync(path.join(tmpdir(), `pcb-${board}-place-`)))
  const layers = stringifyGerberCommandLayers(convertSoupToGerberCommands(circuit, { flip_y_axis: false }))
  spliceInnerRings(circuit, layers as Record<string, string>)
  if (layers["F_SilkScreen"]) layers["F_SilkScreen"] = layers["F_SilkScreen"].replace(/M02\*/, `${ledKnockoutGerber(circuit, layers["F_SilkScreen"])}\nM02*`)
  for (const [n, txt] of Object.entries(layers)) writeFileSync(path.join(scratch, `${n}.gbr`), txt as string)
  const pth = convertSoupToExcellonDrillCommands({ circuitJson: throughDrilled(circuit), is_plated: true, flip_y_axis: false })
  if (pth.length) writeFileSync(path.join(scratch, "drill.drl"), stringifyExcellonDrill(pth))
  const npth = convertSoupToExcellonDrillCommands({ circuitJson: circuit, is_plated: false, flip_y_axis: false })
  if (npth.length) writeFileSync(path.join(scratch, "drill_npth.drl"), stringifyExcellonDrill(npth))
  const { top, bottom, overlay, inners, topmask, bottommask, widthMm, heightMm } = await composeViews(scratch, scheme)
  const previewSvgs: Record<string, string> = { top, bottom, overlay, ...inners }
  if (topmask) previewSvgs.topmask = topmask
  if (bottommask) previewSvgs.bottommask = bottommask
  writeViews(previewSvgs)
  rmSync(scratch, { recursive: true, force: true })
  // Refresh picks from the placement circuit-json (pads only) so the pad picker
  // lands on the new positions during the preview, not the prior render's.
  try {
    const picksTmp = track(path.join(dir, `_build-${board}.place-picks.tmp.json`))
    writeFileSync(picksTmp, JSON.stringify(circuit))
    await sh("bun", [path.join(dir, "pick-data.ts"), `${board}.tsx`, picksTmp], { cwd: dir, inherit: true })
    rmSync(picksTmp, { force: true })
  } catch {}
  console.error(`[${board}] placement preview: ${widthMm} × ${heightMm} mm (no traces/pours)`)
}

// Export a board .tsx to circuit-json via tsci (one autoroute + pour pass). A <trace> with
// pcbComb="<orientation>" is routed natively by tscircuit as a fixed straight → 45° → straight
// comb in its manual-trace phase — before the autorouter — so it lands as real copper the rest
// of the board routes around and the pour clears. Nothing 2nd-pass happens here.
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

// The COMPLETE routed circuit-json in ONE render: tscircuit places every pcbComb trace as
// fixed copper before autorouting, routes the rest around it, and solves the pours against
// all of it. The post-export passes below only widen/clean pours the solver already cut.
const circuit = await exportCircuitJson(board)
const boardSrc = readFileSync(boardFile, "utf8")
const clr = widenPourVoids(circuit, findPourClearanceRules(boardSrc))
if (clr.added) console.log(`[${board}] pour-clearance: widened ${clr.added} antipad void(s) across ${Object.keys(clr.perPour).length} pour(s)`)
const ann = widenFastenerAnnuli(circuit, findFastenerAnnuli(boardSrc))
if (ann.added) console.log(`[${board}] fastener annuli: cleared ${ann.added} outer-layer pour region(s) under mounting hardware (${ann.pads.join(", ")})`)
const antN = antennaKeepout(circuit)
if (antN) console.log(`[${board}] antenna keepout: cleared the WROOM antenna box from ${antN} pour(s)`)
const slivN = dropPourSlivers(circuit)
if (slivN) console.log(`[${board}] pour slivers: dropped ${slivN} sub-min-feature floating fragment(s)`)

// Persist the routed circuit-json for the 3D assembly step. board-3d.py's ensure_circuit_json
// reuses out/<board>.circuit.json when it's newer than the board .tsx — so writing it here lets
// the dev-server's background GLB rebuild skip a second full autoroute pass and just read our
// already-routed board. It's a gitignored regenerable intermediate (never committed), and the
// watcher ignores out/, so this write neither bloats commits nor re-triggers a render.
writeFileSync(path.join(outDir, `${board}.circuit.json`), JSON.stringify(circuit))

// Generate the fabrication set (gerbers + drill + BOM + CPL) from that circuit-json with
// the standalone converters — the SAME ones tscircuit's CLI uses, but with no autorouter
// in the loop. Write into a scratch dir for compose + back-silk, then zip to out/.
console.log(`[${board}] generating gerbers from circuit-json (${circuit.length} elements, no 2nd autoroute)…`)
const scratch = track(mkdtempSync(path.join(tmpdir(), `pcb-${board}-`)))
try {
  const layers = stringifyGerberCommandLayers(convertSoupToGerberCommands(circuit, { flip_y_axis: false }))
  // Splice the inner-layer annular rings into the plane copper (the generator draws a plated
  // hole only on the layers it lists; see inner-rings.ts), then check they landed.
  spliceInnerRings(circuit, layers as Record<string, string>)
  assertInnerRinged(circuit, layers as Record<string, string>)
  // Splice the LED knockout badges into the front silk (filled D + text/pad antipads — not
  // expressible in circuit-json; see led-knockout.ts).
  if (layers["F_SilkScreen"]) layers["F_SilkScreen"] = layers["F_SilkScreen"].replace(/M02\*/, `${ledKnockoutGerber(circuit, layers["F_SilkScreen"])}\nM02*`)
  for (const [name, txt] of Object.entries(layers)) writeFileSync(path.join(scratch, `${name}.gbr`), txt as string)
  const pth = convertSoupToExcellonDrillCommands({ circuitJson: throughDrilled(circuit), is_plated: true, flip_y_axis: false })
  const pthTxt = stringifyExcellonDrill(pth)
  assertFullyDrilled(circuit, pthTxt, ["pcb_via", "pcb_plated_hole"], "drill.drl")
  if (pth.length) writeFileSync(path.join(scratch, "drill.drl"), pthTxt)
  const npth = convertSoupToExcellonDrillCommands({ circuitJson: circuit, is_plated: false, flip_y_axis: false })
  const npthTxt = stringifyExcellonDrill(npth)
  assertFullyDrilled(circuit, npthTxt, ["pcb_hole"], "drill_npth.drl")
  if (npth.length) writeFileSync(path.join(scratch, "drill_npth.drl"), npthTxt)
  const bomCsv = await convertBomRowsToCsv(await convertCircuitJsonToBomRows({ circuitJson: circuit }))
  writeFileSync(path.join(scratch, "bom.csv"), fillBomComments(bomCsv, circuit))
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

  // Canonicalize the fab-set instants before zipping: circuit-json-to-gerber stamps
  // every .gbr/.drl with a live `%TF.CreationDate,<now>*%` (plus a G04 / drill date
  // comment), which churns the zip's bytes on every render even when the copper is
  // identical — the composed SVG/PNG views never see it because they read geometry,
  // not comments. Pin the ISO instant to a fixed one, the same reason the CAD exports
  // pin their STEP timestamp to 1970. (Fixing it in the fork would not survive the
  // weekly upstream rebase; this repo owns the reproducibility.)
  const CANON_INSTANT = "1970-01-01T00:00:00.000Z"
  const isoInstant = /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z/g
  for (const f of readdirSync(scratch)) {
    if (!/\.(gbr|drl)$/.test(f)) continue
    const p = path.join(scratch, f)
    writeFileSync(p, readFileSync(p, "utf8").replace(isoInstant, CANON_INSTANT))
  }

  // Zip the fab set into out/ (fresh — drop any prior zip first). Deterministic:
  // sort the entries and stamp each with a canonical mtime, and pass -X to drop the
  // platform extra fields, so identical gerbers zip to identical bytes (mirrors the
  // STEP/PDF canonicalization the CAD exports do in _cadq_export.py). Without this the
  // archive's per-entry DOS timestamps and readdir order churn git on every render for
  // a non-change — the gerbers inside are already deterministic.
  rmSync(zip, { force: true })
  const zipMtime = new Date("1980-01-01T00:00:00Z")  // DOS-zip epoch floor (1970 underflows)
  const fabFiles = readdirSync(scratch).sort()
  for (const f of fabFiles) utimesSync(path.join(scratch, f), zipMtime, zipMtime)
  await sh("zip", ["-qXj", zip, ...fabFiles.map((f) => path.join(scratch, f))])

  const { top, bottom, overlay, inners, topmask, bottommask, widthMm, heightMm } = await composeViews(scratch, scheme)
  // top/bottom/overlay always; plus one solo view per inner copper layer (4-layer+) and a
  // solder-mask view per outer face (present whenever the fab set carries the mask gerbers).
  const svgs: Record<string, string> = { top, bottom, overlay, ...inners }
  if (topmask) svgs.topmask = topmask
  if (bottommask) svgs.bottommask = bottommask
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

// NB: the render intentionally does NOT rebuild the 3D assembly (out/<board>.glb + face
// textures) — CadQuery adds ~14 s and iteration must stay fast. The GLB therefore goes stale
// during a work session; it is brought current at COMMIT time by the pre-commit hook
// (.githooks/pre-commit), which rebuilds it only when it's behind the gerbers. Rebuild by hand
// anytime with `tools/cad-venv/bin/python board-3d.py` (the dev-server also rebuilds it in the
// background). See the README's Building section.

lock.release()
