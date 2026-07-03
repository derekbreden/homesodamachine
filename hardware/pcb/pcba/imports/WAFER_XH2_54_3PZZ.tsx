import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"]
} as const

export const WAFER_XH2_54_3PZZ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5374805"
  ]
}}
      manufacturerPartNumber="WAFER_XH2_54_3PZZ"
      footprint={<footprint>
        <platedhole  portHints={["pin1"]} pcbX="-2.499995mm" pcbY="0mm" outerDiameter="1.524mm" holeDiameter="0.9144mm" shape="circle" />
<platedhole  portHints={["pin2"]} pcbX="0.000127mm" pcbY="0mm" outerDiameter="1.524mm" holeDiameter="0.9144mm" shape="circle" />
<platedhole  portHints={["pin3"]} pcbX="2.499995mm" pcbY="0mm" outerDiameter="1.524mm" holeDiameter="0.9144mm" shape="circle" />
<silkscreenpath route={[{"x":-1.3204443999999285,"y":-2.9209999999999354},{"x":1.2700000000002092,"y":-2.9209999999999354},{"x":1.2700000000002092,"y":-2.399995200000035}]} />
<silkscreenpath route={[{"x":-1.3204443999999285,"y":-2.399995200000035},{"x":-1.3204443999999285,"y":-2.9209999999999354}]} />
<silkscreenpath route={[{"x":4.999990000000025,"y":3.1999935999999707},{"x":4.999990000000025,"y":-2.399995200000035}]} />
<silkscreenpath route={[{"x":-4.999990000000025,"y":3.1999935999999707},{"x":-4.999990000000025,"y":-2.399995200000035}]} />
<silkscreenpath route={[{"x":4.999990000000025,"y":-2.399995200000035},{"x":-4.999990000000025,"y":-2.399995200000035}]} />
<silkscreenpath route={[{"x":4.999990000000025,"y":3.1999935999999707},{"x":-4.999990000000025,"y":3.1999935999999707}]} />
<courtyardoutline outline={[{"x":-5.289994999999976,"y":3.4504000000000588},{"x":5.243005000000039,"y":3.4504000000000588},{"x":5.243005000000039,"y":-3.22180000000003},{"x":-5.289994999999976,"y":-3.22180000000003},{"x":-5.289994999999976,"y":3.4504000000000588}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5374805.obj?uuid=75868382eac940f7b1b5135168a01a5d",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5374805.step?uuid=75868382eac940f7b1b5135168a01a5d",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -0.09999979999997777, z: -0.000006799999999973494 },
      }}
      {...props}
    />
  )
}