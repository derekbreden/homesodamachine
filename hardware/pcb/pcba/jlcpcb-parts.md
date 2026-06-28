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
| J8, J10 — 2-pin (5V, 12V) | XH2.54 2P, vertical THT male wafer | wafer, 2.5 mm | C5359631 | Extended | 74,020 | $0.0141 |
| J9 — 3-pin (DISPLAY) | XH2.54 3P | wafer, 2.5 mm | C7429633 | Extended | 411,459 | $0.0117 |
| J3, J11 — 4-pin (FAUCET, GAS) | XH2.54 4P | wafer, 2.5 mm | C7429634 | Extended | 609,442 | $0.0116 |
| J6 — 5-pin (REEDS A) | XH2.54 5P | wafer, 2.5 mm | C5359633 | Extended | 14,791 | $0.0294 |
| J2, J4 — 6-pin (MANIFOLD B, SENSORS) | XH2.54 6P | wafer, 2.5 mm | C5359634 | Extended | 42,550 | $0.0254 |
| J7 — 7-pin (REEDS B) | XH2.54 7P | wafer, 2.5 mm | C5359635 | Extended | 16,231 | $0.0278 |
| J1, J5 — 9-pin (MANIFOLD A, DRIVER) | XH2.54 9P | wafer, 2.5 mm | C7429639 | Extended | 39,643 | $0.0410 |

Manufacturers: C4190 / C22978 / C21190 = UNI-ROYAL 0603WAF series; C49678 = YAGEO
CC0805KRX7R9BB104; C845537 = UMW (Youtai) ULN2803A; C47023 = Microchip MCP23017-E/SO;
C94598 = Jiangsu Huaneng MLT-5020; C2146 = JSCJ S8050 J3Y; XH2.54 connectors = XUNPU
WAFER-XH2.54-NPZZ (2/5/6/7P) + Megastar ZX-XH2.54-NPZZ (3/4/9P), both vertical THT.

**The "XH2.54" connectors are physically 2.5 mm pitch.** Genuine JST XH is 2.50 mm; the
ubiquitous "2.54 mm JST-XH" kits/housings are that same 2.50 mm part with a rounded label,
and the JLCPCB XH2.54 wafers measure 2.50 mm (holes at ±6.25/±3.75/±1.25 mm on the 6P). So
the board header is 2.5 mm, not 2.54 — the `Jst` footprint is `pinrow${n}_p2.5mm_id1.1mm_od1.65mm`
to match the wafer land pattern exactly (clean IoU), and it mates with the standard female
XH housings the wiring kits use. Every XH2.54 part in the library is Extended (no Basic option),
so the 11 connectors share two feeders (XUNPU + Megastar) across all seven pin counts.

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
