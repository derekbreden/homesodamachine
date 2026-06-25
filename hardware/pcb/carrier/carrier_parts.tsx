/**
 * carrier_parts — geometry-only footprint templates for the esp32-mcp carrier.
 *
 * Each component here draws ONE real module's physical footprint (its 2.54 mm
 * header rows, mounting holes, silk outline + label) and nothing else. They
 * carry NO traces: every electrical connection is declared at the board level
 * in mini.tsx, where the placement is visible and the "route to a specific
 * module pad" decisions live. A module bridges its own VCC pins together and
 * its GND pins together internally, so the board can route each shared-net leg
 * to a *distinct* pad of a module and let the module common them off-router —
 * which is what keeps the shared nets (GND / 3V3 / I2C) routing as forced,
 * via-free 2-pin hops instead of one wandering tree.
 *
 * Footprints from hardware/reference/{mcp23017,uln2803a,ds3231-rtc}:
 *   MCP23017  23.3 x 38.5; 2x M2 holes one end; 2x 10-pin GPIO + 6-pin I2C
 *   ULN2803A  23 x 24;     2x dia-3 holes on the centreline; 2x 9-pin rows
 *   DS3231    38.5 x 21.3;  3x dia-2.4 holes; 6-pin header + 4-pin I2C tap
 *   ESP32     2x19 @ 2.54 mm, rows 25.4 mm (1.0") apart, DevKitC-32E map
 */

export const i8 = [0, 1, 2, 3, 4, 5, 6, 7]

// pcbX/pcbY for the PCB, with a matching schematic spot so the schematic view
// doesn't pile every part on the origin.
export const at = (px: number, py: number) => ({ pcbX: px, pcbY: py, schX: px / 6, schY: py / 6 })

// Rotate a module-local offset (ox, oy) by a whole quarter-turn `deg` (CCW, the
// tscircuit pcbRotation sense), so a module dropped at 0/90/180/270 turns every
// sub-element (holes, headers) with it.
export const rotxy = (ox: number, oy: number, deg: number): [number, number] => {
  switch (((deg % 360) + 360) % 360) {
    case 90: return [-oy, ox]
    case 180: return [-ox, -oy]
    case 270: return [oy, -ox]
    default: return [ox, oy]
  }
}

// ---- pin-label rosters (top->bottom as the module reads) -------------------
export const espA = ["3V3", "EN", "IO36", "IO39", "IO34", "IO35", "IO32", "IO33", "IO25",
  "IO26", "IO27", "IO14", "IO12", "GND", "IO13", "IO9", "IO10", "IO11", "V5"]
