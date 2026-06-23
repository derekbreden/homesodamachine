/**
 * esp32-mcp-mini — an ESP32 DevKitC-32E (socketed on two 1x19 rows) and an
 * MCP23017 (DIP-28) over I2C, with the MCP's GPA0-7 / GPB0-7 and four spare
 * ESP32 GPIO on edge headers. The ESP's 3V3 pin powers the MCP. Through-hole,
 * two layers.
 *
 * The ESP socket rows are 22.86 mm (0.9") apart and the pin map is the standard
 * DevKitC-32E 38-pin layout — both unconfirmed against the physical module.
 */

export default () => {
  // ESP32-DevKitC-32E 38-pin map (Espressif standard), row by row.
  const espA = ["3V3", "EN", "IO36", "IO39", "IO34", "IO35", "IO32", "IO33", "IO25",
    "IO26", "IO27", "IO14", "IO12", "GND", "IO13", "IO9", "IO10", "IO11", "V5"]
  const espB = ["GNDb", "IO23", "IO22", "IO1", "IO3", "IO21", "GNDc", "IO19", "IO18",
    "IO5", "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "IO8", "IO7", "IO6"]

  return (
    <board width="120mm" height="80mm">
      {/* ---- ESP32 DevKitC socket: two 1x19 female rows, 22.86 mm apart ---- */}
      <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female"
        footprint="pinrow19" pinLabels={espA}
        pcbX={-30} pcbY={11.43} schX={-10} schY={6} />
      <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female"
        footprint="pinrow19" pinLabels={espB}
        pcbX={-30} pcbY={-11.43} schX={-10} schY={-6} />

      {/* ---- MCP23017 in DIP-28 (real chip, real pinout) ---- */}
      <chip name="U2" footprint="dip28_w7.62mm" pcbX={28} pcbY={0} schX={6} schY={0}
        pinLabels={{
          pin1: "GPB0", pin2: "GPB1", pin3: "GPB2", pin4: "GPB3",
          pin5: "GPB4", pin6: "GPB5", pin7: "GPB6", pin8: "GPB7",
          pin9: "VDD", pin10: "VSS", pin11: "NC1", pin12: "SCL", pin13: "SDA", pin14: "NC2",
          pin15: "A0", pin16: "A1", pin17: "A2", pin18: "RST", pin19: "INTB", pin20: "INTA",
          pin21: "GPA0", pin22: "GPA1", pin23: "GPA2", pin24: "GPA3",
          pin25: "GPA4", pin26: "GPA5", pin27: "GPA6", pin28: "GPA7",
        }} />

      {/* ---- I2C pull-ups + MCP decoupling (THT) ---- */}
      <resistor name="R1" resistance="4.7k" footprint="axial" pcbX={2} pcbY={14} schX={0} schY={4} />
      <resistor name="R2" resistance="4.7k" footprint="axial" pcbX={2} pcbY={10} schX={1} schY={4} />
      <capacitor name="C1" capacitance="100nF" footprint="axial" pcbX={2} pcbY={-14} schX={2} schY={-3} />

      {/* ---- edge breakout headers ---- */}
      <pinheader name="JA" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={["GPA0", "GPA1", "GPA2", "GPA3", "GPA4", "GPA5", "GPA6", "GPA7"]}
        pcbX={46} pcbY={-24} schX={14} schY={-6} />
      <pinheader name="JB" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={["GPB0", "GPB1", "GPB2", "GPB3", "GPB4", "GPB5", "GPB6", "GPB7"]}
        pcbX={46} pcbY={24} schX={14} schY={6} />
      <pinheader name="JE" pinCount={6} pitch="2.54mm" gender="male" footprint="pinrow6"
        pinLabels={["IO32", "IO33", "IO25", "IO26", "3V3", "GND"]}
        pcbX={-30} pcbY={-32} schX={-10} schY={-14} />

      {/* ===================== NETS ===================== */}
      {/* power: the ESP's 3V3 pin feeds the MCP + pull-ups + decoupling + edge 3V3 */}
      <netlabel net="V3_3" schX={-2} schY={2} connectsTo={[
        ".U1A > .3V3", ".U2 > .VDD", ".U2 > .RST",
        ".R1 > .pin2", ".R2 > .pin2", ".C1 > .pin1", ".JE > .3V3",
      ]} />
      <netlabel net="GND" schX={-2} schY={-2} connectsTo={[
        ".U1B > .GNDb", ".U2 > .VSS", ".U2 > .A0", ".U2 > .A1", ".U2 > .A2",
        ".C1 > .pin2", ".JE > .GND",
      ]} />
      {/* I2C: ESP IO21/IO22 to the MCP, with the pull-ups */}
      <netlabel net="SDA" schX={0} schY={3} connectsTo={[".U1B > .IO21", ".U2 > .SDA", ".R1 > .pin1"]} />
      <netlabel net="SCL" schX={1} schY={3} connectsTo={[".U1B > .IO22", ".U2 > .SCL", ".R2 > .pin1"]} />

      {/* MCP GPA0-7 -> JA, GPB0-7 -> JB */}
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <trace key={`ga-${i}`} from={`.U2 > .GPA${i}`} to={`.JA > .GPA${i}`} />
      ))}
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <trace key={`gb-${i}`} from={`.U2 > .GPB${i}`} to={`.JB > .GPB${i}`} />
      ))}
      {/* a few spare ESP32 GPIO -> JE */}
      <trace from=".U1A > .IO32" to=".JE > .IO32" />
      <trace from=".U1A > .IO33" to=".JE > .IO33" />
      <trace from=".U1A > .IO25" to=".JE > .IO25" />
      <trace from=".U1A > .IO26" to=".JE > .IO26" />
    </board>
  )
}
