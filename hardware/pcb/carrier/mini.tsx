/**
 * esp32-mcp-mini — the controller core on its real, calipered module footprints:
 * an ESP32-DevKitC-32E socket, two Waveshare MCP23017 boards (0x20, 0x21) on the
 * shared I2C bus, and two ULN2803A driver boards driven by 0x20/0x21's GPA banks.
 * Every footprint is the physical MODULE (2.54 mm header rows + its mounting
 * holes), not a bare chip. Through-hole, two layers.
 *
 * Module footprints from hardware/reference/{mcp23017,uln2803a} (calipered):
 *   MCP23017  38.5 x 23.3; 2x M2 holes one end; 2x 10-pin GPIO + 6-pin I2C
 *   ULN2803A  24 x 23; 2x dia-3 holes on the centreline; 2x 9-pin channel rows
 *   ESP32     2x19 @ 2.54 mm, rows 25.4 mm (1.0") apart, DevKitC-32E map
 *
 * The 0x20 + U4 unit is flipped 180deg so 0x20's I2C header faces 0x21's, putting
 * their SDA/SCL pins next to each other for a short bus hop between the two MCPs.
 * Modules carry their own pull-ups/decoupling/flyback, so the carrier adds none.
 */

const i8 = [0, 1, 2, 3, 4, 5, 6, 7]
const at = (px: number, py: number) => ({ pcbX: px, pcbY: py, schX: px / 6, schY: py / 6 })

const espA = ["3V3", "EN", "IO36", "IO39", "IO34", "IO35", "IO32", "IO33", "IO25",
  "IO26", "IO27", "IO14", "IO12", "GND", "IO13", "IO9", "IO10", "IO11", "V5"]
