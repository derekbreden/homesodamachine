/**
 * pcba — the controller board, ordered fully assembled from JLCPCB. Every active
 * part is bare silicon on this board (no modules, nothing hand-soldered), and every
 * off-board interface lands on a labeled edge connector (J1-J14). Footprint geometry
 * lives in ./parts (the part wrappers) and ./routing (hand-routing geometry); placement + routing
 * are declared here.
 *
 * The ESP32 sits at the far-left, antenna off-board. Its usable GPIO are nearly all on the
 * north and south castellations (the east edge is flash + the lone GPIO IO13), so every
 * off-board signal fans up or down and its connector lives on that edge, ordered to match the
 * pin run. NORTH / top: RELAYS (J5) at the edge, the USB-C programming block (J14 + the CH340
 * bridge, above the WROOM) at the top-left, and — combed up from the north
 * pins as one parallel bus — the two pump drivers (U11/U12) feeding PUMPS. SOUTH / bottom: an
 * edge row of cable connectors — GAS (J11), FAUCET (J3), SENSORS (J4), DISPLAY (J9) — with
 * their on-board conditioning just above (the R1-R4 gas dividers under the WROOM, the 3V3 LDO
 * U9 above FAUCET, the U7 RS485 transceiver above DISPLAY). The buzzer (U8/Q1/R5) sits east of
 * the ESP by its IO13 pin; the 5V buck (U10) below the coin cell; the identity nameplate
 * in the bay north of U9. Center:
 * DS3231 + coin cell; the two MCPs stacked through the middle (0x20 north, 0x21 south) with
 * their reed inputs on REEDS A (above) / REEDS B (below). Right block: the two ULNs with the
 * valve manifolds immediately to their right, and the 12V inlet (J10) at the south-east corner.
 *
 * FOUR layers, stackup top->bottom:
 *   L1 top    — signals + the V12 island
 *   L2 inner1 — 3V3 plane (full flood) + the SDA bus trace
 *   L3 inner2 — 5V plane (full flood) + the SCL bus trace
 *   L4 bottom — GND plane (full flood) + signals
 * 3V3/5V/GND are full-flood planes: each pin commons to its plane at the barrel
 * (through-hole) or an auto-stitched via (SMD). V12 is a top-copper island over the valve/
 * buck/driver block (the rectangle at the pours): top-layer 12V pads sit on it directly,
 * through-hole 12V pins pick it up at the barrel. The I2C bus (SDA / SCL) rides the two
 * plane layers as hand traces (routeInner, I2C block below): the planes carry no other
 * trace copper, so each bus net crosses a near-empty layer and its pour carves clearance
 * around the trace as it does around any foreign copper. All other signals are hand copper
 * on top and bottom.
 *
 * Every via is ONE full-stack through-hole drill — JLCPCB standard assembly drills no
 * blind/buried vias. A routeBottom via transitions top<->bottom; a routeInner via enters on
 * its pad and leaves on an inner layer — the barrel still spans the whole column (the core
 * fork records `pcb_via.layers` as the full stack), the pours antipad it on every plane it
 * crosses, and the DRC (clearance.ts) flags any barrel that isn't full-column. Every pad-via
 * is via-in-pad, so order filled+capped vias.
 *
 * Every signal connection is an explicit hand path (pcbPath) — the autorouter owns nothing.
 * Its config on the board tag (`viaMode="through-hole"`, `viaInPad`, `viaRingKeepout`,
 * `traceClearance`) still governs the mesh should a connection ever be handed back to it;
 * keep `traceClearance` in the ~0.12-0.14 zone (the realized-floor peak) if that day comes.
 *
 * `schematicDisabled` on the board: this is a fab-only PCB (its canonical "schematic" is
 * esp32-pinout.mmd). tscircuit's schematic-trace-solver — NOT the PCB autorouter — hangs on
 * this dense layout whenever a net is added; the capacity-autorouter handles the PCB fine.
 * Disabling the schematic removes the hang and speeds every render; the gerbers are unaffected.
 *
 * The clearance floor (0.15) is a hand trace threading the buck cluster's pad column
 * (U10, below the coin cell); the web viewer's board chip reports it live
 * (clearance.ts -> picks.json).
 */
import { at, Cap, Res, Jst, jstPins, ulnOUT, Uln2803, Mcp23017, Ds3231Smd, Cos13487, Sm712, Buck5, Buzzer, CoinHolder, BulkCap, Npn, Esp32, Ams1117, Ch340, Usblc6, UsbC, Drv8870, Tact, Diode, Pfet, Tvs, Zener, And2 } from "./parts"
import { KF301_5_0_2P } from "./imports/KF301_5_0_2P"
import { frame, route, routeBottom, routeInner, channel } from "./routing"
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
const U14El = <Usblc6 name="U14" x={-56.25} y={16} rot={270} ly={1.9} />  // ref-des north: the centre row is the GND/VBUS pads
const C22El = <Cap name="C22" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-56.25} y={19.35} rot={0} side="N" />
const J14El = <UsbC name="J14" x={-62} y={16.5} rot={270} />
const U13El = <Ch340 name="U13" x={-48.25} y={23.55} rot={0} />  // slid E 1.0 (clear of C22's SW-corner overlap) + S 1.0 to open the tact strip
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
// from U13's east edge. Q3's collector runs the boot wall to IO0 (through R8's pull-up pad); Q2's
// runs the far-west flank to EN, tapped by SW2's reset line.
const Q2El = <Npn name="Q2" x={-65.5} y={24.75} rot={90} />
const Q3El = <Npn name="Q3" x={-61.5} y={24.75} rot={90} />
const R17El = <Res name="R17" resistance="10k" footprint="0603" jlcpcb="C25804" x={-64.5} y={28.75} rot={0} side="W" />
const R18El = <Res name="R18" resistance="10k" footprint="0603" jlcpcb="C25804" x={-61.9} y={28.75} rot={90} side="W" />
// IO0's 10k pull-up, parked in the pocket east of U13's body where the corridor down to the pad
// row is empty — every slot nearer the lattice is fenced by the DTR/RTS runs, J14's courtyard,
// and the switch row (whose band the relay's bottom lane also crosses). pin1 (rot90: south) drops
// the corridor and crosses to IO0 on the bottom, under the relay's top rise; pin2 (3V3) stitches
// to its plane.
const R8El = <Res name="R8" resistance="10k" footprint="0603" jlcpcb="C25804" x={-50.5} y={15} rot={90} side="W" />  // W of IO0 (pin1 drops S then E into IO0); vacated its old (-46) seat for U15 + R24
const R8f = frame(R8El)
// ── Gas→compressor interlock (U15 74LVC1G08 AND gate) ─────────────────────────────────────────
// The firmware-INDEPENDENT compressor interlock the GAS block calls out: U15 gates the ESP compressor
// command (A ← U1.IO19) with the MQ-6 hardware gas-clear line (B ← divided DOUT), driving the relay
// (Y → J5.IO19). Y = A·B, so the compressor energizes ONLY when firmware asks AND the sensor reads
// clear — a gas trip cuts the relay in hardware even if firmware is hung. It seats in the pocket E of
// the WROOM (x>-47, off the castellation rim) ON the old IO19→J5 corridor: A and Y are the two halves
// of a haul that already routed clean, and only B is a new run — around the WROOM's SE, never across
// the module. SOT-353 rot0: A(pin2)/B(pin1)/GND(pin3) south, Y(pin4)/VCC(pin5) north. Truth + fail-safe
// + invert provisions in the GAS-block comment below.
const U15El = <And2 name="U15" x={-45.9} y={15.5} rot={0} />  // ref-des on the body centre (SOT-353 has no centre pad), between the pad rows
// R24 (100k) pulls the gate-B node LOW at the gate, so a broken B-haul fails safe (B→0 ⇒ Y→0 ⇒ relay
// OFF ⇒ compressor off). R25 (0Ω) is the DOUT-polarity invert-select link in series from the divider
// node; C23 (0.1µF) decouples VCC. R24 sits just W of B in the flank; C23 N of the gate by VCC.
const R24El = <Res name="R24" resistance="100k" footprint="0402" jlcpcb="C60491" x={-48.2} y={14.6} rot={90} side="W" />  // B-node pulldown (fail-safe): pin1 S → B, pin2 N → GND; in the flank W of U15
const C23El = <Cap name="C23" capacitance="0.1uF" footprint="0402" jlcpcb="C1525" x={-45.5} y={17.9} rot={0} side="N" />   // VCC decoupler, N of the gate
const R25El = <Res name="R25" resistance="0" footprint="0402" jlcpcb="C17168" x={-52.7} y={-12.6} rot={0} side="S" />       // DOUT invert-select series link (clear top spot E of C10; pin1 W→DOUT, pin2 E→B)
const R25f = frame(R25El)
const U15f = frame(U15El), R24f = frame(R24El), C23f = frame(C23El)
// BOOT (SW1) and RESET (SW2) tacts stand rotated in the strip between U13 and the north edge,
// pads N/S (the rotation narrows each to the strip's width; south pads clear the RTS rail at
// y28.9, north pads stay inside the board-edge pour margin). Each connects one DIAGONAL pair —
// the only pairing that is a switch whatever the internal terminal split: SW1 signal pin4 (NE,
// down the J5 GND/V5 ring channel to IO0), GND pin1 (SW); SW2 signal pin3 (NW, a bottom drop to
// Q2.C), GND pin2 (SE). GND sits on a SOUTH pad on both — a north-pad stitch via would tangent
// the GND pour's 0.5 board-edge margin.
const SW1El = <Tact name="SW1" x={-51.75} y={31.75} rot={90} />
const SW2El = <Tact name="SW2" x={-57.75} y={31.75} rot={270} />
const SW2f = frame(SW2El)

