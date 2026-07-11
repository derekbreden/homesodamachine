/**
 * parts — every component wrapper the board places, plus the placement helper the wrappers share.
 *
 * One class of part per section: the SMD chip passives (Cap/Res, with hand-drawn silk), the JST
 * field connectors (the one through-hole class), and the bare SMD silicon (WROOM, MCP, ULN, buck,
 * bridges, …) — each an imported JLCPCB footprint (real pads + origin + 3D model, so the CPL
 * rotation matches JLCPCB's library) wrapped with our pin labels and an upright ref-des that rides
 * with (x,y). `at(px,py)` is the shared placement helper: pcb coords + a scaled schematic spot.
 */
import { passiveImport } from "./imports/passives"
import { WAFER_XH2_54_3PZZ } from "./imports/WAFER_XH2_54_3PZZ"
import { WAFER_XH2_54_4PZZ } from "./imports/WAFER_XH2_54_4PZZ"
import { WAFER_XH2_54_5PZZ } from "./imports/WAFER_XH2_54_5PZZ"
import { WAFER_XH2_54_6PZZ } from "./imports/WAFER_XH2_54_6PZZ"
import { WAFER_XH2_54_7PZZ } from "./imports/WAFER_XH2_54_7PZZ"
import { WAFER_XH2_54_9PZZ } from "./imports/WAFER_XH2_54_9PZZ"
import { K7805_2000R3 } from "./imports/K7805_2000R3"
import { MLT_5020 } from "./imports/MLT_5020"
import { KH_CR2032_2_1 } from "./imports/KH_CR2032_2_1"
import { NXB_25V470_10_12_5 } from "./imports/NXB_25V470_10_12_5"
import { S8050_J3Y_RANGE_200_350_ } from "./imports/S8050_J3Y_RANGE_200_350_"
import { ULN2803A } from "./imports/ULN2803A"
import { MCP23017_E_SO } from "./imports/MCP23017_E_SO"
import { DS3231SN_T_R } from "./imports/DS3231SN_T_R"
import { COS13487EESA_3_3 } from "./imports/COS13487EESA_3_3"
import { SM712_TCT } from "./imports/SM712_TCT"
import { ESP32_WROOM_32E_N4 } from "./imports/ESP32_WROOM_32E_N4"
import { AMS1117_3_3 } from "./imports/AMS1117_3_3"
import { CH340C } from "./imports/CH340C"
import { USBLC6_2SC6 } from "./imports/USBLC6_2SC6"
import { TYPE_C_31_M_12 } from "./imports/TYPE_C_31_M_12"
import { DRV8870DDAR } from "./imports/DRV8870DDAR"
import { TS_1187A_B_A_B } from "./imports/TS_1187A_B_A_B"

// pcbX/pcbY for the PCB, with a matching schematic spot so the schematic view
// doesn't pile every part on the origin.
export const at = (px: number, py: number) => ({ pcbX: px, pcbY: py, schX: px / 6, schY: py / 6 })

// MANIFOLD A's connector reuses the ULN output order (ch1-8 + the 12 V flyback COM).
export const ulnOUT = ["COM", "OUT1", "OUT2", "OUT3", "OUT4", "OUT5", "OUT6", "OUT7", "OUT8"]

