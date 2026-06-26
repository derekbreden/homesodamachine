/**
 * esp32-mcp-mini — the controller carrier. Off-the-shelf modules plug into
 * 2.54 mm header sockets; the board is the interconnect, and every off-board
 * interface lands on a labeled edge connector (J1-J11). Footprint geometry
 * lives in ./carrier_parts; placement + routing are declared here.
 *
 * Left column top->bottom: RS485, ESP32, DS3231. MCP stack (0x20 over 0x21) with
 * the ULN drivers and manifold connectors to the right. The buzzer tucks into the
 * pocket below the ESP; the gas dividers sit at the far-left edge.
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

export default () => (
  <board layers={4} outline={[{ x: -67, y: -51 }, { x: 61, y: -51 }, { x: 61, y: 49.5 }, { x: -67, y: 49.5 }]} minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.5mm" autorouter={{ traceClearance: 0.55 }}>
    <Ds3231 name="U6" x={-37.15} y={-27.65} rot={0} />
    <Esp32 x={-31.15} y={-1} />
    <Rs485 name="U7" x={-29.0} y={26.375} rot={180} />
    <Mcp23017 name="U2" x={14.5} y={20.25} addr="0x20" />
    <Mcp23017 name="U3" x={14.5} y={-20.25} addr="0x21" />
    <Uln2803 name="U4" x={39.65} y={23.02} />
    <Uln2803 name="U5" x={39.65} y={-17.48} />
    <Buzzer name="U8" x={-6} y={-33} rot={180} />
    <Jst name="J1" x={56.0} y={23.02} count={9} labels={[...ulnOUT].reverse()} rot={90} label="MANIFOLD A" labelDir={1} />
    <Jst name="J2" x={56.0} y={-13.67} count={6} labels={["COM", "FAN", "OUT4", "OUT3", "OUT2", "OUT1"]} rot={90} label="MANIFOLD B" labelDir={1} />
    <Jst name="J3" x={-30.0} y={42.65} count={4} labels={["GND", "V5", "IO33", "IO35"]} rot={0} label="FAUCET" />
    <Jst name="J4" x={-62.0} y={3} count={6} labels={["GND", "IO15", "V5", "IO14", "IO13", "3V3"]} rot={90} label="SENSORS" />
    <Jst name="J5" x={-27.0} y={-46} count={9} labels={["GND", "IO16", "IO17", "IO27", "IO5", "IO26", "IO18", "IO25", "IO19"]} rot={0} label="DRIVER" />
    <Jst name="J8" x={-52.0} y={-43.3} count={2} labels={["GND", "V5"]} rot={0} label="POWER" />
    <Jst name="J6" x={12.5} y={44.4} count={5} labels={["GND", "RA1", "RA2", "RA3", "RA4"]} rot={0} label="REEDS A" />
    <Jst name="J7" x={13.0} y={-46} count={7} labels={["GND", "CARBHI", "CARBLO", "RB4", "RB3", "RB2", "RB1"]} rot={0} label="REEDS B" />
    <Jst name="J9" x={-46.0} y={42.65} count={3} labels={["EARTH", "B", "A"]} rot={0} label="DISPLAY" />
    <Jst name="J10" x={56.0} y={5} count={2} labels={["GND", "V12"]} rot={90} label="12V" />
    <Jst name="J11" x={-62.0} y={-25} count={4} labels={["GND", "V5", "AOUT", "DOUT"]} rot={90} label="GAS" />
    {/* GAS dividers: step the MQ-6's 0-5 V AOUT/DOUT down to ~3.0 V on-board, so a
        plain sensor cable is safe (IO36/IO39 are NOT 5 V tolerant). Each output is
        a vertical 2-resistor series: 2.2k (input, bottom) -> midpoint -> 3.3k (to
        GND, top) -> 5*3.3/5.5 = 3.0 V (safely under 3.3 V, still a valid logic HIGH
        for DOUT). The midpoint taps right into the ESP; AOUT: R1/R2 -> IO39, DOUT:
        R3/R4 -> IO36 (the two ADC pins at the ESP top row's left end). */}
    <resistor name="R1" resistance="2.2k" footprint="axial_p2.54mm" pcbRotation={90} {...at(-60, -14.6)} />
    <resistor name="R2" resistance="3.3k" footprint="axial_p2.54mm" pcbRotation={90} {...at(-60, -9.6)} />
    <resistor name="R3" resistance="2.2k" footprint="axial_p2.54mm" pcbRotation={90} {...at(-64, -14.6)} />
    <resistor name="R4" resistance="3.3k" footprint="axial_p2.54mm" pcbRotation={90} {...at(-64, -9.6)} />

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

    {/* RS485 TTL side -> ESP UART */}
    <trace from=".U7T > .TXD" to=".U1A > .IO32" />
    <trace from=".U7T > .RXD" to=".U1A > .IO34" />
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

    {/* POWER in: 5V via the plane; ground here */}
    <trace from=".J8 > .GND" to="net.GND" />

    {/* REEDS A (reservoir A) -> 0x20 GPB inputs */}
    <trace from=".J6 > .RA1" to=".U2B > .GPB0" />
    <trace from=".J6 > .RA2" to=".U2B > .GPB1" />
    <trace from=".J6 > .RA3" to=".U2B > .GPB2" />
    <trace from=".J6 > .RA4" to=".U2B > .GPB3" />
    <trace from=".J6 > .GND" to="net.GND" />

    {/* REEDS B (reservoir B + carbonator low/high) -> 0x21 GPB inputs */}
    <trace from=".J7 > .RB1" to=".U3B > .GPB0" />
    <trace from=".J7 > .RB2" to=".U3B > .GPB1" />
    <trace from=".J7 > .RB3" to=".U3B > .GPB2" />
    <trace from=".J7 > .RB4" to=".U3B > .GPB3" />
    <trace from=".J7 > .CARBLO" to=".U3B > .GPB4" />
    <trace from=".J7 > .CARBHI" to=".U3B > .GPB5" />
    <trace from=".J7 > .GND" to="net.GND" />
    <trace from=".U3B > .GND" to="net.GND" />

    {/* DISPLAY: RS485 line side (A/B/Earth) out to the front 4.3" config panel.
        Signal only — the panel takes its own 7-36 V power off the 12 V harness. */}
    <trace from=".J9 > .A" to=".U7L > .A" />
    <trace from=".J9 > .B" to=".U7L > .B" />
    <trace from=".J9 > .EARTH" to=".U7L > .Earth" />

    {/* 12V in: J10 feeds the ULN flyback commons (net.V12). */}
    <trace from=".U4O > .COM" to="net.V12" />
    <trace from=".U5O > .COM" to="net.V12" />
    <trace from=".J10 > .GND" to="net.GND" />
    <trace from=".U5I > .GND" to="net.GND" />

    {/* BUZZER: passive piezo in the pocket below the ESP. Tone on IO4 (LEDC); VCC
        on the 5 V plane; GND on the ground plane. */}
    <trace from=".U8 > .IO" to=".U1B > .IO4" />
    <trace from=".U8 > .GND" to="net.GND" />

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

    {/* Power planes, top->bottom: V12 island (top, over the valve block), 3V3
        (inner1, full flood), 5V (inner2, full flood), GND (bottom, full flood).
        Every ground/3V3/5V/12V pin lands on its net and commons to the plane at
        its through-hole barrel, so none of these nets is individually routed. */}
    <trace from=".U1B > .GNDb" to="net.GND" />
    <trace from=".J10 > .V12" to="net.V12" />
    <copperpour name="GNDPLANE" layer="bottom" connectsTo="net.GND" />
    <copperpour name="V12PLANE" layer="top" connectsTo="net.V12"
      outline={[{ x: 47, y: -30.5 }, { x: 60, y: -30.5 }, { x: 60, y: 40 }, { x: 47, y: 40 }]} />
    <copperpour name="V3V3PLANE" layer="inner1" connectsTo="net.V3V3" />
    <copperpour name="V5PLANE" layer="inner2" connectsTo="net.V5" />
  </board>
)
