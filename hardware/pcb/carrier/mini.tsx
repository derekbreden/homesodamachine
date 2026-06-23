/**
 * esp32-mcp-mini — an ESP32 DevKitC-32E socket; two MCP23017 (DIP-28) on a
 * shared I2C bus (U2 at 0x20, U3 at 0x21); U2's GPA0-7 drive a ULN2803 (U4)
 * that sinks eight 12 V solenoid outputs on J_VA; U2's GPB and both of U3's
 * banks land on edge headers; four spare ESP32 GPIO on JE. J12 brings 12 V in
 * for the ULN common and the solenoid high side; the ESP's 3V3 pin powers the
 * MCPs. Through-hole, two layers.
 *
 * Layout: each MCP sits between its two breakout headers — GPB on the left
 * edge, GPA on the right — so every bank leaves as a straight bundle. ESP
 * socket: 2x19 @ 2.54 mm, rows 25.4 mm (1.0") apart, standard DevKitC-32E map.
 */

const i8 = [0, 1, 2, 3, 4, 5, 6, 7]
const gpa = i8.map((i) => `GPA${i}`)
const gpb = i8.map((i) => `GPB${i}`)
const valves = ["VA", "VB", "VC", "VD", "VE", "VF", "VG", "VH"]

const at = (px: number, py: number) => ({ pcbX: px, pcbY: py, schX: px / 6, schY: py / 6 })

const espA = ["3V3", "EN", "IO36", "IO39", "IO34", "IO35", "IO32", "IO33", "IO25",
  "IO26", "IO27", "IO14", "IO12", "GND", "IO13", "IO9", "IO10", "IO11", "V5"]
