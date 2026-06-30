# JLCPCB parts inventory

Parts confirmed in the JLCPCB assembly library, and where each was found. This is the
shared parts reference — separate from BOM/CPL generation: the board carries footprints,
this carries the JLCPCB/LCSC identity each maps to. Stock and price are point-in-time
(date each row). Add rows as steps convert modules.

## Finding a part

- JLCPCB will assemble a part only if it resolves at `jlcpcb.com/partdetail/<slug>/<C#>`
  (the slug is ignored; the `C#` is canonical). The badge under the part name reads
  **Basic**, **Promotional Extended**, or **Extended**. Basic carries no per-part feeder
  fee; Extended adds a feeder/setup fee per unique part and must be in stock.
- An LCSC catalog number (`lcsc.com`) existing does **not** mean JLCPCB stocks it for
  assembly. Verify the JLCPCB partdetail resolves. `C72518` (ROQANG RVT1E471M1010,
  470µF/25V) is on LCSC but its JLCPCB partdetail redirects to `/parts` — not in the
  assembly library. The JLCPCB-library equivalents carry different `C#`s (e.g. `C3351`).
- Search the library: `jlcpcb.com/parts` → search `value package` (e.g. `470uF 25V SMD`)
  → the componentSearch grid; filter Parts Type and In-stock; read MFR Part #, LCSC #,
  library type, stock, price.
- Footprint into tscircuit: standard chip passives use the built-in footprinter names
  (`0603`, `0805`), which match the JLCPCB part. For THT or odd parts the generic footprint
  can mismatch the supplier's land pattern — `tsci build` prints a copper-IoU warning — so
  pull the real one with `tsci import <C#>` and use it (see C3 → `imports/`).
- Wire a part onto the board with `supplierPartNumbers={{ jlcpcb: ["C#"] }}` on the
  component; that is what flows into the JLCPCB BOM/CPL.

## Inventory

| Board use | Value | Package | LCSC | Library | Stock (2026-06-27) | Unit |
|---|---|---|---|---|---|---|
| R1, R3 — gas divider, top leg | 2.2 kΩ ±1% | 0603 | C4190 | Basic | 2,358,134 | $0.0019 |
| R2, R4 — gas divider, bottom leg | 3.3 kΩ ±1% | 0603 | C22978 | Basic | 1,028,999 | $0.0023 |
| C1, C2 — V12 HF decouple | 0.1 µF 50V X7R | 0805 | C49678 | Basic | 8,182,736 | $0.0136 |
| C3 — V12 bulk | 470 µF 25V | radial THT, D10×12.5, 5.08 mm | C350206 | Extended | 91 | $0.105 |
| U4, U5 — valve/fan sink drivers | ULN2803A, 8-ch Darlington | SOIC-18 (300 mil) | C845537 | Extended | 350,244 | $0.089 |
| U2, U3 — I²C GPIO expanders | MCP23017, 16-bit | SOIC-28 (300 mil) | C47023 | Extended | — | — |
| U8 — alarm/tone buzzer | MLT-5020, passive magnetic (external drive), 4 kHz/75 dB, ~100 mA | SMD 5×5 mm | C94598 | Extended | 104,490 | $0.434 |
| Q1 — U8 low-side driver | S8050 (J3Y), NPN 25 V/500 mA | SOT-23 | C2146 | Basic | 554,300 | $0.015 |
| R5 — Q1 base | 1 kΩ ±1% | 0603 | C21190 | Basic | 6,282,722 | $0.0023 |
| U6 — RTC | DS3231SN, TCXO RTC (±2 ppm) | SOIC-16 (300 mil) | C9866 | Extended | 335 | $6.14 |
| BT1 — RTC backup | CR2032 coin base, 2-pin THT (horizontal) | THT plugin ~25×23 mm | C5365915 | Extended | 11,888 (2026-06-30) | $0.135 |
| U7 — RS485 to display | THVD1426, auto-direction transceiver, 3.3 V | SOIC-8 | C5215922 | Extended | 5,945 | $1.84 |
| D1 — RS485 line ESD | SM712, RS485 TVS array (−7/+12 V) | SOT-23 | C12067 | Extended | 35,585 | $0.41 |
| R6 — RS485 termination | 120 Ω ±1% | 0603 | C22787 | Basic | 1,728,584 | $0.0022 |
| U9 — 12V→3V3 buck | K7803-1000R3, 1 A non-isolated switcher | SIP-3 (THT) | C5369647 | Extended | — | — |
| U10 — 12V→5V buck | K7805-2000R3, 2 A non-isolated switcher | SIP-3 (THT) | C18212380 | Extended | — | — |
| U11, U12 — pump H-bridges | DRV8870, single H-bridge, 45 V / 3.6 A | SOIC-8 PowerPAD | C86590 | Extended | — | — |
| C13/C14/C15/C17/C19 — buck/driver decouple | 10 µF 25V X5R | 0805 | C15850 | Basic | (see C11) | $0.01 |
| C16 — U10 5V buck output | 22 µF 25V X5R | 0805 | C45783 | Basic | — | $0.02 |
| C18/C20 — driver VM HF | 0.1 µF 50V X7R | 0805 | C49678 | Basic | (see C1/C2) | $0.0136 |
| U1 — base controller | ESP32-WROOM-32E-N4, no radio | SMD module 18×25.5 mm | C701341 | Extended | 22,002 (2026-06-28) | $3.77 |
| R7, R8 — EN / IO0 pull-ups | 10 kΩ ±1% | 0603 | C25804 | Basic | 3,845,978 | $0.0013 |
| C10 — ESP 3V3 decouple | 0.1 µF 50V X7R | 0805 | C49678 | Basic | (see C1/C2) | $0.0136 |
| C11 — ESP 3V3 bulk | 10 µF 25V X5R | 0805 | C15850 | Basic | (see C8) | $0.01 |
| C12 — EN power-on RC | 1 µF 50V X5R | 0603 | C15849 | Basic | 6,521,627 | $0.036 |
| J10 — 2-pin (12V inlet) | XH2.54 2P, vertical THT male wafer | wafer, 2.5 mm | C5359631 | Extended | 74,020 | $0.0141 |
| J9 — 3-pin (SCREEN / RS485) | XH2.54 3P | wafer, 2.5 mm | C5374805 | Extended | 9,613 (2026-06-30) | $0.0218 |
| J3, J5, J11, J13 — 4-pin (FAUCET, RELAYS, GAS, PUMPS) | XH2.54 4P | wafer, 2.5 mm | C5359632 | Extended | 39,475 (2026-06-30) | $0.0116 |
| J6 — 5-pin (REEDS A) | XH2.54 5P | wafer, 2.5 mm | C5359633 | Extended | 14,791 | $0.0294 |
| J2, J4, J12 — 6-pin (MANIFOLD B, SENSORS, PROG) | XH2.54 6P | wafer, 2.5 mm | C5359634 | Extended | 42,550 | $0.0254 |
| J7 — 7-pin (REEDS B) | XH2.54 7P | wafer, 2.5 mm | C5359635 | Extended | 16,231 | $0.0278 |
| J1 — 9-pin (MANIFOLD A) | XH2.54 9P | wafer, 2.5 mm | C5359637 | Extended | 380 (2026-06-30) | $0.0400 |

