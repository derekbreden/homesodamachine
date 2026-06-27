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
- Footprint into tscircuit: `tsci import <C#>`. Standard chip passives use the built-in
  footprinter names (`0603`, `0805`).

## Inventory

| Board use | Value | Package | LCSC | Library | Stock (2026-06-27) | Unit |
|---|---|---|---|---|---|---|
| R1, R3 — gas divider, top leg | 2.2 kΩ ±1% | 0603 | C4190 | Basic | 2,358,134 | $0.0019 |
| R2, R4 — gas divider, bottom leg | 3.3 kΩ ±1% | 0603 | C22978 | Basic | 1,028,999 | $0.0023 |
| C1, C2 — V12 HF decouple | 0.1 µF 50V X7R | 0805 | C49678 | Basic | 8,182,736 | $0.0136 |
| C3 — V12 bulk | 470 µF 25V | open | not yet assigned | — | — | — |

Manufacturers: C4190 / C22978 = UNI-ROYAL 0603WAF series; C49678 = YAGEO
CC0805KRX7R9BB104.

**C3 has no JLCPCB part assigned yet — its form is an open decision.** Its need is V12
bulk decoupling (soak solenoid inrush + flyback). JLCPCB's Basic library carries no
aluminium-electrolytic or polymer at bulk values: both 470 µF/25V and 100 µF/25V SMD are
**Extended only** (verified across every manufacturer in the library, Rubycon / Panasonic /
Nichicon included). So an SMD bulk cap is an Extended line whatever the value. Options:

- **THT radial**, placed by JLCPCB through-hole assembly (already paid for the J connectors,
  plan step 5); keeps its barrel plane-stitch. Needs a JLCPCB-library THT 470 µF/25V part chosen.
- **One Extended SMD electrolytic** — `C3351` (Honor RVT1E471M1010, $0.060), `C47023111`
  (D8×L10, $0.050), `C3445246` (90 mΩ / 5000 h, $0.091).
- **A Basic MLCC bank** — ceramics are the Basic library's strength and electrically the best
  snubber; reaching usable bulk (~100 µF) takes several 25V MLCCs, and the bulk-vs-ESR
  tradeoff against the electrolytic wants checking against the actual solenoid current.
