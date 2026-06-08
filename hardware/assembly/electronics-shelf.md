# Electronics Shelf

The production procedure for the appliance's single electronics shelf — the bench-built assembly that carries every controller, driver, distribution block, and regulator on one panel behind the rear-panel C14 inlet. Feeds [`enclosure-mechanical.md`](enclosure-mechanical.md) alongside [`faucet-and-umbilical.md`](faucet-and-umbilical.md).

Topology lives in [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd) (AC + 12 V), [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) (controller pin map), and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd) (MCP23017 + ULN2803A fan-out). Run-by-run gauges, lengths, and terminations live in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

## Scope

In: all controllers (ESP32-DevKitC-32E, MCP23017 ×2, ULN2803A ×2, L298N peristaltic-pump driver, Teyleten 3.3 V opto-isolated relays ×2, DS3231 RTC, Mean Well IRM-90-12ST PSU, Legrand 1597BKCCD12 GFCI module, 5 V regulator + 3.3 V regulator, Wago 221-413 lever blocks ×3 for AC distribution, a printed/screw DC distribution block, solid-copper ground bus, JST XH 4-pin / 6-pin / 9-pin connector kits, CQRobot bonded ribbon, Keszoox 50 cm pre-crimped silicone pigtails, 16 AWG appliance wire + 18 AWG hookup wire + crimp ferrules), and the printed electronics-shelf frame.

