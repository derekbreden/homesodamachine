import type { DiodeProps } from "@tscircuit/props"

// SMAJ15A — 400 W unidirectional TVS, SMA / DO-214AC (C571368). 15 V reverse stand-off (above the
// 12 V rail, no leakage in normal operation), 24.4 V clamp at 16.4 A Ipp — under C3's 25 V rating.
// Sits across the V12 island → GND at the J10 inlet, clamping the surge the BOARD sees.
//
// pin1 = CATHODE (the banded end, JLCPCB/library convention) → V12 island; pin2 = ANODE → GND. The
// genuine C571368 SMA land (pads at ±2.329942 mm), with its cathode-band glyph silk kept so polarity
// survives assembly. Only the footprint {NAME} silk is stripped — the wrapper draws the upright ref-des.
export const SMAJ15A = (props: DiodeProps) => {
  const { name = "D", ...restProps } = props
  return (
    <diode
      name={name}
      supplierPartNumbers={{ jlcpcb: ["C571368"] }}
      manufacturerPartNumber="SMAJ15A"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="2.329942mm" pcbY="0mm" width="1.8999962mm" height="1.8999962mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-2.329942mm" pcbY="0mm" width="1.8999962mm" height="1.8999962mm" shape="rect" />
<silkscreenpath route={[{"x":-2.3000207999999702,"y":1.4999969999998939},{"x":2.3000207999998565,"y":1.4999969999998939}]} />
<silkscreenpath route={[{"x":-0.2540000000001328,"y":0},{"x":0.5079999999999245,"y":-0.7620000000000573},{"x":0.5079999999999245,"y":0.7619999999999436},{"x":-0.2540000000001328,"y":0}]} />
<silkscreenpath route={[{"x":-0.2540000000001328,"y":-0.7620000000000573},{"x":-0.2540000000001328,"y":0.7619999999999436}]} />
<silkscreenpath route={[{"x":1.2699999999998681,"y":0},{"x":-1.0160000000000764,"y":0}]} />
<silkscreenpath route={[{"x":2.3000207999998565,"y":-1.4999970000000076},{"x":-2.3000207999999702,"y":-1.4999970000000076}]} />
<silkscreenpath route={[{"x":-2.3000207999999702,"y":1.4999969999998939},{"x":-2.3000207999999702,"y":1.1811508000000686}]} />
<silkscreenpath route={[{"x":-2.3000207999999702,"y":-1.1811507999999549},{"x":-2.3000207999999702,"y":-1.4999970000000076}]} />
<silkscreenpath route={[{"x":2.3000207999998565,"y":1.4999969999998939},{"x":2.3000207999998565,"y":1.1811508000000686}]} />
<silkscreenpath route={[{"x":2.3000207999998565,"y":-1.1811507999999549},{"x":2.3000207999998565,"y":-1.4999970000000076}]} />
<courtyardoutline outline={[{"x":-3.5520000000001346,"y":1.7486000000000104},{"x":3.552000000000021,"y":1.7486000000000104},{"x":3.552000000000021,"y":-1.7485999999998967},{"x":-3.5520000000001346,"y":-1.7485999999998967},{"x":-3.5520000000001346,"y":1.7486000000000104}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C571368.obj?uuid=4689b37d740647079f86f5f772d33885",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C571368.step?uuid=4689b37d740647079f86f5f772d33885",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0.000012700000070253736, y: -0.000012700000070253736, z: -0.01 },
      }}
      {...restProps}
    />
  )
}
