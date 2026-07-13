import type { ChipProps } from "@tscircuit/props"

// ESD9B3.3ST5G — bidirectional low-capacitance ESD/TVS, SOD-923 (C96512, onsemi). 3.3 V working /
// bidirectional, ~15 pF, 400 W (8/20 µs). The board-side faucet-UART clamp: one per line, shunting
// the U1-side of the series resistor (IO33/IO35) to the GND plane at the WROOM. Bidirectional, so
// pin1/pin2 are interchangeable — one taps the signal net, the other via-in-pads to GND. pin1 at
// −0.5 mm, pin2 at +0.5 mm on the 0.4 × 0.4 mm SOD-923 land. Footprint {NAME} silk stripped for the
// wrapper's upright ref-des; the body-outline silk is dropped (0.4 mm marks that would ink the tiny
// pads / crowd the WROOM south rim). No cadModel wiring here — BOM/CPL ride supplierPartNumbers.
const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
} as const

export const ESD9B3_3ST5G = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C96512"
  ]
}}
      manufacturerPartNumber="ESD9B3_3ST5G"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="0.499999mm" pcbY="0mm" width="0.3999992mm" height="0.3999992mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-0.499999mm" pcbY="0mm" width="0.3999992mm" height="0.3999992mm" shape="rect" />
<courtyardoutline outline={[{"x":-0.9613270000000966,"y":0.6310000000000855},{"x":0.9356729999999516,"y":0.6310000000000855},{"x":0.9356729999999516,"y":-0.6309999999999718},{"x":-0.9613270000000966,"y":-0.6309999999999718},{"x":-0.9613270000000966,"y":0.6310000000000855}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C96512.obj?uuid=a4c9f70a097a4133a99076e04275cb3c",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C96512.step?uuid=a4c9f70a097a4133a99076e04275cb3c",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0.00012700000002041634, y: 0, z: -0.14 },
      }}
      {...props}
    />
  )
}