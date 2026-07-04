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
//   PITCH — 2.5 mm for 3/5/6/9P but 2.54 mm for 4/7P (each label row is drawn at its own pitch).
//   OPEN  — the mating opening (the tall shroud side) faces +Y at rot 0 for 3/4/9P but -Y for
//           5/6/7P. The Jst helper reads this to rotate each connector so its opening faces the
//           board edge it sits on (`side`), uniform across the board.
const WAFER_BY_COUNT: Record<number, (props: any) => any> = {
  3: WAFER_XH2_54_3PZZ, 4: WAFER_XH2_54_4PZZ, 5: WAFER_XH2_54_5PZZ,
  6: WAFER_XH2_54_6PZZ, 7: WAFER_XH2_54_7PZZ, 9: WAFER_XH2_54_9PZZ,
}
const WAFER_PITCH: Record<number, number> = { 3: 2.5, 4: 2.54, 5: 2.5, 6: 2.5, 7: 2.54, 9: 2.5 }
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

// ---- SMD capacitor with a hand-drawn ref-des -------------------------------
// A 2-pad ceramic whose ref-des is drawn here, not by the footprint. tscircuit's
// auto ref-des locks a vertical part's label to top-to-bottom; every connector
// label on this board reads bottom-to-top (the Jst helper hand-draws its labels
// for the same reason). So we suppress the footprint ref-des (`_norefdes`, which
// keeps the silkscreen fence) and redraw it: rot 90 for a vertical part (reads
// bottom-to-top), rot 0 for a horizontal one.
//
// `side` is which edge of the fence the ref-des sits beside — pick whichever is
// clear of neighbouring traces/parts; the default is the connector convention
// (W for a vertical part, N for a horizontal one). The OFFSET is not hand-tuned:
// it's derived from the part's actual PRINTED fence — the silkscreen path, not
// the (larger) courtyard outline — so every label clears the fence by exactly the
// margin the footprint's own auto ref-des uses. Footprinter centres its ref-des at
// `fence + 0.5 mm` (measured from its output, font-independent); matching that is
// what makes a hand-drawn label read as clean as a stock one like C12's.
const CAP_FENCE_HALF: Record<string, number> = { "0603": 0.875, "0805": 1.1, "1206": 1.1 }
const REFDES_GAP = 0.5 // printed fence edge -> ref-des centre (footprinter's own margin)
export const Cap = ({ name, capacitance, footprint, jlcpcb, x, y, rot = 90, side }: {
  name: string; capacitance: string; footprint: string; jlcpcb: string
  x: number; y: number; rot?: number; side?: "N" | "S" | "E" | "W"
}) => {
  const vertical = rot % 180 !== 0
  const s = side ?? (vertical ? "W" : "N")
  const off = (CAP_FENCE_HALF[footprint] ?? 1.1) + REFDES_GAP
  const [lx, ly] = s === "N" ? [0, off] : s === "S" ? [0, -off] : s === "E" ? [off, 0] : [-off, 0]
  return (
    <>
      <capacitor name={name} capacitance={capacitance} footprint={`${footprint}_norefdes`} supplierPartNumbers={{ jlcpcb: [jlcpcb] }} pcbRotation={rot} {...at(x, y)} />
      <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x + lx} pcbY={y + ly} pcbRotation={vertical ? 90 : 0} />
    </>
  )
}

// ---- SMD resistor with a hand-drawn ref-des -------------------------------
// Same idea as Cap: a resistor rotated 180° for routing prints its footprint
// ref-des upside-down, so suppress it (`_norefdes`, keeps the silk fence) and
// redraw it upright, at a fence-derived offset that rides with (x,y).
const RES_FENCE_HALF: Record<string, number> = { "0402": 0.65, "0603": 0.875, "0805": 1.1 }
export const Res = ({ name, resistance, footprint, jlcpcb, x, y, rot = 0, side }: {
  name: string; resistance: string; footprint: string; jlcpcb: string
  x: number; y: number; rot?: number; side?: "N" | "S" | "E" | "W"
}) => {
  const vertical = rot % 180 !== 0
  const s = side ?? (vertical ? "W" : "N")
  const off = (RES_FENCE_HALF[footprint] ?? 0.875) + REFDES_GAP
  const [lx, ly] = s === "N" ? [0, off] : s === "S" ? [0, -off] : s === "E" ? [off, 0] : [-off, 0]
  return (
    <>
      <resistor name={name} resistance={resistance} footprint={`${footprint}_norefdes`} supplierPartNumbers={{ jlcpcb: [jlcpcb] }} pcbRotation={rot} {...at(x, y)} />
      <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x + lx} pcbY={y + ly} pcbRotation={vertical ? 90 : 0} />
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
// position so it always tracks the pin, whatever the seating rotation. `rot`/`jlcpcb` are ignored
// (kept for call-site compatibility): the rotation is derived, the part rides in the footprint.
export const Jst = ({ name, x, y, count, labels, label, side }: { name: string; x: number; y: number; count: number; labels: string[]; rot?: number; label: string; side: "N" | "S" | "E" | "W"; jlcpcb?: string }) => {
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
