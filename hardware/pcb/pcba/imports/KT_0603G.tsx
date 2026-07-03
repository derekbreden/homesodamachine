import type { LedProps } from "@tscircuit/props"

export const KT_0603G = (props: LedProps) => {
  const { name = "LED1", ...restProps } = props

  return (
    <led
      name={name}
      supplierPartNumbers={{
  "jlcpcb": [
    "C12624"
  ]
}}
      manufacturerPartNumber="KT_0603G"
      // pin1 = ANODE (+x pad), pin2 = CATHODE (-x, silk cathode bracket). tscircuit's <led>
      // hard-aliases anode->pin1, and the EasyEDA source for this KENTO part numbers the
      // cathode as pad 1 — so the pin1/pin2 portHints are swapped from the raw import to match
      // the anode=pin1 convention (and the red KT-0603R). Keep this if re-importing C12624.
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="0.7489952mm" pcbY="0.000127mm" width="0.7999984mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-0.7489952mm" pcbY="-0.000127mm" width="0.7999984mm" height="0.7999984mm" shape="rect" />
<silkscreenpath route={[{"x":0.22042119999991883,"y":-0.3235197999999855},{"x":0.21046439999986433,"y":-0.3235197999999855},{"x":-0.11958320000007916,"y":0.006527799999958006}]} />
<silkscreenpath route={[{"x":0.22042119999991883,"y":0.3565143999999236},{"x":0.22042119999991883,"y":0.346532199999956},{"x":-0.11958320000007916,"y":0.006527799999958006}]} />
<silkscreenpath route={[{"x":0.22042119999991883,"y":0.3565143999999236},{"x":0.22042119999991883,"y":-0.3235197999999855}]} />
<silkscreenpath route={[{"x":0.24046179999993456,"y":0.7565898000000288},{"x":1.3904721999999765,"y":0.7565898000000288}]} />
<silkscreenpath route={[{"x":0.24046179999993456,"y":-0.7435342000001128},{"x":1.3904721999999765,"y":-0.7435342000001128}]} />
<silkscreenpath route={[{"x":1.3904721999999765,"y":0.7564882000000352},{"x":1.3904721999999765,"y":-0.7234428000000435}]} />
<silkscreenpath route={[{"x":-0.13954760000001443,"y":-0.7458455999999387},{"x":-1.1896598000000722,"y":-0.7458455999999387}]} />
<silkscreenpath route={[{"x":-1.4896084000000656,"y":-0.3457701999999472},{"x":-1.4896084000000656,"y":-0.44579539999995177},{"x":-1.1896598000000722,"y":-0.7458455999999387}]} />
<silkscreenpath route={[{"x":-1.4896084000000656,"y":0.3541776000000709},{"x":-1.4896084000000656,"y":-0.3457701999999472}]} />
<silkscreenpath route={[{"x":-1.4896084000000656,"y":0.3541776000000709},{"x":-1.4896084000000656,"y":0.45432980000009593},{"x":-1.1896598000000722,"y":0.7542784000000893}]} />
<silkscreenpath route={[{"x":-0.13954760000001443,"y":0.7542784000000893},{"x":-1.1896598000000722,"y":0.7542784000000893}]} />
<silkscreenpath route={[{"x":0.22042119999991883,"y":0.006527799999958006},{"x":-0.11958320000007916,"y":0.006527799999958006}]} />
<courtyardoutline outline={[{"x":-1.7517750000001797,"y":1.0177150000000665},{"x":1.618425000000002,"y":1.0177150000000665},{"x":1.618425000000002,"y":-0.9808849999999438},{"x":-1.7517750000001797,"y":-0.9808849999999438},{"x":-1.7517750000001797,"y":1.0177150000000665}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C12624.obj?uuid=3c2caa1a3e7d4a5a87f46b87d898ef41",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C12624.step?uuid=3c2caa1a3e7d4a5a87f46b87d898ef41",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: -0.000012700000070253736, y: 0.000012699999956566899, z: -0.01 },
      }}
      {...restProps}
    />
  )
}