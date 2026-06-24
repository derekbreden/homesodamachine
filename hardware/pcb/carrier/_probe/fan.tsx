/**
 * Isolated autorouter probe: a header "H" fanning to a header "V", nothing else
 * on the board. Geometry is driven by the PROBE env var (JSON) so a sweep can
 * vary one knob at a time and read back via/error counts from circuit-json.
 *
 *   PROBE='{"n":8,"mode":"perp","gap":20}' tsci export -f circuit-json -o out.json _probe/fan.tsx
 *
 * knobs:
 *   n       pin count in the fan
 *   mode    "perp"     H is a horizontal row below the vertical column V (90deg)
 *           "parallel" H is a second vertical column left of V (0deg between rows)
 *   gap     perp: vertical drop from V's centre to H's row; parallel: column spacing
 *   offsetX perp: x-shift of H (centre the row under the column, or off to one side)
 *   pair    "fwd" Pi->Pi   "rev" Pi->P(n-1-i)   (which pairing is the planar one)
 *   effort  autorouterEffortLevel  "1x".."100x"
 *   version autorouterVersion      "v1".."v6"
 */
const cfg = JSON.parse(process.env.PROBE || "{}")
const n = cfg.n ?? 8
const mode = cfg.mode ?? "perp"
const gap = cfg.gap ?? 20
const offsetX = cfg.offsetX ?? 0
const pair = cfg.pair ?? "fwd"
const effort = cfg.effort ?? "1x"
const version = cfg.version

const P: string[] = Array.from({ length: n }, (_, i) => `P${i}`)

const boardProps: any = {
  width: "160mm",
  height: "160mm",
  minTraceWidth: "0.2mm",
  traceClearance: "0.4mm",
  autorouterEffortLevel: effort,
}
if (version) boardProps.autorouterVersion = version

const yshift = cfg.yshift ?? 0 // parallel: vertical misalignment between the two rows
const Hx = mode === "perp" ? offsetX : -gap
const Hy = mode === "perp" ? -gap : yshift
const Hrot = mode === "perp" ? 0 : 90

export default () => (
  <board {...boardProps}>
    <pinheader name="V" pinCount={n} pitch="2.54mm" footprint={`pinrow${n}`} pcbRotation={90} pinLabels={P} pcbX={0} pcbY={0} />
    <pinheader name="H" pinCount={n} pitch="2.54mm" footprint={`pinrow${n}`} pcbRotation={Hrot} pinLabels={P} pcbX={Hx} pcbY={Hy} />
    {P.map((p, i) => {
      const ti = pair === "rev" ? n - 1 - i : i
      const target = P[ti]
      // optional single midpoint hint (global coords) along the straight diagonal
      const hx = mode === "perp" ? Hx + (i - (n - 1) / 2) * 2.54 : Hx
      const hy = mode === "perp" ? Hy : (i - (n - 1) / 2) * 2.54
      const vx = 0
      const vy = (ti - (n - 1) / 2) * 2.54
      const hintProps = cfg.hints === "mid"
        ? { pcbRouteHints: [{ x: (hx + vx) / 2, y: (hy + vy) / 2 }] }
        : {}
      return <trace key={i} from={`.H > .${p}`} to={`.V > .${target}`} {...hintProps} />
    })}
  </board>
)
