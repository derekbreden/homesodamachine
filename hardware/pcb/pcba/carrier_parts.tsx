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
// keeps the 3-sided silk courtyard) and redraw it: rot 90 for a vertical part
// (reads bottom-to-top), rot 0 for a horizontal one. `lab` is the ref-des centre
// relative to the body; the default sits one tier off the body — on the -X side
// for a vertical part (the connector convention), above for a horizontal one.
export const Cap = ({ name, capacitance, footprint, jlcpcb, x, y, rot = 90, lab }: {
  name: string; capacitance: string; footprint: string; jlcpcb: string
  x: number; y: number; rot?: number; lab?: [number, number]
}) => {
  const vertical = rot % 180 !== 0
  const [lx, ly] = lab ?? (vertical ? [-1.85, 0] : [0, 1.35])
  return (
    <>
      <capacitor name={name} capacitance={capacitance} footprint={`${footprint}_norefdes`} supplierPartNumbers={{ jlcpcb: [jlcpcb] }} pcbRotation={rot} {...at(x, y)} />
      <silkscreentext text={name} fontSize="0.8mm" pcbX={x + lx} pcbY={y + ly} pcbRotation={vertical ? 90 : 0} />
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
// standard female JST-XH 2.54 housings). XUNPU WAFER-XH2.54-NPZZ / Megastar
// ZX-XH2.54-NPZZ — see jlcpcb-parts.md.
const XH254_BY_COUNT: Record<number, string> = {
  2: "C5359631", 3: "C7429633", 4: "C7429634", 5: "C5359633",
  6: "C5359634", 7: "C5359635", 9: "C7429639",
}

// The two wafer vendors seat their 3D model a half-turn apart for the same CPL
// rotation — XUNPU (2/5/6/7P) one way, Megastar (3/4/9P) the other — so a board
// that mixes both shows connectors facing two ways per edge. The single-row pad set
// is symmetric under 180°, so flipping one vendor's parts a half-turn AND reversing
// their pin order turns the wafer to match the other while leaving copper, nets and
// silk byte-identical. Flip the Megastar parts onto the XUNPU orientation. (If the
// JLCPCB preview wants the opposite seating, swap this set for the XUNPU C#s.)
const FLIP_WAFER = new Set(["C7429633", "C7429634", "C7429639"]) // Megastar ZX-XH2.54 3/4/9P

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
  // A vertical connector is the horizontal layout turned a quarter-turn CCW (the
  // rotation that makes the text read bottom-to-top), so the function label sits on
  // the -X side — the side that reads as ABOVE the pins once the board is turned to
  // read it — and the pin labels + ref-des on +X. Uniform across all connectors so
  // they're consistent; labelDir is accepted but no longer needed for this.
  const perpDir = vertical ? -1 : 1
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
  // Vendor-orientation fix: only the part placement turns (half-turn + reversed pin
  // order for the flip vendor) so its 3D wafer matches the others; the fence + every
  // silk label below stay on the un-flipped layout, so the rendered board is identical.
  const part = jlcpcb ?? XH254_BY_COUNT[count]
  const flip = part != null && FLIP_WAFER.has(part)
  const phRot = flip ? (rot + 180) % 360 : rot
  const phLabels = flip ? [...labels].reverse() : labels
  return (
    <>
      <pinheader name={name} pinCount={count} pitch="2.5mm" gender="male" footprint={`pinrow${count}_p2.5mm_id1.1mm_od1.65mm_nopinlabels_norefdes`} pcbRotation={phRot} pinLabels={phLabels} supplierPartNumbers={part ? { jlcpcb: [part] } : undefined} {...at(x, y)} />
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
