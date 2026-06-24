const f = process.env.FP || "pinrow10"
const rot = Number(process.env.ROT || "0")
export default () => (
  <board width="60mm" height="60mm">
    <pinheader name="H" pinCount={10} pitch="2.54mm" footprint={f} pcbRotation={rot}
      pinLabels={["P0","P1","P2","P3","P4","P5","P6","P7","P8","P9"]} pcbX={0} pcbY={0} />
  </board>
)
