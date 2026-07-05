import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"],
  pin4: ["pin4"],
  pin5: ["pin5"]
} as const

export const WAFER_XH2_54_5PZZ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C5359633"
  ]
}}
      manufacturerPartNumber="WAFER_XH2_54_5PZZ"
      footprint={<footprint>
        <platedhole  portHints={["pin1"]} pcbX="-4.99999mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin2"]} pcbX="-2.500122mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin3"]} pcbX="0mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin4"]} pcbX="2.500122mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<platedhole  portHints={["pin5"]} pcbX="4.99999mm" pcbY="0mm" outerDiameter="1.5999968mm" holeDiameter="0.999998mm" shape="circle" />
<silkscreenpath route={[{"x":-7.500010400000065,"y":1.1998960000000807},{"x":-6.899986200000058,"y":1.1998960000000807}]} />
<silkscreenpath route={[{"x":-7.500010400000065,"y":2.374900000000025},{"x":-7.500010400000065,"y":-3.50},{"x":7.500010399999951,"y":-3.50},{"x":7.500010399999951,"y":2.374900000000025},{"x":-7.500010400000065,"y":2.374900000000025}]} />
<silkscreenpath route={[{"x":-7.500010400000065,"y":0.5692394000000149},{"x":-6.899986200000058,"y":0.5692394000000149}]} />
<silkscreenpath route={[{"x":6.900011599999857,"y":0.5692648000000418},{"x":7.500010399999951,"y":0.5692648000000418}]} />
<silkscreenpath route={[{"x":6.900011599999857,"y":1.1998960000000807},{"x":7.500010399999951,"y":1.1998960000000807}]} />
<silkscreenpath route={[{"x":4.339234399999896,"y":2.387447600000087},{"x":4.339234399999896,"y":1.856257400000004}]} />
<silkscreenpath route={[{"x":5.700013999999896,"y":2.29989379999995},{"x":5.700013999999896,"y":1.8124170000000959}]} />
<silkscreenpath route={[{"x":-6.900011599999971,"y":1.7998947999999473},{"x":-6.900011599999971,"y":-3.000095599999895},{"x":6.900011599999857,"y":-3.000095599999895},{"x":6.900011599999857,"y":1.7998947999999473},{"x":-6.900011599999971,"y":1.7998947999999473}]} />
<silkscreenpath route={[{"x":-5.571261400000026,"y":2.374900000000025},{"x":-5.571261400000026,"y":1.8436844000000292}]} />
<silkscreenpath route={[{"x":-5.571261400000026,"y":1.8436844000000292},{"x":-5.5665488472276365,"y":1.8199858607190436},{"x":-5.553125800000089,"y":1.7998947999999473}]} />
<silkscreenpath route={[{"x":-4.174261400000091,"y":2.374900000000025},{"x":-4.201104567834932,"y":2.3347304126975814},{"x":-4.210532599999965,"y":2.2873462000000018}]} />
<silkscreenpath route={[{"x":-4.210532599999965,"y":2.2873462000000018},{"x":-4.210532599999965,"y":1.7998947999999473}]} />
<silkscreenpath route={[{"x":5.736259799999971,"y":2.387447600000087},{"x":5.70941663216513,"y":2.3472780126974158},{"x":5.699988600000097,"y":2.29989379999995}]} />
<silkscreenpath route={[{"x":4.3392597999999225,"y":1.856232000000091},{"x":4.343972352772425,"y":1.8325334607189916},{"x":4.357395399999973,"y":1.812442400000009}]} />
<courtyardoutline outline={[{"x":-7.768400000000042,"y":2.6503000000001293},{"x":7.768399999999929,"y":2.6503000000001293},{"x":7.768399999999929,"y":-3.767900000000054},{"x":-7.768400000000042,"y":-3.767900000000054},{"x":-7.768400000000042,"y":2.6503000000001293}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359633.obj?uuid=734fe54367814b879ac1b4031d994be3",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C5359633.step?uuid=734fe54367814b879ac1b4031d994be3",
        pcbRotationOffset: 180,
        modelOriginPosition: { x: 0, y: -0.5001005999999961, z: 0.09999300000000044 },
      }}
      {...props}
    />
  )
}