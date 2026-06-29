/**
 * esp32-mcp-mini — the controller carrier. Off-the-shelf modules plug into
 * 2.54 mm header sockets; the board is the interconnect, and every off-board
 * interface lands on a labeled edge connector (J1-J11). Footprint geometry
 * lives in ./carrier_parts; placement + routing are declared here.
 *
 * Left column: RS485 over the ESP32; DS3231 centered in the pocket below it. MCP stack
 * (0x20 over 0x21) with the ULN drivers and manifold connectors to the right, dropped to
 * sit flush with the left half. The buzzer sits bottom-left, beside DS3231; the gas
 * dividers (R1-R4) sit up top in the connector row, over the ESP IO36/IO39 ADC pins.
 *
 * FOUR layers, stackup top->bottom:
 *   L1 top    — signals + the V12 pour over the valve block (top-right)
 *   L2 inner1 — 3V3 plane (full flood)
 *   L3 inner2 — 5V plane (full flood)
 *   L4 bottom — GND plane (full flood)
 * 3V3, 5V, GND and V12 are poured: every through-hole pin on those nets commons
 * to its plane at the barrel, so none of them is routed (no power vias). Only the
 * point-to-point signals + the I2C bus are traced, and they are confined to the
 * two outer layers (the core patch hands the router a 2-layer view so the inner
 * planes stay pristine copper). SDA/SCL stay a routed top bus — two co-located
 * nets pour into ugly interlocking islands, a clean trace pair reads better.
 */
import { at, Cap, Jst, ulnOUT } from "./carrier_parts"
import { Uln2803, Mcp23017, Ds3231Smd, Thvd1426, Sm712, Ams1117_33 } from "./pcba_parts"
import { boardVersionParts } from "./board-version"
import { logoRoutes } from "./logo"
import { NXB_25V470_10_12_5 } from "./imports/NXB_25V470_10_12_5"
import { MLT_5020 } from "./imports/MLT_5020"
import { S8050_J3Y_RANGE_200_350_ as S8050 } from "./imports/S8050_J3Y_RANGE_200_350_"
import { CR2032_______3V as CoinCell } from "./imports/CR2032_______3V"
import { ESP32_WROOM_32E_N4 as Wroom } from "./imports/ESP32_WROOM_32E_N4"

// Identity stamp version (commit date + short SHA), computed once per render.
const ID = boardVersionParts()

