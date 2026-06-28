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
