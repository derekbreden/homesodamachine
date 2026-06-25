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
  <board width="116mm" height="82mm" minTraceWidth="0.2mm" traceClearance="0.4mm">
    <Ds3231 name="U6" x={-35.15} y={-28.65} rot={180} />
    <Esp32 x={-28.15} y={-2} />
    <Rs485 name="U7" x={-28.15} y={25.375} rot={180} />
    <Mcp23017 name="U2" x={11.5} y={20.25} addr="0x20" />
    <Mcp23017 name="U3" x={11.5} y={-20.25} addr="0x21" />
    <Uln2803 name="U4" x={36.65} y={25.56} />
    <Uln2803 name="U5" x={36.65} y={-14.94} />
    <Jst name="J1" x={54} y={25.56} count={9} labels={ulnOUT} rot={90} label="MANIFOLD A" />
    <Jst name="J2" x={54} y={-14.94} count={9} labels={ulnOUT} rot={90} label="MANIFOLD B" />

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
  </board>
)