Out: one bench-built electronics shelf with every module mounted, the AC distribution block populated (H/N/G Wagos seated, three loads landed), the DC distribution block populated (12 V trunk in from PSU, branches to relay #2, L298N, ULN2803A pair, 5 V regulator, condenser-fan run), all module-to-module JST harnesses crimped and plugged, the ground bus prepared with a labeled ring-terminal landing per exposed-metal load, and AC + DC pigtails landed and labeled by run-ID — AC-1a (H/N/G) stubs hanging long for the C14 inlet, AC-1b internal to the shelf between the GFCI and the Wagos, AC-4/5/6 pigtails landed on relay #1 and the AC distribution block for compressor-side termination at [`wiring.md`](wiring.md), DC-1/4/6/8 trunk and branch stubs ready, and SIG headers ready to take the sensor harnesses. Unpowered.

Not in scope: physical install of the shelf into the enclosure top-back, including chassis-ground-stud landing — that is [`enclosure-mechanical.md`](enclosure-mechanical.md). Landing the AC pigtails into the C14 inlet's solder-tab pins and routing the AC-4/5/6 bundle through the compressor-shroud grommet — that is [`wiring.md`](wiring.md). Flashing firmware to the MCUs and first power-up — that is [`firmware-and-commissioning.md`](firmware-and-commissioning.md). The ESP32-S3 rotary display lives on the front face per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md); its UART trunk (SIG-7) lands on the shelf-side header at system integration.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/bom.md`](/hardware/bom.md) §1 (controllers + electronics), §11 (wiring + JST kits + Wagos), §13 (heat-set inserts + M3 SHCS for module mounting).

| Item | Source | Notes |
|---|---|---|
| ESP32-DevKitC-32E | B09MQJWQN2 | Main MCU; pin map in [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd). Pre-mounted on its ESP32 DIN Rail Breakout (B0BW4SJ5X2). |
| ESP32 DIN Rail Breakout Board | B0BW4SJ5X2 | Carrier for the ESP32. |
| MCP23017 I²C GPIO expander ×2 | B07P2H1NZG ×2 | 0x20 (valves on PA + PB[0:3] + Reservoir A reeds on PB[4:7]) and 0x21 (Reservoir B reeds on PA[0:3] + condenser-fan low-side on PA4). Map in [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd). |
| ULN2803A high-current driver module ×2 | B0F872W528 (2-pc) | Sinks 12 solenoid coils + condenser fan to GND; COM tied to 12 V via DC-6 for flyback. |
| L298N Dual H-Bridge | B0C5JCF5RS (1 of 4-pack) | Drives both Kamoer peristaltic pumps from MCP23017-adjacent ESP32 GPIO; pump cartridge lands at the manifold via pogo pins. |
| Teyleten 3.3 V opto-isolated relay module ×2 | B07XGZSYJV (2 of 5-pack) | Relay #1 switches the compressor 120 VAC hot leg (ESP32 [GPIO 14](RELAY_COMPRESSOR_GPIO)); relay #2 gates 12 V to the SeaFlo diaphragm pump ([GPIO 4](RELAY_DIAPHRAGM_GPIO)). Both stay on the shelf, outside the compressor shroud per [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd). |
| DS3231 RTC | B01N1LZSK3 (1 of 5-pack) | I²C device at 0x68. |
| Mean Well IRM-90-12ST | B0CNRST18V | [80 W](PSU_POWER) / [12 V](PSU_VOLTAGE) / [6.7 A](PSU_CURRENT) encapsulated PSU; IEC 60335-1 listed. Primary lands on the AC distribution block via AC-2; secondary feeds the DC distribution block via DC-1. |
| Legrand 1597BKCCD12 GFCI module | B017HAB4BO ([`/hardware/bom.md`](/hardware/bom.md) §11) | UL 943 Class A [6 mA](GFCI_TRIP) personnel-protection device. Wired inline between the C14 inlet LOAD and the AC distribution block. Self-test every [3 seconds](GFCI_SELF_TEST) + SafeLock end-of-life lockout. Mounted on the shelf. |
| 5 V regulator + 3.3 V regulator | per [`/hardware/bom.md`](/hardware/bom.md) §1 | 12 V → 5 V → 3.3 V cascade per [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd) "Regulation". |
| Wago 221-413 lever-nut connector ×[3](WAGO_COUNT) | per [`/hardware/bom.md`](/hardware/bom.md) §11 | AC distribution block — one Wago per conductor (H, N, G), each carrying one in-leg from the C14 pigtail and two out-legs. |
| DC distribution block | placeholder per [`/hardware/bom.md`](/hardware/bom.md) §11 | 12 V + and GND rails for the DC-2 / DC-4 / DC-6 / DC-8 / DC-9 fan-out from the PSU secondary. Hardware TBD — see Open items. |
| Solid-copper ground bus | per [`/hardware/bom.md`](/hardware/bom.md) §11 (16 AWG green stock) | Single chassis-ground tie point on the shelf. Receives PSU chassis ground (AC-2 G) and the C14 inlet's earth pin (via AC-1a G → GFCI pass-through earth → AC-1b G); distributes to every exposed-metal load via short green pigtails. |
| JST XH 2.54 mm connector kits — 4-pin / 6-pin / 9-pin / 10-pin | B0B2RB524Y / B0B2R8Q1JL / B0B2R73RQB / B0B2R93CV3 | Inter-module logic harnesses per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Inter-module connectors": [~3](JST_4PIN_COUNT)× 4-pin (I²C / UART hops), [~1](JST_6PIN_COUNT)× 6-pin (L298N control), [~4](JST_9PIN_COUNT)× 9-pin (ULN sides), [~4](JST_10PIN_COUNT)× 10-pin (MCP GPIO rows). |
| CQRobot bonded ribbon kit (15 cm × 12 cond × 8 ribbons) | B0F6C7X5CR | Module-to-module connections under ~6"; pre-crimped female XH terminals on both ends. |
| Keszoox [50 cm](KESZOOX_LENGTH) pre-crimped silicone pigtails (20 wires, 10 colors, 22 AWG) | B0F8HMQRRN | Cabinet-spanning runs; supplies the ULN→solenoid fan-out leads + sensor pigtails handed off to [`wiring.md`](wiring.md). |
| 16 AWG silicone-insulated appliance wire (black/white/green) | per [`/hardware/bom.md`](/hardware/bom.md) §11 | AC pigtail stock for AC-1a through AC-6. |
| 18 AWG stranded hookup wire | per [`/hardware/bom.md`](/hardware/bom.md) §11 | 12 V trunk + branch stock (DC-2/3/6/9). |
| Spade crimp terminals + ferrules + ring terminals | per [`/hardware/bom.md`](/hardware/bom.md) §11 (B0B9MZJ2ML + B01MZZGAJP) | AC pigtails land in Wago 221 lever blocks via crimp ferrules; the PSU primary and Teyleten contact terminals take crimp forks; the ground bus takes ring terminals. |
| Printed electronics-shelf frame | TBD (see Open items) | PET-CF, M3 heat-set inserts (ruthex per [`/hardware/bom.md`](/hardware/bom.md) §13). |
| M3 heat-set inserts + M3 × 8/12 SHCS | per [`/hardware/bom.md`](/hardware/bom.md) §13 | Module mounting. |

Tooling: Hakko FX-888D iron + T18 tip kit for the heat-set inserts and JST male-header solder pass (per [`/hardware/handwork.md`](/hardware/handwork.md) "Solder JST connectors"), ESD mat, ferrule crimper, JST XH crimper, ring/fork-terminal crimper, helping hands, multimeter for AC-side continuity and DC-side polarity checks.

## Procedure

### 1. Prepare the printed shelf frame

Heat-set M3 inserts into every mounting boss on the printed shelf per its CAD source. Verify each insert is flush with the boss face.

Module placement geometry on the shelf is set by the shelf STL — see Open items.

### 2. Solder JST XH male headers to module carriers

Per [`/hardware/handwork.md`](/hardware/handwork.md) "Solder JST connectors". Hakko station, 60/40 leaded, ESD mat. Pin-count assignments per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Inter-module connectors":

- **4-pin** — the 4-wire I²C / UART hops: the DS3231 RTC's I²C (VCC / GND / SDA / SCL) and one UART trunk header for SIG-7 to the front-face ESP32-S3 (lands at system integration per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism"). The ESP32 I²C/UART ends land on the DIN-breakout **screw terminals**; the two MCP23017s join the I²C bus on their native **PH2.0** connectors, not XH.
- **6-pin** — L298N control row (ENA / IN1 / IN2 / IN3 / IN4 / ENB); the module ships these pins pre-soldered, so desolder them first.
- **9-pin** — ULN2803A modules × 2 (each gets two 9-pin headers, one per Darlington row of 8 channels + COM/GND).
- **10-pin** — MCP23017 modules × 2 (a 10-pin header per used GPIO row: **VCC + GND + 8 GPIO**). The port row is 10 holes; a 10-pin fills the footprint so neither the header nor the housing can seat off-by-one. The MCP I²C side is the board's native **PH2.0** connector (2.0 mm) — not XH; the I²C bus reaches each MCP on PH2.0, only the ESP32/DS3231 ends are XH.

After every module's headers are in, leave the modules off-shelf on the ESD mat.

### 3. Stage the AC distribution block + ground bus

Mount the three Wago 221-413 lever blocks in their bays on the shelf — one each for H, N, G. Label each block at its bay (H / N / G) with label tape or printed shelf bay-callouts.

Cut and prep the 16 AWG appliance-wire pigtails for AC-1a through AC-6 per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "AC mains" table:

- **AC-1a** — [~150 mm](PIGTAIL_GFCI) pigtails on H, N, G between the C14 inlet and the Legrand GFCI's **LINE** terminals. Backstab or screw terminations at the LINE end; the inlet-side end is left long ([~150 mm](PIGTAIL_SLACK) slack) for the C14 inlet's solder-tab terminations during [`wiring.md`](wiring.md). Label each conductor "AC-1a H" / "AC-1a N" / "AC-1a G" with heat-shrink flags.
- **AC-1b** — [~150 mm](PIGTAIL_GFCI) pigtails on H, N, G between the GFCI's **LOAD** terminals and the H / N / G Wago 221 lever blocks. Backstab or screw terminations at the LOAD end; ferrules at the Wago end. Label each conductor "AC-1b H" / "AC-1b N" / "AC-1b G" with heat-shrink flags. Both ends land in this procedure — AC-1b does not hang off-shelf.
- **AC-2** — H + N + G pigtails from the H / N / G Wago blocks to the PSU primary terminals, [~100 mm](PIGTAIL_MEDIUM), ferrules at the Wago end, crimp forks at the PSU end.
- **AC-3** — H pigtail from the H Wago block to the relay #1 contact input ("common" terminal), [~50 mm](PIGTAIL_SHORT), ferrule one end, crimp fork the other.
- **AC-4/5/6** — pigtails from the relay #1 contact output (AC-4 switched H, [~400 mm](PIGTAIL_COMPRESSOR)), the N Wago block (AC-5, [~400 mm](PIGTAIL_COMPRESSOR)), and the ground bus (AC-6, [~400 mm](PIGTAIL_COMPRESSOR)). Each carries a female disconnect at the compressor-side end and is left coiled with a labeled flag for routing through the compressor-shroud grommet at [`wiring.md`](wiring.md).

Land the solid-copper ground bus on its mounting boss. Stage short green 16 AWG pigtails with ring terminals at the bus end for each exposed-metal load: PSU chassis (lands at PSU mounting in step 4), pressure vessel, faucet SS plate, compressor body / shroud, BiB adapter plate. Leave the load-side end of each pigtail un-terminated and labeled; those land at [`wiring.md`](wiring.md). Bus-to-chassis stud connection lands at [`enclosure-mechanical.md`](enclosure-mechanical.md).

### 4. Mount all modules + PSU on the shelf

Place each module on its boss pattern, M3 × 8 SHCS through the module PCB into the heat-set insert. Mount sequence top-down by bay:

1. **Legrand 1597BKCCD12 GFCI module** — inline between the C14 inlet LOAD and the AC distribution block. AC-1a lands on the device's LINE terminals; AC-1b on the LOAD terminals.
2. **Mean Well IRM-90-12ST PSU**.
3. **Teyleten relay #1** (compressor switch) and **Teyleten relay #2** (diaphragm-pump switch).
4. **ESP32-DevKitC-32E** (on its DIN-rail breakout) — on the logic side of the shelf.
5. **MCP23017 × 2** — co-located with the ESP32.
6. **DS3231 RTC** — same I²C bus.
7. **ULN2803A × 2** — adjacent to the MCP23017s, COM pins facing the DC distribution block, channel outputs facing the solenoid-fan-out bay.
8. **L298N pump driver** — its own bay.
9. **5 V regulator + 3.3 V regulator** — on the 12 V → 5 V → 3.3 V cascade path.

Pre-flash happens at [`firmware-and-commissioning.md`](firmware-and-commissioning.md).

### 5. Land AC pigtails into the distribution block + PSU + relay #1

Open each Wago 221-413 lever and seat the staged ferrules. Each block carries one in-leg (the AC-1b conductor from the GFCI's LOAD terminals) plus the out-legs called out in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md):

- **H Wago** — AC-1b H in; AC-2 H out to PSU primary; AC-3 H out to relay #1 contact input.
- **N Wago** — AC-1b N in; AC-2 N out to PSU primary; AC-5 N out left coiled with its labeled flag (compressor-side disconnect terminated, lands during [`wiring.md`](wiring.md)).
- **G Wago** — AC-1b G in; AC-2 G out to the PSU chassis ground stud; AC-6 G out to the ground bus, which carries the compressor-shroud bond branch.

Lock down each Wago lever. Multimeter-check each Wago bay for continuity from the AC-1b stub to every named out-leg.

Land AC-2 forks on the PSU primary screw terminals. Land AC-3 fork on relay #1's contact-input terminal ("COM" on the Teyleten silkscreen). Verify the relay's other contact terminal ("NO") has the AC-4 switched-H pigtail crimped on with its compressor-side disconnect already in place from step 3.

### 6. Stage the DC distribution block + populate the 12 V branches

Mount the DC distribution block on its boss pattern. Land the DC-1 pair (PSU 12 V + and GND, 16 AWG, [~100 mm](PIGTAIL_MEDIUM), crimp forks at the PSU and ferrules at the distribution block).

Land the branches per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "12 V distribution":

- **DC-2** — 16 AWG 12 V + to relay #2 contact input; the contact-output pigtail (DC-3) is left coiled with a labeled flag and a female disconnect for the SeaFlo pump landing during [`wiring.md`](wiring.md).
- **DC-4** — 22 AWG + and GND to the L298N motor-driver VS / GND screw terminals.
- **DC-6** — 18 AWG + to each ULN2803A COM pin (one branch per ULN module, two total). Flyback rail for the solenoid + condenser-fan inductive loads.
- **DC-8** — 22 AWG + and GND to the 5 V regulator input pins.
- **DC-9** — 22 AWG + pair pigtail with a female disconnect at the fan-side end, left coiled with a labeled flag for the condenser-fan landing during [`wiring.md`](wiring.md). The ULN-sink return is part of the U2-channel-5 fan-out in step 7.

### 7. Crimp + plug the inter-module JST harnesses

Build the logic-side harnesses module-to-module from the JST kits + bonded ribbon + Keszoox pigtails. Build order: I²C trunk, UART hops, ULN-MCP bus, off-shelf fan-out pigtails.

- **I²C trunk** — the ESP32 end (GPIO 21/22 + 3.3 V + GND) lands on the DIN-breakout **screw terminals**; the bus daisy-chains to the DS3231 (4-pin XH) and to each MCP23017 on its native **PH2.0** connector (the MCP I²C side is PH2.0, not XH). Pull-ups on the bus are on the MCP23017 breakouts.
- **UART hops** — one 4-pin XH header on the ESP32 with its shelf-side end seated and its off-shelf end left open for system integration. SIG-7 (GPIO 15 TX / 34 RX + 5 V + GND) lands on the ESP32-S3 on the front face per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md) "S3 detach mechanism".
- **MCP23017 → ULN2803A** — 9-pin XH ribbons, two per MCP (one per port). Port A of 0x20 trunks straight into ULN #1's 8-channel input row; Port B[0:3] of 0x20 lands on ULN #2 inputs 1-4. Port A[4] of 0x21 lands on ULN #2 input 5 (the condenser-fan channel). The Reservoir A reed inputs on 0x20 PB[4:7] and Reservoir B reed inputs on 0x21 PA[0:3] terminate at JST headers at the edge of the shelf — those plug into the Keszoox pigtails that route to the reservoir-mounted reeds at [`wiring.md`](wiring.md).
- **ULN2803A → off-shelf solenoids + condenser fan** — 12 × Keszoox [50 cm](KESZOOX_LENGTH) pre-crimped pigtails crimped into the ULN outputs (8 from ULN #1, 4 from ULN #2 channels 1-4) and one more for the condenser-fan return (ULN #2 channel 5). Each pigtail's far end terminates in a female disconnect for the manifold valves or the fan motor; they leave the shelf as a single bundled run for the valve manifold + a single pigtail for the fan, both labeled.
- **L298N control** — 6-pin XH on the L298N control row (ENA / IN1–4 / ENB; desolder the stock control pins first). The ESP32 ends (GPIO 33/25/26 for pump A, 19/18/5 for pump B per [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd)) land on the DIN-breakout screw terminals. OUT-A and OUT-B land on the peristaltic-pump cartridge via pogo pins at the manifold during [`wiring.md`](wiring.md).
- **3.3 V relay control (LV-1, LV-2, LV-3)** — all screw terminals, no JST: the Teyleten modules' input side is a 3-position screw terminal (VCC / GND / IN), and the ESP32 ends ([GPIO 14](RELAY_COMPRESSOR_GPIO) → relay #1 IN, [GPIO 4](RELAY_DIAPHRAGM_GPIO) → relay #2 IN) land on the DIN-breakout screw terminals. LV-3 feeds 5 V + GND from the 5 V regulator to each relay module's VCC screw terminal.

### 8. Stage the sensor (SIG) pigtails as labeled off-shelf stubs

Per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Sensors and signal", crimp a Keszoox pigtail for each SIG-N run with the shelf-side end terminated in its JST XH housing (soldered onto the appropriate ESP32 GPIO during step 2), and the load-side end left bare with a labeled heat-shrink flag identifying the run by ID (SIG-1 DS18B20 bus, SIG-2/3 reeds, SIG-4 flow meter, SIG-7 S3 rotary display, SIG-9 backflow moisture). The load-side terminations happen at [`wiring.md`](wiring.md) once each sensor is in its final location.

The [4.7 kΩ](DS18B20_PULLUP) DS18B20 pull-up resistor (between SIG-1 data and 3.3 V) is installed at the ESP32 end during this step.

### 9. Pre-power continuity + isolation check

Before the shelf leaves the bench, unpowered:

- AC side: continuity from each AC-1b pigtail (GFCI LOAD-side end) through its Wago block to every named out-leg, including the long compressor-side coils. The C14-side AC-1a through-GFCI continuity is not verifiable at this bench stage because the device's relay is open in the unpowered / un-RESET state; that path is exercised at first power-on per [`firmware-and-commissioning.md`](firmware-and-commissioning.md). Confirm no continuity between the H bus and the G bus, the N bus and the G bus, or the H bus and the N bus.
- DC side: continuity from each DC-1 trunk pair through the distribution block to every named branch. Confirm correct polarity at each branch.
- Ground bus: continuity from every ring-terminal pigtail on the bus back to the AC-1a G stub (the C14-inlet-side pigtail; earth is a pass-through on the GFCI, not sensed by the CT, so the end-to-end continuity is valid at unpowered state).
- I²C trunk: visual check that every JST is fully seated and oriented correctly.

First power-on happens at [`firmware-and-commissioning.md`](firmware-and-commissioning.md), after the shelf is installed and the chassis-ground bonds are landed.

## Output condition

A finished electronics shelf is:

- Fully populated — every module from the inputs table mounted on its boss pattern, ESD-handled, screws torqued by feel
- AC distribution block landed with the three Wago 221-413 levers locked, AC-2 + AC-3 internal stubs terminated at the PSU primary and relay #1 contact input
- DC distribution block landed with the DC-1 trunk from the PSU and DC-4 / DC-6 / DC-8 internal stubs terminated at the L298N, ULN2803A pair, and 5 V regulator
- Inter-module JST harnesses crimped and plugged — I²C, both UART trunks, MCP-to-ULN ports, L298N control
- Relay control + outputs and the ESP32-hub logic landed on screw terminals (no JST)
- Ground bus mounted, bus-side ring terminals seated for every exposed-metal load, load-side ends left long with labeled flags
- AC-1a (H/N/G), AC-4/5/6 (compressor-side), and DC-3 (diaphragm pump) and DC-9 (condenser fan) pigtails coiled with labeled heat-shrink flags identifying the run-ID — ready to be picked up by [`wiring.md`](wiring.md)
- SIG-1 through SIG-9 sensor pigtails crimped, shelf-side seated, load-side ends labeled, DS18B20 pull-up installed at the ESP32 end
- Pre-power continuity and isolation checks passed (AC bus separation, DC polarity, ground continuity)
- Unpowered, MCUs unflashed

## Open items

1. **Printed electronics-shelf frame.** STL / CadQuery source is not yet committed under [`/hardware/printed-parts/enclosure/`](/hardware/printed-parts/enclosure/). The frame's overall envelope, mounting-boss layout for each module, AC-distribution + DC-distribution bays, ground-bus boss, and the wire-egress paths off the shelf all need to be specified in CAD before this procedure can run on unit 1.
2. **PCB / breakout mounting hardware.** M3 standoff heights for each module (the ESP32 DIN-rail breakout, the MCP23017 carriers, the Teyleten relay modules, the ULN2803A carriers, the L298N) are not yet in [`/hardware/bom.md`](/hardware/bom.md) §13. Commit a standoff SKU + per-module count once the shelf CAD lands.
3. **DC distribution block hardware.** The 12 V distribution block is a placeholder. Pick after the shelf CAD lands and the bay it occupies is sized.
4. **Shelf frame material thickness.** PET-CF, 3-4 mm thick at 30-40 % infill working assumption. Confirm once the heaviest module (the Mean Well IRM-90-12ST PSU at [~200 g](PSU_MASS)) is staged against the candidate frame.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_electronics_shelf_sync.py`
