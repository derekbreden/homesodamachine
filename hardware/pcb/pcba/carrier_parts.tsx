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

// A stroked rectangle on the silk layer — a part's PCB outline / fence.
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

// XH2.54 vertical THT male wafer connectors (JLCPCB assembly), keyed by pin count.
// The "2.54" is the market label; the parts are genuine 2.5 mm-pitch XH (mate with
// standard female JST-XH 2.54 housings). One vendor for every count — XUNPU's
// WAFER-XH2.54-{n}PZZ series — so every wafer seats the same way and its pin-1 (square)
// pad sits at the same end (no per-vendor 3D-rotation offset to compensate). See
// jlcpcb-parts.md.
const XH254_BY_COUNT: Record<number, string> = {
  2: "C5359631", 3: "C5374805", 4: "C5359632", 5: "C5359633",
  6: "C5359634", 7: "C5359635", 9: "C5359637",
}

// ---- JST trunk connector ---------------------------------------------------
// A board header (the off-board loom cable plugs in): a fence holding the pin
// row, the function label, the pin labels and the ref-des. Laid out for a
// horizontal row — function label one side, pin labels + ref-des the other —
// then placed for the connector's orientation so a vertical one is the horizontal
// turned a quarter-turn and every label reads the same way (bottom-to-top
// vertical, left-to-right horizontal). The pin labels are drawn here, not by the
// footprint (whose auto labels lock vertical rows to top-to-bottom); the footprint
// string is pads-only. Margins to the fence are even on all four sides.
//
// A seated wafer hides everything inside the fence, so a second copy of BOTH the pin
// labels and the function label is drawn OUTBOARD of the fence — in the margin between
// the fence and the board edge — where they survive assembly. `side` is the board edge
// this connector faces (N/S/E/W); it picks which fence edge is outboard. The board is
// sized so every connector's fence sits the same distance from its edge, so that outboard
// block reads identically on all four sides.
export const Jst = ({ name, x, y, count, labels, rot = 0, label, side, jlcpcb }: { name: string; x: number; y: number; count: number; labels: string[]; rot?: number; label: string; side: "N" | "S" | "E" | "W"; jlcpcb?: string }) => {
  const vertical = rot % 180 !== 0
  const pitch = 2.5, padR = 0.825                   // XH 2.5 mm pitch, 1.65 mm pad radius
  const bigHalf = 0.42, smHalf = 0.24               // ink cap half-heights (0.6 × font size)
  const G = 0.45, M = 0.6                            // even tier gap; even content -> fence margin
  // A vertical connector is the horizontal layout turned a quarter-turn CCW (the
  // rotation that makes the text read bottom-to-top), so the function label sits on
  // the -X side — the side that reads as ABOVE the pins once the board is turned to
  // read it — and the pin labels + ref-des on +X. Uniform across all connectors so
  // they're consistent.
  const perpDir = vertical ? -1 : 1
  const bigOff = padR + G + bigHalf                 // row -> function label
  const labelOff = padR + G + smHalf                // row -> pin label
  const refOff = labelOff + smHalf + G + smHalf     // row -> ref-des (one tier beyond pin labels)
  const uc = ((bigOff + bigHalf) - (refOff + smHalf)) / 2     // fence centre, perpendicular
  const dep = (bigOff + bigHalf) + (refOff + smHalf) + 2 * M + 0.2  // +0.2 fence stroke
  // The fence is the true XH wafer body along the pin axis — JST-XH housing width
  // A = pitch·(count-1) + 4.9 mm (2.45 mm of plastic past each outer pin), NOT a
  // pad-derived margin. A pad-margin fence reads ~0.9 mm narrow per end, so a gap
  // measured fence-to-fence understates the real body-to-body clearance by ~1.85 mm.
  const len = (count - 1) * pitch + 4.9
  const [w, h] = vertical ? [dep, len] : [len, dep]
  const P = (u: number, v: number): [number, number] => (vertical ? [perpDir * u, v] : [v, perpDir * u])
  const [bdx, bdy] = P(bigOff, 0)
  const [rdx, rdy] = P(-refOff, 0)
  const [fdx, fdy] = P(uc, 0)
  // Survives-assembly block: with the wafer seated over the fence, a second copy of the
  // pin labels and the function label is drawn OUTBOARD of the fence, in the margin to the
  // board edge, so both stay readable on the populated board. Everything is referenced to
  // the fence's own outboard silk edge — `outU` is which way that is in the P() frame (+u
  // toward N/W, -u toward S/E) — so the block clears the fence by the same G tiers on every
  // connector: pin labels one tier out, the function label the tier beyond.
  const outU = side === "N" || side === "W" ? 1 : -1
  const fenceOut = dep / 2 + 0.1 + outU * uc          // pin row -> fence outboard silk edge (+0.1 = half stroke)
  const pinSurviveOff = fenceOut + G + smHalf          // -> survives pin-label row
  const labelSurviveOff = pinSurviveOff + smHalf + G + bigHalf   // -> survives function label
  const [sdx, sdy] = P(outU * labelSurviveOff, 0)
  const part = jlcpcb ?? XH254_BY_COUNT[count]
  return (
    <>
      <pinheader name={name} pinCount={count} pitch="2.5mm" gender="male" footprint={`pinrow${count}_p2.5mm_id1.1mm_od1.65mm_nopinlabels_norefdes`} pcbRotation={rot} pinLabels={labels} supplierPartNumbers={part ? { jlcpcb: [part] } : undefined} {...at(x, y)} />
      <Outline x={x + fdx} y={y + fdy} w={w} h={h} />
      {labels.map((lbl, i) => {
        const [dx, dy] = P(-labelOff, (i - (count - 1) / 2) * pitch)
        return <silkscreentext key={i} text={lbl} fontSize="0.8mm" pcbX={x + dx} pcbY={y + dy} pcbRotation={rot} />
      })}
      <silkscreentext text={label} fontSize="1.4mm" pcbX={x + bdx} pcbY={y + bdy} pcbRotation={rot} />
      <silkscreentext text={name} fontSize="0.8mm" pcbX={x + rdx} pcbY={y + rdy} pcbRotation={rot} />
      <silkscreentext text={label} fontSize="1.4mm" pcbX={x + sdx} pcbY={y + sdy} pcbRotation={rot} />
      {labels.map((lbl, i) => {
        const [dx, dy] = P(outU * pinSurviveOff, (i - (count - 1) / 2) * pitch)
        return <silkscreentext key={i} text={lbl} fontSize="0.8mm" pcbX={x + dx} pcbY={y + dy} pcbRotation={rot} />
      })}
    </>
  )
}
