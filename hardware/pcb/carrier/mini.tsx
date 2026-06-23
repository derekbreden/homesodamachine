/**
 * esp32-mcp-mini — an ESP32 DevKitC-32E socket; two MCP23017 (DIP-28) on a
 * shared I2C bus (U2 at 0x20, U3 at 0x21); U2's GPA0-7 drive a ULN2803 (U4)
 * that sinks eight 12 V solenoid outputs on J_VA; U2's GPB and both of U3's
 * banks land on edge headers; four spare ESP32 GPIO on JE. J12 brings 12 V in
 * for the ULN common and the solenoid high side; the ESP's 3V3 pin powers the
 * MCPs. Through-hole, two layers.
 *
 * Each repeated unit is a component that ties its own pins to global named nets
 * (V3_3, GND, SDA, SCL, V12) and exposes its banks as `<ref>_GPA{i}` / `_GPB{i}`
 * / `_OUT{i}` nets; the board below composes them. ESP socket: 2x19 @ 2.54 mm,
 * rows 25.4 mm (1.0") apart, standard DevKitC-32E 38-pin map.
 */

const i8 = [0, 1, 2, 3, 4, 5, 6, 7]
const gpa = i8.map((i) => `GPA${i}`)
const gpb = i8.map((i) => `GPB${i}`)
const valves = ["VA", "VB", "VC", "VD", "VE", "VF", "VG", "VH"]

// pcb position + a matching, spread-out schematic position from one origin
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
// ULN2803A: pin1-8 IN, pin9 GND, pin10 COM, pin11-18 OUT8..OUT1.
const ulnPins = {
  pin1: "IN1", pin2: "IN2", pin3: "IN3", pin4: "IN4",
  pin5: "IN5", pin6: "IN6", pin7: "IN7", pin8: "IN8",
  pin9: "GND", pin10: "COM",
  pin11: "OUT8", pin12: "OUT7", pin13: "OUT6", pin14: "OUT5",
  pin15: "OUT4", pin16: "OUT3", pin17: "OUT2", pin18: "OUT1",
}

// ---- reusable units --------------------------------------------------------

// ESP32 DevKitC socket: two 1x19 female rows 25.4 mm apart, the I2C pull-ups,
// and the bus/power/spare-GPIO tied to named nets.
const Esp32 = ({ x, y }: { x: number; y: number }) => (
  <>
    <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pinLabels={espA} {...at(x, y + 12.7)} />
    <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pinLabels={espB} {...at(x, y - 12.7)} />
    <resistor name="R1" resistance="4.7k" footprint="axial" {...at(x + 30, y + 4)} />
    <resistor name="R2" resistance="4.7k" footprint="axial" {...at(x + 30, y)} />
    <trace from=".U1A > .3V3" to="net.V3_3" />
    <trace from=".U1B > .GNDb" to="net.GND" />
    <trace from=".U1B > .IO21" to="net.SDA" />
    <trace from=".U1B > .IO22" to="net.SCL" />
    <trace from=".R1 > .pin1" to="net.SDA" />
    <trace from=".R1 > .pin2" to="net.V3_3" />
    <trace from=".R2 > .pin1" to="net.SCL" />
    <trace from=".R2 > .pin2" to="net.V3_3" />
    {["IO32", "IO33", "IO25", "IO26"].map((g) => <trace key={g} from={`.U1A > .${g}`} to={`net.${g}`} />)}
  </>
)

// MCP23017: chip + decoupling, address straps (A0 high = 0x21, low = 0x20),
// power + I2C to named nets, GPA/GPB banks exposed as `<name>_GPA{i}`/`_GPB{i}`.
const Mcp23017 = ({ name, x, y, a0High }: { name: string; x: number; y: number; a0High: boolean }) => (
  <>
    <chip name={name} footprint="dip28_w7.62mm" pinLabels={mcpPins} {...at(x, y)} />
    <capacitor name={`${name}C`} capacitance="100nF" footprint="axial" {...at(x - 14, y)} />
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

// ULN2803: eight low-side sinks. IN1-8 pulled from `${inPrefix}{i}` nets, OUT1-8
// exposed as `<name>_OUT{i}`, clamp common on 12 V.
const Uln2803 = ({ name, x, y, inPrefix }: { name: string; x: number; y: number; inPrefix: string }) => (
  <>
    <chip name={name} footprint="dip18" pinLabels={ulnPins} {...at(x, y)} />
    {i8.map((i) => <trace key={`in${i}`} from={`.${name} > .IN${i + 1}`} to={`net.${inPrefix}${i}`} />)}
    {i8.map((i) => <trace key={`o${i}`} from={`.${name} > .OUT${i + 1}`} to={`net.${name}_OUT${i}`} />)}
    <trace from={`.${name} > .COM`} to="net.V12" />
    <trace from={`.${name} > .GND`} to="net.GND" />
  </>
)

// A breakout header: each pin `labels[i]` wired to `nets[i]`.
const EdgeBank = ({ name, x, y, labels, nets }: { name: string; x: number; y: number; labels: string[]; nets: string[] }) => (
  <>
    <pinheader name={name} pinCount={labels.length} pitch="2.54mm" gender="male" footprint={`pinrow${labels.length}`} pinLabels={labels} {...at(x, y)} />
    {labels.map((lab, i) => <trace key={i} from={`.${name} > .${lab}`} to={`net.${nets[i]}`} />)}
  </>
)

// 12 V input + bulk cap.
const PowerIn = ({ name, x, y }: { name: string; x: number; y: number }) => (
  <>
    <pinheader name={name} pinCount={2} pitch="2.54mm" gender="male" footprint="pinrow2" pinLabels={["V12", "GND"]} {...at(x, y)} />
    <capacitor name={`${name}C`} capacitance="100uF" footprint="radial" polarized {...at(x + 16, y)} />
    <trace from={`.${name} > .V12`} to="net.V12" />
    <trace from={`.${name} > .GND`} to="net.GND" />
    <trace from={`.${name}C > .pin1`} to="net.V12" />
    <trace from={`.${name}C > .pin2`} to="net.GND" />
  </>
)

// ---- the board -------------------------------------------------------------

export default () => (
  <board width="175mm" height="125mm">
    <Esp32 x={-55} y={0} />
    <PowerIn name="J12" x={-58} y={46} />

    <Mcp23017 name="U2" x={2} y={30} a0High={false} />
    <Mcp23017 name="U3" x={2} y={-28} a0High={true} />
    <Uln2803 name="U4" x={30} y={32} inPrefix="U2_GPA" />

    {/* U2's GPA bank -> ULN -> eight solenoids + 12 V common */}
    <EdgeBank name="J_VA" x={58} y={40} labels={[...valves, "COM"]} nets={[...i8.map((i) => `U4_OUT${i}`), "V12"]} />
    {/* the other three banks straight to edge headers */}
    <EdgeBank name="JB" x={58} y={14} labels={gpb} nets={i8.map((i) => `U2_GPB${i}`)} />
    <EdgeBank name="JC" x={58} y={-20} labels={gpa} nets={i8.map((i) => `U3_GPA${i}`)} />
    <EdgeBank name="JD" x={58} y={-40} labels={gpb} nets={i8.map((i) => `U3_GPB${i}`)} />
    {/* spare ESP32 GPIO + power */}
    <EdgeBank name="JE" x={-58} y={-44}
      labels={["IO32", "IO33", "IO25", "IO26", "3V3", "GND"]}
      nets={["IO32", "IO33", "IO25", "IO26", "V3_3", "GND"]} />
  </board>
)