export const espB = ["GNDb", "IO23", "IO22", "IO1", "IO3", "IO21", "GNDc", "IO19", "IO18",
  "IO5", "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "IO8", "IO7", "IO6"]
export const mcpGPB = ["VCC", "GND", "GPB7", "GPB6", "GPB5", "GPB4", "GPB3", "GPB2", "GPB1", "GPB0"]
export const mcpGPA = ["VCC", "GND", "GPA0", "GPA1", "GPA2", "GPA3", "GPA4", "GPA5", "GPA6", "GPA7"]
export const mcpI2C = ["VCC", "GND", "SDA", "SCL", "INTA", "INTB"]
export const ulnIN = ["IN1", "IN2", "IN3", "IN4", "IN5", "IN6", "IN7", "IN8", "GND"]
export const ulnOUT = ["OUT1", "OUT2", "OUT3", "OUT4", "OUT5", "OUT6", "OUT7", "OUT8", "COM"]
export const dsH6 = ["32K", "SQW", "SCL", "SDA", "VCC", "GND"]
export const dsH4 = ["SCL", "SDA", "VCC", "GND"]
export const rs485T = ["VCC", "TXD", "RXD", "GND"]
export const rs485L = ["A", "B", "Earth"]

// A stroked rectangle on the silk layer — the module's PCB outline.
export const Outline = ({ x, y, w, h }: { x: number; y: number; w: number; h: number }) => (
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

// ---- ESP32-DevKitC-32E socket (2x19 @ 2.54, rows 25.4 apart) ---------------
// rot turns the whole socket a quarter-turn: the A/B rows swap sides and each
// row's pin order reverses, so the labels still resolve but the bus row can be
// aimed at whatever neighbour it should face.
export const Esp32 = ({ x, y, rot = 0 }: { x: number; y: number; rot?: number }) => {
  const o = (ox: number, oy: number) => rotxy(ox, oy, rot)
  const a = o(0, 12.7), b = o(0, -12.7)
  const [w, h] = rot % 180 === 0 ? [52, 28] : [28, 52]
  return (
    <>
      <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pcbRotation={rot} pinLabels={espA} {...at(x + a[0], y + a[1])} />
      <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pcbRotation={rot} pinLabels={espB} {...at(x + b[0], y + b[1])} />
      <Outline x={x} y={y} w={w} h={h} />
      <silkscreentext text="ESP32" fontSize="3mm" pcbX={x} pcbY={y} />
    </>
  )
}

// ---- Waveshare MCP23017 board (23.3 x 38.5) --------------------------------
// I2C header on the +Y edge, GPA row on +X, GPB row on -X (before rotation).
export const Mcp23017 = ({ name, x, y, addr, rot = 0 }: { name: string; x: number; y: number; addr: string; rot?: number }) => {
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
    </>
  )
}

// ---- ULN2803A board (23 x 24) ----------------------------------------------
// IN row on -X, OUT row on +X (before rotation); GND is IN pin 9, COM is OUT pin 9.
export const Uln2803 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => {
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
    </>
  )
}

// ---- DORHEA DS3231 RTC board (38.5 x 21.3) ---------------------------------
// 6-pin header at -X end, 4-pin I2C tap at +X end. BOTH headers carry SCL/SDA/
// VCC/GND, bridged internally — so the module is a clean BRIDGE: feed the bus +
// power into one header, take it out the other, two forced 2-pin hops.
export const Ds3231 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => {
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
    </>
  )
}

// ---- ALMOCN TTL-to-RS485 transceiver (51.85 x 22.75) -----------------------
// 4-pin TTL header (VCC/TXD/RXD/GND) at +X end -> ESP UART, on-board. 3-pin line
// header (A/B/Earth, re-headered from the stock screw terminal) at -X end ->
// off-board to the front 4.3" display. Auto-direction (no DE/RE); VCC at 3.3V.
export const Rs485 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => {
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
      <pinheader name={`${name}L`} pinCount={3} pitch="5.08mm" gender="female" pcbRotation={90 + rot} pinLabels={rs485L} {...at(x + pL[0], y + pL[1])} />
    </>
  )
}

// ---- JST trunk connector ---------------------------------------------------
// A board header (the off-board loom cable plugs in) with a body outline + a
// function label. Single row, in-plane body ~5.8 mm deep. The function label
// sits perpendicular to the row, offset toward the board interior so it never
// runs off the edge the connector lands on — auto from the connector's own
// position (toward 0,0), since a connector on the bottom/left edge needs the
// opposite sign from one on the top/right. labelDir overrides the sign if given.
export const Jst = ({ name, x, y, count, labels, rot = 0, label, labelDir }: { name: string; x: number; y: number; count: number; labels: string[]; rot?: number; label: string; labelDir?: number }) => {
  const len = count * 2.54 + 2
  const dep = 5.8
  const [w, h] = rot % 180 === 0 ? [len, dep] : [dep, len]
  const off = dep / 2 + 2
  const [lx, ly] = rot % 180 === 0
    ? [0, (labelDir ?? (-Math.sign(y) || -1)) * off]
    : [(labelDir ?? (-Math.sign(x) || -1)) * off, 0]
  return (
    <>
      <pinheader name={name} pinCount={count} pitch="2.54mm" gender="male" footprint={`pinrow${count}`} pcbRotation={rot} pinLabels={labels} {...at(x, y)} />
      <Outline x={x} y={y} w={w} h={h} />
      <silkscreentext text={label} fontSize="1.4mm" pcbX={x + lx} pcbY={y + ly} />
    </>
  )
}