// ---- SMD passives (resistor / capacitor) with hand-drawn silk --------------
// Every 2-terminal chip passive on the board — resistor AND capacitor — goes
// through here, so they read identically: one clean, symmetric two-line mark
// between the pads plus an upright ref-des that rides with (x,y).
//
// Why not the footprint's own silk? Footprinter draws a capacitor (and a
// `_norefdes`-suffixed resistor) as an ASYMMETRIC three-sided box, tied to the
// part rotation — so when one part in a group is flipped 180° for routing, its
// box points the other way and the row looks wrong. And a bare resistor's silk
// (two lines) differs from that box, so R's and C's on the same board disagree.
// We drop the footprint silk wholesale (`_nosilkscreen`, pads only) and redraw
// it here: the KiCad nonpolarized pair — two short lines just clear of the pads,
// mirror-symmetric so it's INVARIANT under a 180° flip (a flipped part looks
// like its neighbours), rotated with the part (rot 90/270 → a vertical pair) so
// it always sits between the pads. Identical geometry for a resistor and a
// capacitor of the same size: one mark, one rule.
//
// `side` (N/S/E/W) is which edge of the part the ref-des sits beside — same
// meaning and same default for both R and C. The preferred sides: N for a
// horizontal part, E for a vertical one (the defaults); W and S are the
// dodge fallbacks when the preferred side has copper or other ink.
// The offset is DERIVED, not hand-tuned: the part's real
// half-extent in that board direction (`ax` = pad reach along the pad axis,
// `pe` = mark reach across it) + a fixed gap, so the label clears the part by
// the same margin whichever side is chosen and whichever way the part is turned.
type Side = "N" | "S" | "E" | "W"
const REFDES_GAP = 0.5 // part edge -> ref-des centre
const SILK_STROKE = 0.12
// Per size: len/yOut place the two-line mark (x∈[-len,len], y=±yOut — the KiCad
// nonpolarized-resistor silk); ax/pe are the half-extents used to place the
// ref-des (ax = p/2+pw/2 to the pad's outer edge, pe = yOut across the part).
const PASSIVE_SIZE: Record<string, { len: number; yOut: number; ax: number; pe: number }> = {
  "0402": { len: 0.153641, yOut: 0.38, ax: 0.78, pe: 0.38 },
  "0603": { len: 0.237258, yOut: 0.5225, ax: 1.225, pe: 0.5225 },
  "0805": { len: 0.227064, yOut: 0.735, ax: 1.425, pe: 0.735 },
  "1206": { len: 0.727064, yOut: 0.91, ax: 2.025, pe: 0.91 },
}

// Shared silk for a passive at (x,y), seating rotation `rot`, ref-des on `side`.
const passiveSilk = (name: string, footprint: string, x: number, y: number, rot: number, side?: Side) => {
  const sz = PASSIVE_SIZE[footprint] ?? PASSIVE_SIZE["0603"]!
  const vertical = rot % 180 !== 0
  const s = side ?? (vertical ? "E" : "N")
  const rad = (rot * Math.PI) / 180, c = Math.cos(rad), sn = Math.sin(rad)
  const R = (px: number, py: number) => ({ x: x + px * c - py * sn, y: y + px * sn + py * c })  // local->world, CCW
  const mark = (yy: number) => [R(-sz.len, yy), R(sz.len, yy)]
  // ref-des offset: the part's half-extent in the chosen board direction + gap.
  // A vertical part swaps its along-axis (ax) and across-axis (pe) extents. On the
  // pad-AXIS side, the ref-des reads parallel to the pads (it's turned to match the
  // part), so its own half-length reaches back toward the part — add it so the text
  // clears the pad instead of landing on it. On the across side the text's narrow
  // dimension faces the part and the gap already covers it.
  const ns = s === "N" || s === "S"
  const axisSide = vertical ? ns : !ns
  const textHalfLen = name.length * 0.3   // ref-des reads ~0.6·fontSize per glyph
  const off = (ns ? (vertical ? sz.ax : sz.pe) : (vertical ? sz.pe : sz.ax)) + REFDES_GAP + (axisSide ? textHalfLen : 0)
  const [lx, ly] = s === "N" ? [0, off] : s === "S" ? [0, -off] : s === "E" ? [off, 0] : [-off, 0]
  return (
    <>
      <silkscreenpath route={mark(sz.yOut)} strokeWidth={`${SILK_STROKE}mm`} />
      <silkscreenpath route={mark(-sz.yOut)} strokeWidth={`${SILK_STROKE}mm`} />
      <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x + lx} pcbY={y + ly} pcbRotation={vertical ? 90 : 0} />
    </>
  )
}

// Each passive rides its JLCPCB-imported footprint (pads + origin + 3D model) keyed by its
// `jlcpcb` part number — so the CPL rotation matches JLCPCB's library, like every other part.
// The import carries no silk (passiveSilk draws the shared mark + ref-des); `footprint` (the
// size) still sizes that mark. See ./imports/passives.
export const Cap = ({ name, capacitance, footprint, jlcpcb, x, y, rot = 90, side }: {
  name: string; capacitance: string; footprint: string; jlcpcb: string
  x: number; y: number; rot?: number; side?: Side
}) => {
  const imp = passiveImport(jlcpcb)
  return (
    <>
      <capacitor name={name} capacitance={capacitance} footprint={imp.footprint()} cadModel={imp.cadModel} supplierPartNumbers={{ jlcpcb: [jlcpcb] }} pcbRotation={rot} {...at(x, y)} />
      {passiveSilk(name, footprint, x, y, rot, side)}
    </>
  )
}

