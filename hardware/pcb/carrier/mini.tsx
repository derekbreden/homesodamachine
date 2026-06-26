/**
 * esp32-mcp-mini — the controller carrier. Off-the-shelf modules plug into
 * 2.54 mm header sockets; the board is the interconnect, and every off-board
 * interface lands on a labeled edge connector (J1-J11). Footprint geometry
 * lives in ./carrier_parts; placement + routing are declared here.
 *
 * Left column top->bottom: RS485, ESP32, DS3231. MCP stack (0x20 over 0x21) with
 * the ULN drivers and manifold connectors to the right. I2C bus, the
 * GPA->ULN->manifold valve chain, reed inputs, the ESP GPIO harness, the RS485
 * UART + line-out, and the 5 V / 12 V power all route to edge connectors J1-J10.
 */
import {
  i8, at, Esp32, Mcp23017, Uln2803, Ds3231, Rs485, Jst, Buzzer, ulnOUT,
} from "./carrier_parts"

export default () => (
  <board width="134mm" height="100mm" minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" autorouter={{ traceClearance: 0.47 }}>
    <Ds3231 name="U6" x={-32.15} y={-28.65} rot={180} />
    <Esp32 x={-25.15} y={-2} />
    <Rs485 name="U7" x={-29.0} y={25.375} rot={180} />
    <Mcp23017 name="U2" x={14.5} y={20.25} addr="0x20" />
    <Mcp23017 name="U3" x={14.5} y={-20.25} addr="0x21" />
    <Uln2803 name="U4" x={39.65} y={25.56} />
    <Uln2803 name="U5" x={39.65} y={-14.94} />
    <Buzzer name="U8" x={44} y={-42.5} rot={90} />
    <Jst name="J1" x={57.0} y={25.56} count={9} labels={ulnOUT} rot={90} label="MANIFOLD A" labelDir={1} />
    <Jst name="J2" x={57.0} y={-14.94} count={6} labels={["OUT1", "OUT2", "OUT3", "OUT4", "FAN", "COM"]} rot={90} label="MANIFOLD B" labelDir={1} />
    <Jst name="J3" x={-30.0} y={44} count={4} labels={["GND", "V5", "IO35", "IO33"]} rot={0} label="FAUCET" />
    <Jst name="J4" x={-63.0} y={2} count={6} labels={["GND", "V5", "3V3", "IO13", "IO23", "IO14"]} rot={90} label="SENSORS" />
    <Jst name="J5" x={-25.0} y={-46} count={9} labels={["GND", "IO16", "IO17", "IO5", "IO18", "IO19", "IO26", "IO25", "IO27"]} rot={0} label="DRIVER" />
    <Jst name="J8" x={-52.0} y={-45} count={2} labels={["GND", "V5"]} rot={0} label="POWER" />
    <Jst name="J6" x={3.0} y={46} count={5} labels={["GND", "RA1", "RA2", "RA3", "RA4"]} rot={0} label="REEDS A" />
    <Jst name="J7" x={5.0} y={-46} count={7} labels={["GND", "RB1", "RB2", "RB3", "RB4", "CARBLO", "CARBHI"]} rot={0} label="REEDS B" />
    <Jst name="J9" x={-13.0} y={46} count={3} labels={["A", "B", "EARTH"]} rot={0} label="DISPLAY" />
    <Jst name="J10" x={63.0} y={5} count={2} labels={["GND", "V12"]} rot={90} label="VALVE 12V" />
    <Jst name="J11" x={-63.0} y={-22} count={4} labels={["GND", "V5", "AOUT", "DOUT"]} rot={90} label="GAS" />
    {/* GAS dividers: step the MQ-6's 0-5 V AOUT/DOUT down to ~3.0 V on-board, so a
        plain sensor cable is safe (IO36/IO39 are NOT 5 V tolerant). Through-hole
        axial resistors, 2.2k top + 3.3k bottom -> 5*3.3/5.5 = 3.0 V (safely under
        3.3 V, still a valid logic HIGH for DOUT). AOUT: R1/R2; DOUT: R3/R4. */}
    <resistor name="R1" resistance="2.2k" footprint="axial_p2.54mm" {...at(-60, -8)} />
    <resistor name="R2" resistance="3.3k" footprint="axial_p2.54mm" {...at(-60, -15)} />
    <resistor name="R3" resistance="2.2k" footprint="axial_p2.54mm" {...at(-53, -8)} />
    <resistor name="R4" resistance="3.3k" footprint="axial_p2.54mm" {...at(-53, -15)} />

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

    {/* ULN U4 ground -> MCP ground; U5's ground returns through J10 (below). The
        back-side pour ties all grounds into the plane. */}
    <trace from=".U4I > .GND" to=".U2I > .GND" />

    {/* GPA -> ULN inputs */}
    {i8.map((k) => <trace key={`i4${k}`} from={`.U4I > .IN${k + 1}`} to={`net.U2_GPA${k}`} />)}
    {i8.map((k) => <trace key={`i5${k}`} from={`.U5I > .IN${k + 1}`} to={`net.U3_GPA${k}`} />)}

    {/* RS485 TTL side -> ESP UART + power (top row faces up toward RS485) */}
    <trace from=".U7T > .TXD" to=".U1A > .IO32" />
    <trace from=".U7T > .RXD" to=".U1A > .IO34" />
    <trace from=".U7T > .VCC" to=".U1A > .3V3" />
    <trace from=".U7T > .GND" to=".U1B > .GNDb" />

    {/* manifold JSTs: ULN outputs -> valve looms (parallel to the OUT rows) */}
    {i8.map((k) => <trace key={`j1${k}`} from={`.J1 > .OUT${k + 1}`} to={`.U4O > .OUT${k + 1}`} />)}
    <trace from=".J1 > .COM" to=".U4O > .COM" />
    {/* MANIFOLD B: 4 valves (V-I/V-J/V-K-A/V-K-B) on U5 ch1-4, condenser FAN on
        U5 ch5 (0x21 GPA4), COM = 12V flyback. U5 ch6-8 are spare (not broken out). */}
    <trace from=".J2 > .OUT1" to=".U5O > .OUT1" />
    <trace from=".J2 > .OUT2" to=".U5O > .OUT2" />
    <trace from=".J2 > .OUT3" to=".U5O > .OUT3" />
    <trace from=".J2 > .OUT4" to=".U5O > .OUT4" />
    <trace from=".J2 > .FAN" to=".U5O > .OUT5" />
    <trace from=".J2 > .COM" to=".U5O > .COM" />

    {/* FAUCET UART (IO33 TX / IO35 RX) */}
    <trace from=".J3 > .IO33" to=".U1A > .IO33" />
    <trace from=".J3 > .IO35" to=".U1A > .IO35" />
    <trace from=".J3 > .V5" to=".U1A > .V5" />
    <trace from=".J3 > .GND" to=".U1A > .GND" />

    {/* SENSORS: flow (IO23) / 1-wire temps (IO14) / backflow drip-pan moisture
        (IO13). 3V3 powers the DS18B20 probes (IO14 is NOT 5 V tolerant; it is also
        the 1-wire pull-up reference) AND the moisture module (so its DO on IO13 is
        3.3 V-safe); V5 powers the 5 V flow sensor. (IO36 moved to the GAS connector
        as the MQ-6 DOUT.) */}
    <trace from=".J4 > .IO14" to=".U1A > .IO14" />
    <trace from=".J4 > .3V3" to=".U1A > .3V3" />
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

    {/* REEDS A (reservoir A) -> 0x20 GPB inputs */}
    <trace from=".J6 > .RA1" to=".U2B > .GPB0" />
    <trace from=".J6 > .RA2" to=".U2B > .GPB1" />
    <trace from=".J6 > .RA3" to=".U2B > .GPB2" />
    <trace from=".J6 > .RA4" to=".U2B > .GPB3" />
    <trace from=".J6 > .GND" to=".U2I > .GND" />

    {/* REEDS B (reservoir B + carbonator low/high) -> 0x21 GPB inputs */}
    <trace from=".J7 > .RB1" to=".U3B > .GPB0" />
    <trace from=".J7 > .RB2" to=".U3B > .GPB1" />
    <trace from=".J7 > .RB3" to=".U3B > .GPB2" />
    <trace from=".J7 > .RB4" to=".U3B > .GPB3" />
    <trace from=".J7 > .CARBLO" to=".U3B > .GPB4" />
    <trace from=".J7 > .CARBHI" to=".U3B > .GPB5" />
    <trace from=".J7 > .GND" to=".U3B > .GND" />

    {/* DISPLAY: RS485 line side (A/B/Earth) out to the front 4.3" config panel.
        Signal only — the 4.3B takes its own 7-36 V screw-terminal power straight
        off the 12 V bus harness, not through this connector. */}
    <trace from=".J9 > .A" to=".U7L > .A" />
    <trace from=".J9 > .B" to=".U7L > .B" />
    <trace from=".J9 > .EARTH" to=".U7L > .Earth" />

    {/* VALVE 12V in: feeds the ULN flyback commons + solenoid high side, and the
        valve-current ground return to the ULN grounds (power.mmd). */}
    <trace from=".J10 > .V12" to=".U4O > .COM" />
    <trace from=".J10 > .V12" to=".U5O > .COM" />
    <trace from=".J10 > .GND" to=".U4I > .GND" />
    <trace from=".J10 > .GND" to=".U5I > .GND" />

    {/* BUZZER: passive piezo. I/O takes a PWM tone from IO4 (LEDC); VCC is the
        5 V rail; GND ties into the back-side ground pour. */}
    <trace from=".U8 > .IO" to=".U1B > .IO4" />
    <trace from=".U8 > .VCC" to=".U1A > .V5" />
    <trace from=".U8 > .GND" to="net.GND" />

    {/* GAS: ACEIRMC MQ-6 combustible / refrigerant-leak sensor, mounted low on the
        rear cabinet floor (catches dense R-600a pooling). 5 V heater supply. BOTH
        MQ-6 outputs swing 0-5 V; each is stepped to ~3.3 V by an on-board divider
        (R1/R2, R3/R4 above) before the ESP, since IO36/IO39 are NOT 5 V tolerant:
          AOUT (analog level)        -> R1/R2 -> IO39 (ADC1) — trend + warm-up sense
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
    <trace from=".J11 > .V5" to=".U1A > .V5" />
    <trace from=".J11 > .GND" to="net.GND" />

    {/* Power planes. A ground pour fills the back (valve return + logic ground);
        a 12V pour covers the valve block on the front — J10 feeds the ULN flyback
        commons and the manifold COM pins, which carry the summed solenoid + fan
        current (up to three valves open at once, see fluid-topology.md). The two
        traces below name the nets so the pours bind to them. */}
    <trace from=".U1B > .GNDb" to="net.GND" />
    <trace from=".J10 > .V12" to="net.V12" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" />
    <copperpour name="V12PLANE" layer="top" connectsTo="net.V12"
      outline={[{ x: 44, y: -16 }, { x: 66, y: -16 }, { x: 66, y: 40 }, { x: 44, y: 40 }]} />
  </board>
)
