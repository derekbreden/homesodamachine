/**
 * esp32-mcp-mini — an ESP32 DevKitC-32E socket; two MCP23017 (DIP-28) on a
 * shared I2C bus (U2 at 0x20, U3 at 0x21); U2's GPA0-7 drive a ULN2803 (U4)
 * that sinks eight 12 V solenoid outputs on J_VA; U2's GPB0-7 and both of U3's
 * banks land on edge headers; four spare ESP32 GPIO on JE. J12 brings 12 V in
 * for the ULN COM and the solenoid high side; the ESP's 3V3 pin powers the
 * MCPs. Through-hole, two layers.
 *
 * ESP socket: 2x19 @ 2.54 mm pitch, rows 25.4 mm (1.0") apart, pin map the
 * standard DevKitC-32E 38-pin layout.
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
  // ULN2803A: pin1-8 IN, pin9 GND, pin10 COM, pin11-18 OUT8..OUT1.
  const ulnPins = {
    pin1: "IN1", pin2: "IN2", pin3: "IN3", pin4: "IN4",
    pin5: "IN5", pin6: "IN6", pin7: "IN7", pin8: "IN8",
    pin9: "GND", pin10: "COM",
    pin11: "OUT8", pin12: "OUT7", pin13: "OUT6", pin14: "OUT5",
    pin15: "OUT4", pin16: "OUT3", pin17: "OUT2", pin18: "OUT1",
  }
  const i8 = [0, 1, 2, 3, 4, 5, 6, 7]
  const valves = ["VA", "VB", "VC", "VD", "VE", "VF", "VG", "VH"]
  const gpb = i8.map((i) => `GPB${i}`)
  const gpa = i8.map((i) => `GPA${i}`)

  return (
    <board width="175mm" height="125mm">
      {/* ---- ESP32 DevKitC socket: two 1x19 female rows, 25.4 mm apart ---- */}
      <pinheader name="U1A" pinCount={19} pitch="2.54mm" gender="female"
        footprint="pinrow19" pinLabels={espA}
        pcbX={-55} pcbY={13} schX={-14} schY={6} />
      <pinheader name="U1B" pinCount={19} pitch="2.54mm" gender="female"
        footprint="pinrow19" pinLabels={espB}
        pcbX={-55} pcbY={-13} schX={-14} schY={-6} />

      {/* ---- MCP23017 #1 @0x20 (A0/A1/A2 = GND) ---- */}
      <chip name="U2" footprint="dip28_w7.62mm" pcbX={2} pcbY={30} schX={3} schY={7} pinLabels={mcpPins} />
      {/* ---- MCP23017 #2 @0x21 (A0 = 3V3, A1/A2 = GND) ---- */}
      <chip name="U3" footprint="dip28_w7.62mm" pcbX={2} pcbY={-28} schX={3} schY={-7} pinLabels={mcpPins} />
      {/* ---- ULN2803A: sinks 8 solenoids, driven by U2 GPA0-7, COM at 12 V ---- */}
      <chip name="U4" footprint="dip18" pcbX={28} pcbY={32} schX={8} schY={9} pinLabels={ulnPins} />

      {/* ---- I2C pull-ups, MCP decoupling, 12 V bulk (THT) ---- */}
      <resistor name="R1" resistance="4.7k" footprint="axial" pcbX={-20} pcbY={24} schX={0} schY={3} />
      <resistor name="R2" resistance="4.7k" footprint="axial" pcbX={-20} pcbY={20} schX={1} schY={3} />
      <capacitor name="C1" capacitance="100nF" footprint="axial" pcbX={-20} pcbY={34} schX={-3} schY={10} />
      <capacitor name="C2" capacitance="100nF" footprint="axial" pcbX={-20} pcbY={-34} schX={-3} schY={-10} />
      <capacitor name="C3" capacitance="100uF" footprint="radial" polarized pcbX={-40} pcbY={46} schX={-7} schY={13} />

      {/* ---- connectors ---- */}
      <pinheader name="J12" pinCount={2} pitch="2.54mm" gender="male" footprint="pinrow2"
        pinLabels={["V12", "GND"]} pcbX={-58} pcbY={46} schX={-14} schY={13} />
      {/* solenoid outputs: 8 ULN sinks + a 12 V common (high side) */}
      <pinheader name="J_VA" pinCount={9} pitch="2.54mm" gender="male" footprint="pinrow9"
        pinLabels={[...valves, "COM"]} pcbX={56} pcbY={40} schX={16} schY={9} />
      {/* U2 GPB, and both of U3's banks, straight to edge headers */}
      <pinheader name="JB" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={gpb} pcbX={56} pcbY={14} schX={16} schY={4} />
      <pinheader name="JC" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={gpa} pcbX={56} pcbY={-20} schX={16} schY={-5} />
      <pinheader name="JD" pinCount={8} pitch="2.54mm" gender="male" footprint="pinrow8"
        pinLabels={gpb} pcbX={56} pcbY={-40} schX={16} schY={-9} />
      <pinheader name="JE" pinCount={6} pitch="2.54mm" gender="male" footprint="pinrow6"
        pinLabels={["IO32", "IO33", "IO25", "IO26", "3V3", "GND"]}
        pcbX={-58} pcbY={-44} schX={-14} schY={-13} />

      {/* ===================== NETS ===================== */}
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
        ".U4 > .GND", ".C1 > .pin2", ".C2 > .pin2", ".C3 > .pin2",
        ".J12 > .GND", ".JE > .GND",
      ]} />
      {/* 12 V: input, the ULN clamp common, the solenoid high side, bulk cap */}
      <netlabel net="V12" schX={6} schY={13} connectsTo={[
        ".J12 > .V12", ".U4 > .COM", ".J_VA > .COM", ".C3 > .pin1",
      ]} />
      {/* shared I2C bus */}
      <netlabel net="SDA" schX={1} schY={2} connectsTo={[
        ".U1B > .IO21", ".U2 > .SDA", ".U3 > .SDA", ".R1 > .pin1",
      ]} />
      <netlabel net="SCL" schX={2} schY={2} connectsTo={[
        ".U1B > .IO22", ".U2 > .SCL", ".U3 > .SCL", ".R2 > .pin1",
      ]} />

      {/* U2 GPA0-7 -> ULN IN1-8 -> J_VA (the solenoid drive chain) */}
      {i8.map((i) => (
        <trace key={`u2a-in-${i}`} from={`.U2 > .GPA${i}`} to={`.U4 > .IN${i + 1}`} />
      ))}
      {i8.map((i) => (
        <trace key={`uln-out-${i}`} from={`.U4 > .OUT${i + 1}`} to={`.J_VA > .${valves[i]}`} />
      ))}
      {/* U2 GPB0-7 -> JB */}
      {i8.map((i) => (
        <trace key={`u2b-${i}`} from={`.U2 > .GPB${i}`} to={`.JB > .GPB${i}`} />
      ))}
      {/* U3 GPA0-7 -> JC, GPB0-7 -> JD */}
      {i8.map((i) => (
        <trace key={`u3a-${i}`} from={`.U3 > .GPA${i}`} to={`.JC > .GPA${i}`} />
      ))}
      {i8.map((i) => (
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
