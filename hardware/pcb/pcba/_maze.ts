/**
 * _maze.ts — the obstacle-aware second-pass router. Where clean-pass.ts's fan rule
 * needs an empty corridor, this threads a clean octilinear (H/V/45°) route through a
 * field of pads, traces, and vias — the "more intelligence" for congested cases.
 *
 *   bun _maze.ts
 *
 * It builds the obstacle field by exporting mini.tsx with the target nets' <trace>s
 * removed (so the autorouter places everything else as it will once these are
 * carved), rasterizes every other net's copper + every pad/via into a per-layer
 * occupancy grid with a clearance halo, then routes each target net with an
 * 8-direction A* (diagonals cost √2, corner-cutting forbidden, vias costed high so
 * they appear only when a layer change is genuinely needed). Each routed net joins
 * the obstacle field for the next. Output is <pcbtrace> JSX for mini.tsx; the core
 * carve patch drops these connections from the autorouter (the <trace> stays the
 * netlist). Edit SPEC for a different case.
 */
import { execFileSync } from "node:child_process"
import { readFileSync, writeFileSync, rmSync } from "node:fs"
import { mazeRouteNets, routedNetToJSX } from "./pretty-router"

// ── CASES: named connection groups to maze-route. Select with `bun _maze.ts <case>`.
// pairs are routed in order (hardest first helps). region is the routing window (mm).
const COMMON = { board: "pcba", cell: 0.1, clr: 0.25, width: 0.2, viaCost: 60, startLayer: "top", turn: 12 }
const CASES: Record<string, any> = {
  // J6 reeds past the U2 I2C header (committed)
  j6: {
    ...COMMON,
    pairs: [
      { from: "J6.RA1", to: "U2B.GPB0" }, { from: "J6.RA2", to: "U2B.GPB1" },
      { from: "J6.RA3", to: "U2B.GPB2" }, { from: "J6.RA4", to: "U2B.GPB3" },
    ],
    region: { x0: 2, x1: 21, y0: 20, y1: 44 },
  },
  // J5 driver -> ESP. 3 signals reach the FAR U1A row (route the long ones first),
  // 5 reach the near U1B row. Window spans the whole ESP height.
  j5: {
    ...COMMON,
    pairs: [
      { from: "J5.IO27", to: "U1A.IO27" }, { from: "J5.IO26", to: "U1A.IO26" }, { from: "J5.IO25", to: "U1A.IO25" },
      { from: "J5.IO16", to: "U1B.IO16" }, { from: "J5.IO17", to: "U1B.IO17" }, { from: "J5.IO5", to: "U1B.IO5" },
      { from: "J5.IO18", to: "U1B.IO18" }, { from: "J5.IO19", to: "U1B.IO19" },
    ],
    region: { x0: -42, x1: -13, y0: -47, y1: 14 },
  },
  // I2C bus: two 4-pin nets routed as their declared tree segments. The MCP<->MCP
  // backbone (U2I<->U3I) falls out as a clean vertical pair; the ESP feeds the
  // backbone bottom (U3I) and taps the RTC (U6I). Segments meet at the shared pads.
  i2c: {
    ...COMMON,
    pairs: [
      { from: "U2I.SDA", to: "U3I.SDA" }, { from: "U2I.SCL", to: "U3I.SCL" },
      { from: "U1B.IO21", to: "U3I.SDA" }, { from: "U1B.IO22", to: "U3I.SCL" },
      { from: "U1B.IO21", to: "U6I.SDA" }, { from: "U1B.IO22", to: "U6I.SCL" },
    ],
    region: { x0: -24, x1: 18, y0: -35, y1: 38 },
  },
  // ESP IO4 -> buzzer U8. IO4 is the rightmost ESP top-row pin; U8 sits down-left.
  // The route drops below the ESP pin row (y=-13.7) and threads the clear corridor
  // above the U8 pins (y=-20.5), dodging U8.VCC, to land on U8.IO.
  io4u8: {
    ...COMMON, clr: 0.45, // hugs the dense ESP pin row — hold the full board clearance
    pairs: [{ from: "U8.IO", to: "U1B.IO4" }],
    region: { x0: -58, x1: -36, y0: -26, y1: -10 },
  },
  // FAUCET UART + RS485 UART off the ESP far row (U1A). 4 signals fan up-left out
  // of the dense top ESP row: IO33/IO35 climb to the FAUCET connector on the top
  // edge, IO32/IO34 reach the RS485 TTL header on the far left. The transceiver's
  // TXD (upper pad) -> IO34 (right) and RXD (lower pad) -> IO32 (left) nest without
  // a crossing, so the pair routes cleanly without the old bottom-layer split.
  faucet485: {
    ...COMMON,
    pairs: [
      { from: "J3.IO33", to: "U1A.IO33" }, { from: "J3.IO35", to: "U1A.IO35" },
      { from: "U7T.TXD", to: "U1A.IO34" }, { from: "U7T.RXD", to: "U1A.IO32" },
    ],
    region: { x0: -52, x1: -12, y0: 9, y1: 45 },
  },
  // GAS divider network: J11.AOUT/DOUT -> R1/R3 -> midpoints -> R2/R4 (GND legs stay
  // on the plane) and the two midpoint taps drop ~30mm straight down to the ESP ADC
  // pins IO39/IO36. The taps are the nesty runs; DOUT must also reach R3 past R1/R2.
  divider: {
    ...COMMON,
    pairs: [
      { from: "R1.pin2", to: "U1A.IO39" }, { from: "R3.pin2", to: "U1A.IO36" },
      { from: "J11.AOUT", to: "R1.pin1" }, { from: "J11.DOUT", to: "R3.pin1" },
      { from: "R1.pin2", to: "R2.pin1" }, { from: "R3.pin2", to: "R4.pin1" },
    ],
    region: { x0: -27, x1: -7, y0: 9, y1: 46 },
  },
}
const SPEC = CASES[process.argv[2] || "j6"]
if (!SPEC) { console.error(`unknown case "${process.argv[2]}" — have: ${Object.keys(CASES).join(", ")}`); process.exit(1) }

// ── export the obstacle board: mini.tsx with the SPEC nets' <trace>s removed ──
const src = readFileSync(`${SPEC.board}.tsx`, "utf8")
let stripped = src
for (const { from, to } of SPEC.pairs) {
  const fa = from.replace(".", " > ."), ta = to.replace(".", " > .")
  const re = new RegExp(`\\s*<trace from="\\.${fa.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}" to="\\.${ta.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}" />`, "g")
  stripped = stripped.replace(re, "")
}
const tmpTsx = `._maze_obstacles.tsx`, tmpJson = `._maze_obstacles.json`
writeFileSync(tmpTsx, stripped)
execFileSync("node_modules/.bin/tsci", ["export", "-f", "circuit-json", "-o", tmpJson, tmpTsx], { stdio: ["ignore", "ignore", "pipe"] })
const c = JSON.parse(readFileSync(tmpJson, "utf8")) as any[]
rmSync(tmpTsx, { force: true }); rmSync(tmpJson, { force: true })
rmSync(`.${tmpTsx.slice(1).replace(/\.tsx$/, "")}.circuit.json`, { force: true })

// Route the SPEC's nets against the obstacle circuit-json and print <pcbtrace> JSX.
// The routing core lives in pretty-router.ts so the same code runs as a build stage.
for (const rn of mazeRouteNets(c, SPEC.pairs, SPEC)) console.log(routedNetToJSX(rn))
