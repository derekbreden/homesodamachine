import type { ChipProps } from "@tscircuit/props"

// AO3407A — P-channel MOSFET, SOT-23 (C347478). VDS -30 V, VGS ±20 V, RDS(on) ~55 mΩ@-10 V,
// ID -4.1 A. The reverse-polarity high-side pass FET at the J10 12 V inlet: DRAIN to the incoming
// V12IN (screw terminal), SOURCE to the board-side V12 island, GATE pulled to GND through R23. The
// AOS "A" grade of the AO3407: same SOT-23 die/pinout/ratings, but it ships an EasyEDA 3D model
// (obj + step) and carries healthy JLCPCB stock — the plain AO3407 (C181093) has neither.
//
// Pinout is the standard SOT-23 P-FET map (AOS): pin1 = Gate, pin2 = Source, pin3 = Drain — the
// same three SOT-23 lands JLCPCB numbers pin1/2/3 for every SOT-23 (the S8050 NPN uses the identical
// pad geometry), so the CPL pad-to-pin numbering matches JLCPCB's library; only the pin FUNCTION
// differs from a transistor's B/E/C. Pads are the imported SOT-23 land (pin1/pin2 the paired side,
// pin3 the single drain tab); the {NAME} silk is stripped (the centred() Pfet wrapper draws the
// upright ref-des), and the courtyard is a tight IPC keep-out so the narrow-profile seating
// (rot 90/270) fits the C5↔J10 slot. cadModel is `tsci import`'s for C347478.
const pinLabels = {
  pin1: ["G"],
  pin2: ["S"],
  pin3: ["D"],
} as const

export const AO3407A = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{ jlcpcb: ["C347478"] }}
      manufacturerPartNumber="AO3407A"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="1.149985mm" pcbY="-0.94996mm" width="0.999998mm" height="0.7999984mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="1.149985mm" pcbY="0.94996mm" width="0.999998mm" height="0.7999984mm" shape="rect" />
        <smtpad portHints={["pin3"]} pcbX="-1.149985mm" pcbY="0mm" width="0.999998mm" height="0.7999984mm" shape="rect" />
        <courtyardoutline outline={[{"x":-1.75,"y":1.4},{"x":1.75,"y":1.4},{"x":1.75,"y":-1.4},{"x":-1.75,"y":-1.4},{"x":-1.75,"y":1.4}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C347478.obj?uuid=d777607a152f4f3aac9bb0d0c14ed6fd",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C347478.step?uuid=d777607a152f4f3aac9bb0d0c14ed6fd",
        pcbRotationOffset: 180,
        modelOriginPosition: { x: 0.00003809999999759839, y: -0.00003810000001180924, z: 0.050795 },
      }}
      {...props}
    />
  )
}
