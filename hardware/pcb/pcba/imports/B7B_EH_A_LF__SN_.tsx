import type { ChipProps } from "@tscircuit/props"

// B7B-EH-A (C160254) — JST-EH 7P, the keyed alternative to the XH reeds header (see parts.tsx).
// The {NAME} silk is stripped (the Jst wrapper draws the ref-des). The model CDN has an OBJ for
// C160254 but no STEP (.obj 200, .step 404), so the cadModel carries objUrl only — board-3d.py
// builds the 3D body from the OBJ mesh (its STEP-less twin path), and the STEP-based orientation
// audit skips it. modelOriginPosition / pcbRotationOffset are `tsci import`'s and place the OBJ
// (same EasyEDA geometry/frame the STEP would use).

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"],
  pin4: ["pin4"],
  pin5: ["pin5"],
  pin6: ["pin6"],
  pin7: ["pin7"]
} as const

export const B7B_EH_A_LF__SN_ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C160254"
  ]
}}
      manufacturerPartNumber="B7B_EH_A_LF__SN_"
      footprint={<footprint>
        <platedhole  portHints={["pin1"]} pcbX="-7.499985mm" pcbY="0mm" outerDiameter="1.850009mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin2"]} pcbX="-4.999863mm" pcbY="0mm" outerDiameter="1.850009mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin3"]} pcbX="-2.499995mm" pcbY="0mm" outerDiameter="1.850009mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin4"]} pcbX="0.000127mm" pcbY="0mm" outerDiameter="1.850009mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin5"]} pcbX="2.499995mm" pcbY="0mm" outerDiameter="1.850009mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin6"]} pcbX="5.000117mm" pcbY="0mm" outerDiameter="1.850009mm" holeDiameter="1.1000232mm" shape="circle" />
<platedhole  portHints={["pin7"]} pcbX="7.499985mm" pcbY="0mm" outerDiameter="1.850009mm" holeDiameter="1.1000232mm" shape="circle" />
<silkscreenpath route={[{"x":10.150475,"y":1.7500599999999906},{"x":10.150475,"y":-2.349500000000006}]} />
<silkscreenpath route={[{"x":-10.149204999999995,"y":0},{"x":-9.648824999999988,"y":0},{"x":-9.648824999999988,"y":1.249679999999998},{"x":9.700895000000003,"y":1.249679999999998}]} />
<silkscreenpath route={[{"x":-10.149204999999995,"y":-0.8508999999999958},{"x":-9.150985000000006,"y":-0.8508999999999958},{"x":-9.150985000000006,"y":-2.349500000000006}]} />
<silkscreenpath route={[{"x":-10.149204999999995,"y":1.7500599999999906},{"x":-10.149204999999995,"y":-2.349500000000006}]} />
<silkscreenpath route={[{"x":-10.149204999999995,"y":1.7500599999999906},{"x":10.150475,"y":1.7500599999999906}]} />
<silkscreenpath route={[{"x":10.150475,"y":-2.349500000000006},{"x":-10.149204999999995,"y":-2.349500000000006}]} />
<silkscreenpath route={[{"x":9.700895000000003,"y":0},{"x":10.150475,"y":0}]} />
<silkscreenpath route={[{"x":9.700895000000003,"y":0},{"x":9.700895000000003,"y":1.249679999999998}]} />
<silkscreenpath route={[{"x":10.09967499999999,"y":-0.8001000000000005},{"x":9.098915000000005,"y":-0.8001000000000005},{"x":9.098915000000005,"y":-2.298700000000011}]} />
<courtyardoutline outline={[{"x":-10.391584999999992,"y":2.002599999999987},{"x":10.403014999999996,"y":2.002599999999987},{"x":10.403014999999996,"y":-2.586800000000025},{"x":-10.391584999999992,"y":-2.586800000000025},{"x":-10.391584999999992,"y":2.002599999999987}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C160254.obj?uuid=66590d75cddd41bfa876d1dd5d046a34",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: -0.0009905999999944015, y: 0.29999940000001857, z: 0.2999930000000002 },
      }}
      {...props}
    />
  )
}