export const Res = ({ name, resistance, footprint, jlcpcb, x, y, rot = 0, side }: {
  name: string; resistance: string; footprint: string; jlcpcb: string
  x: number; y: number; rot?: number; side?: Side
}) => {
  const imp = passiveImport(jlcpcb)
  return (
    <>
      <resistor name={name} resistance={resistance} footprint={imp.footprint()} cadModel={imp.cadModel} supplierPartNumbers={{ jlcpcb: [jlcpcb] }} pcbRotation={rot} {...at(x, y)} />
      {passiveSilk(name, footprint, x, y, rot, side)}
    </>
  )
}

// ---- JST trunk connector ---------------------------------------------------
// JLCPCB-imported XH2.54 wafer footprints keyed by pin count — the real body + holes + 3D model,
// so the CPL rotation matches JLCPCB's library (the generic pinrow placed the wafer body
// mis-rotated). JLCPCB's own footprints for this series are NOT uniform, which is what made the
// slots look random:
//   OPEN  — the mating opening (the tall shroud side) faces +Y at rot 0 for 3/4/9P but -Y for
//           5/6/7P. The Jst helper reads this so the caller's uniform `rot` means the same thing
//           for every count (see below).
// PITCH is a uniform 2.5 mm across the series (XH2.54 is a 2.5 mm-pitch part — the "2.54" is the
// nominal name, not the drawn pitch). JLCPCB's 4/7P footprints were drawn at 2.54 while their outer
// shroud walls were sized for 2.5 (B = pin-span + 5.0), so their pins were pulled to 2.5 to match.
const WAFER_BY_COUNT: Record<number, (props: any) => any> = {
  3: WAFER_XH2_54_3PZZ, 4: WAFER_XH2_54_4PZZ, 5: WAFER_XH2_54_5PZZ,
  6: WAFER_XH2_54_6PZZ, 7: WAFER_XH2_54_7PZZ, 9: WAFER_XH2_54_9PZZ,
}
const WAFER_PITCH: Record<number, number> = { 3: 2.5, 4: 2.5, 5: 2.5, 6: 2.5, 7: 2.5, 9: 2.5 }
// intrinsic opening direction at rot 0: +1 = +Y (north), -1 = -Y (south)
const WAFER_OPEN: Record<number, number> = { 3: 1, 4: 1, 5: -1, 6: -1, 7: -1, 9: 1 }
// which end pin 1 sits at, at rot 0 — WEST (-X) for the whole series EXCEPT the 7P, whose JLCPCB
// footprint numbers from the EAST. Used to keep every net on the same physical pin as before.
const WAFER_PIN1_WEST: Record<number, boolean> = { 3: true, 4: true, 5: true, 6: true, 7: false, 9: true }
// how far the body extends on the opening side (mm) — the survive block clears it
const WAFER_BODY_OUT: Record<number, number> = { 3: 3.45, 4: 3.72, 5: 3.77, 6: 3.69, 7: 3.76, 9: 3.76 }

// A board header for an off-board loom (the cable plugs in). The imported wafer footprint
// (WAFER_BY_COUNT) carries the real body + holes + 3D model. `rot` is the ordinary seating rotation
// (CCW degrees) every part on the board takes — for a Jst, the UNIFORM convention is rot 0 = the
// mating opening faces +Y (north), 90 = west, 180 = south, 270 = east. The wafer's REAL pcbRotation
// absorbs the series' inconsistent intrinsic opening (WAFER_OPEN) so `rot` means the same thing for
// every pin count — the caller never has to know a part's quirks. Everything else derives from that:
// the outboard direction (= the opening, toward the board edge), the pin order, and the label rows.
// It draws the pin labels, function label and ref-des INBOARD (readable on the bare board), plus a
// "survives-assembly" copy OUTBOARD past the body (visible once a wafer is seated over the inboard
// set). `labels[i]` is the net on pin i+1 (pin 1 at the -X end at rot 0), drawn at its pin's rotated
// position so it tracks the pin whatever the seating rotation.
// A Jst's label→pin geometry at the uniform `rot`: `wafRot` is the wafer's real pcbRotation
// (absorbing the series' inconsistent intrinsic opening), and `pins` pairs each label with its
// board-axes offset from the wafer centre, in physical pin order. Keeping every net on the same
// PHYSICAL pin as the pre-import design means two things reverse the label order along the edge —
// a wafer rotation of 180/270, and the 7P footprint that numbers from the east; when exactly one
// applies, the list reverses. One copy of this math: the Jst silk below and routing's connector
// frames both read it.
export const jstPins = ({ count, labels, rot = 0 }: { count: number; labels: string[]; rot?: number }) => {
  const pitch = WAFER_PITCH[count] ?? 2.5
  const openAngle = WAFER_OPEN[count] > 0 ? 90 : 270
  const wafRot = (((rot + 90) - openAngle) % 360 + 360) % 360
  const pin1West = WAFER_PIN1_WEST[count] ?? true
  const flip = (wafRot === 180 || wafRot === 270) !== !pin1West
  const L = flip ? [...labels].reverse() : labels
  const rad = (wafRot * Math.PI) / 180, c = Math.cos(rad), s = Math.sin(rad)
  const span = ((count - 1) * pitch) / 2
  const pins: [string, [number, number]][] = L.map((lbl, i) => {
    const along = pin1West ? -span + i * pitch : span - i * pitch
    return [lbl, [along * c, along * s]]
  })
  return { wafRot, pins }
}

