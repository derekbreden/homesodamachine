/**
 * esp32-mcp-mini — the controller core on its real, calipered module footprints:
 * an ESP32-DevKitC-32E socket, two Waveshare MCP23017 boards (0x20, 0x21) on the
 * shared I2C bus, two ULN2803A driver boards driven by 0x20/0x21's GPA banks, and
 * a DORHEA DS3231 RTC on the same I2C bus. Every footprint is the physical MODULE
 * (2.54 mm header rows + its mounting holes), not a bare chip. Through-hole, two
 * layers.
 *
 * Module footprints from hardware/reference/{mcp23017,uln2803a,ds3231-rtc}:
 *   MCP23017  38.5 x 23.3; 2x M2 holes one end; 2x 10-pin GPIO + 6-pin I2C
 *   ULN2803A  24 x 23; 2x dia-3 holes on the centreline; 2x 9-pin channel rows
 *   DS3231    38.5 x 21.3; 3x dia-2.4 holes; 6-pin header + 4-pin I2C tap
 *   ESP32     2x19 @ 2.54 mm, rows 25.4 mm (1.0") apart, DevKitC-32E map
 *
 * The 0x20 + U4 unit is turned a quarter-turn CCW and stacked above 0x21, which
 * swings 0x20's I2C header from its top edge round to its left edge — both MCP
 * I2C headers then open onto one shared centre-left channel where the DS3231 taps
 * in. Modules carry their own pull-ups/decoupling/flyback, so the carrier adds none.
 */

const i8 = [0, 1, 2, 3, 4, 5, 6, 7]
const at = (px: number, py: number) => ({ pcbX: px, pcbY: py, schX: px / 6, schY: py / 6 })

// Rotate a module-local offset (ox, oy) by a whole quarter-turn `deg` (CCW, the
// tscircuit pcbRotation sense), so a module can be dropped at 0/90/180/270 and
// every sub-element (holes, headers) turns with it.
const rotxy = (ox: number, oy: number, deg: number): [number, number] => {
  switch (((deg % 360) + 360) % 360) {
    case 90: return [-oy, ox]
    case 180: return [-ox, -oy]
    case 270: return [oy, -ox]
    default: return [ox, oy]
  }
}

const espA = ["3V3", "EN", "IO36", "IO39", "IO34", "IO35", "IO32", "IO33", "IO25",
  "IO26", "IO27", "IO14", "IO12", "GND", "IO13", "IO9", "IO10", "IO11", "V5"]
const espB = ["GNDb", "IO23", "IO22", "IO1", "IO3", "IO21", "GNDc", "IO19", "IO18",
  "IO5", "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "IO8", "IO7", "IO6"]

const mcpGPB = ["VCC", "GND", "GPB7", "GPB6", "GPB5", "GPB4", "GPB3", "GPB2", "GPB1", "GPB0"]
const mcpGPA = ["VCC", "GND", "GPA0", "GPA1", "GPA2", "GPA3", "GPA4", "GPA5", "GPA6", "GPA7"]
const mcpI2C = ["VCC", "GND", "SDA", "SCL", "INTA", "INTB"]
const ulnIN = ["IN1", "IN2", "IN3", "IN4", "IN5", "IN6", "IN7", "IN8", "GND"]
const ulnOUT = ["OUT1", "OUT2", "OUT3", "OUT4", "OUT5", "OUT6", "OUT7", "OUT8", "COM"]
const dsH6 = ["32K", "SQW", "SCL", "SDA", "VCC", "GND"]
const dsH4 = ["SCL", "SDA", "VCC", "GND"]
const rs485T = ["VCC", "TXD", "RXD", "GND"]
const rs485L = ["A", "B", "Earth"]

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
    {/* one 3V3 + one GND tie — the module bridges its other power/ground pins */}
    <trace from=".U1A > .3V3" to="net.V3_3" />
    <trace from=".U1A > .GND" to="net.GND" />
    <trace from=".U1B > .IO21" to="net.SDA" />
    <trace from=".U1B > .IO22" to="net.SCL" />
  </>
)

