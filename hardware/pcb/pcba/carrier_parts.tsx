/**
 * carrier_parts — the board-level helpers pcba.tsx and pcba_parts.tsx share.
 *
 * Every plug-in module the carrier once socketed is now bare SMD silicon in
 * ./pcba_parts (its footprint + JLCPCB part), so the 2.54 mm header footprints
 * that lived here are gone. What remains is the geometry the SMD board still
 * uses: the placement helper (`at`), a silk outline, the ULN output roster the
 * manifold connector reuses, and the `Jst` field connector — the one through-hole
 * part class, the off-board loom headers (J1-J12), specified for JLCPCB assembly.
 */
import { passiveImport } from "./imports/passives"
import { WAFER_XH2_54_3PZZ } from "./imports/WAFER_XH2_54_3PZZ"
import { WAFER_XH2_54_4PZZ } from "./imports/WAFER_XH2_54_4PZZ"
import { WAFER_XH2_54_5PZZ } from "./imports/WAFER_XH2_54_5PZZ"
import { WAFER_XH2_54_6PZZ } from "./imports/WAFER_XH2_54_6PZZ"
import { WAFER_XH2_54_7PZZ } from "./imports/WAFER_XH2_54_7PZZ"
import { WAFER_XH2_54_9PZZ } from "./imports/WAFER_XH2_54_9PZZ"

// JLCPCB-imported XH2.54 wafer footprints keyed by pin count — the real body + holes + 3D model,
// so the CPL rotation matches JLCPCB's library (the generic pinrow placed the wafer body
// mis-rotated). JLCPCB's own footprints for this series are NOT uniform, which is what made the
// slots look random:
//   OPEN  — the mating opening (the tall shroud side) faces +Y at rot 0 for 3/4/9P but -Y for
//           5/6/7P. The Jst helper reads this to rotate each connector so its opening faces the
//           board edge it sits on (`side`), uniform across the board.
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

// pcbX/pcbY for the PCB, with a matching schematic spot so the schematic view
// doesn't pile every part on the origin.
export const at = (px: number, py: number) => ({ pcbX: px, pcbY: py, schX: px / 6, schY: py / 6 })

// MANIFOLD A's connector reuses the ULN output order (ch1-8 + the 12 V flyback COM).
export const ulnOUT = ["OUT1", "OUT2", "OUT3", "OUT4", "OUT5", "OUT6", "OUT7", "OUT8", "COM"]

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
// meaning and same default for both R and C (W for a vertical part, N for a
// horizontal one). The offset is DERIVED, not hand-tuned: the part's real
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
  const s = side ?? (vertical ? "W" : "N")
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
// A board header for an off-board loom (the cable plugs in). The imported wafer footprint
// (WAFER_BY_COUNT) carries the real body + holes + 3D model; this helper rotates it so the mating
// opening faces the board edge it sits on (`side`), accounting for the series' inconsistent
// intrinsic opening (WAFER_OPEN). It then draws the pin labels, function label and ref-des INBOARD
// (toward the interior, readable on the bare board), plus a "survives-assembly" copy OUTBOARD past
// the body toward the edge (visible once a wafer is seated over the inboard set). `labels[i]` is the
// net on pin i+1 (pin 1 at the footprint's -X end); each label is drawn at its pin's rotated
// position so it always tracks the pin, whatever the seating rotation. Orientation is `side` ALONE:
// the wafer's real rotation is DERIVED from it (per-part, absorbing the manufacturer differences
// noted above), so there's no free `rot` to set — a Jst faces an edge, and that edge is its pose.
export const Jst = ({ name, x, y, count, labels, label, side }: { name: string; x: number; y: number; count: number; labels: string[]; label: string; side: "N" | "S" | "E" | "W" }) => {
  const Wafer = WAFER_BY_COUNT[count]
  const pitch = WAFER_PITCH[count] ?? 2.5
  const smHalf = 0.24, bigHalf = 0.42, padR = 0.825, G = 0.25   // ink cap half-heights; pad radius; tier gap
  // Rotate the wafer so its opening (intrinsic +Y or -Y, WAFER_OPEN) faces the board edge `side`.
  const openAngle = WAFER_OPEN[count] > 0 ? 90 : 270              // intrinsic opening angle (deg CCW)
  const wantAngle: Record<"N" | "S" | "E" | "W", number> = { N: 90, S: 270, E: 0, W: 180 }
  const rot = ((wantAngle[side] - openAngle) % 360 + 360) % 360
  // Keep every net on the same PHYSICAL pin as the pre-import design (loom pinout + IC->connector
  // fans unchanged; only the wafer body turns to face the edge). Two things reverse the pin order
  // along the edge: a rotation flip (rot 180 on a N/S edge, 270 on E/W) and the 7P footprint that
  // numbers from the east. When exactly one applies, reverse the label list.
  const pin1West = WAFER_PIN1_WEST[count] ?? true
  const flip = (rot === 180 || rot === 270) !== !pin1West
  const L = flip ? [...labels].reverse() : labels
  const pinLabelObj = Object.fromEntries(L.map((l, i) => [`pin${i + 1}`, l]))
  const rad = (rot * Math.PI) / 180, c = Math.cos(rad), s = Math.sin(rad)
  const R = (ax: number, ay: number): [number, number] => [ax * c - ay * s, ax * s + ay * c]  // CCW
  const OUT: Record<"N" | "S" | "E" | "W", [number, number]> = { N: [0, 1], S: [0, -1], E: [1, 0], W: [-1, 0] }
  const [ox, oy] = OUT[side]                          // unit vector toward the edge (outboard)
  const textRot = side === "E" || side === "W" ? 90 : 0        // vertical rows read bottom-to-top
  const pinOff = padR + G + smHalf                    // pin row -> pin label (inboard)
  const refOff = -pinOff          // -> ref-des (inboard, next tier)
  const survPinOff = WAFER_BODY_OUT[count] + G                   // outboard, clear of the body
  const survFuncOff = survPinOff + smHalf + G + bigHalf                   // outboard function, next tier
  const span = ((count - 1) * pitch) / 2
  const pinAt = (i: number): [number, number] => R(pin1West ? -span + i * pitch : span - i * pitch, 0)  // pin i+1 local->world
  return (
    <>
      <Wafer name={name} pcbRotation={rot} pinLabels={pinLabelObj} {...at(x, y)} />
      {L.map((lbl, i) => {
        const [px, py] = pinAt(i)
        return <silkscreentext key={`p${i}`} text={lbl} fontSize="0.8mm" pcbX={x + px - ox * pinOff} pcbY={y + py - oy * pinOff} pcbRotation={textRot} />
      })}
      <silkscreentext text={name} fontSize="0.8mm" pcbX={x - ox * refOff} pcbY={y - oy * refOff} pcbRotation={textRot} />
      <silkscreentext text={label} fontSize="1.4mm" pcbX={x + ox * survFuncOff} pcbY={y + oy * survFuncOff} pcbRotation={textRot} />
      {L.map((lbl, i) => {
        const [px, py] = pinAt(i)
        return <silkscreentext key={`s${i}`} text={lbl} fontSize="0.8mm" pcbX={x + px + ox * survPinOff} pcbY={y + py + oy * survPinOff} pcbRotation={textRot} />
      })}
    </>
  )
}
