# Electronics Shelf

The production procedure for the appliance's electronics shelf — the parts that stand as one column down the enclosure's **+X wall** in the band above the cold core, feet on its foam-cap lid: the controller PCBA, the Mean Well PSU, both Teyleten relay modules, the AC + DC distribution, and the ground bus. Each is turned so its own mounting plane faces that wall, and each bolts to printed bosses reaching in off it; the one printed carrier is the [ac-hub](/hardware/printed-parts/electronics/ac-hub/), which holds the three lever nuts that have nothing of their own to bolt with. **There is no tray under any of it.** Feeds [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) alongside [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md).

All controller, driver, and logic-rail electronics live on the one JLCPCB-assembled controller PCBA ([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), the canonical pin map): the bare ESP32-WROOM-32E, both MCP23017 expanders, the DS3231 RTC, both TBD62083 solenoid/fan sink drivers, both DRV8870 pump H-bridges, the RS485 transceiver, and the on-board 5 V buck + 3.3 V LDO rails. The board arrives assembled — nothing is soldered on this shelf; every field interface is a labeled edge connector (J1–J14), and every loom lands there or on a relay module's screw terminals. Topology lives in [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd) (AC + 12 V), [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd) (pin map), and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd) (expander fan-out). Run-by-run gauges, lengths, and terminations live in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

## Scope

In: the controller PCBA, the Teyleten 3.3 V opto-isolated relays ×2, the Mean Well IRM-90-12ST PSU, Wago 221-413 lever blocks ×[3](WAGO_COUNT) for AC distribution, a printed/screw DC distribution block, the solid-copper ground bus (ring-terminal stack), 16 AWG appliance wire + 22 AWG hookup wire + crimp ferrules/forks/rings, the RELAYS J5 loom from [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md), and the printed AC hub.