export const Jst = ({ name, x, y, count, labels, label, rot = 0 }: { name: string; x: number; y: number; count: number; labels: string[]; label: string; rot?: number }) => {
  const Wafer = WAFER_BY_COUNT[count]
  const smHalf = 0.24, bigHalf = 0.42, padR = 0.825, G = 0.25   // ink cap half-heights; pad radius; tier gap
  const { wafRot, pins } = jstPins({ count, labels, rot })
  const pinLabelObj = Object.fromEntries(pins.map(([lbl], i) => [`pin${i + 1}`, lbl]))
  const rad = (wafRot * Math.PI) / 180
  // Outboard (toward the board edge) = the opening direction: the intrinsic ±Y opening turned by wafRot.
  const ox = -WAFER_OPEN[count] * Math.sin(rad), oy = WAFER_OPEN[count] * Math.cos(rad)
  const textRot = Math.abs(ox) > Math.abs(oy) ? 90 : 0         // vertical rows (E/W edges) read bottom-to-top
  const pinOff = padR + G + smHalf                    // pin row -> pin label (inboard)
  const refOff = -pinOff          // -> ref-des (inboard, next tier)
  const survPinOff = WAFER_BODY_OUT[count] + G                   // outboard, clear of the body
  const survFuncOff = survPinOff + smHalf + G + bigHalf                   // outboard function, next tier
  return (
    <>
      <Wafer name={name} pcbRotation={wafRot} pinLabels={pinLabelObj} {...at(x, y)} />
      {pins.map(([lbl, [px, py]], i) => (
        <silkscreentext key={`p${i}`} text={lbl} fontSize="0.8mm" pcbX={x + px - ox * pinOff} pcbY={y + py - oy * pinOff} pcbRotation={textRot} />
      ))}
      <silkscreentext text={name} fontSize="0.8mm" pcbX={x - ox * refOff} pcbY={y - oy * refOff} pcbRotation={textRot} />
      <silkscreentext text={label} fontSize="1.4mm" pcbX={x + ox * survFuncOff} pcbY={y + oy * survFuncOff} pcbRotation={textRot} />
      {pins.map(([lbl, [px, py]], i) => (
        <silkscreentext key={`s${i}`} text={lbl} fontSize="0.8mm" pcbX={x + px + ox * survPinOff} pcbY={y + py + oy * survPinOff} pcbRotation={textRot} />
      ))}
    </>
  )
}

// ---- ULN2803A — SOIC-18 (300 mil wide) -------------------------------------
// Octal Darlington sink driver. C845537 (UMW ULN2803A, SOP-18-300mil). Pinout:
// 1-8 IN1-IN8 (left, toward the MCP GPA banks), 9 GND, 10 COM (12 V flyback
// common), 11-18 OUT8-OUT1 (right, toward the manifold JSTs). Default
// orientation already runs IN on -X / OUT on +X, so the GPA->IN->OUT->valve flow
// is left-to-right with no row reversal. GND (pin 9, an SMD pad) auto-stitches to
// the bottom GND plane; COM (pin 10) lands on net.V12 under the top V12 island.
const ulnPinLabels = {
  pin1: "IN1", pin2: "IN2", pin3: "IN3", pin4: "IN4",
  pin5: "IN5", pin6: "IN6", pin7: "IN7", pin8: "IN8",
  pin9: "GND", pin10: "COM",
  pin11: "OUT8", pin12: "OUT7", pin13: "OUT6", pin14: "OUT5",
  pin15: "OUT4", pin16: "OUT3", pin17: "OUT2", pin18: "OUT1",
}

