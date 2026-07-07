import type { ChipProps } from "@tscircuit/props"

// SS34 — 40 V / 3 A Schottky rectifier, SMA / DO-214AC (C8678). easyeda/JLCPCB library part
// (footprint SMA_L4.3-W2.6-LS5.2): pin1 K (cathode, band end), pin2 A (anode). Current flows
// anode(pin2) -> cathode(pin1). Used here for the boost rectifier and the two reverse-isolation
// diodes (VBUS->V5, and — on a production board — nothing; demo only).
const pinLabels = {
  pin1: ["K"],
  pin2: ["A"],
} as const

export const SS34 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{ jlcpcb: ["C8678"] }}
      manufacturerPartNumber="SS34"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-2.2mm" pcbY="0mm" width="2.0mm" height="2.0mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="2.2mm" pcbY="0mm" width="2.0mm" height="2.0mm" shape="rect" />
        <courtyardoutline outline={[{ x: -3.35, y: -1.35 }, { x: 3.35, y: -1.35 }, { x: 3.35, y: 1.35 }, { x: -3.35, y: 1.35 }, { x: -3.35, y: -1.35 }]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C8678.obj?uuid=e3551acb3c5a4975a5e9d36087fe1fa2",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C8678.step?uuid=e3551acb3c5a4975a5e9d36087fe1fa2",
        pcbRotationOffset: 0,
      }}
      {...props}
    />
  )
}
