# Module-by-module conversion plan

Each step is one in-place swap on the PCBA board (method in [`README.md`](README.md)),
rendered and read against the carrier before the next. Every render also writes
`out/pcba.{bom,cpl}.csv` (the JLCPCB BOM + placements) and logs how many parts carry a
JLCPCB part number — the fab package is proven continuously and the wired count (N/35) is
the coverage signal, so nothing is deferred to "figure out at the end."

| # | Step | Becomes |
|---|------|---------|
| 0 | Project bring-up | copy carrier → `pcba` board + `pcba_parts` |
| 1 | Through-hole passives | R1–R4, C1–C3 → SMD |
| 2 | ULN2803A ×2 (U4/U5) | SOIC-18 |
| 3 | MCP23017 ×2 (U2/U3) | SOIC-28 |
| 4 | Buzzer (U8) | SMD buzzer |
| 5 | Connectors J1–J11 | THT assembly (BOM/CPL) |
| 6 | DS3231 (U6) | DS3231SN + coin cell |
| 7 | RS485 (U7) | auto-direction transceiver |
| 8 | Power | 5 V→3V3 LDO |
| 9 | ESP32 (U1) | WROOM-32E |
| 10 | Integration + DFM | place, paste, BOM/CPL, stock |

## Steps

### 0 — Project bring-up
Copy `../carrier/mini.tsx` to a `pcba` board; copy the parts it imports. `pcba_parts.tsx`
holds the SMD footprints as authored; `carrier_parts.tsx` stays the THT module footprints,
imported until each module is converted. The carrier's render pipeline + patches run
against the copy. First render matches the carrier.

### 1 — Through-hole passives → SMD
R1–R4 (2.2k/3.3k) → 0603 (C4190 / C22978, Basic); C1/C2 (0.1 µF) → 0805 (C49678, Basic).
C3 (470 µF / 25 V) is wired as a THT radial — `C350206`, placed by JLCPCB through-hole
assembly (no Basic SMD bulk cap exists; see [`jlcpcb-parts.md`](jlcpcb-parts.md)); its barrel
stitches to the planes directly. Each SMD pad on a plane net (the GND legs) is auto-stitched to
the plane by the core patch — a net-carrying via-in-pad, no `<pcbtrace>` declared in the board;
see [`plane-stitching.md`](plane-stitching.md). All seven step-1 passives carry
`supplierPartNumbers` (JLCPCB BOM/CPL-ready).

### 2 — ULN2803A ×2 → SOIC-18
The 18 module pins (8 IN, 8 OUT, GND, COM) → the 18 SOIC pads, same nets. Flyback diodes
internal; optional 0.1 µF on COM. Roster: `ulnIN` / `ulnOUT` in `carrier_parts`.

### 3 — MCP23017 ×2 → SOIC-28
SOIC-28 + 0.1 µF + RESET pull-up + A0/A1/A2 straps. U2=0x20, U3=0x21 differ at A0.
GPA / GPB / SDA / SCL / INT → existing nets.

### 4 — Buzzer → SMD buzzer
SMD buzzer on GND / IO / VCC; drive transistor + base resistor where the buzzer current
exceeds the GPIO's source.

### 5 — Connectors J1–J11 → THT assembly (BOM/CPL)
The JST / screw terminals stay through-hole, marked for JLCPCB through-hole assembly in
the BOM/CPL, each mapped to a stocked LCSC THT part — a stocked equivalent or a consigned
part where a series isn't carried.

### 6 — DS3231 → DS3231SN + coin cell
DS3231SN (SOIC-16; TCXO + crystal internal) + 0.1 µF + SMD coin-cell holder; the AT24C32
EEPROM dropped. New: the VBAT net and the holder footprint in the existing rectangle.
I²C at 0x68. Non-rechargeable hold (CR2032, no charging path).

### 7 — RS485 → auto-direction transceiver
Auto-direction transceiver (no DE/RE) + bias / termination + line ESD; VCC 3.3 V. A
discrete auto-direction circuit's RC turn-around is set by the baud rate and is not in
the render.

### 8 — Power → 5 V→3V3 LDO
LDO (5 V → 3V3) + input/output caps near the ESP block. 3V3 loads: both MCPs, DS3231,
RS485, the sensor loom's 3V3 leg.

### 9 — ESP32 → WROOM-32E
See [`esp32-scope.md`](esp32-scope.md).

### 10 — Complete coverage + DFM
The BOM/CPL already regenerate each render; this is where the wired count reaches 35/35
(every connector and former module carries a JLCPCB #), plus final DFM — one-side placement
where possible, paste + courtyards, LCSC stock recheck, JLCPCB assembly rules. Fabrication here.
