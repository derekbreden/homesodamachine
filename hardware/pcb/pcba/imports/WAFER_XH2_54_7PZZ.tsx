import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"],
  pin4: ["pin4"],
  pin5: ["pin5"],
  pin6: ["pin6"],
  pin7: ["pin7"]
} as const

export const WAFER_XH2_54_7PZZ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5359635"
  ]
}}
      manufacturerPartNumber="WAFER_XH2_54_7PZZ"
      footprint={<footprint>
        <platedhole  portHints={["pin7"]} pcbX="-7.62mm" pcbY="0mm" outerDiameter="1.7999964mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin6"]} pcbX="-5.08mm" pcbY="0mm" outerDiameter="1.7999964mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin5"]} pcbX="-2.54mm" pcbY="0mm" outerDiameter="1.7999964mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin4"]} pcbX="-0mm" pcbY="0mm" outerDiameter="1.7999964mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin3"]} pcbX="2.54mm" pcbY="0mm" outerDiameter="1.7999964mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin2"]} pcbX="5.08mm" pcbY="0mm" outerDiameter="1.7999964mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin1"]} pcbX="7.62mm" pcbY="0mm" outerDiameter="1.7999964mm" holeDiameter="1.1000232mm" shape="circle" />
<silkscreenpath route={[{"x":7.039990999999873,"y":1.7999964000000546},{"x":7.039990999999873,"y":2.4349964000000455}]} />
<silkscreenpath route={[{"x":8.055051199999752,"y":1.7779237999999395},{"x":8.055051199999752,"y":2.412923800000044}]} />
<silkscreenpath route={[{"x":-8.039989000000105,"y":1.699996599999963},{"x":-8.039989000000105,"y":2.399995199999921}]} />
<silkscreenpath route={[{"x":-7.0399910000001,"y":2.399995199999921},{"x":-7.0384162000001425,"y":1.6870172000000139}]} />
<silkscreenpath route={[{"x":4.192270000000008,"y":-2.6924000000000206},{"x":8.999981999999818,"y":-2.6924000000000206},{"x":8.999981999999818,"y":1.6764000000000578}]} />
<silkscreenpath route={[{"x":4.159046799999942,"y":1.6764000000000578},{"x":8.999981999999818,"y":1.6764000000000578}]} />
<silkscreenpath route={[{"x":4.159046799999942,"y":1.6764000000000578},{"x":-9.396730000000048,"y":1.6764000000000578},{"x":-9.396730000000048,"y":-2.6924000000000206},{"x":4.192270000000008,"y":-2.6924000000000206}]} />
<silkscreenpath route={[{"x":-10.000005400000077,"y":2.4999950000000126},{"x":-10.000005400000077,"y":-3.4999930000001314},{"x":10.000005399999964,"y":-3.4999930000001314},{"x":10.000005399999964,"y":2.4999950000000126},{"x":-10.000005400000077,"y":2.4999950000000126}]} />
<courtyardoutline outline={[{"x":-10.261410000000069,"y":2.7392000000000962},{"x":10.22838999999999,"y":2.7392000000000962},{"x":10.22838999999999,"y":-3.7551999999999452},{"x":-10.261410000000069,"y":-3.7551999999999452},{"x":-10.261410000000069,"y":2.7392000000000962}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359635.obj?uuid=7ee3caeb75114dc8ac6b488e06803f66",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359635.step?uuid=7ee3caeb75114dc8ac6b488e06803f66",
        pcbRotationOffset: 180,
        modelOriginPosition: { x: 0, y: -0.5049990000000026, z: -0.000006799999999973494 },
      }}
      {...props}
    />
  )
}