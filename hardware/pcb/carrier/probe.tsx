/** throwaway: verify (a) functional components that return a fragment inline,
 * and (b) traces to net.X join into one global net across components. */
const Pull = ({ name, x }: { name: string; x: number }) => (
  <>
    <resistor name={name} resistance="4.7k" footprint="0402" pcbX={x} pcbY={6} />
    <trace from={`.${name} > .pin2`} to="net.V3_3" />
  </>
)

export default () => (
  <board width="40mm" height="20mm">
    <chip name="U1" footprint="dip8" pcbX={-10} pcbY={0}
      pinLabels={{ pin1: "VCC", pin4: "GND", pin5: "SDA" }} />
    <Pull name="R1" x={8} />
    <trace from=".U1 > .VCC" to="net.V3_3" />
    <trace from=".U1 > .SDA" to=".R1 > .pin1" />
  </board>
)