// ── Buzzer chain (IO13 → R5 → Q1 → U8) ────────────────────────────────────────────────
const R5El = <Res name="R5" resistance="1k" footprint="0603" jlcpcb="C21190" x={-45.228} y={-4.445} rot={180} side="N" />
const Q1El = <Npn name="Q1" x={-41.45} y={-5.395} rot={180} />
const U8El = <Buzzer name="U8" x={-37.9} y={-10.72} />
// D7 — buzzer-coil flyback clamp (1N4148W SOD-123). Stands vertical (rot 270: pin1 CATHODE north,
// pin2 anode south) in the strip S of the buzzer, between the LED column (west) and BT1/U10 (east).
// Cathode commons to the 5V plane at its stitch via (the same node as U8._POS); the anode → U8._NEG
// (Q1.C) tap must cross the IO26 top trace (y-11.1, which runs between the two coil pads), so it
// hops to the bottom — the one clear layer in that column — and climbs a via back into _NEG.
const D7El = <Diode name="D7" x={-36.0} y={-17.0} rot={270} ly={-3.0} />
const R5f = frame(R5El), Q1f = frame(Q1El), U8f = frame(U8El), D7f = frame(D7El)
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
// Ref-des sit E (the vertical preference): R2's tap rises east of its label (the -2.1 jog), C12's
// W dodges the EN riser in its channel, and R4's E crosses the IO36 tap hairline — the one channel
// R4 has (EN riser west, column link south, the module north), a deliberate least-collision pick.
const CX_EN = -65.5, CX_DOUT = -63.5, CX_AOUT = -61.5   // columns W→E
const CY_BOT = -15.65, CY_TOP = -12.15                    // input (south) / GND·V3V3 (north) rows (N clears U1 courtyard -10.05)
// Placed here (not down in the return) so each frame derives from its own element; rendered below
// via {R1El}… The grid parts ride the CX/CY consts, so a one-line const move still slides the lattice.
const R1El = <Res name="R1" resistance="2.2k" footprint="0603" jlcpcb="C4190" x={CX_AOUT} y={CY_BOT} rot={90} side="W" />   // AOUT in (pin1 S) → midpoint (pin2 N)
const R2El = <Res name="R2" resistance="3.3k" footprint="0603" jlcpcb="C22978" x={CX_AOUT} y={CY_TOP} rot={90} side="W" />  // midpoint (pin1 S) → GND (pin2 N)
const R3El = <Res name="R3" resistance="2.2k" footprint="0603" jlcpcb="C4190" x={CX_DOUT} y={CY_BOT} rot={90} side="W" />   // DOUT in (pin1 S) → midpoint (pin2 N)
const R4El = <Res name="R4" resistance="3.3k" footprint="0603" jlcpcb="C22978" x={CX_DOUT} y={CY_TOP} rot={90} side="W" />  // midpoint (pin1 S) → GND (pin2 N)
const R7El = <Res name="R7" resistance="10k" footprint="0603" jlcpcb="C25804" x={CX_EN} y={CY_BOT} rot={270} side="W" />    // EN node (pin1 N) → V3V3 (pin2 S)
const C12El = <Cap name="C12" capacitance="1uF" footprint="0603" jlcpcb="C15849" x={CX_EN} y={CY_TOP} rot={90} side="W" />  // EN node (pin1 S) → GND (pin2 N); near U1.EN
const R1f = frame(R1El), R2f = frame(R2El), R3f = frame(R3El), R4f = frame(R4El), R7f = frame(R7El), C12f = frame(C12El)
const U1El = <Esp32 name="U1" x={-57} y={0} rot={0} ly={4} />  // ref-des north of the centre GND thermal-pad array
const U1f = frame(U1El)                               // ESP32; taps by label (EN/IO36/IO39)
const J11El = <Jst name="J11" x={-62} y={-23.85} count={4} labels={["GND", "V5", "DOUT", "AOUT"]} label="GAS" rot={90} />
const J11f = frame("J11", J11El.props.x, J11El.props.y, 0, Object.fromEntries(jstPins(J11El.props).pins))
// SENSORS connector + its 1-wire pull-up (R9), framed for the R9→IO26 tap below. R9 seats
// in the band between U10's courtyard and J4's, straddling the IO26 drop column (pads thread
// it at 0.245 a side) with pin2 — the tap — east; ref-des east, riding the IO26/IO27 gap.
const R9El = <Res name="R9" resistance="4.7k" footprint="0603" jlcpcb="C23162" x={-32.5} y={-26.45} rot={0} side="E" />
const R9f = frame(R9El)
// IO25 flow-input hardening (IO25 is NOT 5V-tolerant). Two 0402s stack in the SENSORS pocket W of
// R9: R21 (1k) in SERIES between the U1.IO25 haul and J4.IO25, R22 (4.7k) pulls the J4-side up to
// 3V3 — the same protection R9 gives the IO26 1-wire line. Both horizontal; R21 south (haul enters
// pin1 from the low band, pin2 drops to the barrel), R22 north (pin1→3V3 plane, pin2 taps R21.pin2).
const R21El = <Res name="R21" resistance="1k" footprint="0402" jlcpcb="C11702" x={-35.9} y={-26.55} rot={0} side="S" />
const R22El = <Res name="R22" resistance="4.7k" footprint="0402" jlcpcb="C25900" x={-35.9} y={-24.9} rot={0} side="N" />
const R21f = frame(R21El), R22f = frame(R22El)
// ── J10 12V input protection: reverse-polarity pass FET + surge clamp ──────────────────
// The one clear home is the slot WEST of J10 (x 4.5→8.11, C5 east to J10 body). Q4 (AO3407 P-FET,
// SOT-23) sits high beside C5, drain EAST toward J10; its narrow profile (rot 180 lands D/S along
// the E-W axis) threads the C5↔J10 slot. D8 (SMAJ15A TVS, SMA) stands vertical in the wider bay
// below C5; D9 (BZT52C15 Zener, SOD-123) + R23 (100k gate pulldown) stack in the west column east
// of U3. Wiring + the V12→V12IN island split are in the return, by the J10 block.
const Q4El = <Pfet name="Q4" x={6.3} y={-15.8} rot={180} />
const D8El = <Tvs name="D8" x={6.1} y={-23.0} rot={270} />
const D9El = <Zener name="D9" x={3.2} y={-23.5} rot={90} />
const R23El = <Res name="R23" resistance="100k" footprint="0402" jlcpcb="C60491" x={3.2} y={-19.7} rot={90} side="E" />
const Q4f = frame(Q4El), D8f = frame(D8El), D9f = frame(D9El), R23f = frame(R23El)
// J10 (KF301 screw terminal) is placed inline in the return; frame it here so the V12IN stub can
// route into the V12 barrel. rot 90 puts pin1/GND south (12.35,-24), pin2/V12 north (12.35,-19).
const J10f = frame("J10", 12.35, -21.5, 90, { V12: [2.5, 0], GND: [-2.5, 0] })
const J4El = <Jst name="J4" x={-35.0} y={-30.3} count={7} labels={["3V3", "GND", "V5", "IO25", "IO26", "IO27", "IO23"]} label="SENSORS" rot={180} />
const J4f = frame("J4", J4El.props.x, J4El.props.y, 0, Object.fromEntries(jstPins(J4El.props).pins))
const J5El = <Jst name="J5" x={-41.95} y={31.0} count={4} labels={["GND", "V5", "IO2", "IO19"]} label="RELAYS" rot={0} />
const J5f = frame("J5", J5El.props.x, J5El.props.y, 0, Object.fromEntries(jstPins(J5El.props).pins))
// Pump H-bridges, framed for the IN-bus routing below. J13 sits centred over the driver
// pair (U11+4.25 / U12-2.75); the VM caps flank each driver at ∓1.5/+1.75.
const U11El = <Drv8870 name="U11" x={-16.5} y={22.75} rot={0} ly={4.75} />  // ref-des north, clear of the thermal PAD
const U12El = <Drv8870 name="U12" x={-9.5} y={22.75} rot={0} ly={4.75} />  // ref-des north, clear of the thermal PAD
const U11f = frame(U11El), U12f = frame(U12El)
// Firmware status-LED resistors, framed for the GPIO-feed routing below.
const R10El = <Res name="R10" resistance="470" footprint="0603" jlcpcb="C23179" x={-43.2} y={-15.5} rot={0} side="N" />
const R11El = <Res name="R11" resistance="470" footprint="0603" jlcpcb="C23179" x={-43.2} y={-18} rot={0} side="N" />
const R12El = <Res name="R12" resistance="470" footprint="0603" jlcpcb="C23179" x={-43.2} y={-20.5} rot={0} side="N" />
const R10f = frame(R10El), R11f = frame(R11El), R12f = frame(R12El)
// RS485 display block, framed for the A/B pair routing below.
const U7El = <Cos13487 name="U7" x={-19.5} y={-19.65} rot={180} />
const R6El = <Res name="R6" resistance="120" footprint="0603" jlcpcb="C22787" x={-19.5} y={-26.1} rot={0} side="N" />
const D1El = <Sm712 name="D1" x={-23.1} y={-25.6} rot={90} />
const J9El = <Jst name="J9" x={-17.75} y={-30.3} count={4} labels={["B", "A", "GND", "V12"]} label="DISPLAY" rot={180} />
const U7f = frame(U7El), R6f = frame(R6El), D1f = frame(D1El)
const J9f = frame("J9", J9El.props.x, J9El.props.y, 0, Object.fromEntries(jstPins(J9El.props).pins))
// Faucet UART connector, framed for the IO33/IO35 routing below.
const J3El = <Jst name="J3" x={-52.25} y={-30.3} count={4} labels={["GND", "V5", "IO35", "IO33"]} label="FAUCET" rot={180} />
const J3f = frame("J3", J3El.props.x, J3El.props.y, 0, Object.fromEntries(jstPins(J3El.props).pins))
// Faucet-UART series resistors (R26 in IO33, R27 in IO35) — the driver-end backstop for the ~1 m
// umbilical to the faucet display: series damping on the TTL edges + a current-limit into the
// board's own pin under an ESD strike. Each ~220Ω 0402 splits its line like R21 splits IO25 — the
// U1-side trace ends at pin1, the far pad carries on to J3. Both sit OFF J3 (the barrel row has no
// room) in the only two homes the dense cap column leaves: R26 (rot 0, pin1 W) in the open top
// pocket E of the caps / N of U9 (x biased W of the WROOM pin-column bottom haul at −51.05), reached
// by jogging IO33 E below C11; R27 (rot 270, pin1 N) in the west sliver on IO35's own drop, between
// the C10 courtyard and IO34's RS485 bottom haul — that haul is nudged one drop-column W (see the
// IO34→U7.RO route) to open the sliver. The PRIMARY faucet ESD clamps live at the display connector
// end of the umbilical, at the user-touch source (see cable-assemblies.md); these are the backstop.
const R26El = <Res name="R26" resistance="220" footprint="0402" jlcpcb="C25091" x={-52.5} y={-18.7} rot={0} side="S" />    // IO33: pin1 (W) ← U1, pin2 (E) → J3 (W end of the bay: clears the −51.05 bottom haul E + C11 courtyard W; version stamp's date/rev shifted E to clear its ref-des)
const R27El = <Res name="R27" resistance="220" footprint="0402" jlcpcb="C25091" x={-59.65} y={-13.5} rot={270} side="E" /> // IO35: pin1 (N) ← U1, pin2 (S) → J3
const R26f = frame(R26El), R27f = frame(R27El)
// Pumps connector + RTC block + status LEDs, framed for the last hand routes below.
const J13El = <Jst name="J13" x={-12.25} y={31} count={4} labels={["AM2", "AM1", "BM2", "BM1"]} label="PUMPS" rot={0} />
const J13f = frame("J13", J13El.props.x, J13El.props.y, 0, Object.fromEntries(jstPins(J13El.props).pins))
const BT1El = <CoinHolder name="BT1" x={-20.5} y={-1.25} />
const U6El = <Ds3231Smd name="U6" x={-40.35} y={2.5} rot={270} />  // nudged 0.15 E (clear of BT1): opens the WROOM↔U6 flank for the interlock B-haul beside the IO15→R10 feed
const BT1f = frame(BT1El), U6f = frame(U6El)
const D2El = <LedRed name="D2" pcbRotation={180} {...at(-39.75, -15.5)} />
const D3El = <LedGrn name="D3" pcbRotation={180} {...at(-39.75, -18)} />
const D4El = <LedBlu name="D4" pcbRotation={180} {...at(-39.75, -20.5)} />
const D5El = <LedGrn name="D5" pcbRotation={180} {...at(-39.75, -23.0)} />
const D6El = <LedGrn name="D6" pcbRotation={180} {...at(-39.75, -25.5)} />
const D2f = frame(D2El), D3f = frame(D3El), D4f = frame(D4El), D5f = frame(D5El), D6f = frame(D6El)
const R13El = <Res name="R13" resistance="470" footprint="0603" jlcpcb="C23179" x={-43.2} y={-23.0} rot={0} side="N" />
const R14El = <Res name="R14" resistance="470" footprint="0603" jlcpcb="C23179" x={-43.2} y={-25.5} rot={0} side="N" />
const R13f = frame(R13El), R14f = frame(R14El)

// ── I2C bus (SDA / SCL as routeInner traces on the plane layers) ─────────────────────────
// The bus members (U2/U3 MCPs, U6 RTC, J8 → the off-board MPR121) framed for the routeInner
// edges below. R19/R20 are the bus pull-ups (4.7k → 3V3): every device on the bus is
// open-drain with no pull-up of its own, and the ESP32's ~45k internal ones are too weak for
// a board-length multi-drop bus. Each parks with pin1 rising into the row-28.2 corridor and
// closing on its hub barrel, pin2 stitching to the 3V3 plane. R19 stands VERTICAL (rot 270,
// pin1 NORTH) on U11's west flank above C17 — east of the col -21.7 SDA/SCL risers, under
// J6's south face; R20 HORIZONTAL (rot 180, pin1 EAST) in the band under J8's bay (y≈26.2:
// U12's courtyard fences everything south, J8's body everything north of ~28.5).
const U2El = <Mcp23017 name="U2" x={-31.4} y={20.25} addr="0x20" rot={180} />
const U3El = <Mcp23017 name="U3" x={-7.2} y={-20.15} addr="0x21" rot={0} />
const U2f = frame(U2El), U3f = frame(U3El)
const J8El = <Jst name="J8" x={1.3} y={31} count={4} labels={["GND", "3V3", "SDA", "SCL"]} label="I2C" rot={0} />
const J8f = frame("J8", J8El.props.x, J8El.props.y, 0, Object.fromEntries(jstPins(J8El.props).pins))
const R19El = <Res name="R19" resistance="4.7k" footprint="0603" jlcpcb="C23162" x={-20.7} y={26.67} rot={270} side="W" />
const R20El = <Res name="R20" resistance="4.7k" footprint="0603" jlcpcb="C23162" x={-4.8} y={26.2} rot={180} side="N" />
const R19f = frame(R19El), R20f = frame(R20El)

// ── Valve/reed fan frames — the ULNs, manifolds, and reed connectors, framed for the
// nested fan routes below (each MCP↔ULN↔manifold column and its reed connector). ─────────
const U4El = <Uln2803 name="U4" x={-0.75} y={9.9} rot={270} />
const U5El = <Uln2803 name="U5" x={-0.5} y={-7.35} rot={270} />
const U4f = frame(U4El), U5f = frame(U5El)
const J1El = <Jst name="J1" x={11} y={16.48} count={9} labels={[...ulnOUT].reverse()} label="MANIFOLD A" rot={270} />
const J2El = <Jst name="J2" x={11} y={-5.77} count={6} labels={["COM", "FAN", "OUT4", "OUT3", "OUT2", "OUT1"]} label="MANIFOLD B" rot={270} />
const J6El = <Jst name="J6" x={-27.1} y={31} count={5} labels={["GND", "RA4", "RA3", "RA2", "RA1"]} label="REEDS A" rot={0} />
// J7 is a JST-EH (not XH) wafer: REEDS B carries only dry-reed signals, and J4 SENSORS is the same 7P
// grid — keying J7 to a non-intermating EH housing makes a loom swap (which would drive 5V/3V3 into MCP
// inputs) physically impossible. Same holes/pitch as XH, so every reed net stays on its barrel.
const J7El = <Jst name="J7" x={-0.5} y={-30.3} count={7} labels={["RB1", "RB2", "RB3", "RB4", "CLO", "CHI", "GND"]} label="REEDS B" rot={180} series="EH" />
const J1f = frame("J1", J1El.props.x, J1El.props.y, 0, Object.fromEntries(jstPins(J1El.props).pins))
const J2f = frame("J2", J2El.props.x, J2El.props.y, 0, Object.fromEntries(jstPins(J2El.props).pins))
const J6f = frame("J6", J6El.props.x, J6El.props.y, 0, Object.fromEntries(jstPins(J6El.props).pins))
const J7f = frame("J7", J7El.props.x, J7El.props.y, 0, Object.fromEntries(jstPins(J7El.props).pins))

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
  { cap: "C23", near: "U15", role: "interlock AND-gate VCC", kind: "hf" },
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
//   J10 inlet → pass-FET drain stub (Q4.D → J10.V12) — the ONE 12V path that isn't a pour: the
//     whole board's ~3.3A peak (both pumps priming + valves + fan) crosses it. Routed 1.6mm, want
//     ≥1.5mm (IPC-2221, ~1.57mm for 3.3A at 10°C rise on 1oz external — and the peak is transient).
//     The source→island side needs no rule: the island floods Q4's source pad, unlimited pour copper.
// `pin` is an endpoint-pin prefix (U11.OUT matches U11.OUT1/OUT2, etc.). Rules of thumb, not a
// thermal model — enough to catch a fat path left on the 0.2mm floor.
export const ampacity: AmpacityRule[] = [
  { pin: "U11.OUT", minWidthMm: 0.3, role: "pump A motor (~0.8A)" },
  { pin: "U12.OUT", minWidthMm: 0.3, role: "pump B motor (~0.8A)" },
  { pin: "U4.OUT", minWidthMm: 0.25, role: "MANIFOLD A valves (ULN, ≤0.5A)" },
  { pin: "U5.OUT", minWidthMm: 0.25, role: "MANIFOLD B valves + fan (ULN, ≤0.5A)" },
  { pin: "Q4.D", minWidthMm: 1.5, role: "12V inlet pass-FET drain stub (~3.3A board peak)" },
]

