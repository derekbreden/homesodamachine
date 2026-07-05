import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"],
  pin4: ["pin4"],
  pin5: ["pin5"],
  pin6: ["pin6"]
} as const

export const WAFER_XH2_54_6PZZ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5359634"
  ]
}}
      manufacturerPartNumber="WAFER_XH2_54_6PZZ"
      footprint={<footprint>
        <platedhole  portHints={["pin1"]} pcbX="-6.249924mm" pcbY="0mm" outerDiameter="1.6500094mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin2"]} pcbX="-3.750056mm" pcbY="0mm" outerDiameter="1.6500094mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin3"]} pcbX="-1.249934mm" pcbY="0mm" outerDiameter="1.6500094mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin4"]} pcbX="1.249934mm" pcbY="0mm" outerDiameter="1.6500094mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin5"]} pcbX="3.750056mm" pcbY="0mm" outerDiameter="1.6500094mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin6"]} pcbX="6.249924mm" pcbY="0mm" outerDiameter="1.6500094mm" holeDiameter="1.1000232mm" shape="circle" />
<silkscreenpath route={[{"x":-8.800058600000057,"y":1.0999470000000429},{"x":-8.200034400000163,"y":1.0999470000000429}]} />
<silkscreenpath route={[{"x":-8.800058600000057,"y":-0.000050799999826267594},{"x":-8.200034400000163,"y":-0.000050799999826267594}]} />
<silkscreenpath route={[{"x":-8.800007800000117,"y":2.474899800000003},{"x":-8.800007800000117,"y":-3.50},{"x":8.800007800000003,"y":-3.50},{"x":8.800007800000003,"y":2.474899800000003},{"x":-8.800007800000117,"y":2.474899800000003}]} />
<silkscreenpath route={[{"x":8.199983599999996,"y":-0.000050799999826267594},{"x":8.800007800000003,"y":-0.000050799999826267594}]} />
<silkscreenpath route={[{"x":8.199983599999996,"y":1.0999470000000429},{"x":8.800007800000003,"y":1.0999470000000429}]} />
<silkscreenpath route={[{"x":5.499963600000001,"y":1.8999454000000924},{"x":5.499963600000001,"y":2.474899800000003}]} />
<silkscreenpath route={[{"x":4.099940999999944,"y":1.8999454000000924},{"x":4.099940999999944,"y":2.474899800000003}]} />
<silkscreenpath route={[{"x":-5.900039000000106,"y":1.8999454000000924},{"x":-5.900039000000106,"y":2.474899800000003}]} />
<silkscreenpath route={[{"x":-4.5000164000000495,"y":1.8999454000000924},{"x":-4.5000164000000495,"y":2.474899800000003}]} />
<courtyardoutline outline={[{"x":-9.038400000000024,"y":2.726500000000101},{"x":9.063799999999901,"y":2.726500000000101},{"x":9.063799999999901,"y":-3.691699999999969},{"x":-9.038400000000024,"y":-3.691699999999969},{"x":-9.038400000000024,"y":2.726500000000101}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359634.obj?uuid=7eb11e45495244088378b19bd8a4dc5f",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359634.step?uuid=7eb11e45495244088378b19bd8a4dc5f",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 6.250038099999983, y: 0.000049899999953639806, z: -0.000005999999999950489 },
      }}
      {...props}
    />
  )
}