/**
 * esp32-mcp-mini — the controller carrier. Off-the-shelf modules plug into
 * 2.54 mm header sockets; the board is the interconnect, and every off-board
 * interface lands on a labeled edge connector (J1-J11). Footprint geometry
 * lives in ./carrier_parts; placement + routing are declared here.
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
 * buck/driver block (the L outline at the pours): top-layer 12V pads sit on it directly,
 * through-hole 12V pins pick it up at the barrel. Point-to-point signals route on ALL six
 * layers: `autorouter.viaMode="through-hole"` (below) tells the homesodamachine capacity-autorouter
 * fork to use the inner copper but make a mesh node via-capable only where the full board column
 * is clear, and emit those vias top<->bottom (JLCPCB drills through-holes only, no blind/buried —
 * see patches/capacity-autorouter-fork/). Each poured plane carves clearance around the inner-layer
 * signals crossing it and every via is a manufacturable through-hole; the DRC (clearance.ts)
 * proves no blind/buried via and no barrel crossing foreign copper survives.
 *
 * `schematicDisabled` on the board: this is a fab-only PCB (its canonical "schematic" is
 * esp32-pinout.mmd). tscircuit's schematic-trace-solver — NOT the PCB autorouter — hangs on
 * this dense layout whenever a net is added; the capacity-autorouter handles the PCB fine.
 * Disabling the schematic removes the hang and speeds every render; the gerbers are unaffected.
 *
 * `autorouter.traceClearance` (the homesodamachine core patch feeds it to the capacity
 * solver's obstacle margin) is the packing target, and its realized floor is counter-
 * intuitive: too HIGH and the router can't meet it in the dense pump-driver comb, crams the
 * leftover space, and the realized min copper gap COLLAPSES. On this board (164 vias) 0.15
 * holds a 0.115 mm floor; keep it in the ~0.12–0.15 low zone, don't raise it toward 0.25+.
 * That 0.115 floor is a via hugging the WROOM/pump-driver pads (U12) — traceClearance won't
 * beat it; only spreading the comb will (all six layers already carry signal). The web
 * viewer's board chip reports this floor live (clearance.ts -> picks.json).
 */
import { at, Cap, Res, Jst, ulnOUT } from "./carrier_parts"
import { Uln2803, Mcp23017, Ds3231Smd, Thvd1426, Sm712, Buck5, Buzzer, CoinHolder, BulkCap, Npn } from "./pcba_parts"
import { AMS1117_3_3 } from "./imports/AMS1117_3_3"
import { KF301_5_0_2P } from "./imports/KF301_5_0_2P"
import { DRV8870DDAR as Drv8870 } from "./imports/DRV8870DDAR"
import { boardVersionParts } from "./board-version"
import { logoRoutes } from "./logo"
import { ESP32_WROOM_32E_N4 as Wroom } from "./imports/ESP32_WROOM_32E_N4"
import { KT_0603R as LedRed } from "./imports/KT_0603R"
import { KT_0603G as LedGrn } from "./imports/KT_0603G"
import { Blue_light_0603 as LedBlu } from "./imports/Blue_light_0603"
import { CH340C } from "./imports/CH340C"
import { TYPE_C_31_M_12 as UsbC } from "./imports/TYPE_C_31_M_12"
import { USBLC6_2SC6 as Usblc6 } from "./imports/USBLC6_2SC6"
import { TS_1187A_B_A_B as Tact } from "./imports/TS_1187A_B_A_B"
import { S8050_J3Y_RANGE_200_350_ as S8050 } from "./imports/S8050_J3Y_RANGE_200_350_"

// Identity stamp version (commit date + short SHA), computed once per render.
const ID = boardVersionParts()