// ---- Waveshare MCP23017 board (23.3 x 38.5) --------------------------------
// rot turns the whole module a quarter-turn at a time (every offset rotates,
// headers turn with it) — pin labels/nets are unchanged, so the wiring holds.
const Mcp23017 = ({ name, x, y, addr, breakout = false, rot = 0 }: { name: string; x: number; y: number; addr: string; breakout?: boolean; rot?: number }) => {
  const o = (ox: number, oy: number) => rotxy(ox, oy, rot)
  const [w, h] = rot % 180 === 0 ? [23.3, 38.5] : [38.5, 23.3]
  const hA = o(9.4, 16.75), hB = o(-9.4, 16.75)
  const pB = o(-10, 1.5), pA = o(10, 1.5), pI = o(0, 17.25)
  return (
    <>
      <Outline x={x} y={y} w={w} h={h} />
      <silkscreentext text={`MCP ${addr}`} fontSize="2.6mm" pcbX={x} pcbY={y} />
      <hole shape="circle" diameter="2mm" pcbX={x + hA[0]} pcbY={y + hA[1]} />
      <hole shape="circle" diameter="2mm" pcbX={x + hB[0]} pcbY={y + hB[1]} />
      <pinheader name={`${name}B`} pinCount={10} pitch="2.54mm" gender="female" footprint="pinrow10" pcbRotation={90 + rot} pinLabels={mcpGPB} {...at(x + pB[0], y + pB[1])} />
      <pinheader name={`${name}A`} pinCount={10} pitch="2.54mm" gender="female" footprint="pinrow10" pcbRotation={90 + rot} pinLabels={mcpGPA} {...at(x + pA[0], y + pA[1])} />
      <pinheader name={`${name}I`} pinCount={6} pitch="2.54mm" gender="female" footprint="pinrow6" pcbRotation={rot} pinLabels={mcpI2C} {...at(x + pI[0], y + pI[1])} />
      {/* power + ground in via the I2C header only; the module bridges VCC/GND
          to its GPA/GPB rows internally, so the carrier ties one of each */}
      <trace from={`.${name}I > .VCC`} to="net.V3_3" />
      <trace from={`.${name}I > .GND`} to="net.GND" />
      <trace from={`.${name}I > .SDA`} to="net.SDA" />
      <trace from={`.${name}I > .SCL`} to="net.SCL" />
      {breakout && i8.map((k) => <trace key={`a${k}`} from={`.${name}A > .GPA${k}`} to={`net.${name}_GPA${k}`} />)}
    </>
  )
}

// ---- ULN2803A board (23 x 24) ----------------------------------------------
const Uln2803 = ({ name, x, y, srcPrefix, rot = 0 }: { name: string; x: number; y: number; srcPrefix: string; rot?: number }) => {
  const o = (ox: number, oy: number) => rotxy(ox, oy, rot)
  const [w, h] = rot % 180 === 0 ? [23, 24] : [24, 23]
  const hT = o(0, 8.75), hB = o(0, -8.75)
  const pI = o(-10, 0), pO = o(10, 0)
  return (
    <>
      <Outline x={x} y={y} w={w} h={h} />
      <silkscreentext text={name} fontSize="2.6mm" pcbX={x} pcbY={y} />
      <hole shape="circle" diameter="3mm" pcbX={x + hT[0]} pcbY={y + hT[1]} />
      <hole shape="circle" diameter="3mm" pcbX={x + hB[0]} pcbY={y + hB[1]} />
      <pinheader name={`${name}I`} pinCount={9} pitch="2.54mm" gender="female" footprint="pinrow9" pcbRotation={90 + rot} pinLabels={ulnIN} {...at(x + pI[0], y + pI[1])} />
      <pinheader name={`${name}O`} pinCount={9} pitch="2.54mm" gender="female" footprint="pinrow9" pcbRotation={90 + rot} pinLabels={ulnOUT} {...at(x + pO[0], y + pO[1])} />
      <trace from={`.${name}I > .GND`} to="net.GND" />
      {i8.map((k) => <trace key={`in${k}`} from={`.${name}I > .IN${k + 1}`} to={`net.${srcPrefix}${k}`} />)}
    </>
  )
}

// ---- DORHEA DS3231 RTC board (38.5 x 21.3) ---------------------------------
// Long axis along X. 6-pin header (32K/SQW/SCL/SDA/VCC/GND) at the -X end, the
// 4-pin I2C tap (SCL/SDA/VCC/GND) at the +X end, 3 mounting holes (the 4th
// corner left open for the coin cell). Both headers are the same bus; the
// carrier wires only the clean 4-pin tap, the 6-pin pads are on record but unused.
const Ds3231 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => {
  const o = (ox: number, oy: number) => rotxy(ox, oy, rot)
  const [w, h] = rot % 180 === 0 ? [38.5, 21.3] : [21.3, 38.5]
  const h1 = o(-10.75, -8.65), h2 = o(-10.75, 8.65), h3 = o(15.05, 8.65)
  const pH = o(-17.25, 0), pI = o(17.25, 0)
  return (
    <>
      <Outline x={x} y={y} w={w} h={h} />
      <silkscreentext text="DS3231" fontSize="2.6mm" pcbX={x} pcbY={y} />
      <hole shape="circle" diameter="2.4mm" pcbX={x + h1[0]} pcbY={y + h1[1]} />
      <hole shape="circle" diameter="2.4mm" pcbX={x + h2[0]} pcbY={y + h2[1]} />
      <hole shape="circle" diameter="2.4mm" pcbX={x + h3[0]} pcbY={y + h3[1]} />
      <pinheader name={`${name}H`} pinCount={6} pitch="2.54mm" gender="female" footprint="pinrow6" pcbRotation={90 + rot} pinLabels={dsH6} {...at(x + pH[0], y + pH[1])} />
      <pinheader name={`${name}I`} pinCount={4} pitch="2.54mm" gender="female" footprint="pinrow4" pcbRotation={90 + rot} pinLabels={dsH4} {...at(x + pI[0], y + pI[1])} />
      <trace from={`.${name}I > .SDA`} to="net.SDA" />
      <trace from={`.${name}I > .SCL`} to="net.SCL" />
      <trace from={`.${name}I > .VCC`} to="net.V3_3" />
      <trace from={`.${name}I > .GND`} to="net.GND" />
    </>
  )
}

