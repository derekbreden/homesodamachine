import type { ChipProps } from "@tscircuit/props"

// FNR4030S4R7MT — 4.7 µH shielded SMD power inductor, 4.0×4.0 mm (C167874). easyeda/JLCPCB
// library part (footprint IND-SMD_L4.0-W4.0_FNR40XXS): two pads, non-polar (pin1/pin2). The
// boost inductor between VBUS and the MT3608 SW node.
const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
} as const

export const FNR4030 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{ jlcpcb: ["C167874"] }}
      manufacturerPartNumber="FNR4030S4R7MT"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-1.5mm" pcbY="0mm" width="1.6mm" height="3.9mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="1.5mm" pcbY="0mm" width="1.6mm" height="3.9mm" shape="rect" />
        <courtyardoutline outline={[{ x: -2.1, y: -2.1 }, { x: 2.1, y: -2.1 }, { x: 2.1, y: 2.1 }, { x: -2.1, y: 2.1 }, { x: -2.1, y: -2.1 }]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C167874.obj?uuid=f10f9856fbf34a8a9250995f07743de3",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C167874.step?uuid=f10f9856fbf34a8a9250995f07743de3",
        pcbRotationOffset: 270,
      }}
      {...props}
    />
  )
}
