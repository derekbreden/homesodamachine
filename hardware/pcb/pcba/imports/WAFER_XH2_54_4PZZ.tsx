import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"],
  pin4: ["pin4"]
} as const

export const WAFER_XH2_54_4PZZ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5359632"
  ]
}}
      manufacturerPartNumber="WAFER_XH2_54_4PZZ"
      footprint={<footprint>
        <platedhole  portHints={["pin4"]} pcbX="3.75mm" pcbY="-0.000127mm" outerDiameter="1.499997mm" holeDiameter="0.9000236mm" shape="circle" />
<platedhole  portHints={["pin3"]} pcbX="1.25mm" pcbY="-0.000127mm" outerDiameter="1.499997mm" holeDiameter="0.9000236mm" shape="circle" />
<platedhole  portHints={["pin2"]} pcbX="-1.25mm" pcbY="-0.000127mm" outerDiameter="1.499997mm" holeDiameter="0.9000236mm" shape="circle" />
<platedhole  portHints={["pin1"]} pcbX="-3.75mm" pcbY="0.000127mm" outerDiameter="1.499997mm" holeDiameter="0.9000236mm" shape="circle" />
<silkscreenpath route={[{"x":-5.588050800000019,"y":-1.0328147999999828},{"x":-6.249974800000018,"y":-1.0328147999999828}]} />
<silkscreenpath route={[{"x":6.249873199999911,"y":-1.040561799999864},{"x":5.587949199999912,"y":-1.040561799999864}]} />
<silkscreenpath route={[{"x":5.5899303999999574,"y":-0.15008860000000368},{"x":6.2518543999999565,"y":-0.15008860000000368}]} />
<silkscreenpath route={[{"x":-6.247968199999946,"y":-0.15775940000003175},{"x":-5.586069599999973,"y":-0.15775940000003175}]} />
<silkscreenpath route={[{"x":6.249873199999911,"y":-2.349703199999908},{"x":-6.249974800000018,"y":-2.349703199999908}]} />
<silkscreenpath route={[{"x":-6.249974800000018,"y":3.50},{"x":6.249873199999911,"y":3.50}]} />
<silkscreenpath route={[{"x":6.249873199999911,"y":3.50},{"x":6.249873199999911,"y":-2.349703199999908}]} />
<silkscreenpath route={[{"x":-6.249974800000018,"y":-2.349703199999908},{"x":-6.249974800000018,"y":3.50}]} />
<silkscreenpath route={[{"x":-5.588050800000019,"y":2.5399238000001105},{"x":-5.588050800000019,"y":-1.7780761999999868},{"x":5.587949199999912,"y":-1.7780761999999868},{"x":5.587949199999912,"y":2.5399238000001105},{"x":-5.588050800000019,"y":2.5399238000001105}]} />
<silkscreenpath route={[{"x":-4.592543400000127,"y":-1.7780761999999868},{"x":-4.592543400000127,"y":-2.349703199999908}]} />
<silkscreenpath route={[{"x":-2.865318000000061,"y":-1.7780761999999868},{"x":-2.865318000000061,"y":-2.349703199999908}]} />
<silkscreenpath route={[{"x":2.9328820000000087,"y":-1.7780761999999868},{"x":2.9328820000000087,"y":-2.349703199999908}]} />
<silkscreenpath route={[{"x":4.558456599999945,"y":-1.7780761999999868},{"x":4.558456599999945,"y":-2.349703199999908}]} />
<courtyardoutline outline={[{"x":-6.523799999999937,"y":3.721544999999992},{"x":6.498400000000174,"y":3.721544999999992},{"x":6.498400000000174,"y":-2.6966549999999643},{"x":-6.523799999999937,"y":-2.6966549999999643},{"x":-6.523799999999937,"y":3.721544999999992}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359632.obj?uuid=0c24b14046bf4569801f186f9b426daa",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359632.step?uuid=0c24b14046bf4569801f186f9b426daa",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0.000038099999983387534, y: -0.5099341999999707, z: -0.000006799999999973494 },
      }}
      {...props}
    />
  )
}