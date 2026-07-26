# Electronics Shelf

The production procedure for the appliance's electronics shelf — the bench-built pair of trays that lie flat on the cold core's foam-cap top in the band above it, on the rear-panel C14 inlet's column: the controller PCBA, the Mean Well PSU, both Teyleten relay modules, the AC + DC distribution, and the ground bus, across two printed trays. The trays are the committed CAD under [`/hardware/printed-parts/electronics/`](/hardware/printed-parts/electronics/) ([pcba-tray](/hardware/printed-parts/electronics/pcba-tray/), [power-tray](/hardware/printed-parts/electronics/power-tray/)). Feeds [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) alongside [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md).

All controller, driver, and logic-rail electronics live on the one JLCPCB-assembled controller PCBA ([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), the canonical pin map): the bare ESP32-WROOM-32E, both MCP23017 expanders, the DS3231 RTC, both TBD62083 solenoid/fan sink drivers, both DRV8870 pump H-bridges, the RS485 transceiver, and the on-board 5 V buck + 3.3 V LDO rails. The board arrives assembled — nothing is soldered on this shelf; every field interface is a labeled edge connector (J1–J14), and every loom lands there or on a relay module's screw terminals. Topology lives in [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd) (AC + 12 V), [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) (pin map), and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd) (expander fan-out). Run-by-run gauges, lengths, and terminations live in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

## Scope

In: the controller PCBA, the Teyleten 3.3 V opto-isolated relays ×2, the Mean Well IRM-90-12ST PSU, Wago 221-413 lever blocks ×[3](WAGO_COUNT) for AC distribution, a printed/screw DC distribution block, the solid-copper ground bus (ring-terminal stack), 16 AWG appliance wire + 22 AWG hookup wire + crimp ferrules/forks/rings, the RELAYS J5 loom from [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md), and the two printed electronics-shelf trays.