Manufacturers: C4190 / C22978 / C21190 = UNI-ROYAL 0603WAF series; C49678 = YAGEO
CC0805KRX7R9BB104; C845537 = UMW (Youtai) ULN2803A; C47023 = Microchip MCP23017-E/SO;
C94598 = Jiangsu Huaneng MLT-5020; C2146 = JSCJ S8050 J3Y; XH2.54 connectors = XUNPU
WAFER-XH2.54-{n}PZZ, one vendor across all seven pin counts, vertical THT.

**The "XH2.54" connectors are physically 2.5 mm pitch.** Genuine JST XH is 2.50 mm; the
ubiquitous "2.54 mm JST-XH" kits/housings are that same 2.50 mm part with a rounded label,
and the JLCPCB XH2.54 wafers measure 2.50 mm (holes at ±6.25/±3.75/±1.25 mm on the 6P). So
the board header is 2.5 mm, not 2.54 — the `Jst` footprint is `pinrow${n}_p2.5mm_id1.1mm_od1.65mm`
to match the wafer land pattern exactly (clean IoU), and it mates with the standard female
XH housings the wiring kits use. Every XH2.54 part in the library is Extended (no Basic
option), and all seven counts come from **one vendor — XUNPU's WAFER-XH2.54-{n}PZZ
series** — so every wafer's 3D model seats the same way at a given CPL rotation and its
pin-1 (square) pad sits at the same end, with no per-part rotation offset to maintain.
(A single vendor was preferred over the cheapest-per-count mix precisely so the assembled
board reads uniformly; the only watch-out is the 9P, `C5359637`, which runs lower stock —
~380 at 2026-06-30 vs tens of thousands for the rest — but it's the lone MANIFOLD A
connector, so fine for a build; glance at it before a large run.)

