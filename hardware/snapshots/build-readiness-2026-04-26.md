# Build readiness — Unit #1 — Snapshot 2026-04-26

**This is a point-in-time snapshot, not a living document.** The data here will go stale as bom.md and purchases.md evolve. As of this writing the user is more than a month out from placing the unit-#1 order and further design work may revise the BOM in the meantime. Treat this file as a reference point for re-running the same audit later — same methodology, fresh data — and for comparing against the then-current state.

## TL;DR

- **Estimated total spend to fully provision unit #1: ~$619** (plus NE tax + shipping).
  - **~$469** in single-unit items consumed 1:1 per appliance.
  - **~$150** in pack purchases that also feed future units.
- **Lead time:** most items are Amazon Prime (1–3 day delivery). No items are stuck on a long-lead vendor. The four forward-plan SKUs (Wellbom regulator, Westbrass R2031-NL-62 faucet, DIGITEN G3/8" flow sensor, PureSec Y splitter) and the zip ties pack just need a quick "do we still want this SKU vs alternate-on-hand" review before ordering — they're not pre-ordered because they were always future-plan, not because they're hard to source.

## Source-data state at snapshot time

- `bom.md` per-unit total: **$1,286.85** (state at commit `48ca800`, after rear-panel bezel-recess directive moved to future.md; reflects Tier 2 + Tier 3 amortizations and the Kamoer/L298N/VALVENTO/ANPTGHT/VEVOR fold-up corrections)
- `purchases.md` ACQUIRED hardware: **$14,472.92** / grand total: **$19,886.69** (state at commit `7e7e7b8`, after GASHER spares order)

## Methodology

Walked every line of `bom.md` §§1–12 and cross-referenced against `purchases.md` ACQUIRED / ON-ORDER inventory, with the assumption that the **bench prototype has consumed 1 unit's worth of every item that gets physically installed** (not tools, fabrication equipment, or shop bench gear). For pack-amortized items, available pack qty is reduced by 1 (prototype consumption) before checking whether unit #1 is covered.

To re-run later: spawn a `general-purpose` Claude agent with the same prompt structure used on 2026-04-26, pointing at then-current `bom.md` and `purchases.md`. Original prompt is preserved in the conversation log on that date.

## Items needing a fresh order

### Single-unit items (consumed 1:1 per appliance)

| BOM § | Item | ASIN | Qty | $ | Notes |
|---|---|---|---:|---:|---|
| §1 | ESP32-DevKitC-32E | B09MQJWQN2 | 1 | $11.00 | Main controller board |
| §1 | Meshnology ESP32-S3 1.28" rotary display | B0G5Q4LXVJ | 1 | $47.76 | UI display board |
| §1 | ESP32 DIN-rail breakout | B0BW4SJ5X2 | 1 | $25.99 | |
| §1 | MCP23017 I2C GPIO expander | B07P2H1NZG | 1 | $12.99 | |
| §1 | Mean Well IRM-90-12ST PSU | B0CNRST18V | 1 | $31.66 | LRS-200-12 alternate already on hand if BOM swap considered |
| §2 | Control Devices SV-100 PRV | B0D361X97X | 1 | $16.06 | |
| §3 | SEAFLO 22-Series 12 V pump | B0166UBJX4 | 1 | $48.25 | |
| §3 | John Guest 1/4"×1/8" NPT push-fit | B07V6XKZG9 | 1 | $5.00 | |
| §4 | Wellbom CO2 regulator | B0G13P5PMY | 1 | $44.99 | Forward-plan SKU; never ordered (TAPRITE B00L38DRD0 acquired is different) |
| §5 | Frigidaire ice-maker donor | B07PCZKG94 | 1 | $78.70 | **See caveats — alternate donor B0F42MT8JX may cover unit #1** |
| §5 | Supco SUD8358 drier | B009AX2O5W | 1 | $13.40 | |
| §8 | Kamoer KPHM400 pump | B09MS6C91D | 1 | $32.55 | 3 acquired, 2 in prototype, 1 left → need 1 more |
| §8 | Platypus 1 L SoftBottle bladder | B08PG3GMQ8 | 2 | $46.98 | All bladder variants consumed by prototype |
| §9 | Westbrass R2031-NL-62 8" Touch-Flo faucet | B07KH285GJ | 1 | $31.28 | Forward-plan SKU; never ordered |
| §9 | DIGITEN G3/8" Hall-effect flow sensor | B07QQW4C7R | 1 | $7.99 | Forward-plan SKU; G1/4" variants on hand are different |
| §12 | DEVMO MINI float switch (donor) | B07T18PGJ4 | 1 | $13.93 | |
| | **Single-unit subtotal** | | | **~$468.53** | |

### Pack purchases (cover prototype shortfall + future units)

| BOM § | Item | ASIN | $ | Notes |
|---|---|---|---:|---|
| §6 | Fiberglass Supply Depot 2 lb pour-in-place PU foam kit | B08R7TX8QJ | $39.99 | Long-standing LIKELY-TO-BUY; never ordered |
| §8 | Beduan 12 V solenoid valve (~10 more) | B07NWCQJK9 | ~$96.40 | BOM needs 12; ~3 on hand. Long-known shortage |
| §8 | PureSec TWS1414 Y splitter (10-pk) | B01N5I1ZJC | $7.99 | Forward-plan SKU; never ordered |
| §11 | Zip ties (200-pk) | B0BC1VH4XB | ~$6.00 | Forward-plan SKU; never ordered |
| | **Pack subtotal** | | **~$150.38** | |

**Grand total to fully provision unit #1: ~$618.91 + tax/ship.**

## Items confirmed sufficient for unit #1

Already covered, no order needed:

- **§1 Controllers/electronics:** Waveshare RP2040 LCD (qty 2), L298N 4-pack, ULN2803 10-pack, Teyleten relays (5-pack + 1 = 6 on hand)
- **§2 Vessel:** LTWFITTING 5-pack, FERRODAY sparge stone 2-set (1 left), Millrose PTFE tape, Tap Magic fluid, Cambro 6 QT (qty 2 across the ledger), 316L tube and endcap stock on order from OnlineMetals + SendCutSend
- **§3 Water inlet:** Hooshing 2-pack (1 left), Sealproof PVC, LOKMAN clamps 20-pack, MAACFLOW 4-pack, GASHER check valves (3 packs = 6 valves with the Apr 27 spares delivery), Lifevant tubing, John Guest bulkhead (qty 2, 1 left), Multiplex backflow preventers (5 on order across two vendors)
- **§4 CO2:** 5/16" CO2 line + clamps, DERPIPE 5-pack (4 left, but see caveats)
- **§5 Refrigeration:** GOORY 50 ft copper coil (1/2 roll left), DS18B20 5-pack (3 left), MXR C14 inlet 10-pack, Monoprice cord 6-pack, Enviro-Safe R-600a 3-pack (~12 charges), 3M 425 foil tape (12 builds per roll, on order)
- **§8 Flavor:** Pogo pin 2-pair (1 pair left), Platypus Hoser kit (qty 2, 1 left), 1/8" silicone tubing (qty 2, 1 roll left), Supply Depot BIB 2-pack (1 left)
- **§9 Dispensing:** VALVENTO compression 2-pack (1 left), VALVENTO 1/4" tube 5-pack (4 left)
- **§10 UI:** KRAUS air switch (qty 3, 2 left)
- **§11 Wiring:** Dupont jumpers 120-pack, female spade 60-pack, male spade 100-pack
- **§12 Level sensing:** Tandefio 1/8" 316 SS rod 5-pack (10 vessels per pack, on order), Gebildet reed switch 6-pack (4 left after prototype)

## Caveats / open questions

1. **Frigidaire donor — possible $78.70 savings.** purchases.md §6 has both **B07PCZKG94 Frigidaire** ($78.70) and **B0F42MT8JX generic** ($63.80), qty 1 each. The BOM specifies Frigidaire by ASIN, but the parts harvested (compressor / condenser / cap-tube / drier) are generic — the alternate donor should function equivalently. If the prototype consumed only one, the other is available for unit #1. Worth a visual confirmation of which donor is in the prototype before placing a third order.

2. **PETG filament inventory not measured.** BOM §7 estimates **8 kg per unit**. Bambu Lab orders include several PETG spools (Black ×4 in line 293, Translucent Clear ×4 in line 298, plus the founding-purchase color assortment) but exact remaining stock isn't tracked. If prototype consumed multiple kg, unit #1 may run short. Worth a physical spool count before assuming PETG is covered.

3. **DERPIPE 5/16" push-to-connect (B09LXVGPG7)** — flagged in BOM as delisted on Amazon. 4 left in the existing 5-pack covers unit #1, but plan a replacement SKU search before unit #2.

4. **Mean Well IRM-90-12ST vs LRS-200-12.** Both acquired (qty 1 each). If prototype is using the IRM-90 specified by the BOM, unit #1 needs another IRM-90 — or formally swap to the LRS-200 (already on hand but larger physical envelope per BOM §1 rationale). The IRM-90 at 190 cm³ vs LRS-200's 288 cm³ matters for under-counter packaging, so the BOM choice is intentional.

5. **Forward-plan SKU swaps need a "still the right pick?" review** before ordering:
   - **Wellbom B0G13P5PMY** regulator — vs TAPRITE E-T742 B00L38DRD0 already acquired ($96.47). If TAPRITE works, swap the BOM and save the $44.99 buy.
   - **Westbrass R2031-NL-62 B07KH285GJ** faucet — vs three other Westbrass SKUs already on hand (B0BXFW1J38, B01MZ6JPXW, B01N5LVNQA). Worth confirming the visual/feature delta justifies the swap.
   - **DIGITEN G3/8" B07QQW4C7R** flow sensor — vs G1/4" B07QRXLRTH and B07QS17S6Q already on hand. The thread size mismatch is real, but it's worth confirming whether a 3/8"→1/4" adapter would let the on-hand sensors work.

## What this snapshot is NOT

- Not a shopping list to act on right now (~1 month before unit-#1 order placement).
- Not a static record of the BOM — that's `bom.md`.
- Not a procurement decision document — that requires the SKU-swap review noted above and possible BOM updates first.
- Not maintained going forward. **When re-running this audit, generate a fresh dated snapshot rather than editing this one.**
