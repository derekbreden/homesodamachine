import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["_POS"],
  pin2: ["_NEG"],
  pin3: ["NC"]
} as const

export const MLT_5020 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C94598"
  ]
}}
      manufacturerPartNumber="MLT_5020"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="2.29997mm" pcbY="-1.749933mm" width="1.6999966mm" height="0.6999986mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-2.29997mm" pcbY="-1.749933mm" width="1.6999966mm" height="0.6999986mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-2.29997mm" pcbY="1.749933mm" width="1.6999966mm" height="0.6999986mm" shape="rect" />
<silkscreenpath route={[{"x":-2.793999999999869,"y":2.3312120000000505},{"x":-2.793999999999869,"y":2.5400000000000773},{"x":1.77800000000002,"y":2.5400000000000773},{"x":2.7940000000000964,"y":1.524000000000001}]} />
<silkscreenpath route={[{"x":-2.793999999999869,"y":-1.168781000000081},{"x":-2.793999999999869,"y":1.168907999999874}]} />
<silkscreenpath route={[{"x":-2.793999999999869,"y":-2.5400000000000773},{"x":-2.793999999999869,"y":-2.33108500000003}]} />
<silkscreenpath route={[{"x":2.7934920000001284,"y":-2.3315930000001117},{"x":2.7934920000001284,"y":-2.539873000000057},{"x":-2.793999999999869,"y":-2.5400000000000773}]} />
<silkscreenpath route={[{"x":2.7940000000000964,"y":1.524000000000001},{"x":2.7940000000000964,"y":-1.168781000000081}]} />
<silkscreentext text="+" pcbX="-1.524mm" pcbY="-1.397127mm" anchorAlignment="bottom_left" fontSize="2.032mm" />
<silkscreentext text="-" pcbX="0.762mm" pcbY="-1.397127mm" anchorAlignment="bottom_left" fontSize="2.032mm" />
<silkscreentext text="{NAME}" pcbX="-0.003048mm" pcbY="3.618867mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-3.4026479999998855,"y":2.8688669999999092},{"x":3.3965520000000424,"y":2.8688669999999092},{"x":3.3965520000000424,"y":-2.8889330000000655},{"x":-3.4026479999998855,"y":-2.8889330000000655},{"x":-3.4026479999998855,"y":2.8688669999999092}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C94598.obj?uuid=5e71db11d9fa48278b90d6344e196479",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C94598.step?uuid=5e71db11d9fa48278b90d6344e196479",
        pcbRotationOffset: 270,
        modelOriginPosition: { x: 0.00007619999996677507, y: 0.06042139999991303, z: 0 },
      }}
      {...props}
    />
  )
}