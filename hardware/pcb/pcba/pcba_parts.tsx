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
import { ULN2803A } from "./imports/ULN2803A"
import { MCP23017_E_SO } from "./imports/MCP23017_E_SO"
import { DS3231SN_T_R } from "./imports/DS3231SN_T_R"
import { COS13487EESA_3_3 } from "./imports/COS13487EESA_3_3"
import { SM712_TCT } from "./imports/SM712_TCT"
import { ESP32_WROOM_32E_N4 } from "./imports/ESP32_WROOM_32E_N4"
import { AMS1117_3_3 } from "./imports/AMS1117_3_3"
import { CH340C } from "./imports/CH340C"
import { USBLC6_2SC6 } from "./imports/USBLC6_2SC6"
import { TYPE_C_31_M_12 } from "./imports/TYPE_C_31_M_12"
import { DRV8870DDAR } from "./imports/DRV8870DDAR"
import { MT3608 } from "./imports/MT3608"
import { SS34 } from "./imports/SS34"
import { FNR4030 } from "./imports/FNR4030"

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

// JLCPCB-imported footprint (./imports/ULN2803A) so the CPL rotation matches JLCPCB's
// library orientation. Its own pin labels (Input1/Output1) are overridden with ours so the
// net wiring is unchanged. Imported rot 0 is HORIZONTAL (pins on N/S rows); the caller's rot
// is that value directly (rot 270 for the vertical IN-west/OUT-east seating used on U4/U5).
// The import's {NAME} silk is stripped (it rode the seating rotation, reading top-to-bottom at
// rot 270); the ref-des is drawn here upright and centred on the body — a pure function of (x,y).
export const Uln2803 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <>
    <ULN2803A name={name} pinLabels={ulnPinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
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

// JLCPCB-imported footprint (./imports/MCP23017_E_SO, C47023) so the CPL rotation matches
// JLCPCB's library orientation — the generic soic28 placed the body mis-rotated on the pads.
// Its built-in GPB0/GPA7 pin labels are overridden with ours (VCC/GND for VDD/VSS, NC/INT pins
// dropped) so the net wiring is unchanged. Imported rot 0 seats GPA on the north row / GPB on the
// south; the caller's rot is that value directly (rot 180 mirrors that for U2's GPA-south seating,
// rot 0 for U3's GPA-north). The import's own {NAME} silk is stripped (it rides the chip rotation
// and reads sideways/upside-down); the ref-des is drawn here upright and centred on the body — a
// pure function of (x,y), so it rides when the chip is moved.
export const Mcp23017 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; addr?: string; rot?: number }) => (
  <>
    <MCP23017_E_SO name={name} pinLabels={mcpPinLabels} pcbRotation={rot} {...at(x, y)} />
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

// JLCPCB-imported footprint (./imports/DS3231SN_T_R, C9866) for the correct CPL rotation.
// Nearly all pins are poured nets (VCC/GND/SDA/SCL auto-stitch) or run to the coin cell
// (VBAT->BT1), so seating rotation is a fit choice, not a routing one; rot 270 keeps the
// long axis vertical as before. The import's built-in 32kHz/INTSQW labels are overridden with
// ours (NC pins 5-12 dropped). Its {NAME} silk is stripped (sideways at rot 270); the ref-des
// is drawn here upright, centred on the body — a pure function of (x,y).
export const Ds3231Smd = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <>
    <DS3231SN_T_R name={name} pinLabels={ds3231PinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
)

// ---- COS13487EESA-3.3 — RS-485 transceiver, SOP-8 (= SOIC-8), 3.3 V, auto-direction ----
// C51949447 (COSINE COS13487E-3.3): a native-3.3 V MAX13487E-equivalent, ±15 kV ESD,
// -7..+12 V common-mode (matches the SM712 clamp). Auto-direction — the driver auto-
// enables on TX off the DI pin, so there is no host DE/RE line to drive. Pinout
// (datasheet Fig.1) is the MAX13487/THVD1426 map: 1 RO (RX out -> ESP), 2 /RE (tie GND =
// always receive), 3 /SHDN (tie VCC = always on), 4 DI (TX in <- ESP), 5 GND, 6 A, 7 B,
// 8 VCC. RO/DI are the TTL side to the ESP UART; A/B the differential line to J9. In stock
// at JLCPCB but shallow (~530, Extended) — glance at it before a large run.
const cos13487PinLabels = {
  pin1: "RO", pin2: "RE", pin3: "SHDN", pin4: "DI",
  pin5: "GND", pin6: "A", pin7: "B", pin8: "VCC",
}

// JLCPCB-imported footprint (./imports/COS13487EESA_3_3, C51949447) for the correct CPL rotation.
// rot 270 seats RO/RE/SHDN/DI on the west column (toward the ESP UART) and VCC/B/A/GND on the east
// (toward J9 / the R6 termination / the D1 ESD array), reproducing the generic orientation. The
// import's labels already match ours; {NAME} silk stripped for the upright manual ref-des.
export const Cos13487 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <>
    <COS13487EESA_3_3 name={name} pinLabels={cos13487PinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
)

// ---- SM712 — RS-485 ESD/TVS array, SOT-23 -----------------------------------
// C12067 (Semtech SM712.TCT). Asymmetric -7 V / +12 V clamp matching the RS-485
// common-mode range, sits at the J9 cable entry. 1 A line, 2 B line, 3 GND.
const sm712PinLabels = { pin1: "A", pin2: "B", pin3: "GND" }

// JLCPCB-imported footprint (./imports/SM712_TCT, C12067) for the correct CPL rotation. SOT-23,
// so it calibrates separately from the SOICs: rot 180 seats A/B on the west column (toward U7 and
// the J9 line entry) and GND on the east, reproducing the generic orientation. The import's
// A11/A12/K labels are overridden with our A/B/GND; {NAME} silk stripped for the manual ref-des.
export const Sm712 = ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
  <>
    <SM712_TCT name={name} pinLabels={sm712PinLabels} pcbRotation={rot} {...at(x, y)} />
    <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
  </>
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

// MLT-5020 magnetic buzzer (seats rot 90): label on the body, nudged west of centre so it
// clears the +/- polarity silk (which the rot-90 seating throws to the east) while staying
// well inside the footprint — reads as the buzzer's own, not the neighbour Q1's to the west.
export const Buzzer = ({ name, x, y }: Labeled) => (
  <>
    <MLT_5020 name={name} pcbRotation={90} {...at(x, y)} />
    {refdes(name, x - 1.8, y)}
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
    {refdes(name, x, y)}
  </>
)

// S8050 NPN in a SOT-23 (auto-reset Q2/Q3 + buzzer-drive Q1). Its import ref-des is stripped,
// so the ref-des is drawn here upright and centred on the body — a pure function of (x,y), so it
// rides when the part is moved, whatever the seating rotation (rot 180 for Q1, 270 for Q2/Q3).
export const Npn = ({ name, x, y, rot = 180 }: Labeled & { rot?: number }) => (
  <>
    <S8050_J3Y_RANGE_200_350_ name={name} pcbRotation={rot} {...at(x, y)} />
    {refdes(name, x, y)}
  </>
)

// ---- centred-ref-des SMD chips ---------------------------------------------
// The remaining imported chips carry their own pin labels/nets, so all a wrapper
// adds is seating + a clean ref-des. Each has its footprint {NAME} silk stripped
// (it rode the seating rotation — sideways/upside-down at rot 270 — and sat offset
// toward a neighbour) and gets an upright ref-des centred on the body, a pure
// function of (x,y) so it rides when the part moves, exactly like U2/U3 (Mcp23017).
const centred = (Part: (props: any) => any) =>
  ({ name, x, y, rot = 0 }: { name: string; x: number; y: number; rot?: number }) => (
    <>
      <Part name={name} pcbRotation={rot} {...at(x, y)} />
      <silkscreentext text={name} fontSize="0.8mm" anchorAlignment="center" pcbX={x} pcbY={y} />
    </>
  )

export const Esp32 = centred(ESP32_WROOM_32E_N4)   // U1  — bare WROOM module
export const Ams1117 = centred(AMS1117_3_3)         // U9  — 3V3 LDO (SOT-223)
export const Ch340 = centred(CH340C)                // U13 — USB-UART bridge (SOP-16)
export const Usblc6 = centred(USBLC6_2SC6)          // U14 — USB ESD array (SOT-23-6)
export const UsbC = centred(TYPE_C_31_M_12)         // J14 — USB-C receptacle
export const Drv8870 = centred(DRV8870DDAR)         // U11/U12 — pump H-bridges (SOP-8)
export const Boost = centred(MT3608)                // U15 — 5V->12V boost (SOT-23-6)
export const Schottky = centred(SS34)               // D7/D8 — SS34 rectifier / VBUS iso (SMA)
export const Inductor = centred(FNR4030)            // L1 — boost inductor (4x4)
