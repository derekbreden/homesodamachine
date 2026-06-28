/**
 * pcba_parts — bare SMD silicon footprints for the JLCPCB-assembled successor.
 *
 * As each plug-in module on the carrier is converted, its 2.54 mm header
 * footprint in ./carrier_parts is replaced by the real chip here: same pin
 * labels and nets, an in-stock LCSC/JLCPCB part on `supplierPartNumbers` so it
 * flows into the BOM/CPL. pcba.tsx imports the converted ones from here and the
 * not-yet-converted ones from ./carrier_parts.
 */
import { at } from "./carrier_parts"

// ---- ULN2803A — SOIC-18 (300 mil wide) -------------------------------------
// Octal Darlington sink driver. C845537 (UMW ULN2803A, SOP-18-300mil). Pinout:
// 1-8 IN1-IN8 (left, toward the MCP GPA banks), 9 GND, 10 COM (12 V flyback
// common), 11-18 OUT8-OUT1 (right, toward the manifold JSTs). Default
// orientation already runs IN on -X / OUT on +X, so the GPA->IN->OUT->valve flow
// is left-to-right with no row reversal. GND (pin 9, an SMD pad) auto-stitches to
// the bottom GND plane; COM (pin 10) lands on net.V12 under the top V12 island.
const ulnPinLabels = {
  pin1: "IN1", pin2: "IN2", pin3: "IN3", pin4: "IN4",
  pin5: "IN5", pin6: "IN6", pin7: "IN7", pin8: "IN8",
  pin9: "GND", pin10: "COM",
  pin11: "OUT8", pin12: "OUT7", pin13: "OUT6", pin14: "OUT5",
  pin15: "OUT4", pin16: "OUT3", pin17: "OUT2", pin18: "OUT1",
}

export const Uln2803 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <chip
    name={name}
    footprint="soic18_w7.5mm_p1.27mm"
    pcbRotation={rot}
    pinLabels={ulnPinLabels}
    supplierPartNumbers={{ jlcpcb: ["C845537"] }}
    {...at(x, y)}
  />
)

// ---- MCP23017 — SOIC-28 (300 mil) ------------------------------------------
// 16-bit I2C GPIO expander. C47023 (Microchip MCP23017-E/SO). Pinout: 1-8 GPB0-7
// (left, toward the reed JSTs), 9 VDD, 10 VSS, 11 NC, 12 SCL, 13 SDA, 14 NC,
// 15 A0, 16 A1, 17 A2, 18 /RESET, 19 INTB, 20 INTA, 21-28 GPA0-7 (right, toward
// the ULN inputs). VDD auto-stitches to the 3V3 inner plane, VSS to the bottom GND
// plane. A0/A1/A2 are strapped and /RESET tied high in pcba.tsx (the address +
// reset the breakout module set with jumpers); INTA/INTB are unused (polled). NC
// pins 11/14 and the INT pins are left off the label map → unconnected pads.
const mcpPinLabels = {
  pin1: "GPB0", pin2: "GPB1", pin3: "GPB2", pin4: "GPB3",
  pin5: "GPB4", pin6: "GPB5", pin7: "GPB6", pin8: "GPB7",
  pin9: "VCC", pin10: "GND", pin12: "SCL", pin13: "SDA",
  pin15: "A0", pin16: "A1", pin17: "A2", pin18: "RESET",
  pin21: "GPA0", pin22: "GPA1", pin23: "GPA2", pin24: "GPA3",
  pin25: "GPA4", pin26: "GPA5", pin27: "GPA6", pin28: "GPA7",
}

export const Mcp23017 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; addr?: string; rot?: number }) => (
  <chip
    name={name}
    footprint="soic28_w7.5mm_p1.27mm"
    pcbRotation={rot}
    pinLabels={mcpPinLabels}
    supplierPartNumbers={{ jlcpcb: ["C47023"] }}
    {...at(x, y)}
  />
)

