/** throwaway syntax probe — verify patterns before authoring the full board */
export default () => (
  <board width="70mm" height="40mm">
    {/* a module standin as a 2-row THT chip with function pin labels */}
    <chip
      name="U1"
      footprint="dip38"
      pcbX={-18}
      pinLabels={{ pin1: "EN", pin19: "GND1", pin20: "VIN", pin38: "IO23" }}
    />
    <chip
      name="U3"
      footprint="dip28"
      pcbX={12}
      pinLabels={{ pin1: "VCC", pin2: "GND2", pin28: "GPA0" }}
    />
    {/* multi-pin power net via netlabel + connectsTo */}
    <netlabel
      net="GND"
      schX={0}
      schY={-6}
      connectsTo={[".U1 > .GND1", ".U3 > .GND2"]}
    />
    {/* signal trace by function label */}
    <trace from=".U1 > .IO23" to=".U3 > .GPA0" />
    {/* trace straight to a named net */}
    <trace from=".U1 > .VIN" to="net.V12" />
  </board>
)
