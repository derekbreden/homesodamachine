import type { DiodeProps } from "@tscircuit/props"

// BZT52C15 — 15 V, 0.5 W Zener, SOD-123 (C173427, MDD). Clamps Vgs on the reverse-polarity pass FET
// (AO3407A): CATHODE → SOURCE (V12 island), ANODE → GATE (net.VGATE). In normal polarity Vgs ≈ -12 V
// (below the 15 V knee, no conduction); a transient that would drive Vgs past -15 V is clamped short
// of the FET's ±20 V gate-oxide rating.
//
// pin1 = CATHODE (banded end, JLCPCB/library convention), pin2 = ANODE — the same SOD-123 land the
// 1N4148W uses (pads at ±1.735 mm), cathode-band silk kept so polarity survives assembly. cadModel
// (obj + step) is `tsci import`'s for C173427; BOM/CPL ride supplierPartNumbers.
export const BZT52C15 = (props: DiodeProps) => {
  const { name = "D", ...restProps } = props
  return (
    <diode
      name={name}
      supplierPartNumbers={{ jlcpcb: ["C173427"] }}
      manufacturerPartNumber="BZT52C15"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-1.734947mm" pcbY="0mm" width="1.0999978mm" height="0.999998mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="1.734947mm" pcbY="0mm" width="1.0999978mm" height="0.999998mm" shape="rect" />
        <silkscreenpath route={[{"x":-0.9167368,"y":0.8761222},{"x":-0.9167368,"y":-0.8763254}]} />
        <courtyardoutline outline={[{"x":-2.3,"y":0.85},{"x":2.3,"y":0.85},{"x":2.3,"y":-0.85},{"x":-2.3,"y":-0.85},{"x":-2.3,"y":0.85}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C173427.obj?uuid=4d7f235d12124480ae44c354a7fd93dd",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C173427.step?uuid=4d7f235d12124480ae44c354a7fd93dd",
        pcbRotationOffset: 180,
        modelOriginPosition: { x: 0.000012699999956566899, y: 0, z: 0.025856 },
      }}
      {...restProps}
    />
  )
}
