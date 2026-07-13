import type { ChipProps } from "@tscircuit/props"

// AO3407 — P-channel MOSFET, SOT-23 (C181093). VDS -30 V, VGS ±20 V, RDS(on) ~60 mΩ@-10 V,
// ID -4.1 A. The reverse-polarity high-side pass FET at the J10 12 V inlet: DRAIN to the incoming
// V12IN (screw terminal), SOURCE to the board-side V12 island, GATE pulled to GND through R23.
//
// Pinout is the standard SOT-23 P-FET map (AOS): pin1 = Gate, pin2 = Source, pin3 = Drain — the
// same three SOT-23 lands JLCPCB numbers pin1/2/3 for every SOT-23 (the S8050 NPN uses the identical
// pad geometry), so the CPL pad-to-pin numbering matches JLCPCB's library; only the pin FUNCTION
// differs from a transistor's B/E/C. Pads are the proven SOT-23 land (pin1/pin2 the paired side,
// pin3 the single drain tab); the courtyard is a tight IPC keep-out so the narrow-profile seating
// (rot 90/270) fits the C5↔J10 slot. No cadModel — the 3D is deferred (best-effort GLB); the
// orientation audit skips model-less parts and the BOM/CPL ride supplierPartNumbers.
const pinLabels = {
  pin1: ["G"],
  pin2: ["S"],
  pin3: ["D"],
} as const

export const AO3407 = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{ jlcpcb: ["C181093"] }}
      manufacturerPartNumber="AO3407"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="1.101344mm" pcbY="-0.94996mm" width="1.0374884mm" height="0.532003mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="1.101344mm" pcbY="0.94996mm" width="1.0374884mm" height="0.532003mm" shape="rect" />
        <smtpad portHints={["pin3"]} pcbX="-1.101344mm" pcbY="0mm" width="1.0374884mm" height="0.532003mm" shape="rect" />
        <courtyardoutline outline={[{"x":-1.75,"y":1.4},{"x":1.75,"y":1.4},{"x":1.75,"y":-1.4},{"x":-1.75,"y":-1.4},{"x":-1.75,"y":1.4}]} />
      </footprint>}
      {...props}
    />
  )
}
