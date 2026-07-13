import type { DiodeProps } from "@tscircuit/props"

// SMAJ15A — 400 W unidirectional TVS, SMA / DO-214AC (C571368). 15 V reverse stand-off (above the
// 12 V rail, no leakage in normal operation), 24.4 V clamp at 16.4 A Ipp — under C3's 25 V rating.
// Sits across the V12 island → GND right at the J10 inlet, clamping the surge the BOARD sees.
//
// pin1 = CATHODE (the banded end, JLCPCB/library convention) → V12 island; pin2 = ANODE → GND. The
// standard SMA land (KiCad Diode_SMD:D_SMA: 2.5×1.8 mm pads at ±2.0 mm, 7.0×3.5 mm courtyard) with a
// cathode-band silk so the polarity survives assembly, exactly like the 1N4148W. No cadModel — 3D
// deferred (best-effort GLB); BOM/CPL ride supplierPartNumbers, the orientation audit skips it.
export const SMAJ15A = (props: DiodeProps) => {
  const { name = "D", ...restProps } = props
  return (
    <diode
      name={name}
      supplierPartNumbers={{ jlcpcb: ["C571368"] }}
      manufacturerPartNumber="SMAJ15A"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-2.0mm" pcbY="0mm" width="2.5mm" height="1.8mm" shape="rect" />
        <smtpad portHints={["pin2"]} pcbX="2.0mm" pcbY="0mm" width="2.5mm" height="1.8mm" shape="rect" />
        <silkscreenpath route={[{"x":-3.15,"y":-1.05},{"x":-3.15,"y":1.05}]} />
        <courtyardoutline outline={[{"x":-3.5,"y":1.75},{"x":3.5,"y":1.75},{"x":3.5,"y":-1.75},{"x":-3.5,"y":-1.75},{"x":-3.5,"y":1.75}]} />
      </footprint>}
      {...restProps}
    />
  )
}