// JLCPCB-imported footprint (./imports/ULN2803A) so the CPL rotation matches JLCPCB's
// library orientation. Its own pin labels (Input1/Output1) are overridden with ours so the
// net wiring is unchanged. Imported rot 0 is HORIZONTAL (pins on N/S rows); the caller's rot
// is that value directly (rot 270 for the vertical IN-west/OUT-east seating used on U4/U5).
// The import's {NAME} silk is stripped (it rode the seating rotation, reading top-to-bottom at
// rot 270); the ref-des is drawn here upright and centred on the body — a pure function of (x,y).
export const Uln2803 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <>
    <ULN2803A name={name} pinLabels={ulnPinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
)

// ---- MCP23017 — SOIC-28 (300 mil) ------------------------------------------
// 16-bit I2C GPIO expander. C47023 (Microchip MCP23017-E/SO). Pinout: 1-8 GPB0-7
// (left, toward the reed JSTs), 9 VDD, 10 VSS, 11 NC, 12 SCL, 13 SDA, 14 NC,
// 15 A0, 16 A1, 17 A2, 18 /RESET, 19 INTB, 20 INTA, 21-28 GPA0-7 (right, toward
// the ULN inputs). VDD auto-stitches to the 3V3 inner plane, VSS to the bottom GND
// plane. A0/A1/A2 are strapped and /RESET tied high in pcba.tsx (the address +
// reset the breakout module set with jumpers); INTA/INTB are unused (polled). NC
// pins 11/14 and the INT pins are left off the label map → unconnected pads.
const mcpPinLabels = {
  pin1: "GPB0", pin2: "GPB1", pin3: "GPB2", pin4: "GPB3",
  pin5: "GPB4", pin6: "GPB5", pin7: "GPB6", pin8: "GPB7",
  pin9: "VCC", pin10: "GND", pin12: "SCL", pin13: "SDA",
  pin15: "A0", pin16: "A1", pin17: "A2", pin18: "RESET",
  pin21: "GPA0", pin22: "GPA1", pin23: "GPA2", pin24: "GPA3",
  pin25: "GPA4", pin26: "GPA5", pin27: "GPA6", pin28: "GPA7",
}

