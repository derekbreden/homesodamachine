import type { ChipProps } from "@tscircuit/props"

// MT3608 — Aerosemi 2 A step-up (boost) converter, SOT-23-6 (C84817). Pin map from the
// easyeda/JLCPCB library part (footprint SOT-23-6_L2.9-W1.6-P0.95): 1 SW, 2 GND, 3 FB,
// 4 EN, 5 IN, 6 NC. Vout = 0.6 V·(1 + Rfb_top/Rfb_bot). Async boost: external Schottky
// rectifier off SW to Vout, and an inductor from IN to SW.
const pinLabels = {
  pin1: ["SW"],
  pin2: ["GND"],
  pin3: ["FB"],
  pin4: ["EN"],
  pin5: ["VIN"],
  pin6: ["NC"],
} as const

export const MT3608 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{ jlcpcb: ["C84817"] }}
      manufacturerPartNumber="MT3608"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-0.95mm" pcbY="-1.149mm" width="0.532mm" height="1.072mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="0mm" pcbY="-1.149mm" width="0.532mm" height="1.072mm" shape="rect" />
        <smtpad portHints={["pin3"]} pcbX="0.95mm" pcbY="-1.149mm" width="0.532mm" height="1.072mm" shape="rect" />
        <smtpad portHints={["pin4"]} pcbX="0.95mm" pcbY="1.149mm" width="0.532mm" height="1.072mm" shape="rect" />
        <smtpad portHints={["pin5"]} pcbX="0mm" pcbY="1.149mm" width="0.532mm" height="1.072mm" shape="rect" />
        <smtpad portHints={["pin6"]} pcbX="-0.95mm" pcbY="1.149mm" width="0.532mm" height="1.072mm" shape="rect" />
        <courtyardoutline outline={[{ x: -1.5, y: -1.95 }, { x: 1.5, y: -1.95 }, { x: 1.5, y: 1.95 }, { x: -1.5, y: 1.95 }, { x: -1.5, y: -1.95 }]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C84817.obj?uuid=229b69761e2c45dba6a83d8866dec72d",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C84817.step?uuid=229b69761e2c45dba6a83d8866dec72d",
        pcbRotationOffset: 90,
      }}
      {...props}
    />
  )
}