**U4/U5 are `C845537`** (UMW ULN2803A, SOP-18-300mil wide body). No Basic ULN2803 SOIC
exists in the library — every ULN2803 part is Extended — so the feeder fee is unavoidable;
C845537 is the cheapest with deep stock (genuine-TI ULN2803ADWR is `C9683`, ~$4.40). The
generic `soic18_w7.5mm_p1.27mm` footprint matches the 300-mil land pattern (no IoU warning),
so no `tsci import`. Pins 1-8 IN1-IN8, 9 GND, 10 COM (12 V flyback common), 11-18 OUT8-OUT1.

**C3 is wired as a THT radial — `C350206`** (SamYoung NXB, D10×12.5 mm, 5.08 mm pitch,
53 mΩ ESR / 1.36 A ripple / 4000 h @105 °C), placed by JLCPCB through-hole assembly; its
barrel stitches to V12/GND directly (no SMD via). Footprint pulled with `tsci import` to
match the part's pads — the generic `radial_p5.08mm` matched at only IoU 0.55 → `imports/`.

THT because the need (V12 bulk decoupling) has no Basic SMD option: both 470 µF/25V and
100 µF/25V SMD are **Extended only** across the whole library (Rubycon / Panasonic / Nichicon
included). Extended SMD alternatives, for a full-reflow board: `C3351` (Honor RVT1E471M1010,
$0.060), `C47023111` (D8×L10, $0.050), `C3445246` (90 mΩ / 5000 h, $0.091); or a Basic MLCC
bank (several 25V MLCCs — lower bulk, far lower ESR, wants checking against the solenoid inrush).

**U8 is a passive buzzer + transistor, not an active buzzer.** The firmware generates the
tone on IO4 (LEDC), so the part must be externally driven — `C94598` (MLT-5020) is passive
electromagnetic. Every passive SMD buzzer in the library is Extended; `C94598` has the deepest
stock at 5×5 mm. Its ~100 mA coil exceeds the ESP32 GPIO's ~12 mA source, so it is **low-side
switched** by Q1 (`C2146`, S8050 NPN, Basic): IO4 → R5 (1 kΩ base) → Q1 base; Q1 collector
sinks the buzzer's − leg, emitter to the GND plane, the + leg on the 5 V plane. No flyback
diode (per the step spec); the S8050's 25 V Vce(o) is the only clamp on the coil's turn-off
spike — the first thing to add if the transistor shows stress. Q1 emitter and U8 + are SMD
plane pads and auto-stitch to GND / 5 V (see [`plane-stitching.md`](plane-stitching.md)).

**BT1 is a THT coin base (`C5365915`, Kinghelm KH-CR2032-2-1), not the cheapest SMT clip.**
The bare bent-leg SMT clip (`C70373`, $0.05, 27k stock) is the cheapest CR2032 holder in the
library, but JLCPCB rates it **"Assembly difficulty: High"** — it trips the "processing of this
component is difficult" review (and a possible advanced-option fee) on every order. Every CR2032
holder in the library is Extended (no Basic option), so the feeder fee is unavoidable either way;
among the holders JLCPCB does **not** flag, the 2-pin THT base is the mechanically secure choice and
rides the through-hole assembly the board already runs for the XH connectors. Two 1.2 mm plated
posts at ±10 mm: pin1 (silk-marked +) → DS3231 VBAT, pin2 (−) → GND; the cell is retained by the
molded base. `tsci import` pulled the real land pattern (→ `imports/KH_CR2032_2_1.tsx`).

**U1 is the bare ESP32-WROOM-32E-N4 (`C701341`, Extended), the ESP32 base part.**
The only ESP32 base part the design needs — radio unused, so the cheapest WROOM-32E variant
(4 MB, N4) is fine; the keepout silk stays but no plane is carved (no RF). Placed `rot 180`
so the module's pin geography falls into two rows (ADC/UART/pump-A north,
I2C/pump-B/buzzer/IO0 south), keeping the driver and faucet route corridors clean. It is **3V3-only** — no onboard regulator, no V5 pin — drawing the WiFi-idle ~110 mA
peak from the 3V3 buck plane through its single 3V3 stitch via, with C10 (0.1 µF) + C11
(10 µF bulk) at the pin. The 3 castellated GND pads + the 9-pad centre thermal pad all share
one `GND` port and each auto-stitches to the bottom plane. EN power-on RC: R7 (10 kΩ, `C25804`
Basic) up to 3V3, C12 (1 µF, `C15849` Basic) to GND. IO0 held high by R8 (10 kΩ). J12 is the
6-pin serial bootloader header (TX0/RX0/IO0/EN/GND/3V3) on the same XH wafer as the field
connectors. The bare module's IO pins are SMD pads, so the maze router was taught to take SMD
pads as single-layer endpoints (a barrel-free via lands a bottom run up onto the top pad —
`pretty-router.ts`); 8 such maze nets land via-in-pad, capped like the plane stitches.
