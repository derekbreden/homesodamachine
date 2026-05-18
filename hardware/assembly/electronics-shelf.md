# Electronics Shelf

The production procedure for the appliance's single electronics shelf — the bench-built assembly that carries every controller, driver, distribution block, and regulator on one panel behind the rear-panel C14 inlet. This document is the repeatable procedure for taking a printed shelf frame + the loose modules listed under "Inputs" to a fully populated, harnessed, pigtail-terminated shelf ready to drop into the enclosure top-back. Off-appliance bench build, runs in parallel with [`faucet-and-umbilical.md`](faucet-and-umbilical.md); both feed [`enclosure-mechanical.md`](enclosure-mechanical.md).

Topology lives in [`../wiring/power.mmd`](../wiring/power.mmd) (AC + 12 V), [`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd) (controller pin map), and [`../wiring/valve-control.mmd`](../wiring/valve-control.mmd) (MCP23017 + ULN2803A fan-out). Run-by-run gauges, lengths, and terminations live in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md). This document is the procedure that ties them together.

## Scope

In: all controllers (ESP32-DevKitC-32E, ESP32-S3 1.28" rotary display for config, MCP23017 ×2, ULN2803A ×2, L298N peristaltic-pump driver, Teyleten 3.3 V opto-isolated relays ×2, DS3231 RTC, Mean Well IRM-90-12ST PSU, 5 V regulator + 3.3 V regulator, Wago 221-413 lever blocks ×3 for AC distribution, a printed/screw DC distribution block, solid-copper ground bus, JST XH 4-pin / 6-pin / 9-pin connector kits, CQRobot bonded ribbon, Keszoox 50 cm pre-crimped silicone pigtails, 16 AWG appliance wire + 18 AWG hookup wire + crimp ferrules), and the printed electronics-shelf frame.

Out: one bench-built electronics shelf with every module mounted, the AC distribution block populated (H/N/G Wagos seated, three loads landed), the DC distribution block populated (12 V trunk in from PSU, branches to relay #2, L298N, ULN2803A pair, 5 V regulator, condenser-fan run), all module-to-module JST harnesses crimped and plugged, the ground bus prepared with a labeled ring-terminal landing per exposed-metal load, and AC + DC pigtails landed and labeled by run-ID — AC-1/2/3 stubs hanging long for the C14 inlet, AC-4/5/6 pigtails landed on relay #1 and the AC distribution block for compressor-side termination at [`wiring.md`](wiring.md), DC-1/4/6/8 trunk and branch stubs ready, and SIG headers ready to take the sensor harnesses. Unpowered.

Not in scope: physical install of the shelf into the enclosure top-back, including chassis-ground-stud landing — that is [`enclosure-mechanical.md`](enclosure-mechanical.md). Landing the AC pigtails into the C14 inlet's solder-tab pins and routing the AC-4/5/6 bundle through the compressor-shroud grommet — that is [`wiring.md`](wiring.md). Flashing firmware to the MCUs and first power-up — that is [`firmware-and-commissioning.md`](firmware-and-commissioning.md). The RP2040 round display does not appear here either; it ships with the under-counter faucet head per [`faucet-and-umbilical.md`](faucet-and-umbilical.md), and lands on the shelf's SIG-6 header during system integration.

## Inputs per appliance

Per-unit BOM lives in [`../bom.md`](../bom.md) §1 (controllers + electronics), §11 (wiring + JST kits + Wagos), §13 (heat-set inserts + M3 SHCS for module mounting). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost.

| Item | Source | Notes |
|---|---|---|
| ESP32-DevKitC-32E | B09MQJWQN2 | Main MCU; pin map in [`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd). Pre-mounted on its ESP32 DIN Rail Breakout (B0BW4SJ5X2). |
| ESP32 DIN Rail Breakout Board | B0BW4SJ5X2 | Carrier for the ESP32; provides the screw-terminal landing the inter-module JST headers solder back into. |
| Meshnology ESP32-S3 1.28" Rotary Display | B0G5Q4LXVJ | Config / BLE MCU; receives SIG-7 UART trunk from the ESP32. Sits on the shelf, not in the under-counter faucet head. |
| MCP23017 I²C GPIO expander ×2 | B07P2H1NZG ×2 | 0x20 (valves on PA + PB[0:3] + Reservoir A reeds on PB[4:7]) and 0x21 (Reservoir B reeds on PA[0:3] + condenser-fan low-side on PA4). Map in [`../wiring/valve-control.mmd`](../wiring/valve-control.mmd). |
| ULN2803A high-current driver module ×2 | B0F872W528 (2-pc) | Sinks 12 solenoid coils + condenser fan to GND; COM tied to 12 V via DC-6 for flyback. |
| L298N Dual H-Bridge | B0C5JCF5RS (1 of 4-pack) | Drives both Kamoer peristaltic pumps from MCP23017-adjacent ESP32 GPIO; pump cartridge lands at the manifold via pogo pins, not at the shelf. |
| Teyleten 3.3 V opto-isolated relay module ×2 | B07XGZSYJV (2 of 5-pack) | Relay #1 switches the compressor 120 VAC hot leg (ESP32 GPIO 14); relay #2 gates 12 V to the SeaFlo diaphragm pump (GPIO 4). Both stay on the shelf, outside the compressor shroud per [`../wiring/power.mmd`](../wiring/power.mmd). |
| DS3231 RTC | B01N1LZSK3 (1 of 5-pack) | I²C device at 0x68, co-located with the MCP23017s on the shared bus. |
| Mean Well IRM-90-12ST | B0CNRST18V | 80 W / 12 V / 6.7 A encapsulated PSU; IEC 60335-1 listed. Primary lands on the AC distribution block via AC-2; secondary feeds the DC distribution block via DC-1. |
| 5 V regulator + 3.3 V regulator | per [`../bom.md`](../bom.md) §1 | Regulated logic-level rails; 12 V → 5 V → 3.3 V cascade per [`../wiring/power.mmd`](../wiring/power.mmd) "Regulation". |
| Wago 221-413 lever-nut connector ×3 | per [`../bom.md`](../bom.md) §11 | AC distribution block — one Wago per conductor (H, N, G), each carrying one in-leg from the C14 pigtail and two out-legs (to PSU primary + to relay #1 contact input, plus ground branches). |
| DC distribution block | placeholder per [`../bom.md`](../bom.md) §11 | 12 V + and GND rails for the DC-2 / DC-4 / DC-6 / DC-8 / DC-9 fan-out from the PSU secondary. Hardware TBD — see Open items. |
| Solid-copper ground bus | per [`../bom.md`](../bom.md) §11 (16 AWG green stock) | Single chassis-ground tie point on the shelf. Receives PSU chassis ground (AC-2 G) and the C14 inlet's earth pin (AC-1 G); distributes to every exposed-metal load via short green pigtails. |
| JST XH 2.54 mm connector kits — 4-pin / 6-pin / 9-pin | B0B2RB524Y / B0B2R8Q1JL / B0B2R73RQB | Inter-module logic harnesses per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "Inter-module connectors": ~3× 4-pin (I²C + UART hops), ~1× 6-pin (DS3231 bus), ~6× 9-pin (ULN sides + MCP ports). |
| CQRobot bonded ribbon kit (15 cm × 12 cond × 8 ribbons) | B0F6C7X5CR | Short-hop module-to-module connections under ~6"; pre-crimped female XH terminals on both ends. |
| Keszoox 50 cm pre-crimped silicone pigtails (20 wires, 10 colors, 22 AWG) | B0F8HMQRRN | Cabinet-spanning runs; supplies the ULN→solenoid fan-out leads + sensor pigtails handed off to [`wiring.md`](wiring.md). |
| 16 AWG silicone-insulated appliance wire (black/white/green) | per [`../bom.md`](../bom.md) §11 | AC pigtail stock for AC-1 through AC-6. |
| 18 AWG stranded hookup wire | per [`../bom.md`](../bom.md) §11 | 12 V trunk + branch stock (DC-2/3/6/9). |
| Spade crimp terminals + ferrules + ring terminals | per [`../bom.md`](../bom.md) §11 (B0B9MZJ2ML + B01MZZGAJP) | AC pigtails land in Wago 221 lever blocks via crimp ferrules; the PSU primary and Teyleten contact terminals take crimp forks; the ground bus takes ring terminals. |
| Printed electronics-shelf frame | TBD (see Open items) | The structural panel the modules and distribution blocks mount on. PET-CF, M3 heat-set inserts (ruthex per [`../bom.md`](../bom.md) §13). |
| M3 heat-set inserts + M3 × 8/12 SHCS | per [`../bom.md`](../bom.md) §13 | Module mounting; exact screw lengths and per-module hole counts depend on the shelf CAD — see Open items. |

Tooling (per-unit-amortized only — single-asset tools live in [`../purchases.md`](../purchases.md), not here): Hakko FX-888D iron + T18 tip kit for the heat-set inserts and JST male-header solder pass (per [`../handwork.md`](../handwork.md) "Solder JST connectors"), ESD mat, ferrule crimper, JST XH crimper, ring/fork-terminal crimper, helping hands, multimeter for AC-side continuity and DC-side polarity checks.

## Procedure

### 1. Prepare the printed shelf frame

Heat-set M3 inserts into every mounting boss on the printed shelf per its CAD source. Verify each insert is flush with the boss face; an insert proud of the face will preload the module against the boss instead of the screw face, which over a thermal cycle can crack the module's PCB at the mounting hole.

Module placement geometry on the shelf is set by the shelf STL — see Open items. The bench step here is purely insert prep + visual check; no modules touch the shelf yet.

### 2. Solder JST XH male headers to module carriers

Per [`../handwork.md`](../handwork.md) "Solder JST connectors". Hakko station, 60/40 leaded, ESD mat. Pin-count assignments per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "Inter-module connectors":

- **4-pin** — I²C trunk (ESP32 ↔ MCP23017 ×2 ↔ DS3231 on the shared bus; one header on each carrier), UART trunk to the ESP32-S3 on the shelf, and the SIG-6 UART header that will accept the RP2040's Cat6 pigtail at system integration.
- **6-pin** — DS3231 RTC carrier (VCC / GND / SDA / SCL / SQW / 32K).
- **9-pin** — ULN2803A modules × 2 (each gets two 9-pin headers, one per Darlington row of 8 channels + COM/GND) and MCP23017 modules × 2 (each gets two 9-pin headers, one per Port A / Port B row of 8 GPIO + reference).

After every module's headers are in, leave the modules off-shelf on the ESD mat. They mount in step 4 after the AC + DC distribution is staged.

### 3. Stage the AC distribution block + ground bus

Mount the three Wago 221-413 lever blocks in their bays on the shelf — one each for H, N, G. Label each block at its bay (H / N / G is not visually distinguishable on the Wago itself; label tape or printed shelf bay-callouts).

Cut and prep the 16 AWG appliance-wire pigtails for AC-1 through AC-6 per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "AC mains" table:

- **AC-1** — ~50 mm pigtails on H, N, G with ferrules crimped on the load-side end and the inlet-side end left long (~150 mm slack) for the C14 inlet's solder-tab terminations during [`wiring.md`](wiring.md). Label each conductor "AC-1 H" / "AC-1 N" / "AC-1 G" with heat-shrink flags so the [`wiring.md`](wiring.md) installer doesn't have to ohm them out.
- **AC-2** — H + N + G pigtails from the H / N / G Wago blocks to the PSU primary terminals, ~100 mm, ferrules at the Wago end, crimp forks at the PSU end.
- **AC-3** — H pigtail from the H Wago block to the relay #1 contact input ("common" terminal), ~50 mm, ferrule one end, crimp fork the other.
- **AC-4/5/6** — pigtails from the relay #1 contact output (AC-4 switched H, ~400 mm), the N Wago block (AC-5, ~400 mm), and the ground bus (AC-6, ~400 mm). Each carries a female disconnect at the compressor-side end and is left coiled with a labeled flag — these get routed through the compressor-shroud grommet at [`wiring.md`](wiring.md), not now.

Land the solid-copper ground bus on its mounting boss. Stage short green 16 AWG pigtails with ring terminals at the bus end for each exposed-metal load: PSU chassis (lands at PSU mounting in step 4), pressure vessel, faucet SS plate, compressor body / shroud, BiB adapter plate. Leave the load-side end of each pigtail un-terminated and labeled — those lands happen at [`wiring.md`](wiring.md). The bus-to-chassis stud connection itself happens at [`enclosure-mechanical.md`](enclosure-mechanical.md).

### 4. Mount all modules + PSU on the shelf

Place each module on its boss pattern, M3 × 8 SHCS through the module PCB into the heat-set insert. Torque by feel — snug, no PCB flex. Mount sequence top-down by bay:

1. **Mean Well IRM-90-12ST PSU** — largest part on the shelf, gets seated first so its terminal block is accessible for AC-2 landing in step 5.
2. **Teyleten relay #1** (compressor switch) and **Teyleten relay #2** (diaphragm-pump switch) — close to the PSU so AC-2 + AC-3 and DC-1 + DC-2 are short, clean runs.
3. **ESP32-DevKitC-32E** (on its DIN-rail breakout) and **ESP32-S3 rotary display** — controllers cluster on the logic side of the shelf, away from the PSU's switching-noise zone.
4. **MCP23017 × 2** — co-located with the ESP32 for the short I²C trunk.
5. **DS3231 RTC** — same I²C bus, same neighborhood as the MCP23017s.
6. **ULN2803A × 2** — adjacent to the MCP23017s on one side, oriented so the 12 V COM pins face the DC distribution block and the channel outputs face the bay where the Keszoox solenoid-fan-out pigtails will route off the shelf.
7. **L298N pump driver** — separate bay so its inductive load decoupling stays clear of the logic clusters.
8. **5 V regulator + 3.3 V regulator** — between the PSU and the logic cluster on the 12 V → 5 V → 3.3 V cascade path.

The MCUs go on the shelf bare — no firmware. Pre-flash happens at [`firmware-and-commissioning.md`](firmware-and-commissioning.md).

### 5. Land AC pigtails into the distribution block + PSU + relay #1

Open each Wago 221-413 lever and seat the staged ferrules. Each block carries one in-leg (the AC-1 conductor from the C14 inlet) plus the out-legs called out in [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md):

- **H Wago** — AC-1 H in; AC-2 H out to PSU primary; AC-3 H out to relay #1 contact input.
- **N Wago** — AC-1 N in; AC-2 N out to PSU primary; AC-5 N out left coiled with its labeled flag (compressor-side disconnect terminated, lands during [`wiring.md`](wiring.md)).
- **G Wago** — AC-1 G in; AC-2 G out to the PSU chassis ground stud; AC-6 G out to the ground bus, which carries the compressor-shroud bond branch (also left coiled with its labeled flag).

Lock down each Wago lever. Multimeter-check each wago bay for continuity from the AC-1 stub to every named out-leg (the wago side; the loads are still unpowered).

Land AC-2 forks on the PSU primary screw terminals. Land AC-3 fork on relay #1's contact-input terminal ("COM" on the Teyleten silkscreen). Verify the relay's other contact terminal ("NO") has the AC-4 switched-H pigtail crimped on with its compressor-side disconnect already in place from step 3.

### 6. Stage the DC distribution block + populate the 12 V branches

Mount the DC distribution block on its boss pattern. Land the DC-1 pair (PSU 12 V + and GND, 16 AWG, ~100 mm, crimp forks at the PSU and ferrules at the distribution block).

Land the branches per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "12 V distribution":

- **DC-2** — 16 AWG 12 V + to relay #2 contact input; the contact-output pigtail (DC-3) is left coiled with a labeled flag and a female disconnect for the SeaFlo pump landing during [`wiring.md`](wiring.md).
- **DC-4** — 22 AWG + and GND to the L298N motor-driver VS / GND screw terminals.
- **DC-6** — 18 AWG + to each ULN2803A COM pin (one branch per ULN module, two total). This is the flyback rail for the solenoid + condenser-fan inductive loads.
- **DC-8** — 22 AWG + and GND to the 5 V regulator input pins.
- **DC-9** — 22 AWG + pair pigtail with a female disconnect at the fan-side end, left coiled with a labeled flag for the condenser-fan landing during [`wiring.md`](wiring.md). The ULN-sink return is part of the U2-channel-5 fan-out in step 7.

### 7. Crimp + plug the inter-module JST harnesses

Build the logic-side harnesses module-to-module from the JST kits + bonded ribbon + Keszoox pigtails. Standard build order: I²C trunk first (shortest, exercises the crimper warm-up), UART hops next, then the wider ULN-MCP bus, then the off-shelf fan-out pigtails.

- **I²C trunk** — 4-pin XH bonded ribbon from ESP32 GPIO 21/22 + 3.3 V + GND, daisy-chained through the DS3231, both MCP23017s. Headers seat at each device; pull-ups on the bus are on the MCP23017 breakouts (no external resistors needed on the shelf).
- **UART hops** — 4-pin XH bonded ribbon ESP32 ↔ ESP32-S3 (GPIO 15 TX / 34 RX + 5 V + GND, per SIG-7). A second 4-pin XH header on the ESP32 (GPIO 32 TX / 35 RX + 5 V + GND, per SIG-6) is plugged but its other end stays open — that's the SIG-6 trunk that lands on the RP2040 round display at system integration via the Cat6 run.
- **MCP23017 → ULN2803A** — 9-pin XH ribbons, two per MCP (one per port). Port A of 0x20 trunks straight into ULN #1's 8-channel input row; Port B[0:3] of 0x20 lands on ULN #2 inputs 1-4. Port A[4] of 0x21 lands on ULN #2 input 5 (the condenser-fan channel). The Reservoir A reed inputs on 0x20 PB[4:7] and Reservoir B reed inputs on 0x21 PA[0:3] terminate at JST headers at the edge of the shelf — those plug into the Keszoox pigtails that route to the reservoir-mounted reeds at [`wiring.md`](wiring.md).
- **ULN2803A → off-shelf solenoids + condenser fan** — 12 × Keszoox 50 cm pre-crimped pigtails crimped into the ULN outputs (8 from ULN #1, 4 from ULN #2 channels 1-4) and one more for the condenser-fan return (ULN #2 channel 5). Each pigtail's far end terminates in a female disconnect for the manifold valves or the fan motor; they leave the shelf as a single bundled run for the valve manifold + a single pigtail for the fan, both labeled.
- **L298N control** — Dupont female on the ESP32 side (GPIO 33/25/26 for pump A, 19/18/5 for pump B per [`../wiring/esp32-pinout.mmd`](../wiring/esp32-pinout.mmd)) into the L298N's IN1-IN4 + ENA/ENB pin header. OUT-A and OUT-B are not crimped here — those land on the peristaltic-pump cartridge via pogo pins at the manifold during [`wiring.md`](wiring.md).
- **3.3 V relay control (LV-1, LV-2, LV-3)** — Dupont female on the ESP32 side (GPIO 14 → relay #1 IN, GPIO 4 → relay #2 IN). LV-3 is a short 5 V + GND pigtail from the 5 V regulator to each relay module's VCC pin (the opto-isolation keeps the coil supply electrically separate from logic).

### 8. Stage the sensor (SIG) pigtails as labeled off-shelf stubs

Per [`../wiring/ac-wiring-schedule.md`](../wiring/ac-wiring-schedule.md) "Sensors and signal", crimp a Keszoox pigtail for each SIG-N run with the shelf-side end terminated in its JST XH housing (already soldered onto the appropriate ESP32 GPIO during step 2), and the load-side end left bare with a labeled heat-shrink flag identifying the run by ID (SIG-1 DS18B20 bus, SIG-2/3 reeds, SIG-4 flow meter, SIG-5 air switch, SIG-6 RP2040, SIG-7 S3 config, SIG-8 I²C — already done in step 7 — SIG-9 backflow moisture). The load-side terminations happen at [`wiring.md`](wiring.md) once each sensor is in its final location.

The 4.7 kΩ DS18B20 pull-up resistor (between SIG-1 data and 3.3 V) is installed at the ESP32 end, not at the probe end, during this step.

### 9. Pre-power continuity + isolation check

Before the shelf leaves the bench, unpowered:

- AC side: continuity from each AC-1 pigtail (C14-stub end) through its Wago block to every named out-leg, including the long compressor-side coils. Confirm no continuity between the H bus and the G bus, the N bus and the G bus, or the H bus and the N bus.
- DC side: continuity from each DC-1 trunk pair through the distribution block to every named branch. Confirm correct polarity at each branch (the L298N + ULN modules are polarity-sensitive on the COM rail).
- Ground bus: continuity from every ring-terminal pigtail on the bus back to the AC-1 G stub.
- I²C trunk: visual check that every JST is fully seated and oriented correctly.

The shelf does not get powered at this stage. First power-on happens at [`firmware-and-commissioning.md`](firmware-and-commissioning.md), after the shelf is installed and the chassis-ground stud is bonded.

## Output condition

A finished electronics shelf is:

- Fully populated — every module from the inputs table mounted on its boss pattern, ESD-handled, screws torqued by feel
- AC distribution block landed with the three Wago 221-413 levers locked, AC-2 + AC-3 internal stubs terminated at the PSU primary and relay #1 contact input
- DC distribution block landed with the DC-1 trunk from the PSU and DC-4 / DC-6 / DC-8 internal stubs terminated at the L298N, ULN2803A pair, and 5 V regulator
- Inter-module JST harnesses crimped and plugged — I²C, both UART trunks, MCP-to-ULN ports, L298N control, relay control
- Ground bus mounted, bus-side ring terminals seated for every exposed-metal load, load-side ends left long with labeled flags
- AC-1 (H/N/G), AC-4/5/6 (compressor-side), and DC-3 (diaphragm pump) and DC-9 (condenser fan) pigtails coiled with labeled heat-shrink flags identifying the run-ID — ready to be picked up by [`wiring.md`](wiring.md)
- SIG-1 through SIG-9 sensor pigtails crimped, shelf-side seated, load-side ends labeled, DS18B20 pull-up installed at the ESP32 end
- Pre-power continuity and isolation checks passed (AC bus separation, DC polarity, ground continuity)
- Unpowered — MCUs unflashed, no first-power yet

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Printed electronics-shelf frame.** STL / CadQuery source is not yet committed under [`../printed-parts/enclosure/`](../printed-parts/enclosure/) (sibling to `back-panel/` and `nameplate/`). The frame's overall envelope, mounting-boss layout for each module, AC-distribution + DC-distribution bays, ground-bus boss, and the wire-egress paths off the shelf all need to be specified in CAD before this procedure can run on unit 1. Module placement order in step 4 is descriptive of the intended grouping (PSU near relays, MCUs near I²C devices, ULN outputs near the manifold-side wire egress) but the actual geometry follows the frame STL.
2. **PCB / breakout mounting hardware.** M3 standoff heights for each module (the ESP32 DIN-rail breakout, the MCP23017 carriers, the Teyleten relay modules, the ULN2803A carriers, the L298N) are not yet in [`../bom.md`](../bom.md) §13. Working assumption: M3 × 4 ruthex inserts in the printed shelf, M3 × 8 mm SHCS direct into the boss for low-profile modules, with brass or nylon standoffs (3 mm or 5 mm) inserted between the boss and the PCB on any module whose underside has exposed solder joints. Commit a standoff SKU + per-module count once the shelf CAD lands.
3. **DC distribution block hardware.** The AC side commits to Wago 221-413 lever blocks (3 per build, [`../bom.md`](../bom.md) §11), but the 12 V distribution block is a placeholder — a screw-terminal block, a Wago 221-415 5-conductor variant, or a small PCB-mounted distribution bar are all defensible. Pick after the shelf CAD lands and the bay it occupies is sized.
4. **Shelf frame material thickness.** PET-CF is the working-assumption material consistent with the rest of the enclosure ([`../future.md`](../future.md) "Other metal candidates considered, decided against"). The shelf carries no AC-arc-flash duty (the relay #1 arc happens inside its enclosed Teyleten module), so a structural panel thickness of 3-4 mm at 30-40 % infill is plausible — confirm once the heaviest module (the Mean Well IRM-90-12ST PSU at ~200 g) is staged against the candidate frame.