const espB = ["GNDb", "IO23", "IO22", "IO1", "IO3", "IO21", "GNDc", "IO19", "IO18",
  "IO5", "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "IO8", "IO7", "IO6"]

const mcpGPB = ["VCC", "GND", "GPB7", "GPB6", "GPB5", "GPB4", "GPB3", "GPB2", "GPB1", "GPB0"]
const mcpGPA = ["VCC", "GND", "GPA0", "GPA1", "GPA2", "GPA3", "GPA4", "GPA5", "GPA6", "GPA7"]
const mcpI2C = ["VCC", "GND", "SDA", "SCL", "INTA", "INTB"]
const ulnIN = ["IN1", "IN2", "IN3", "IN4", "IN5", "IN6", "IN7", "IN8", "GND"]
const ulnOUT = ["OUT1", "OUT2", "OUT3", "OUT4", "OUT5", "OUT6", "OUT7", "OUT8", "COM"]

// A stroked rectangle on the silk layer — the module's PCB outline.
const Outline = ({ x, y, w, h }: { x: number; y: number; w: number; h: number }) => (
  <silkscreenpath
    strokeWidth="0.2mm"
    route={[
      { x: x - w / 2, y: y - h / 2 },
      { x: x + w / 2, y: y - h / 2 },
      { x: x + w / 2, y: y + h / 2 },
      { x: x - w / 2, y: y + h / 2 },
      { x: x - w / 2, y: y - h / 2 },
    ]}
  />
)

// ---- ESP32-DevKitC-32E socket ----------------------------------------------
const Esp32 = ({ x, y }: { x: number; y: number }) => (
  <>
    <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pinLabels={espA} {...at(x, y + 12.7)} />
    <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pinLabels={espB} {...at(x, y - 12.7)} />
    <Outline x={x} y={y} w={52} h={28} />
    <silkscreentext text="ESP32" fontSize="3mm" pcbX={x} pcbY={y} />
    <trace from=".U1A > .3V3" to="net.V3_3" />
    <trace from=".U1A > .GND" to="net.GND" />
    <trace from=".U1B > .GNDb" to="net.GND" />
    <trace from=".U1B > .IO21" to="net.SDA" />
    <trace from=".U1B > .IO22" to="net.SCL" />
  </>
)

// ---- Waveshare MCP23017 board (23.3 x 38.5) --------------------------------
// rot=180 flips the whole module about its centre (every sub-element offset
// negates, headers turn 180deg) — pin labels/nets are unchanged, so wiring holds.
const Mcp23017 = ({ name, x, y, addr, breakout = false, rot = 0 }: { name: string; x: number; y: number; addr: string; breakout?: boolean; rot?: number }) => {
  const s = rot === 180 ? -1 : 1
  return (
    <>
      <Outline x={x} y={y} w={23.3} h={38.5} />
      <silkscreentext text={`MCP ${addr}`} fontSize="2.6mm" pcbX={x} pcbY={y} />
      <hole shape="circle" diameter="2mm" pcbX={x + s * 9.4} pcbY={y + s * 16.75} />
      <hole shape="circle" diameter="2mm" pcbX={x - s * 9.4} pcbY={y + s * 16.75} />
      <pinheader name={`${name}B`} pinCount={10} pitch="2.54mm" gender="female" footprint="pinrow10" pcbRotation={90 + rot} pinLabels={mcpGPB} {...at(x - s * 10, y + s * 1.5)} />
      <pinheader name={`${name}A`} pinCount={10} pitch="2.54mm" gender="female" footprint="pinrow10" pcbRotation={90 + rot} pinLabels={mcpGPA} {...at(x + s * 10, y + s * 1.5)} />
      <pinheader name={`${name}I`} pinCount={6} pitch="2.54mm" gender="female" footprint="pinrow6" pcbRotation={rot} pinLabels={mcpI2C} {...at(x, y + s * 17.25)} />
      <trace from={`.${name}I > .VCC`} to="net.V3_3" />
      <trace from={`.${name}I > .GND`} to="net.GND" />
      <trace from={`.${name}I > .SDA`} to="net.SDA" />
      <trace from={`.${name}I > .SCL`} to="net.SCL" />
      <trace from={`.${name}A > .VCC`} to="net.V3_3" />
      <trace from={`.${name}A > .GND`} to="net.GND" />
      <trace from={`.${name}B > .VCC`} to="net.V3_3" />
      <trace from={`.${name}B > .GND`} to="net.GND" />
      {breakout && i8.map((k) => <trace key={`a${k}`} from={`.${name}A > .GPA${k}`} to={`net.${name}_GPA${k}`} />)}
    </>
  )
}

// ---- ULN2803A board (23 x 24) ----------------------------------------------
const Uln2803 = ({ name, x, y, srcPrefix, rot = 0 }: { name: string; x: number; y: number; srcPrefix: string; rot?: number }) => {
  const s = rot === 180 ? -1 : 1
  return (
    <>
      <Outline x={x} y={y} w={23} h={24} />
      <silkscreentext text={name} fontSize="2.6mm" pcbX={x} pcbY={y} />
      <hole shape="circle" diameter="3mm" pcbX={x} pcbY={y + 8.75} />
      <hole shape="circle" diameter="3mm" pcbX={x} pcbY={y - 8.75} />
      <pinheader name={`${name}I`} pinCount={9} pitch="2.54mm" gender="female" footprint="pinrow9" pcbRotation={90 + rot} pinLabels={ulnIN} {...at(x - s * 10, y)} />
      <pinheader name={`${name}O`} pinCount={9} pitch="2.54mm" gender="female" footprint="pinrow9" pcbRotation={90 + rot} pinLabels={ulnOUT} {...at(x + s * 10, y)} />
      <trace from={`.${name}I > .GND`} to="net.GND" />
      {i8.map((k) => <trace key={`in${k}`} from={`.${name}I > .IN${k + 1}`} to={`net.${srcPrefix}${k}`} />)}
    </>
  )
}

// ---- the board -------------------------------------------------------------
// ESP dropped down level with 0x21. 0x20 + its ULN (U4) flipped 180deg so 0x20's
// I2C header sits just above 0x21's — SDA-to-SDA is a short straight hop. U4 rides
// the flip to the left; each MCP's GPA bank still feeds its ULN straight across.
export default () => (
  <board width="125mm" height="100mm" minTraceWidth="0.2mm" traceClearance="0.4mm">
    <Esp32 x={-33} y={-23} />
    <Mcp23017 name="U2" x={5.46} y={16.5} addr="0x20" breakout rot={180} />
    <Mcp23017 name="U3" x={8} y={-23} addr="0x21" breakout />
    <Uln2803 name="U4" x={-22.54} y={11.19} srcPrefix="U2_GPA" rot={180} />
    <Uln2803 name="U5" x={36} y={-17.69} srcPrefix="U3_GPA" />
  </board>
)
