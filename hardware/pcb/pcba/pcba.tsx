/**
 * esp32-mcp-mini — the controller carrier. Off-the-shelf modules plug into
 * 2.54 mm header sockets; the board is the interconnect, and every off-board
 * interface lands on a labeled edge connector (J1-J11). Footprint geometry
 * lives in ./carrier_parts; placement + routing are declared here.
 *
 * The ESP32 sits at the far-left, antenna off-board. Its usable GPIO are nearly all on the
 * north and south castellations (the east edge is flash + the lone GPIO IO13), so every
 * off-board signal fans up or down and its connector lives on that edge, ordered to match the
 * pin run. NORTH / top: RELAYS (J5) and PROG (J12) at the edge, and — combed up from the north
 * pins as one parallel bus — the two pump drivers (U11/U12) feeding PUMPS. SOUTH / bottom: an
 * edge row of cable connectors — GAS (J11), SCREEN (J9), FAUCET (J3), SENSORS (J4) — with their
 * on-board conditioning in a second row just above (the R1-R4 gas dividers, the U7 RS485
 * transceiver). The buzzer (U8/Q1/R5) sits east of the ESP by its IO13 pin. Center: DS3231 +
 * coin cell; the two MCPs stacked through the middle (0x20 north, 0x21 south) with their reed
 * inputs on REEDS A (above) / REEDS B (below). Right block: the two ULNs with the valve
 * manifolds immediately to their right and the V12 bulk/HF decoupling between them; the K7803/
 * K7805 bucks (U9 top, U10 bottom) and the 12V inlet (J10) frame the right column.
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
 * through-hole 12V pins pick it up at the barrel. Point-to-point signals are traced on the
 * two outer layers (the core patch gives the router a top+bottom view).
 */
import { at, Cap, Jst, ulnOUT } from "./carrier_parts"
import { Uln2803, Mcp23017, Ds3231Smd, Thvd1426, Sm712 } from "./pcba_parts"
import { K7803_1000R3 } from "./imports/K7803_1000R3"
import { K7805_2000R3 } from "./imports/K7805_2000R3"
import { DRV8870DDAR as Drv8870 } from "./imports/DRV8870DDAR"
import { boardVersionParts } from "./board-version"
import { logoRoutes } from "./logo"
import { NXB_25V470_10_12_5 } from "./imports/NXB_25V470_10_12_5"
import { MLT_5020 } from "./imports/MLT_5020"
import { S8050_J3Y_RANGE_200_350_ as S8050 } from "./imports/S8050_J3Y_RANGE_200_350_"
import { KH_CR2032_2_1 as CoinCell } from "./imports/KH_CR2032_2_1"
import { ESP32_WROOM_32E_N4 as Wroom } from "./imports/ESP32_WROOM_32E_N4"

// Identity stamp version (commit date + short SHA), computed once per render.
const ID = boardVersionParts()

