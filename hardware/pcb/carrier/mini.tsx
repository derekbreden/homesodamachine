/**
 * esp32-mcp-mini — an ESP32 DevKitC-32E (socketed on two 1x19 rows, 25.4 mm
 * apart) and two MCP23017 (DIP-28) on a shared I2C bus, U2 at 0x20 and U3 at
 * 0x21. Each MCP's GPA0-7 / GPB0-7 lands on its own edge header; four spare
 * ESP32 GPIO land on JE. The ESP's 3V3 pin powers both MCPs. Through-hole,
 * two layers.
 *
 * ESP socket geometry: 2x19 @ 2.54 mm pitch, rows 25.4 mm (1.0") apart, pin map
 * the standard DevKitC-32E 38-pin layout.
 */

export default () => {
  // ESP32-DevKitC-32E 38-pin map (Espressif standard), row by row.
  const espA = ["3V3", "EN", "IO36", "IO39", "IO34", "IO35", "IO32", "IO33", "IO25",
    "IO26", "IO27", "IO14", "IO12", "GND", "IO13", "IO9", "IO10", "IO11", "V5"]
  const espB = ["GNDb", "IO23", "IO22", "IO1", "IO3", "IO21", "GNDc", "IO19", "IO18",
    "IO5", "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "IO8", "IO7", "IO6"]

  const mcpPins = {
    pin1: "GPB0", pin2: "GPB1", pin3: "GPB2", pin4: "GPB3",
    pin5: "GPB4", pin6: "GPB5", pin7: "GPB6", pin8: "GPB7",
    pin9: "VDD", pin10: "VSS", pin11: "NC1", pin12: "SCL", pin13: "SDA", pin14: "NC2",
    pin15: "A0", pin16: "A1", pin17: "A2", pin18: "RST", pin19: "INTB", pin20: "INTA",
    pin21: "GPA0", pin22: "GPA1", pin23: "GPA2", pin24: "GPA3",
    pin25: "GPA4", pin26: "GPA5", pin27: "GPA6", pin28: "GPA7",
  }
  const bank = (n: number) => [0, 1, 2, 3, 4, 5, 6, 7].map((i) => `${n === 0 ? "GPA" : "GPB"}${i}`)

  return (
    <board width="150mm" height="115mm">
      {/* ---- ESP32 DevKitC socket: two 1x19 female rows, 25.4 mm apart ---- */}
      <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female"
        footprint="pinrow19" pinLabels={espA}
        pcbX={-45} pcbY={12.7} schX={-12} schY={6} />
      <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female"
        footprint="pinrow19" pinLabels={espB}
        pcbX={-45} pcbY={-12.7} schX={-12} schY={-6} />

      {/* ---- MCP23017 #1 @0x20 (A0/A1/A2 = GND) ---- */}
      <chip name="U2" footprint="dip28_w7.62mm" pcbX={5} pcbY={26} schX={4} schY={7} pinLabels={mcpPins} />
      {/* ---- MCP23017 #2 @0x21 (A0 = 3V3, A1/A2 = GND) ---- */}
      <chip name="U3" footprint="dip28_w7.62mm" pcbX={5} pcbY={-26} schX={4} schY={-7} pinLabels={mcpPins} />

      {/* ---- I2C pull-ups + per-MCP decoupling (THT) ---- */}
      <resistor name="R1" resistance="4.7k" footprint="axial" pcbX={-12} pcbY={20} schX={0} schY={3} />
      <resistor name="R2" resistance="4.7k" footprint="axial" pcbX={-12} pcbY={16} schX={1} schY={3} />
      <capacitor name="C1" capacitance="100nF" footprint="axial" pcbX={-12} pcbY={32} schX={-3} schY={9} />
      <capacitor name="C2" capacitance="100nF" footprint="axial" pcbX={-12} pcbY={-32} schX={-3} schY={-9} />

      {/* ---- edge breakout headers: one GPA + one GPB per MCP, plus ESP spares ---- */}
      <pinheader name="JA" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={bank(0)} pcbX={42} pcbY={34} schX={14} schY={9} />
      <pinheader name="JB" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={bank(1)} pcbX={42} pcbY={18} schX={14} schY={5} />
      <pinheader name="JC" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={bank(0)} pcbX={42} pcbY={-18} schX={14} schY={-5} />
      <pinheader name="JD" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={bank(1)} pcbX={42} pcbY={-34} schX={14} schY={-9} />
      <pinheader name="JE" pinCount={6} pitch="2.54mm" gender="male" footprint="pinrow6"
        pinLabels={["IO32", "IO33", "IO25", "IO26", "3V3", "GND"]}
        pcbX={-45} pcbY={-42} schX={-12} schY={-13} />

      {/* ===================== NETS ===================== */}
      {/* the ESP's 3V3 pin feeds both MCPs (VDD + RST), the pull-ups, the decaps,
          and the edge 3V3; U3 A0 = 3V3 sets its 0x21 address */}
      <netlabel net="V3_3" schX={-3} schY={1} connectsTo={[
        ".U1A > .3V3",
        ".U2 > .VDD", ".U2 > .RST",
        ".U3 > .VDD", ".U3 > .RST", ".U3 > .A0",
        ".R1 > .pin2", ".R2 > .pin2", ".C1 > .pin1", ".C2 > .pin1", ".JE > .3V3",
      ]} />
      <netlabel net="GND" schX={-3} schY={-1} connectsTo={[
        ".U1B > .GNDb",
        ".U2 > .VSS", ".U2 > .A0", ".U2 > .A1", ".U2 > .A2",
        ".U3 > .VSS", ".U3 > .A1", ".U3 > .A2",
        ".C1 > .pin2", ".C2 > .pin2", ".JE > .GND",
      ]} />
      {/* shared I2C bus: ESP IO21/IO22 + both MCPs + pull-ups */}
      <netlabel net="SDA" schX={1} schY={2} connectsTo={[
        ".U1B > .IO21", ".U2 > .SDA", ".U3 > .SDA", ".R1 > .pin1",
      ]} />
      <netlabel net="SCL" schX={2} schY={2} connectsTo={[
        ".U1B > .IO22", ".U2 > .SCL", ".U3 > .SCL", ".R2 > .pin1",
      ]} />

      {/* MCP #1 GPA0-7 -> JA, GPB0-7 -> JB */}
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <trace key={`u2a-${i}`} from={`.U2 > .GPA${i}`} to={`.JA > .GPA${i}`} />
      ))}
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <trace key={`u2b-${i}`} from={`.U2 > .GPB${i}`} to={`.JB > .GPB${i}`} />
      ))}
      {/* MCP #2 GPA0-7 -> JC, GPB0-7 -> JD */}
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <trace key={`u3a-${i}`} from={`.U3 > .GPA${i}`} to={`.JC > .GPA${i}`} />
      ))}
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <trace key={`u3b-${i}`} from={`.U3 > .GPB${i}`} to={`.JD > .GPB${i}`} />
      ))}
      {/* four spare ESP32 GPIO -> JE */}
      <trace from=".U1A > .IO32" to=".JE > .IO32" />
      <trace from=".U1A > .IO33" to=".JE > .IO33" />
      <trace from=".U1A > .IO25" to=".JE > .IO25" />
      <trace from=".U1A > .IO26" to=".JE > .IO26" />
    </board>
  )
}
