// A vertical header built two ways, to see which emits a (correct) courtyard.
const col = (name: string, x: number) =>
  [0,1,2,3,4,5,6,7,8,9].map(k =>
    <platedhole key={k} name={`${name}_P${k}`} shape="circle" holeDiameter="1mm" outerDiameter="1.8mm"
      portHints={[`P${k}`]} pcbX={x} pcbY={(k-4.5)*2.54} />)
export default () => (
  <board width="60mm" height="60mm">
    {/* A: footprinter pinrow rotated 90 (our current approach) */}
    <pinheader name="A" pinCount={10} pitch="2.54mm" footprint="pinrow10" pcbRotation={90}
      pinLabels={["P0","P1","P2","P3","P4","P5","P6","P7","P8","P9"]} pcbX={-15} pcbY={0} />
    {/* B: hand-placed vertical plated holes, no footprinter */}
    {col("B", 15)}
    <trace from=".A > .P0" to=".B_P0 > .P0" />
  </board>
)
