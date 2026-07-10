/**
 * esp32-mcp-mini — the controller carrier. Off-the-shelf modules plug into
 * 2.54 mm header sockets; the board is the interconnect, and every off-board
 * interface lands on a labeled edge connector (J1-J11). Footprint geometry
 * lives in ./parts (the part wrappers) and ./routing (hand-routing geometry); placement + routing
 * are declared here.
 *
 * The ESP32 sits at the far-left, antenna off-board. Its usable GPIO are nearly all on the
 * north and south castellations (the east edge is flash + the lone GPIO IO13), so every
 * off-board signal fans up or down and its connector lives on that edge, ordered to match the
 * pin run. NORTH / top: RELAYS (J5) at the edge, the USB-C programming block (J14 + the CH340
 * bridge, above the WROOM) at the top-left, and — combed up from the north
 * pins as one parallel bus — the two pump drivers (U11/U12) feeding PUMPS. SOUTH / bottom: an
 * edge row of cable connectors — GAS (J11), SCREEN (J9), FAUCET (J3), SENSORS (J4) — with their
 * on-board conditioning in a second row just above (the R1-R4 gas dividers, the U7 RS485
 * transceiver). The buzzer (U8/Q1/R5) sits east of the ESP by its IO13 pin. Center: DS3231 +
 * coin cell; the two MCPs stacked through the middle (0x20 north, 0x21 south) with their reed
 * inputs on REEDS A (above) / REEDS B (below). Right block: the two ULNs with the valve
 * manifolds immediately to their right and the V12 bulk/HF decoupling between them; the 3V3
 * LDO / 5V buck (U9 top, U10 bottom) and the 12V inlet (J10) frame the right column.
 *
 * SIX layers, stackup top->bottom:
 *   L1 top    — signals + the V12 island
 *   L2 inner1 — 3V3 plane (full flood)
 *   L3 inner2 — 5V plane (full flood)
 *   L4 inner3 — SDA plane (full flood)
 *   L5 inner4 — SCL plane (full flood)
 *   L6 bottom — GND plane (full flood)
 * 3V3/5V/SDA/SCL/GND are full-flood planes: each pin commons to its plane at the barrel
 * (through-hole) or an auto-stitched via (SMD). V12 is a top-copper island over the valve/
 * buck/driver block (the rectangle at the pours): top-layer 12V pads sit on it directly,
 * through-hole 12V pins pick it up at the barrel. Point-to-point signals route on ALL six
 * layers: `autorouter.viaMode="through-hole"` (below) tells the homesodamachine capacity-autorouter
 * fork to use the inner copper but make a mesh node via-capable only where the full board column
 * is clear, and emit those vias top<->bottom (JLCPCB drills through-holes only, no blind/buried —
 * see patches/capacity-autorouter-fork/). Each poured plane carves clearance around the inner-layer
 * signals crossing it and every via is a manufacturable through-hole; the DRC (clearance.ts)
 * proves no blind/buried via and no barrel crossing foreign copper survives. `viaInPad` (below)
 * then pulls each route's terminal transition via back onto its pad wherever the barrel column and
 * the replacement segment clear all foreign copper — via-in-pad, so order filled+capped vias.
 * `viaRingKeepout={false}` (below) drops the mesh-level via-ring carve: through-hole via-capability
 * still requires a clear full-stack column, but pad-adjacent full-stack mesh nodes are no longer
 * shattered per-layer to reserve the via annular ring. That carve ~doubled the mesh (8842 vs 4237
 * nodes here) and the autoroute (~93 -> ~26 s) without binding — the DRC (clearance.ts) already
 * proves via-ring-to-pad clearance holds (floor 0.155, 0 errors), so it enforces the ring instead.
 *
 * `schematicDisabled` on the board: this is a fab-only PCB (its canonical "schematic" is
 * esp32-pinout.mmd). tscircuit's schematic-trace-solver — NOT the PCB autorouter — hangs on
 * this dense layout whenever a net is added; the capacity-autorouter handles the PCB fine.
 * Disabling the schematic removes the hang and speeds every render; the gerbers are unaffected.
 *
 * `autorouter.traceClearance` (the homesodamachine core patch feeds it to the capacity
 * solver's obstacle margin) is the packing target, and its realized floor is counter-
 * intuitive AND non-monotonic: too HIGH and the router can't meet it in the dense fan-outs,
 * crams the leftover space, and the realized min copper gap COLLAPSES. On this placement the
 * realized floor peaks sharply at traceClearance 0.13 (0.129 mm); 0.12 -> 0.120, 0.14 -> 0.119,
 * 0.15 -> 0.111. Keep it in the ~0.12–0.14 low zone at the peak, don't raise it toward 0.25+.
 * That 0.129 floor is a trace hugging the WROOM 3V3-decoupling fan-out (C10, off U1's ~38-pin
 * west castellation comb) — traceClearance won't beat it, only spreading that comb will (all six
 * layers already carry signal). The web viewer's board chip reports this floor live
 * (clearance.ts -> picks.json).
 */
import { at, Cap, Res, Jst, jstPins, ulnOUT, Uln2803, Mcp23017, Ds3231Smd, Cos13487, Sm712, Buck5, Buzzer, CoinHolder, BulkCap, Npn, Esp32, Ams1117, Ch340, Usblc6, UsbC, Drv8870, Tact } from "./parts"
import { KF301_5_0_2P } from "./imports/KF301_5_0_2P"
import { frame, route, routeBottom, channel } from "./routing"
import { boardVersionParts } from "./board-version"
import { logoRoutes } from "./logo"
import { KT_0603R as LedRed } from "./imports/KT_0603R"
import { KT_0603G as LedGrn } from "./imports/KT_0603G"
import { Blue_light_0603 as LedBlu } from "./imports/Blue_light_0603"
import type { DecouplingRule } from "./cap-audit"
import type { AmpacityRule } from "./ampacity-audit"

// Identity stamp version (commit date + short SHA), computed once per render.
const ID = boardVersionParts()

// Hand-routing geometry (frame / pcbPath helpers) lives in ./routing.

// Each framed part is placed here as an element carrying literal x/y on the tag (the drag editor needs
// a numeric x={…}/y={…} on the component's own line — web/lib/pcb-editor-routes.js parses/rewrites it),
// then rendered below via {U14El}/… `frame(el)` derives centre, rotation, AND pad geometry from that one
// element, so a drag moves the part and its routing follows — nothing to keep in sync by hand.
const U14El = <Usblc6 name="U14" x={-56.25} y={16} rot={270} />
const C22El = <Cap name="C22" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-56.25} y={19.5} rot={0} side="N" />
const J14El = <UsbC name="J14" x={-62} y={16.5} rot={270} />
const U13El = <Ch340 name="U13" x={-49.25} y={26} rot={0} />
const R16El = <Res name="R16" resistance="5.1k" footprint="0603" jlcpcb="C23186" x={-56.75} y={13} rot={0} side="N" />
const R15El = <Res name="R15" resistance="5.1k" footprint="0603" jlcpcb="C23186" x={-56.75} y={21.75} rot={0} side="N" />
const U14f = frame(U14El)
const J14f = frame(J14El)
const C22f = frame(C22El)
const R16f = frame(R16El)
const R15f = frame(R15El)
const U13f = frame(U13El)
const dMinusLane = U14f.row("pin3", -0.85)

// ── Auto-reset lattice ────────────────────────────────────────────────────────────────
// Cross-coupled NPN pair north of U13 (Q2 drives EN, Q3 drives IO0). rot90 aims each collector
// SOUTH, toward its U1 load; base resistors sit directly north of each base. DTR/RTS drive the pair
// from U13's east edge. Collector reaches (EN, IO0) are long traces out to U1 — deferred until their
// corridors are known.
const Q2El = <Npn name="Q2" x={-65.5} y={24.75} rot={90} />
const Q3El = <Npn name="Q3" x={-61.5} y={24.75} rot={90} />
const R17El = <Res name="R17" resistance="10k" footprint="0603" jlcpcb="C25804" x={-64.5} y={28.75} rot={90} side="N" />
const R18El = <Res name="R18" resistance="10k" footprint="0603" jlcpcb="C25804" x={-60.5} y={28.75} rot={90} side="N" />
// BOOT override tact (IO0 branch). rot180 seats pin1 (signal) on the SE corner so it exits south,
// clear of U13, down to IO0; pin4 (NW) is the diagonal contact to GND. SW2 (RESET/EN) stays inline.
const SW1El = <Tact name="SW1" x={-47.5} y={33.5} rot={180} />

// ── Buzzer chain (IO13 → R5 → Q1 → U8) ────────────────────────────────────────────────
const R5El = <Res name="R5" resistance="1k" footprint="0603" jlcpcb="C21190" x={-45.228} y={-4.445} rot={180} side="N" />
const Q1El = <Npn name="Q1" x={-41.45} y={-5.395} rot={180} />
const U8El = <Buzzer name="U8" x={-37.9} y={-10.72} />
const R5f = frame(R5El), Q1f = frame(Q1El), U8f = frame(U8El)
const Q2f = frame(Q2El), Q3f = frame(Q3El), R17f = frame(R17El), R18f = frame(R18El)
const SW1f = frame(SW1El)

