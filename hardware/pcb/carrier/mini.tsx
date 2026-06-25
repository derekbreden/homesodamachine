/**
 * esp32-mcp-mini — the controller carrier. Off-the-shelf modules plug into
 * 2.54 mm header sockets; the board is the interconnect. Footprint geometry
 * lives in ./carrier_parts; ALL routing is declared here, where the placement
 * is visible.
 *
 * Routing idiom — exploit that each module bridges its own VCC pins together
 * and its GND pins together *internally*. The carrier routes each shared-net
 * leg (GND / 3V3 / I2C) to a DISTINCT pad of a module and lets the module
 * common them off-router. tscircuit then sees forced 2-pin nets it can't
 * re-pair, so the shared nets route as clean, via-free hops instead of one
 * wandering tree. Consequence: in the model GND/3V3 read as several fragments
 * joined only through the real modules — there is intentionally no single GND
 * net (so no pour, and no whole-net continuity check) until that is revisited.
 */
import {
  i8, Esp32, Mcp23017, Uln2803, Ds3231, Rs485, Jst, ulnOUT,
} from "./carrier_parts"

export default () => (
  <board width="112mm" height="82mm" minTraceWidth="0.2mm" traceClearance="0.4mm">
    {/* left column, top->bottom: DS3231, ESP32 (180deg), RS485 — then the MCP
        stack + ULN block to the right, manifolds on the right edge */}
    <Ds3231 name="U6" x={-21.4} y={28.9} rot={180} />
    <Esp32 x={-28.15} y={2.25} rot={180} />
    <Rs485 name="U7" x={-28.075} y={-25.125} rot={180} />
    <Mcp23017 name="U2" x={11.5} y={20.55} addr="0x20" />
    <Mcp23017 name="U3" x={11.5} y={-20.25} addr="0x21" />
    <Uln2803 name="U4" x={36.65} y={25.56} />
    <Uln2803 name="U5" x={36.65} y={-14.94} />
    <Jst name="J1" x={53} y={25.56} count={9} labels={ulnOUT} rot={90} label="MANIFOLD A" />
    <Jst name="J2" x={53} y={-14.94} count={9} labels={ulnOUT} rot={90} label="MANIFOLD B" />

    {/* ---- I2C + power: ESP bus row (now up, toward DS3231) -> DS3231 -> MCPs ---- */}
    <trace from=".U1B > .IO21" to=".U6H > .SDA" />
    <trace from=".U1B > .IO22" to=".U6H > .SCL" />
    <trace from=".U1A > .3V3" to=".U6H > .VCC" />
    <trace from=".U1B > .GNDb" to=".U6H > .GND" />
    {/* DS3231 6-pin header -> MCP 0x20 (DS taps the bus in-line) */}
    <trace from=".U6H > .SDA" to=".U2I > .SDA" />
    <trace from=".U6H > .SCL" to=".U2I > .SCL" />
    <trace from=".U6H > .VCC" to=".U2I > .VCC" />
    <trace from=".U6H > .GND" to=".U2I > .GND" />
    {/* MCP 0x20 -> 0x21: SDA/SCL on the only I2C pads; VCC/GND on distinct GPB pads */}
    <trace from=".U2I > .SDA" to=".U3I > .SDA" />
    <trace from=".U2I > .SCL" to=".U3I > .SCL" />
    <trace from=".U2B > .VCC" to=".U3B > .VCC" />
    <trace from=".U2B > .GND" to=".U3B > .GND" />

    {/* ---- ULN grounds star into a spare GPA-row ground pad on each MCP ---- */}
    <trace from=".U4I > .GND" to=".U2A > .GND" />
    <trace from=".U5I > .GND" to=".U3A > .GND" />

    {/* ---- GPA bank -> ULN inputs (clean 2-pin nets, the aligned bundle) ---- */}
    {i8.map((k) => <trace key={`u4${k}`} from={`.U2A > .GPA${k}`} to={`.U4I > .IN${k + 1}`} />)}
    {i8.map((k) => <trace key={`u5${k}`} from={`.U3A > .GPA${k}`} to={`.U5I > .IN${k + 1}`} />)}

    {/* ---- RS485 TTL side -> ESP UART + power (UART row now down, toward RS485) ---- */}
    <trace from=".U7T > .TXD" to=".U1A > .IO32" />
    <trace from=".U7T > .RXD" to=".U1A > .IO34" />
    <trace from=".U7T > .VCC" to=".U1A > .3V3" />
    <trace from=".U7T > .GND" to=".U1A > .GND" />

    {/* ---- manifold JSTs: ULN outputs -> valve looms (parallel to the OUT rows) ---- */}
    {i8.map((k) => <trace key={`j1${k}`} from={`.J1 > .OUT${k + 1}`} to={`.U4O > .OUT${k + 1}`} />)}
    <trace from=".J1 > .COM" to=".U4O > .COM" />
    {i8.map((k) => <trace key={`j2${k}`} from={`.J2 > .OUT${k + 1}`} to={`.U5O > .OUT${k + 1}`} />)}
    <trace from=".J2 > .COM" to=".U5O > .COM" />
  </board>
)
