/**
 * Home Soda Machine — controller carrier board.
 *
 * A through-hole carrier the off-the-shelf modules plug into on 2.54 mm
 * headers: it carries power, routes the signals between them, and lands every
 * field harness on a labeled connector. The connection contract is
 * ../netlist.md.
 *
 * Module sockets are placeholder dip{n} footprints; the outline is provisional.
 * The pumps drive through ENA/ENB (the L298N is 3-wire); the backflow moisture
 * sensor is on GPIO 13.
 */

export default () => {
  // ---- repetitive fan-outs, as data ----
  const valveAH = ["A", "B", "C", "D", "E", "F", "G", "H"] // U3 GPA0..7 -> U5 IN1..8 -> J8
  const valveIKB = ["I", "J", "KA", "KB"] //                  U3 GPB0..3 -> U6 IN1..4 -> J9

  // ---- floor plan ----
  // PCB positions in mm; rows top->bottom: MCU/logic, expanders, drivers,
  // passives, then two connector banks along the bottom edge.
  const PCB: Record<string, [number, number]> = {
    U1: [-148, 60], U9: [-30, 82], U10: [10, 82], U12: [48, 82],
    U3: [-112, 42], U4: [-52, 42], U5: [24, 42], U6: [76, 42],
    U7U8: [-112, 2], K1: [-42, 4], K2: [2, 4],
    R1: [-138, -30], R2: [-120, -30], R3: [-102, -30], R4: [-84, -30],
    R5: [-66, -30], RFLOW: [-48, -30], C1: [-18, -30],
    J2: [-150, -62], J3: [-116, -62], J4: [-84, -62], J5: [-46, -62],
    J6: [-14, -62], J7: [12, -62], J8: [44, -62],
    J9: [-150, -96], J10: [-110, -96], J11: [-82, -96], J12: [-56, -96],
    J13: [-34, -96], J14: [-12, -96], J15: [10, -96], J16: [30, -96], J17: [56, -96],
  }
  // schematic positions (grid units), spread by function
  const SCH: Record<string, [number, number]> = {
    U1: [-6, 0], U3: [4, 9], U4: [4, -9], U5: [14, 9], U6: [14, -9],
    U7U8: [-6, -14], U9: [-18, 9], U10: [-18, 15], U12: [-18, -10],
    K1: [16, 14], K2: [16, -14],
    R1: [-1, 8], R2: [1, 8], R3: [-9, 4], R4: [-9, 6], R5: [-7, 6], RFLOW: [-9, 2], C1: [-20, 12],
    J2: [-22, 15], J3: [24, 16], J4: [26, 14], J5: [24, -16], J6: [-14, -18], J7: [-10, -18],
    J8: [24, 9], J9: [24, -9], J10: [10, 18], J11: [6, 18], J12: [-24, 9], J13: [-24, 6],
    J14: [-24, 3], J15: [-24, -6], J16: [-24, -12], J17: [-24, -15],
  }
  const px = (r: string) => PCB[r][0]
  const py = (r: string) => PCB[r][1]
  const sx = (r: string) => SCH[r][0]
  const sy = (r: string) => SCH[r][1]

  // field connectors: [ref, [pin labels]]
  const connectors: [string, string[]][] = [
    ["J2", ["V12", "GND"]], //                12 V in
    ["J3", ["ACH", "ACN"]], //                AC in (fenced corner)
    ["J4", ["ACH_SW", "ACN", "EARTH"]], //    compressor out
    ["J5", ["PUMP12", "PUMPRET"]], //         diaphragm pump
    ["J6", ["A1", "A2"]], //                  peristaltic pump A
    ["J7", ["B1", "B2"]], //                  peristaltic pump B
    ["J8", ["VA", "VB", "VC", "VD", "VE", "VF", "VG", "VH", "COM"]], // solenoids A-H
    ["J9", ["VI", "VJ", "VKA", "VKB", "FAN", "COM", "COM2"]], //       solenoids I-KB + fan
    ["J10", ["RA1", "RA2", "RA3", "RA4", "GND"]], //  reservoir A reeds
    ["J11", ["RB1", "RB2", "RB3", "RB4", "GND"]], //  reservoir B reeds
    ["J12", ["RLOW", "RHIGH", "GND"]], //            carbonator reeds
    ["J13", ["OW", "V3_3", "GND"]], //               DS18B20 1-wire
    ["J14", ["FLOW", "V5", "GND"]], //               flow meter
    ["J15", ["MOIST", "GND"]], //                    backflow moisture
    ["J16", ["A", "B", "V12", "GND"]], //            RS485 -> 4.3B config display
    ["J17", ["TX", "RX", "V5", "GND"]], //           UART -> faucet display
  ]

  return (
    <board width="340mm" height="220mm" routingDisabled>
      {/* ======================= MODULE SOCKETS ======================= */}

      {/* U1 — ESP32 DevKitC-32E (USB, CH340, 3V3 reg and BOOT/EN live on the module) */}
      <chip
        name="U1"
        footprint="dip38"
        pcbX={px("U1")} pcbY={py("U1")} schX={sx("U1")} schY={sy("U1")}
        pinLabels={{
          pin1: "V5", pin2: "V3_3", pin3: "GND", pin4: "GND2",
          pin5: "IO21", pin6: "IO22", pin7: "IO16", pin8: "IO17", pin9: "IO27",
          pin10: "IO23", pin11: "IO14", pin12: "IO4", pin13: "IO25", pin14: "IO26",
          pin15: "IO33", pin16: "IO18", pin17: "IO5", pin18: "IO19", pin19: "IO15",
          pin20: "IO34", pin21: "IO32", pin22: "IO35", pin23: "IO13",
        }}
      />

      {/* U3 — MCP23017 @0x20: valve bank GPA0-7 + GPB0-3, reservoir-A reeds GPB4-7 */}
      <chip
        name="U3"
        footprint="dip28"
        pcbX={px("U3")} pcbY={py("U3")} schX={sx("U3")} schY={sy("U3")}
        pinLabels={{
          pin1: "VCC", pin2: "GND", pin3: "SDA", pin4: "SCL", pin5: "RST",
          pin6: "A0", pin7: "A1", pin8: "A2",
          pin9: "GPA0", pin10: "GPA1", pin11: "GPA2", pin12: "GPA3",
          pin13: "GPA4", pin14: "GPA5", pin15: "GPA6", pin16: "GPA7",
          pin17: "GPB0", pin18: "GPB1", pin19: "GPB2", pin20: "GPB3",
          pin21: "GPB4", pin22: "GPB5", pin23: "GPB6", pin24: "GPB7",
        }}
      />

      {/* U4 — MCP23017 @0x21: reservoir-B reeds GPA0-3, condenser fan GPA4 */}
      <chip
        name="U4"
        footprint="dip28"
        pcbX={px("U4")} pcbY={py("U4")} schX={sx("U4")} schY={sy("U4")}
        pinLabels={{
          pin1: "VCC", pin2: "GND", pin3: "SDA", pin4: "SCL", pin5: "RST",
          pin6: "A0", pin7: "A1", pin8: "A2",
          pin9: "GPA0", pin10: "GPA1", pin11: "GPA2", pin12: "GPA3",
          pin13: "GPA4", pin14: "GPA5", pin15: "GPA6", pin16: "GPA7",
          pin17: "GPB0", pin18: "GPB1", pin19: "GPB2", pin20: "GPB3",
          pin21: "GPB4", pin22: "GPB5", pin23: "GPB6", pin24: "GPB7",
        }}
      />

      {/* U5 — ULN2803A #1: solenoids A-H (real pinout: 1-8 IN, 9 GND, 10 COM, 11-18 OUT8..1) */}
      <chip
        name="U5"
        footprint="dip18"
        pcbX={px("U5")} pcbY={py("U5")} schX={sx("U5")} schY={sy("U5")}
        pinLabels={{
          pin1: "IN1", pin2: "IN2", pin3: "IN3", pin4: "IN4",
          pin5: "IN5", pin6: "IN6", pin7: "IN7", pin8: "IN8",
          pin9: "GND", pin10: "COM",
          pin11: "OUT8", pin12: "OUT7", pin13: "OUT6", pin14: "OUT5",
          pin15: "OUT4", pin16: "OUT3", pin17: "OUT2", pin18: "OUT1",
        }}
      />

      {/* U6 — ULN2803A #2: solenoids I-KB (ch1-4) + condenser fan (ch5) */}
      <chip
        name="U6"
        footprint="dip18"
        pcbX={px("U6")} pcbY={py("U6")} schX={sx("U6")} schY={sy("U6")}
        pinLabels={{
          pin1: "IN1", pin2: "IN2", pin3: "IN3", pin4: "IN4",
          pin5: "IN5", pin6: "IN6", pin7: "IN7", pin8: "IN8",
          pin9: "GND", pin10: "COM",
          pin11: "OUT8", pin12: "OUT7", pin13: "OUT6", pin14: "OUT5",
          pin15: "OUT4", pin16: "OUT3", pin17: "OUT2", pin18: "OUT1",
        }}
      />

      {/* U7U8 — L298N dual H-bridge module: both peristaltic pumps */}
      <chip
        name="U7U8"
        footprint="dip14"
        pcbX={px("U7U8")} pcbY={py("U7U8")} schX={sx("U7U8")} schY={sy("U7U8")}
        pinLabels={{
          pin1: "ENA", pin2: "IN1", pin3: "IN2", pin4: "IN3", pin5: "IN4", pin6: "ENB",
          pin7: "OUT1", pin8: "OUT2", pin9: "OUT3", pin10: "OUT4",
          pin11: "VS", pin12: "V5", pin13: "GND", pin14: "GND2",
        }}
      />

      {/* U9 — DS3231 RTC module (coin cell on the module) */}
      <chip
        name="U9"
        footprint="dip8"
        pcbX={px("U9")} pcbY={py("U9")} schX={sx("U9")} schY={sy("U9")}
        pinLabels={{ pin1: "VCC", pin2: "GND", pin3: "SDA", pin4: "SCL", pin5: "SQW", pin6: "N32K" }}
      />

      {/* U10 — MP1584EN buck module, 12 V -> 5 V */}
      <chip
        name="U10"
        footprint="dip4"
        pcbX={px("U10")} pcbY={py("U10")} schX={sx("U10")} schY={sy("U10")}
        pinLabels={{ pin1: "INp", pin2: "INn", pin3: "OUTp", pin4: "OUTn" }}
      />

      {/* U12 — RS485 transceiver module (3.3 V, auto-direction) */}
      <chip
        name="U12"
        footprint="dip8"
        pcbX={px("U12")} pcbY={py("U12")} schX={sx("U12")} schY={sy("U12")}
        pinLabels={{ pin1: "VCC", pin2: "GND", pin3: "DI", pin4: "RO", pin5: "DE", pin6: "RE", pin7: "A", pin8: "B" }}
      />

      {/* K1 — AC relay module (compressor, fenced corner) */}
      <chip
        name="K1"
        footprint="dip6"
        pcbX={px("K1")} pcbY={py("K1")} schX={sx("K1")} schY={sy("K1")}
        pinLabels={{ pin1: "IN", pin2: "VCC", pin3: "GND", pin4: "COM", pin5: "NO", pin6: "NC" }}
      />

      {/* K2 — DC relay module (diaphragm pump 12 V) */}
      <chip
        name="K2"
        footprint="dip6"
        pcbX={px("K2")} pcbY={py("K2")} schX={sx("K2")} schY={sy("K2")}
        pinLabels={{ pin1: "IN", pin2: "VCC", pin3: "GND", pin4: "COM", pin5: "NO", pin6: "NC" }}
      />

      {/* ======================= DISCRETE PASSIVES (THT) ======================= */}
      <resistor name="R1" resistance="4.7k" footprint="axial" pcbX={px("R1")} pcbY={py("R1")} schX={sx("R1")} schY={sy("R1")} />
      <resistor name="R2" resistance="4.7k" footprint="axial" pcbX={px("R2")} pcbY={py("R2")} schX={sx("R2")} schY={sy("R2")} />
      <resistor name="R3" resistance="4.7k" footprint="axial" pcbX={px("R3")} pcbY={py("R3")} schX={sx("R3")} schY={sy("R3")} />
      <resistor name="R4" resistance="10k" footprint="axial" pcbX={px("R4")} pcbY={py("R4")} schX={sx("R4")} schY={sy("R4")} />
      <resistor name="R5" resistance="10k" footprint="axial" pcbX={px("R5")} pcbY={py("R5")} schX={sx("R5")} schY={sy("R5")} />
      <resistor name="RFLOW" resistance="10k" footprint="axial" pcbX={px("RFLOW")} pcbY={py("RFLOW")} schX={sx("RFLOW")} schY={sy("RFLOW")} />
      <capacitor name="C1" capacitance="470uF" footprint="radial" polarized pcbX={px("C1")} pcbY={py("C1")} schX={sx("C1")} schY={sy("C1")} />

      {/* ======================= FIELD CONNECTORS ======================= */}
      {connectors.map(([ref, pins]) => (
        <pinheader
          key={ref}
          name={ref}
          pinCount={pins.length}
          pitch="2.54mm"
          gender="male"
          footprint={`pinrow${pins.length}`}
          pinLabels={pins}
          pcbX={px(ref)} pcbY={py(ref)} schX={sx(ref)} schY={sy(ref)}
        />
      ))}

      {/* ======================= POWER RAILS ======================= */}
      <netlabel net="GND" schX={-2} schY={-3} connectsTo={[
        ".J2 > .GND", ".C1 > .pin2",
        ".U1 > .GND", ".U1 > .GND2",
        ".U3 > .GND", ".U3 > .A0", ".U3 > .A1", ".U3 > .A2",
        ".U4 > .GND", ".U4 > .A1", ".U4 > .A2",
        ".U5 > .GND", ".U6 > .GND",
        ".U7U8 > .GND", ".U7U8 > .GND2",
        ".U9 > .GND", ".U10 > .INn", ".U10 > .OUTn", ".U12 > .GND",
        ".K1 > .GND", ".K2 > .GND",
        ".J5 > .PUMPRET",
        ".J10 > .GND", ".J11 > .GND", ".J12 > .GND", ".J13 > .GND",
        ".J14 > .GND", ".J15 > .GND", ".J16 > .GND", ".J17 > .GND",
      ]} />

      <netlabel net="V12" schX={-2} schY={3} connectsTo={[
        ".J2 > .V12", ".C1 > .pin1",
        ".U5 > .COM", ".U6 > .COM",
        ".U7U8 > .VS", ".U10 > .INp",
        ".K2 > .COM",
        ".J8 > .COM", ".J9 > .COM", ".J9 > .COM2",
        ".J16 > .V12",
      ]} />

      <netlabel net="V5" schX={-2} schY={1} connectsTo={[
        ".U10 > .OUTp", ".U1 > .V5", ".U7U8 > .V5",
        ".K1 > .VCC", ".K2 > .VCC",
        ".J14 > .V5", ".J17 > .V5",
      ]} />

      <netlabel net="V3_3" schX={-2} schY={2} connectsTo={[
        ".U1 > .V3_3",
        ".U3 > .VCC", ".U3 > .RST",
        ".U4 > .VCC", ".U4 > .RST", ".U4 > .A0",
        ".U9 > .VCC", ".U12 > .VCC",
        ".R1 > .pin2", ".R2 > .pin2", ".R3 > .pin2",
        ".R4 > .pin2", ".R5 > .pin2", ".RFLOW > .pin2",
        ".J13 > .V3_3",
      ]} />

      {/* ======================= I2C BUS ======================= */}
      <netlabel net="SDA" schX={0} schY={5} connectsTo={[
        ".U1 > .IO21", ".U3 > .SDA", ".U4 > .SDA", ".U9 > .SDA", ".R1 > .pin1",
      ]} />
      <netlabel net="SCL" schX={1} schY={5} connectsTo={[
        ".U1 > .IO22", ".U3 > .SCL", ".U4 > .SCL", ".U9 > .SCL", ".R2 > .pin1",
      ]} />

      {/* ======================= VALVE / FAN FAN-OUTS ======================= */}
      {/* solenoids A-H: MCP U3 GPA0..7 -> ULN U5 IN1..8 -> J8 */}
      {valveAH.map((v, i) => (
        <trace key={`u3-${v}`} from={`.U3 > .GPA${i}`} to={`.U5 > .IN${i + 1}`} />
      ))}
      {valveAH.map((v, i) => (
        <trace key={`j8-${v}`} from={`.U5 > .OUT${i + 1}`} to={`.J8 > .V${v}`} />
      ))}
      {/* solenoids I-KB: MCP U3 GPB0..3 -> ULN U6 IN1..4 -> J9 */}
      {valveIKB.map((v, i) => (
        <trace key={`u6in-${v}`} from={`.U3 > .GPB${i}`} to={`.U6 > .IN${i + 1}`} />
      ))}
      {valveIKB.map((v, i) => (
        <trace key={`j9-${v}`} from={`.U6 > .OUT${i + 1}`} to={`.J9 > .V${v}`} />
      ))}
      {/* condenser fan: MCP U4 GPA4 -> ULN U6 IN5 -> J9 FAN */}
      <trace from=".U4 > .GPA4" to=".U6 > .IN5" />
      <trace from=".U6 > .OUT5" to=".J9 > .FAN" />

      {/* ======================= RESERVOIR REEDS ======================= */}
      {[0, 1, 2, 3].map((i) => (
        <trace key={`ra-${i}`} from={`.J10 > .RA${i + 1}`} to={`.U3 > .GPB${i + 4}`} />
      ))}
      {[0, 1, 2, 3].map((i) => (
        <trace key={`rb-${i}`} from={`.J11 > .RB${i + 1}`} to={`.U4 > .GPA${i}`} />
      ))}

      {/* ======================= SENSOR INPUTS ======================= */}
      <trace from=".J12 > .RLOW" to=".U1 > .IO17" />
      <trace from=".J12 > .RHIGH" to=".U1 > .IO27" />
      <trace from=".R4 > .pin1" to=".U1 > .IO17" />
      <trace from=".R5 > .pin1" to=".U1 > .IO27" />
      <trace from=".J13 > .OW" to=".U1 > .IO16" />
      <trace from=".R3 > .pin1" to=".U1 > .IO16" />
      <trace from=".J14 > .FLOW" to=".U1 > .IO23" />
      <trace from=".RFLOW > .pin1" to=".U1 > .IO23" />
      <trace from=".J15 > .MOIST" to=".U1 > .IO13" />

      {/* ======================= PUMPS (L298N) ======================= */}
      <trace from=".U1 > .IO33" to=".U7U8 > .ENA" />
      <trace from=".U1 > .IO25" to=".U7U8 > .IN1" />
      <trace from=".U1 > .IO26" to=".U7U8 > .IN2" />
      <trace from=".U1 > .IO19" to=".U7U8 > .ENB" />
      <trace from=".U1 > .IO18" to=".U7U8 > .IN3" />
      <trace from=".U1 > .IO5" to=".U7U8 > .IN4" />
      <trace from=".U7U8 > .OUT1" to=".J6 > .A1" />
      <trace from=".U7U8 > .OUT2" to=".J6 > .A2" />
      <trace from=".U7U8 > .OUT3" to=".J7 > .B1" />
      <trace from=".U7U8 > .OUT4" to=".J7 > .B2" />

      {/* ======================= RELAYS ======================= */}
      <trace from=".U1 > .IO14" to=".K1 > .IN" />
      <trace from=".U1 > .IO4" to=".K2 > .IN" />
      {/* AC: J3 in -> K1 switches hot -> J4 out (neutral passes through) */}
      <trace from=".J3 > .ACH" to=".K1 > .COM" />
      <trace from=".K1 > .NO" to=".J4 > .ACH_SW" />
      <trace from=".J3 > .ACN" to=".J4 > .ACN" />
      {/* DC: K2 gates 12 V to the diaphragm pump */}
      <trace from=".K2 > .NO" to=".J5 > .PUMP12" />

      {/* ======================= DISPLAY LINKS ======================= */}
      {/* RS485 -> 4.3B config display */}
      <trace from=".U1 > .IO15" to=".U12 > .DI" />
      <trace from=".U12 > .RO" to=".U1 > .IO34" />
      <trace from=".U12 > .A" to=".J16 > .A" />
      <trace from=".U12 > .B" to=".J16 > .B" />
      <trace from=".U12 > .DE" to=".U12 > .RE" />
      {/* UART -> faucet display */}
      <trace from=".U1 > .IO32" to=".J17 > .TX" />
      <trace from=".J17 > .RX" to=".U1 > .IO35" />
    </board>
  )
}