export default () => (
  <board layers={4} schematicDisabled outline={[{ x: -68, y: -36.3 }, { x: 17, y: -36.3 }, { x: 17, y: 36.5 }, { x: -68, y: 36.5 }]} minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" pcbStyle={{ silkscreenFontSize: "0.8mm", viaPadDiameter: "0.5mm", viaHoleDiameter: "0.3mm" }} autorouter={{ traceClearance: 0.15, viaMode: "through-hole", viaInPad: true, viaRingKeepout: false }}>
    {/* DS3231SN RTC + CR2032 backup, east of the ESP. U6 (the SOIC) sits high with its
        0.1uF decoupler (C6) to its west and the buzzer column below it; the 20 mm THT coin
        base (BT1) is the bulk to U6's east. + is pin1 (the silk-marked post -> VBAT), - is
        pin2 (-> GND); the cell is retained by the molded base, not SMT clips. */}
    {BT1El}
    {U6El}
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
    {R8El}
    {/* RS-485 to the front display (J9). COS13487EESA-3.3 auto-direction transceiver (U7):
        no host DE/RE — /RE tied low (always receive), /SHDN tied high (always on),
        only DI (from ESP TX) and RO (to ESP RX) are driven. R6 = 120R line termination
        across A/B; D1 = SM712 ESD array at the J9 cable entry; C7 decouples VCC. */}
    {U7El}
    {R6El}
    {D1El}
    <Cap name="C7" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-19.3} y={-14.05} rot={0} side="N" />
    {/* On-board supplies. U10 = K7805 (12V->5V, 2A) SIP module (pin1 Vin / pin2 GND / pin3
        +Vo), 10uF input + 22uF output cap. U9 = AMS1117-3.3 (C6186, SOT-223 LDO) makes 3V3
        from the 5V rail: VIN off V5, VOUT1 + VOUT2 (tab) to 3V3, GND to the bottom plane;
        the SMD pads auto-stitch to their planes. C13 (10uF V5 input) + C14 (22uF 3V3
        output) stand as a vertical column on U9's west flank beside the VOUT tab,
        threading between the IO35 column and the IO33 channel (pads 0.27+ clear of
        each); C13's ref-des sits west of the pair, crossing the IO35 hairline as
        mask-covered ink. U10 stands vertical (rot 90, pin column at x -30.8, body east)
        in the bay west of BT1: the pin column threads BETWEEN the IO26 and IO27 sensor
        drop columns (0.15+ pad-shadow clear of each) so the pins sit on the island
        without the pour edge moving, and the whole column sits north of both RS485
        bottom rows (the 2.54 pin pitch can't straddle them). C15/C16 stand as a
        vertical pair on its east flank (C16 output cap
        north by pin3, C15 input cap south toward pin1, pads clear of the DI row); every pin
        is a plane pickup, so the buck cluster carries no routed copper at all. */}
    <Ams1117 name="U9" x={-51.43} y={-23.8} rot={0} />
    <Cap name="C13" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-57.55} y={-20.59} rot={90} side="W" />
    <Cap name="C14" capacitance="22uF" footprint="0805" jlcpcb="C45783" x={-57.55} y={-25.25} rot={90} side="W" />
    <Buck5 name="U10" x={-30.8} y={-19.2} rot={90} />
    <Cap name="C15" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-23.8} y={-20.35} rot={90} side="W" />
    <Cap name="C16" capacitance="22uF" footprint="0805" jlcpcb="C45783" x={-23.8} y={-15.4} rot={90} side="W" />
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
    <Cap name="C17" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-20.72} y={22.75} rot={90} side="W" />
    <Cap name="C18" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-18.2} y={17.35} rot={180} side="N" />{/* nudged S so the N ref-des clears U11's GND pad */}
    {U12El}
    <Cap name="C19" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-5.4} y={22.75} rot={90} side="W" />
    <Cap name="C20" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-11.2} y={17.35} rot={180} side="N" />{/* nudged S so the N ref-des clears U12's GND pad */}
    {U2El}
    {U3El}
    {U4El}
    {U5El}
    {U8El}
    {Q1El}
    {R5El}
    {/* Manifolds sit immediately right of their ULNs so OUT1-8/COM are straight shots
        across (J1 pin order = ULN output pin order, reversed). */}
    {J1El}
    {J2El}
    {/* Pump-motor outputs — one PUMPS connector. Pin order is AM2/AM1/BM2/BM1, left to
        right, matching the drivers' OUT pads west-to-east (U11 then U12) so each pair
        combs straight up to its own side of J13 with no crossing. */}
    {J13El}
    {J3El}
    {J4El}
    {/* RELAYS — logic-level control out to the two external opto-isolated relay modules
        (compressor AC switch + carbonator diaphragm-pump 12V gate, both off-board). IO2/
        IO19 drive them (IO2 is boot-safe into an opto input: the module's LED load holds it
        low, which is also what download mode wants); V5 feeds the relay modules' coil/opto
        supply; GND returns. */}
    {J5El}
    {J6El}
    {J7El}
    {J8El}
    {R19El}
    {R20El}
    {J9El}
    {/* 12V inlet — KF301-5.0-2P 2-pin 5.0mm screw terminal (C474881, 17A/250V), the board's power
        inlet on the east edge (south end, below MANIFOLD B). Sized for the ~3.3A peak (both pumps
        priming + a few valves + the condenser fan) with margin the 2A XH wafer didn't have.
        pcbRotation 90 aims the wire throats at the east board edge, so the field loom feeds in from
        OUTSIDE the board. pin1->GND on the south pin, pin2->V12 on the north. The barrel now lands on
        net.V12IN, the RAW inlet node — the incoming 12V passes through the Q4 reverse-polarity pass
        FET before it reaches the V12 island, so a mis-wired loom no longer cooks C3, the K7805, or
        the drivers (Q4 blocks reverse current; D8 clamps the surge the board sees). THT barrels pick
        up their nets: V12IN off the wide top stub to Q4's drain (the island voids around the barrel),
        GND off the bottom plane (the pour antipads the GND barrel clear of the island). Labels are
        hand-drawn, all bottom-to-top (the east-edge convention): the pin labels (0.8mm) sit OUTBOARD
        east of the throats where the wires land, "12V" (1.4mm) + the ref-des west of the body. */}
    <KF301_5_0_2P name="J10" pinLabels={{ pin1: ["GND"], pin2: ["V12"] }} pcbRotation={90} {...at(12.35, -21.5)} />
    <silkscreentext text="GND" fontSize="0.8mm" anchorAlignment="center" pcbX={16.45} pcbY={-24.0} pcbRotation={90} />
    <silkscreentext text="V12" fontSize="0.8mm" anchorAlignment="center" pcbX={16.45} pcbY={-19.0} pcbRotation={90} />
    <silkscreentext text="12V" fontSize="1.4mm" anchorAlignment="center" pcbX={7.3} pcbY={-18.6} pcbRotation={90} />
    <silkscreentext text="J10" fontSize="0.8mm" anchorAlignment="center" pcbX={7.3} pcbY={-22.3} pcbRotation={90} />
    {/* Reverse-polarity + surge block, in the slot west of J10 (wiring/pour split below). */}
    {Q4El}
    {D8El}
    {D9El}
    {R23El}
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
    {/* I2C expansion header (J8) for the off-board MPR121 cap-sense controller. GND/3V3 land
        on their plane pours at the barrel; the SDA/SCL barrels are the BUS JUNCTIONS — every
        routeInner edge of the I2C block (below) terminates at them, so the connector's spot
        anchors the whole bus tree. R19/R20 pull-up high sides stitch to the 3V3 plane. */}
    <trace from=".J8 > .GND" to="net.GND" />
    <trace from=".J8 > .3V3" to="net.V3V3" />
    <trace from=".R19 > .pin2" to="net.V3V3" />
    <trace from=".R20 > .pin2" to="net.V3V3" />
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
        U1f.below("EN", 0.45),
        U1f.col("EN", 0),
        "U1.EN",
    )} />
    <trace from=".R7 > .pin2" to="net.V3V3" />
    <trace from=".C12 > .pin2" to="net.GND" />
    <trace from=".R8 > .pin2" to="net.V3V3" />

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

    {/* RTC backup: CR2032 + (pin1) -> VBAT; - (pin2) -> GND. VBAT exits its east-row pad and
        runs its own row east under the holder body, dropping into the + post from the north. */}
    <trace from="U6.VBAT" to="BT1.pin1" pcbPathRelativeTo="board" pcbPath={route(
        "U6.VBAT",
        BT1f.col("pin1"),
        "BT1.pin1",
    )} />
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
    {/* C4 stands on U2's east flank (the U2/U11 channel) — the north band under J5 and the
        south band over the IO-rows are both too shallow for an 0805 courtyard. 4.2mm from
        U2's nearest pad, serving VDD through the 3V3 plane like the original south-side
        seat did. */}
    <Cap name="C4" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-41.9} y={16.5} rot={90} side="W" />{/* W: E grazes U2's fence; dropped S 1.0 to clear U13's SE corner as it slid east */}
    <Cap name="C5" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={3.35} y={-16.15} rot={270} side="W" />
    <trace from=".C4 > .pin1" to="net.V3V3" />
    <trace from=".C4 > .pin2" to="net.GND" />
    <trace from=".C5 > .pin1" to="net.V3V3" />
    <trace from=".C5 > .pin2" to="net.GND" />

    {/* GPA -> ULN inputs, GPA_k -> IN_{8-k} (GPA0->IN8 ... GPA7->IN1), so the firmware
        valve mapping is unchanged; inside the ULN, channel j is IN_j -> OUT_j -> J.OUT_j
        (valve-control.mmd). Each MCP sits west of its ULN, and the pin orders anti-align
        (U2's westmost GPA pairs with U4's southmost IN), so the eight L's nest by
        construction: each GPA exits its pad away from the body, drops its own column to
        its IN pad's row, and runs east into the pad's west face — a drop never crosses a
        foreign run because every run starts east of it. U2's long arms cross the open band
        north of BT1; U3's stay short. U4/U5 sit rot 270, so F.col(pin) is the board ROW
        through the pad. */}
    <trace from="U2.GPA0" to="U4.IN8" pcbPathRelativeTo="board" pcbPath={route("U2.GPA0", U4f.col("IN8"), "U4.IN8")} />
    <trace from="U2.GPA1" to="U4.IN7" pcbPathRelativeTo="board" pcbPath={route("U2.GPA1", U4f.col("IN7"), "U4.IN7")} />
    <trace from="U2.GPA2" to="U4.IN6" pcbPathRelativeTo="board" pcbPath={route("U2.GPA2", U4f.col("IN6"), "U4.IN6")} />
    <trace from="U2.GPA3" to="U4.IN5" pcbPathRelativeTo="board" pcbPath={route("U2.GPA3", U4f.col("IN5"), "U4.IN5")} />
    <trace from="U2.GPA4" to="U4.IN4" pcbPathRelativeTo="board" pcbPath={route("U2.GPA4", U4f.col("IN4"), "U4.IN4")} />
    <trace from="U2.GPA5" to="U4.IN3" pcbPathRelativeTo="board" pcbPath={route("U2.GPA5", U4f.col("IN3"), "U4.IN3")} />
    <trace from="U2.GPA6" to="U4.IN2" pcbPathRelativeTo="board" pcbPath={route("U2.GPA6", U4f.col("IN2"), "U4.IN2")} />
    <trace from="U2.GPA7" to="U4.IN1" pcbPathRelativeTo="board" pcbPath={route("U2.GPA7", U4f.col("IN1"), "U4.IN1")} />
    <trace from="U3.GPA0" to="U5.IN8" pcbPathRelativeTo="board" pcbPath={route("U3.GPA0", U5f.col("IN8"), "U5.IN8")} />
    <trace from="U3.GPA1" to="U5.IN7" pcbPathRelativeTo="board" pcbPath={route("U3.GPA1", U5f.col("IN7"), "U5.IN7")} />
    <trace from="U3.GPA2" to="U5.IN6" pcbPathRelativeTo="board" pcbPath={route("U3.GPA2", U5f.col("IN6"), "U5.IN6")} />
    <trace from="U3.GPA3" to="U5.IN5" pcbPathRelativeTo="board" pcbPath={route("U3.GPA3", U5f.col("IN5"), "U5.IN5")} />
    <trace from="U3.GPA4" to="U5.IN4" pcbPathRelativeTo="board" pcbPath={route("U3.GPA4", U5f.col("IN4"), "U5.IN4")} />
    <trace from="U3.GPA5" to="U5.IN3" pcbPathRelativeTo="board" pcbPath={route("U3.GPA5", U5f.col("IN3"), "U5.IN3")} />
    <trace from="U3.GPA6" to="U5.IN2" pcbPathRelativeTo="board" pcbPath={route("U3.GPA6", U5f.col("IN2"), "U5.IN2")} />
    {/* IN1 is the northmost run, in BT1.pin1's latitude: hold the east haul low at {row -2.8}
        (clearing the + post's south edge -2.25, riding a touch nearer its IN2 sibling), step
        north at {col -9} once east of the post, then close into the pad. */}
    <trace from="U3.GPA7" to="U5.IN1" pcbPathRelativeTo="board" pcbPath={route("U3.GPA7", { row: -2.8 }, { col: -9 }, U5f.col("IN1"), "U5.IN1")} />

    {/* I2C bus — SDA rides inner1 (the 3V3 plane layer), SCL rides inner2 (the 5V plane
        layer) as routeInner traces: the plane layers carry no other trace copper, so each
        net crosses a near-empty layer and the pour carves clearance around it. The tree is a
        STAR at J8's barrels: each SMD drop is exactly one pad-via (via-in-pad, full-stack
        drill), every edge terminates AT its J8 barrel — the one junction structure that
        conducts on every layer without a via — so no pad ever carries two drills. The two
        nets mirror each other's geometry on their own layers (same-plan crossings between
        them are layer-separated by the core):
          · the WROOM corridor {row 10.95} — north of the U1 pad-row shadows (y ≤ 10.15)
            and the boot line's bottom-hop vias (y 10.45), south of J14's shell-slot copper
            (y ≥ 11.175);
          · the mid-board riser {col -20.5} — west of U4's IN-pad wall (a solid shadow
            y 3.6..15.4: 1.62mm pads at 1.27 pitch overlap in projection) and of U9's tab;
          · the north corridor {row 28.2} — above U2's pad row (y ≤ 26.46), below the
            J6/J8 barrel rings (y ≥ 30.2);
          · U3's edges exit SOUTH of its pad row and rise between U3's east flank and U4's
            IN wall (SDA x 1.95, SCL x 2.35), rising east of U3's pad rows between C3's
            barrels, clear of C2 and C5.
        U6.SDA exits WEST (its own column is squatted by U6.SCL's pad shadow); U6.SCL rises
        its own clear column. R19/R20 pin1 edges drop from the pull-up pads into the same
        north corridor. */}
    <trace from="U1.IO21" to="J8.SDA" pcbPathRelativeTo="board" pcbPath={routeInner("inner1",
        "U1.IO21",
        { row: 10.95 },
        { col: -21.7 },
        { row: 28.2 },
        J8f.col("SDA"),
        "J8.SDA",
    )} />
    <trace from="U6.SDA" to="J8.SDA" pcbPathRelativeTo="board" pcbPath={routeInner("inner1",
        "U6.SDA",
        U6f.below("SDA", 0.35),     // board-WEST of the pad row (rot270: local -y), clear of U6.SCL's shadow
        { row: 10.95 },
        { col: -21.7 },
        { row: 28.2 },
        J8f.col("SDA"),
        "J8.SDA",
    )} />
    <trace from="U2.SDA" to="J8.SDA" pcbPathRelativeTo="board" pcbPath={routeInner("inner1",
        "U2.SDA",
        { row: 28.2 },
        J8f.col("SDA"),
        "J8.SDA",
    )} />
    <trace from="U3.SDA" to="J8.SDA" pcbPathRelativeTo="board" pcbPath={routeInner("inner1",
        "U3.SDA",
        U3f.below("SDA", 0.35),     // south exit under the pad row
        { col: 1.95 },
        { row: 28.2 },
        J8f.col("SDA"),
        "J8.SDA",
    )} />
    <trace from="R19.pin1" to="J8.SDA" pcbPathRelativeTo="board" pcbPath={routeInner("inner1",
        "R19.pin1",
        { row: 28.2 },
        J8f.col("SDA"),
        "J8.SDA",
    )} />
    <trace from="U1.IO22" to="J8.SCL" pcbPathRelativeTo="board" pcbPath={routeInner("inner2",
        "U1.IO22",
        { row: 10.95 },
        { col: -21.7 },
        { row: 28.2 },
        J8f.col("SCL"),
        "J8.SCL",
    )} />
    <trace from="U6.SCL" to="J8.SCL" pcbPathRelativeTo="board" pcbPath={routeInner("inner2",
        "U6.SCL",
        { row: 10.95 },
        { col: -21.7 },
        { row: 28.2 },
        J8f.col("SCL"),
        "J8.SCL",
    )} />
    <trace from="U2.SCL" to="J8.SCL" pcbPathRelativeTo="board" pcbPath={routeInner("inner2",
        "U2.SCL",
        { row: 28.2 },
        J8f.col("SCL"),
        "J8.SCL",
    )} />
    <trace from="U3.SCL" to="J8.SCL" pcbPathRelativeTo="board" pcbPath={routeInner("inner2",
        "U3.SCL",
        U3f.below("SCL", 0.35),     // south exit under the pad row
        { col: 2.35 },
        { row: 28.2 },
        J8f.col("SCL"),
        "J8.SCL",
    )} />
    <trace from="R20.pin1" to="J8.SCL" pcbPathRelativeTo="board" pcbPath={routeInner("inner2",
        "R20.pin1",
        { row: 28.2 },
        J8f.col("SCL"),
        "J8.SCL",
    )} />

    {/* RS485 TTL side -> ESP UART. RO (the receiver output) lands on IO34 — the ESP
        UART RX, an input-only pin, all an RX needs; DI (the driver input) is fed by
        IO32 — the ESP UART TX, which must be output-capable (IO34/35/36/39 can't
        drive). 3.3 V VCC keeps RO's swing safe for input-only IO34. /RE -> GND keeps
        the receiver always on; auto-direction is driven entirely off the DI pin. */}
    {/* RO/DI — the ~40mm west haul to U1's south row. The top face is the sensor comb's (its
        drops wall x-46.75/-32.5/-29.75 through the whole band), so both ride the BOTTOM as
        parallel lanes: IO34 drops its own clear column, IO32 threads the C10 pin1/pin2 channel
        (its own column sits in C10.pin2's shadow). Through the LED field the pair runs low,
        threading between the PWR row's pad-vias and the 5V row's; east of the field each jogs
        one tier north (IO32 first at -36.5, IO34 nested at -35.5) to the pocket rows that
        cross U10's column south of its pin1 barrel and clear D1's pads. RO's rises through
        U7's VCC/B pad channel, DI's stops short of U7.GND's through-stack shadow and rises
        along the pad row's west flank; both close north into a pad-via on U7's north row from
        the lane between the pad rows. Lane pitch 0.6 everywhere; the C11/C10 stitch barrels
        flank the channel at 0.65. */}
    <trace from="U1.IO34" to="U7.RO" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO34",
        { row: -11 },               // clear the pad row, then step the drop column W
        { col: -60.35 },            // drop nudged W of IO35's column — opens the sliver for R27 (IO35 series-R)
        { row: -27.9 },             // south detour under the relocated U9 cluster
        { col: -45.7 },             // rise east of the cluster, west of the LED resistors
        { row: -24.4 },             // south lane of the pair, over the 5V LED row
        { col: -35.5 },             // jog north east of the LED field (nested inside IO32's)
        { row: -23.7 },             // south pocket lane, under D1's A/B pads
        { col: -18.3 },             // rise through U7's VCC/B pad channel, west of the VCC via
        { row: -21.1 },             // between U7's pad rows, east into the RO pad-via
        "U7.RO",
    )} />
    <trace from="U1.IO32" to="U7.DI" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO32",
        { row: -11.5 },             // clear of the pad row before jogging east
        { col: -56.5 },             // the C10/C11 pin1-pin2 channel
        { row: -27.5 },             // south detour under the U9 cluster
        { col: -46.2 },             // rise east of the cluster, paired lane
        { row: -23.8 },             // north lane of the pair, under the PWR LED row
        { col: -36.5 },             // jog north east of the LED field, before IO34's
        { row: -23.1 },             // north pocket lane, ending west of U7.GND's shadow
        { col: -21.95 },            // rise along the pad row's west flank, clear of the GND via
        { row: -21.1 },             // between U7's pad rows, east into the DI pad-via
        "U7.DI",
    )} />
    <trace from=".U7 > .RE" to="net.GND" />
    <trace from=".U7 > .GND" to="net.GND" />
    <trace from=".C7 > .pin2" to="net.GND" />

    {/* manifold JSTs: ULN outputs -> valve looms. J1's pin order matches U4's OUT order,
        but the barrel pitch (2.5) is double the pad pitch (1.27), so the pairs diverge:
        OUT1-6 rise to their barrels; OUT7-8's barrels sit barely above their pads. Each
        0.3mm line exits its pad east, turns in its own lane column, and closes east into
        the barrel. Riser lanes step east as the rows descend (J1x-4.4 .. J1x-1.4, pitch
        0.6) so every riser passes only landing rows above its own. OUT8 hooks up west of
        the riser wall; OUT7 runs its pad row east PAST the wall and hooks up at J1x-0.7,
        just west of its own ring — its pad row crosses no riser (all start north of it). */}
    <trace from="U4.OUT1" to="J1.OUT1" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U4.OUT1", J1f.col("OUT1", -4.4), J1f.row("OUT1"), "J1.OUT1")} />
    <trace from="U4.OUT2" to="J1.OUT2" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U4.OUT2", J1f.col("OUT2", -3.8), J1f.row("OUT2"), "J1.OUT2")} />
    <trace from="U4.OUT3" to="J1.OUT3" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U4.OUT3", J1f.col("OUT3", -3.2), J1f.row("OUT3"), "J1.OUT3")} />
    <trace from="U4.OUT4" to="J1.OUT4" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U4.OUT4", J1f.col("OUT4", -2.6), J1f.row("OUT4"), "J1.OUT4")} />
    <trace from="U4.OUT5" to="J1.OUT5" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U4.OUT5", J1f.col("OUT5", -2.0), J1f.row("OUT5"), "J1.OUT5")} />
    <trace from="U4.OUT6" to="J1.OUT6" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U4.OUT6", J1f.col("OUT6", -1.4), J1f.row("OUT6"), "J1.OUT6")} />
    <trace from="U4.OUT7" to="J1.OUT7" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U4.OUT7", J1f.col("OUT7", -0.7), J1f.row("OUT7"), "J1.OUT7")} />
    <trace from="U4.OUT8" to="J1.OUT8" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U4.OUT8", J1f.col("OUT8", -5.6), J1f.row("OUT8"), "J1.OUT8")} />
    <trace from=".J1 > .COM" to="net.V12" />
    {/* MANIFOLD B: 4 valves on U5 ch1-4, condenser FAN on U5 ch5, COM = 12V flyback.
        Same nested-Z pattern as J1: OUT1-3 rise, OUT4/FAN drop away with the doubled
        barrel pitch — deeper fallers turn earlier (west, pitch 0.8), so each landing row
        passes south of every foreign column. OUT2's barrel sits above OUT1's pad row, so
        it hooks up east of OUT1's riser (J2x-1.2), clear of the whole lane fan. */}
    <trace from="U5.OUT1" to="J2.OUT1" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U5.OUT1", J2f.col("OUT1", -2.0), J2f.row("OUT1"), "J2.OUT1")} />
    <trace from="U5.OUT2" to="J2.OUT2" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U5.OUT2", J2f.col("OUT2", -1.2), J2f.row("OUT2"), "J2.OUT2")} />
    <trace from="U5.OUT3" to="J2.OUT3" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U5.OUT3", J2f.col("OUT3", -3.6), J2f.row("OUT3"), "J2.OUT3")} />
    <trace from="U5.OUT4" to="J2.OUT4" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U5.OUT4", J2f.col("OUT4", -4.4), J2f.row("OUT4"), "J2.OUT4")} />
    <trace from="U5.OUT5" to="J2.FAN" thickness="0.3mm" pcbPathRelativeTo="board" pcbPath={route("U5.OUT5", J2f.col("FAN", -5.2), J2f.row("FAN"), "J2.FAN")} />
    <trace from=".J2 > .COM" to="net.V12" />

    {/* FAUCET UART — IO33 TX (output-capable) / IO35 RX (input-only), both S-edge pins, the J3
        connector in the bottom row below them. Each line carries a ~220Ω series resistor at the
        driver end (R26 in IO33, R27 in IO35 — see the FAUCET block up top) as the display-cable
        ESD/damping backstop, so each line is TWO hops: U1 → series-R, then series-R → J3 barrel.
        IO35 keeps its own clear west column (west of the C10/C11 pads); IO33 threads the C10/C11
        pin1-pin2 channel on the TOP (IO32 rides that same channel on the BOTTOM). */}
    {/* IO35 splits across R27 (220Ω series): U1.IO35 drops below its pad row, jogs W into the sliver
        (opened by the IO34-haul nudge) onto R27.pin1 (N); pin2 (S) carries the tail down its own
        clear column, then E along the east-run S of U9 into the barrel. */}
    <trace from="U1.IO35" to="R27.pin1" pcbPathRelativeTo="board" pcbPath={route(
        "U1.IO35",
        { row: -11 },               // clear the U1 pad row before the jog west
        R27f.row("pin1"),           // W onto R27's column (rot 270 → its board col, x -59.65)
        "R27.pin1",
    )} />
    <trace from="R27.pin2" to="J3.IO35" pcbPathRelativeTo="board" pcbPath={route(
        "R27.pin2",
        J3f.row("IO35", 2),         // down the sliver column to the east-run, S of U9
        J3f.col("IO35"),            // E into the barrel column
        "J3.IO35",
    )} />
    {/* IO33 splits across R26 (220Ω series): U1.IO33 down the C10/C11 channel, then E below C11 into
        the open pocket at R26.pin1 (W); pin2 (E) drops under the U9 body to the low band, then E
        into the barrel (approached from the W, S of the U9 pin column). */}
    <trace from="U1.IO33" to="R26.pin1" pcbPathRelativeTo="board" pcbPath={route(
        "U1.IO33",
        { row: -12 },               // clear of the pad row before the jog west
        { col: -56.5 },             // the C10/C11 pin1-pin2 channel (top)
        R26f.row("pin1"),           // drop to R26's row (y -18.7), then E straight into pin1
        "R26.pin1",
    )} />
    <trace from="R26.pin2" to="J3.IO33" pcbPathRelativeTo="board" pcbPath={route(
        "R26.pin2",
        { row: -27.5 },             // S under the U9 body (between the tab and the pin column) to the low band
        J3f.col("IO33"),            // E along the low band into the barrel column
        "J3.IO33",
    )} />
    <trace from=".J3 > .GND" to="net.GND" />

    {/* SENSORS: flow (IO25) / 1-wire temps (IO26) / backflow drip-pan moisture signal
        (IO27) — three adjacent S-edge GPIOs — plus the moisture module's switched VCC on
        IO23 (pin 7): GPIO-sourced so the electrodes sit unpowered between samples. The
        1-wire bus gets a proper 4.7k external pull-up to 3V3 on-board (R9 above), not the
        ESP's weak internal one; flow uses the internal pull-up (open-collector). 3V3 powers
        the DS18B20 probes; V5 the flow sensor. J4 and J7 share the 7P housing. */}
    {/* SENSORS IO25/26/27 — owned: a nested 3-lane top comb from U1's south row to J4. Stubs exit
        each pad SOUTH; lanes stack IO27/IO26/IO25 top-to-bottom (0.6 pitch, above the buzzer pads)
        so no stub crosses a foreign lane, and the W→E pin order lands J4's W→E order uncrossed.
        Drops: IO25 can't use its own column (U8._POS pinches beside it, and the LED cathode-via
        column blocks the J4.GND/V5 channel), so it drops early in the open corridor between
        J3.IO33's column and the R10-R14 field, then runs the low band east into the barrel;
        IO26 drops straight down its barrel column, threading R9's pads on the way (R9's tap is
        the same net); IO27 drops just east of U10's pin barrels — the board's 0.15 floor pair —
        and turns west into its barrel above J4. IO25's haul now ends at R21 (1k series) instead of
        the barrel; R21.pin2 → J4.IO25, with R22 (4.7k) pulling that J4-side node to 3V3. */}
    <trace from="U1.IO25" to="R21.pin1" pcbPathRelativeTo="board" pcbPath={route(
        "U1.IO25",
        U1f.below("IO25", 1.65),                            // bottom lane
        { col: channel(-48.5, -45) },                       // drop between J3.IO33's column and the R field
        J4f.row("IO25", 1.2),                               // low band east under the LED field
        R21f.col("pin1"),                                   // rise into R21.pin1's column
        "R21.pin1",
    )} />
    {/* R21 series output → J4.IO25 barrel; R22 pull-up taps that same node and stitches to 3V3. */}
    <trace from="R21.pin2" to="J4.IO25" pcbPathRelativeTo="board" pcbPath={route(
        "R21.pin2",
        J4f.col("IO25"),                                    // E onto the barrel column, then S into it
        "J4.IO25",
    )} />
    <trace from="R22.pin2" to="R21.pin2" pcbPathRelativeTo="board" pcbPath={route("R22.pin2", "R21.pin2")} />
    <trace from=".R22 > .pin1" to="net.V3V3" />
    <trace from="U1.IO26" to="J4.IO26" pcbPathRelativeTo="board" pcbPath={route(
        "U1.IO26",
        U1f.below("IO26", 1.05),                            // middle lane
        J4f.col("IO26"),                                    // straight down the barrel column
        "J4.IO26",
    )} />
    <trace from="U1.IO27" to="J4.IO27" pcbPathRelativeTo="board" pcbPath={route(
        "U1.IO27",
        U1f.below("IO27", 0.45),                            // top lane
        J4f.col("IO27", 0.25),                              // just east of U10's pin barrels (the 0.15 floor)
        J4f.row("IO27", 1.5),                               // west into the barrel above J4
        "J4.IO27",
    )} />
    <trace from=".J4 > .GND" to="net.GND" />
    {/* IO23 — the switched moisture VCC's haul to J4 pin 7. IO23 is a north-row pad, so its
        pad-via drops STRAIGHT INTO the module interior on the 3V3 plane (inner1) — the west
        room of that plane, W of the centre GND thermal-pad array, is a clear channel. The line
        runs S off the pad into the interior, E under the body (S of the thermal pads, N of the
        south row), drops below the E GND corner pad, exits past the module's east column, and
        rides inner1 down the east flank (clear of the IO15 feed, which is on the bottom) into
        the south lane and the barrel. One via, never the antenna keepout — the interior IS the
        crossing. (The nearer top/bottom escapes are fenced by the boot wall and the pump comb.) */}
    <trace from="U1.IO23" to="J4.IO23" pcbPathRelativeTo="board" pcbPath={routeInner("inner1",
        "U1.IO23",
        { row: -6.6 },              // S off the pad into the interior's south strip (below the E GND corner pad's latitude; SDA/SCL are at y10.95, N — uncrossed)
        { col: -46 },               // E through the interior and clear past the module's east pad column
        { row: -29 },               // S the east flank on inner1 — the IO15 feed rides the bottom, so this lane is clear
        J4f.col("IO23"),
        "J4.IO23",
    )} />

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
    {/* Pump OUT comb — the four 0.4mm motor lines fan north-east into J13, whose label order
        already matches the pads' W→E order, so the rows just descend eastward (pitch 0.7) and
        every riser/drop pair stays y-disjoint. */}
    <trace from="U11.OUT2" to="J13.AM2" thickness="0.4mm" pcbPathRelativeTo="board" pcbPath={route(
        "U11.OUT2",
        J13f.row("AM2", -1.15),
        J13f.col("AM2"),
        "J13.AM2",
    )} />
    <trace from="U11.OUT1" to="J13.AM1" thickness="0.4mm" pcbPathRelativeTo="board" pcbPath={route(
        "U11.OUT1",
        J13f.row("AM1", -1.85),
        J13f.col("AM1"),
        "J13.AM1",
    )} />
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
    <trace from="U12.OUT2" to="J13.BM2" thickness="0.4mm" pcbPathRelativeTo="board" pcbPath={route(
        "U12.OUT2",
        J13f.row("BM2", -2.55),
        J13f.col("BM2"),
        "J13.BM2",
    )} />
    <trace from="U12.OUT1" to="J13.BM1" thickness="0.4mm" pcbPathRelativeTo="board" pcbPath={route(
        "U12.OUT1",
        J13f.row("BM1", -3.25),
        J13f.col("BM1"),
        "J13.BM1",
    )} />
    <trace from=".C19 > .pin1" to="net.V12" />
    <trace from=".C19 > .pin2" to="net.GND" />
    <trace from=".C20 > .pin1" to="net.V12" />
    <trace from=".C20 > .pin2" to="net.GND" />

    {/* RELAYS (J5): logic out to the two external opto-isolated relay modules + their V5 coil supply. */}
    {/* IO19 relay — now GATED by the U15 interlock (declared up top; truth table in the GAS block).
        U15 seats E of the WROOM (x-45.9) in the RXD↔SW1-boot gap, ON the old IO19→J5 corridor, so the
        haul splits into two clean halves and the module is never crossed:
          A ← IO19 — the WEST half, BOTTOM at y12 (the lane the direct haul already used).
          Y → J5.IO19 — the EAST half, BOTTOM: jog E off Y's north pad, drop to the y13 corridor
            (S of C4/U13, N of A's y12), E to U2's RESET/INTB pad-column gap, up it, onto J5.IO19's
            barrel (routeInner ends there — the barrel conducts every layer, no closing drill).
        VCC (pin5) / GND (pin3) auto-stitch to their planes; C23 decouples VCC just N of the gate. */}
    {U15El}{R24El}{C23El}
    <trace from="U1.IO19" to="U15.A" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO19",
        { row: 12 },
        U15f.col("A"),
        "U15.A",
    )} />
    <trace from="U15.Y" to="J5.IO19" pcbPathRelativeTo="board" pcbPath={routeInner("bottom",
        "U15.Y",
        U15f.east("Y", 0.4),        // jog E off the north pad onto the bottom, clear of GND's pad-via
        { row: 13.5 },              // the E-bound corridor: S of C4/U13, N of A's y12 haul + the Q2.C hop via
        U2f.col("RESET", -0.635),   // riser threads the RESET/INTB pad-column gap (both U2 rows align)
        { row: 29.5 },              // jog under J5's barrel row, over to the IO19 column
        J5f.col("IO19"),
        "J5.IO19",
    )} />
    <trace from=".U15 > .VCC" to="net.V3V3" />
    <trace from=".U15 > .GND" to="net.GND" />
    <trace from=".C23 > .pin1" to="net.V3V3" />
    <trace from=".C23 > .pin2" to="net.GND" />
    <trace from=".R24 > .pin2" to="net.GND" />
    <trace from="R24.pin1" to="U15.B" pcbPathRelativeTo="board" pcbPath={route(
        "R24.pin1",
        { row: 13.9 },              // S off pin1 into the flank lane
        { col: U15f.pin("B").x },   // E (over RXD on the bottom) to B's column, then N into B's S face
        "U15.B",
    )} />
    {/* IO2 relay — up the east corridor, split across layers: TOP from the pad through the
        module/U6 channel (the original col), jogging east at y9.3 (above U6's pads, below the
        IO0 lane) into the column just east of U13's pad rows, stopping short of the south row
        at y20.4; one via; BOTTOM east under U13's south row (0.2 south of the pad shadows),
        then up IO2's own barrel column — west of U2's pad block, east of IO19's y29.5 jog —
        entering the barrel from the south. Mixed-layer, so the path is assembled from the
        same frame-derived coordinates route() would use. */}
    <trace from="U1.IO2" to="J5.IO2" pcbPathRelativeTo="board" pcbPath={(() => {
        const col1 = channel(-47.055, -46.365) // the module-east / U6-west pad channel
        const col2 = U13f.pin("pin8").x + 0.635 // just east of U13's pad rows, west of C4
        const y0 = U1f.pin("IO2").y            // exit the pad east on its own row
        return [
            "U1.IO2",
            { x: col1, y: y0 },
            { x: col1, y: 9.3 },               // above U6's pads, below the IO0 approach lane
            { x: col2, y: 9.3 },
            { x: col2, y: 19.5 },              // short of U13's south pad row (its shadow now reaches y19.8 after U13's south slide)
            { x: col2, y: 19.5, via: true, toLayer: "bottom" } as const,
            { x: col2, y: 19.5 },
            { x: J5f.pin("IO2").x, y: 19.5 },  // bottom: east clear of U13's south-pad shadows
            "J5.IO2",
        ]
    })()} />
    <trace from=".J5 > .V5" to="net.V5" />
    <trace from=".J5 > .GND" to="net.GND" />


    {/* REEDS A (reservoir A) -> 0x20 GPB inputs; J6 sits above U2's north row. GPB0→RA1
        still steps east; the other three targets sit WEST of their pads, so the west-going
        lanes nest the other way: the FURTHEST west (GPB3→RA4) takes the lane closest to the
        pad row (J6y-3.4) and lanes step toward the barrels as the reach shortens (pitch 0.7).
        A west lane then passes only stubs east of its own start and only drops whose spans
        begin above it — no lane crosses a foreign stub or drop. */}
    <trace from="U2.GPB0" to="J6.RA1" pcbPathRelativeTo="board" pcbPath={route("U2.GPB0", J6f.row("RA1", -1.3), J6f.col("RA1"), "J6.RA1")} />
    <trace from="U2.GPB1" to="J6.RA2" pcbPathRelativeTo="board" pcbPath={route("U2.GPB1", J6f.row("RA2", -2.0), J6f.col("RA2"), "J6.RA2")} />
    <trace from="U2.GPB2" to="J6.RA3" pcbPathRelativeTo="board" pcbPath={route("U2.GPB2", J6f.row("RA3", -2.7), J6f.col("RA3"), "J6.RA3")} />
    <trace from="U2.GPB3" to="J6.RA4" pcbPathRelativeTo="board" pcbPath={route("U2.GPB3", J6f.row("RA4", -3.4), J6f.col("RA4"), "J6.RA4")} />
    <trace from=".J6 > .GND" to="net.GND" />

    {/* REEDS B (reservoir B + carbonator low/high) -> 0x21 GPB inputs; J7 sits below U3's
        south row and six staircases fan down (the doubled barrel pitch walks the targets
        east). The FURTHEST pair takes the lane closest to the pad row (J7y+4.7, 0.24 clear
        of the row's 2.3-long pads) and lanes step toward the barrels as reach shortens
        (pitch 0.7), so every barrel drop spans only lanes below its own and no lane crosses
        a foreign drop. GPB0's descent jogs east to -14.6 — off its own pad column, which
        J9.B's escape channel now occupies — threading between that channel and GPB1's
        column, and passing under RB2's lane start. */}
    <trace from="U3.GPB0" to="J7.RB1" pcbPathRelativeTo="board" pcbPath={route("U3.GPB0", U3f.below("GPB0", 0.35), { col: -14.6 }, J7f.row("RB1", 1.24), J7f.col("RB1"), "J7.RB1")} />
    <trace from="U3.GPB1" to="J7.RB2" pcbPathRelativeTo="board" pcbPath={route("U3.GPB1", J7f.row("RB2", 1.73), J7f.col("RB2"), "J7.RB2")} />
    <trace from="U3.GPB2" to="J7.RB3" pcbPathRelativeTo="board" pcbPath={route("U3.GPB2", J7f.row("RB3", 2.22), J7f.col("RB3"), "J7.RB3")} />
    <trace from="U3.GPB3" to="J7.RB4" pcbPathRelativeTo="board" pcbPath={route("U3.GPB3", J7f.row("RB4", 2.71), J7f.col("RB4"), "J7.RB4")} />
    <trace from="U3.GPB4" to="J7.CLO" pcbPathRelativeTo="board" pcbPath={route("U3.GPB4", J7f.row("CLO", 3.20), J7f.col("CLO"), "J7.CLO")} />
    <trace from="U3.GPB5" to="J7.CHI" pcbPathRelativeTo="board" pcbPath={route("U3.GPB5", J7f.row("CHI", 3.69), J7f.col("CHI"), "J7.CHI")} />
    <trace from=".J7 > .GND" to="net.GND" />

    {/* DISPLAY: the front 4.3" config panel's whole loom lands on J9 — RS485 signal AND the panel's
        7-36 V supply. The differential pair fans U7.A/B -> J9, tapped by the 120R termination (R6) and
        the SM712 ESD array (D1) at the cable entry; GND (pin3) is the RS485 reference, the panel's
        power return, and the cable earth all in one; V12 (pin4) feeds the panel its 12 V. Since V12
        is a top island (not a plane), J9.V12's barrel only picks it up where the pour physically covers
        it — the V12 rectangle (below) floods under the whole south edge, covering J9's V12 barrel. */}
    {/* The pair's pin order SWAPS between ends (A west of B at U7/R6, east of B at J9), so a
        planar route inside the pocket is impossible — B escapes it: east through the J9 GND/V12
        barrel channel, along the strip south of the connector row, into J9.B by its south face.
        A stays inside: down R6.pin1's column, west over the barrel row, into J9.A. R6 hangs
        directly under the pair (each pin a straight drop off its transceiver pad's column); D1
        stands rot 90 in the bay west of R6 — A/B pads on its north row, GND south toward J9 —
        taps A in the lane south of U7's pad row and drops B straight into J9.B's barrel. */}
    <trace from="U7.A" to="R6.pin1" pcbPathRelativeTo="board" pcbPath={route(
        "U7.A",
        U7f.col("A"),               // straight down; the closing jog lands inside pin1
        "R6.pin1",
    )} />
    <trace from="U7.B" to="R6.pin2" pcbPathRelativeTo="board" pcbPath={route(
        "U7.B",
        U7f.col("B"),
        "R6.pin2",
    )} />
    <trace from="U7.A" to="D1.A" pcbPathRelativeTo="board" pcbPath={route(
        "U7.A",
        U7f.above("A", 0.305),      // U7 sits rot 180: its local "above" is board-south — the lane under the pad row
        D1f.row("A"),               // D1 sits rot 90: its local "row" is the board column into A
        "D1.A",
    )} />
    <trace from="R6.pin1" to="J9.A" pcbPathRelativeTo="board" pcbPath={route(
        "R6.pin1",
        J9f.row("A", 2),            // west over the barrel row
        J9f.col("A"),
        "J9.A",
    )} />
    <trace from="R6.pin2" to="J9.B" pcbPathRelativeTo="board" pcbPath={route(
        "R6.pin2",
        R6f.below("pin2", 0.97),    // clear of the pad before the east jog
        { col: channel(J9f.pin("GND").x, J9f.pin("V12").x) }, // the GND/V12 barrel channel
        J9f.row("B", -2.2),         // the strip south of the connector row
        J9f.col("B"),
        "J9.B",
    )} />
    <trace from="D1.B" to="J9.B" pcbPathRelativeTo="board" pcbPath={route(
        "D1.B",
        J9f.row("B", 1.5),          // straight drop off B's column, into the barrel's north face
        "J9.B",
    )} />
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
    {/* D7 flyback clamp across the coil. pin1 (cathode) commons to the 5V plane at its own stitch
        via — the same node as U8._POS (which stitches there too), so no top tap is needed and the
        freewheel loop closes through the plane. pin2 (anode) → U8._NEG (Q1.C): _NEG sits N of the
        IO26 top trace (y-11.1, which runs between the two coil pads), so this tap drops onto the
        bottom at pin2, runs the clear column (x-35.1, E of D7's stitch via and the _POS via) N
        under IO26, and climbs a via into _NEG. */}
    {D7El}
    <trace from=".D7 > .pin1" to="net.V5" />
    <trace from="D7.pin2" to="U8._NEG" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "D7.pin2",
        { col: -35.1 },             // E of D7's stitch via + the _POS via, under the IO26 top trace
        "U8._NEG",
    )} />

    {/* GAS: ACEIRMC MQ-6 combustible / refrigerant-leak sensor, mounted low on the
        rear cabinet floor (catches dense R-600a pooling). 5 V heater supply. BOTH
        MQ-6 outputs swing 0-5 V; each is stepped to ~3.0 V by an on-board divider
        (R1/R2, R3/R4 above) before the ESP, since IO36/IO39 are NOT 5 V tolerant:
          AOUT (analog level)          -> R1/R2 -> IO39 (ADC1) — trend + warm-up sense
          DOUT (LM393 comparator trip) -> R3/R4 -> IO36       — the hardware gas trip
        Own connector, isolated from the SENSORS loom, so the fire-safety run is
        unambiguous. The divided DOUT node (R3.pin2/R4.pin1, ~3.0 V, the same node feeding IO36)
        drives the firmware-INDEPENDENT compressor interlock now ON the board: U15 (74LVC1G08 AND,
        declared up top, seated E of the WROOM) takes DOUT on B and the ESP compressor command IO19
        on A, and only its output Y reaches the relay (J5.IO19). Y = A·B, so:
          truth (IO19, gas) -> J5.IO19:  (on, clear) -> ON,  (on, GAS) -> OFF,  (off, *) -> OFF
        Fail-safe is THREE-WAY — B defaults LOW (R24 100k pulldown AT the gate-B pad), so a broken
        B-haul, an unpowered/unprogrammed ESP (A low), OR a gate with no VCC each leave the relay OFF
        (compressor off). Assumed polarity (to bench-confirm): DOUT HIGH = gas clear, relay active-HIGH.
        Two provisions cover the polarities that need bench truth:
          · R25 (0Ω) is the DOUT-polarity invert-select, in series from the divider node — default
            pass-through; if DOUT reads active-HIGH-on-gas, feed B from an inverted source in its place.
          · if the relay module is active-LOW, drop in the pin-identical 74LVC1G00 NAND (C12508) —
            same SOT-353 land, no layout change. */}
    <trace from="R1.pin2" to="R2.pin1" pcbPath={route("R1.pin2", "R2.pin1")} />
    <trace from="R3.pin2" to="R4.pin1" pcbPath={route("R3.pin2", "R4.pin1")} />
    <trace from=".R2 > .pin2" to="net.GND" />
    <trace from=".R4 > .pin2" to="net.GND" />
    <trace from="R2.pin1" to="U1.IO39" pcbPathRelativeTo="board" pcbPath={route(
        "R2.pin1",
        R2f.row("pin1", -1.16),     // the lane between R2's pads and R1's north pad
        { col: -60.8 },             // ascend east of the grid's east pad column
        U1f.below("IO39", 0.55),
        U1f.col("IO39", 0),
        "U1.IO39",
    )} />
    <trace from="R4.pin1" to="U1.IO36" pcbPathRelativeTo="board" pcbPath={route("R4.pin1", U1f.col("IO36", 0), "U1.IO36")} />
    <trace from="R1.pin1" to="J11.AOUT" pcbPathRelativeTo="board" pcbPath={route("R1.pin1", J11f.row("AOUT", 0), "J11.AOUT")} />
    <trace from="R3.pin1" to="J11.DOUT" pcbPathRelativeTo="board" pcbPath={route("R3.pin1", J11f.row("DOUT", 0), "J11.DOUT")} />
    <trace from=".J11 > .GND" to="net.GND" />
    {/* Interlock B-side (truth table above): the divided-DOUT node → R25 (0Ω) → the B-haul → U15.B,
        with R24 pulling B low at the gate. R25 sits in the clear S band E of the divider. Its DOUT
        tap runs the BOTTOM W to R4.pin1 (S of the divider midpoint pads); the B-haul runs the BOTTOM
        E along the south perimeter, clears the module's SE corner, climbs the WROOM's E flank (E of
        the east pads, W of U6), and pops to TOP just below B — never crossing a castellation rim. */}
    {R25El}
    {/* Both B-side hauls ride INNER2 (the 5V plane) across the south region — the emptiest layer here,
        so they clear the top/bottom fan + RS485 congestion, weaving only the sparse divider/GND-via
        pads. The lane sits at y-11 (S of the module pad shadow, N of the divider midpoint pads/GND
        vias). The B-haul climbs the flank on inner2 to y10 (S of the y11 wall's SCL/Q2.C), then pops
        to TOP into B (crossing the wall on top, E of IO2's -46.7 column). */}
    <trace from="R4.pin1" to="R25.pin1" pcbPathRelativeTo="board" pcbPath={(() => {
        const a = R4f.pin("pin1"), r = R25f.pin("pin1")
        const lane = -10.6
        return [
            "R4.pin1",
            { x: a.x, y: a.y, via: true, toLayer: "inner2" } as const,
            { x: a.x, y: a.y },
            { x: -62.3, y: a.y },                                    // E off R4.pin1 (past the same-net IO36 tap), clear of R4.pin2's GND-via column
            { x: -62.3, y: lane },                                   // N to the clear inner2 lane (N of the divider GND vias, S of the pad shadows)
            { x: r.x, y: lane },                                     // E along the lane to R25.pin1's column
            { x: r.x, y: r.y },                                      // S into R25.pin1
            { x: r.x, y: r.y, via: true, toLayer: "top" } as const,
            "R25.pin1",
        ]
    })()} />
    <trace from="R25.pin2" to="U15.B" pcbPathRelativeTo="board" pcbPath={(() => {
        const r = R25f.pin("pin2"), b = U15f.pin("B")
        const lane = -10.6          // inner2 E-bound lane (the LED feeds here ride the bottom, so inner2 is clear)
        const transX = -46.5        // inner2→bottom via column, midway between IO23's inner1 descent (-46.0) and IO15→R10 (-46.95)
        const flankX = -46.6        // bottom climb column: 0.15 off IO15→R10, 0.17 off R5.pin2, 0.20 off U6's shadow
        const popY = 9.85           // bottom→top, in the gap between IO2's y9.3 turn and SW1.D (10.45)
        return [
            "R25.pin2",
            { x: r.x, y: r.y, via: true, toLayer: "inner2" } as const,
            { x: r.x, y: r.y },
            { x: r.x, y: lane },                                     // N to the inner2 E-bound lane
            { x: transX, y: lane },                                  // E on inner2 to the transition column
            { x: transX, y: -8.0 },                                 // N into the clear top-gap (S of Q2.C, N of IO27)
            { x: transX, y: -8.0, via: true, toLayer: "bottom" } as const, // inner2→bottom, clear of IO15→R10
            { x: transX, y: -8.0 },
            { x: flankX, y: -8.0 },                                 // jog E to the climb column
            { x: flankX, y: popY },                                 // N up the flank on the BOTTOM, beside IO15→R10 (crosses R5/IO23/Q2.C off-layer)
            { x: flankX, y: popY, via: true, toLayer: "top" } as const, // bottom→top, S of SW1.D (10.45) / the wall
            { x: flankX, y: popY },
            { x: flankX, y: b.y },                                  // top up past the wall (E of IO2's -46.71 column)
            "U15.B",                                                 // W into B's pad
        ]
    })()} />

    {/* V12 decoupling. HF: two 0.1uF ceramics (C1/C2 aligned at y1.33) on the V12 island
        by the ULN/manifold block, snubbing the fast solenoid-turn-off edge. BULK: a
        470uF low-ESR electrolytic (C3, BOM 1) at the board centre between the two MCP
        stacks (U2 north, U3 south), west of the ULNs it feeds across the V12 island,
        soaking the inrush + flyback dump the ceramics can't. Every pin1 -> V12, pin2 ->
        GND plane — no routing, no vias, barrel pickup like every power pin; the top V12
        island floods the whole valve block. C3 is polarized: pin1 (+) is V12. */}
    <Cap name="C1" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={3.3} y={1.33} rot={270} side="W" />
    <Cap name="C2" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={0.4} y={1.33} rot={90} side="W" />
    <BulkCap name="C3" x={2.6} y={22.95} />
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
    {R21El}
    {R22El}
    {R26El}
    {R27El}
    <trace from=".R9 > .pin1" to="net.V3V3" />
    {/* 1-wire pull-up tap: R9.pin2 drops onto IO26 at the SENSORS connector, sharing the pad with
        the IO26 run to U1 — the external 4.7k sits right where the DS18B20 probe loom leaves the
        board. Exit pin2's west face, a 0.75 mm jog onto the column, straight south into the pad. */}
    <trace from="R9.pin2" to="J4.IO26" pcbPathRelativeTo="board" pcbPath={route(
        "R9.pin2",
        J4f.col("IO26", 0),
        "J4.IO26",
    )} />

    {/* ── Indicator LEDs — one labelled column on the west edge ──────────────────────
        Five rows at 2.5 pitch (LEDs x -39.75, their 470R C23179 resistors x -43.2), each
        named by a 1.4mm silk label east of its LED:
          ERR (red, IO15 / MTDO — runs high during boot: a glint at reset, harmless)
          RUN (green, IO12 / MTDI — heartbeat; wants low at boot, LED-to-GND only, never tied high)
          ACT (blue, IO14 — activity, not a strap)
          PWR (green, 3V3 rail)   5V (green, 5V rail)
        The firmware rows drive three otherwise-idle, boot-safe ESP GPIO, active-high to
        GND; the rail rows hang off their planes through the series R (PWR lit ⇒ 12 V in
        AND the 5V buck + 3V3 LDO are up — the board is alive before firmware runs).
        Ref-des silk is stripped from the LED imports (it collides at this pitch); the
        labels name the rows (see esp32-scope.md). The RO/DI bottom lanes thread the
        PWR/5V row gap (RS485 block above). */}
    {/* anode toward its R (outboard, -x). Every KT-0603 import carries pin1=anode on the
        +x pad, so all five seat rot 180 to swing the anode pad outboard-left. */}
    {D2El}
    {D3El}
    {D4El}
    {R10El}
    {R11El}
    {R12El}
    {D5El}
    {D6El}
    {R13El}
    {R14El}
    {/* The five LED names (ERR/RUN/ACT/PWR/5V) are drawn as KNOCKOUT badges — the label is the
        bare board showing through a filled silk background, D-shaped (flat west, round east),
        each background reaching west to wrap its LED (pads antipadded, no silk on copper). That
        needs a filled silk region with pad clearances, which circuit-json can't express, so the
        badges are emitted straight into F_SilkScreen by led-knockout.ts (injected in
        render-board.ts). The LED positions it wraps come from D2–D6 above; edit the text/geometry
        there. The LED footprint silk (diode glyph) is stripped from the imports so it doesn't sit
        under the fill. */}

    {/* firmware: GPIO -> R -> anode, cathode -> GND */}
    {/* LED feeds — the top band south of U1 is the sensor comb's, so all three ride the BOTTOM as
        nested pad-via L's; the GPIO→colour map is firmware's, so pins are assigned by geometry:
        IO15 comes down U1's east flank (between the GND corner pad and R5.pin2) and takes the
        top row, entering R10.pin1 by its north face (IO15 runs high during boot — a red glint
        at reset, harmless on a status LED); IO12/IO14 drop south off the pad row and nest
        into R11/R12 by their west faces — east pin to upper row, so nothing crosses. */}
    <trace from="U1.IO15" to="R10.pin1" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO15",
        { col: -46.99 },        // east-flank lane, hugging U1's east pads — leaves the U6 side of the flank for the interlock B-haul
        { row: -14.6 },         // north of the R row, over to pin1's column
        R10f.col("pin1"),
        "R10.pin1",
    )} />
    <trace from="R10.pin2" to="D2.pin1" pcbPathRelativeTo="board" pcbPath={route("R10.pin2", "D2.pin1")} />
    <trace from=".D2 > .cathode" to="net.GND" />
    <trace from="U1.IO12" to="R11.pin1" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO12",
        R11f.row("pin1"),
        "R11.pin1",
    )} />
    <trace from="R11.pin2" to="D3.pin1" pcbPathRelativeTo="board" pcbPath={route("R11.pin2", "D3.pin1")} />
    <trace from=".D3 > .cathode" to="net.GND" />
    <trace from="U1.IO14" to="R12.pin1" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U1.IO14",
        R12f.row("pin1"),
        "R12.pin1",
    )} />
    <trace from="R12.pin2" to="D4.pin1" pcbPathRelativeTo="board" pcbPath={route("R12.pin2", "D4.pin1")} />
    <trace from=".D4 > .cathode" to="net.GND" />
    {/* rails: plane -> R -> anode, cathode -> GND (R/LED pads auto-stitch to their planes) */}
    <trace from=".R13 > .pin1" to="net.V3V3" />
    <trace from="R13.pin2" to="D5.pin1" pcbPathRelativeTo="board" pcbPath={route("R13.pin2", "D5.pin1")} />
    <trace from=".D5 > .cathode" to="net.GND" />
    <trace from=".R14 > .pin1" to="net.V5" />
    <trace from="R14.pin2" to="D6.pin1" pcbPathRelativeTo="board" pcbPath={route("R14.pin2", "D6.pin1")} />
    <trace from=".D6 > .cathode" to="net.GND" />

    {/* ── USB-C programming block ─────────────────────────────────────────────────────
        USB-C receptacle (J14, west edge above the WROOM, opening flush to the west board edge) +
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
    <Cap name="C21" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-57.25} y={25.05} rot={180} side="N" />
    {/* EN branch: U13.DTR -> R17 -> Q2.base; U13.RTS -> Q2.emitter; Q2.collector -> EN; SW2 */}
    {R17El}
    {Q2El}
    {SW2El}
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
    {/* The programming UART, on the BOTTOM — the pair anti-nests (TXD west pad → the east
        target, RXD east pad → the west target), so RXD detours around TXD through the module's
        NE window (the pad-free band between IO2's shadow and the north row's) while TXD takes
        the short nested Z west under R16 and the shell pill into IO3. */}
    <trace from="U13.TXD" to="U1.IO3" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "U13.TXD",
        { row: 13.7 },               // south past the comb's band, under R16's shadow
        { col: -58.3 },              // between R16.pin1's shadow and its J14 route's column
        { row: 10.45 },              // the low tier, under EH2's pill
        "U1.IO3",
    )} />
    <trace from="U13.RXD" to="U1.IO1" pcbPathRelativeTo="board" pcbPath={(() => {
        // Bottom out of the pad block and east past TXD's column; the pump comb owns the bottom's
        // y10.9-12.1 band clear across, so the crossing vias to the TOP at 12.55 (above IO19's
        // lane) and descends the D_NEG/pin7 channel's east side — the boot wall ends at IO0, so
        // the top is open here — then west through the NE window into IO1's pad, no second via.
        const rxd = U13f.pin("RXD")          // rides U13 (moved E/S) — the via is on the pad, not a hand literal
        const hop = { x: -47.3, y: 12.55 }
        return [
            "U13.RXD",
            { x: rxd.x, y: rxd.y, via: true, toLayer: "bottom" } as const,
            { x: rxd.x, y: rxd.y },
            { x: rxd.x, y: 19.0 },           // drop below U13's (moved) south pad shadows
            { x: hop.x, y: 19.0 },
            hop,
            { ...hop, via: true, toLayer: "top" } as const,
            hop,
            { x: hop.x, y: 6.55 },
            { x: U1f.pin("IO1").x, y: 6.55 },
            "U1.IO1",
        ]
    })()} />
    {/* Auto-reset cross-coupled pair (see block header for the truth table): the six internal
        DTR/RTS connections, then each collector's reach — Q3 down the far-west lane into U1's
        north-edge corridor to IO0; Q2 around the far-west flank to EN on the south edge. */}
    {/* base nodes: each transistor's base to the near (south) pin of its base resistor */}
    <trace from="Q2.B" to="R17.pin1" pcbPathRelativeTo="board" pcbPath={route(
        "Q2.B",
        R17f.row("pin1"),            // rise B's column, between R17's pads, west into pin1
        "R17.pin1"
    )} />
    <trace from="Q3.B" to="R18.pin1" pcbPathRelativeTo="board" pcbPath={route("Q3.B", "R18.pin1")} />
    {/* Cross-coupled pair. The two trunks leave U13 on OPPOSITE sides so they never
        cross: RTS exits east and runs the high rail to R18.pin2, then hops to Q2.E on the
        bottom (routeBottom, west past R17's column and down to the emitter row); DTR exits
        west and runs the lane between C21/Q3's pad tops and U13's dropped north row (y26.77)
        to Q3.E, which links up to R17.pin2 along its row. */}
    <trace from="U13.RTS" to="R18.pin2" pcbPathRelativeTo="board" pcbPath={route(
        "U13.RTS",
        { row: 27.7 },               // rise into the clear band between U13's north pads and the tacts' south pads
        { col: -60.5 },              // west under the tacts, east of SW2's west pad and R18
        { row: 29.5 },               // up the R18/SW2 flank to R18.pin2's level
        "R18.pin2")
    } />
    <trace from="R18.pin2" to="Q2.E" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "R18.pin2",
        { col: -63.0 },              // out the pad's west side, between R17's column and Q3
        { row: 24.75 },              // the lane below the B/E pad row, clear of B's and C's shadows
        { col: Q2f.pin("E").x },     // west under the pad row, rising only at E's own column
        "Q2.E"
    )} />
    <trace from="U13.DTR" to="Q3.E" pcbPathRelativeTo="board" pcbPath={route(
        "U13.DTR",
        { row: 25.3 },               // drop below U13's (moved) north-pad shadow
        { col: -55.15 },             // west to just east of C21 (clears C21.pin1 by 0.2+)
        { row: 23.9 },               // duck below C21's band (starts 24.375)
        { col: -59.7 },              // west, clear of C21, east of Q3.B's column
        Q3f.col("E", -1),            // rise into the Q3.B/Q3.C gap — the proven Q3.E approach
        Q3f.row("E"),
        "Q3.E"
    )} />
    <trace from="Q3.E" to="R17.pin2" pcbPathRelativeTo="board" pcbPath={route(
        "Q3.E",
        { col: -63.05 },             // jog west off the pad, clear of R18's pin1 column
        R17f.row("pin2"),            // rise, east along R17's row into pin2
        "R17.pin2"
    )} />
    {/* Q2's collector reach to EN — off the antenna keepout entirely (the far-west flank crossed the
        WROOM antenna box). Q2.C drops onto inner2 (the 5V plane, empty here but for SCL) at its own
        pad, runs the clear lane north of SCL east to the one open top window — between the IO2 riser
        (x−43.17) and U6 (x−35.75) — hops up over the stacked wall (comb y11–12 · SCL · SDA, all on
        other layers) and back to inner2 south of it, descends the Q1.C/C6 gap (0.93 mm), and runs west
        under the module (north of the south-pad row, clear of IO23 on inner1) up into EN from the
        north. C12's RC feed still enters EN from the south. Board-absolute lanes: they thread
        board-fixed copper (SCL, the comb, the module pads), so they anchor to no part. */}
    <trace from="Q2.C" to="U1.EN" pcbPathRelativeTo="board" pcbPath={(() => {
        const c = Q2f.pin("C"), en = U1f.pin("EN")
        const eastLane = 11.75       // inner2, N of SCL (10.95), under the comb (11–12, bottom): the clear east run
        const cross = -39.37         // top-hop + descent column: clear top window, and the Q1.C↔C6 gap (0.93 mm) below
        const viaN = 12.8            // via up, N of the comb's north row (IO19, y12)
        const viaS = 10.0            // via down, S of SCL (10.95)
        const underLane = -7.4       // inner2, under the module: N of the south pads (−7.95), clear of IO23 (inner1, −6.6)
        return [
            "Q2.C",
            { x: c.x, y: c.y, via: true, toLayer: "inner2" } as const,    // onto inner2 at the pad (shares SW2's drill)
            { x: c.x, y: c.y },
            { x: c.x, y: eastLane },                                      // down Q2.C's column to the east lane
            { x: cross, y: eastLane },                                    // east on empty inner2, N of SCL
            { x: cross, y: viaN },                                        // rise N of the comb for a clean via
            { x: cross, y: viaN, via: true, toLayer: "top" } as const,    // up to top — the clear window
            { x: cross, y: viaN },
            { x: cross, y: viaS },                                        // top crosses S over comb / SCL / SDA
            { x: cross, y: viaS, via: true, toLayer: "inner2" } as const, // back to inner2, S of SCL
            { x: cross, y: viaS },
            { x: cross, y: underLane },                                   // descend the Q1.C/C6 gap
            { x: en.x, y: underLane },                                    // west under the module to EN's column
            { x: en.x, y: underLane, via: true, toLayer: "top" } as const,// up to top, N of the pad
            { x: en.x, y: underLane },
            "U1.EN",                                                      // top stub S into EN (C12 enters from the S)
        ]
    })()} />
    <trace from="Q3.C" to="U1.IO0" pcbPathRelativeTo="board" pcbPath={route(
        "Q3.C",
        { col: channel(U1f.pin("IO1").x, U1f.pin("IO22").x) },   // drop the west lane, clear of the CC/J14 block
        U1f.above("IO0", 0.475),                                 // corridor centred in the lane between U1's tall north pads and the CC2 dip
        "U1.IO0",
    )} />
    {/* R8's pull-up reach — R8 sits S of U13, just W of IO0's column (it vacated its old -46 seat for
        the U15 interlock): pin1 drops S off its pad into the clear band above the pump comb, then E to
        IO0's column and straight down into the pad (all IO0 net, so the boot wall it meets is same-net). */}
    <trace from="R8.pin1" to="U1.IO0" pcbPathRelativeTo="board" pcbPath={route(
        "R8.pin1",
        { row: 13.5 },               // drop S off pin1, above the pump-comb band
        { col: U1f.pin("IO0").x },   // W to IO0's column
        "U1.IO0",
    )} />
    {/* Manual BOOT (IO0) / RESET (EN) — each tact connects one diagonal pad pair (see the
        placement block). SW1's boot line exits pin4 (NE) east over J5's body, drops the J5
        GND/V5 ring channel, jogs into U13's pin9/pin10–pin7/pin8 column gap (east of the
        D+/D-/DTR rivers, west of the IO2 column), then hops to the BOTTOM at y10.45 — over the
        pad row, under the pump comb, below RXD's bottom column — runs west to IO0's column, and
        rises by its own via just north of IO0's pad. SW2's reset line hops to the bottom at pin3 (NW), drops straight down its own
        column east of R18's seat, crosses under the collector row, and rises into Q2.C's pad
        via from the south. */}
    <trace from="SW1.pin4" to="U1.IO0" pcbPathRelativeTo="board" pcbPath={(() => {
        const p4 = SW1f.pin("pin4")
        const ringCol = channel(J5f.pin("GND").x, J5f.pin("V5").x)  // the J5 GND/V5 ring channel
        const col = U13f.pin("pin8").x - 0.635  // the pin9/pin10 = pin7/pin8 gap column
        const io0 = U1f.pin("IO0")
        const lane = 10.45                      // bottom lane: over the pad row, under the combs
        return [
            "SW1.pin4",
            { x: ringCol, y: p4.y },
            { x: ringCol, y: 29.3 },            // below the barrel rings, above U13's north pads
            { x: col, y: 29.3 },
            { x: col, y: lane },
            { x: col, y: lane, via: true, toLayer: "bottom" } as const,
            { x: col, y: lane },
            { x: io0.x, y: lane },
            { x: io0.x, y: lane, via: true, toLayer: "top" } as const,
            { x: io0.x, y: lane },
            "U1.IO0",
        ]
    })()} />
    <trace from=".SW1 > .pin1" to="net.GND" />
    <trace from="SW2.pin3" to="Q2.C" pcbPathRelativeTo="board" pcbPath={routeBottom(
        "SW2.pin3",
        { col: -57.25 },             // east off the pad, down the C21 pad-pair channel
        { row: 22.7 },               // under the collector row, over J14's shell legs
        Q2f.row("C"),                // up into the pad via from the south
        "Q2.C",
    )} />
    <trace from=".SW2 > .pin2" to="net.GND" />

    {/* ── M3 mounting holes, one per corner, electrically isolated: no net attaches, and
        every plane antipads the barrel. The screws drive into printed PETG bosses (the
        tray/enclosure) — the bottom face seats on plastic; the head and any washer seat on
        the top face. A symmetric rectangle: every hole is inset 3.5 mm from both of its board
        edges, so the four stay centred on the board and clear of the nearest connector at
        each corner. 3.2 mm hole / 4.0 mm pad (r 2.0): an M3 screw head (socket-cap or pan,
        ~5.5 mm ⌀ → r ~2.75) overhangs the pad by ~0.75 mm, and an M3 hex standoff (5.5 mm A/F,
        r ~3.2) or washer (~7 mm ⌀, r ~3.5) more — so the nearest corner connector housing is
        held ≥2 mm off the pad edge (the seated head + standoff clear it), the tightest being
        J8→MH3 and J11→MH4. The connector audit (connector-audit.ts) measures this each render.
        fastenerAnnulus (parsed by pour-clearance.ts, like the pours' netClearance) holds every
        top-face pour ≥3.75 mm (washer r ~3.5 + 0.25) off each hole centre — the V12 island at
        MH2/MH3 is the pour this cuts. */}
    <platedhole name="MH1" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" fastenerAnnulus="3.75mm top" pcbX={-64.5} pcbY={33.0} />
    <platedhole name="MH2" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" fastenerAnnulus="3.75mm top" pcbX={13.5} pcbY={33.0} />
    <platedhole name="MH3" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" fastenerAnnulus="3.75mm top" pcbX={13.5} pcbY={-33.3} />
    <platedhole name="MH4" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" fastenerAnnulus="3.75mm top" pcbX={-64.5} pcbY={-33.3} />

    {/* Global fiducials — three non-collinear 1 mm bare-copper dots (2 mm mask opening) for the
        assembler's vision system to register the panel. FID1 (SE) + FID2 (NE) sit INSIDE the V12
        top island: the pour voids 0.5 mm around each netless dot (its netClearance), so their
        nearest copper is the V12 pour edge at ~0.5 mm — below JLC's ideal 1 mm keep-ring but a
        deliberate DFM tradeoff on a board with no clear east-corner laminate (the island floods
        x[-31.75,16.5]). FID3 (SW) sits on clear west laminate near MH4. Not a BOM part (no source
        component, no JLCPCB #); the paste aperture the native fiducial carries is harmless on a
        no-component dot. */}
    <fiducial name="FID1" padDiameter="1mm" pcbX={15} pcbY={-28.3} />
    <fiducial name="FID2" padDiameter="1mm" pcbX={16} pcbY={27.5} />
    <fiducial name="FID3" padDiameter="1mm" pcbX={-59.5} pcbY={-34.8} />

    {/* Board identity nameplate — the soda-glass brand mark (ios/AppIcon.svg,
        monocolor silk via logo.ts) beside the two-line name, over MACHINE and the
        two-line version stamp, filling the bay north of U9 (C10/C11 column west,
        the R10-R12 bank east, the IO25/26/27 top runs north). Every element sits
        on bare laminate except MACHINE's east end, which crosses the IO25 drop
        column as mask-covered ink — same call as R4's label; the IO12/IO14 runs
        under the bay are bottom copper. The version is the firmware scheme
        (firmware/pre_build.py): commit date + short SHA, a trailing `+` from
        uncommitted edits — a pure function of the commit, naming which source
        tree a fabbed board came from. */}
    {logoRoutes(-52.9, -13.6, 3).map((route, i) => (
      <silkscreenpath key={`logo${i}`} strokeWidth="0.15mm" route={route} />
    ))}
    <silkscreentext text="HOME" fontSize="1.4mm" anchorAlignment="center" pcbX={-49.2} pcbY={-12.75} />
    <silkscreentext text="SODA" fontSize="1.4mm" anchorAlignment="center" pcbX={-49.2} pcbY={-14.55} />
    <silkscreentext text="MACHINE" fontSize="1.4mm" anchorAlignment="center" pcbX={-50.2} pcbY={-16.35} />
    <silkscreentext text={ID.date} fontSize="0.8mm" anchorAlignment="center" pcbX={-49.2} pcbY={-18.05} />
    <silkscreentext text={ID.rev} fontSize="0.8mm" anchorAlignment="center" pcbX={-49.2} pcbY={-19.15} />

    {/* Power pours — FOUR layers, top->bottom: top (signals + the V12 island), 3V3 (inner1),
        5V (inner2), GND (bottom). 3V3/5V/GND are full-flood planes; each pin commons to its
        plane at its through-hole barrel or an auto-stitched via (SMD). V12 is a top-copper
        island over the valve/buck/driver block (the rectangle below): top-layer 12V pads sit
        directly on it, through-hole 12V pins pick it up at the barrel. The SDA/SCL bus traces
        ride inner1/inner2 (routeInner, I2C block above); each plane carves clearance around
        its bus trace and its via barrels like any other foreign copper. */}
    {/* J10 12V input protection wiring. The screw-terminal barrel lands on net.V12IN (the RAW inlet,
        upstream of the FET); a wide (1.6mm) top stub carries the full ~3.3A board peak from the
        barrel to Q4's DRAIN. Q4 (AO3407 P-FET) passes it to the V12 island at its SOURCE — the island
        floods the source pad directly (unlimited pour copper), so the source→island tie needs no
        trace. Body-diode orientation is the crux: a P-channel body diode points DRAIN→SOURCE, so with
        drain=input / source=load it conducts input→load in normal polarity (then the channel enhances,
        Vgs≈-12V within the ±20V rating) and BLOCKS load→input under reverse polarity (body diode
        reverse-biased) — the board sees no current. R23 (100k) pulls the GATE to GND so an unplugged
        terminal can't float it into an undefined state; D9 (Zener 15V) clamps Vgs (cathode→source,
        anode→gate) short of the ±20V gate-oxide rating. D8 (SMAJ15A) clamps the surge the board sees,
        island→GND at the inlet (24.4V clamp < C3's 25V). The V12 island voids around the V12IN barrel,
        the stub, and every foreign VGATE/GND pad, exactly as it does for the signal fan-out. */}
    <trace from=".J10 > .V12" to="net.V12IN" />
    <trace from=".Q4 > .D" to="net.V12IN" />
    <trace from="Q4.D" to="J10.V12" thickness="1.6mm" pcbPathRelativeTo="board" pcbPath={route("Q4.D", { col: 9.0 }, "J10.V12")} />
    <trace from=".Q4 > .S" to="net.V12" />
    <trace from="Q4.G" to="R23.pin1" pcbPathRelativeTo="board" pcbPath={route("Q4.G", { col: 4.3 }, { row: R23f.pin("pin1").y }, "R23.pin1")} />
    <trace from="R23.pin1" to="D9.pin2" pcbPathRelativeTo="board" pcbPath={route("R23.pin1", "D9.pin2")} />
    <trace from=".R23 > .pin2" to="net.GND" />
    <trace from=".D9 > .pin1" to="net.V12" />
    <trace from=".D8 > .pin1" to="net.V12" />
    <trace from=".D8 > .pin2" to="net.GND" />
    {/* V12 top island — a plain rectangle over the whole 12 V region (pump drivers, ULN commons +
        manifolds, buck, bulk cap), x[-31.75,26.5] running the FULL board depth y[-38.5,36.5]. V12 is
        an ISLAND, not a plane, so a barrel only picks it up where the pour physically covers it — and
        a connector's barrel row (J7's reeds, J9's own pins) is a wall of near-touching antipads that
        no pour can thread. So instead of reaching for each south-edge 12 V barrel with a finger (which
        those walls chop into disconnected scraps), the sheet just swallows them: because it fills the
        strip BELOW the barrel rows too (down to y -38.5), V12 flows UNDER every connector and around
        the walls, reaching J10's inlet barrel (x 16) and J9's display-feed barrel (x -16.5) alike.
        One dumb connected rectangle, 0.5 mm off the north/east/south edges; its west edge x -31.75
        clears the LED column, U6/C6/U8, and the nameplate, while the buck cluster's pins (U10's
        column at x -30.8, C15's V12 pad) sit fully inside it — a pour boundary through a pad is a
        DRC fault, so the edge threads BETWEEN pad columns. Everything foreign inside it (the
        barrels, the MCPs, BT1, the signal fan-out, the SE mounting hole) is just a hole in
        the sheet. */}
    <copperpour name="V12ISLAND" layer="top" connectsTo="net.V12" netClearance="0.5mm from V3V3, V5, SDA, SCL"
      outline={[{ x: -31.75, y: 36.0 }, { x: 16.5, y: 36.0 }, { x: 16.5, y: -35.8 },
                { x: -31.75, y: -35.8 }]} />
    <copperpour name="V3V3PLANE" layer="inner1" connectsTo="net.V3V3" boardEdgeMargin="0.5mm" />
    <copperpour name="V5PLANE" layer="inner2" connectsTo="net.V5" boardEdgeMargin="0.5mm" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" boardEdgeMargin="0.5mm" />
  </board>
)
