/**
 * esp32-mcp-mini — the controller carrier. Off-the-shelf modules plug into
 * 2.54 mm header sockets; the board is the interconnect. Footprint geometry
 * lives in ./carrier_parts; routing is declared here.
 *
 * Left column top->bottom: DS3231, ESP32 (180deg), RS485. MCP stack + ULN block
 * to the right. Only the established MCP/ULN core routing is wired; the ESP,
 * DS3231, and RS485 are placed but not yet connected.
 */
import {
  i8, Esp32, Mcp23017, Uln2803, Ds3231, Rs485, Jst, ulnOUT,
} from "./carrier_parts"

export default () => (
  <board width="145mm" height="100mm" minTraceWidth="0.2mm" traceClearance="0.4mm">
    <Ds3231 name="U6" x={-35.15} y={-28.65} rot={180} />
    <Esp32 x={-28.15} y={-2} />
    <Rs485 name="U7" x={-28.15} y={25.375} rot={180} />
    <Mcp23017 name="U2" x={11.5} y={20.25} addr="0x20" />
    <Mcp23017 name="U3" x={11.5} y={-20.25} addr="0x21" />
    <Uln2803 name="U4" x={36.65} y={25.56} />
    <Uln2803 name="U5" x={36.65} y={-14.94} />
    <Jst name="J1" x={54} y={25.56} count={9} labels={ulnOUT} rot={90} label="MANIFOLD A" />
    <Jst name="J2" x={54} y={-14.94} count={9} labels={ulnOUT} rot={90} label="MANIFOLD B" />
    <Jst name="J3" x={-45} y={44} count={4} labels={["GND", "V5", "IO35", "IO33"]} rot={0} label="FAUCET" />
    <Jst name="J4" x={-66} y={2} count={7} labels={["GND", "V5", "IO13", "IO23", "IO39", "IO36", "IO14"]} rot={90} label="SENSORS" />
    <Jst name="J5" x={-2} y={-46} count={9} labels={["GND", "IO16", "IO17", "IO5", "IO18", "IO19", "IO26", "IO25", "IO27"]} rot={0} label="DRIVER" />
    <Jst name="J8" x={-55} y={-45} count={2} labels={["GND", "V5"]} rot={0} label="POWER" />

    {/* MCP 0x21 power -> 0x20 */}
    <trace from=".U3I > .VCC" to=".U2B > .VCC" />
    <trace from=".U3I > .GND" to=".U2B > .GND" />

    {/* I2C bus */}
    <trace from=".U1B > .IO21" to=".U6I > .SDA" />
    <trace from=".U1B > .IO22" to=".U6I > .SCL" />
    <trace from=".U2I > .SDA" to=".U3I > .SDA" />
    <trace from=".U2I > .SCL" to=".U3I > .SCL" />
    <trace from=".U1B > .IO21" to=".U3I > .SDA" />
    <trace from=".U1B > .IO22" to=".U3I > .SCL" />

    {/* DS3231 VCC / GND */}
    <trace from=".U6H > .VCC" to=".U3B > .VCC" />
    <trace from=".U6H > .GND" to=".U3A > .GND" />

    {/* ESP 3V3 + GND feed the expander power/ground (completes logic power) */}
    <trace from=".U1A > .3V3" to=".U2I > .VCC" />
    <trace from=".U1B > .GNDc" to=".U6I > .GND" />

    {/* MCP GPA banks broken out */}
    {i8.map((k) => <trace key={`a2${k}`} from={`.U2A > .GPA${k}`} to={`net.U2_GPA${k}`} />)}
    {i8.map((k) => <trace key={`a3${k}`} from={`.U3A > .GPA${k}`} to={`net.U3_GPA${k}`} />)}

    {/* ULN grounds */}
    <trace from=".U5I > .GND" to=".U2A > .GND" />
    <trace from=".U4I > .GND" to=".U2I > .GND" />

    {/* GPA -> ULN inputs */}
    {i8.map((k) => <trace key={`i4${k}`} from={`.U4I > .IN${k + 1}`} to={`net.U2_GPA${k}`} />)}
    {i8.map((k) => <trace key={`i5${k}`} from={`.U5I > .IN${k + 1}`} to={`net.U3_GPA${k}`} />)}

    {/* RS485 TTL side -> ESP UART + power (top row faces up toward RS485) */}
    <trace from=".U7T > .TXD" to=".U1A > .IO32" />
    <trace from=".U7T > .RXD" to=".U1A > .IO34" />
    <trace from=".U7T > .VCC" to=".U1A > .3V3" />
    <trace from=".U7T > .GND" to=".U1A > .GND" />

    {/* manifold JSTs: ULN outputs -> valve looms (parallel to the OUT rows) */}
    {i8.map((k) => <trace key={`j1${k}`} from={`.J1 > .OUT${k + 1}`} to={`.U4O > .OUT${k + 1}`} />)}
    <trace from=".J1 > .COM" to=".U4O > .COM" />
    {i8.map((k) => <trace key={`j2${k}`} from={`.J2 > .OUT${k + 1}`} to={`.U5O > .OUT${k + 1}`} />)}
    <trace from=".J2 > .COM" to=".U5O > .COM" />

    {/* FAUCET UART (IO33 TX / IO35 RX) */}
    <trace from=".J3 > .IO33" to=".U1A > .IO33" />
    <trace from=".J3 > .IO35" to=".U1A > .IO35" />
    <trace from=".J3 > .V5" to=".U1A > .V5" />
    <trace from=".J3 > .GND" to=".U1A > .GND" />

    {/* SENSORS: flow / 1-wire / backflow + two spare input-only pins */}
    <trace from=".J4 > .IO14" to=".U1A > .IO14" />
    <trace from=".J4 > .IO36" to=".U1A > .IO36" />
    <trace from=".J4 > .IO39" to=".U1A > .IO39" />
    <trace from=".J4 > .IO23" to=".U1B > .IO23" />
    <trace from=".J4 > .IO13" to=".U1A > .IO13" />
    <trace from=".J4 > .V5" to=".U1A > .V5" />
    <trace from=".J4 > .GND" to=".U1B > .GNDb" />

    {/* DRIVER: pump A (27/25/26) + pump B (19/18/5) + relays (17/16) */}
    <trace from=".J5 > .IO27" to=".U1A > .IO27" />
    <trace from=".J5 > .IO25" to=".U1A > .IO25" />
    <trace from=".J5 > .IO26" to=".U1A > .IO26" />
    <trace from=".J5 > .IO19" to=".U1B > .IO19" />
    <trace from=".J5 > .IO18" to=".U1B > .IO18" />
    <trace from=".J5 > .IO5" to=".U1B > .IO5" />
    <trace from=".J5 > .IO17" to=".U1B > .IO17" />
    <trace from=".J5 > .IO16" to=".U1B > .IO16" />
    <trace from=".J5 > .GND" to=".U1B > .GNDb" />

    {/* POWER in: 5V -> ESP V5 (3V3 regulated on-board) */}
    <trace from=".J8 > .V5" to=".U1A > .V5" />
    <trace from=".J8 > .GND" to=".U1B > .GNDb" />
  </board>
)