Out: one bench-built electronics shelf with the PCBA and both relay modules mounted, the AC distribution block populated (H/N/G Wagos seated, three loads landed), the DC distribution block populated (12 V trunk in from the PSU, branches to relay #2 and the board's J10 inlet), the RELAYS J5 loom landed at both ends, the ground bus prepared with a labeled ring-terminal landing per exposed-metal load, and AC + DC pigtails landed and labeled by run-ID — AC-1 (H/N/G) from the C14 inlet to the Wagos, the inlet-side ends hanging long for the C14 inlet termination, and the DC-3 diaphragm-pump pigtail staged. Relay #1's NO contact, the N Wago's third port, and the ground bus stand open for the AC-4/5/6 SJOOW lead built and landed at [`wiring.md`](/hardware/assembly/wiring.md) §2. Unpowered.

Not in scope: physical install of the trays onto the foam-cap top, including chassis-ground-stud landing — that is [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md). Landing the AC pigtails into the C14 inlet's solder-tab pins, and building the AC-4/5/6 SJOOW lead and passing it through the compressor-shroud cable gland — that is [`wiring.md`](/hardware/assembly/wiring.md), along with every field loom (J1–J4, J6–J9, J11, J13 all land there). Loom fabrication — that is [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md). Flashing firmware and first power-up — that is [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md). The ESP32-S3-Touch-LCD-4.3B config display lives on the front face per [`/hardware/printed-parts/enclosure/front-panel/README.md`](/hardware/printed-parts/enclosure/front-panel/README.md); its SIG-7 RS485 link lands on the board's J9 at system integration.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §1 (controller PCBA + electronics), §11 (wiring + Wagos), §13 (heat-set inserts + M3 SHCS).

| Item | Source | Notes |
|---|---|---|
| Controller PCBA | [`/hardware/pcb/pcba/`](/hardware/pcb/pcba/) | JLCPCB-assembled, 85.05 × 72.85 mm; connector map + order parameters in [`order.md`](/hardware/pcb/pcba/order.md) and [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Board connector map". Takes [12 V](PSU_VOLTAGE) at the J10 screw inlet; makes its own logic rails on-board. |
| Teyleten 3.3 V opto-isolated relay module ×2 | B07XGZSYJV (2 of 5-pack) | Relay #1 switches the compressor 120 VAC hot leg (board [IO19](RELAY_COMPRESSOR_GPIO) through the on-board gas-interlock gate U15); relay #2 gates 12 V to the SeaFlo diaphragm pump ([IO2](RELAY_DIAPHRAGM_GPIO)). Both stay on the shelf, outside the compressor shroud per [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd). Control side wires to the board's J5 (RELAYS). |
| Mean Well IRM-90-12ST | B0CNRST18V | [80 W](PSU_POWER) / [12 V](PSU_VOLTAGE) / [6.7 A](PSU_CURRENT) encapsulated PSU; IEC 60335-1 listed. Primary lands on the AC distribution block via AC-2; secondary feeds the DC distribution block via DC-1. |
| Wago 221-413 lever-nut connector ×[3](WAGO_COUNT) | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | AC distribution block — one Wago per conductor (H, N, G), each carrying one in-leg from the C14 pigtail and two out-legs. |
| DC distribution block | placeholder per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | 12 V + and GND rails for the DC-2 / DC-4 fan-out from the PSU secondary. Hardware TBD — see Open items. |
| Solid-copper ground bus | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 (16 AWG green stock) | Single chassis-ground tie point on the shelf ([`/hardware/reference/ground-ring-stack/`](/hardware/reference/ground-ring-stack/)). Receives PSU chassis ground (AC-2 G) and the C14 inlet's earth pin (via AC-1 G); distributes to the exposed-metal loads via short green pigtails, and receives the compressor-shroud bond — AC-6, the SJOOW's G — at [`wiring.md`](/hardware/assembly/wiring.md) §2. |
| RELAYS J5 loom | [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) | 4-conductor XH housing at J5; screw-terminal ends at both relay modules (LV-1/2/3). |
| 16 AWG silicone-insulated appliance wire (black/white/green) | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | AC-1 pigtail stock + the DC-1/2/4 trunk and branches + ground bonds. |
| 16 AWG stranded hookup wire | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | AC branch stock (AC-2 + AC-3). |
| Spade crimp terminals + ferrules + ring terminals | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 (B0B9MZJ2ML spades + Preciva-kit ferrules + B08B5VS8ZR rings) | AC pigtails land in Wago 221 lever blocks via crimp ferrules; the PSU primary and Teyleten contact terminals take crimp forks; the ground bus takes ring terminals; DC-4 lands under the J10 screw clamps via ferrules. |
| Printed electronics-shelf trays ×2 | [`/hardware/printed-parts/electronics/`](/hardware/printed-parts/electronics/) (pcba-tray, power-tray) | PETG per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §7, M3 heat-set inserts (ruthex per §13). |
| M3 heat-set inserts + M3 × 8 SHCS | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13 | Board + module mounting. |

Tooling: Hakko FX-888D iron + T18 tip kit for the heat-set inserts, ESD mat, ferrule crimper, ring/fork-terminal crimper, helping hands, multimeter for AC-side continuity and DC-side polarity checks.

## Procedure

### 1. Prepare the printed shelf trays

Heat-set M3 inserts into the relay and ground-stud bosses on the [power-tray](/hardware/printed-parts/electronics/power-tray/), per its CAD source under [`/hardware/printed-parts/electronics/`](/hardware/printed-parts/electronics/). Verify each insert is flush with the boss face. The board's and the PSU's inserts are not here — they go into the foam cap's deck-mount columns before the pour, at [`cold-core.md`](/hardware/assembly/cold-core.md) step 3.

Placement geometry is set by the tray CAD: relay #1 + Wago AC distribution + ground ring-stack on the power-tray. Relay #2 and the DC distribution block have no committed bay yet — see Open items; stage them beside the power-tray.

### 2. Stage the AC distribution block + ground bus

Mount the three Wago 221-413 lever blocks in their power-tray slots — one each for H, N, G. Label each block at its bay (H / N / G) with label tape or printed shelf bay-callouts.

Cut and prep the AC pigtails for AC-1 through AC-3 per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "AC mains" table:

- **AC-1** — [~150 mm](PIGTAIL_INLET) 16 AWG pigtails on H, N, G between the C14 inlet and the H / N / G Wago 221 lever blocks. Ferrules at the Wago end; the inlet-side end is left long ([~150 mm](PIGTAIL_SLACK) slack) for the C14 inlet's solder-tab terminations during [`wiring.md`](/hardware/assembly/wiring.md). Label each conductor "AC-1 H" / "AC-1 N" / "AC-1 G" with heat-shrink flags. Ground-fault protection is deferred — see [`/pie-in-the-sky/gfci.md`](/pie-in-the-sky/gfci.md).
- **AC-2** — H + N + G pigtails from the H / N / G Wago blocks to the PSU primary terminals, [~100 mm](PIGTAIL_MEDIUM), ferrules at the Wago end, crimp forks at the PSU end.
- **AC-3** — H pigtail from the H Wago block to the relay #1 contact input ("common" terminal), [~50 mm](PIGTAIL_SHORT), ferrule one end, crimp fork the other.
- **AC-4/5/6** — not cut here. These are the three conductors of one 18 AWG SJOOW jacketed lead ([~400 mm](SHROUD_LEAD_LEN)), pre-built at [`wiring.md`](/hardware/assembly/wiring.md) §2 and passed through the compressor shroud's cable gland — its switched H forks onto relay #1's NO contact, its N seats in the N Wago's open port, its G rings onto the ground bus.

Land the solid-copper ground bus on its power-tray boss. Stage short green 16 AWG pigtails with ring terminals at the bus end for each exposed-metal load: PSU chassis (lands at PSU mounting in step 3), pressure vessel, compressor body. The faucet SS plate's bond is staged the same way but has no landing yet — see [`wiring.md`](/hardware/assembly/wiring.md) Open items 4. Leave the load-side end of each pigtail un-terminated and labeled; those land at [`wiring.md`](/hardware/assembly/wiring.md). Stage the short green block-to-bus leg — ring terminal at the bus, ferrule for the G Wago (seats in step 4) — that carries the C14 earth onto the bus. The compressor-shroud bond is not staged here: it is AC-6, the SJOOW's G conductor, ring-landed on the stack at [`wiring.md`](/hardware/assembly/wiring.md) §2. Bus-to-chassis stud connection lands at [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md).

### 3. Mount the PSU, relays, and PCBA

Place each part on its boss pattern, M3 × 8 SHCS into the heat-set insert, torqued by feel. Mount sequence:

The PSU and the controller PCBA do **not** mount on this bench. Each bolts to four boss columns of the cold core's top foam cap, in the chassis, at [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §8 — there is no tray floor under either. What mounts here is what still rides the power tray:

1. **Teyleten relay #1** (compressor switch) on the power-tray; **relay #2** (diaphragm-pump switch) at its staged position.

Leave the PSU and the board in their ESD/anti-static packaging with their pigtails and looms staged and labeled. The board's four holes are its electrically isolated MH1–MH4; the screw heads seat on the top-face pads, which the board's pours keep clear. Its orientation is fixed by the cap's station: the USB-C programming port (J14) flush at the west board edge looking south down the bay, the J10 12 V screw throats east looking north, both edges left reachable.

Pre-flash happens at [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md), over J14, with the chassis assembled.

### 4. Land AC pigtails into the distribution block + PSU + relay #1

Open each Wago 221-413 lever and seat the staged ferrules. Each block carries one in-leg (the AC-1 conductor from the C14 inlet) plus the out-legs called out in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md):

- **H Wago** — AC-1 H in; AC-2 H out to PSU primary; AC-3 H out to relay #1 contact input.
- **N Wago** — AC-1 N in; AC-2 N out to PSU primary; the third port stays open — AC-5, the SJOOW's N conductor, seats there at [`wiring.md`](/hardware/assembly/wiring.md) §2.
- **G Wago** — AC-1 G in; AC-2 G out to the PSU chassis ground stud; the block-to-bus leg out to the ground bus's ring stack, carrying the C14 earth onto the bus.

Lock down each Wago lever. Multimeter-check each Wago bay for continuity from the AC-1 stub to every named out-leg.

Land AC-2 forks on the PSU primary screw terminals. Land AC-3 fork on relay #1's contact-input terminal ("COM" on the Teyleten silkscreen). The relay's other contact terminal ("NO") stays empty — AC-4, the SJOOW's switched hot, forks onto it at [`wiring.md`](/hardware/assembly/wiring.md) §2.

### 5. Stage the DC distribution block + populate the 12 V branches

Mount the DC distribution block at its staged position. Land the DC-1 pair (PSU 12 V + and GND, 16 AWG, [~100 mm](PIGTAIL_MEDIUM), crimp forks at the PSU and ferrules at the distribution block).

Land the branches per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "12 V distribution":

- **DC-2** — 16 AWG 12 V + to relay #2 contact input; the contact-output pigtail (DC-3) is left coiled with a labeled flag and a female disconnect for the SeaFlo pump landing during [`wiring.md`](/hardware/assembly/wiring.md).
- **DC-4** — 16 AWG + and GND from the distribution block to the board's J10 screw inlet, ferrules under the clamps. `V12` seats on the east pad, `GND` west, both silked at the screws. Everything the board feeds — 10 valves, both peristaltic pumps, the condenser fan, display 12 V, and both logic rails — draws through this run.

### 6. Land the RELAYS J5 loom

Seat the J5 loom's XH housing on the board's J5 (RELAYS) wafer and land the screw-terminal ends per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Low-voltage logic":

- **LV-1** — `IO19` conductor to relay #1's IN terminal. The board asserts this line through the on-board gas→compressor interlock (U15), so relay #1 cannot energize while the MQ-6 reads gas.
- **LV-2** — `IO2` conductor to relay #2's IN terminal.
- **LV-3** — `V5` + `GND` conductors teed at the relay end to both modules' VCC / GND screw terminals. Coil/opto 5 V comes off the board's K7805 rail through J5; opto isolation keeps the coil supply electrically separate from the mains contacts.

This is the only loom that lands at shelf-build time — both its ends live on the shelf. Every other loom (J1–J4, J6–J9, J11, J13) is fabricated at [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) and lands at [`wiring.md`](/hardware/assembly/wiring.md); the board's silk labels + per-loom housing labels are the misplug guard (J4 and J7 share the 7P housing — labelling discipline per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)).

### 7. Pre-power continuity + isolation check

Before the shelf leaves the bench, unpowered:

- AC side: continuity from each AC-1 pigtail (C14-inlet-side end) through its Wago block to every named out-leg. Confirm no continuity between the H bus and the G bus, the N bus and the G bus, or the H bus and the N bus.
- DC side: continuity from each DC-1 trunk pair through the distribution block to every named branch. Confirm correct polarity at each branch — at the J10 clamps, the conductor under the `V12` screw must trace to the PSU +.
- Ground bus: continuity from every ring-terminal pigtail on the bus back to the AC-1 G stub (the C14-inlet-side pigtail).
- J5 loom: seated square on its wafer, screw terminals tugged.

First power-on happens at [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md), after the shelf is installed and the chassis-ground bonds are landed.

## Output condition

A finished electronics shelf is:

- Fully populated — the controller PCBA on its four isolated mounting holes, PSU and both relay modules on their boss patterns, ESD-handled, screws torqued by feel
- AC distribution block landed with the three Wago 221-413 levers locked, AC-2 + AC-3 internal stubs terminated at the PSU primary and relay #1 contact input
- DC distribution block landed with the DC-1 trunk from the PSU, DC-2 terminated at relay #2, and DC-4 terminated under the board's J10 screw clamps, polarity verified
- RELAYS J5 loom landed at both ends (the board wafer + both relay modules' screw terminals)
- Ground bus mounted, bus-side ring terminals seated for each staged bond, load-side ends left long with labeled flags
- AC-1 (H/N/G, inlet-side) and DC-3 (diaphragm pump) pigtails coiled with labeled heat-shrink flags identifying the run-ID — ready to be picked up by [`wiring.md`](/hardware/assembly/wiring.md); relay #1's NO contact, the N Wago's third port, and the ground bus stand open for the AC-4/5/6 SJOOW lead landed there
- Pre-power continuity and isolation checks passed (AC bus separation, DC polarity, ground continuity)
- Unpowered, MCU unflashed

## Open items

1. **Relay #2 + DC distribution block bay.** Neither has a committed printed mount; both stage beside the power-tray. Commit a bay — extend the power-tray `Layout` or add a small dedicated tray — once the DC-block hardware (per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 placeholder) is picked.
2. ~~**Shelf insert + screw counts in the BOM.**~~ **CLOSED.** [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13 carries them: the ruthex row's 40/build includes 13 shelf-tray bosses (pcba-tray 4, power-tray 9), and the M3 × 8 row's 13/build is spent entirely here — 4 PCBA hold-downs + 4 PSU + 4 relay #1 + 1 ground-stack clamp.
3. **Tray thickness under the PSU.** PETG, 3 mm floor at 30-40 % infill working assumption. Confirm once the heaviest part (the Mean Well IRM-90-12ST at [~200 g](PSU_MASS)) is staged against the power-tray.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_electronics_shelf_sync.py`
