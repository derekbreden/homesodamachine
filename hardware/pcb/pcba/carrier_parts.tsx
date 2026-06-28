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
export const rs485L = ["A", "B", "ERTH"]
// 3-pin header across the body's +Y end; pin1->pin3 run GND/IO/VCC from -X to
// +X, matching the module's pad order so each labelled pad lands on its pin.
export const buzz = ["GND", "IO", "VCC"]

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
  // WROOM PCB antenna: an 18 x 6 mm keepout off the 3V3 short end. The socket is
  // soldered SILK-SIDE-UP, so U1A/U1B carry the DevKitC columns reversed (pin1
  // lands at +X), putting the 3V3 short end at +X — where this keepout sits. It
  // turns with the module so neighbours / stacked boards stay clear in any rot.
  const ant = o(29, 0)
  const [aw, ah] = rot % 180 === 0 ? [6, 18] : [18, 6]
  return (
    <>
      {/* Both rows read their labels toward the body centre (inside the fence,
          flanking the ESP32 mark). U1B's near row already does; U1A is the far
          row, so it flips its pin labels + ref-des to its inner side. */}
      <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19_flippinlabels" pcbRotation={rot} pinLabels={[...espA].reverse()} {...at(x + a[0], y + a[1])} />
      <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female" footprint="pinrow19" pcbRotation={rot} pinLabels={[...espB].reverse()} {...at(x + b[0], y + b[1])} />
      <Outline x={x} y={y} w={w} h={h} />
      <Outline x={x + ant[0]} y={y + ant[1]} w={aw} h={ah} />
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
      {/* Labels read toward the body centre (inside the fence): the +X GPA row
          already does; the -X GPB row and the +Y I2C tap flip to their inner side. */}
      <pinheader name={`${name}B`} pinCount={10} pitch="2.54mm" gender="female" footprint="pinrow10_flippinlabels" pcbRotation={90 + rot} pinLabels={mcpGPB} {...at(x + pB[0], y + pB[1])} />
      <pinheader name={`${name}A`} pinCount={10} pitch="2.54mm" gender="female" footprint="pinrow10" pcbRotation={90 + rot} pinLabels={mcpGPA} {...at(x + pA[0], y + pA[1])} />
      <pinheader name={`${name}I`} pinCount={6} pitch="2.54mm" gender="female" footprint="pinrow6_flippinlabels" pcbRotation={rot} pinLabels={mcpI2C} {...at(x + pI[0], y + pI[1])} />
    </>
  )
}

// ---- ULN2803A board (23 x 24) ----------------------------------------------
// IN row on -X, OUT row on +X (before rotation). Soldered SILK-SIDE-UP, so the
// two 9-pin rows run reversed: IN1/OUT1 land at +Y, GND/COM at -Y.
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
      {/* Labels read toward the body centre (inside the fence): the +X OUT row
          already does; the -X IN row flips its pin labels + ref-des to its inner side. */}
      <pinheader name={`${name}I`} pinCount={9} pitch="2.54mm" gender="female" footprint="pinrow9_flippinlabels" pcbRotation={90 + rot} pinLabels={[...ulnIN].reverse()} {...at(x + pI[0], y + pI[1])} />
      <pinheader name={`${name}O`} pinCount={9} pitch="2.54mm" gender="female" footprint="pinrow9" pcbRotation={90 + rot} pinLabels={[...ulnOUT].reverse()} {...at(x + pO[0], y + pO[1])} />
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
      {/* Labels read toward the body centre (inside the fence): the +X I2C tap
          already does; the -X 6-pin header flips its labels + ref-des to its inner side. */}
      <pinheader name={`${name}H`} pinCount={6} pitch="2.54mm" gender="female" footprint="pinrow6_flippinlabels" pcbRotation={90 + rot} pinLabels={dsH6} {...at(x + pH[0], y + pH[1])} />
      <pinheader name={`${name}I`} pinCount={4} pitch="2.54mm" gender="female" footprint="pinrow4" pcbRotation={90 + rot} pinLabels={dsH4} {...at(x + pI[0], y + pI[1])} />
    </>
  )
}

// ---- ALMOCN TTL-to-RS485 transceiver (51.85 x 22.75) -----------------------
// 4-pin TTL header (VCC/TXD/RXD/GND) at +X end -> ESP UART, on-board. 3-pin line
// header (A/B/ERTH, re-headered from the stock screw terminal) at -X end ->
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

