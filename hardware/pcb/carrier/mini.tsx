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
import {
  i8, at, Esp32, Mcp23017, Uln2803, Ds3231, Rs485, Jst, Buzzer, ulnOUT,
} from "./carrier_parts"
import { boardVersionParts } from "./board-version"
import { logoRoutes } from "./logo"

// Identity stamp version (commit date + short SHA), computed once per render.
const ID = boardVersionParts()

export default () => (
  <board layers={4} outline={[{ x: -66.9, y: -51 }, { x: 60.9, y: -51 }, { x: 60.9, y: 47.7 }, { x: -66.9, y: 47.7 }]} minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" pcbStyle={{ silkscreenFontSize: "0.8mm" }} autorouter={{ traceClearance: 0.45 }}>
    <Ds3231 name="U6" x={-27.25} y={-28.65} rot={0} />
    <Esp32 x={-31.15} y={-1} />
    <Rs485 name="U7" x={-29.0} y={26.375} rot={180} />
    <Mcp23017 name="U2" x={14.5} y={18.65} addr="0x20" />
    <Mcp23017 name="U3" x={14.5} y={-21.85} addr="0x21" />
    <Uln2803 name="U4" x={39.65} y={21.42} />
    <Uln2803 name="U5" x={39.65} y={-19.08} />
    <Buzzer name="U8" x={-55} y={-33} />
    <Jst name="J1" x={56.0} y={21.42} count={9} labels={[...ulnOUT].reverse()} rot={90} label="MANIFOLD A" labelDir={1} />
    <Jst name="J2" x={56.0} y={-15.27} count={6} labels={["COM", "FAN", "OUT4", "OUT3", "OUT2", "OUT1"]} rot={90} label="MANIFOLD B" labelDir={1} />
    <Jst name="J3" x={-40.63} y={42.65} count={4} labels={["GND", "V5", "IO33", "IO35"]} rot={0} label="FAUCET" />
    <Jst name="J4" x={-62.0} y={3} count={6} labels={["GND", "IO15", "V5", "IO14", "IO13", "3V3"]} rot={90} label="SENSORS" />
    <Jst name="J5" x={-27.0} y={-46} count={9} labels={["GND", "IO16", "IO17", "IO27", "IO5", "IO26", "IO18", "IO25", "IO19"]} rot={0} label="DRIVER" />
    <Jst name="J8" x={-62.0} y={-11.3} count={2} labels={["GND", "V5"]} rot={90} label="5V" />
    <Jst name="J6" x={12.5} y={42.8} count={5} labels={["GND", "RA1", "RA2", "RA3", "RA4"]} rot={0} label="REEDS A" />
    <Jst name="J7" x={13.0} y={-46} count={7} labels={["GND", "CHI", "CLO", "RB4", "RB3", "RB2", "RB1"]} rot={0} label="REEDS B" />
    <Jst name="J9" x={-1.7} y={42.65} count={3} labels={["A", "B", "ERTH"]} rot={0} label="DISPLAY" />
    <Jst name="J10" x={56.0} y={-0.7233} count={2} labels={["GND", "V12"]} rot={90} label="12V" labelDir={1} />
    <Jst name="J11" x={-26.47} y={42.65} count={4} labels={["GND", "V5", "AOUT", "DOUT"]} rot={0} label="GAS" />
    {/* GAS dividers: step the MQ-6's 0-5 V AOUT/DOUT down to ~3.0 V on-board, so a
        plain sensor cable is safe (IO36/IO39 are NOT 5 V tolerant). Each output is
        a vertical 2-resistor series: 2.2k (input, bottom) -> midpoint -> 3.3k (to
        GND, top) -> 5*3.3/5.5 = 3.0 V (safely under 3.3 V, still a valid logic HIGH
        for DOUT). The midpoint taps right into the ESP; AOUT: R1/R2 -> IO39, DOUT:
        R3/R4 -> IO36 (IO36/IO39, the ADC1 pins on the ESP top row below the dividers). */}
    <resistor name="R1" resistance="2.2k" footprint="axial_p2.54mm" pcbRotation={0} {...at(-16.42, 40.9)} />
    <resistor name="R2" resistance="3.3k" footprint="axial_p2.54mm" pcbRotation={0} {...at(-16.42, 44.4)} />
    <resistor name="R3" resistance="2.2k" footprint="axial_p2.54mm" pcbRotation={0} {...at(-10.48, 40.9)} />
    <resistor name="R4" resistance="3.3k" footprint="axial_p2.54mm" pcbRotation={0} {...at(-10.48, 44.4)} />

    {/* 3V3 rail -> inner1 plane. ESP 3V3 sources it; the I2C devices (both MCPs,
        DS3231), RS485, and the sensor loom common to it at their barrels. */}
    <trace from=".U1A > .3V3" to="net.V3V3" />
    <trace from=".U2I > .VCC" to="net.V3V3" />
    <trace from=".U2B > .VCC" to="net.V3V3" />
    <trace from=".U3I > .VCC" to="net.V3V3" />
    <trace from=".U3B > .VCC" to="net.V3V3" />
    <trace from=".U6H > .VCC" to="net.V3V3" />
    <trace from=".U7T > .VCC" to="net.V3V3" />
    <trace from=".J4 > .3V3" to="net.V3V3" />

    {/* 5V rail -> inner2 plane. J8 feeds it; ESP V5, faucet, sensors, gas, and the
        buzzer common to it at their barrels. */}
    <trace from=".U1A > .V5" to="net.V5" />
    <trace from=".J8 > .V5" to="net.V5" />
    <trace from=".J3 > .V5" to="net.V5" />
    <trace from=".J4 > .V5" to="net.V5" />
    <trace from=".J11 > .V5" to="net.V5" />
    <trace from=".U8 > .VCC" to="net.V5" />

    {/* grounds (every GND pin -> the bottom plane) */}
    <trace from=".U3I > .GND" to="net.GND" />
    <trace from=".U2B > .GND" to="net.GND" />
    <trace from=".U6H > .GND" to="net.GND" />
    <trace from=".U3A > .GND" to="net.GND" />
    <trace from=".U1B > .GNDc" to="net.GND" />
    <trace from=".U6I > .GND" to="net.GND" />

    {/* I2C bus — routed top bus, not poured (two co-located nets) */}
    <trace from=".U1B > .IO21" to=".U6I > .SDA" />
    <trace from=".U1B > .IO22" to=".U6I > .SCL" />
    <trace from=".U2I > .SDA" to=".U3I > .SDA" />
    <trace from=".U2I > .SCL" to=".U3I > .SCL" />
    <trace from=".U1B > .IO21" to=".U3I > .SDA" />
    <trace from=".U1B > .IO22" to=".U3I > .SCL" />

    {/* I2C bus, maze-routed: the MCP<->MCP backbone (U2I<->U3I) is a clean vertical
        pair on top; the ESP feeds the backbone bottom (U3I) and taps the RTC (U6I) —
        all octilinear, no vias. Each <pcbtrace> carves its segment from the autorouter;
        the <trace>s above stay the netlist. Generated by _maze.ts (i2c). */}
    {/* U2I.SDA -> U3I.SDA — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:13.23,y:35.9,width:0.2,layer:"top"},
      {route_type:"wire",x:13.23,y:-4.6,width:0.2,layer:"top"},
    ]} />
    {/* U2I.SCL -> U3I.SCL — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:15.77,y:35.9,width:0.2,layer:"top"},
      {route_type:"wire",x:15.77,y:-4.6,width:0.2,layer:"top"},
    ]} />
    {/* U1B.IO21 -> U3I.SDA — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-20.99,y:-13.7,width:0.2,layer:"top"},
      {route_type:"wire",x:-13.8,y:-6.5,width:0.2,layer:"top"},
      {route_type:"wire",x:11.3,y:-6.5,width:0.2,layer:"top"},
      {route_type:"wire",x:13.23,y:-4.6,width:0.2,layer:"top"},
    ]} />
    {/* U1B.IO22 -> U3I.SCL — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-13.37,y:-13.7,width:0.2,layer:"top"},
      {route_type:"wire",x:-6.7,y:-7,width:0.2,layer:"top"},
      {route_type:"wire",x:13.4,y:-7,width:0.2,layer:"top"},
      {route_type:"wire",x:15.77,y:-4.6,width:0.2,layer:"top"},
    ]} />
    {/* U1B.IO21 -> U6I.SDA — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-20.99,y:-13.7,width:0.2,layer:"top"},
      {route_type:"wire",x:-21,y:-18.9,width:0.2,layer:"top"},
      {route_type:"wire",x:-10,y:-29.92,width:0.2,layer:"top"},
    ]} />
    {/* U1B.IO22 -> U6I.SCL — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-13.37,y:-13.7,width:0.2,layer:"top"},
      {route_type:"wire",x:-8.8,y:-18.3,width:0.2,layer:"top"},
      {route_type:"wire",x:-8.8,y:-31.3,width:0.2,layer:"top"},
      {route_type:"wire",x:-10,y:-32.46,width:0.2,layer:"top"},
    ]} />

    {/* MCP GPA banks broken out */}
    {i8.map((k) => <trace key={`a2${k}`} from={`.U2A > .GPA${k}`} to={`net.U2_GPA${k}`} />)}
    {i8.map((k) => <trace key={`a3${k}`} from={`.U3A > .GPA${k}`} to={`net.U3_GPA${k}`} />)}

    {/* ULN U4 + MCP 0x20 grounds */}
    <trace from=".U4I > .GND" to="net.GND" />
    <trace from=".U2I > .GND" to="net.GND" />
    <trace from=".U2A > .GND" to="net.GND" />

    {/* GPA -> ULN inputs. Silk-up ULN reverses its IN row (IN1 lands at +Y), so
        GPA_k feeds IN_{8-k} to keep the bank crossing-free: GPA0->IN8 ... GPA7->IN1.
        (Re-synced in valve-control.mmd.) */}
    {i8.map((k) => <trace key={`i4${k}`} from={`.U4I > .IN${8 - k}`} to={`net.U2_GPA${k}`} />)}
    {i8.map((k) => <trace key={`i5${k}`} from={`.U5I > .IN${8 - k}`} to={`net.U3_GPA${k}`} />)}

    {/* RS485 TTL side -> ESP UART. The module's TXD (its RS485-receiver TTL output)
        lands on IO34 — the ESP UART RX, an input-only pin, all an RX needs; the
        module's RXD (driver input) is fed by IO32 — the ESP UART TX, which must be
        output-capable (IO34/35/36/39 can't drive). The transceiver's 3.3 V VCC keeps
        TXD's swing safe for input-only IO34. */}
    <trace from=".U7T > .TXD" to=".U1A > .IO34" />
    <trace from=".U7T > .RXD" to=".U1A > .IO32" />
    <trace from=".U7T > .GND" to="net.GND" />

    {/* manifold JSTs: ULN outputs -> valve looms */}
    {i8.map((k) => <trace key={`j1${k}`} from={`.J1 > .OUT${k + 1}`} to={`.U4O > .OUT${k + 1}`} />)}
    <trace from=".J1 > .COM" to="net.V12" />
    {/* MANIFOLD B: 4 valves on U5 ch1-4, condenser FAN on U5 ch5, COM = 12V flyback. */}
    <trace from=".J2 > .OUT1" to=".U5O > .OUT1" />
    <trace from=".J2 > .OUT2" to=".U5O > .OUT2" />
    <trace from=".J2 > .OUT3" to=".U5O > .OUT3" />
    <trace from=".J2 > .OUT4" to=".U5O > .OUT4" />
    <trace from=".J2 > .FAN" to=".U5O > .OUT5" />
    <trace from=".J2 > .COM" to="net.V12" />

    {/* FAUCET UART (IO33 TX / IO35 RX) */}
    <trace from=".J3 > .IO33" to=".U1A > .IO33" />
    <trace from=".J3 > .IO35" to=".U1A > .IO35" />
    <trace from=".J3 > .GND" to="net.GND" />
    <trace from=".U1A > .GND" to="net.GND" />

    {/* FAUCET + RS485 UART fan off the ESP far row, maze-routed: IO33/IO35 climb to the
        FAUCET connector on top; IO32/IO34 run on the BOTTOM layer (entering at the ESP
        and RS485 through-hole barrels) under the faucet traces to the RS485 TTL header.
        TXD->IO34 / RXD->IO32 nests the pair without a crossing, so each is a single clean
        diagonal — no vias. Each <pcbtrace> carves its connection (declared above) from the
        autorouter; the <trace>s stay the netlist. Generated by _maze.ts (faucet485). */}
    {/* J3.IO33 -> U1A.IO33 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-39.36,y:42.65,width:0.2,layer:"top"},
      {route_type:"wire",x:-26.1,y:29.3,width:0.2,layer:"top"},
      {route_type:"wire",x:-26.07,y:11.7,width:0.2,layer:"top"},
    ]} />
    {/* J3.IO35 -> U1A.IO35 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-36.82,y:42.65,width:0.2,layer:"top"},
      {route_type:"wire",x:-21,y:26.8,width:0.2,layer:"top"},
      {route_type:"wire",x:-20.99,y:11.7,width:0.2,layer:"top"},
    ]} />
    {/* U7T.TXD -> U1A.IO34 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-47.725,y:27.645,width:0.2,layer:"bottom"},
      {route_type:"wire",x:-34.3,y:27.6,width:0.2,layer:"bottom"},
      {route_type:"wire",x:-18.45,y:11.7,width:0.2,layer:"bottom"},
    ]} />
    {/* U7T.RXD -> U1A.IO32 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-47.725,y:25.105,width:0.2,layer:"bottom"},
      {route_type:"wire",x:-36.9,y:25.1,width:0.2,layer:"bottom"},
      {route_type:"wire",x:-23.53,y:11.7,width:0.2,layer:"bottom"},
    ]} />

    {/* SENSORS: flow (IO15) / 1-wire temps (IO14) / backflow drip-pan moisture
        (IO13). 3V3 powers the DS18B20 probes + the moisture module; V5 the flow
        sensor. */}
    <trace from=".J4 > .IO14" to=".U1A > .IO14" />
    <trace from=".J4 > .IO15" to=".U1B > .IO15" />
    <trace from=".J4 > .IO13" to=".U1A > .IO13" />
    <trace from=".J4 > .GND" to="net.GND" />

    {/* DRIVER: pump A (27/25/26) + pump B (19/18/5) + relays (17/16) */}
    <trace from=".J5 > .IO27" to=".U1A > .IO27" />
    <trace from=".J5 > .IO25" to=".U1A > .IO25" />
    <trace from=".J5 > .IO26" to=".U1A > .IO26" />
    <trace from=".J5 > .IO19" to=".U1B > .IO19" />
    <trace from=".J5 > .IO18" to=".U1B > .IO18" />
    <trace from=".J5 > .IO5" to=".U1B > .IO5" />
    <trace from=".J5 > .IO17" to=".U1B > .IO17" />
    <trace from=".J5 > .IO16" to=".U1B > .IO16" />
    <trace from=".J5 > .GND" to="net.GND" />

    {/* DRIVER fan, maze-routed: 8 signals split across both ESP rows — 3 climb the
        middle channel to the far U1A row (dodging the U1B pad in each shared column),
        5 land on the near U1B row. Each <pcbtrace> carves its connection from the
        autorouter; the <trace> above stays the netlist. Generated by _maze.ts (j5). */}
    {/* J5.IO27 -> U1A.IO27 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-29.54,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:-32.5,y:-43,width:0.2,layer:"top"},
      {route_type:"wire",x:-32.5,y:10.5,width:0.2,layer:"top"},
      {route_type:"wire",x:-33.69,y:11.7,width:0.2,layer:"top"},
    ]} />
    {/* J5.IO26 -> U1A.IO26 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-24.46,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:-29.9,y:-40.6,width:0.2,layer:"top"},
      {route_type:"wire",x:-29.9,y:10.5,width:0.2,layer:"top"},
      {route_type:"wire",x:-31.15,y:11.7,width:0.2,layer:"top"},
    ]} />
    {/* J5.IO25 -> U1A.IO25 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-19.38,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:-27.4,y:-38,width:0.2,layer:"top"},
      {route_type:"wire",x:-27.4,y:10.5,width:0.2,layer:"top"},
      {route_type:"wire",x:-28.61,y:11.7,width:0.2,layer:"top"},
    ]} />
    {/* J5.IO16 -> U1B.IO16 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-34.62,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:-36.2,y:-44.4,width:0.2,layer:"top"},
      {route_type:"wire",x:-36.23,y:-13.7,width:0.2,layer:"top"},
    ]} />
    {/* J5.IO17 -> U1B.IO17 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-32.08,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:-33.7,y:-44.4,width:0.2,layer:"top"},
      {route_type:"wire",x:-33.69,y:-13.7,width:0.2,layer:"top"},
    ]} />
    {/* J5.IO5 -> U1B.IO5 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-27,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:-31.1,y:-41.9,width:0.2,layer:"top"},
      {route_type:"wire",x:-31.15,y:-13.7,width:0.2,layer:"top"},
    ]} />
    {/* J5.IO18 -> U1B.IO18 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-21.92,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:-28.6,y:-39.3,width:0.2,layer:"top"},
      {route_type:"wire",x:-28.61,y:-13.7,width:0.2,layer:"top"},
    ]} />
    {/* J5.IO19 -> U1B.IO19 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:-16.84,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:-26.1,y:-36.7,width:0.2,layer:"top"},
      {route_type:"wire",x:-26.07,y:-13.7,width:0.2,layer:"top"},
    ]} />

    {/* 5V in (J8, labeled "5V" to pair with the "12V" connector): rail via the
        plane; ground here */}
    <trace from=".J8 > .GND" to="net.GND" />

    {/* REEDS A (reservoir A) -> 0x20 GPB inputs */}
    <trace from=".J6 > .RA1" to=".U2B > .GPB0" />
    <trace from=".J6 > .RA2" to=".U2B > .GPB1" />
    <trace from=".J6 > .RA3" to=".U2B > .GPB2" />
    <trace from=".J6 > .RA4" to=".U2B > .GPB3" />
    <trace from=".J6 > .GND" to="net.GND" />

    {/* REEDS A fan, maze-routed past U2's I2C header (U2I), its mounting hole, and the
        SDA bus. The two reeds that must cross the bus run on the BOTTOM layer — they
        enter at the J6 through-hole barrel (no via); the other two stay on top. 0 vias.
        Each <pcbtrace> carves its connection from the autorouter; the <trace> above
        stays the netlist. Generated by _maze.ts (j6). */}
    {/* J6.RA1 -> U2B.GPB0 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:9.96,y:42.8,width:0.2,layer:"top"},
      {route_type:"wire",x:6.5,y:39.3,width:0.2,layer:"top"},
      {route_type:"wire",x:6.5,y:33.6,width:0.2,layer:"top"},
      {route_type:"wire",x:4.5,y:31.58,width:0.2,layer:"top"},
    ]} />
    {/* J6.RA2 -> U2B.GPB1 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:12.5,y:42.8,width:0.2,layer:"bottom"},
      {route_type:"wire",x:6.5,y:36.8,width:0.2,layer:"bottom"},
      {route_type:"wire",x:6.5,y:31,width:0.2,layer:"bottom"},
      {route_type:"wire",x:4.5,y:29.04,width:0.2,layer:"bottom"},
    ]} />
    {/* J6.RA3 -> U2B.GPB2 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:15.04,y:42.8,width:0.2,layer:"top"},
      {route_type:"wire",x:11.9,y:39.7,width:0.2,layer:"top"},
      {route_type:"wire",x:11.9,y:33.9,width:0.2,layer:"top"},
      {route_type:"wire",x:4.5,y:26.5,width:0.2,layer:"top"},
    ]} />
    {/* J6.RA4 -> U2B.GPB3 — 0 vias */}
    <pcbtrace route={[
      {route_type:"wire",x:17.58,y:42.8,width:0.2,layer:"bottom"},
      {route_type:"wire",x:11.9,y:37.1,width:0.2,layer:"bottom"},
      {route_type:"wire",x:11.9,y:31.4,width:0.2,layer:"bottom"},
      {route_type:"wire",x:4.5,y:23.96,width:0.2,layer:"bottom"},
    ]} />

    {/* REEDS B (reservoir B + carbonator low/high) -> 0x21 GPB inputs */}
    <trace from=".J7 > .RB1" to=".U3B > .GPB0" />
    <trace from=".J7 > .RB2" to=".U3B > .GPB1" />
    <trace from=".J7 > .RB3" to=".U3B > .GPB2" />
    <trace from=".J7 > .RB4" to=".U3B > .GPB3" />
    <trace from=".J7 > .CLO" to=".U3B > .GPB4" />
    <trace from=".J7 > .CHI" to=".U3B > .GPB5" />
    <trace from=".J7 > .GND" to="net.GND" />
    <trace from=".U3B > .GND" to="net.GND" />

    {/* REEDS B fan, hand-routed: a nested riser+45° fan on the top layer, no vias,
        one parallel diagonal per reed (all corners at y=-25.04 — source pitch and
        GPB pitch are both 2.54). Each <pcbtrace>'s wire endpoints land on the
        connection's two pads, which the core patch reads to carve that connection
        out of the autorouter (so the pcbtrace is the net's only copper); the <trace>
        above stays as the netlist. RB1 is the autorouter's own matching path.
        Generated by clean-pass.ts from the live J7/U3B pad coordinates. */}
    {/* RB2 -> U3B.GPB1 */}
    <pcbtrace route={[
      {route_type:"wire",x:18.08,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:18.08,y:-25.04,width:0.2,layer:"top"},
      {route_type:"wire",x:4.5,y:-11.46,width:0.2,layer:"top"},
    ]} />
    {/* RB3 -> U3B.GPB2 */}
    <pcbtrace route={[
      {route_type:"wire",x:15.54,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:15.54,y:-25.04,width:0.2,layer:"top"},
      {route_type:"wire",x:4.5,y:-14,width:0.2,layer:"top"},
    ]} />
    {/* RB4 -> U3B.GPB3 */}
    <pcbtrace route={[
      {route_type:"wire",x:13,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:13,y:-25.04,width:0.2,layer:"top"},
      {route_type:"wire",x:4.5,y:-16.54,width:0.2,layer:"top"},
    ]} />
    {/* CLO -> U3B.GPB4 */}
    <pcbtrace route={[
      {route_type:"wire",x:10.46,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:10.46,y:-25.04,width:0.2,layer:"top"},
      {route_type:"wire",x:4.5,y:-19.08,width:0.2,layer:"top"},
    ]} />
    {/* CHI -> U3B.GPB5 */}
    <pcbtrace route={[
      {route_type:"wire",x:7.92,y:-46,width:0.2,layer:"top"},
      {route_type:"wire",x:7.92,y:-25.04,width:0.2,layer:"top"},
      {route_type:"wire",x:4.5,y:-21.62,width:0.2,layer:"top"},
    ]} />

    {/* DISPLAY: RS485 line side (A/B/ERTH) out to the front 4.3" config panel.
        Signal only — the panel takes its own 7-36 V power off the 12 V harness. */}
    <trace from=".J9 > .A" to=".U7L > .A" />
    <trace from=".J9 > .B" to=".U7L > .B" />
    <trace from=".J9 > .ERTH" to=".U7L > .ERTH" />

    {/* 12V in: J10 feeds the ULN flyback commons (net.V12). */}
    <trace from=".U4O > .COM" to="net.V12" />
    <trace from=".U5O > .COM" to="net.V12" />
    <trace from=".J10 > .GND" to="net.GND" />
    <trace from=".U5I > .GND" to="net.GND" />

    {/* BUZZER: passive piezo in the pocket below the ESP. Tone on IO4 (LEDC); VCC
        on the 5 V plane; GND on the ground plane. */}
    <trace from=".U8 > .IO" to=".U1B > .IO4" />
    <trace from=".U8 > .GND" to="net.GND" />
    {/* IO4 -> U8 tone line, maze-routed: a 45°/H/45° dodge that drops below the ESP
        pin row and runs the open corridor above the U8 pins past U8.VCC, no vias. The
        <pcbtrace> carves this connection from the autorouter; the <trace> above stays
        the netlist. Generated by _maze.ts (io4u8). */}
    <pcbtrace route={[
      {route_type:"wire",x:-55,y:-20.5,width:0.2,layer:"top"},
      {route_type:"wire",x:-49.6,y:-15.1,width:0.2,layer:"top"},
      {route_type:"wire",x:-40.2,y:-15.1,width:0.2,layer:"top"},
      {route_type:"wire",x:-38.77,y:-13.7,width:0.2,layer:"top"},
    ]} />

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
    <trace from=".R1 > .pin2" to=".U1A > .IO39" />
    <trace from=".R2 > .pin2" to="net.GND" />
    <trace from=".J11 > .DOUT" to=".R3 > .pin1" />
    <trace from=".R3 > .pin2" to=".R4 > .pin1" />
    <trace from=".R3 > .pin2" to=".U1A > .IO36" />
    <trace from=".R4 > .pin2" to="net.GND" />
    <trace from=".J11 > .GND" to="net.GND" />

    {/* GAS divider net, maze-routed: the two midpoint taps drop nearly straight down to
        the ESP ADC pins (R1/2 -> IO39, R3/4 -> IO36); AOUT/DOUT feed the inputs (DOUT
        threads between the R1 and R2 rows to reach R3); the R1->R2 series link takes the
        bottom layer via the resistor barrels. 0 vias. Each <pcbtrace> carves its segment
        from the autorouter; the <trace>s above stay the netlist (the GND legs stay on the
        plane). Generated by _maze.ts (divider). */}
    <pcbtrace route={[
      {route_type:"wire",x:-15.15,y:40.9,width:0.2,layer:"top"},
      {route_type:"wire",x:-15.9,y:40.2,width:0.2,layer:"top"},
      {route_type:"wire",x:-15.91,y:11.7,width:0.2,layer:"top"},
    ]} />
    <pcbtrace route={[
      {route_type:"wire",x:-9.21,y:40.9,width:0.2,layer:"top"},
      {route_type:"wire",x:-13.4,y:36.7,width:0.2,layer:"top"},
      {route_type:"wire",x:-13.37,y:11.7,width:0.2,layer:"top"},
    ]} />
    <pcbtrace route={[
      {route_type:"wire",x:-25.2,y:42.65,width:0.2,layer:"top"},
      {route_type:"wire",x:-23.5,y:40.9,width:0.2,layer:"top"},
      {route_type:"wire",x:-17.69,y:40.9,width:0.2,layer:"top"},
    ]} />
    <pcbtrace route={[
      {route_type:"wire",x:-22.66,y:42.65,width:0.2,layer:"top"},
      {route_type:"wire",x:-13.4,y:42.6,width:0.2,layer:"top"},
      {route_type:"wire",x:-11.75,y:40.9,width:0.2,layer:"top"},
    ]} />
    <pcbtrace route={[
      {route_type:"wire",x:-15.15,y:40.9,width:0.2,layer:"bottom"},
      {route_type:"wire",x:-17.7,y:43.4,width:0.2,layer:"bottom"},
      {route_type:"wire",x:-17.69,y:44.4,width:0.2,layer:"bottom"},
    ]} />
    <pcbtrace route={[
      {route_type:"wire",x:-9.21,y:40.9,width:0.2,layer:"top"},
      {route_type:"wire",x:-11.7,y:43.4,width:0.2,layer:"top"},
      {route_type:"wire",x:-11.75,y:44.4,width:0.2,layer:"top"},
    ]} />

    {/* V12 decoupling. HF: two 0.1uF ceramics (C1/C2) set into the right-edge
        connector stack, centered across the MANIFOLD fence — C2 in the gap above
        the 12V inlet, C1 below MANIFOLD B — snubbing the fast solenoid-turn-off
        edge. BULK: a 470uF low-ESR electrolytic (C3, BOM 1) in the open valley
        between the two ULNs it feeds, soaking the inrush + flyback dump the
        ceramics can't. Every pin1 -> V12, pin2 -> GND plane — no routing, no vias,
        barrel pickup like every power pin; the top V12 island floods the whole
        valve block, covering each pin1 barrel. C3 is polarized: pin1 (+) is V12. */}
    <capacitor name="C1" capacitance="0.1uF" footprint="axial_p2.54mm" pcbRotation={0} {...at(56, -26.9767)} />
    <capacitor name="C2" capacitance="0.1uF" footprint="axial_p2.54mm" pcbRotation={0} {...at(56, 5.9033)} />
    <capacitor name="C3" capacitance="470uF" footprint="radial_p5.08mm" {...at(39.65, 1.17)} />
    <silkscreentext text="+" fontSize="1.6mm" pcbX={33.5} pcbY={1.17} />
    <trace from=".C1 > .pin1" to="net.V12" />
    <trace from=".C1 > .pin2" to="net.GND" />
    <trace from=".C2 > .pin1" to="net.V12" />
    <trace from=".C2 > .pin2" to="net.GND" />
    <trace from=".C3 > .pin1" to="net.V12" />
    <trace from=".C3 > .pin2" to="net.GND" />

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
    <trace from=".U1B > .GNDb" to="net.GND" />
    <trace from=".J10 > .V12" to="net.V12" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" boardEdgeMargin="0.5mm" />
    <copperpour name="V12PLANE" layer="top" connectsTo="net.V12"
      outline={[{ x: 33.5, y: -33.2 }, { x: 60, y: -33.2 }, { x: 60, y: 35.6 }, { x: 33.5, y: 35.6 }]} />
    <copperpour name="V3V3PLANE" layer="inner1" connectsTo="net.V3V3" boardEdgeMargin="0.5mm" />
    <copperpour name="V5PLANE" layer="inner2" connectsTo="net.V5" boardEdgeMargin="0.5mm" />
  </board>
)
