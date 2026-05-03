# Handwork

Skilled-hand tasks on the path to a finished unit. One person, one unit at a time — the Founder Edition cadence ([target-market.md](../marketing/target-market.md)).

Companion to [bom.md](bom.md) (per-unit parts) and [purchases.md](purchases.md) (every dollar out, with founder time explicitly excluded — "sweat equity, un-booked by design").

Order isn't strict — pressure-testing waits on tap + weld being complete on the same vessel; the others run independently.

## Solder JST connectors to boards

Solder male JST-XH 2.54 mm headers to the carrier boards so the field-crimped female housings (loose terminals + bonded ribbons + Keszoox pre-crimped pigtails) can plug in. Three pin counts per [bom.md §11](bom.md):

- **4-pin** (B0B2RB524Y) — I2C and UART hops between modules (ESP32 ↔ MCP23017, ESP32 ↔ ESP32-S3 UART, ESP32 ↔ RP2040 UART), ~3 connectors per unit.
- **6-pin** (B0B2R8Q1JL) — DS3231 RTC (VCC/GND/SDA/SCL/SQW/32K), ~1 connector per unit.
- **9-pin** (B0B2R73RQB) — ULN2803A module sides (8 channels + COM/GND) and MCP23017 Port A/B rows, ~6 connectors per unit.

Hakko station, 60/40 leaded solder, ESD mat — all already in [purchases.md §14](purchases.md).

## Bend copper around the pressure vessel

Wind the GOORY 1/4" OD × 0.031" wall ACR copper tubing tight around the vessel OD as the evaporator coil. The 0.031" wall resists kink at the bend radius required around the 5" OD vessel. Single-layer wrap at ~1/8" pitch yields ~22 ft of wrap per vessel + ~2 ft each end for compressor and suction-line tie-ins ([bom.md §5](bom.md)). Bonded to the tank OD with 3M 425 aluminum foil tape — applied as a continuous skin under the coil so the tape spans the tank ↔ coil thermal interface ([future.md](future.md) "Refrigeration subsystem").

## Tap NPT in 316L end caps

Hand-tap 1/4"-18 NPT directly into the 1/4"-thick laser-cut 316L end-cap plates from SendCutSend (`endcap-circular-2hole.dxf`). 2 ports per plate × 2 plates per vessel × 10 vessels of stock = 40 holes. Tap Magic EP-Xtra cutting fluid; Drill America HSS pipe tap; Brown & Sharpe spring-loaded tap guide on the WEN drill press; Drill America DWT adjustable tap wrench for the hand drive. The committed plan for the first hole is [tapping-plan-2026-05-03.md](tapping-plan-2026-05-03.md); the remaining 39 follow once that one proves the fixture and the feel.

## Weld 316L end caps to 316L tubes

Join the 1/4"-thick 316L end-cap plates to the 5" OD × 0.065" wall 316L tube ends with the XLaserlab X1 Pro handheld laser welder, STARTECHWELD ER316L .030 filler (matches the 316L parent metal — undermatching with 308L would lose the molybdenum across the joint). Top + bottom plates per vessel × 10 vessels of stock. The 1/8" 316L float rod (Tandefio B0CY4DWJFQ, cut to ~6") tack-welds vertically to the inside face of the bottom plate as part of this same operation, before the bottom-plate-to-tube weld closes the vessel ([future.md](future.md) "Level sensing").

## Pressure-test 316L vessels

Hydro-test each fully welded + tapped vessel to 150 PSI for 30 minutes (~2× the 70 PSI working pressure). Done after tapping and welding are both complete on a given vessel. Beyond the 30-min hydro-test minimum, an in-vessel pressure-test gauge (LIKELY-TO-BUY in [purchases.md](purchases.md)) supports hour-scale leak soaks for catching slow weep before passivation and service.
