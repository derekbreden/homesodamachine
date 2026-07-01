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
import { K7805_2000R3 } from "./imports/K7805_2000R3"
import { MLT_5020 } from "./imports/MLT_5020"
import { KH_CR2032_2_1 } from "./imports/KH_CR2032_2_1"
import { NXB_25V470_10_12_5 } from "./imports/NXB_25V470_10_12_5"
import { S8050_J3Y_RANGE_200_350_ } from "./imports/S8050_J3Y_RANGE_200_350_"

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

// The soic28 footprint is `_norefdes` (its auto ref-des locks to the chip's 90°/270°
// rotation and reads sideways), so the ref-des is drawn here, upright and centred on
// the body — a pure function of (x,y), so it rides when the chip is moved.
export const Mcp23017 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; addr?: string; rot?: number }) => (
  <>
    <chip
      name={name}
      footprint="soic28_w7.5mm_p1.27mm_norefdes"
      pcbRotation={rot}
      pinLabels={mcpPinLabels}
      supplierPartNumbers={{ jlcpcb: ["C47023"] }}
      {...at(x, y)}
    />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
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

// ---- labeled wrappers for imported parts -----------------------------------
// These imports either carry no footprint ref-des (coin holder, bulk cap, buzzer)
// or one that reads upside-down at the part's seating rotation (the rot-180 buck +
// transistor). Each wrapper draws an upright ref-des whose position is a pure
// function of (x,y) — so it rides with the part when moved, the Cap/Jst convention —
// and bakes in the fixed seating rotation. `dx/dy` place the label just off the
// printed body: outside it for the tall through-hole parts (coin, bulk cap, buzzer),
// inside the fence above the pin row for the buck (matches U9). The buzzer/coin/bulk
// bodies stand over the board, so their labels sit clear of the footprint.
type Labeled = { name: string; x: number; y: number }
const refdes = (name: string, x: number, y: number) =>
  <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />

// K7805 5 V buck (seats rot 180): label upright inside the fence, above the pins.
export const Buck5 = ({ name, x, y }: Labeled) => (
  <>
    <K7805_2000R3 name={name} pcbRotation={180} {...at(x, y)} />
    {refdes(name, x, y + 3)}
  </>
)

// MLT-5020 magnetic buzzer (seats rot 90): label in the open lane to the west
// (Q1 sits north, an LED resistor south).
export const Buzzer = ({ name, x, y }: Labeled) => (
  <>
    <MLT_5020 name={name} pcbRotation={90} {...at(x, y)} />
    {refdes(name, x - 4.2, y)}
  </>
)

// CR2032 20 mm coin holder: label above the holder (its body covers the centre).
export const CoinHolder = ({ name, x, y }: Labeled) => (
  <>
    <KH_CR2032_2_1 name={name} pcbRotation={0} {...at(x, y)} />
    {refdes(name, x, y + 12)}
  </>
)

// 470 µF radial bulk cap: label below the can (its body covers the centre).
export const BulkCap = ({ name, x, y }: Labeled) => (
  <>
    <NXB_25V470_10_12_5 name={name} pcbRotation={0} {...at(x, y)} />
    {refdes(name, x + 1.75, y - 6.3)}
  </>
)

// S8050 NPN (seats rot 180; its import ref-des is stripped so it isn't drawn
// upside-down): label upright just north of the body (R5 sits to the west).
export const Npn = ({ name, x, y }: Labeled) => (
  <>
    <S8050_J3Y_RANGE_200_350_ name={name} pcbRotation={180} {...at(x, y)} />
    {refdes(name, x, y + 2.85)}
  </>
)
