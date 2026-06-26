/**
 * _mini4.tsx — 4-layer redesign of mini.tsx (working copy; promoted to mini.tsx
 * once verified). Stackup top->bottom:
 *   L1 top    : signals + V12 pour (valve block, unchanged)
 *   L2 inner1 : 3V3 plane (full flood) — logic devices common at their barrels
 *   L3 inner2 : 5V plane (bounded region, cut clear of the V12 valve block)
 *   L4 bottom : GND pour (full, unchanged)
 * 3V3 and 5V move from surface daisy-chains to inner planes; every through-hole
 * pin commons to its plane at the barrel (no vias). SDA/SCL stay a routed top bus
 * (two co-located nets pour into ugly interlocking islands). Routing is locked to
 * top+bottom so the planes stay pristine (autorouter.layerCount).
 */
import {
  i8, at, Esp32, Mcp23017, Uln2803, Ds3231, Rs485, Jst, Buzzer, ulnOUT,
} from "./carrier_parts"

export default () => (
  <board layers={4} width="146mm" height="100mm" minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" autorouter={{ traceClearance: 0.47 }}>
    <Ds3231 name="U6" x={-37.15} y={-28.65} rot={180} />
    <Esp32 x={-31.15} y={-2} />
    <Rs485 name="U7" x={-29.0} y={25.375} rot={180} />
    <Mcp23017 name="U2" x={14.5} y={20.25} addr="0x20" />
    <Mcp23017 name="U3" x={14.5} y={-20.25} addr="0x21" />
    <Uln2803 name="U4" x={39.65} y={23.02} />
    <Uln2803 name="U5" x={39.65} y={-17.48} />
    <Buzzer name="U8" x={-5} y={-32} rot={180} />
    <Jst name="J1" x={57.0} y={23.02} count={9} labels={[...ulnOUT].reverse()} rot={90} label="MANIFOLD A" labelDir={1} />
    <Jst name="J2" x={57.0} y={-17.48} count={6} labels={["COM", "FAN", "OUT4", "OUT3", "OUT2", "OUT1"]} rot={90} label="MANIFOLD B" labelDir={1} />
    <Jst name="J3" x={-30.0} y={44} count={4} labels={["GND", "V5", "IO33", "IO35"]} rot={0} label="FAUCET" />
    <Jst name="J4" x={-64.0} y={3} count={6} labels={["GND", "IO23", "V5", "IO13", "IO14", "3V3"]} rot={90} label="SENSORS" />
    <Jst name="J5" x={-25.0} y={-46} count={9} labels={["GND", "IO16", "IO17", "IO27", "IO5", "IO26", "IO18", "IO25", "IO19"]} rot={0} label="DRIVER" />
    <Jst name="J8" x={-52.0} y={-45} count={2} labels={["GND", "V5"]} rot={0} label="POWER" />
    <Jst name="J6" x={10.0} y={46} count={5} labels={["GND", "RA1", "RA2", "RA3", "RA4"]} rot={0} label="REEDS A" />
    <Jst name="J7" x={13.0} y={-46} count={7} labels={["GND", "CARBHI", "CARBLO", "RB4", "RB3", "RB2", "RB1"]} rot={0} label="REEDS B" />
    <Jst name="J9" x={-13.0} y={46} count={3} labels={["EARTH", "B", "A"]} rot={0} label="DISPLAY" />
    <Jst name="J10" x={57.0} y={5} count={2} labels={["GND", "V12"]} rot={90} label="12V" />
    <Jst name="J11" x={-64.0} y={-24} count={4} labels={["GND", "V5", "AOUT", "DOUT"]} rot={90} label="GAS" />
    {/* GAS dividers: step the MQ-6's 0-5 V AOUT/DOUT down to ~3.0 V on-board. */}
    <resistor name="R1" resistance="2.2k" footprint="axial_p2.54mm" pcbRotation={90} {...at(-62, -14)} />
    <resistor name="R2" resistance="3.3k" footprint="axial_p2.54mm" pcbRotation={90} {...at(-62, -9)} />
    <resistor name="R3" resistance="2.2k" footprint="axial_p2.54mm" pcbRotation={90} {...at(-66, -14)} />
    <resistor name="R4" resistance="3.3k" footprint="axial_p2.54mm" pcbRotation={90} {...at(-66, -9)} />

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

    {/* grounds */}
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

    {/* MCP GPA banks broken out */}
    {i8.map((k) => <trace key={`a2${k}`} from={`.U2A > .GPA${k}`} to={`net.U2_GPA${k}`} />)}
    {i8.map((k) => <trace key={`a3${k}`} from={`.U3A > .GPA${k}`} to={`net.U3_GPA${k}`} />)}

    {/* ULN U4 + MCP 0x20 grounds */}
    <trace from=".U4I > .GND" to="net.GND" />
    <trace from=".U2I > .GND" to="net.GND" />
    <trace from=".U2A > .GND" to="net.GND" />

    {/* GPA -> ULN inputs (GPA_k -> IN_{8-k}, crossing-free) */}
    {i8.map((k) => <trace key={`i4${k}`} from={`.U4I > .IN${8 - k}`} to={`net.U2_GPA${k}`} />)}
    {i8.map((k) => <trace key={`i5${k}`} from={`.U5I > .IN${8 - k}`} to={`net.U3_GPA${k}`} />)}

    {/* RS485 TTL side -> ESP UART */}
    <trace from=".U7T > .TXD" to=".U1A > .IO32" />
    <trace from=".U7T > .RXD" to=".U1A > .IO34" />
    <trace from=".U7T > .GND" to="net.GND" />

    {/* manifold JSTs: ULN outputs -> valve looms */}
    {i8.map((k) => <trace key={`j1${k}`} from={`.J1 > .OUT${k + 1}`} to={`.U4O > .OUT${k + 1}`} />)}
    <trace from=".J1 > .COM" to="net.V12" />
    <trace from=".J2 > .OUT1" to=".U5O > .OUT1" />
    <trace from=".J2 > .OUT2" to=".U5O > .OUT2" />
    <trace from=".J2 > .OUT3" to=".U5O > .OUT3" />
    <trace from=".J2 > .OUT4" to=".U5O > .OUT4" />
    <trace from=".J2 > .FAN" to=".U5O > .OUT5" />
    <trace from=".J2 > .COM" to="net.V12" />

    {/* FAUCET UART */}
    <trace from=".J3 > .IO33" to=".U1A > .IO33" />
    <trace from=".J3 > .IO35" to=".U1A > .IO35" />
    <trace from=".J3 > .GND" to="net.GND" />
    <trace from=".U1A > .GND" to="net.GND" />

    {/* SENSORS */}
    <trace from=".J4 > .IO14" to=".U1A > .IO14" />
    <trace from=".J4 > .IO23" to=".U1B > .IO23" />
    <trace from=".J4 > .IO13" to=".U1A > .IO13" />
    <trace from=".J4 > .GND" to="net.GND" />

    {/* DRIVER */}
    <trace from=".J5 > .IO27" to=".U1A > .IO27" />
    <trace from=".J5 > .IO25" to=".U1A > .IO25" />
    <trace from=".J5 > .IO26" to=".U1A > .IO26" />
    <trace from=".J5 > .IO19" to=".U1B > .IO19" />
    <trace from=".J5 > .IO18" to=".U1B > .IO18" />
    <trace from=".J5 > .IO5" to=".U1B > .IO5" />
    <trace from=".J5 > .IO17" to=".U1B > .IO17" />
    <trace from=".J5 > .IO16" to=".U1B > .IO16" />
    <trace from=".J5 > .GND" to="net.GND" />

    {/* POWER in: 5V via plane; ground here */}
    <trace from=".J8 > .GND" to="net.GND" />

    {/* REEDS A -> 0x20 GPB */}
    <trace from=".J6 > .RA1" to=".U2B > .GPB0" />
    <trace from=".J6 > .RA2" to=".U2B > .GPB1" />
    <trace from=".J6 > .RA3" to=".U2B > .GPB2" />
    <trace from=".J6 > .RA4" to=".U2B > .GPB3" />
    <trace from=".J6 > .GND" to="net.GND" />

    {/* REEDS B -> 0x21 GPB */}
    <trace from=".J7 > .RB1" to=".U3B > .GPB0" />
    <trace from=".J7 > .RB2" to=".U3B > .GPB1" />
    <trace from=".J7 > .RB3" to=".U3B > .GPB2" />
    <trace from=".J7 > .RB4" to=".U3B > .GPB3" />
    <trace from=".J7 > .CARBLO" to=".U3B > .GPB4" />
    <trace from=".J7 > .CARBHI" to=".U3B > .GPB5" />
    <trace from=".J7 > .GND" to="net.GND" />
    <trace from=".U3B > .GND" to="net.GND" />

    {/* DISPLAY: RS485 line side */}
    <trace from=".J9 > .A" to=".U7L > .A" />
    <trace from=".J9 > .B" to=".U7L > .B" />
    <trace from=".J9 > .EARTH" to=".U7L > .Earth" />

    {/* 12V in */}
    <trace from=".U4O > .COM" to="net.V12" />
    <trace from=".U5O > .COM" to="net.V12" />
    <trace from=".J10 > .GND" to="net.GND" />
    <trace from=".U5I > .GND" to="net.GND" />

    {/* BUZZER: tone on IO4; VCC on the 5V plane */}
    <trace from=".U8 > .IO" to=".U1B > .IO4" />
    <trace from=".U8 > .GND" to="net.GND" />

    {/* GAS dividers: AOUT -> R1/R2 -> IO39, DOUT -> R3/R4 -> IO36 */}
    <trace from=".J11 > .AOUT" to=".R1 > .pin1" />
    <trace from=".R1 > .pin2" to=".R2 > .pin1" />
    <trace from=".R1 > .pin2" to=".U1A > .IO39" />
    <trace from=".R2 > .pin2" to="net.GND" />
    <trace from=".J11 > .DOUT" to=".R3 > .pin1" />
    <trace from=".R3 > .pin2" to=".R4 > .pin1" />
    <trace from=".R3 > .pin2" to=".U1A > .IO36" />
    <trace from=".R4 > .pin2" to="net.GND" />
    <trace from=".J11 > .GND" to="net.GND" />

    {/* Power planes, top->bottom: V12 island (top), 3V3 (inner1, full), 5V
        (inner2, bounded clear of the valve block at x>=47), GND (bottom, full). */}
    <trace from=".U1B > .GNDb" to="net.GND" />
    <trace from=".J10 > .V12" to="net.V12" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" />
    <copperpour name="V12PLANE" layer="top" connectsTo="net.V12"
      outline={[{ x: 47, y: -30.5 }, { x: 60, y: -30.5 }, { x: 60, y: 40 }, { x: 47, y: 40 }]} />
    <copperpour name="V3V3PLANE" layer="inner1" connectsTo="net.V3V3" />
    <copperpour name="V5PLANE" layer="inner2" connectsTo="net.V5" />
  </board>
)