// ---- DS3231SN — SOIC-16 (300 mil) ------------------------------------------
// I2C RTC with internal TCXO + crystal (±2 ppm). C9866 (ADI/Maxim DS3231SN#).
// Pinout: 1 32KHZ, 2 VCC, 3 INT/SQW, 4 /RST, 5-12 NC, 13 GND, 14 VBAT, 15 SDA,
// 16 SCL. The breakout's AT24C32 EEPROM is dropped (firmware uses none). VCC
// auto-stitches to the 3V3 inner plane, GND to the bottom plane; VBAT runs to the
// coin cell (no charging path — trickle charger off by default). 32KHZ/SQW unused,
// /RST has an internal pull-up (NC). NC pins are left off the map → unconnected.
const ds3231PinLabels = {
  pin1: "T32K", pin2: "VCC", pin3: "SQW", pin4: "RST",
  pin13: "GND", pin14: "VBAT", pin15: "SDA", pin16: "SCL",
}

export const Ds3231Smd = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <chip
    name={name}
    footprint="soic16_w7.5mm_p1.27mm"
    pcbRotation={rot}
    pinLabels={ds3231PinLabels}
    supplierPartNumbers={{ jlcpcb: ["C9866"] }}
    {...at(x, y)}
  />
)

// ---- THVD1426 — RS-485 transceiver, SOIC-8, auto-direction -------------------
// C5215922 (TI THVD1426DRLR). 3.0-5.5 V, 12 Mbps, internal auto-direction off the
// D pin — no host DE/RE. NOT the MAX485 pinout: 1 R (RX out), 2 /RE (tie GND =
// always receive), 3 /SHDN (tie VCC = always on), 4 D (TX in), 5 GND, 6 A, 7 B,
// 8 VCC. R/D are the TTL side to the ESP UART; A/B the differential line to J9.
const thvdPinLabels = {
  pin1: "R", pin2: "RE", pin3: "SHDN", pin4: "D",
  pin5: "GND", pin6: "A", pin7: "B", pin8: "VCC",
}

export const Thvd1426 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <chip
    name={name}
    footprint="soic8"
    pcbRotation={rot}
    pinLabels={thvdPinLabels}
    supplierPartNumbers={{ jlcpcb: ["C5215922"] }}
    {...at(x, y)}
  />
)

// ---- SM712 — RS-485 ESD/TVS array, SOT-23 -----------------------------------
// C12067 (Semtech SM712.TCT). Asymmetric -7 V / +12 V clamp matching the RS-485
// common-mode range, sits at the J9 cable entry. 1 A line, 2 B line, 3 GND.
const sm712PinLabels = { pin1: "A", pin2: "B", pin3: "GND" }

export const Sm712 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <chip
    name={name}
    footprint="sot23"
    pcbRotation={rot}
    pinLabels={sm712PinLabels}
    supplierPartNumbers={{ jlcpcb: ["C12067"] }}
    {...at(x, y)}
  />
)

// ---- AMS1117-3.3 — 5 V -> 3V3 LDO, SOT-223 ----------------------------------
// C6186 (AMS1117-3.3, 1 A, 1.1 V dropout). Pin 1 GND, 2 VOUT, 3 VIN; the heat-tab
// is VOUT (labelled on the 4th pad). The board's 3V3 source once the ESP module's
// onboard regulator is dropped — feeds both MCPs, DS3231, RS485, the sensor 3V3 leg
// and (after step 9) the bare ESP, so it carries the WiFi-TX peak. 10uF in / 22uF out.
const amsPinLabels = { pin1: "GND", pin2: "VOUT", pin3: "VIN", pin4: "VOUT" }

export const Ams1117_33 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <chip
    name={name}
    footprint="sot223"
    pcbRotation={rot}
    pinLabels={amsPinLabels}
    supplierPartNumbers={{ jlcpcb: ["C6186"] }}
    {...at(x, y)}
  />
)
