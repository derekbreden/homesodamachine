# Handwork

Skilled-hand tasks on the path to a finished unit. One person, one unit at a time — the Founder Edition cadence ([target-market.md](/marketing/target-market.md)).

Companion to [bom.md](/hardware/ledger/bom.md) (per-unit parts) and [purchases.md](/hardware/ledger/purchases.md) (every dollar out, with founder time explicitly excluded — "sweat equity, un-booked by design").

Order isn't strict — pressure-testing waits on tap + weld being complete on the same vessel; the others run independently.

## Solder JST connectors to boards

Solder male JST-XH 2.54 mm headers to module pin-header rows so field-crimped female housings (loose terminals + bonded ribbons + Keszoox pre-crimped pigtails) plug in. Rule of thumb: **JST-XH every module-to-module logic connection that lands on pin headers; leave screw-terminal connections as-is** — they're already vibration-secure (the ESP32 DIN-rail breakout's terminals, the L298N power/motor terminals, the Teyleten relay modules' in/out terminals). Some boards ship their headers **pre-soldered** (MCP23017 GPIO rows, L298N control row) — desolder the stock pins first, then solder the XH header; the ULN2803A ships its headers **loose**, so its XH headers solder straight on. Four pin counts per [bom.md §11](/hardware/ledger/bom.md):

- **4-pin** (B0B2RB524Y) — the 4-wire I²C / UART hops: the DS3231 RTC's I²C (VCC/GND/SDA/SCL — SQW/32K unused) and the UART trunk to the front-face ESP32-S3 display. ESP32 ends land on the DIN-breakout screw terminals; the MCP23017 I²C side is **PH2.0**, not XH. ~3 connectors per unit.
- **6-pin** (B0B2R8Q1JL) — L298N control row (ENA / IN1 / IN2 / IN3 / IN4 / ENB), the six lines driving the two peristaltic pumps. ~1 connector per unit.
- **9-pin** (B0B2R73RQB) — ULN2803A module sides (8 channels + COM/GND); 2 ULNs × 2 sides, ~4 connectors per unit.
- **10-pin** (B0B2R93CV3) — MCP23017 Port A/B GPIO rows (**VCC + GND + 8 GPIO**). The row is 10 holes, so a 10-pin fills it and can't seat off-by-one; a 9-pin would drop VCC and float on the row. ~4 per unit.

Hakko station, 60/40 leaded solder, ESD mat — all already in [purchases.md §14](/hardware/ledger/purchases.md).

## Bend copper around the pressure vessel

Wind the GOORY 1/4" OD × 0.031" wall ACR copper tubing tight around the vessel OD as the evaporator coil. The 0.031" wall resists kink at the bend radius required around the 5" OD vessel. Single-layer wrap at ~1/8" pitch yields ~22 ft of wrap per vessel + ~2 ft each end for compressor and suction-line tie-ins ([bom.md §5](/hardware/ledger/bom.md)). Bonded to the tank OD with 3M 425 aluminum foil tape — applied as a continuous skin under the coil so the tape spans the tank ↔ coil thermal interface ([future.md](/hardware/future.md) "Refrigeration subsystem").

See [assembly/refrigerant-loop.md](/hardware/assembly/refrigerant-loop.md) step 4 for the production-procedure framing.

## Tap NPT in 316L end caps

Hand-tap 1/4"-18 NPT directly into the 1/4"-thick laser-cut 316L end-cap plates from SendCutSend (`endcap-circular-2hole.dxf`). 2 ports per plate × 2 plates per vessel × 10 vessels of stock = 40 holes. Tap Magic EP-Xtra cutting fluid; LingGan M35 cobalt 1/4-18 NPT pipe tap (HSS-E, wears slower on stainless than plain HSS); Brown & Sharpe spring-loaded tap guide on the WEN drill press; Drill America DWT adjustable tap wrench for the hand drive. The committed plan for the first hole is [tapping-plan-2026-05-03.md](/hardware/snapshots/tapping-plan-2026-05-03.md); the remaining 39 follow once that one proves the fixture and the feel.

See [assembly/pressure-vessel.md](/hardware/assembly/pressure-vessel.md) step 1 for the production-procedure framing.

## Weld 316L end caps to 316L tubes

Join the 1/4"-thick 316L end-cap plates to the 5" OD × 0.065" wall 316L tube ends with the XLaserlab X1 Pro handheld laser welder, STARTECHWELD ER316L .030 filler (matches the 316L parent metal — undermatching with 308L would lose the molybdenum across the joint). Top + bottom plates per vessel × 10 vessels of stock. The 1/8" 316L float rod (Tandefio B0CY4DWJFQ, cut to [131.1 mm (5.16 in)](ROD_LEN)) tack-welds vertically to the inside face of the bottom plate as part of this same operation, before the bottom-plate-to-tube weld closes the vessel ([future.md](/hardware/future.md) "Level sensing").

See [assembly/pressure-vessel.md](/hardware/assembly/pressure-vessel.md) steps 2-5 for the production-procedure framing.

## Cut + seat the reservoir float rods

Cut two 1/8" 316L SS rods — one per flavor reservoir — to [174 mm (6.85 in)](RESERVOIR_ROD_LEN) from the same Tandefio B0CY4DWJFQ stock as the carbonator float rod. Same square-cut-and-deburr discipline. Unlike the carbonator rod these are **not welded**: each is captured by printed PETG bosses at both ends. Seat the bottom end in the standing body-boss blind bore on the reservoir BODY wet slope, slip the harvested DEVMO MINI donut float (B07T18PGJ4) over the rod, and let the cap-side register boss capture the top end as the reservoir cap is installed. The cut length already backs off the body-boss-floor-to-cap-boss seat-to-seat span for clearance (per `reservoir.py`), so the rod locates without ever holding the cap off its gasket.

See [reservoir/level-sensing.md](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) for the rod / float / reed geometry and [assembly/cold-core.md](/hardware/assembly/cold-core.md) (reservoir-internal assembly) for where this sits in the cold-core build.

## Pressure-test 316L vessels

Hydro-test each fully welded + tapped vessel to 180 PSI for 30 minutes (~2× the 90 PSI working pressure). Done after tapping and welding are both complete on a given vessel. Beyond the 30-min hydro-test minimum, the in-vessel SENCTRL pressure-test gauge (B0BCHMQLFB, ACQUIRED in [purchases.md](/hardware/ledger/purchases.md) §1) supports hour-scale leak soaks for catching slow weep before passivation and service.

See [assembly/pressure-vessel.md](/hardware/assembly/pressure-vessel.md) step 6 for the production-procedure framing, including the rig + criteria + failure-handling gaps still open.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_handwork_sync.py`
