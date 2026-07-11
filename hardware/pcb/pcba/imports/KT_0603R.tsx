import type { LedProps } from "@tscircuit/props"

export const KT_0603R = (props: LedProps) => {
  const { name = "LED1", ...restProps } = props

  return (
    <led
      name={name}
      supplierPartNumbers={{
  "jlcpcb": [
    "C2286"
  ]
}}
      manufacturerPartNumber="KT_0603R"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="-0.750062mm" pcbY="0mm" width="0.7999984mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="0.750062mm" pcbY="0mm" width="0.7999984mm" height="0.7999984mm" shape="rect" />
<courtyardoutline outline={[{"x":-1.9474820000000364,"y":0.9459599999999},{"x":1.7275180000000319,"y":0.9459599999999},{"x":1.7275180000000319,"y":-0.9510400000000345},{"x":-1.9474820000000364,"y":-0.9510400000000345},{"x":-1.9474820000000364,"y":0.9459599999999}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C2286.obj?uuid=0da0275bf7a84667bce8747a921fb9e3",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C2286.step?uuid=0da0275bf7a84667bce8747a921fb9e3",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0.000050799999826267594, y: -0.00005079999993995443, z: -0.01 },
      }}
      {...restProps}
    />
  )
}