const espB = ["GNDb", "IO23", "IO22", "IO1", "IO3", "IO21", "GNDc", "IO19", "IO18",
  "IO5", "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "IO8", "IO7", "IO6"]
const mcpPins = {
  pin1: "GPB0", pin2: "GPB1", pin3: "GPB2", pin4: "GPB3",
  pin5: "GPB4", pin6: "GPB5", pin7: "GPB6", pin8: "GPB7",
  pin9: "VDD", pin10: "VSS", pin11: "NC1", pin12: "SCL", pin13: "SDA", pin14: "NC2",
  pin15: "A0", pin16: "A1", pin17: "A2", pin18: "RST", pin19: "INTB", pin20: "INTA",
  pin21: "GPA0", pin22: "GPA1", pin23: "GPA2", pin24: "GPA3",
  pin25: "GPA4", pin26: "GPA5", pin27: "GPA6", pin28: "GPA7",
}
const ulnPins = {
  pin1: "IN1", pin2: "IN2", pin3: "IN3", pin4: "IN4",
  pin5: "IN5", pin6: "IN6", pin7: "IN7", pin8: "IN8",
  pin9: "GND", pin10: "COM",
  pin11: "OUT8", pin12: "OUT7", pin13: "OUT6", pin14: "OUT5",
  pin15: "OUT4", pin16: "OUT3", pin17: "OUT2", pin18: "OUT1",
}

// ---- reusable units --------------------------------------------------------

const Esp32 = ({ x, y }: { x: number; y: number }) => (
  <>
    <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pinLabels={espA} {...at(x, y + 12.7)} />
    <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pinLabels={espB} {...at(x, y - 12.7)} />
    <resistor name="R1" resistance="4.7k" footprint="axial" {...at(x + 27, y + 3)} />
    <resistor name="R2" resistance="4.7k" footprint="axial" {...at(x + 27, y - 1)} />
    <trace from=".U1A > .3V3" to="net.V3_3" />
    {/* tie every ground pin, incl. the center one, so consumers reach ground short */}
    <trace from=".U1B > .GNDb" to="net.GND" />
    <trace from=".U1B > .GNDc" to="net.GND" />
    <trace from=".U1A > .GND" to="net.GND" />
    {/* I2C on IO21/IO22 — the ESP32 default Wire pins (16/17 carry the two relay
        drives in the netlist GPIO map) */}
    <trace from=".U1B > .IO21" to="net.SDA" />
    <trace from=".U1B > .IO22" to="net.SCL" />
    <trace from=".R1 > .pin1" to="net.SDA" />
    <trace from=".R1 > .pin2" to="net.V3_3" />
    <trace from=".R2 > .pin1" to="net.SCL" />
    <trace from=".R2 > .pin2" to="net.V3_3" />
    {["IO32", "IO33", "IO25", "IO26"].map((g) => <trace key={g} from={`.U1A > .${g}`} to={`net.${g}`} />)}
  </>
)

const Mcp23017 = ({ name, x, y, a0High }: { name: string; x: number; y: number; a0High: boolean }) => (
  <>
    <chip name={name} footprint="dip28_w7.62mm" pinLabels={mcpPins} {...at(x, y)} />
    <capacitor name={`${name}C`} capacitance="100nF" footprint="axial" {...at(x, y - 20)} />
    <trace from={`.${name} > .VDD`} to="net.V3_3" />
    <trace from={`.${name} > .RST`} to="net.V3_3" />
    <trace from={`.${name} > .VSS`} to="net.GND" />
    <trace from={`.${name} > .SDA`} to="net.SDA" />
    <trace from={`.${name} > .SCL`} to="net.SCL" />
    <trace from={`.${name} > .A0`} to={a0High ? "net.V3_3" : "net.GND"} />
    <trace from={`.${name} > .A1`} to="net.GND" />
    <trace from={`.${name} > .A2`} to="net.GND" />
    <trace from={`.${name}C > .pin1`} to="net.V3_3" />
    <trace from={`.${name}C > .pin2`} to="net.GND" />
    {i8.map((i) => <trace key={`a${i}`} from={`.${name} > .GPA${i}`} to={`net.${name}_GPA${i}`} />)}
    {i8.map((i) => <trace key={`b${i}`} from={`.${name} > .GPB${i}`} to={`net.${name}_GPB${i}`} />)}
  </>
)

const Uln2803 = ({ name, x, y, inPrefix }: { name: string; x: number; y: number; inPrefix: string }) => (
  <>
    <chip name={name} footprint="dip18" pinLabels={ulnPins} {...at(x, y)} />
    {/* IN1 takes GPA7, IN8 takes GPA0 — so the bundle from the MCP runs straight,
        not crossed (the MCP's GPA0 sits at the bottom of its pin column) */}
    {i8.map((i) => <trace key={`in${i}`} from={`.${name} > .IN${i + 1}`} to={`net.${inPrefix}${7 - i}`} />)}
    {i8.map((i) => <trace key={`o${i}`} from={`.${name} > .OUT${i + 1}`} to={`net.${name}_OUT${i}`} />)}
    <trace from={`.${name} > .COM`} to="net.V12" />
    <trace from={`.${name} > .GND`} to="net.GND" />
  </>
)

// A breakout header; rot=90 stands it vertical so it hugs a chip's pin column.
const EdgeBank = ({ name, x, y, labels, nets, rot = 0 }: { name: string; x: number; y: number; labels: string[]; nets: string[]; rot?: number }) => (
  <>
    <pinheader name={name} pinCount={labels.length} pitch="2.54mm" gender="male" footprint={`pinrow${labels.length}`} pinLabels={labels} pcbRotation={rot} {...at(x, y)} />
    {labels.map((lab, i) => <trace key={i} from={`.${name} > .${lab}`} to={`net.${nets[i]}`} />)}
  </>
)

const PowerIn = ({ name, x, y }: { name: string; x: number; y: number }) => (
  <>
    <pinheader name={name} pinCount={2} pitch="2.54mm" gender="male" footprint="pinrow2" pinLabels={["V12", "GND"]} {...at(x, y)} />
    <capacitor name={`${name}C`} capacitance="100uF" footprint="radial" polarized {...at(x, y - 8)} />
    <trace from={`.${name} > .V12`} to="net.V12" />
    <trace from={`.${name} > .GND`} to="net.GND" />
    <trace from={`.${name}C > .pin1`} to="net.V12" />
    <trace from={`.${name}C > .pin2`} to="net.GND" />
  </>
)

// ---- the board -------------------------------------------------------------
// Two MCP "stations" stacked vertically. Each: [GPB header | MCP | GPA side].
// GPB banks exit left, GPA banks exit right, so no bundle crosses the board.

export default () => (
  <board width="150mm" height="120mm" minTraceWidth="0.2mm" traceClearance="0.5mm">
    {/* brain + bus on the left; spares break out just above the socket */}
    <Esp32 x={-46} y={0} />
    <EdgeBank name="JE" x={-50} y={32} rot={0}
      labels={["IO32", "IO33", "IO25", "IO26", "3V3", "GND"]}
      nets={["IO32", "IO33", "IO25", "IO26", "V3_3", "GND"]} />

    {/* upper station: U2 -> ULN -> solenoids. GPB header order reversed so the
        bundle aligns with the MCP's left column (GPB0 at top). */}
    <EdgeBank name="JB" x={-14} y={31} rot={90} labels={[...gpb].reverse()} nets={[...i8].reverse().map((i) => `U2_GPB${i}`)} />
    <Mcp23017 name="U2" x={2} y={24} a0High={false} />
    <Uln2803 name="U4" x={22} y={30} inPrefix="U2_GPA" />
    <EdgeBank name="J_VA" x={40} y={30} rot={90} labels={[...valves, "COM"]} nets={[...i8.map((i) => `U4_OUT${i}`), "V12"]} />
    <PowerIn name="J12" x={54} y={40} />

    {/* lower station: U3 banks straight to headers */}
    <EdgeBank name="JD" x={-14} y={-17} rot={90} labels={[...gpb].reverse()} nets={[...i8].reverse().map((i) => `U3_GPB${i}`)} />
    <Mcp23017 name="U3" x={2} y={-24} a0High={true} />
    <EdgeBank name="JC" x={20} y={-17} rot={90} labels={gpa} nets={i8.map((i) => `U3_GPA${i}`)} />

    {/* silkscreen block labels — name each subsystem so the board reads at a glance */}
    {[
      { t: "ESP32-MCP-MINI", x: 0, y: 57, s: 4 },
      { t: "ESP32", x: -46, y: 0, s: 5 },
      { t: "SPARE GPIO", x: -50, y: 47, s: 3 },
      { t: "MCP 0x20", x: -2, y: 51, s: 3 }, // upper sub-row
      { t: "ULN2803", x: 28, y: 46, s: 2.8 }, // lower sub-row, offset right
      { t: "VALVES", x: 46, y: 51, s: 2.8 }, // upper sub-row
      { t: "12V IN", x: 58, y: 46, s: 2.8 }, // lower sub-row
      { t: "MCP 0x21", x: 2, y: -48, s: 3.5 },
    ].map((L) => (
      <silkscreentext key={L.t} text={L.t} fontSize={`${L.s}mm`} pcbX={L.x} pcbY={L.y} />
    ))}
  </board>
)