// ── GAS/EN divider grid (pcbPath hand-routing) ───────────────────────────────────────
// Six 0603s (AOUT divider R1/R2, DOUT divider R3/R4, EN network R7/C12) as vertical (rot90) parts in
// 3 columns ordered EN·DOUT·AOUT west→east to match U1's tap pins (EN -63.75 · IO36 -62.48 · IO39
// -61.21), so each divider's midpoint taps straight up in order — no crossings. Each column is a
// pair: input/pullup south (toward J11), GND/V3V3 north; the midpoint jogs east past the top part up
// to U1. Column pitch 2.0 (rot90 courtyard ~1.8 wide — the middle tap needs the 0.2 mm lane, so this
// is the floor); row pitch 3.5 (courtyard ~3.3 tall). Grid pulled north to the U1 courtyard so J11
// can follow it up. One const per axis → one-line move; frames + placements read the same const.
const CX_EN = -65.5, CX_DOUT = -63.5, CX_AOUT = -61.5   // columns W→E
const CY_BOT = -15.8, CY_TOP = -12.3                    // input (south) / GND·V3V3 (north) rows (N clears U1 courtyard -10.05)
// Placed here (not down in the return) so each frame derives from its own element; rendered below
// via {R1El}… The grid parts ride the CX/CY consts, so a one-line const move still slides the lattice.
const R1El = <Res name="R1" resistance="2.2k" footprint="0603" jlcpcb="C4190" x={CX_AOUT} y={CY_BOT} rot={90} side="N" />   // AOUT in (pin1 S) → midpoint (pin2 N)
const R2El = <Res name="R2" resistance="3.3k" footprint="0603" jlcpcb="C22978" x={CX_AOUT} y={CY_TOP} rot={90} side="N" />  // midpoint (pin1 S) → GND (pin2 N)
const R3El = <Res name="R3" resistance="2.2k" footprint="0603" jlcpcb="C4190" x={CX_DOUT} y={CY_BOT} rot={90} side="N" />   // DOUT in (pin1 S) → midpoint (pin2 N)
const R4El = <Res name="R4" resistance="3.3k" footprint="0603" jlcpcb="C22978" x={CX_DOUT} y={CY_TOP} rot={90} side="N" />  // midpoint (pin1 S) → GND (pin2 N)
const R7El = <Res name="R7" resistance="10k" footprint="0603" jlcpcb="C25804" x={CX_EN} y={CY_BOT} rot={270} side="N" />    // EN node (pin1 N) → V3V3 (pin2 S)
const C12El = <Cap name="C12" capacitance="1uF" footprint="0603" jlcpcb="C15849" x={CX_EN} y={CY_TOP} rot={90} side="N" />  // EN node (pin1 S) → GND (pin2 N); near U1.EN
const R1f = frame(R1El), R2f = frame(R2El), R3f = frame(R3El), R4f = frame(R4El), R7f = frame(R7El), C12f = frame(C12El)
const U1El = <Esp32 name="U1" x={-57} y={0} rot={0} />
const U1f = frame(U1El)                               // ESP32; taps by label (EN/IO36/IO39)
const J11El = <Jst name="J11" x={-62} y={-24.3} count={4} labels={["GND", "V5", "DOUT", "AOUT"]} label="GAS" rot={90} />
const J11f = frame("J11", J11El.props.x, J11El.props.y, 0, Object.fromEntries(jstPins(J11El.props).pins))
// SENSORS connector + its 1-wire pull-up (R9), framed for the R9→IO26 tap below.
const R9El = <Res name="R9" resistance="4.7k" footprint="0603" jlcpcb="C23162" x={-34.25} y={-28.25} rot={0} side="N" />
const R9f = frame(R9El)
const J4El = <Jst name="J4" x={-36.25} y={-33} count={6} labels={["3V3", "GND", "V5", "IO25", "IO26", "IO27"]} label="SENSORS" rot={180} />
const J4f = frame("J4", J4El.props.x, J4El.props.y, 0, Object.fromEntries(jstPins(J4El.props).pins))
const J5El = <Jst name="J5" x={-36.5} y={31} count={4} labels={["GND", "V5", "IO23", "IO19"]} label="RELAYS" rot={0} />
const J5f = frame("J5", J5El.props.x, J5El.props.y, 0, Object.fromEntries(jstPins(J5El.props).pins))
// Pump H-bridges, framed for the IN-bus routing below.
const U11El = <Drv8870 name="U11" x={-28.25} y={22.5} rot={0} />
const U12El = <Drv8870 name="U12" x={-21.25} y={22.5} rot={0} />
const U11f = frame(U11El), U12f = frame(U12El)

// ── Decoupling audit ────────────────────────────────────────────────────────────────────
// The single source of truth for which support cap serves which part, its role, and its job
// class (`kind`). The web viewer's Board-checks panel reads this table (pick-data.ts →
// cap-audit.ts) and measures each cap's real pad-to-pad gap to its target from the placed
// geometry, flagging any past the budget its `kind` implies. Intent only — NO coordinates here,
// so it re-measures every render and can never fall out of sync with a move. `kind` sets the
// distance budget by job (cap-audit.ts BUDGETS): `hf` 0.1uF ceramics hug their chip tightest,
// `bulk` 10/22uF reservoirs get more room, `rc` is a timing node, `reservoir` is the one central
// 470uF electrolytic (loosest, it feeds the whole valve block). See each placement comment below.
export const decoupling: DecouplingRule[] = [
  { cap: "C13", near: "U9", role: "AMS1117 V5 input", kind: "bulk" },
  { cap: "C14", near: "U9", role: "AMS1117 3V3 output", kind: "bulk" },
  { cap: "C15", near: "U10", role: "K7805 buck input", kind: "bulk" },
  { cap: "C16", near: "U10", role: "K7805 buck output", kind: "bulk" },
  { cap: "C17", near: "U11", role: "DRV8870 VM bulk", kind: "bulk" },
  { cap: "C18", near: "U11", role: "DRV8870 VM HF", kind: "hf" },
  { cap: "C19", near: "U12", role: "DRV8870 VM bulk", kind: "bulk" },
  { cap: "C20", near: "U12", role: "DRV8870 VM HF", kind: "hf" },
  { cap: "C10", near: "U1", role: "WROOM 3V3 HF", kind: "hf" },
  { cap: "C11", near: "U1", role: "WROOM 3V3 bulk", kind: "bulk" },
  { cap: "C12", near: "U1", role: "EN power-on RC", kind: "rc" },
  { cap: "C6", near: "U6", role: "DS3231 VCC", kind: "hf" },
  { cap: "C7", near: "U7", role: "COS13487 VCC", kind: "hf" },
  { cap: "C4", near: "U2", role: "MCP 0x20 VDD", kind: "hf" },
  { cap: "C5", near: "U3", role: "MCP 0x21 VDD", kind: "hf" },
  { cap: "C21", near: "U13", role: "CH340C 3V3", kind: "hf" },
  { cap: "C22", near: "U14", role: "USBLC6 VBUS", kind: "hf" },
  { cap: "C1", near: "U5", role: "V12 island HF (ULN B)", kind: "hf" },
  { cap: "C2", near: "U4", role: "V12 island HF (ULN A)", kind: "hf" },
  { cap: "C3", near: "U4", role: "V12 470uF bulk reservoir", kind: "reservoir" },
]

// ── Ampacity audit ──────────────────────────────────────────────────────────────────────
// Current-carrying SIGNAL traces and the min width they want (cap-audit's sibling — ampacity-
// audit.ts checks the routed width against this). Each such trace carries an explicit `thickness`
// below so the router lays it wide instead of the 0.2mm floor it gives every logic line. The power
// RAILS need no entry: V12/V5/GND are poured planes picked up at the barrel. What does:
//   pump motors (U11/U12.OUT → J13) — ~0.8A peak (Kamoer KPHM400-SW). Routed 0.4mm, want ≥0.3mm
//     (IPC-2221 rule of thumb for ~0.8A at ~10°C rise on 1oz; more on inner 0.5oz — kept short).
//   manifold valves + condenser fan (U4/U5.OUT → J1/J2) — sunk by the ULN2803, so ≤0.5A/channel.
//     Routed 0.3mm, want ≥0.25mm.
// `pin` is an endpoint-pin prefix (U11.OUT matches U11.OUT1/OUT2, etc.). Rules of thumb, not a
// thermal model — enough to catch a fat path left on the 0.2mm floor.
export const ampacity: AmpacityRule[] = [
  { pin: "U11.OUT", minWidthMm: 0.3, role: "pump A motor (~0.8A)" },
  { pin: "U12.OUT", minWidthMm: 0.3, role: "pump B motor (~0.8A)" },
  { pin: "U4.OUT", minWidthMm: 0.25, role: "MANIFOLD A valves (ULN, ≤0.5A)" },
  { pin: "U5.OUT", minWidthMm: 0.25, role: "MANIFOLD B valves + fan (ULN, ≤0.5A)" },
]

