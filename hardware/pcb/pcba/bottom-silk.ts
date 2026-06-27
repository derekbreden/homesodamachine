/**
 * Synthesize the back-side silkscreen from the front.
 *
 * tscircuit draws every label and outline on the TOP silk only (F_SilkScreen);
 * the back is blank. For a hand-wired through-hole board you read the labels
 * from the solder side too, so we want the same legend on the bottom — same
 * positions, same font, same stroke weight, just mirrored so it reads the right
 * way round when you turn the board over.
 *
 * Rather than re-render glyphs by hand (which never matches tscircuit's font
 * metrics or its per-size stroke widths), we read the structured silk out of the
 * circuit JSON and emit a throwaway board of `layer="bottom"` copies — one
 * silkscreentext / silkscreenpath per front element, at the same pad-anchored
 * position. render-board builds THAT with tscircuit and lifts its B_SilkScreen
 * gerber, so the back legend is rendered by the same engine as the front and is
 * pixel-identical in size and weight. tscircuit handles the bottom-layer mirror
 * (each glyph flipped in place); the compositor's bottom view flips it back so
 * it reads forwards there, while the fab gerber stays correct on the real board.
 */
const n = (v: number) => (Number.isFinite(v) ? +v.toFixed(4) : 0)

/** A tscircuit board source whose bottom silk mirrors a board's front silk. */
export function backSilkBoardTsx(circuit: any[]): string {
  const board = circuit.find((e) => e.type === "pcb_board")
  const W = board?.width ?? 200
  const H = board?.height ?? 200
  const els: string[] = []
  for (const e of circuit) {
    if (e.type === "pcb_silkscreen_text" && e.layer === "top" && e.text) {
      // Preserve the front text's anchor — anchor_position is that anchor's
      // point, not necessarily the center. Re-emitting a corner-anchored label
      // (e.g. the bottom_right board nameplate) as "center" would place its
      // centre where its corner was, throwing half the text off the board edge.
      els.push(
        `    <silkscreentext layer="bottom" text={${JSON.stringify(e.text)}} ` +
          `pcbX={${n(e.anchor_position.x)}} pcbY={${n(e.anchor_position.y)}} ` +
          `fontSize="${n(e.font_size)}mm" pcbRotation={${e.ccw_rotation || 0}} ` +
          `anchorAlignment=${JSON.stringify(e.anchor_alignment || "center")} />`,
      )
    } else if (e.type === "pcb_silkscreen_path" && e.layer === "top") {
      const route = JSON.stringify((e.route || []).map((p: any) => ({ x: n(p.x), y: n(p.y) })))
      els.push(`    <silkscreenpath layer="bottom" strokeWidth="${n(e.stroke_width || 0.15)}mm" route={${route}} />`)
    }
  }
  return `export default () => (\n  <board width="${n(W)}mm" height="${n(H)}mm">\n${els.join("\n")}\n  </board>\n)\n`
}
