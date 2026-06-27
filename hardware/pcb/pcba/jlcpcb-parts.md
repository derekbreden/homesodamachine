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

Manufacturers: C4190 / C22978 = UNI-ROYAL 0603WAF series; C49678 = YAGEO
CC0805KRX7R9BB104.

**C3 is wired as a THT radial — `C350206`** (SamYoung NXB, D10×12.5 mm, 5.08 mm pitch,
53 mΩ ESR / 1.36 A ripple / 4000 h @105 °C), placed by JLCPCB through-hole assembly; its
barrel stitches to V12/GND directly (no SMD via). Footprint pulled with `tsci import` to
match the part's pads — the generic `radial_p5.08mm` matched at only IoU 0.55 → `imports/`.

THT because the need (V12 bulk decoupling) has no Basic SMD option: both 470 µF/25V and
100 µF/25V SMD are **Extended only** across the whole library (Rubycon / Panasonic / Nichicon
included). Extended SMD alternatives, for a full-reflow board: `C3351` (Honor RVT1E471M1010,
$0.060), `C47023111` (D8×L10, $0.050), `C3445246` (90 mΩ / 5000 h, $0.091); or a Basic MLCC
bank (several 25V MLCCs — lower bulk, far lower ESR, wants checking against the solenoid inrush).