// ---- DIYables passive piezo buzzer module (13 x 32) ------------------------
// 3-pin header (GND/IO/VCC) across the +Y short end; a dia-4.2 mounting hole
// just below body centre; "BUZZER" tucked into the empty -Y end clear of both.
// The I/O pin takes a PWM tone straight from an ESP GPIO (LEDC) — VCC is the 5 V
// rail, GND the logic ground.
export const Buzzer = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => {
  const o = (ox: number, oy: number) => rotxy(ox, oy, rot)
  const [w, h] = rot % 180 === 0 ? [13, 32] : [32, 13]
  const hM = o(0, -0.6), pP = o(0, 12.5), lbl = o(0, -9)
  return (
    <>
      <Outline x={x} y={y} w={w} h={h} />
      {/* Horizontal label, offset into the body's empty end (clear of the centre
          mounting hole + the pin row); the offset rotates with the module but the
          glyphs stay readable rather than turning with it. */}
      <silkscreentext text="BUZZER" fontSize="1.8mm" pcbX={x + lbl[0]} pcbY={y + lbl[1]} />
      <hole shape="circle" diameter="4.2mm" pcbX={x + hM[0]} pcbY={y + hM[1]} />
      <pinheader name={name} pinCount={3} pitch="2.54mm" gender="female" footprint="pinrow3" pcbRotation={rot} pinLabels={buzz} {...at(x + pP[0], y + pP[1])} />
    </>
  )
}

// XH2.54 vertical THT male wafer connectors (JLCPCB assembly), keyed by pin count.
// The "2.54" is the market label; the parts are genuine 2.5 mm-pitch XH (mate with
// standard female JST-XH 2.54 housings). XUNPU WAFER-XH2.54-NPZZ / Megastar
// ZX-XH2.54-NPZZ — see jlcpcb-parts.md.
const XH254_BY_COUNT: Record<number, string> = {
  2: "C5359631", 3: "C7429633", 4: "C7429634", 5: "C5359633",
  6: "C5359634", 7: "C5359635", 9: "C7429639",
}

// ---- JST trunk connector ---------------------------------------------------
// A board header (the off-board loom cable plugs in): a fence holding the pin
// row, the function label, the pin labels and the ref-des. Laid out for a
// horizontal row — function label one side, pin labels + ref-des the other —
// then placed for the connector's orientation so a vertical one is the horizontal
// turned a quarter-turn and every label reads the same way (bottom-to-top
// vertical, left-to-right horizontal). The pin labels are drawn here, not by the
// footprint (whose auto labels lock vertical rows to top-to-bottom); the footprint
// string is pads-only. Margins to the fence are even on all four sides; labelDir
// flips the function label to the loom-facing side (clear of the trunk traces).
export const Jst = ({ name, x, y, count, labels, rot = 0, label, labelDir, jlcpcb }: { name: string; x: number; y: number; count: number; labels: string[]; rot?: number; label: string; labelDir?: number; jlcpcb?: string }) => {
  const vertical = rot % 180 !== 0
  const pitch = 2.5, padR = 0.825                   // XH 2.5 mm pitch, 1.65 mm pad radius
  const bigHalf = 0.42, smHalf = 0.24               // ink cap half-heights (0.6 × font size)
  const G = 0.45, M = 0.6                            // even tier gap; even content -> fence margin
  // perpDir = the side the function label sits on (pin labels + ref-des opposite).
  // Defaults toward the board centre; labelDir overrides where the loom dictates.
  const perpDir = vertical ? (labelDir ?? (-Math.sign(x) || -1)) : 1
  const bigOff = padR + G + bigHalf                 // row -> function label
  const labelOff = padR + G + smHalf                // row -> pin label
  const refOff = labelOff + smHalf + G + smHalf     // row -> ref-des (one tier beyond pin labels)
  const uc = ((bigOff + bigHalf) - (refOff + smHalf)) / 2     // fence centre, perpendicular
  const dep = (bigOff + bigHalf) + (refOff + smHalf) + 2 * M + 0.2  // +0.2 fence stroke
  const len = (count - 1) * pitch + 2 * (padR + M + 0.1)
  const [w, h] = vertical ? [dep, len] : [len, dep]
  const P = (u: number, v: number): [number, number] => (vertical ? [perpDir * u, v] : [v, perpDir * u])
  const [bdx, bdy] = P(bigOff, 0)
  const [rdx, rdy] = P(-refOff, 0)
  const [fdx, fdy] = P(uc, 0)
  return (
    <>
      <pinheader name={name} pinCount={count} pitch="2.5mm" gender="male" footprint={`pinrow${count}_p2.5mm_id1.1mm_od1.65mm_nopinlabels_norefdes`} pcbRotation={rot} pinLabels={labels} supplierPartNumbers={(() => { const p = jlcpcb ?? XH254_BY_COUNT[count]; return p ? { jlcpcb: [p] } : undefined })()} {...at(x, y)} />
      <Outline x={x + fdx} y={y + fdy} w={w} h={h} />
      {labels.map((lbl, i) => {
        const [dx, dy] = P(-labelOff, (i - (count - 1) / 2) * pitch)
        return <silkscreentext key={i} text={lbl} fontSize="0.8mm" pcbX={x + dx} pcbY={y + dy} pcbRotation={rot} />
      })}
      <silkscreentext text={label} fontSize="1.4mm" pcbX={x + bdx} pcbY={y + bdy} pcbRotation={rot} />
      <silkscreentext text={name} fontSize="0.8mm" pcbX={x + rdx} pcbY={y + rdy} pcbRotation={rot} />
    </>
  )
}
