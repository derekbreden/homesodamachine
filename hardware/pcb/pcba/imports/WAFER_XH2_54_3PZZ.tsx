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
{/* Silk rebuilt to the real XUNPU WAFER-XH2.54-NPZZ geometry (the stock EasyEDA footprint
    for this SKU drew a spurious tab and a too-shallow 5.6 mm body). Datasheet: body B=10 mm
    wide (x ±5.0), depth 5.90 mm, pitch 2.50 mm. The pin row sits 3.50 mm from the opening
    (shroud) face and 2.40 mm from the base face — the SAME offset every count in this series
    has, verified against the 9P/6P footprints (depth 5.90) and the on-board plastic-to-edge
    check. Opening is +Y. Inner shroud wall + base-cavity slot ticks match the 4P sibling. */}
<silkscreenpath route={[{"x":-5.0,"y":-2.40},{"x":-5.0,"y":3.50}]} />
<silkscreenpath route={[{"x":5.0,"y":-2.40},{"x":5.0,"y":3.50}]} />
<silkscreenpath route={[{"x":-5.0,"y":3.50},{"x":5.0,"y":3.50}]} />
<silkscreenpath route={[{"x":-5.0,"y":-2.40},{"x":5.0,"y":-2.40}]} />
<silkscreenpath route={[{"x":-4.338,"y":-1.778},{"x":-4.338,"y":2.54},{"x":4.338,"y":2.54},{"x":4.338,"y":-1.778},{"x":-4.338,"y":-1.778}]} />
<silkscreenpath route={[{"x":3.32,"y":-2.40},{"x":3.32,"y":-1.778}]} />
<silkscreenpath route={[{"x":1.68,"y":-2.40},{"x":1.68,"y":-1.778}]} />
<silkscreenpath route={[{"x":-1.68,"y":-2.40},{"x":-1.68,"y":-1.778}]} />
<silkscreenpath route={[{"x":-3.32,"y":-2.40},{"x":-3.32,"y":-1.778}]} />
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