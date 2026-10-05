# Gun positioner: owned stock and tools

What the gun positioner and its camera stages take from stock Derek already owns, what they
must leave alone, and what the purchase list in [`prime-verified.json`](prime-verified.json)
adds. Checked 2026-10-04 against [`purchases.md`](../../ledger/purchases.md),
[`tools.md`](../../ledger/tools.md) and [`inventory.md`](../../ledger/inventory.md).

The ledger records 2026 purchases and does not track what is left in a pack or on a spool, so
the counts below are pack counts less the uses the repository records.

## Taken from stock

| Item | Use in this build | Ledger ASIN |
|---|---|---|
| BNTECHGO 18 AWG silicone wire, red 25 ft + black 25 ft (no other role) | 24 V motor distribution | [B07HGTKQ89](https://www.amazon.com/dp/B07HGTKQ89) |
| BNTECHGO 24 AWG silicone, 100 ft (free); KWANGIL 22 AWG 12-conductor jacketed cable, 25 ft (free) | Limit, overload and STOP loops, each signal twisted with its own GND return | [B01K4TLR1W](https://www.amazon.com/dp/B01K4TLR1W), [B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21) |
| BNTECHGO 22 AWG silicone black, 250 ft (production uses about 30 ft per build) | Short signal jumpers | [B06Y2PNW41](https://www.amazon.com/dp/B06Y2PNW41) |
| Preciva ferrule kit, spade and ring kits, crimpers, heat-shrink, sleeving | Harness termination | [B0DS622GKN](https://www.amazon.com/dp/B0DS622GKN) and the crimp-tool rows in `tools.md` |
| WAGO 221 lever connectors; 2.54 mm and 5.08 mm screw terminals | Bench distribution and test leads | [B07W7W91FX](https://www.amazon.com/dp/B07W7W91FX), [B0FHGXX6SK](https://www.amazon.com/dp/B0FHGXX6SK), [B093DL8DKC](https://www.amazon.com/dp/B093DL8DKC) |
| M3 washers, Ø7, 200 (no other role) | 64 rail-base washers on the camera stages | [B0F9KKJ22M](https://www.amazon.com/dp/B0F9KKJ22M) |
| HiLetgo DS18B20 1 m stainless probes, 5 (bench spares) | Motor-case and driver-heatsink logging alongside the dual-K thermometer | [B00M1PM55K](https://www.amazon.com/dp/B00M1PM55K) |
| Neoteck 0.0005 in dial test indicator and magnetic base (shared with the weld rotator) | Creep screen, runout of the friction faces, spring grading on the drill press | [B09W2R3SCD](https://www.amazon.com/dp/B09W2R3SCD) |
| Smart Weigh 2000 g × 0.1 g scale (shared) | Weighing the hanging masses for the 100 mm torque lever | [B00IZ1YHZK](https://www.amazon.com/dp/B00IZ1YHZK) |
| NEIKO 0–6 in caliper; AstroAI multimeter | Fit checks; meter-before-power gate | [B000GSLKIW](https://www.amazon.com/dp/B000GSLKIW), [B071JL6LLL](https://www.amazon.com/dp/B071JL6LLL) |
| WEN 4208T drill press; WEN BA4555 band saw with 24 TPI M42 blade | Plate and shaft drilling, spring and link testing under the quill; cutting screws, rod, bar and extrusion | [B08ZVT5JKC](https://www.amazon.com/dp/B08ZVT5JKC), [B09XWQCNGT](https://www.amazon.com/dp/B09XWQCNGT) |
| Noga deburr tool; Hakko FX-888D with T18 insert tips (M2–M8); C-clamps; DeWalt and Ryobi drill/drivers | Deburring, inserts, clamping | [B0D4DJW54S](https://www.amazon.com/dp/B0D4DJW54S), [B0CS662NVK](https://www.amazon.com/dp/B0CS662NVK) |
| Revopoint MINI 2 scanner (shared) | Scanning the gun body for its clamp shell | [B0FPX92DG3](https://www.amazon.com/dp/B0FPX92DG3) |
| Bambu H2C printers; free PET-CF17, Bambu PET-CF and PETG-CF spools; TPU and PEBA for pads | Printed parts and pads | `purchases.md` filament rows |
| SunTop clear PETG, 2 × 1 kg (a reservoir-filament candidate; the reservoirs print in Bambu PETG) | Controller backplane 300 × 300 × 6 mm, 28 insulating spacers and the fan stand: unfilled stock, so the panel does not rely on carbon-filled filament as an insulator | [B0FP34MJ94](https://www.amazon.com/dp/B0FP34MJ94) |

## Left alone

| Item | Committed to |
|---|---|
| NEMA 23 + DM542T kit, BTF-LIGHTING 24 V 4 A adapter, 5 V adapter, HimaPro pedal, ESP32 with breakout and ULN2803A, HTD-5M belt and pulley, the rotator's inserts and screws | The weld rotator. The positioner has its own 24 V supply, controller and stop. |
| ELP 16 MP camera and SMALLRIG arm | The panelcam. The camera stages use the two FoMaKo cameras. |
| Polymaker PET-GF15 | Production exterior parts, about 6.15 kg per build. Positioner prints come from the free spools. |
| BNUOK M3×25, M3×8, M5×10 | Production. |
| Hgnova 1064 nm protective windows | The X1 Pro head. |

## Bought for this build

None of these is on hand; [`prime-verified.json`](prime-verified.json) lists each verified
listing, pack, quantity and price:

- Motion and controls: NEMA17 motors, TMC2209 drivers, Pico, 24 V and 5 V supplies, relay,
  stop and its enclosure, limit and overload switches, fuses, connectors, terminal blocks,
  capacitors and resistors (the 4.7 k / 2.2 k / 3.3 kΩ stock does not cover the 10 kΩ, 1 kΩ
  and 100 kΩ values; the owned 470 µF capacitors are rated 25 V).
- Mechanics: SBR12 rails, TR8×2 screws and nuts, KP08 and KP001 bearings, F8-16M thrust
  and F688ZZ flanged bearings, GT2 pulleys and belts, 304 shaft, springs, bushings, all
  aluminum plate, square bar, angle, tube and extrusion, and the corner brackets.
- Fasteners: every bolt, nut, washer and T-nut, one shared pack per size for the mechanism,
  both camera stages and the controller panel. The 64 camera rail-base washers above come
  from stock.
- Cameras: both FoMaKo cameras and Raynox lenses, switch, hub, cables, lights.
- Shop tools the ledger does not record: metric cobalt drills, 4.2 mm cobalt drills, 12 mm
  reamer, drill-press vise, transfer punches, centre punch, metric hex keys, feeler gauges,
  jigsaw with aluminum blades, 500 N force gauge, dual-K thermometer, cobalt spiral-flute M5
  tap with a small T-handle tap wrench (the owned DWT wrench starts at 1/4 in), certified
  torque screwdriver with metric hex bits, Loctite 243, PTFE grease, cutting fluid.
- Reference weights for the 0.1 g scale (1 kg OIML M1 and a 1000 g M2 set). The ledger
  records no weight with the scale.