// JLCPCB-imported footprint (./imports/MCP23017_E_SO, C47023) so the CPL rotation matches
// JLCPCB's library orientation — the generic soic28 placed the body mis-rotated on the pads.
// Its built-in GPB0/GPA7 pin labels are overridden with ours (VCC/GND for VDD/VSS, NC/INT pins
// dropped) so the net wiring is unchanged. Imported rot 0 seats GPA on the north row / GPB on the
// south; the caller's rot is that value directly (rot 180 mirrors that for U2's GPA-south seating,
// rot 0 for U3's GPA-north). The import's own {NAME} silk is stripped (it rides the chip rotation
// and reads sideways/upside-down); the ref-des is drawn here upright and centred on the body — a
// pure function of (x,y), so it rides when the chip is moved.
export const Mcp23017 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; addr?: string; rot?: number }) => (
  <>
    <MCP23017_E_SO name={name} pinLabels={mcpPinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
)

// ---- DS3231SN — SOIC-16 (300 mil) ------------------------------------------
// I2C RTC with internal TCXO + crystal (±2 ppm). C9866 (ADI/Maxim DS3231SN#).
// Pinout: 1 32KHZ, 2 VCC, 3 INT/SQW, 4 /RST, 5-12 NC, 13 GND, 14 VBAT, 15 SDA,
// 16 SCL. The breakout's AT24C32 EEPROM is dropped (firmware uses none). VCC
// auto-stitches to the 3V3 inner plane, GND to the bottom plane; VBAT runs to the
// coin cell (no charging path — trickle charger off by default). 32KHZ/SQW unused,
// /RST has an internal pull-up (NC). NC pins are left off the map → unconnected.
const ds3231PinLabels = {
  pin1: "T32K", pin2: "VCC", pin3: "SQW", pin4: "RST",
  pin13: "GND", pin14: "VBAT", pin15: "SDA", pin16: "SCL",
}

// JLCPCB-imported footprint (./imports/DS3231SN_T_R, C9866) for the correct CPL rotation.
// VCC/GND auto-stitch to their planes, SDA/SCL ride the I2C routeInner edges (pcba.tsx),
// and VBAT runs to the coin cell (BT1); rot 270 keeps the
// long axis vertical. The import's built-in 32kHz/INTSQW labels are overridden with
// ours (NC pins 5-12 dropped). Its {NAME} silk is stripped (sideways at rot 270); the ref-des
// is drawn here upright, centred on the body — a pure function of (x,y).
export const Ds3231Smd = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <>
    <DS3231SN_T_R name={name} pinLabels={ds3231PinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
)

// ---- COS13487EESA-3.3 — RS-485 transceiver, SOP-8 (= SOIC-8), 3.3 V, auto-direction ----
// C51949447 (COSINE COS13487E-3.3): a native-3.3 V MAX13487E-equivalent, ±15 kV ESD,
// -7..+12 V common-mode (matches the SM712 clamp). Auto-direction — the driver auto-
// enables on TX off the DI pin, so there is no host DE/RE line to drive. Pinout
// (datasheet Fig.1) is the MAX13487/THVD1426 map: 1 RO (RX out -> ESP), 2 /RE (tie GND =
// always receive), 3 /SHDN (tie VCC = always on), 4 DI (TX in <- ESP), 5 GND, 6 A, 7 B,
// 8 VCC. RO/DI are the TTL side to the ESP UART; A/B the differential line to J9. In stock
// at JLCPCB but shallow (~530, Extended) — glance at it before a large run.
const cos13487PinLabels = {
  pin1: "RO", pin2: "RE", pin3: "SHDN", pin4: "DI",
  pin5: "GND", pin6: "A", pin7: "B", pin8: "VCC",
}

// JLCPCB-imported footprint (./imports/COS13487EESA_3_3, C51949447) for the correct CPL rotation.
// rot 270 seats RO/RE/SHDN/DI on the west column (toward the ESP UART) and VCC/B/A/GND on the east
// (toward J9 / the R6 termination / the D1 ESD array), reproducing the generic orientation. The
// import's labels already match ours; {NAME} silk stripped for the upright manual ref-des.
export const Cos13487 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <>
    <COS13487EESA_3_3 name={name} pinLabels={cos13487PinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
)

// ---- SM712 — RS-485 ESD/TVS array, SOT-23 -----------------------------------
// C12067 (Semtech SM712.TCT). Asymmetric -7 V / +12 V clamp matching the RS-485
// common-mode range, sits at the J9 cable entry. 1 A line, 2 B line, 3 GND.
const sm712PinLabels = { pin1: "A", pin2: "B", pin3: "GND" }

// JLCPCB-imported footprint (./imports/SM712_TCT, C12067) for the correct CPL rotation. SOT-23,
// so it calibrates separately from the SOICs: rot 180 seats A/B on the west column and GND on
// the east, reproducing the generic orientation (rot 90 turns that to A/B north, GND south).
// The import's A11/A12/K labels are overridden with our A/B/GND; {NAME} silk stripped for the
// manual ref-des.
export const Sm712 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <>
    <SM712_TCT name={name} pinLabels={sm712PinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
)

// ---- labeled wrappers for imported parts -----------------------------------
// These imports either carry no footprint ref-des (coin holder, bulk cap, buzzer)
// or one that reads upside-down at the part's seating rotation (the rot-180 buck +
// transistor). Each wrapper draws an upright ref-des whose position is a pure
// function of the seating (x, y — and rot for the buck) — so it rides with the part
// when moved, the Cap/Jst convention — and bakes in the fixed seating rotation.
// `dx/dy` place the label just off the printed body: outside it for the tall
// through-hole parts (coin, bulk cap, buzzer), on the body block clear of the pin
// row for the buck. The buzzer/coin/bulk bodies stand over the board, so their
// labels sit clear of the footprint.
type Labeled = { name: string; x: number; y: number }
const refdes = (name: string, x: number, y: number) =>
  <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />

// K7805 5 V buck (seats rot 180 horizontal by default; rot 90/270 stands it vertical).
// The SIP-3 footprint anchors on its pin row with the body block hanging to one side
// (silk body centre 1.6mm past the row; the 1.6mm pin pads reach 0.8mm past it), so the
// ref-des seats 2.4mm beyond the row, rotated with the seating — centred on the body
// block, clear of the pin pads, the chip-family convention.
export const Buck5 = ({ name, x, y, rot = 180 }: Labeled & { rot?: number }) => {
  const dx = rot === 90 ? 2.4 : rot === 270 ? -2.4 : 0
  const dy = rot === 0 ? -2.4 : rot === 180 ? 2.4 : 0
  return (
    <>
      <K7805_2000R3 name={name} pcbRotation={rot} {...at(x, y)} />
      {refdes(name, x + dx, y + dy)}
    </>
  )
}

// MLT-5020 magnetic buzzer (seats rot 90): label on the body, nudged west of centre so it
// clears the +/- polarity silk (which the rot-90 seating throws to the east) while staying
// well inside the footprint — reads as the buzzer's own, not the neighbour Q1's to the west.
export const Buzzer = ({ name, x, y }: Labeled) => (
  <>
    <MLT_5020 name={name} pcbRotation={90} {...at(x, y)} />
    {refdes(name, x - 1.8, y)}
  </>
)

// CR2032 20 mm coin holder: label above the holder (its body covers the centre).
export const CoinHolder = ({ name, x, y }: Labeled) => (
  <>
    <KH_CR2032_2_1 name={name} pcbRotation={0} {...at(x, y)} />
    {refdes(name, x, y + 12)}
  </>
)

// 470 µF radial bulk cap: label below the can (its body covers the centre).
export const BulkCap = ({ name, x, y }: Labeled) => (
  <>
    <NXB_25V470_10_12_5 name={name} pcbRotation={0} {...at(x, y)} />
    {refdes(name, x, y)}
  </>
)

// S8050 NPN in a SOT-23 (auto-reset Q2/Q3 + buzzer-drive Q1). Its import ref-des is stripped,
// so the ref-des is drawn here upright and centred on the body — a pure function of (x,y), so it
// rides when the part is moved, whatever the seating rotation (rot 180 for Q1, 270 for Q2/Q3).
export const Npn = ({ name, x, y, rot = 180 }: Labeled & { rot?: number }) => (
  <>
    <S8050_J3Y_RANGE_200_350_ name={name} pcbRotation={rot} {...at(x, y)} />
    {refdes(name, x, y)}
  </>
)

// TS-1187A 6 mm SMD tact (SW1/SW2 BOOT/RESET). The import self-labels and carries its own pin
// hints, so the wrapper only seats it. pin1↔pin4 is one diagonal switch contact (pin2↔pin3 the
// other), so a press shorts pin1 (signal) to pin4 (GND) whatever the internal terminal split.
// The import's {NAME} silk is stripped (it rode the seating rotation — upside-down at SW1's
// rot 180, off the board edge at SW2's rot 0); the ref-des is drawn upright and centred on
// the button body like the centred chips — the top-edge reset trace walls the north side.
export const Tact = ({ name, x, y, rot = 0 }: Labeled & { rot?: number }) => (
  <>
    <TS_1187A_B_A_B name={name} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
)

// ---- centred-ref-des SMD chips ---------------------------------------------
// The remaining imported chips carry their own pin labels/nets, so all a wrapper
// adds is seating + a clean ref-des. Each has its footprint {NAME} silk stripped
// (it rode the seating rotation — sideways/upside-down at rot 270 — and sat offset
// toward a neighbour) and gets an upright ref-des centred on the body, a pure
// function of (x,y) so it rides when the part moves, exactly like U2/U3 (Mcp23017).
const centred = (Part: (props: any) => any) =>
  ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
    <>
      <Part name={name} pcbRotation={rot} {...at(x, y)} />
      <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
    </>
  )

export const Esp32 = centred(ESP32_WROOM_32E_N4)   // U1  — bare WROOM module
export const Ams1117 = centred(AMS1117_3_3)         // U9  — 3V3 LDO (SOT-223)
export const Ch340 = centred(CH340C)                // U13 — USB-UART bridge (SOP-16)
export const Usblc6 = centred(USBLC6_2SC6)          // U14 — USB ESD array (SOT-23-6)
export const UsbC = centred(TYPE_C_31_M_12)         // J14 — USB-C receptacle
export const Drv8870 = centred(DRV8870DDAR)         // U11/U12 — pump H-bridges (SOP-8)
