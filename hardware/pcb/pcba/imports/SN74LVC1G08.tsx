import type { ChipProps } from "@tscircuit/props"

// SN74LVC1G08 — single 2-input AND gate, SOT-353 / SC-70-5 (C12512, ~29k stock). The
// firmware-independent gas→compressor interlock: it gates the ESP compressor command (A ← IO19)
// with the MQ-6 hardware gas-clear signal (B ← divided DOUT) and drives the relay line (Y → J5.IO19).
// Y = A·B, so the compressor energizes ONLY when firmware asks AND the sensor says clear.
//
// Pinout is the standard single-gate SC-70-5 map (Nexperia 74LVC1G08GW): pin1 = B (input),
// pin2 = A (input), pin3 = GND, pin4 = Y (output), pin5 = VCC. The pin-identical 74LVC1G00 NAND
// (C12508, same GW package) is a drop-in swap for an active-LOW relay module — no layout change.
// Pads are the IPC SC-70-5 land (0.65 mm pitch, 3 leads south / 2 north); the courtyard is a tight
// keep-out for the dense NE pocket. No cadModel — the 3D is deferred (like Q4/D8); the orientation
// audit skips model-less parts and the BOM/CPL ride supplierPartNumbers.
const pinLabels = {
  pin1: ["B"],
  pin2: ["A"],
  pin3: ["GND"],
  pin4: ["Y"],
  pin5: ["VCC"],
} as const

export const SN74LVC1G08 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{ jlcpcb: ["C12512"] }}
      manufacturerPartNumber="74LVC1G08GW,125"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-0.65mm" pcbY="-0.9mm" width="0.4mm" height="0.6mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="0mm" pcbY="-0.9mm" width="0.4mm" height="0.6mm" shape="rect" />
        <smtpad portHints={["pin3"]} pcbX="0.65mm" pcbY="-0.9mm" width="0.4mm" height="0.6mm" shape="rect" />
        <smtpad portHints={["pin4"]} pcbX="0.65mm" pcbY="0.9mm" width="0.4mm" height="0.6mm" shape="rect" />
        <smtpad portHints={["pin5"]} pcbX="-0.65mm" pcbY="0.9mm" width="0.4mm" height="0.6mm" shape="rect" />
        <courtyardoutline outline={[{"x":-1.05,"y":1.35},{"x":1.05,"y":1.35},{"x":1.05,"y":-1.35},{"x":-1.05,"y":-1.35},{"x":-1.05,"y":1.35}]} />
      </footprint>}
      {...props}
    />
  )
}