export default () => (
  <board layers={6} schematicDisabled outline={[{ x: -67.5, y: -38.57 }, { x: 34.9, y: -38.57 }, { x: 34.9, y: 37 }, { x: -67.5, y: 37 }]} minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" pcbStyle={{ silkscreenFontSize: "0.8mm" }} autorouter={{ traceClearance: 0.15, viaMode: "through-hole" }}>
    {/* DS3231SN RTC + CR2032 backup, east of the ESP. U6 (the SOIC) sits high with its
        0.1uF decoupler (C6) to its west and the buzzer column below it; the 20 mm THT coin
        base (BT1) is the bulk to U6's east. + is pin1 (the silk-marked post -> VBAT), - is
        pin2 (-> GND); the cell is retained by the molded base, not SMT clips. */}
    <CoinHolder name="BT1" x={-18.6} y={-2} />
    <Ds3231Smd name="U6" x={-38.05} y={7.1} />
    <Cap name="C6" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-44} y={8} rot={90} />
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
    <Wroom name="U1" pcbX={-56.45} pcbY={0} pcbRotation={0} />
    {/* WROOM support south of U1: the EN power-on RC (R7 + C12) stacked at the far-west,
        hard by U1's EN pin so the EN trace stays short; the supply decouplers C10 + C11
        share the lane just east of them. */}
    <capacitor name="C12" capacitance="1uF" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C15849"] }} {...at(-63.5, -13.5)} />
    <resistor name="R7" resistance="10k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C25804"] }} {...at(-63.5, -17.5)} />
    <Cap name="C10" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-58.5} y={-14.0} rot={90} />
    <Cap name="C11" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-53.5} y={-14.0} rot={90} side="E" />
    <resistor name="R8" resistance="10k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C25804"] }} pcbRotation={90} {...at(-44, 12)} />
    {/* RS-485 to the front display (J9). THVD1426 auto-direction transceiver (U7):
        no host DE/RE — /RE tied low (always receive), /SHDN tied high (always on),
        only D (from ESP TX) and R (to ESP RX) are driven. R6 = 120R line termination
        across A/B; D1 = SM712 ESD array at the J9 cable entry; C7 decouples VCC. */}
    <Thvd1426 name="U7" x={-50} y={-22} />
    <resistor name="R6" resistance="120" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22787"] }} {...at(-44.6, -22.55)} />
    <Sm712 name="D1" x={-44} y={-25.95} rot={0} />
    <Cap name="C7" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-50} y={-17} rot={90} side="E" />
    {/* On-board supplies. U10 = K7805 (12V->5V, 2A) SIP module (pin1 Vin / pin2 GND / pin3
        +Vo), 10uF input + 22uF output cap. U9 = AMS1117-3.3 (C6186, SOT-223 LDO) makes 3V3
        from the 5V rail: VIN off V5, VOUT1 + VOUT2 (tab) to 3V3, GND to the bottom plane;
        the SMD pads auto-stitch to their planes. Each cap flanks the LDO at the pin of its
        own net: C13 (10uF V5 input) hard by VIN on the east, C14 (22uF 3V3 output) under the
        VOUT tab on the west — so each closes a tight local loop like C15/C16 flank U10. */}
    <AMS1117_3_3 name="U9" pcbRotation={0} {...at(-10.22, 28.45)} />
    <Cap name="C13" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-3.0} y={30.75} rot={0} side="S" />
    <Cap name="C14" capacitance="22uF" footprint="0805" jlcpcb="C45783" x={-13.5} y={23.4} rot={0} side="S" />
    <Buck5 name="U10" x={22.81} y={-25.95} />
    <Cap name="C15" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={13.88} y={-26.9} rot={0} side="S" />
    <Cap name="C16" capacitance="22uF" footprint="0805" jlcpcb="C45783" x={30.66} y={-25.65} rot={270} side="E" />
    {/* Pump drivers, in the second row behind the top-edge connectors: one DRV8870 H-bridge per peristaltic flavor
        pump (Kamoer KPHM400-SW, 12V brushed DC, 0.8A at full speed per the datasheet — PWM'd well below that at the
        1:20 dispense ratio; prime/clean is where it hits 0.8A), 45V/3.6A SMD with internal freewheeling +
        OCP/OTP/UVLO. VM->12V (the top SMD pad lands directly on the V12 island), GND/PAD->GND,
        ISEN->GND, VREF->3V3, IN1/IN2 from the ESP north-edge pins, OUT1/OUT2 to PUMPS. 10uF +
        0.1uF VM decoupling per chip. */}
    <Drv8870 name="U11" pcbX={-27.95} pcbY={22} pcbRotation={0} />
    <Cap name="C17" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-31.6} y={15.65} rot={0} side="S" />
    <Cap name="C18" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-26.55} y={15.7} rot={0} side="S" />
    <Drv8870 name="U12" pcbX={-21} pcbY={22} pcbRotation={0} />
    <Cap name="C19" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-21.05} y={15.7} rot={0} side="S" />
    <Cap name="C20" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-16} y={15.7} rot={0} side="S" />
    <Mcp23017 name="U2" x={4.48} y={18.1} addr="0x20" rot={270} />
    <Mcp23017 name="U3" x={6.53} y={-21.35} addr="0x21" rot={90} />
    <Uln2803 name="U4" x={18.48} y={8.45} />
    <Uln2803 name="U5" x={18.58} y={-8.35} />
    <Buzzer name="U8" x={-36.3} y={-8.4} />
    <Npn name="Q1" x={-35.8} y={-2.35} />
    <Res name="R5" resistance="1k" footprint="0603" jlcpcb="C21190" x={-40.7} y={-1.05} rot={180} side="N" />
    {/* Manifolds sit immediately right of their ULNs so OUT1-8/COM are straight shots
        across (J1 pin order = ULN output pin order, reversed). */}
    <Jst name="J1" x={28.28} y={12.45} count={9} labels={[...ulnOUT].reverse()} rot={90} label="MANIFOLD A" side="E" />
    <Jst name="J2" x={28.33} y={-9.7} count={6} labels={["COM", "FAN", "OUT4", "OUT3", "OUT2", "OUT1"]} rot={90} label="MANIFOLD B" side="E" />
    {/* Pump-motor outputs — one PUMPS connector. Pin order is AM2/AM1/BM2/BM1, left to
        right, matching the drivers' OUT pads west-to-east (U11 then U12) so each pair
        combs straight up to its own side of J13 with no crossing. */}
    <Jst name="J13" x={-22.78} y={31} count={4} labels={["AM2", "AM1", "BM2", "BM1"]} rot={0} label="PUMPS" side="N" />
    <Jst name="J3" x={-30.5} y={-32} count={4} labels={["GND", "V5", "IO35", "IO33"]} rot={0} label="FAUCET" side="S" />
    <Jst name="J4" x={-14.6} y={-32} count={6} labels={["GND", "V5", "IO25", "IO26", "IO27", "3V3"]} rot={0} label="SENSORS" side="S" />
    {/* RELAYS — logic-level control out to the two external opto-isolated relay modules
        (compressor AC switch + carbonator diaphragm-pump 12V gate, both off-board). IO23/
        IO19 drive them; V5 feeds the relay modules' coil/opto supply; GND returns. */}
    <Jst name="J5" x={-36.18} y={31} count={4} labels={["GND", "V5", "IO23", "IO19"]} rot={0} label="RELAYS" side="N" />
    <Jst name="J6" x={9.23} y={31} count={5} labels={["GND", "RA4", "RA3", "RA2", "RA1"]} rot={0} label="REEDS A" side="N" />
    <Jst name="J7" x={5.05} y={-32.05} count={7} labels={["RB1", "RB2", "RB3", "RB4", "CLO", "CHI", "GND"]} rot={0} label="REEDS B" side="S" />
    <Jst name="J8" x={22.2} y={-32} count={4} labels={["GND", "3V3", "SDA", "SCL"]} rot={0} label="I2C" side="S" />
    <Jst name="J9" x={-42.65} y={-32} count={3} labels={["A", "B", "ERTH"]} rot={0} label="SCREEN" side="S" />
    {/* 12V inlet — KF301-5.0-2P 2-pin 5.0mm screw terminal (C474881, 17A/250V), the board's
        power inlet. Sized for the ~3.3A peak (both pumps priming + a few valves + the condenser
        fan) with margin the 3A XH wafer didn't have. pcbRotation 180 aims the wire throats at the
        north board edge, so the field loom feeds in from OUTSIDE the board. y=30.115 seats the body
        (fence) top edge on the same line as the north JST fences (33.815) — every north connector's
        fence sits the same distance from the edge, so J10 reads uniform with J5/J6/J13. pin1->GND,
        pin2->V12; the 180 seats GND on the east pad (x 18.4) and V12 on the west (x 13.4) —
        reversing 12V would cook the polarised bulk cap (C3), the bucks, and the drivers. THT
        barrels pick up their nets: V12 off the top island, GND off the bottom plane (the pour
        antipads the GND barrel clear of the V12 island). Traces unchanged (.J10 > .GND / .V12).
        Labels ARE the Jst survive-block: the import's own ref-des is suppressed (it would print
        upside-down here), "12V" (1.4mm) + the pin labels (0.8mm) are hand-drawn upright OUTBOARD of
        the fence toward the edge, at the same absolute Y as the north JSTs (pin labels 34.605,
        function 35.715) so all four read identically; the ref-des sits inside the fence (hidden
        under the body once populated), exactly where the JSTs tuck theirs. */}
    <KF301_5_0_2P name="J10" pinLabels={{ pin1: ["GND"], pin2: ["V12"] }} pcbRotation={180} {...at(23.4, 30.115)} />
    <silkscreentext text="GND" fontSize="0.8mm" anchorAlignment="center" pcbX={25.9} pcbY={34.605} />
    <silkscreentext text="V12" fontSize="0.8mm" anchorAlignment="center" pcbX={20.9} pcbY={34.605} />
    <silkscreentext text="12V" fontSize="1.4mm" anchorAlignment="center" pcbX={23.4} pcbY={35.715} />
    <silkscreentext text="J10" fontSize="0.8mm" anchorAlignment="center" pcbX={23.4} pcbY={27.0} />
    <Jst name="J11" x={-54.8} y={-32} count={4} labels={["GND", "V5", "DOUT", "AOUT"]} rot={0} label="GAS" side="S" />
    {/* GAS dividers: step the MQ-6's 0-5 V AOUT/DOUT down to ~3.0 V on-board, so a
        plain sensor cable is safe (IO36/IO39 are NOT 5 V tolerant). Each output is
        a vertical 2-resistor series: 2.2k (input, bottom) -> midpoint -> 3.3k (to
        GND, top) -> 5*3.3/5.5 = 3.0 V (safely under 3.3 V, still a valid logic HIGH
        for DOUT). The midpoint taps right into the ESP; AOUT: R1/R2 -> IO39, DOUT:
        R3/R4 -> IO36. IO36/IO39 are the ADC1 input-only pins at the west end of the ESP
        south edge; the dividers sit just below them, the GAS connector below the dividers. */}
    <Res name="R1" resistance="2.2k" footprint="0603" jlcpcb="C4190" x={-59} y={-25} rot={180} side="S" />
    <resistor name="R2" resistance="3.3k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22978"] }} pcbRotation={0} {...at(-59, -21.3)} />
    <resistor name="R3" resistance="2.2k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C4190"] }} pcbRotation={0} {...at(-63, -25)} />
    <resistor name="R4" resistance="3.3k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22978"] }} pcbRotation={0} {...at(-63, -21.3)} />

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
    <trace from=".R7 > .pin2" to="net.V3V3" />
    <trace from=".R7 > .pin1" to=".U1 > .EN" />
    <trace from=".C12 > .pin1" to=".U1 > .EN" />
    <trace from=".C12 > .pin2" to="net.GND" />
    <trace from=".R8 > .pin2" to="net.V3V3" />
    <trace from=".R8 > .pin1" to=".U1 > .IO0" />

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
        their planes (plane-stitching.md) — none of this routes. */}
    <trace from=".U2 > .A0" to="net.GND" />
    <trace from=".U2 > .A1" to="net.GND" />
    <trace from=".U2 > .A2" to="net.GND" />
    <trace from=".U2 > .RESET" to="net.V3V3" />
    <trace from=".U3 > .A0" to="net.V3V3" />
    <trace from=".U3 > .A1" to="net.GND" />
    <trace from=".U3 > .A2" to="net.GND" />
    <trace from=".U3 > .RESET" to="net.V3V3" />
    <Cap name="C4" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={2.18} y={12} rot={0} side="S" />
    <Cap name="C5" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={9} y={-26.9} rot={180} side="S" />
    <trace from=".C4 > .pin1" to="net.V3V3" />
    <trace from=".C4 > .pin2" to="net.GND" />
    <trace from=".C5 > .pin1" to="net.V3V3" />
    <trace from=".C5 > .pin2" to="net.GND" />

    {/* GPA -> ULN inputs, GPA_k -> IN_{8-k} (GPA0->IN8 ... GPA7->IN1), so the firmware
        valve mapping is unchanged; inside the ULN, channel j is IN_j -> OUT_j -> J.OUT_j
        (valve-control.mmd). Each MCP sits immediately left of its ULN, so the eight pairs
        cross straight across. */}
    <trace from=".U2 > .GPA0" to=".U4 > .IN8" />
    <trace from=".U2 > .GPA1" to=".U4 > .IN7" />
    <trace from=".U2 > .GPA2" to=".U4 > .IN6" />
    <trace from=".U2 > .GPA3" to=".U4 > .IN5" />
    <trace from=".U2 > .GPA4" to=".U4 > .IN4" />
    <trace from=".U2 > .GPA5" to=".U4 > .IN3" />
    <trace from=".U2 > .GPA6" to=".U4 > .IN2" />
    <trace from=".U2 > .GPA7" to=".U4 > .IN1" />
    <trace from=".U3 > .GPA0" to=".U5 > .IN8" />
    <trace from=".U3 > .GPA1" to=".U5 > .IN7" />
    <trace from=".U3 > .GPA2" to=".U5 > .IN6" />
    <trace from=".U3 > .GPA3" to=".U5 > .IN5" />
    <trace from=".U3 > .GPA4" to=".U5 > .IN4" />
    <trace from=".U3 > .GPA5" to=".U5 > .IN3" />
    <trace from=".U3 > .GPA6" to=".U5 > .IN2" />
    <trace from=".U3 > .GPA7" to=".U5 > .IN1" />

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

    {/* RS485 TTL side -> ESP UART. R (the receiver output) lands on IO34 — the ESP
        UART RX, an input-only pin, all an RX needs; D (the driver input) is fed by
        IO32 — the ESP UART TX, which must be output-capable (IO34/35/36/39 can't
        drive). 3.3 V VCC keeps R's swing safe for input-only IO34. /RE -> GND keeps
        the receiver always on; auto-direction is driven entirely off the D pin. */}
    <trace from=".U7 > .R" to=".U1 > .IO34" />
    <trace from=".U7 > .D" to=".U1 > .IO32" />
    <trace from=".U7 > .RE" to="net.GND" />
    <trace from=".U7 > .GND" to="net.GND" />
    <trace from=".C7 > .pin2" to="net.GND" />

    {/* manifold JSTs: ULN outputs -> valve looms */}
    <trace from=".U4 > .OUT1" to=".J1 > .OUT1" />
    <trace from=".U4 > .OUT2" to=".J1 > .OUT2" />
    <trace from=".U4 > .OUT3" to=".J1 > .OUT3" />
    <trace from=".U4 > .OUT4" to=".J1 > .OUT4" />
    <trace from=".U4 > .OUT5" to=".J1 > .OUT5" />
    <trace from=".U4 > .OUT6" to=".J1 > .OUT6" />
    <trace from=".U4 > .OUT7" to=".J1 > .OUT7" />
    <trace from=".U4 > .OUT8" to=".J1 > .OUT8" />
    <trace from=".J1 > .COM" to="net.V12" />
    {/* MANIFOLD B: 4 valves on U5 ch1-4, condenser FAN on U5 ch5, COM = 12V flyback. */}
    <trace from=".U5 > .OUT1" to=".J2 > .OUT1" />
    <trace from=".U5 > .OUT2" to=".J2 > .OUT2" />
    <trace from=".U5 > .OUT3" to=".J2 > .OUT3" />
    <trace from=".U5 > .OUT4" to=".J2 > .OUT4" />
    <trace from=".U5 > .OUT5" to=".J2 > .FAN" />
    <trace from=".J2 > .COM" to="net.V12" />

    {/* FAUCET UART — IO33 TX (output-capable) / IO35 RX (input-only), both S-edge pins;
        the connector sits in the bottom row below them. */}
    <trace from=".J3 > .IO33" to=".U1 > .IO33" />
    <trace from=".J3 > .IO35" to=".U1 > .IO35" />
    <trace from=".J3 > .GND" to="net.GND" />

    {/* SENSORS: flow (IO25) / 1-wire temps (IO26) / backflow drip-pan moisture
        (IO27) — three adjacent S-edge GPIOs. The 1-wire bus gets a proper 4.7k external
        pull-up to 3V3 on-board (R9 above), not the ESP's weak internal one; flow uses the
        internal pull-up (open-collector). 3V3 powers the DS18B20 probes + the moisture
        module; V5 the flow sensor. */}
    <trace from=".J4 > .IO25" to=".U1 > .IO25" />
    <trace from=".J4 > .IO26" to=".U1 > .IO26" />
    <trace from=".J4 > .IO27" to=".U1 > .IO27" />
    <trace from=".J4 > .GND" to="net.GND" />

    {/* PUMP DRIVERS — the two DRV8870 H-bridges (U11 pump A, U12 pump B). IN pins fed from
        the ESP north-edge bus, ordered so the four traces comb up west-to-east with no
        crossing: IO18->U11.IN2, IO17->U11.IN1, IO16->U12.IN2, IO4->U12.IN1 (the WROOM pins
        run IO18/IO17/IO16/IO4 west-to-east, the IN2/IN1 pads west-to-east — IN1/IN2 only set
        H-bridge polarity, so the firmware picks the forward sense). OUT1/OUT2 to the PUMPS
        connector. VM off 12V; GND + thermal PAD to the plane; ISEN to GND, VREF to 3V3; VM
        decoupled by C17/C18 (U11) and C19/C20 (U12). IO5 and IO15 are the only free GPIO. */}
    <trace from=".U1 > .IO18" to=".U11 > .IN2" />
    <trace from=".U1 > .IO17" to=".U11 > .IN1" />
    <trace from=".U11 > .VM" to="net.V12" />
    <trace from=".U11 > .GND" to="net.GND" />
    <trace from=".U11 > .PAD" to="net.GND" />
    <trace from=".U11 > .ISEN" to="net.GND" />
    <trace from=".U11 > .VREF" to="net.V3V3" />
    <trace from=".U11 > .OUT1" to=".J13 > .AM1" />
    <trace from=".U11 > .OUT2" to=".J13 > .AM2" />
    <trace from=".C17 > .pin1" to="net.V12" />
    <trace from=".C17 > .pin2" to="net.GND" />
    <trace from=".C18 > .pin1" to="net.V12" />
    <trace from=".C18 > .pin2" to="net.GND" />
    <trace from=".U1 > .IO16" to=".U12 > .IN2" />
    <trace from=".U1 > .IO4" to=".U12 > .IN1" />
    <trace from=".U12 > .VM" to="net.V12" />
    <trace from=".U12 > .GND" to="net.GND" />
    <trace from=".U12 > .PAD" to="net.GND" />
    <trace from=".U12 > .ISEN" to="net.GND" />
    <trace from=".U12 > .VREF" to="net.V3V3" />
    <trace from=".U12 > .OUT1" to=".J13 > .BM1" />
    <trace from=".U12 > .OUT2" to=".J13 > .BM2" />
    <trace from=".C19 > .pin1" to="net.V12" />
    <trace from=".C19 > .pin2" to="net.GND" />
    <trace from=".C20 > .pin1" to="net.V12" />
    <trace from=".C20 > .pin2" to="net.GND" />

    {/* RELAYS (J5): logic out to the two external opto-isolated relay modules + their V5 coil supply. */}
    <trace from=".J5 > .IO19" to=".U1 > .IO19" />
    <trace from=".J5 > .IO23" to=".U1 > .IO23" />
    <trace from=".J5 > .V5" to="net.V5" />
    <trace from=".J5 > .GND" to="net.GND" />


    {/* REEDS A (reservoir A) -> 0x20 GPB inputs; J6 sits directly above U2 and fans down. */}
    <trace from=".J6 > .RA1" to=".U2 > .GPB0" />
    <trace from=".J6 > .RA2" to=".U2 > .GPB1" />
    <trace from=".J6 > .RA3" to=".U2 > .GPB2" />
    <trace from=".J6 > .RA4" to=".U2 > .GPB3" />
    <trace from=".J6 > .GND" to="net.GND" />

    {/* REEDS B (reservoir B + carbonator low/high) -> 0x21 GPB inputs; J7 sits below U3 and fans up. */}
    <trace from=".J7 > .RB1" to=".U3 > .GPB0" />
    <trace from=".J7 > .RB2" to=".U3 > .GPB1" />
    <trace from=".J7 > .RB3" to=".U3 > .GPB2" />
    <trace from=".J7 > .RB4" to=".U3 > .GPB3" />
    <trace from=".J7 > .CLO" to=".U3 > .GPB4" />
    <trace from=".J7 > .CHI" to=".U3 > .GPB5" />
    <trace from=".J7 > .GND" to="net.GND" />
    <trace from=".U3 > .GND" to="net.GND" />

    {/* DISPLAY: RS485 line side (A/B/ERTH) out to the front 4.3" config panel.
        Signal only — the panel takes its own 7-36 V power off the 12 V harness. The
        differential pair fans U7.A/B -> J9, tapped by the 120R termination (R6) and
        the SM712 ESD array (D1) at the cable entry; ERTH bonds the cable to GND. */}
    <trace from=".U7 > .A" to=".J9 > .A" />
    <trace from=".U7 > .B" to=".J9 > .B" />
    <trace from=".U7 > .A" to=".R6 > .pin1" />
    <trace from=".U7 > .B" to=".R6 > .pin2" />
    <trace from=".U7 > .A" to=".D1 > .A" />
    <trace from=".U7 > .B" to=".D1 > .B" />
    <trace from=".D1 > .GND" to="net.GND" />
    <trace from=".J9 > .ERTH" to="net.GND" />

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
    <trace from=".U8 > ._NEG" to=".Q1 > .C" />
    <trace from=".Q1 > .E" to="net.GND" />
    <trace from=".Q1 > .B" to=".R5 > .pin1" />
    <trace from=".R5 > .pin2" to=".U1 > .IO13" />

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
    <trace from=".J11 > .AOUT" to=".R1 > .pin1" />
    <trace from=".R1 > .pin2" to=".R2 > .pin1" />
    <trace from=".R1 > .pin2" to=".U1 > .IO39" />
    <trace from=".R2 > .pin2" to="net.GND" />
    <trace from=".J11 > .DOUT" to=".R3 > .pin1" />
    <trace from=".R3 > .pin2" to=".R4 > .pin1" />
    <trace from=".R3 > .pin2" to=".U1 > .IO36" />
    <trace from=".R4 > .pin2" to="net.GND" />
    <trace from=".J11 > .GND" to="net.GND" />

    {/* V12 decoupling. HF: two 0.1uF ceramics (C1 y-16.6, C2 y0.2) on the V12 island
        by the ULN/manifold block, snubbing the fast solenoid-turn-off edge. BULK: a
        470uF low-ESR electrolytic (C3, BOM 1) at the board centre between the two MCP
        stacks (U2 north, U3 south), west of the ULNs it feeds across the V12 island,
        soaking the inrush + flyback dump the ceramics can't. Every pin1 -> V12, pin2 ->
        GND plane — no routing, no vias, barrel pickup like every power pin; the top V12
        island floods the whole valve block. C3 is polarized: pin1 (+) is V12. */}
    <Cap name="C1" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={21.08} y={-16.6} rot={0} side="S" />
    <Cap name="C2" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={20.98} y={0.2} rot={0} side="S" />
    <BulkCap name="C3" x={6.824} y={-0.606} />
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
    <resistor name="R9" resistance="4.7k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C23162"] }} {...at(-16, -28)} />
    <trace from=".R9 > .pin1" to="net.V3V3" />
    <trace from=".R9 > .pin2" to=".J4 > .IO26" />

    {/* ── Indicator LEDs flanking the brand logo ─────────────────────────────────────
        LEFT — firmware status, three otherwise-idle ESP GPIO, active-high to GND, boot-safe:
        RED = fault (IO14, not a strap), GREEN = ready/heartbeat (IO2, wants low at boot),
        BLUE = activity (IO12 / MTDI, wants low at boot — LED-to-GND only, never tied high).
        RIGHT — power rails, each off its plane through a series R: 3V3 + 5V (3V3 lit ⇒ 12 V in
        AND the 5V buck + 3V3 LDO are up — the board is alive before firmware runs). 470R (C23179) per
        LED; ref-des silk stripped from the LED imports (it collides at this pitch), so meaning
        is by colour + position (see esp32-scope.md). */}
    {/* left — firmware R/G/B; anode toward its R (outboard, -x): D2 red rot 180, D3/D4 native */}
    <LedRed name="D2" pcbRotation={180} {...at(-31.5, -15.05)} />
    <LedGrn name="D3" {...at(-31.5, -17.55)} />
    <LedBlu name="D4" {...at(-31.5, -20.05)} />
    <resistor name="R10" resistance="470" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C23179"] }} {...at(-36, -15.05)} />
    <resistor name="R11" resistance="470" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C23179"] }} {...at(-36, -17.55)} />
    <resistor name="R12" resistance="470" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C23179"] }} {...at(-36, -20.05)} />
    {/* right — power rails (green), anode toward its R (outboard, +x): both rot 180 */}
    <LedGrn name="D5" pcbRotation={180} {...at(-21.5, -17)} />
    <LedGrn name="D6" pcbRotation={180} {...at(-21.5, -20)} />
    <resistor name="R13" resistance="470" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C23179"] }} {...at(-17, -17)} />
    <resistor name="R14" resistance="470" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C23179"] }} {...at(-17, -20)} />
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
    {/* Layout: J14 / U14 / U13 stack on x=-51.5, D+/D- running down the column. BOOT/RESET
        tacts stack on the west edge (x=-62). The auto-reset pair straddles the CH340's
        south-edge DTR/RTS — Q2 west (collector to the WROOM EN pin at the SW corner), Q3 east
        by IO0 — with R17/R18 between. CC pulldowns sit in the top corners; C22 rides U14's
        VBUS, C21 rides U13's 3V3. East column on x=-44, 4 mm pitch: C6 / R8 / Q3 / C21 (with
        R15 above), R8 the IO0 pull-up spun vertical into the stack. */}
    <UsbC name="J14" pcbX={-51.5} pcbY={31.3} pcbRotation={180} />
    <Usblc6 name="U14" pcbX={-51.5} pcbY={25.7} pcbRotation={180} />
    <CH340C name="U13" pcbX={-51.5} pcbY={19.3} pcbRotation={180} />
    <resistor name="R16" resistance="5.1k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C23186"] }} {...at(-58.9, 34.7)} />
    <resistor name="R15" resistance="5.1k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C23186"] }} {...at(-44, 34.7)} />
    <Cap name="C22" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-47.5} y={25.7} rot={90} side="E" />
    <Cap name="C21" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-44} y={20} rot={90} side="E" />
    {/* EN branch (west): U13.DTR -> R17 -> Q2.base; U13.RTS -> Q2.emitter; Q2.collector -> EN; SW2 */}
    <resistor name="R17" resistance="10k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C25804"] }} {...at(-53, 14.5)} />
    <S8050 name="Q2" pcbX={-56.5} pcbY={13} pcbRotation={0} />
    <silkscreentext text="Q2" fontSize="0.8mm" anchorAlignment="center" pcbX={-56.5} pcbY={10.9} />
    <Tact name="SW2" pcbX={-62} pcbY={27} pcbRotation={0} />
    {/* IO0 branch (east): U13.RTS -> R18 -> Q3.base; U13.DTR -> Q3.emitter; Q3.collector -> IO0; SW1 */}
    <resistor name="R18" resistance="10k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C25804"] }} {...at(-49, 14.5)} />
    <S8050 name="Q3" pcbX={-44} pcbY={16} pcbRotation={0} />
    <silkscreentext text="Q3" fontSize="0.8mm" anchorAlignment="center" pcbX={-41.9} pcbY={16} />
    <Tact name="SW1" pcbX={-62} pcbY={20} pcbRotation={0} />
    {/* USB-C: GND (pin13/14) + shield ears (pin1-4) to plane; VBUS (pin15/16) to the ESD
        rail only (not board power); CC1 (pin6) / CC2 (pin12) each to a 5.1k Rd; D+ = pin8+pin10,
        D- = pin7+pin9 (both orientations tied). */}
    <trace from=".J14 > .pin13" to="net.GND" />
    <trace from=".J14 > .pin14" to="net.GND" />
    <trace from=".J14 > .pin1" to="net.GND" />
    <trace from=".J14 > .pin2" to="net.GND" />
    <trace from=".J14 > .pin3" to="net.GND" />
    <trace from=".J14 > .pin4" to="net.GND" />
    <trace from=".J14 > .pin6" to=".R15 > .pin1" />
    <trace from=".R15 > .pin2" to="net.GND" />
    <trace from=".J14 > .pin12" to=".R16 > .pin1" />
    <trace from=".R16 > .pin2" to="net.GND" />
    <trace from=".J14 > .pin8" to=".U14 > .pin1" />
    <trace from=".J14 > .pin10" to=".U14 > .pin1" />
    <trace from=".J14 > .pin7" to=".U14 > .pin3" />
    <trace from=".J14 > .pin9" to=".U14 > .pin3" />
    <trace from=".J14 > .pin15" to=".U14 > .pin5" />
    <trace from=".J14 > .pin16" to=".U14 > .pin5" />
    {/* ESD array: GND + VBUS rail + bypass cap; D+/D- pass through to the bridge. */}
    <trace from=".U14 > .pin2" to="net.GND" />
    <trace from=".C22 > .pin1" to=".U14 > .pin5" />
    <trace from=".C22 > .pin2" to="net.GND" />
    <trace from=".U14 > .pin6" to=".U13 > .D_POS" />
    <trace from=".U14 > .pin4" to=".U13 > .D_NEG" />
    {/* CH340C: 3V3 supply (VCC + V3 tied for 3.3 V op) + 0.1uF decoupling; UART crossed to
        the WROOM (bridge TXD -> ESP RXD0/IO3, bridge RXD -> ESP TXD0/IO1). */}
    <trace from=".U13 > .VCC" to="net.V3V3" />
    <trace from=".U13 > .V3" to="net.V3V3" />
    <trace from=".U13 > .GND" to="net.GND" />
    <trace from=".C21 > .pin1" to="net.V3V3" />
    <trace from=".C21 > .pin2" to="net.GND" />
    <trace from=".U13 > .TXD" to=".U1 > .IO3" />
    <trace from=".U13 > .RXD" to=".U1 > .IO1" />
    {/* Auto-reset cross-coupled pair (see block header for the truth table). */}
    <trace from=".U13 > .DTR" to=".R17 > .pin1" />
    <trace from=".R17 > .pin2" to=".Q2 > .B" />
    <trace from=".U13 > .RTS" to=".Q2 > .E" />
    <trace from=".Q2 > .C" to=".U1 > .EN" />
    <trace from=".U13 > .RTS" to=".R18 > .pin1" />
    <trace from=".R18 > .pin2" to=".Q3 > .B" />
    <trace from=".U13 > .DTR" to=".Q3 > .E" />
    <trace from=".Q3 > .C" to=".U1 > .IO0" />
    {/* Manual BOOT (IO0) / RESET (EN) — diagonal switch pads = the two terminals. */}
    <trace from=".SW1 > .pin1" to=".U1 > .IO0" />
    <trace from=".SW1 > .pin4" to="net.GND" />
    <trace from=".SW2 > .pin1" to=".U1 > .EN" />
    <trace from=".SW2 > .pin4" to="net.GND" />

    {/* ── M3 mounting holes, one per corner, plated and tied to GND so a metal screw can't
        bridge a power plane (GND connects on the bottom plane; V12 / 3V3 / 5V / SDA / SCL
        antipad). A symmetric rectangle: every hole is inset 3.5 mm from both of its board
        edges, so the four stay centred on the board and clear of the nearest connector at
        each corner. */}
    <platedhole name="MH1" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" connectsTo="net.GND" pcbX={-64.0} pcbY={33.5} />
    <platedhole name="MH2" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" connectsTo="net.GND" pcbX={31.4} pcbY={33.5} />
    <platedhole name="MH3" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" connectsTo="net.GND" pcbX={31.4} pcbY={-35.07} />
    <platedhole name="MH4" shape="circle" holeDiameter="3.2mm" outerDiameter="4.0mm" connectsTo="net.GND" pcbX={-64.0} pcbY={-35.07} />

    {/* Board identity nameplate — the soda-glass brand mark (ios/AppIcon.svg,
        monocolor silk via logo.ts) over the centered name + version, a compact
        stack in the open lower-centre, between the RS485 cluster to its west and
        the south MCP (U3) to its east. The version is the firmware scheme
        (firmware/pre_build.py): commit date + short SHA, a trailing `+` from
        uncommitted edits — a pure function of the commit, naming which source
        tree a fabbed board came from. */}
    {logoRoutes(-26.631, -18.0, 6).map((route, i) => (
      <silkscreenpath key={`logo${i}`} strokeWidth="0.15mm" route={route} />
    ))}
    <silkscreentext text="HOME SODA MACHINE" fontSize="1.6mm" anchorAlignment="center" pcbX={-26.631} pcbY={-23.0} />
    <silkscreentext text={`${ID.date}.${ID.rev}`} fontSize="1.6mm" anchorAlignment="center" pcbX={-26.631} pcbY={-25.0} />

    {/* Power/bus pours — SIX layers, top->bottom: top (signals + the V12 island), 3V3
        (inner1), 5V (inner2), SDA (inner3), SCL (inner4), GND (bottom). 3V3/5V/SDA/SCL/GND
        are full-flood planes; each pin commons to its plane at its through-hole barrel or
        an auto-stitched via (SMD). V12 is a top-copper island over the valve/buck/driver
        block (its L outline below): top-layer 12V pads sit directly on it, through-hole 12V
        pins pick it up at the barrel. Point-to-point signals route on top and bottom. */}
    <trace from=".J10 > .V12" to="net.V12" />
    <copperpour name="V12ISLAND" layer="top" connectsTo="net.V12" netClearance="0.5mm from V3V3, V5, SDA, SCL"
      outline={[{ x: -37, y: 35 }, { x: 33, y: 35 }, { x: 33, y: -37 }, { x: -8, y: -37 },
                { x: -8, y: 11 }, { x: -37, y: 11 }]} />
    <copperpour name="V3V3PLANE" layer="inner1" connectsTo="net.V3V3" boardEdgeMargin="0.5mm" />
    <copperpour name="V5PLANE" layer="inner2" connectsTo="net.V5" boardEdgeMargin="0.5mm" />
    <copperpour name="SDAPLANE" layer="inner3" connectsTo="net.SDA" boardEdgeMargin="0.5mm" />
    <copperpour name="SCLPLANE" layer="inner4" connectsTo="net.SCL" boardEdgeMargin="0.5mm" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" boardEdgeMargin="0.5mm" />
  </board>
)