export default () => (
  <board layers={6} outline={[{ x: -67.5, y: -38 }, { x: 27, y: -38 }, { x: 27, y: 36 }, { x: -67.5, y: 36 }]} minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" pcbStyle={{ silkscreenFontSize: "0.8mm" }} autorouter={{ traceClearance: 0.45 }}>
    {/* DS3231SN RTC + CR2032 backup, east of the ESP. U6 (the SOIC) sits high with its
        0.1uF decoupler (C6) to its west and the buzzer column below it; the 20 mm THT coin
        base (BT1) is the bulk to U6's east. + is pin1 (the silk-marked post -> VBAT), - is
        pin2 (-> GND); the cell is retained by the molded base, not SMT clips. */}
    <CoinCell name="BT1" pcbX={-20.55} pcbY={-2} pcbRotation={180} />
    <Ds3231Smd name="U6" x={-35.85} y={7.1} />
    <Cap name="C6" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-41.95} y={8.15} rot={90} />
    {/* Base controller — bare ESP32-WROOM-32E (U1, C701341), no radio, antenna keepout
        pointing west off the board edge. Usable GPIO sit on the north and south
        castellations only (the east edge is the module's flash); the relay/pump/buzzer/
        I2C/prog lines land on the north edge, the UART/ADC/sensor lines on the south (pin
        map in esp32-scope.md). 3V3 is the only supply pin (no V5): it draws from the 3V3
        plane (sourced by the K7803 buck), every GND pad (incl. the centre thermal pad)
        auto-stitches to the bottom plane. Decoupling (C10 0.1uF + C11 10uF bulk) and the EN
        power-on RC (R7 10k pull-up + C12 1uF) sit at the south edge by the 3V3/EN pins; R8
        (10k) pulls IO0 up; J12 is the 6-pin serial programming header on the north edge by its
        IO0/TX0/RX0 pins — only its EN line climbs from the south edge. */}
    <Wroom name="U1" pcbX={-56.45} pcbY={0} pcbRotation={0} />
    {/* WROOM support south of U1: the EN power-on RC (R7 + C12) stacked at the far-west,
        hard by U1's EN pin so the EN trace stays short; the supply decouplers C10 + C11
        share the lane just east of them. */}
    <capacitor name="C12" capacitance="1uF" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C15849"] }} {...at(-63.5, -13.5)} />
    <resistor name="R7" resistance="10k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C25804"] }} {...at(-63.5, -17.5)} />
    <Cap name="C10" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-58.5} y={-14.0} rot={90} lab={[-1.85, 0]} />
    <Cap name="C11" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-53.5} y={-14.0} rot={90} lab={[1.85, 0]} />
    <resistor name="R8" resistance="10k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C25804"] }} pcbRotation={90} {...at(-49.2, 14.8)} />
    <Jst name="J12" x={-45} y={31} count={6} labels={["3V3", "EN", "TX0", "RX0", "IO0", "GND"]} rot={0} label="PROG" />
    {/* RS-485 to the front display (J9). THVD1426 auto-direction transceiver (U7):
        no host DE/RE — /RE tied low (always receive), /SHDN tied high (always on),
        only D (from ESP TX) and R (to ESP RX) are driven. R6 = 120R line termination
        across A/B; D1 = SM712 ESD array at the J9 cable entry; C7 decouples VCC. */}
    <Thvd1426 name="U7" x={-50} y={-22} />
    <resistor name="R6" resistance="120" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22787"] }} {...at(-44, -22)} />
    <Sm712 name="D1" x={-44} y={-26} rot={0} />
    <Cap name="C7" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-50} y={-17} rot={90} lab={[1.85, 0]} />
    {/* On-board supplies in the open right-hand area: U9 = K7803 (12V->3V3, 1A), U10 =
        K7805 (12V->5V, 2A), 3-pin SIP modules (pin1 Vin / pin2 GND / pin3 +Vo, 2.54 mm
        pitch). Vin/+Vo/GND each common to their plane at the barrel. Per buck: a 10uF input
        cap (Vin->GND) and an output cap (+Vo->GND, 10uF on U9, 22uF on U10). */}
    <K7803_1000R3 name="U9" pcbX={10.15} pcbY={28.45} pcbRotation={0} />
    <Cap name="C13" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={6.15} y={24.45} rot={0} lab={[0, -1.35]} />
    <Cap name="C14" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={14.15} y={24.35} rot={0} lab={[0, -1.35]} />
    <K7805_2000R3 name="U10" pcbX={18.75} pcbY={-29.85} pcbRotation={180} />
    {/* U10 ref-des hand-drawn upright inside its fence (the footprint's own label is
        suppressed: at rot 180 it read upside-down, below the fence). */}
    <silkscreentext text="U10" fontSize="1mm" anchorAlignment="center" pcbX={18.75} pcbY={-25.0} />
    <Cap name="C15" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={14.75} y={-34.1} rot={0} lab={[0, -1.35]} />
    <Cap name="C16" capacitance="22uF" footprint="0805" jlcpcb="C45783" x={22.75} y={-34.1} rot={0} lab={[0, -1.35]} />
    {/* Pump drivers, in the second row behind the top-edge connectors: one DRV8870 H-bridge per peristaltic flavor
        pump (12V brushed DC, 0.3-0.5A, PWM), 45V/3.6A SMD with internal freewheeling +
        OCP/OTP/UVLO. VM->12V (the top SMD pad lands directly on the V12 island), GND/PAD->GND,
        ISEN->GND, VREF->3V3, IN1/IN2 from the ESP north-edge pins, OUT1/OUT2 to PUMPS. 10uF +
        0.1uF VM decoupling per chip. */}
    <Drv8870 name="U11" pcbX={-31.55} pcbY={22} pcbRotation={0} />
    <Cap name="C17" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-35.1} y={14.5} rot={0} lab={[0, -1.35]} />
    <Cap name="C18" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-28.1} y={13} rot={0} lab={[0, -1.35]} />
    <Drv8870 name="U12" pcbX={-18.5} pcbY={22} pcbRotation={0} />
    <Cap name="C19" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-22.05} y={13} rot={0} lab={[0, -1.35]} />
    <Cap name="C20" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-15.05} y={13} rot={0} lab={[0, -1.35]} />
    <Mcp23017 name="U2" x={-2.2} y={18.1} addr="0x20" rot={270} />
    <Mcp23017 name="U3" x={-2.1} y={-22.85} addr="0x21" rot={90} />
    {/* MCP / buzzer ref-des hand-drawn upright to the west of each part (the
        footprints' own labels are suppressed — _norefdes on the MCPs, the MLT label
        dropped — because the chip rotations turned them upside-down or sideways). */}
    <silkscreentext text="U2" fontSize="1mm" anchorAlignment="center" pcbX={-8.5} pcbY={18.1} />
    <silkscreentext text="U3" fontSize="1mm" anchorAlignment="center" pcbX={-8.5} pcbY={-22.85} />
    <Uln2803 name="U4" x={11.8} y={4.85} />
    <Uln2803 name="U5" x={11.9} y={-11.95} />
    <MLT_5020 name="U8" {...at(-41.45, -15.35)} pcbRotation={270} />
    <silkscreentext text="U8" fontSize="1mm" anchorAlignment="center" pcbX={-36.5} pcbY={-15.35} />
    <S8050 name="Q1" {...at(-42, -9)} />
    <resistor name="R5" resistance="1k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C21190"] }} {...at(-42, -5)} />
    {/* Manifolds sit immediately right of their ULNs so OUT1-8/COM are straight shots
        across (J1 pin order = ULN output pin order, reversed). */}
    <Jst name="J1" x={21.6} y={8.85} count={9} labels={[...ulnOUT].reverse()} rot={90} label="MANIFOLD A" labelDir={1} />
    <Jst name="J2" x={21.65} y={-13} count={6} labels={["COM", "FAN", "OUT4", "OUT3", "OUT2", "OUT1"]} rot={90} label="MANIFOLD B" labelDir={1} />
    {/* Pump-motor outputs — one PUMPS connector. Pin order is AM2/AM1/BM2/BM1, left to
        right, matching the drivers' OUT pads west-to-east (U11 then U12) so each pair
        combs straight up to its own side of J13 with no crossing. */}
    <Jst name="J13" x={-26} y={31} count={4} labels={["AM2", "AM1", "BM2", "BM1"]} rot={0} label="PUMPS" labelDir={1} />
    <Jst name="J3" x={-36.5} y={-32} count={4} labels={["GND", "V5", "IO35", "IO33"]} rot={0} label="FAUCET" />
    <Jst name="J4" x={-21} y={-32} count={6} labels={["GND", "V5", "IO25", "IO26", "IO27", "3V3"]} rot={0} label="SENSORS" />
    {/* RELAYS — logic-level control out to the two external opto-isolated relay modules
        (compressor AC switch + carbonator diaphragm-pump 12V gate, both off-board). IO23/
        IO19 drive them; V5 feeds the relay modules' coil/opto supply; GND returns. */}
    <Jst name="J5" x={-60} y={31} count={4} labels={["GND", "V5", "IO23", "IO19"]} rot={0} label="RELAYS" />
    <Jst name="J6" x={-4.55} y={31} count={5} labels={["GND", "RA4", "RA3", "RA2", "RA1"]} rot={0} label="REEDS A" />
    <Jst name="J7" x={-1.6} y={-32.05} count={7} labels={["RB1", "RB2", "RB3", "RB4", "CLO", "CHI", "GND"]} rot={0} label="REEDS B" />
    <Jst name="J9" x={-48.25} y={-32} count={3} labels={["A", "B", "ERTH"]} rot={0} label="SCREEN" />
    <Jst name="J10" x={21.25} y={30.95} count={2} labels={["GND", "V12"]} rot={0} label="12V" labelDir={1} />
    <Jst name="J11" x={-60} y={-32} count={4} labels={["GND", "V5", "DOUT", "AOUT"]} rot={0} label="GAS" />
    {/* GAS dividers: step the MQ-6's 0-5 V AOUT/DOUT down to ~3.0 V on-board, so a
        plain sensor cable is safe (IO36/IO39 are NOT 5 V tolerant). Each output is
        a vertical 2-resistor series: 2.2k (input, bottom) -> midpoint -> 3.3k (to
        GND, top) -> 5*3.3/5.5 = 3.0 V (safely under 3.3 V, still a valid logic HIGH
        for DOUT). The midpoint taps right into the ESP; AOUT: R1/R2 -> IO39, DOUT:
        R3/R4 -> IO36. IO36/IO39 are the ADC1 input-only pins at the west end of the ESP
        south edge; the dividers sit just below them, the GAS connector below the dividers. */}
    <resistor name="R1" resistance="2.2k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C4190"] }} pcbRotation={0} {...at(-59, -25)} />
    <resistor name="R2" resistance="3.3k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22978"] }} pcbRotation={0} {...at(-59, -20)} />
    <resistor name="R3" resistance="2.2k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C4190"] }} pcbRotation={0} {...at(-63, -25)} />
    <resistor name="R4" resistance="3.3k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22978"] }} pcbRotation={0} {...at(-63, -20)} />

    {/* 3V3 rail -> inner1 plane, sourced by the K7803 buck (U9) off 12V. The I2C devices
        (both MCPs, DS3231), RS485, the WROOM, and the sensor loom all common to it at
        their barrels. */}
    {/* bucks: Vin (pin1) off 12V, GND (pin2) to the bottom plane, +Vo (pin3) to its rail.
        Local decoupling per buck: input cap Vin->GND, output cap +Vo->GND. */}
    <trace from=".U9 > .pin1" to="net.V12" />
    <trace from=".U9 > .pin2" to="net.GND" />
    <trace from=".U9 > .pin3" to="net.V3V3" />
    <trace from=".C13 > .pin1" to="net.V12" />
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
    <trace from=".U2 > .VCC" to="net.V3V3" />
    <trace from=".U3 > .VCC" to="net.V3V3" />
    <trace from=".U6 > .VCC" to="net.V3V3" />
    <trace from=".C6 > .pin1" to="net.V3V3" />
    <trace from=".U7 > .VCC" to="net.V3V3" />
    <trace from=".U7 > .SHDN" to="net.V3V3" />
    <trace from=".C7 > .pin1" to="net.V3V3" />
    <trace from=".J4 > .3V3" to="net.V3V3" />

    {/* Bare WROOM (U1) power + reset + programming block. 3V3 is the lone supply pin: it,
        the decouplers (C10 0.1uF / C11 10uF bulk), the pull-up high sides (R7 EN, R8 IO0)
        and the prog header (J12) all common to the 3V3 plane; the GND pads (incl. the
        centre thermal pad), the EN cap (C12) low side, and the prog GND to the bottom
        plane — all SMD legs auto-stitch. EN power-on RC: R7 (10k) to 3V3, C12 (1uF) to
        GND. IO0 held high by R8 (10k). J12 breaks out the serial bootloader (TX0=IO1,
        RX0=IO3, IO0, EN). No V5 — the module is 3V3-only. */}
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
    <trace from=".J12 > .3V3" to="net.V3V3" />
    <trace from=".J12 > .GND" to="net.GND" />
    <trace from=".J12 > .EN" to=".U1 > .EN" />
    <trace from=".J12 > .IO0" to=".U1 > .IO0" />
    <trace from=".J12 > .TX0" to=".U1 > .IO1" />
    <trace from=".J12 > .RX0" to=".U1 > .IO3" />

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
    <Cap name="C4" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-4.5} y={12} rot={0} lab={[0, -1.35]} />
    <Cap name="C5" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={9.65} y={-25.9} rot={90} lab={[1.85, 0]} />
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
        (IO27) — three adjacent S-edge GPIOs (internal pull-ups for the 1-wire bus +
        open-collector flow). 3V3 powers the DS18B20 probes + the moisture module; V5
        the flow sensor. */}
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
        decoupled by C17/C18 (U11) and C19/C20 (U12). IO13/IO14/IO15 are unconnected. */}
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

    {/* V12 decoupling, gridded on the right edge. HF: two 0.1uF ceramics (C1/C2)
        each level with its manifold row — C2 by MANIFOLD A (y+19.1), C1 by MANIFOLD
        B (y-19.1) — snubbing the fast solenoid-turn-off edge, with the 12V inlet
        (J10) centered between them at y0. BULK: a 470uF low-ESR electrolytic (C3,
        BOM 1) in the board centre between the two MCP stacks, west of the ULNs it
        feeds across the V12 island, soaking the inrush + flyback dump the ceramics
        can't. Every pin1 -> V12, pin2 -> GND plane — no routing, no vias, barrel
        pickup like every power pin; the top V12 island floods the whole valve
        block. C3 is polarized: pin1 (+) is V12. */}
    <Cap name="C1" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={14.4} y={-20.2} rot={0} lab={[0, -1.35]} />
    <Cap name="C2" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={14.3} y={-3.3} rot={0} lab={[0, -1.35]} />
    <NXB_25V470_10_12_5 name="C3" pcbRotation={180} {...at(-1.4, 3.8)} />
    <silkscreentext text="C3" fontSize="1mm" anchorAlignment="center" pcbX={-1.4} pcbY={-2.8} />
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

    {/* Board identity nameplate — the soda-glass brand mark (ios/AppIcon.svg,
        monocolor silk via logo.ts) over the centered name + version, a compact
        stack in the open lower-centre, between the RS485 cluster to its west and
        the south MCP (U3) to its east. The version is the firmware scheme
        (firmware/pre_build.py): commit date + short SHA, a trailing `+` from
        uncommitted edits — a pure function of the commit, naming which source
        tree a fabbed board came from. */}
    {logoRoutes(-26.631, -19.0, 4).map((route, i) => (
      <silkscreenpath key={`logo${i}`} strokeWidth="0.12mm" route={route} />
    ))}
    <silkscreentext text="HOME SODA MACHINE" fontSize="1mm" anchorAlignment="center" pcbX={-26.631} pcbY={-21.9} />
    <silkscreentext text={`${ID.date} ${ID.rev}`} fontSize="1mm" anchorAlignment="center" pcbX={-26.631} pcbY={-23.2} />

    {/* Power/bus pours — SIX layers, top->bottom: top (signals + the V12 island), 3V3
        (inner1), 5V (inner2), SDA (inner3), SCL (inner4), GND (bottom). 3V3/5V/SDA/SCL/GND
        are full-flood planes; each pin commons to its plane at its through-hole barrel or
        an auto-stitched via (SMD). V12 is a top-copper island over the valve/buck/driver
        block (its L outline below): top-layer 12V pads sit directly on it, through-hole 12V
        pins pick it up at the barrel. Point-to-point signals route on top and bottom. */}
    <trace from=".J10 > .V12" to="net.V12" />
    <copperpour name="V12ISLAND" layer="top" connectsTo="net.V12" netClearance="0.5mm from V3V3, V5, SDA, SCL"
      outline={[{ x: -37, y: 35 }, { x: 26, y: 35 }, { x: 26, y: -37 }, { x: -8, y: -37 },
                { x: -8, y: 11 }, { x: -37, y: 11 }]} />
    <copperpour name="V3V3PLANE" layer="inner1" connectsTo="net.V3V3" boardEdgeMargin="0.5mm" />
    <copperpour name="V5PLANE" layer="inner2" connectsTo="net.V5" boardEdgeMargin="0.5mm" />
    <copperpour name="SDAPLANE" layer="inner3" connectsTo="net.SDA" boardEdgeMargin="0.5mm" />
    <copperpour name="SCLPLANE" layer="inner4" connectsTo="net.SCL" boardEdgeMargin="0.5mm" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" boardEdgeMargin="0.5mm" />
  </board>
)