export default () => (
  <board layers={4} outline={[{ x: -66.9, y: -51 }, { x: 60.9, y: -51 }, { x: 60.9, y: 47.7 }, { x: -66.9, y: 47.7 }]} minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" pcbStyle={{ silkscreenFontSize: "0.8mm" }} autorouter={{ traceClearance: 0.45 }}>
    {/* DS3231SN RTC + CR2032 backup, in the bay below the ESP (the freed DS3231-
        module footprint). The 20 mm coin holder (BT1) is the bulk; U6 (the SOIC) sits
        to its right, its 0.1uF decoupler (C6) tucked against U6's VCC pin on the west
        edge. CR2032 + is the wide can on the centre pad (pin2 -> VBAT); clips are - (GND). */}
    <CoinCell name="BT1" pcbX={-31.15} pcbY={-28} pcbRotation={0} />
    <Ds3231Smd name="U6" x={-9} y={-28} />
    <Cap name="C6" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-17.89} y={-21.75} rot={90} />
    <silkscreentext text="+" fontSize="1.4mm" pcbX={-31.15} pcbY={-23.5} />
    <silkscreentext text="-" fontSize="1.4mm" pcbX={-20} pcbY={-28} />
    {/* Base controller — bare ESP32-WROOM-32E (U1, C701341), no radio. rot 180 puts
        the ADC/UART/pump-A pins on the north edge and the I2C/pump-B/buzzer/IO0 pins on
        the south edge — the same north/south split the DevKitC carrier had, so the J5
        and faucet mazes re-route against the same geometry — with the antenna keepout
        pointing east into open board. 3V3 is the only supply pin (no V5): it draws from
        the step-8 LDO plane, every GND pad (incl. the centre thermal pad) auto-stitches
        to the bottom plane. Decoupling (C10 0.1uF + C11 10uF bulk) and the EN power-on
        RC (R7 10k pull-up + C12 1uF) sit just north by the 3V3/EN pins; R8 (10k) pulls
        IO0 up in the south gap; J12 is the 6-pin serial programming header (TX0/RX0/IO0/
        EN/GND/3V3) in the freed west pocket. */}
    <Wroom name="U1" pcbX={-31.15} pcbY={-1} pcbRotation={180} />
    {/* Decoupling north of U1: the EN power-on RC (R7 + C12) stacked in the x=-25
        lane, hard by U1's EN pin so their EN traces stay short and clear of the J5
        maze window (which reaches y=14 to land J5's signals on U1's north-edge
        GPIO). The supply decouplers C10 + C11 share the y=15.42 lane to the east;
        C10's ref-des sits on the +X side, away from C12. All read bottom-to-top. */}
    <resistor name="R7" resistance="10k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C25804"] }} {...at(-25.0, 12.5)} />
    <capacitor name="C12" capacitance="1uF" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C15849"] }} {...at(-25.0, 17.05)} />
    <Cap name="C10" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={-20.5} y={15.42} rot={90} lab={[1.85, 0]} />
    <Cap name="C11" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-15.0} y={15.42} rot={90} />
    <resistor name="R8" resistance="10k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C25804"] }} pcbRotation={90} {...at(-40, -13.5)} />
    <Jst name="J12" x={-50} y={-1} count={6} labels={["3V3", "EN", "IO0", "RX0", "TX0", "GND"]} rot={90} label="PROG" />
    {/* RS-485 to the front display (J9). THVD1426 auto-direction transceiver (U7):
        no host DE/RE — /RE tied low (always receive), /SHDN tied high (always on),
        only D (from ESP TX) and R (to ESP RX) are driven. R6 = 120R line termination
        across A/B; D1 = SM712 ESD array at the J9 cable entry; C7 decouples VCC. */}
    <Thvd1426 name="U7" x={-13} y={30} />
    <resistor name="R6" resistance="120" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22787"] }} {...at(-7, 30)} />
    <Sm712 name="D1" x={-3} y={37} rot={0} />
    <capacitor name="C7" capacitance="0.1uF" footprint="0805" supplierPartNumbers={{ jlcpcb: ["C49678"] }} pcbRotation={0} {...at(-10.52, 36.43)} />
    {/* 5V -> 3V3 LDO (U9, AMS1117-3.3) in the freed bay above the ESP. Becomes the
        board's 3V3 source — the ESP module no longer feeds net.V3V3 (its onboard
        regulator self-powers it). VIN off the 5V plane, VOUT to the 3V3 plane, both
        via barrels/stitch; C8 (10uF) input bypass; C9 (22uF) output bypass. */}
    <Ams1117_33 name="U9" x={-45} y={22} />
    <Cap name="C8" capacitance="10uF" footprint="0805" jlcpcb="C15850" x={-48.5} y={16} rot={90} />
    <Cap name="C9" capacitance="22uF" footprint="0805" jlcpcb="C45783" x={-51.4} y={22.15} rot={90} />
    <Mcp23017 name="U2" x={22} y={30} addr="0x20" rot={270} />
    <Mcp23017 name="U3" x={22} y={-30} addr="0x21" rot={90} />
    <Uln2803 name="U4" x={36} y={19.1} />
    <Uln2803 name="U5" x={36} y={-19.1} />
    <MLT_5020 name="U8" {...at(-56, -33)} />
    <S8050 name="Q1" {...at(-56, -39)} />
    <resistor name="R5" resistance="1k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C21190"] }} {...at(-52, -39)} />
    <Jst name="J1" x={44.7} y={19.1} count={9} labels={[...ulnOUT].reverse()} rot={90} label="MANIFOLD A" labelDir={1} />
    <Jst name="J2" x={44.7} y={-19.1} count={6} labels={["COM", "FAN", "OUT4", "OUT3", "OUT2", "OUT1"]} rot={90} label="MANIFOLD B" labelDir={1} />
    <Jst name="J3" x={-40.63} y={42.65} count={4} labels={["GND", "V5", "IO33", "IO35"]} rot={0} label="FAUCET" />
    <Jst name="J4" x={-62.0} y={3} count={6} labels={["GND", "IO15", "V5", "IO14", "IO13", "3V3"]} rot={90} label="SENSORS" />
    <Jst name="J5" x={-31.15} y={-46} count={9} labels={["GND", "IO16", "IO17", "IO27", "IO5", "IO26", "IO18", "IO25", "IO19"]} rot={0} label="DRIVER" />
    <Jst name="J8" x={-62.0} y={-11.3} count={2} labels={["GND", "V5"]} rot={90} label="5V" />
    <Jst name="J6" x={25} y={38.65} count={5} labels={["GND", "RA4", "RA3", "RA2", "RA1"]} rot={0} label="REEDS A" />
    <Jst name="J7" x={19} y={-38.65} count={7} labels={["RB1", "RB2", "RB3", "RB4", "CLO", "CHI", "GND"]} rot={0} label="REEDS B" />
    <Jst name="J9" x={-1.7} y={42.65} count={3} labels={["A", "B", "ERTH"]} rot={0} label="DISPLAY" />
    <Jst name="J10" x={56.0} y={0} count={2} labels={["GND", "V12"]} rot={90} label="12V" labelDir={1} />
    <Jst name="J11" x={-26.47} y={42.65} count={4} labels={["GND", "V5", "AOUT", "DOUT"]} rot={0} label="GAS" />
    {/* GAS dividers: step the MQ-6's 0-5 V AOUT/DOUT down to ~3.0 V on-board, so a
        plain sensor cable is safe (IO36/IO39 are NOT 5 V tolerant). Each output is
        a vertical 2-resistor series: 2.2k (input, bottom) -> midpoint -> 3.3k (to
        GND, top) -> 5*3.3/5.5 = 3.0 V (safely under 3.3 V, still a valid logic HIGH
        for DOUT). The midpoint taps right into the ESP; AOUT: R1/R2 -> IO39, DOUT:
        R3/R4 -> IO36 (IO36/IO39, the ADC1 pins on the ESP top row below the dividers). */}
    <resistor name="R1" resistance="2.2k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C4190"] }} pcbRotation={0} {...at(-16.42, 40.9)} />
    <resistor name="R2" resistance="3.3k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22978"] }} pcbRotation={0} {...at(-16.42, 44.4)} />
    <resistor name="R3" resistance="2.2k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C4190"] }} pcbRotation={0} {...at(-10.48, 40.9)} />
    <resistor name="R4" resistance="3.3k" footprint="0603" supplierPartNumbers={{ jlcpcb: ["C22978"] }} pcbRotation={0} {...at(-10.48, 44.4)} />

    {/* 3V3 rail -> inner1 plane. U9 (LDO) sources it from 5V; the I2C devices (both
        MCPs, DS3231), RS485, and the sensor loom common to it at their barrels. The
        ESP module's onboard regulator self-powers it off 5V — its 3V3 pin is left
        unconnected so it doesn't fight the LDO (the bare ESP in step 9 will take 3V3
        from this plane instead). */}
    <trace from=".U9 > .VOUT" to="net.V3V3" />
    <trace from=".U9 > .VIN" to="net.V5" />
    <trace from=".U9 > .GND" to="net.GND" />
    <trace from=".C8 > .pin1" to="net.V5" />
    <trace from=".C8 > .pin2" to="net.GND" />
    <trace from=".C9 > .pin1" to="net.V3V3" />
    <trace from=".C9 > .pin2" to="net.GND" />
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

    {/* 5V rail -> inner2 plane. J8 feeds it; faucet, sensors, and gas common to it at
        their barrels; the buzzer high side (U8 +) auto-stitches to it. The bare WROOM
        draws no 5V (3V3-only). */}
    <trace from=".J8 > .V5" to="net.V5" />
    <trace from=".J3 > .V5" to="net.V5" />
    <trace from=".J4 > .V5" to="net.V5" />
    <trace from=".J11 > .V5" to="net.V5" />
    <trace from=".U8 > ._POS" to="net.V5" />

    {/* grounds (every GND pin -> the bottom plane) */}
    <trace from=".U3 > .GND" to="net.GND" />
    <trace from=".U2 > .GND" to="net.GND" />
    <trace from=".U6 > .GND" to="net.GND" />
    <trace from=".C6 > .pin2" to="net.GND" />

    {/* RTC backup: CR2032 + (centre pad pin2) -> VBAT; clips/holes (-) -> GND. */}
    <trace from=".U6 > .VBAT" to=".BT1 > .pin2" />
    <trace from=".BT1 > .pin1" to="net.GND" />
    <trace from=".BT1 > .pin3" to="net.GND" />
    <trace from=".BT1 > .pin4" to="net.GND" />
    <trace from=".BT1 > .pin5" to="net.GND" />

    {/* I2C bus — routed top bus, not poured (two co-located nets) */}
    <trace from=".U1 > .IO21" to=".U6 > .SDA" />
    <trace from=".U1 > .IO22" to=".U6 > .SCL" />
    <trace from=".U2 > .SDA" to=".U3 > .SDA" />
    <trace from=".U2 > .SCL" to=".U3 > .SCL" />
    <trace from=".U1 > .IO21" to=".U3 > .SDA" />
    <trace from=".U1 > .IO22" to=".U3 > .SCL" />

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
    <Cap name="C4" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={15.4} y={36.55} rot={90} />
    <Cap name="C5" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={30.33} y={-36.25} rot={90} lab={[1.85, 0]} />
    <trace from=".C4 > .pin1" to="net.V3V3" />
    <trace from=".C4 > .pin2" to="net.GND" />
    <trace from=".C5 > .pin1" to="net.V3V3" />
    <trace from=".C5 > .pin2" to="net.GND" />

    {/* GPA -> ULN inputs, GPA_k -> IN_{8-k} (GPA0->IN8 ... GPA7->IN1), so the firmware
        valve mapping is unchanged; inside the ULN, channel j is IN_j -> OUT_j -> J.OUT_j
        (valve-control.mmd). pretty="clean:..." fans each pair as a riser + 45° landing at
        build time (pretty-routes.ts): U2->U4 from the GPA row, U5->U3 from the IN column. */}
    <trace from=".U2 > .GPA0" to=".U4 > .IN8" pretty="clean:fanRowToColumn" />
    <trace from=".U2 > .GPA1" to=".U4 > .IN7" pretty="clean:fanRowToColumn" />
    <trace from=".U2 > .GPA2" to=".U4 > .IN6" pretty="clean:fanRowToColumn" />
    <trace from=".U2 > .GPA3" to=".U4 > .IN5" pretty="clean:fanRowToColumn" />
    <trace from=".U2 > .GPA4" to=".U4 > .IN4" pretty="clean:fanRowToColumn" />
    <trace from=".U2 > .GPA5" to=".U4 > .IN3" pretty="clean:fanRowToColumn" />
    <trace from=".U2 > .GPA6" to=".U4 > .IN2" pretty="clean:fanRowToColumn" />
    <trace from=".U2 > .GPA7" to=".U4 > .IN1" pretty="clean:fanRowToColumn" />
    <trace from=".U3 > .GPA0" to=".U5 > .IN8" pretty="clean:fanRowToColumn" />
    <trace from=".U3 > .GPA1" to=".U5 > .IN7" pretty="clean:fanRowToColumn" />
    <trace from=".U3 > .GPA2" to=".U5 > .IN6" pretty="clean:fanRowToColumn" />
    <trace from=".U3 > .GPA3" to=".U5 > .IN5" pretty="clean:fanRowToColumn" />
    <trace from=".U3 > .GPA4" to=".U5 > .IN4" pretty="clean:fanRowToColumn" />
    <trace from=".U3 > .GPA5" to=".U5 > .IN3" pretty="clean:fanRowToColumn" />
    <trace from=".U3 > .GPA6" to=".U5 > .IN2" pretty="clean:fanRowToColumn" />
    <trace from=".U3 > .GPA7" to=".U5 > .IN1" pretty="clean:fanRowToColumn" />

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

    {/* FAUCET UART (IO33 TX / IO35 RX). pretty="maze:faucet485" climbs both signals
        from the FAUCET connector down to the ESP far row at build time (pretty-routes.ts). */}
    <trace from=".J3 > .IO33" to=".U1 > .IO33" />
    <trace from=".J3 > .IO35" to=".U1 > .IO35" />
    <trace from=".J3 > .GND" to="net.GND" />

    {/* SENSORS: flow (IO15) / 1-wire temps (IO14) / backflow drip-pan moisture
        (IO13). 3V3 powers the DS18B20 probes + the moisture module; V5 the flow
        sensor. */}
    <trace from=".J4 > .IO14" to=".U1 > .IO14" />
    <trace from=".J4 > .IO15" to=".U1 > .IO15" />
    <trace from=".J4 > .IO13" to=".U1 > .IO13" />
    <trace from=".J4 > .GND" to="net.GND" />

    {/* DRIVER: pump A (27/25/26) + pump B (19/18/5) + relays (17/16). pretty="maze:j5"
        hands each signal to the 2nd-pass maze router (pretty-routes.ts), which routes it
        at build time from live pad geometry — fanning past BT1's coin-cell pad, mostly on
        the bottom layer under it. No coordinates are frozen here; move J5/BT1/the ESP and
        the next build re-routes. The GND pin pours to the plane (not routed). */}
    <trace from=".J5 > .IO27" to=".U1 > .IO27" />
    <trace from=".J5 > .IO25" to=".U1 > .IO25" />
    <trace from=".J5 > .IO26" to=".U1 > .IO26" />
    <trace from=".J5 > .IO19" to=".U1 > .IO19" />
    <trace from=".J5 > .IO18" to=".U1 > .IO18" />
    <trace from=".J5 > .IO5" to=".U1 > .IO5" />
    <trace from=".J5 > .IO17" to=".U1 > .IO17" />
    <trace from=".J5 > .IO16" to=".U1 > .IO16" />
    <trace from=".J5 > .GND" to="net.GND" />

    {/* (J5 driver copper is generated at build time from the pretty="maze:j5" traces
        above — see pretty-routes.ts. Nothing is frozen here.) */}

    {/* 5V in (J8, labeled "5V" to pair with the "12V" connector): rail via the
        plane; ground here */}
    <trace from=".J8 > .GND" to="net.GND" />

    {/* REEDS A (reservoir A) -> 0x20 GPB inputs. pretty="clean:fanRowToColumn" fans J6 up. */}
    <trace from=".J6 > .RA1" to=".U2 > .GPB0" />
    <trace from=".J6 > .RA2" to=".U2 > .GPB1" />
    <trace from=".J6 > .RA3" to=".U2 > .GPB2" />
    <trace from=".J6 > .RA4" to=".U2 > .GPB3" />
    <trace from=".J6 > .GND" to="net.GND" />

    {/* REEDS B (reservoir B + carbonator low/high) -> 0x21 GPB inputs. pretty="clean:fanRowToColumn" fans J7 down. */}
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

    {/* BUZZER: MLT-5020 passive magnetic transducer (C94598) in the pocket below the
        ESP, low-side switched by Q1 (S8050 NPN, C2146) so IO4's ~12 mA source isn't
        asked to sink the buzzer's ~100 mA coil. Tone on IO4 (LEDC) -> R5 (1k base) ->
        Q1 base; Q1 collector sinks U8 -, emitter to the GND plane; U8 + on the 5 V
        plane. Left-to-right buzzer -> Q1 -> R5 -> IO4 toward the ESP. */}
    <trace from=".U8 > ._NEG" to=".Q1 > .C" />
    <trace from=".Q1 > .E" to="net.GND" />
    <trace from=".Q1 > .B" to=".R5 > .pin1" />
    <trace from=".R5 > .pin2" to=".U1 > .IO4" />

    {/* GAS: ACEIRMC MQ-6 combustible / refrigerant-leak sensor, mounted low on the
        rear cabinet floor (catches dense R-600a pooling). 5 V heater supply. BOTH
        MQ-6 outputs swing 0-5 V; each is stepped to ~3.0 V by an on-board divider
        (R1/R2, R3/R4 above) before the ESP, since IO36/IO39 are NOT 5 V tolerant:
          AOUT (analog level)          -> R1/R2 -> IO39 (ADC1) — trend + warm-up sense
          DOUT (LM393 comparator trip) -> R3/R4 -> IO36       — the hardware gas trip
        Own connector, isolated from the SENSORS loom, so the fire-safety run is
        unambiguous. DOUT is the signal a firmware-INDEPENDENT compressor interlock
        must consume; that interlock (a 74LVC1G08 gating IO17 -> J5) is NOT yet on
        this board — it needs two bench-verified polarities first (see notes). */}
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
        BOM 1) centered in the valley between the two ULNs it feeds, soaking the
        inrush + flyback dump the ceramics can't. Every pin1 -> V12, pin2 -> GND
        plane — no routing, no vias, barrel pickup like every power pin; the top V12
        island floods the whole valve block. C3 is polarized: pin1 (+) is V12. */}
    <Cap name="C1" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={39} y={-27.5} rot={90} />
    <Cap name="C2" capacitance="0.1uF" footprint="0805" jlcpcb="C49678" x={39.2} y={10.9} rot={90} />
    <NXB_25V470_10_12_5 name="C3" {...at(34.1, -2.2)} />
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
        monocolor silk via logo.ts) centered over the centered name + version,
        stacked in the open lower-right pocket with even vertical spacing. Bottom
        line sits on the 2.0mm bottom margin (rendered bottom y=-49). The version
        is the firmware scheme (firmware/pre_build.py): commit date + short SHA,
        a trailing `+` from uncommitted edits — a pure function of the commit,
        naming which source tree a fabbed board came from. CENTER_X=43 centers the
        block in the pocket. */}
    {logoRoutes(43, -40.87, 5).map((route, i) => (
      <silkscreenpath key={`logo${i}`} strokeWidth="0.15mm" route={route} />
    ))}
    <silkscreentext text="HOME SODA MACHINE" fontSize="2mm" anchorAlignment="center" pcbX={43} pcbY={-45.57} />
    <silkscreentext text={`${ID.date} ${ID.rev}`} fontSize="2mm" anchorAlignment="center" pcbX={43} pcbY={-48.37} />

    {/* Power planes, top->bottom: V12 island (top, over the valve block), 3V3
        (inner1, full flood), 5V (inner2, full flood), GND (bottom, full flood).
        Every ground/3V3/5V/12V pin lands on its net and commons to the plane at
        its through-hole barrel, so none of these nets is individually routed. */}
    <trace from=".J10 > .V12" to="net.V12" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" boardEdgeMargin="0.5mm" />
    <copperpour name="V12PLANE" layer="top" connectsTo="net.V12"
      outline={[{ x: 35, y: -34 }, { x: 60, y: -34 }, { x: 60, y: 34 }, { x: 35, y: 34 }]} />
    <copperpour name="V3V3PLANE" layer="inner1" connectsTo="net.V3V3" boardEdgeMargin="0.5mm" />
    <copperpour name="V5PLANE" layer="inner2" connectsTo="net.V5" boardEdgeMargin="0.5mm" />
  </board>
)
