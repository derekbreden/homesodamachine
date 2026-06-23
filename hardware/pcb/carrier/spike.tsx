/**
 * spike — one ESP32 GPIO -> gate resistor -> low-side N-MOSFET -> 12 V valve.
 * The unit cell of the carrier's valve and relay low-side drive. Two layers,
 * through-hole.
 */

export default () => (
  <board width="40mm" height="22mm">
    {/* +12 V input from the Mean Well PSU */}
    <pinheader
      name="J1"
      pinCount={2}
      pitch="2.54mm"
      gender="male"
      pinLabels={["V12", "GND"]}
      schX={-6}
      pcbX={-15}
      pcbY={0}
    />

    {/* ESP32 GPIO that commands the valve (3-pin stand-in for the dev board) */}
    <pinheader
      name="U1"
      pinCount={3}
      pitch="2.54mm"
      gender="female"
      pinLabels={["GPIO", "V3_3", "GND"]}
      schX={-3}
      schY={2}
      pcbX={-6}
      pcbY={6}
    />

    {/* Gate series resistor */}
    <resistor name="R1" resistance="100" footprint="0603" schX={0} pcbX={-1} pcbY={3} />

    {/* Low-side switch */}
    <mosfet
      name="Q1"
      channelType="n"
      mosfetMode="enhancement"
      footprint="sot23"
      schX={3}
      pcbX={4}
      pcbY={0}
    />

    {/* Valve output: high side at 12 V, low side switched by Q1 */}
    <pinheader
      name="J2"
      pinCount={2}
      pitch="2.54mm"
      gender="male"
      pinLabels={["VALVE", "RTN"]}
      schX={7}
      pcbX={15}
      pcbY={0}
    />

    {/* GPIO -> gate resistor -> MOSFET gate */}
    <trace from=".U1 > .GPIO" to=".R1 > .pin1" />
    <trace from=".R1 > .pin2" to=".Q1 > .gate" />

    {/* 12 V to the valve high side */}
    <trace from=".J1 > .V12" to=".J2 > .VALVE" />

    {/* valve return -> drain, source -> ground, logic ground tied in */}
    <trace from=".J2 > .RTN" to=".Q1 > .drain" />
    <trace from=".Q1 > .source" to=".J1 > .GND" />
    <trace from=".U1 > .GND" to=".J1 > .GND" />
  </board>
)