export default () => (
  <board layers={6} schematicDisabled outline={[{ x: -68, y: -39 }, { x: 27, y: -39 }, { x: 27, y: 37 }, { x: -68, y: 37 }]} minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" pcbStyle={{ silkscreenFontSize: "0.8mm" }} autorouter={{ traceClearance: 0.15, viaMode: "through-hole", viaInPad: true, viaRingKeepout: false }}>
    {/* DS3231SN RTC + CR2032 backup, east of the ESP. U6 (the SOIC) sits high with its
        0.1uF decoupler (C6) to its west and the buzzer column below it; the 20 mm THT coin
        base (BT1) is the bulk to U6's east. + is pin1 (the silk-marked post -> VBAT), - is
        pin2 (-> GND); the cell is retained by the molded base, not SMT clips. */}
    <CoinHolder name="BT1" x={-20.5} y={-1.25} />
    <Ds3231Smd name="U6" x={-40.5} y={2.5} rot={270} />
    <Cap name="C6" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-37.2} y={-4.75} rot={0} />
    {/* Base controller — bare ESP32-WROOM-32E (U1, C701341), no radio, antenna keepout
        pointing west off the board edge. Usable GPIO sit on the north and south
        castellations only (the east edge is the module's flash); the relay/pump/buzzer/
        I2C/prog lines land on the north edge, the UART/ADC/sensor lines on the south (pin
        map in esp32-scope.md). 3V3 is the only supply pin (no V5): it draws from the 3V3
        plane (sourced by the AMS1117 LDO off the 5V rail), every GND pad (incl. the centre thermal pad)
        auto-stitches to the bottom plane. Decoupling (C10 0.1uF + C11 10uF bulk) and the EN
        power-on RC (R7 10k pull-up + C12 1uF) sit at the south edge by the 3V3/EN pins; R8
        (10k) pulls IO0 up; the WROOM is flashed over the USB-C programming block above it
        (CH340 bridge on TX0/RX0, auto-reset on EN/IO0) — see that block below. */}
    {U1El}
    {/* WROOM support south of U1: the EN power-on RC (R7 + C12) stacked at the far-west,
        hard by U1's EN pin so the EN trace stays short; the supply decouplers C10 + C11
        share the lane just east of them. */}
    {C12El}
    {R7El}
    <Cap name="C10" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-56.5} y={-14} rot={180} side="N" />
    <Cap name="C11" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-56.5} y={-17} rot={0} side="N" />
    <Res name="R8" resistance="10k" footprint="0603" jlcpcb="C25804" x={-58.25} y={28.75} rot={270} side="N" />
    {/* RS-485 to the front display (J9). COS13487EESA-3.3 auto-direction transceiver (U7):
        no host DE/RE — /RE tied low (always receive), /SHDN tied high (always on),
        only DI (from ESP TX) and RO (to ESP RX) are driven. R6 = 120R line termination
        across A/B; D1 = SM712 ESD array at the J9 cable entry; C7 decouples VCC. */}
    <Cos13487 name="U7" x={-19} y={-23} rot={180} />
    <Res name="R6" resistance="120" footprint="0603" jlcpcb="C22787" x={-19} y={-28} rot={0} side="N" />
    <Sm712 name="D1" x={-24.5} y={-27.5} rot={180} />
    <Cap name="C7" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-18.5} y={-17.75} rot={0} side="N" />
    {/* On-board supplies. U10 = K7805 (12V->5V, 2A) SIP module (pin1 Vin / pin2 GND / pin3
        +Vo), 10uF input + 22uF output cap. U9 = AMS1117-3.3 (C6186, SOT-223 LDO) makes 3V3
        from the 5V rail: VIN off V5, VOUT1 + VOUT2 (tab) to 3V3, GND to the bottom plane;
        the SMD pads auto-stitch to their planes. Each cap flanks the LDO at the pin of its
        own net: C13 (10uF V5 input) hard by VIN on the east, C14 (22uF 3V3 output) under the
        VOUT tab on the west — so each closes a tight local loop like C15/C16 flank U10. */}
    <Ams1117 name="U9" x={7} y={21.25} rot={0} />
    <Cap name="C13" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={14.5} y={21} rot={0} side="N" />
    <Cap name="C14" capacitance="22uF" footprint="0805" jlcpcb="C45783" x={14.5} y={24} rot={0} side="N" />
    <Buck5 name="U10" x={15.25} y={-25} />
    <Cap name="C15" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={23} y={-27} rot={90} side="E" />
    <Cap name="C16" capacitance="22uF" footprint="0805" jlcpcb="C45783" x={23} y={-22} rot={270} side="E" />
    {/* Pump drivers, in the second row behind the top-edge connectors: one DRV8870 H-bridge per peristaltic flavor
        pump (Kamoer KPHM400-SW, 12V brushed DC, 0.8A at full speed per the datasheet — PWM'd well below that at the
        1:20 dispense ratio; prime/clean is where it hits 0.8A), 45V/3.6A SMD with internal freewheeling +
        OCP/OTP/UVLO. VM->12V (the top SMD pad lands directly on the V12 island), GND/PAD->GND,
        ISEN->GND, VREF->3V3, OUT1/OUT2 to PUMPS. 10uF + 0.1uF VM decoupling per chip.
        DRIVE: the dosing pumps run ONE direction (dispense — peristaltic tubing occlusion stops
        backflow, no reverse-purge), so this is single-direction fast-decay drive: IN2 tied to GND,
        only IN1 PWM'd from the ESP. That halves the IN bus to one trace per pump and frees IO16/IO18.
        (Reversible: re-add IN2->IO16/IO18 if a reverse/anti-drip mode is ever wanted.) */}
    {U11El}
    <Cap name="C17" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-29.75} y={14.75} rot={90} side="E" />
    <Cap name="C18" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-26.5} y={14.75} rot={90} side="E" />
    {U12El}
    <Cap name="C19" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-22.75} y={14.75} rot={90} side="E" />
    <Cap name="C20" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-19.5} y={14.75} rot={90} side="E" />
    <Mcp23017 name="U2" x={-8} y={20.25} addr="0x20" rot={180} />
    <Mcp23017 name="U3" x={-1.75} y={-21.75} addr="0x21" rot={0} />
    <Uln2803 name="U4" x={9.25} y={9.5} rot={270} />
    <Uln2803 name="U5" x={9.5} y={-9} rot={270} />
    {U8El}
    {Q1El}
    {R5El}
    {/* Manifolds sit immediately right of their ULNs so OUT1-8/COM are straight shots
        across (J1 pin order = ULN output pin order, reversed). */}
    <Jst name="J1" x={21} y={13.75} count={9} labels={[...ulnOUT].reverse()} label="MANIFOLD A" rot={270} />
    <Jst name="J2" x={21} y={-9.5} count={6} labels={["COM", "FAN", "OUT4", "OUT3", "OUT2", "OUT1"]} label="MANIFOLD B" rot={270} />
    {/* Pump-motor outputs — one PUMPS connector. Pin order is AM2/AM1/BM2/BM1, left to
        right, matching the drivers' OUT pads west-to-east (U11 then U12) so each pair
        combs straight up to its own side of J13 with no crossing. */}
    <Jst name="J13" x={-22.25} y={31} count={4} labels={["AM2", "AM1", "BM2", "BM1"]} label="PUMPS" rot={0} />
    <Jst name="J3" x={-52.25} y={-33} count={4} labels={["GND", "V5", "IO35", "IO33"]} label="FAUCET" rot={180} />
    {J4El}
    {/* RELAYS — logic-level control out to the two external opto-isolated relay modules
        (compressor AC switch + carbonator diaphragm-pump 12V gate, both off-board). IO23/
        IO19 drive them; V5 feeds the relay modules' coil/opto supply; GND returns. */}
    {J5El}
    <Jst name="J6" x={-7.0} y={31} count={5} labels={["GND", "RA4", "RA3", "RA2", "RA1"]} label="REEDS A" rot={0} />
    <Jst name="J7" x={-3.0} y={-33} count={7} labels={["RB1", "RB2", "RB3", "RB4", "CLO", "CHI", "GND"]} label="REEDS B" rot={180} />
    <Jst name="J8" x={8.5} y={31} count={4} labels={["GND", "3V3", "SDA", "SCL"]} label="I2C" rot={0} />
    <Jst name="J9" x={-20.25} y={-33} count={4} labels={["B", "A", "GND", "V12"]} label="DISPLAY" rot={180} />
    {/* 12V inlet — KF301-5.0-2P 2-pin 5.0mm screw terminal (C474881, 17A/250V), the board's power
        inlet on the south edge (east end, over the V12 island). Sized for the ~3.3A peak
        (both pumps priming + a few valves + the condenser fan) with margin the 2A XH wafer didn't
        have. pcbRotation 0 aims the wire throats at the south board edge, so the field loom feeds in
        from OUTSIDE the board. y=-32.5 seats the body so its south plastic (courtyard) sits ~2.4 mm
        from the board edge, reading uniform with the south JSTs. pin1->GND, pin2->V12; the 0 seats
        GND on the west pad (x 11.0) and V12 on the east (x 16.0) — reversing 12V would cook the
        polarised bulk cap (C3), the bucks, and the drivers. THT barrels pick up their nets: V12 off
        the top island (the rectangle floods under the barrel), GND off the bottom plane (the pour antipads
        the GND barrel clear of the island). Labels ARE the Jst survive-block: the import's own ref-des
        is suppressed, "12V" (1.4mm) + the pin labels (0.8mm) are hand-drawn upright OUTBOARD toward the
        edge at the same absolute Y as the south JSTs; the ref-des sits inside the fence. */}
    <KF301_5_0_2P name="J10" pinLabels={{ pin1: ["GND"], pin2: ["V12"] }} pcbRotation={0} {...at(13.5, -32.5)} />
    <silkscreentext text="GND" fontSize="0.8mm" anchorAlignment="center" pcbX={11.0} pcbY={-36.94} />
    <silkscreentext text="V12" fontSize="0.8mm" anchorAlignment="center" pcbX={16.0} pcbY={-36.94} />
    <silkscreentext text="12V" fontSize="1.4mm" anchorAlignment="center" pcbX={13.5} pcbY={-38.0} />
    <silkscreentext text="J10" fontSize="0.8mm" anchorAlignment="center" pcbX={13.5} pcbY={-29.6} />
    {J11El}
    {/* GAS dividers: step the MQ-6's 0-5 V AOUT/DOUT down to ~3.0 V on-board, so a
        plain sensor cable is safe (IO36/IO39 are NOT 5 V tolerant). Each output is
        a vertical 2-resistor series: 2.2k (input, bottom) -> midpoint -> 3.3k (to
        GND, top) -> 5*3.3/5.5 = 3.0 V (safely under 3.3 V, still a valid logic HIGH
        for DOUT). The midpoint taps right into the ESP; AOUT: R1/R2 -> IO39, DOUT:
        R3/R4 -> IO36. IO36/IO39 are the ADC1 input-only pins at the west end of the ESP
        south edge; the dividers sit just below them, the GAS connector below the dividers. */}
    {R1El}
    {R2El}
    {R3El}
    {R4El}

    {/* 3V3 rail -> inner1 plane, sourced by the AMS1117 LDO (U9) off the 5V rail. The I2C
        devices (both MCPs, DS3231), RS485, the WROOM, and the sensor loom all common to it at
        their barrels. */}
    {/* U9 AMS1117-3.3: VIN off the 5V plane, GND to the bottom plane, VOUT1+VOUT2 (tab) to the
        3V3 plane. U10 K7805 buck: Vin (pin1) off 12V, GND (pin2) to bottom, +Vo (pin3) to 5V.
        Local decoupling: C13 (10uF) V5 input, C14 (22uF) 3V3 output. */}
    <trace from=".U9 > .VIN" to="net.V5" />
    <trace from=".U9 > .GND" to="net.GND" />
    <trace from=".U9 > .VOUT1" to="net.V3V3" />
    <trace from=".U9 > .VOUT2" to="net.V3V3" />
    <trace from=".C13 > .pin1" to="net.V5" />
    <trace from=".C13 > .pin2" to="net.GND" />
    <trace from=".C14 > .pin1" to="net.V3V3" />
    <trace from=".C14 > .pin2" to="net.GND" />
    <trace from=".U10 > .pin1" to="net.V12" />
    <trace from=".U10 > .pin2" to="net.GND" />
    <trace from=".U10 > .pin3" to="net.V5" />
    <trace from=".C15 > .pin1" to="net.V12" />
    <trace from=".C15 > .pin2" to="net.GND" />
    <trace from=".C16 > .pin1" to="net.V5" />
    <trace from=".C16 > .pin2" to="net.GND" />
    {/* I2C expansion header (J8) for the off-board MPR121 cap-sense controller — all four
        pins land on plane pours (stitch vias), so the connector places anywhere. */}
    <trace from=".J8 > .GND" to="net.GND" />
    <trace from=".J8 > .3V3" to="net.V3V3" />
    <trace from=".J8 > .SDA" to="net.SDA" />
    <trace from=".J8 > .SCL" to="net.SCL" />
    <trace from=".U2 > .VCC" to="net.V3V3" />
    <trace from=".U3 > .VCC" to="net.V3V3" />
    <trace from=".U6 > .VCC" to="net.V3V3" />
    <trace from=".C6 > .pin1" to="net.V3V3" />
    <trace from=".U7 > .VCC" to="net.V3V3" />
    <trace from=".U7 > .SHDN" to="net.V3V3" />
    <trace from=".C7 > .pin1" to="net.V3V3" />
    <trace from=".J4 > .3V3" to="net.V3V3" />

    {/* Bare WROOM (U1) power + reset block. 3V3 is the lone supply pin: it, the decouplers
        (C10 0.1uF / C11 10uF bulk) and the pull-up high sides (R7 EN, R8 IO0) all common to
        the 3V3 plane; the GND pads (incl. the centre thermal pad) and the EN cap (C12) low
        side to the bottom plane — all SMD legs auto-stitch. EN power-on RC: R7 (10k) to 3V3,
        C12 (1uF) to GND. IO0 held high by R8 (10k). TX0 (IO1) / RX0 (IO3) / IO0 / EN run to
        the USB-C programming block (below). No V5 — the module is 3V3-only. */}
    <trace from=".U1 > .3V3" to="net.V3V3" />
    <trace from=".U1 > .GND" to="net.GND" />
    <trace from=".C10 > .pin1" to="net.V3V3" />
    <trace from=".C10 > .pin2" to="net.GND" />
    <trace from=".C11 > .pin1" to="net.V3V3" />
    <trace from=".C11 > .pin2" to="net.GND" />
    <trace from="R7.pin1" to="C12.pin1" pcbPath={route("R7.pin1", "C12.pin1")} />
    <trace from="C12.pin1" to="U1.EN" pcbPathRelativeTo="board" pcbPath={route(
        "C12.pin1",
        { col: channel(CX_EN, CX_DOUT) },
        U1f.below("EN", 0.75),
        U1f.col("EN", 0),
        "U1.EN",
    )} />
    <trace from=".R7 > .pin2" to="net.V3V3" />
    <trace from=".C12 > .pin2" to="net.GND" />
    <trace from=".R8 > .pin2" to="net.V3V3" />
    {/* <trace from=".R8 > .pin1" to=".U1 > .IO0" /> */}

    {/* 5V rail -> inner2 plane, now sourced by the K7805 buck (U10). Faucet, sensors, and
        gas common to it at their barrels; the buzzer high side (U8 +) auto-stitches to it.
        The bare WROOM draws no 5V (3V3-only). */}
    <trace from=".J3 > .V5" to="net.V5" />
    <trace from=".J4 > .V5" to="net.V5" />
    <trace from=".J11 > .V5" to="net.V5" />
    <trace from=".U8 > ._POS" to="net.V5" />

    {/* grounds (every GND pin -> the bottom plane) */}
    <trace from=".U3 > .GND" to="net.GND" />
    <trace from=".U2 > .GND" to="net.GND" />
    <trace from=".U6 > .GND" to="net.GND" />
    <trace from=".C6 > .pin2" to="net.GND" />

    {/* RTC backup: CR2032 + (pin1) -> VBAT; - (pin2) -> GND. */}
    <trace from=".U6 > .VBAT" to=".BT1 > .pin1" />
    <trace from=".BT1 > .pin2" to="net.GND" />


    {/* ULN U4 ground (U2/U3 grounds are in the grounds block above) */}
    <trace from=".U4 > .GND" to="net.GND" />

    {/* MCP config: U2=0x20, U3=0x21, differing only at A0. A1/A2 grounded on both;
        A0 -> GND on U2, A0 -> 3V3 on U3. /RESET tied high (unused). INTA/INTB unused
        (firmware polls). One 0.1uF decoupler per chip across VDD/VSS. The strap pins,
        VDD, VSS and the cap pads are all poured-net SMD pads, so they auto-stitch to
        their planes (plane-stitching.md) — none of this routes. The unused GPB inputs
        (U2 GPB4-7, U3 GPB6-7) have no board pull — firmware must enable each MCP's GPPU
        on them (or drive them as outputs) so they don't float and draw input-buffer
        crossover current. */}
    <trace from=".U2 > .A0" to="net.GND" />
    <trace from=".U2 > .A1" to="net.GND" />
    <trace from=".U2 > .A2" to="net.GND" />
    <trace from=".U2 > .RESET" to="net.V3V3" />
    <trace from=".U3 > .A0" to="net.V3V3" />
    <trace from=".U3 > .A1" to="net.GND" />
    <trace from=".U3 > .A2" to="net.GND" />
    <trace from=".U3 > .RESET" to="net.V3V3" />
    <Cap name="C4" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-10.25} y={12.5} rot={0} side="N" />
    <Cap name="C5" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-12.75} y={-25.5} rot={270} side="E" />
    <trace from=".C4 > .pin1" to="net.V3V3" />
    <trace from=".C4 > .pin2" to="net.GND" />
    <trace from=".C5 > .pin1" to="net.V3V3" />
    <trace from=".C5 > .pin2" to="net.GND" />

    {/* GPA -> ULN inputs, GPA_k -> IN_{8-k} (GPA0->IN8 ... GPA7->IN1), so the firmware
        valve mapping is unchanged; inside the ULN, channel j is IN_j -> OUT_j -> J.OUT_j
        (valve-control.mmd). Each MCP sits immediately left of its ULN, so the eight pairs
        cross straight across. */}
    <trace from=".U2 > .GPA0" to=".U4 > .IN8" pcbComb="rowToColumn" />
    <trace from=".U2 > .GPA1" to=".U4 > .IN7" pcbComb="rowToColumn" />
    <trace from=".U2 > .GPA2" to=".U4 > .IN6" pcbComb="rowToColumn" />
    <trace from=".U2 > .GPA3" to=".U4 > .IN5" pcbComb="rowToColumn" />
    <trace from=".U2 > .GPA4" to=".U4 > .IN4" pcbComb="rowToColumn" />
    <trace from=".U2 > .GPA5" to=".U4 > .IN3" pcbComb="rowToColumn" />
    <trace from=".U2 > .GPA6" to=".U4 > .IN2" pcbComb="rowToColumn" />
    <trace from=".U2 > .GPA7" to=".U4 > .IN1" pcbComb="columnToRow" />
    <trace from=".U3 > .GPA0" to=".U5 > .IN8" pcbComb="rowToColumn" />
    <trace from=".U3 > .GPA1" to=".U5 > .IN7" pcbComb="rowToColumn" />
    <trace from=".U3 > .GPA2" to=".U5 > .IN6" pcbComb="rowToColumn" />
    <trace from=".U3 > .GPA3" to=".U5 > .IN5" pcbComb="rowToColumn" />
    <trace from=".U3 > .GPA4" to=".U5 > .IN4" pcbComb="rowToColumn" />
    <trace from=".U3 > .GPA5" to=".U5 > .IN3" pcbComb="rowToColumn" />
    <trace from=".U3 > .GPA6" to=".U5 > .IN2" pcbComb="rowToColumn" />
    <trace from=".U3 > .GPA7" to=".U5 > .IN1" pcbComb="rowToColumn" />

    {/* I2C bus — SDA and SCL are high-fan-out nets, so they are POURED (inner3 / inner4),
        not routed: every SDA/SCL pin is put on its net and commons to that plane (the SMD
        pads auto-stitch a via to the inner layer). net.SDA = U1.IO21 + U6/U2/U3.SDA;
        net.SCL = U1.IO22 + U6/U2/U3.SCL. The router excludes poured nets, so nothing here
        routes. */}
    <trace from=".U1 > .IO21" to="net.SDA" />
    <trace from=".U6 > .SDA" to="net.SDA" />
    <trace from=".U2 > .SDA" to="net.SDA" />
    <trace from=".U3 > .SDA" to="net.SDA" />
    <trace from=".U1 > .IO22" to="net.SCL" />
    <trace from=".U6 > .SCL" to="net.SCL" />
    <trace from=".U2 > .SCL" to="net.SCL" />
    <trace from=".U3 > .SCL" to="net.SCL" />

    {/* RS485 TTL side -> ESP UART. RO (the receiver output) lands on IO34 — the ESP
        UART RX, an input-only pin, all an RX needs; DI (the driver input) is fed by
        IO32 — the ESP UART TX, which must be output-capable (IO34/35/36/39 can't
        drive). 3.3 V VCC keeps RO's swing safe for input-only IO34. /RE -> GND keeps
        the receiver always on; auto-direction is driven entirely off the DI pin. */}
    {/* <trace from=".U7 > .RO" to=".U1 > .IO34" /> */}{/* deferred: autoroute shadowed U1.IO35/D6 under the north-comb re-solve */}
    {/* <trace from=".U7 > .DI" to=".U1 > .IO32" /> */}{/* evicted — owning the north region (routing-procedure step 5) */}
    <trace from=".U7 > .RE" to="net.GND" />
    <trace from=".U7 > .GND" to="net.GND" />
    <trace from=".C7 > .pin2" to="net.GND" />

    {/* manifold JSTs: ULN outputs -> valve looms */}
    <trace from=".U4 > .OUT1" to=".J1 > .OUT1" pcbComb="rowToColumn" thickness="0.3mm" />
    <trace from=".U4 > .OUT2" to=".J1 > .OUT2" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U4 > .OUT3" to=".J1 > .OUT3" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U4 > .OUT4" to=".J1 > .OUT4" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U4 > .OUT5" to=".J1 > .OUT5" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U4 > .OUT6" to=".J1 > .OUT6" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U4 > .OUT7" to=".J1 > .OUT7" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U4 > .OUT8" to=".J1 > .OUT8" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".J1 > .COM" to="net.V12" />
    {/* MANIFOLD B: 4 valves on U5 ch1-4, condenser FAN on U5 ch5, COM = 12V flyback. */}
    <trace from=".U5 > .OUT1" to=".J2 > .OUT1" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U5 > .OUT2" to=".J2 > .OUT2" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U5 > .OUT3" to=".J2 > .OUT3" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U5 > .OUT4" to=".J2 > .OUT4" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".U5 > .OUT5" to=".J2 > .FAN" pcbComb="columnToColumn" thickness="0.3mm" />
    <trace from=".J2 > .COM" to="net.V12" />

    {/* FAUCET UART — IO33 TX (output-capable) / IO35 RX (input-only), both S-edge pins;
        the connector sits in the bottom row below them. */}
    {/* <trace from=".J3 > .IO33" to=".U1 > .IO33" />
    <trace from=".J3 > .IO35" to=".U1 > .IO35" /> */}{/* faucet UART evicted — owning the north region (step 5) */}
    <trace from=".J3 > .GND" to="net.GND" />

    {/* SENSORS: flow (IO25) / 1-wire temps (IO26) / backflow drip-pan moisture
        (IO27) — three adjacent S-edge GPIOs. The 1-wire bus gets a proper 4.7k external
        pull-up to 3V3 on-board (R9 above), not the ESP's weak internal one; flow uses the
        internal pull-up (open-collector). 3V3 powers the DS18B20 probes + the moisture
        module; V5 the flow sensor. */}
    {/* SENSORS IO25/26/27 evicted — owning the north region (step 5); re-add / hand-route in rebuild. */}
    {/* <trace from=".J4 > .IO25" to=".U1 > .IO25" />
    <trace from=".J4 > .IO26" to=".U1 > .IO26" />
    <trace from=".J4 > .IO27" to=".U1 > .IO27" /> */}
    <trace from=".J4 > .GND" to="net.GND" />

    {/* PUMP DRIVERS — the two DRV8870 H-bridges (U11 pump A, U12 pump B). Single-direction drive:
        IN2 -> GND plane (auto-stitched, no route), only IN1 carries PWM from a WROOM north pin.
        OUT1/OUT2 to the PUMPS connector. VM off 12V; GND + thermal PAD to the plane; ISEN to GND,
        VREF to 3V3; VM decoupled by C17/C18 (U11) and C19/C20 (U12). With IN2 grounded, IO16/IO18
        (and IO5) are free GPIO. */}
    <trace from=".U11 > .IN2" to="net.GND" />
    {/* IO17 pump-A PWM — middle lane of the north-edge comb: exit IO17's pad NORTH on the bottom to
        y13 (above the pad-shadow band), east, then north into U11.IN1. */}
    <trace from="U1.IO17" to="U11.IN1" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO17",
        { row: 11.5 },
        U11f.col("IN1"),
        "U11.IN1",
    )} />
    <trace from=".U11 > .VM" to="net.V12" />
    <trace from=".U11 > .GND" to="net.GND" />
    <trace from=".U11 > .PAD" to="net.GND" />
    <trace from=".U11 > .ISEN" to="net.GND" />
    <trace from=".U11 > .VREF" to="net.V3V3" />
    <trace from=".U11 > .OUT1" to=".J13 > .AM1" thickness="0.4mm" />
    <trace from=".U11 > .OUT2" to=".J13 > .AM2" thickness="0.4mm" />
    <trace from=".C17 > .pin1" to="net.V12" />
    <trace from=".C17 > .pin2" to="net.GND" />
    <trace from=".C18 > .pin1" to="net.V12" />
    <trace from=".C18 > .pin2" to="net.GND" />
    <trace from=".U12 > .IN2" to="net.GND" />
    {/* IO4 pump-B PWM — eastmost/bottom lane of the north-edge comb. IO4 sits just east of RXD's old
        lane, so it exits its pad NORTH on the bottom to y12 (above the pad-shadow band, boot wall is
        top), runs east under the open corridor, then north into U12.IN1 (the VM caps are top-only, a
        stitch via 0.86 mm off). */}
    <trace from="U1.IO4" to="U12.IN1" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO4",
        { row: 11 },
        U12f.col("IN1"),
        "U12.IN1",
    )} />
    <trace from=".U12 > .VM" to="net.V12" />
    <trace from=".U12 > .GND" to="net.GND" />
    <trace from=".U12 > .PAD" to="net.GND" />
    <trace from=".U12 > .ISEN" to="net.GND" />
    <trace from=".U12 > .VREF" to="net.V3V3" />
    <trace from=".U12 > .OUT1" to=".J13 > .BM1" thickness="0.4mm" />
    <trace from=".U12 > .OUT2" to=".J13 > .BM2" thickness="0.4mm" />
    <trace from=".C19 > .pin1" to="net.V12" />
    <trace from=".C19 > .pin2" to="net.GND" />
    <trace from=".C20 > .pin1" to="net.V12" />
    <trace from=".C20 > .pin2" to="net.GND" />

    {/* RELAYS (J5): logic out to the two external opto-isolated relay modules + their V5 coil supply. */}
    {/* IO19 relay — westmost/top lane of the north-edge BOTTOM comb (IO19, IO17, IO4 fan east in
        order to J5 / U11 / U12, so they nest without crossing). The boot wall is TOP copper, so on the
        bottom IO19 exits its pad NORTH to y14 — clear above the pad row's shadow band (pads end y10.05)
        and above the R16 stitch via at (-56,13) — then east and north onto J5.IO19's barrel. */}
    <trace from="U1.IO19" to="J5.IO19" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO19",
        { row: 12 },
        J5f.col("IO19"),
        "J5.IO19",
    )} />
    {/* <trace from=".J5 > .IO23" to=".U1 > .IO23" /> */}
    <trace from=".J5 > .V5" to="net.V5" />
    <trace from=".J5 > .GND" to="net.GND" />


    {/* REEDS A (reservoir A) -> 0x20 GPB inputs; J6 sits directly above U2 and fans down. */}
    <trace from=".U2 > .GPB0" to=".J6 > .RA1" pcbComb="rowToRow" />
    <trace from=".U2 > .GPB1" to=".J6 > .RA2" pcbComb="rowToRow" />
    <trace from=".U2 > .GPB2" to=".J6 > .RA3" pcbComb="rowToRow" />
    <trace from=".U2 > .GPB3" to=".J6 > .RA4" pcbComb="rowToRow" />
    <trace from=".J6 > .GND" to="net.GND" />

    {/* REEDS B (reservoir B + carbonator low/high) -> 0x21 GPB inputs; J7 sits below U3 and fans up. */}
    <trace from=".U3 > .GPB0" to=".J7 > .RB1" pcbComb="rowToRow" />
    <trace from=".U3 > .GPB1" to=".J7 > .RB2" pcbComb="rowToRow" />
    <trace from=".U3 > .GPB2" to=".J7 > .RB3" pcbComb="rowToRow" />
    <trace from=".U3 > .GPB3" to=".J7 > .RB4" pcbComb="rowToRow" />
    <trace from=".U3 > .GPB4" to=".J7 > .CLO" pcbComb="rowToRow" />
    <trace from=".U3 > .GPB5" to=".J7 > .CHI" pcbComb="rowToRow" />
    <trace from=".J7 > .GND" to="net.GND" />
    <trace from=".U3 > .GND" to="net.GND" />

    {/* DISPLAY: the front 4.3" config panel's whole loom lands on J9 — RS485 signal AND the panel's
        7-36 V supply. The differential pair fans U7.A/B -> J9, tapped by the 120R termination (R6) and
        the SM712 ESD array (D1) at the cable entry; GND (pin3) is the RS485 reference, the panel's
        power return, and the cable earth all in one; V12 (pin4) feeds the panel its 12 V. Since V12
        is a top island (not a plane), J9.V12's barrel only picks it up where the pour physically covers
        it — the V12 rectangle (below) floods under the whole south edge, covering J9's V12 barrel. */}
    {/* RS485 A/B pair + termination + ESD — evicted while owning the north region (step 5); these
        re-add / hand-route in the rebuild. */}
    {/* <trace from=".U7 > .A" to=".J9 > .A" />
    <trace from=".U7 > .B" to=".J9 > .B" />
    <trace from=".U7 > .A" to=".R6 > .pin1" />
    <trace from=".U7 > .B" to=".R6 > .pin2" />
    <trace from=".U7 > .A" to=".D1 > .A" />
    <trace from=".U7 > .B" to=".D1 > .B" /> */}
    <trace from=".D1 > .GND" to="net.GND" />
    <trace from=".J9 > .GND" to="net.GND" />
    <trace from=".J9 > .V12" to="net.V12" />

    {/* 12V in: J10 feeds the ULN flyback commons (net.V12). */}
    <trace from=".U4 > .COM" to="net.V12" />
    <trace from=".U5 > .COM" to="net.V12" />
    <trace from=".J10 > .GND" to="net.GND" />
    <trace from=".U5 > .GND" to="net.GND" />

    {/* BUZZER: MLT-5020 passive magnetic transducer (C94598) just east of the ESP by its
        IO13 pin, low-side switched by Q1 (S8050 NPN, C2146) so IO13's ~12 mA source isn't
        asked to sink the buzzer's ~100 mA coil. Tone on IO13 (LEDC, the lone usable east-edge
        GPIO) -> R5 (1k base) -> Q1 base; Q1 collector sinks U8 -, emitter to the GND plane;
        U8 + on the 5 V plane. IO13 is a plain GPIO (not a strapping pin), so it boots high-Z
        and the transducer stays silent until firmware drives it. */}
    <trace from="Q1.C" to="U8._NEG" pcbPathRelativeTo="board" pcbPath={route("Q1.C", U8f.row("_NEG", 0), "U8._NEG")} />
    <trace from=".Q1 > .E" to="net.GND" />
    <trace from="R5.pin1" to="Q1.B" pcbPathRelativeTo="board" pcbPath={route("R5.pin1", "Q1.B")} />
    <trace from="R5.pin2" to="U1.IO13" pcbPathRelativeTo="board" pcbPath={route("R5.pin2", "U1.IO13")} />

    {/* GAS: ACEIRMC MQ-6 combustible / refrigerant-leak sensor, mounted low on the
        rear cabinet floor (catches dense R-600a pooling). 5 V heater supply. BOTH
        MQ-6 outputs swing 0-5 V; each is stepped to ~3.0 V by an on-board divider
        (R1/R2, R3/R4 above) before the ESP, since IO36/IO39 are NOT 5 V tolerant:
          AOUT (analog level)          -> R1/R2 -> IO39 (ADC1) — trend + warm-up sense
          DOUT (LM393 comparator trip) -> R3/R4 -> IO36       — the hardware gas trip
        Own connector, isolated from the SENSORS loom, so the fire-safety run is
        unambiguous. DOUT is the signal a firmware-INDEPENDENT compressor interlock
        must consume; that interlock (a 74LVC1G08 gating the compressor relay line IO19 -> J5)
        is NOT yet on this board — it needs two bench-verified polarities first (see notes). */}
    <trace from="R1.pin2" to="R2.pin1" pcbPath={route("R1.pin2", "R2.pin1")} />
    <trace from="R3.pin2" to="R4.pin1" pcbPath={route("R3.pin2", "R4.pin1")} />
    <trace from=".R2 > .pin2" to="net.GND" />
    <trace from=".R4 > .pin2" to="net.GND" />
    <trace from="R2.pin1" to="U1.IO39" pcbPathRelativeTo="board" pcbPath={route(
        "R2.pin1",
        R2f.row("pin1", -0.8),
        U1f.below("IO39", 0.75),
        U1f.col("IO39", 0),
        "U1.IO39",
    )} />
    <trace from="R4.pin1" to="U1.IO36" pcbPathRelativeTo="board" pcbPath={route("R4.pin1", U1f.col("IO36", 0), "U1.IO36")} />
    <trace from="R1.pin1" to="J11.AOUT" pcbPathRelativeTo="board" pcbPath={route("R1.pin1", J11f.row("AOUT", 0), "J11.AOUT")} />
    <trace from="R3.pin1" to="J11.DOUT" pcbPathRelativeTo="board" pcbPath={route("R3.pin1", J11f.row("DOUT", 0), "J11.DOUT")} />
    <trace from=".J11 > .GND" to="net.GND" />

    {/* V12 decoupling. HF: two 0.1uF ceramics (C1 y-16.6, C2 y0.2) on the V12 island
        by the ULN/manifold block, snubbing the fast solenoid-turn-off edge. BULK: a
        470uF low-ESR electrolytic (C3, BOM 1) at the board centre between the two MCP
        stacks (U2 north, U3 south), west of the ULNs it feeds across the V12 island,
        soaking the inrush + flyback dump the ceramics can't. Every pin1 -> V12, pin2 ->
        GND plane — no routing, no vias, barrel pickup like every power pin; the top V12
        island floods the whole valve block. C3 is polarized: pin1 (+) is V12. */}
    <Cap name="C1" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={13.25} y={-17} rot={0} side="N" />
    <Cap name="C2" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={13} y={1.5} rot={0} side="N" />
    <BulkCap name="C3" x={-3} y={-1.25} />
    <trace from=".C1 > .pin1" to="net.V12" />
    <trace from=".C1 > .pin2" to="net.GND" />
    <trace from=".C2 > .pin1" to="net.V12" />
    <trace from=".C2 > .pin2" to="net.GND" />
    <trace from=".C3 > .pin1" to="net.V12" />
    <trace from=".C3 > .pin2" to="net.GND" />

    {/* SMD GND legs (C1/C2 pin2, R2/R4 pin2) stitch to the bottom GND plane: an SMD pad
        has no through-hole barrel, so a pad whose net is poured on another layer would
        float. The core patch auto-drops a via-in-pad on every such pad (pad layer -> pour
        layer), so no stitch via is declared here. C1/C2 pin1 sit on the top V12 island —
        same layer as their pour — and need none; C3's radial barrel picks up V12/GND
        directly. See plane-stitching.md (and order the PCBA with filled+capped vias). */}

    {/* DS18B20 1-wire bus pull-up — 4.7k from the IO26 data line up to 3V3 (BOM §1 /
        ac-wiring-schedule SIG-1). The bus runs ~600 mm out to the cold-core probes, too
        far for the ESP's ~45k internal pull-up, so the 1-wire bus gets its proper external
        pull-up on-board, at the SENSORS connector where the probe loom leaves the board. */}
    {R9El}
    <trace from=".R9 > .pin1" to="net.V3V3" />
    {/* 1-wire pull-up tap: R9.pin2 drops onto IO26 at the SENSORS connector, sharing the pad with
        the IO26 run to U1 — the external 4.7k sits right where the DS18B20 probe loom leaves the
        board. Exit pin2's east face, ~1 mm jog, straight south into the pad. */}
    <trace from="R9.pin2" to="J4.IO26" pcbPathRelativeTo="board" pcbPath={route(
        "R9.pin2",
        J4f.col("IO26", 0),
        "J4.IO26",
    )} />

    {/* ── Indicator LEDs flanking the brand logo ─────────────────────────────────────
        LEFT — firmware status, three otherwise-idle ESP GPIO, active-high to GND, boot-safe:
        RED = fault (IO14, not a strap), GREEN = ready/heartbeat (IO2, wants low at boot),
        BLUE = activity (IO12 / MTDI, wants low at boot — LED-to-GND only, never tied high).
        RIGHT — power rails, each off its plane through a series R: 3V3 + 5V (3V3 lit ⇒ 12 V in
        AND the 5V buck + 3V3 LDO are up — the board is alive before firmware runs). 470R (C23179) per
        LED; ref-des silk stripped from the LED imports (it collides at this pitch), so meaning
        is by colour + position (see esp32-scope.md). */}
    {/* left — firmware R/G/B; anode toward its R (outboard, -x). Every KT-0603 import carries
        pin1=anode on the +x pad, so all three rot 180 to swing the anode pad outboard-left. */}
    <LedRed name="D2" pcbRotation={180} {...at(-39.75, -15.5)} />
    <LedGrn name="D3" pcbRotation={180} {...at(-39.75, -18)} />
    <LedBlu name="D4" pcbRotation={180} {...at(-39.75, -20.5)} />
    <Res name="R10" resistance="470" footprint="0603" jlcpcb="C23179" x={-44.25} y={-15.5} rot={0} side="N" />
    <Res name="R11" resistance="470" footprint="0603" jlcpcb="C23179" x={-44.25} y={-18} rot={0} side="N" />
    <Res name="R12" resistance="470" footprint="0603" jlcpcb="C23179" x={-44.25} y={-20.5} rot={0} side="N" />
    {/* right — power rails (green); anode toward its R (outboard, +x). pin1=anode is already on
        the +x pad, so these stay native (rot 0) to face the anode pad outboard-right at its R. */}
    <LedGrn name="D5" {...at(-29.75, -17)} />
    <LedGrn name="D6" {...at(-29.75, -20)} />
    <Res name="R13" resistance="470" footprint="0603" jlcpcb="C23179" x={-25.25} y={-17} rot={180} side="N" />
    <Res name="R14" resistance="470" footprint="0603" jlcpcb="C23179" x={-25.25} y={-20} rot={180} side="N" />
    
    {/* firmware: GPIO -> R -> anode, cathode -> GND */}
    <trace from=".U1 > .IO14" to=".R10 > .pin1" />
    <trace from=".R10 > .pin2" to=".D2 > .anode" />
    <trace from=".D2 > .cathode" to="net.GND" />
    <trace from=".U1 > .IO2" to=".R11 > .pin1" />
    <trace from=".R11 > .pin2" to=".D3 > .anode" />
    <trace from=".D3 > .cathode" to="net.GND" />
    <trace from=".U1 > .IO12" to=".R12 > .pin1" />
    <trace from=".R12 > .pin2" to=".D4 > .anode" />
    <trace from=".D4 > .cathode" to="net.GND" />
    {/* rails: plane -> R -> anode, cathode -> GND (R/LED pads auto-stitch to their planes) */}
    <trace from=".R13 > .pin1" to="net.V3V3" />
    <trace from=".R13 > .pin2" to=".D5 > .anode" />
    <trace from=".D5 > .cathode" to="net.GND" />
    <trace from=".R14 > .pin1" to="net.V5" />
    <trace from=".R14 > .pin2" to=".D6 > .anode" />
    <trace from=".D6 > .cathode" to="net.GND" />

    {/* ── USB-C programming block ─────────────────────────────────────────────────────
        USB-C receptacle (J14, north edge above the WROOM, opening flush to the board edge) +
        CH340C USB-UART bridge (U13) flash the WROOM over a plain USB-C cable. Data only: the
        bridge runs off the board 3V3, VBUS powers nothing. CC1/CC2 carry 5.1k Rd pulldowns
        (R15/R16); U14 (USBLC6) clamps D+/D-; both D+ / both D- pads tie for either cable
        orientation.
        AUTO-RESET: DTR/RTS drive a cross-coupled NPN pair — Q2 pulls EN, Q3 pulls IO0.
        esptool ClassicReset polarity (assert = pin LOW):
          Q2 (EN):  base=DTR, emitter=RTS, collector=EN   -> EN low only when DTR high, RTS low
          Q3 (IO0): base=RTS, emitter=DTR, collector=IO0  -> IO0 low only when RTS high, DTR low
        Both-asserted or both-idle => Vbe=0 => off. R17/R18 are the base resistors; the pull
        sides are the EN RC (R7/C12) and the IO0 pull-up (R8). BOOT (SW1) and RESET (SW2) tacts
        are the manual overrides (diagonal pads = the two switch terminals). */}
    {J14El}
    {U14El}
    {U13El}
    {R16El}
    {R15El}
    {C22El}
    <Cap name="C21" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-57.25} y={25.5} rot={180} side="N" />
    {/* EN branch: U13.DTR -> R17 -> Q2.base; U13.RTS -> Q2.emitter; Q2.collector -> EN; SW2 */}
    {R17El}
    {Q2El}
    <Tact name="SW2" x={-57.25} y={33.5} rot={0} />
    {/* IO0 branch: U13.RTS -> R18 -> Q3.base; U13.DTR -> Q3.emitter; Q3.collector -> IO0; SW1 */}
    {R18El}
    {Q3El}
    {SW1El}
    {/* USB-C: GND (pin13/14) + shield ears (pin1-4) to plane; VBUS (pin15/16) to the ESD
        rail only (not board power); CC1 (pin6) / CC2 (pin12) each to a 5.1k Rd; D+ = pin8+pin10,
        D- = pin7+pin9 (both orientations tied). */}
    <trace from=".J14 > .pin13" to="net.GND" />
    <trace from=".J14 > .pin14" to="net.GND" />
    <trace from=".J14 > .pin1" to="net.GND" />
    <trace from=".J14 > .pin2" to="net.GND" />
    <trace from=".J14 > .pin3" to="net.GND" />
    <trace from=".J14 > .pin4" to="net.GND" />
    <trace from="R15.pin1" to="J14.pin6" pcbPathRelativeTo="board" pcbPath={route(
        "R15.pin1",
        R15f.col("pin1", -1),
        R15f.row("pin1", 0.2),
        J14f.row("pin6", -2.3),
        "J14.pin6",
    )} />
    <trace from=".R15 > .pin2" to="net.GND" />
    <trace from="R16.pin1" to="J14.pin12" pcbPathRelativeTo="board" pcbPath={route(
        "R16.pin1",
        R16f.col("pin1", -1),
        R16f.row("pin1", -1.9),
        J14f.row("pin12", -2.3),
        "J14.pin12",
    )} />
    <trace from=".R16 > .pin2" to="net.GND" />
    {/* D+ = J14 pin8(A6)+pin10(B6), D- = J14 pin9(A7)+pin7(B7); the connector ties both USB-C
        orientations. Pads interleave D-/D+/D-/D+ (B7 18.5 / A6 18.0 / A7 17.5 / B6 17.0) at 0.5 mm
        pitch. All top, no vias. */}
    <trace from="U14.pin1" to="J14.pin10" pcbPathRelativeTo="board" pcbPath={route(
        "U14.pin1",
        U14f.row("pin1", 0.8),
        U14f.col("pin1", 2.45),
        J14f.row("pin10", 1.08),
        "J14.pin10",
    )} />
    <trace from="J14.pin10" to="J14.pin8" pcbPathRelativeTo="board" pcbPath={route("J14.pin10", J14f.row("pin10", -1.4), "J14.pin8")} />
    <trace from="U14.pin3" to="J14.pin9" pcbPathRelativeTo="board" pcbPath={route("U14.pin3", dMinusLane, "J14.pin9")} />
    <trace from="U14.pin3" to="J14.pin7" pcbPathRelativeTo="board" pcbPath={route("U14.pin3", dMinusLane, "J14.pin7")} />
    {/* ESD array: GND + VBUS rail + bypass cap; D+/D- pass through to the bridge. */}
    <trace from=".U14 > .pin2" to="net.GND" />
    {/* J14 VBUS pads: pin16 is the NORTH pad (y 20.15), pin15 the SOUTH (y 15.35). Top, no vias. */}
    <trace from="U14.pin5" to="C22.pin1" pcbPathRelativeTo="board" pcbPath={route(
        "U14.pin5",
        U14f.row("pin5", -0.8),
        C22f.row("pin1", -1.5),
        "C22.pin1",
    )} />
    <trace from="C22.pin1" to="J14.pin16" pcbPathRelativeTo="board" pcbPath={route(
        "C22.pin1",
        C22f.col("pin1", -1.25),
        J14f.col("pin16", 0),
        "J14.pin16",
    )} />
    <trace from="U14.pin5" to="J14.pin15" pcbPathRelativeTo="board" pcbPath={route(
        "U14.pin5",
        U14f.row("pin5", -0.8),
        "J14.pin15"
    )} />
    <trace from=".C22 > .pin2" to="net.GND" />
    <trace from="U14.pin6" to="U13.D_POS" pcbPathRelativeTo="board" pcbPath={route(
        "U14.pin6", U14f.row("pin6", 0.95), U13f.below("D_POS", 0.3775), U13f.col("D_POS"), "U13.D_POS",
    )} />
    <trace from="U14.pin4" to="U13.D_NEG" pcbPathRelativeTo="board" pcbPath={route(
        "U14.pin4", U14f.row("pin4", 1.35), U13f.below("D_NEG", 0.7775), U13f.col("D_NEG"), "U13.D_NEG",
    )} />
    {/* CH340C: 3V3 supply (VCC + V3 tied for 3.3 V op) + 0.1uF decoupling; UART crossed to
        the WROOM (bridge TXD -> ESP RXD0/IO3, bridge RXD -> ESP TXD0/IO1). */}
    <trace from=".U13 > .VCC" to="net.V3V3" />
    <trace from=".U13 > .V3" to="net.V3V3" />
    <trace from=".U13 > .GND" to="net.GND" />
    <trace from=".C21 > .pin1" to="net.V3V3" />
    <trace from=".C21 > .pin2" to="net.GND" />
    {/* <trace from=".U13 > .TXD" to=".U1 > .IO3" /> */}
    {/* <trace from=".U13 > .RXD" to=".U1 > .IO1" /> */}
    {/* RXD/TXD (UART0, fixed to IO1/IO3 — the west-north pins) are deferred: their bottom lane west
        would cross the pump comb's north exits, so the USB corner is re-planned before they land. */}
    {/* Auto-reset cross-coupled pair (see block header for the truth table). Owning the region:
        the six internal DTR/RTS connections are hand-routed below; Q3's collector reaches IO0 down
        the far-west lane into U1's north-edge corridor. Q2's collector reach to EN stays deferred —
        EN sits on U1's south edge, behind the module, reachable only from the south. */}
    {/* base nodes: each transistor's base to the near (south) pin of its base resistor */}
    <trace from="Q2.B" to="R17.pin1" pcbPathRelativeTo="board" pcbPath={route("Q2.B", "R17.pin1")} />
    <trace from="Q3.B" to="R18.pin1" pcbPathRelativeTo="board" pcbPath={route("Q3.B", "R18.pin1")} />
    {/* Cross-coupled pair, planar on top. The two trunks leave U13 on OPPOSITE sides so they never
        cross: RTS exits east and runs the high rail (y30.8) to R18.pin2 then on to Q2.E; DTR exits
        west and runs low (y22.75, along U13's north edge) to Q3.E, which links up to R17.pin2. */}
    <trace from="U13.RTS" to="R18.pin2" pcbPathRelativeTo="board" pcbPath={route(
        "U13.RTS",
        U13f.row("DTR", 1.5),
        R18f.row("pin2"),
        "R18.pin2")
    } />
    <trace from="R18.pin2" to="Q2.E" pcbPathRelativeTo="board" pcbPath={route(
        "R18.pin2",
        R18f.col("pin2", 0.75),
        Q2f.row("E"),
        "Q2.E"
    )} />
    <trace from="U13.DTR" to="Q3.E" pcbPathRelativeTo="board" pcbPath={route(
        "U13.DTR",
        U13f.row("DTR", -1.7),
        U13f.col("DTR", -9.75),
        Q3f.col("E", -1),
        Q3f.row("E"),
        "Q3.E"
    )} />
    <trace from="Q3.E" to="R17.pin2" pcbPathRelativeTo="board" pcbPath={route(
        "Q3.E",
        R17f.col("pin2", -0.75),
        R17f.row("pin2"),
        "R17.pin2"
    )} />
    {/* <trace from=".Q2 > .C" to=".U1 > .EN" /> */}
    <trace from="Q3.C" to="U1.IO0" pcbPathRelativeTo="board" pcbPath={route(
        "Q3.C",
        { col: channel(U1f.pin("IO1").x, U1f.pin("IO22").x) },   // drop the west lane, clear of the CC/J14 block
        U1f.above("IO0", 0.475),                                 // corridor centred in the lane between U1's tall north pads and the CC2 dip
        "U1.IO0",
    )} />
    {/* Manual BOOT (IO0) / RESET (EN) — diagonal switch pads = the two terminals. SW1's boot line
        drops just east of U13 to IO0 (below); IO0's other reach-outs (R8 pull-up, Q3.C collector)
        stay deferred until their corridors are known. */}
    <trace from="SW1.pin1" to="U1.IO0" pcbPathRelativeTo="board" pcbPath={route(
        "SW1.pin1",
        SW1f.col("pin1", -1),
        U13f.below("D_NEG", 1.1775),   // third lane under the D-pair, hugging U13's south edge
        U14f.row("pin4", 1.75),
        U1f.above("IO0", 0.475),      // Q3.C's lane — the twin — and share its run into IO0
        "U1.IO0",
    )} />
    <trace from=".SW1 > .pin4" to="net.GND" />
    {/* <trace from=".SW2 > .pin1" to=".U1 > .EN" /> */}
    <trace from=".SW2 > .pin4" to="net.GND" />

    {/* ── M3 mounting holes, one per corner, plated and tied to GND so a metal screw can't
        bridge a power plane (GND connects on the bottom plane; V12 / 3V3 / 5V / SDA / SCL
        antipad). A symmetric rectangle: every hole is inset 3.5 mm from both of its board
        edges, so the four stay centred on the board and clear of the nearest connector at
        each corner. 3.2 mm hole / 4.0 mm pad (r 2.0): an M3 screw head (socket-cap or pan,
        ~5.5 mm ⌀ → r ~2.75) overhangs the pad by ~0.75 mm, and an M3 hex standoff (5.5 mm A/F,
        r ~3.2) or washer (~7 mm ⌀, r ~3.5) more — so the nearest corner connector housing is
        held ≥2 mm off the pad edge (the seated head + standoff clear it), the tightest being
        J8→MH3 and J11→MH4. The connector audit (connector-audit.ts) measures this each render. */}
    <platedhole name="MH1" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" connectsTo="net.GND" pcbX={-64.5} pcbY={33.5} />
    <platedhole name="MH2" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" connectsTo="net.GND" pcbX={23.5} pcbY={33.5} />
    <platedhole name="MH3" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" connectsTo="net.GND" pcbX={23.5} pcbY={-35.5} />
    <platedhole name="MH4" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" connectsTo="net.GND" pcbX={-64.5} pcbY={-35.5} />

    {/* Board identity nameplate — the soda-glass brand mark (ios/AppIcon.svg,
        monocolor silk via logo.ts) over the centered name + version, a compact
        stack in the open lower-centre, flanked by the indicator LEDs (the firmware
        R/G/B column to its west, the power pair to its east) with the name + version
        dropping below them. The version is the firmware scheme (firmware/pre_build.py):
        commit date + short SHA, a trailing `+` from uncommitted edits — a pure function
        of the commit, naming which source tree a fabbed board came from. */}
    {logoRoutes(-34.75, -18.0, 6).map((route, i) => (
      <silkscreenpath key={`logo${i}`} strokeWidth="0.15mm" route={route} />
    ))}
    <silkscreentext text="HOME SODA MACHINE" fontSize="1.6mm" anchorAlignment="center" pcbX={-34.75} pcbY={-23.0} />
    <silkscreentext text={`${ID.date}.${ID.rev}`} fontSize="1.6mm" anchorAlignment="center" pcbX={-34.75} pcbY={-25.0} />

    {/* Power/bus pours — SIX layers, top->bottom: top (signals + the V12 island), 3V3
        (inner1), 5V (inner2), SDA (inner3), SCL (inner4), GND (bottom). 3V3/5V/SDA/SCL/GND
        are full-flood planes; each pin commons to its plane at its through-hole barrel or
        an auto-stitched via (SMD). V12 is a top-copper island over the valve/buck/driver
        block (the rectangle below): top-layer 12V pads sit directly on it, through-hole 12V
        pins pick it up at the barrel. Point-to-point signals route on top and bottom. */}
    <trace from=".J10 > .V12" to="net.V12" />
    {/* V12 top island — a plain rectangle over the whole 12 V region (pump drivers, ULN commons +
        manifolds, buck, bulk cap), x[-31.75,26.5] running the FULL board depth y[-38.5,36.5]. V12 is
        an ISLAND, not a plane, so a barrel only picks it up where the pour physically covers it — and
        a connector's barrel row (J7's reeds, J9's own pins) is a wall of near-touching antipads that
        no pour can thread. So instead of reaching for each south-edge 12 V barrel with a finger (which
        those walls chop into disconnected scraps), the sheet just swallows them: because it fills the
        strip BELOW the barrel rows too (down to y -38.5), V12 flows UNDER every connector and around
        the walls, reaching J10's inlet barrel (x 16) and J9's display-feed barrel (x -16.5) alike.
        One dumb connected rectangle, 0.5 mm off the north/east/south edges; its west edge x -31.75
        clears the LED/logo/nameplate cluster. Everything foreign inside it (the barrels, the MCPs,
        BT1, the signal fan-out, the SE GND mounting hole) is just a hole in the sheet. */}
    <copperpour name="V12ISLAND" layer="top" connectsTo="net.V12" netClearance="0.5mm from V3V3, V5, SDA, SCL"
      outline={[{ x: -31.75, y: 36.5 }, { x: 26.5, y: 36.5 }, { x: 26.5, y: -38.5 },
                { x: -31.75, y: -38.5 }]} />
    <copperpour name="V3V3PLANE" layer="inner1" connectsTo="net.V3V3" boardEdgeMargin="0.5mm" />
    <copperpour name="V5PLANE" layer="inner2" connectsTo="net.V5" boardEdgeMargin="0.5mm" />
    <copperpour name="SDAPLANE" layer="inner3" connectsTo="net.SDA" boardEdgeMargin="0.5mm" />
    <copperpour name="SCLPLANE" layer="inner4" connectsTo="net.SCL" boardEdgeMargin="0.5mm" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" boardEdgeMargin="0.5mm" />
  </board>
)