// ---- ALMOCN TTL-to-RS485 transceiver (51.85 x 22.75) -----------------------
// Long axis along X. The 4-pin TTL header (VCC/TXD/RXD/GND, 2.54mm) at the +X end
// wires to the ESP on-board (the SIG-7 hop becomes copper). The stock 5.08mm screw
// terminal at the -X end is desoldered and re-headered so the module plugs in there
// too; its A/B/Earth land on the carrier (3-pin, 5.08mm) and exit off-board to the
// front 4.3" display. A/B/Earth are unwired here (Earth is an isolated shield ref,
// not GND; A/B await the display-side connector). Auto-direction (no DE/RE); VCC at
// 3.3V. Straight-through UART: ESP IO32(TX)->TXD, IO34(RX)<-RXD (IO34 is input-only,
// so it must land on the module's MCU-facing output, RXD).
const Rs485 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => {
  const o = (ox: number, oy: number) => rotxy(ox, oy, rot)
  const [w, h] = rot % 180 === 0 ? [51.85, 22.75] : [22.75, 51.85]
  const h1 = o(-23.8, -9.5), h2 = o(-23.8, 9.5), h3 = o(23.8, -9.5), h4 = o(23.8, 9.5)
  const pT = o(18.725, 0), pL = o(-21.925, 0)
  return (
    <>
      <Outline x={x} y={y} w={w} h={h} />
      <silkscreentext text="RS485" fontSize="2.6mm" pcbX={x} pcbY={y} />
      <hole shape="circle" diameter="2mm" pcbX={x + h1[0]} pcbY={y + h1[1]} />
      <hole shape="circle" diameter="2mm" pcbX={x + h2[0]} pcbY={y + h2[1]} />
      <hole shape="circle" diameter="2mm" pcbX={x + h3[0]} pcbY={y + h3[1]} />
      <hole shape="circle" diameter="2mm" pcbX={x + h4[0]} pcbY={y + h4[1]} />
      <pinheader name={`${name}T`} pinCount={4} pitch="2.54mm" gender="female" footprint="pinrow4" pcbRotation={90 + rot} pinLabels={rs485T} {...at(x + pT[0], y + pT[1])} />
      {/* line side: stock 5.08mm screw terminal desoldered + re-headered, so the
          module plugs in here too; A/B/Earth land on the carrier and exit off-board */}
      <pinheader name={`${name}L`} pinCount={3} pitch="5.08mm" gender="female" pcbRotation={90 + rot} pinLabels={rs485L} {...at(x + pL[0], y + pL[1])} />
      {/* TTL side -> ESP, on-board; line side A/B/Earth off-board, unwired */}
      <trace from={`.${name}T > .VCC`} to="net.V3_3" />
      <trace from={`.${name}T > .GND`} to="net.GND" />
      <trace from={`.${name}T > .TXD`} to=".U1A > .IO32" />
      <trace from={`.${name}T > .RXD`} to=".U1A > .IO34" />
    </>
  )
}

// ---- the board -------------------------------------------------------------
// The module arrangement is unchanged in its relative placement (0x20+U4 turned a
// quarter-turn above 0x21, both MCP I2C headers on the shared centre channel, the
// RS485 / ESP / DS3231 left column). Two whole-cluster moves: (1) the left column
// was raised so the RS485's bottom edge lines up with 0x21's bottom edge; (2) the
// whole cluster is then centred at the origin with a uniform 15 mm border on every
// side — empty perimeter for the JST trunk connectors (5 mm module->connector,
// ~5 mm connector body, 5 mm connector->edge). Used area 108.3 x 94.8; board
// 138.3 x 124.8. Relative geometry (and its routing) is preserved.
export default () => (
  <board width="138.3mm" height="124.8mm" minTraceWidth="0.2mm" traceClearance="0.4mm">
    <Esp32 x={-28.15} y={-5.65} />
    <Mcp23017 name="U2" x={22.1} y={7.75} addr="0x20" breakout rot={90} />
    <Mcp23017 name="U3" x={14.5} y={-28.15} addr="0x21" breakout />
    <Uln2803 name="U4" x={16.79} y={35.9} srcPrefix="U2_GPA" rot={90} />
    <Uln2803 name="U5" x={42.65} y={-22.84} srcPrefix="U3_GPA" />
    <Ds3231 name="U6" x={-21.4} y={24.1} rot={180} />
    <Rs485 name="U7" x={-28.15} y={-36.025} rot={180} />
  </board>
)
