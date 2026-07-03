import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"],
  pin4: ["pin4"],
  pin5: ["pin5"],
  pin6: ["pin6"],
  pin7: ["pin7"],
  pin8: ["pin8"],
  pin9: ["pin9"]
} as const

export const WAFER_XH2_54_9PZZ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5359637"
  ]
}}
      manufacturerPartNumber="WAFER_XH2_54_9PZZ"
      footprint={<footprint>
        <platedhole  portHints={["pin1"]} pcbX="-9.99998mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin2"]} pcbX="-7.499858mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin3"]} pcbX="-4.99999mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin4"]} pcbX="-2.499868mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin5"]} pcbX="-0mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin6"]} pcbX="2.500122mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin7"]} pcbX="4.99999mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin8"]} pcbX="7.500112mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin9"]} pcbX="9.99998mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<silkscreenpath route={[{"x":12.49997499999995,"y":-0.2539999999999054},{"x":11.810974600000009,"y":-0.2539999999999054}]} />
<silkscreenpath route={[{"x":-11.810974600000122,"y":-1.0159999999999627},{"x":-12.499975000000177,"y":-1.0159999999999627}]} />
<silkscreenpath route={[{"x":-11.810974600000122,"y":-0.2539999999999054},{"x":-12.499975000000177,"y":-0.2539999999999054}]} />
<silkscreenpath route={[{"x":12.49997499999995,"y":-1.0159999999999627},{"x":11.810974600000009,"y":-1.0159999999999627}]} />
<silkscreenpath route={[{"x":12.49997499999995,"y":3.4999930000000177},{"x":12.49997499999995,"y":-2.399995200000035}]} />
<silkscreenpath route={[{"x":-12.499975000000177,"y":3.4999930000000177},{"x":-12.499975000000177,"y":-2.399995200000035}]} />
<silkscreenpath route={[{"x":12.49997499999995,"y":3.4999930000000177},{"x":-12.499975000000177,"y":3.4999930000000177}]} />
<silkscreenpath route={[{"x":12.49997499999995,"y":-2.399995200000035},{"x":-12.499975000000177,"y":-2.399995200000035}]} />
<courtyardoutline outline={[{"x":-12.789980000000128,"y":3.7552000000001726},{"x":12.729019999999991,"y":3.7552000000001726},{"x":12.729019999999991,"y":-2.663000000000011},{"x":-12.789980000000128,"y":-2.663000000000011},{"x":-12.789980000000128,"y":3.7552000000001726}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359637.obj?uuid=d4094786c1e94a1c800475e3e29e2d10",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359637.step?uuid=d4094786c1e94a1c800475e3e29e2d10",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -0.5379885000000924, z: -0.000006799999999973494 },
      }}
      {...props}
    />
  )
}