Out: one bench-built electronics shelf with the PCBA and both relay modules mounted, the AC distribution block populated (H/N/G Wagos seated, three loads landed), the DC distribution block populated (12 V trunk in from the PSU, branches to relay #2 and the board's J10 inlet), the RELAYS J5 loom landed at both ends, the ground bus prepared with a labeled ring-terminal landing per exposed-metal load, and AC + DC pigtails landed and labeled by run-ID — AC-1 (H/N/G) from the C14 inlet to the Wagos, the inlet-side ends hanging long for the C14 inlet termination, and the DC-3 diaphragm-pump pigtail staged. Relay #1's NO contact, the N Wago's third port, and the ground bus stand open for the AC-4/5/6 SJOOW lead built and landed at [`wiring.md`](/hardware/assembly/wiring.md) §2. Unpowered.

Not in scope: bolting these bodies onto the enclosure's +X wall, including chassis-ground-stud landing — that is [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md). Landing the AC pigtails into the C14 inlet's solder-tab pins, and building the AC-4/5/6 SJOOW lead and landing it on the compressor's terminal block — that is [`wiring.md`](/hardware/assembly/wiring.md), along with every field loom (J1–J4, J6–J9, J11, J13 all land there). Loom fabrication — that is [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md). Flashing firmware and first power-up — that is [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md). The ESP32-S3-Touch-LCD-4.3B config display is let into the 45° facet chamfered across `enclosure-front-top`'s top-front arris per [`/hardware/printed-parts/enclosure/enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md); its SIG-7 RS485 link lands on the board's J9 at system integration.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §1 (controller PCBA + electronics), §11 (wiring + Wagos), §13 (heat-set inserts + M3 SHCS).

| Item | Source | Notes |
|---|---|---|
| Controller PCBA | [`/hardware/pcb/pcba/`](/hardware/pcb/pcba/) | JLCPCB-assembled, [85 × 72.8 mm](PCBA_SIZE); connector map + order parameters in [`order.md`](/hardware/pcb/pcba/order.md) and [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Board connector map". Takes [12 V](PSU_VOLTAGE) at the J10 screw inlet; makes its own logic rails on-board. |
| Teyleten 3.3 V opto-isolated relay module ×2 | B07XGZSYJV (2 of 5-pack) | Relay #1 switches the compressor 120 VAC hot leg (board [IO19](RELAY_COMPRESSOR_GPIO) through the on-board gas-interlock gate U15); relay #2 gates 12 V to the SeaFlo diaphragm pump ([IO2](RELAY_DIAPHRAGM_GPIO)). Both stay on the shelf, away from the refrigeration compartment per [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd) — relay #1's switching arc is kept off the volume a hydrocarbon leak would pool in. Control side wires to the board's J5 (RELAYS). |
| Mean Well IRM-90-12ST | B0CNRST18V | [80 W](PSU_POWER) / [12 V](PSU_VOLTAGE) / [6.7 A](PSU_CURRENT) encapsulated PSU; IEC 60335-1 listed. Primary lands on the AC distribution block via AC-2; secondary feeds the DC distribution block via DC-1. |
| Wago 221-413 lever-nut connector ×[3](WAGO_COUNT) | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | AC distribution block — one Wago per conductor (H, N, G), each carrying one in-leg from the C14 pigtail and two out-legs. |
| DC distribution block | placeholder per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | 12 V + and GND rails for the DC-2 / DC-4 fan-out from the PSU secondary. Hardware TBD — see Open items. |
| Solid-copper ground bus | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 (16 AWG green stock) | Single chassis-ground tie point on the shelf ([`/hardware/reference/ground-ring-stack/`](/hardware/reference/ground-ring-stack/)). Receives PSU chassis ground (AC-2 G) and the C14 inlet's earth pin (via AC-1 G); distributes to the exposed-metal loads via short green pigtails, and receives the compressor-body bond — AC-6, the SJOOW's G — at [`wiring.md`](/hardware/assembly/wiring.md) §2. |
| RELAYS J5 loom | [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) | 4-conductor XH housing at J5; screw-terminal ends at both relay modules (LV-1/2/3). |
| 16 AWG silicone-insulated appliance wire (black/white/green) | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | AC-1 pigtail stock + the DC-1/2/4 trunk and branches + ground bonds. |
| 16 AWG stranded hookup wire | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | AC branch stock (AC-2 + AC-3). |
| Spade crimp terminals + ferrules + ring terminals | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 (B0B9MZJ2ML spades + Preciva-kit ferrules + B08B5VS8ZR rings) | AC pigtails land in Wago 221 lever blocks via crimp ferrules; the PSU primary and Teyleten contact terminals take crimp forks; the ground bus takes ring terminals; DC-4 lands under the J10 screw clamps via ferrules. |
| Printed AC hub ×1 | [`/hardware/printed-parts/electronics/ac-hub/`](/hardware/printed-parts/electronics/ac-hub/) | PETG per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §7. No inserts — its two hold-down screws pass through it into the +X wall's own bosses. |
| M3 × 8 SHCS ×14 + M3 × 10 ×1 | per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13 | Board + module mounting. Every one lands in a ruthex insert already set in a +X wall boss of `enclosure-back-top` — no insert is pressed on this shelf. See Open items 2. |

Tooling: ESD mat, ferrule crimper, ring/fork-terminal crimper, helping hands, multimeter for AC-side continuity and DC-side polarity checks.

## Procedure

### 1. Prepare the printed AC hub

Print the [ac-hub](/hardware/printed-parts/electronics/ac-hub/) and dry-fit one Wago into each of its three wells, butt-end down, to confirm the press fit. No inserts go into it — every insert this shelf's screws land in is a ruthex short in a +X wall boss of `enclosure-back-top`, pressed at [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §1.

**Placement geometry is the +X wall's, and it is read off each body rather than typed.** Each of the five is turned so its own mounting plane faces that wall and stands on one common seat, and [`front_half.wall_mounts`](/hardware/manifold-layout/front_half.py) carries that body's own hole pattern through its own placement to give the wall one boss per hole — so a body that moves takes its bosses with it, and a boss cannot land on a column the part has no hole in. Down the flank: the board forward, the PSU aft of it, relay #1 and the AC hub stacked on the brick's crown, and the ground stack on the relay's floor forward of the pair. Relay #2 and the DC distribution block have no station yet — see Open items; stage them loose.

### 2. Stage the AC distribution block + ground bus

Stand the three Wago 221-413 lever blocks in the AC hub's wells, butt-end down, wire ports up and levers facing the board — west to east, H / N / G. Label each block at its bay (H / N / G) with label tape or printed shelf bay-callouts.

Cut and prep the AC pigtails for AC-1 through AC-3 per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "AC mains" table:

- **AC-1** — [~150 mm](PIGTAIL_INLET) 16 AWG pigtails on H, N, G between the C14 inlet and the H / N / G Wago 221 lever blocks. Ferrules at the Wago end; the inlet-side end is left long ([~150 mm](PIGTAIL_SLACK) slack) for the C14 inlet's solder-tab terminations during [`wiring.md`](/hardware/assembly/wiring.md). Label each conductor "AC-1 H" / "AC-1 N" / "AC-1 G" with heat-shrink flags. Ground-fault protection is deferred — see [`/pie-in-the-sky/gfci.md`](/pie-in-the-sky/gfci.md).
- **AC-2** — H + N + G pigtails from the H / N / G Wago blocks to the PSU primary terminals, [~100 mm](PIGTAIL_MEDIUM), ferrules at the Wago end, crimp forks at the PSU end.
- **AC-3** — H pigtail from the H Wago block to the relay #1 contact input ("common" terminal), [~50 mm](PIGTAIL_SHORT), ferrule one end, crimp fork the other.
- **AC-4/5/6** — not cut here. These are the three conductors of one 18 AWG SJOOW jacketed lead ([~400 mm](COMP_LEAD_LEN)), pre-built at [`wiring.md`](/hardware/assembly/wiring.md) §2 and run whole to the compressor — its switched H forks onto relay #1's NO contact, its N seats in the N Wago's open port, its G rings onto the ground bus.

The solid-copper ground bus takes its own wall boss on relay #1's floor, forward of the relay and hub pair, under one M3 × 10 — it is landed in the chassis, not on this bench. Stage short green 16 AWG pigtails with ring terminals at the bus end for each exposed-metal load: PSU chassis (lands at PSU mounting in step 3), pressure vessel, compressor body. The faucet SS plate's bond is staged the same way but has no landing yet — see [`wiring.md`](/hardware/assembly/wiring.md) Open items 4. Leave the load-side end of each pigtail un-terminated and labeled; those land at [`wiring.md`](/hardware/assembly/wiring.md). Stage the short green block-to-bus leg — ring terminal at the bus, ferrule for the G Wago (seats in step 4) — that carries the C14 earth onto the bus. The compressor-body bond is not staged here: it is AC-6, the SJOOW's G conductor, ring-landed on the stack at [`wiring.md`](/hardware/assembly/wiring.md) §2. Bus-to-chassis stud connection lands at [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md).

### 3. Stage the PSU, relays, and PCBA

**Nothing on this shelf mounts on this bench.** The board, the PSU, relay #1, the AC hub and the ground stack all bolt to printed bosses on the enclosure's +X wall, in the chassis, at [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §5 — M3 × 8 SHCS in through the body from the room, into the boss's ruthex insert, torqued by feel. There is no tray floor under any of them. **Relay #2** (diaphragm-pump switch) stays at its staged position.

Leave the PSU and the board in their ESD/anti-static packaging with their pigtails and looms staged and labeled. The board's four holes are its electrically isolated MH1–MH4; the screw heads seat on the top-face pads, which the board's pours keep clear. Its orientation is fixed by the wall's own station: the board turned so its flat back faces the wall and its long edge runs fore and aft down the flank, so only its thickness and components reach into the lane and both X edges stay reachable to a hand and a plug.

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

- Fully wired and staged — the controller PCBA, the PSU and both relay modules ESD-handled and left in their packaging, each labeled with the wall station it bolts to at [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §5
- AC distribution block landed with the three Wago 221-413 levers locked, AC-2 + AC-3 internal stubs terminated at the PSU primary and relay #1 contact input
- DC distribution block landed with the DC-1 trunk from the PSU, DC-2 terminated at relay #2, and DC-4 terminated under the board's J10 screw clamps, polarity verified
- RELAYS J5 loom landed at both ends (the board wafer + both relay modules' screw terminals)
- Ground bus staged with its bus-side ring terminals seated for each bond, load-side ends left long with labeled flags
- AC-1 (H/N/G, inlet-side) and DC-3 (diaphragm pump) pigtails coiled with labeled heat-shrink flags identifying the run-ID — ready to be picked up by [`wiring.md`](/hardware/assembly/wiring.md); relay #1's NO contact, the N Wago's third port, and the ground bus stand open for the AC-4/5/6 SJOOW lead landed there
- Pre-power continuity and isolation checks passed (AC bus separation, DC polarity, ground continuity)
- Unpowered, MCU unflashed

## Open items

1. **Relay #2 + DC distribution block station.** Neither has one; both stage loose. What is missing is a root, not room: the five bodies that do have stations pack the +X flank end to end, and the ground stack takes the last gap between the board and the relay-and-hub pair. Every board connector sits on an edge row or an edge column, so the board's middle is clear inboard, and the lane between the flank and the water pump is open the cap's whole depth. Rooting the pair means one of: a boss pair reaching further inboard off the same wall, a bracket sharing the board's own four holes, or the open lane west of the flank. Commit a station once the DC-block hardware (per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 placeholder) is picked and its footprint is known.
2. ~~**The BOM still books this shelf's inserts against the cold core's top cap.**~~ **CLOSED.** [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13 books them as the fourth retention place — `enclosure-back-top`'s +X wall bosses, counted off the placed pack's own `east_bosses` — and [`cold-core.md`](/hardware/assembly/cold-core.md) presses only what its own bench presses.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_electronics_shelf_sync.py`
