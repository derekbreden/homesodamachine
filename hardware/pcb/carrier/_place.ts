/**
 * _place.ts — placement design model. Computes the VISIBLE silk-body gaps (the
 * rectangles drawn by carrier_parts' Outline, rotation applied) between every
 * module and to the board edge, so the grid can be tuned to exact margins WITHOUT
 * a full render each step. Edit PLACE below, `bun _place.ts`, read the gaps.
 *
 * Dims are the module silk outlines from carrier_parts (w,h at the used rotation);
 * the ESP carries its WROOM antenna keepout as a second rect.
 */
const jst = (count: number, rot: number) => {
  const len = count * 2.54 + 2, dep = 5.8
  return rot % 180 ? { w: dep, h: len } : { w: len, h: dep }
}
type Dim = { w: number; h: number; ant?: { dx: number; dy: number; w: number; h: number } }
const DIM: Record<string, Dim> = {
  U1: { w: 52, h: 28, ant: { dx: 29, dy: 0, w: 6, h: 18 } }, // ESP32 rot0 + antenna
  U6: { w: 38.5, h: 21.3 }, // DS3231 rot0
  U7: { w: 51.85, h: 22.75 }, // RS485 rot180
  U2: { w: 23.3, h: 38.5 }, U3: { w: 23.3, h: 38.5 }, // MCP rot0
  U4: { w: 23, h: 24 }, U5: { w: 23, h: 24 }, // ULN rot0
  U8: { w: 13, h: 32 }, // buzzer rot180
  // axial_p2.54mm, pcbRotation 0 (horizontal): pad-span 3.94 x 1.40 (from _silkbox)
  R1: { w: 3.94, h: 1.4 }, R2: { w: 3.94, h: 1.4 }, R3: { w: 3.94, h: 1.4 }, R4: { w: 3.94, h: 1.4 },
  J1: jst(9, 90), J2: jst(6, 90), J3: jst(4, 0), J4: jst(6, 90), J5: jst(9, 0),
  J6: jst(5, 0), J7: jst(7, 0), J8: jst(2, 90), J9: jst(3, 0), J10: jst(2, 90), J11: jst(4, 0),
}

// name -> [x, y]  (rotation already baked into DIM)
const PLACE: Record<string, [number, number]> = {
  U6: [-27.25, -28.65], U1: [-31.15, -1], U7: [-29.0, 26.375],
  U2: [14.5, 18.65], U3: [14.5, -21.85], U4: [39.65, 21.42], U5: [39.65, -19.08],
  U8: [-55, -33],
  J1: [56, 21.42], J2: [56, -15.27], J3: [-46, 42.65], J4: [-62, 3], J5: [-27, -46],
  J8: [-62, -11.3], J6: [12.5, 42.8], J7: [13, -46], J9: [-4, 42.65], J10: [56, 3.4], J11: [-31.8, 42.65],
  R1: [-21.8, 40.9], R2: [-21.8, 44.4], R3: [-12.8, 40.9], R4: [-12.8, 44.4],
}

type Box = { name: string; x0: number; x1: number; y0: number; y1: number }
const boxes: Box[] = []
for (const [name, [x, y]] of Object.entries(PLACE)) {
  const d = DIM[name]; if (!d) continue
  boxes.push({ name, x0: x - d.w / 2, x1: x + d.w / 2, y0: y - d.h / 2, y1: y + d.h / 2 })
  if (d.ant) boxes.push({ name: name + "~ant", x0: x + d.ant.dx - d.ant.w / 2, x1: x + d.ant.dx + d.ant.w / 2, y0: y + d.ant.dy - d.ant.h / 2, y1: y + d.ant.dy + d.ant.h / 2 })
}
const base = (n: string) => n.replace(/~.*/, "")
const gap = (a: Box, b: Box) => {
  const dx = Math.max(b.x0 - a.x1, a.x0 - b.x1, 0), dy = Math.max(b.y0 - a.y1, a.y0 - b.y1, 0)
  return { d: Math.hypot(dx, dy), overlap: dx === 0 && dy === 0 }
}
// content extent + suggested 2mm board outline
let X0 = Infinity, X1 = -Infinity, Y0 = Infinity, Y1 = -Infinity
for (const b of boxes) { X0 = Math.min(X0, b.x0); X1 = Math.max(X1, b.x1); Y0 = Math.min(Y0, b.y0); Y1 = Math.max(Y1, b.y1) }
const M = 2 // target margin
const out = { x0: X0 - M, x1: X1 + M, y0: Y0 - M, y1: Y1 + M }

const pairs: { a: string; b: string; d: number; o: boolean }[] = []
for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
  if (base(boxes[i].name) === base(boxes[j].name)) continue
  const g = gap(boxes[i], boxes[j]); pairs.push({ a: boxes[i].name, b: boxes[j].name, d: g.d, o: g.overlap })
}
pairs.sort((p, q) => p.d - q.d)
const near: Record<string, { o: string; d: number; ov: boolean }> = {}
for (const p of pairs) {
  if (!near[base(p.a)] || p.d < near[base(p.a)].d) near[base(p.a)] = { o: base(p.b), d: p.d, ov: p.o }
  if (!near[base(p.b)] || p.d < near[base(p.b)].d) near[base(p.b)] = { o: base(p.a), d: p.d, ov: p.o }
}
const edge = (b: Box) => Math.min(b.x0 - out.x0, out.x1 - b.x1, b.y0 - out.y0, out.y1 - b.y1)
const eByMod: Record<string, number> = {}
for (const b of boxes) { const k = base(b.name); eByMod[k] = Math.min(eByMod[k] ?? Infinity, edge(b)) }

console.log(`content [x ${X0.toFixed(1)}..${X1.toFixed(1)}  y ${Y0.toFixed(1)}..${Y1.toFixed(1)}]  ${(X1 - X0).toFixed(1)} x ${(Y1 - Y0).toFixed(1)}mm`)
console.log(`board outline @2mm: [{x:${out.x0.toFixed(1)},y:${out.y0.toFixed(1)}},{x:${out.x1.toFixed(1)},y:${out.y0.toFixed(1)}},{x:${out.x1.toFixed(1)},y:${out.y1.toFixed(1)}},{x:${out.x0.toFixed(1)},y:${out.y1.toFixed(1)}}]  ${(out.x1 - out.x0).toFixed(1)} x ${(out.y1 - out.y0).toFixed(1)}mm\n`)
console.log("module → nearest, silk gap, edge gap  (·<2mm  ⚠OVERLAP):")
for (const n of Object.keys(near).sort()) {
  const e = eByMod[n], g = near[n]
  const f = g.ov ? " ⚠OVERLAP" : g.d < 1.99 ? " ·" : ""
  const ef = e < 1.99 ? " ·edge" : ""
  console.log(`  ${n.padEnd(4)} → ${g.o.padEnd(4)} ${g.d.toFixed(2)}mm${f}   edge ${e.toFixed(2)}mm${ef}`)
}
console.log("\ngaps > 4mm (loose, pull in):")
for (const n of Object.keys(near).sort()) if (near[n].d > 4) console.log(`  ${n} ↔ ${near[n].o}: ${near[n].d.toFixed(1)}mm`)
