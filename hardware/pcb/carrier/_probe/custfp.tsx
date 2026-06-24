// One component, hand-authored VERTICAL footprint (no footprinter, no courtyard),
// still addressable by pin label for wiring.
const L = ["P0","P1","P2","P3","P4","P5","P6","P7","P8","P9"]
const vfp = (
  <footprint>
    {L.map((lbl,k)=>(
      <platedhole key={k} portHints={[lbl, String(k+1)]} shape="circle"
        holeDiameter="1mm" outerDiameter="1.8mm" pcbX={0} pcbY={(k-4.5)*2.54} />
    ))}
  </footprint>
)
export default () => (
  <board width="60mm" height="60mm">
    <chip name="U9" footprint={vfp} pinLabels={{pin1:"P0",pin2:"P1",pin3:"P2",pin4:"P3",pin5:"P4",pin6:"P5",pin7:"P6",pin8:"P7",pin9:"P8",pin10:"P9"}} pcbX={-12} pcbY={0} />
    <pinheader name="REF" pinCount={3} pitch="2.54mm" footprint="pinrow3" pinLabels={["P0","P1","P2"]} pcbX={12} pcbY={0} />
    <trace from=".U9 > .P0" to=".REF > .P0" />
    <trace from=".U9 > .P1" to=".REF > .P1" />
  </board>
)
