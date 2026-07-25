# Wiring

The production procedure for executing every electrical run in the appliance — chassis ground bonds, AC mains, the cabinet-side [12 V](DC_BUS_V) branches, and signal looms — once the enclosure is plumbed and the electronics shelf is installed. The schedule of runs is [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md); this doc is the build-order procedure for executing that schedule, with AC, DC, and signal runs interleaved by physical zone.

A single zip-tied bundle exiting the electronics shelf carries [16 AWG](AWG_AC_MAIN) mains, [12 V](DC_BUS_V) power, and [22 AWG](AWG_DC_BRANCH) signal in close proximity. Topology lives in [`/hardware/wiring/power.mmd`](/hardware/wiring/power.mmd), [`/hardware/wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd), and [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd). Every low-voltage run lands on a labeled edge connector of the controller PCBA ([`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx), the canonical pin map) or on a relay module's terminals.

The field harnesses are **not** wired in place conductor-by-conductor — they are **pre-fabricated as cable assemblies** on the bench (cut-to-length all-black silicone, ferruled/crimped, black-braided-sleeved, continuity-tested), then landed here. The fabrication procedure is [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md); a failed harness is swapped as a whole assembly, never repaired conductor-by-conductor. Wire is all-black throughout **except the AC mains** (black hot / white neutral / green ground — a safety convention, not a service aid).

## Scope

In: a chassis that exits [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) — cold core dropped into the enclosure, valve manifold mounted, all water + CO2 + flavor lines plumbed but unwired; electronics shelf installed per [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md) + [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md), populated with the C14 inlet pigtails, AC distribution block, Mean Well IRM-90-12ST PSU, both Teyleten relays, the controller PCBA with its on-board [5 V](LOGIC_V) + [3.3 V](MCU_V) logic rails, the [12 V](DC_BUS_V) distribution block, and ground bus — the shelf-internal runs (DC-1/2/4, LV-1/2/3) done, unpowered, no field-side wires landed; compressor + condenser fan installed in their middle-bottom and side-wall positions, compressor shroud installed with its AC gland open and its bond point unbonded. Plus the bagged faucet-and-umbilical sub-assembly (output of [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md)) brought to the wiring bench with its rear-panel-end signal-cable conductors broken out and accessible; only the rear-panel-end signal cable gets terminated at the electronics shelf during this procedure.

Wire stock and small parts: the pre-fabricated cable assemblies from [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) — one labeled loom per board connector (J1–J4, J6–J9, J11, J13), each ending in a JST XH [2.54 mm](JST_PITCH) housing at the board end; [16 AWG](AWG_AC_MAIN) silicone hookup wire for AC + ground (green for ground, plus the appliance-wire colors used in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) §AC mains); [16 AWG](AWG_AC_BRANCH_U) silicone for the AC-branch runs in the AC schedule; [18 AWG](SHROUD_SJOOW_AWG) SJOOW 3-conductor jacketed cable for the shroud pass-through; ferrules sized for [16/22 AWG](AWG_TRIPLE); ring terminals for the ground bus + shroud stud; female-disconnect (Faston) terminals for the compressor terminal block, diaphragm pump, valves, and condenser fan; black PET braided sleeve + zip ties for bundling; Wago 221 lever nuts for the device-end fan-outs (221-420 at MANIFOLD A + reservoir-B reed GND, 221-415 at the rest incl. MANIFOLD B).

Out: every run in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) executed and continuity-tested. AC runs AC-1 through AC-6 landed, with the C14 ground pin bonded to the central chassis-ground point and onward to the three landable chassis-ground targets (pressure vessel, compressor body, compressor shroud) — the faucet under-counter plate's bond is deferred per Open items 4. Cabinet-side DC runs DC-3 and DC-5 through DC-9 landed. Signal runs SIG-1 through SIG-4 and SIG-6 through SIG-12 landed at both ends. SIG-7 (4.3B config display) is a [~1 m](SIG_DISPLAY_LEN) internal run from the shelf to the front face; SIG-6 (1.47" faucet display, direct TTL UART) rides the umbilical up to the above-counter faucet head, while SIG-4 (flow meter) is a short internal run in the electronics-shelf zone. A dielectric / continuity check passes on the AC side.

Not in scope: applying [120 VAC](AC_LINE_V); flashing firmware; bringing up the [12 V](DC_BUS_V) rail; any sensor probe-into-water service — see [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md). The shelf-internal runs — see [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md). The compressor terminal block's clip-on PTC start relay / overload module is already mated to the compressor body — a donor-side subassembly preserved during teardown ([`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) "Powering and control"); terminal-block wiring here is the appliance-side leads landing on already-populated spade terminals.

## Inputs per appliance

Wire stock, connectors, and termination consumables are in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 — that one section carries all of it: the 16 AWG AC + ground stock, the 22 AWG DC/signal stock, the Wago 221 lever nuts, the spade / fork / ring terminals, the ferrules, the heat-shrink, and the braided sleeve. The AC hardware the runs land *on* is §5 (C14 inlet, line cord, the GEARit SJOOW shroud lead, the SS cable gland, the thermal fuse). Status in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md). The runs themselves are in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) §"Run table".

Tooling: ratcheting crimper for insulated and uninsulated terminals + ferrules + Faston disconnects + JST XH (one tool covers all four with the appropriate die per terminal family); wire strippers sized for [16/22 AWG](AWG_TRIPLE); small flat screwdriver for Wago 221 levers and the relay screw terminals; PEX-style sidecutters for trimming; a hot-glue gun for strain relief at intermediate tie points where the run crosses a printed-part edge; cable-tie tensioner (optional); multimeter for the continuity + dielectric checks at step 3.

## Procedure

Execution order: chassis-ground bonding, then AC, then the cabinet-side DC, then signal, with a static dielectric / continuity check on the AC side gated between AC completion and DC energization. Within each phase, runs are executed in the run-number order from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

### 1. Chassis-ground bonds (single-point ground at the electronics shelf)

Establish the single-point chassis ground first. Chassis grounding is via discrete green wires from the exposed metal parts back to a central ground bus on the electronics shelf. Per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Grounding strategy" all bonds are [16 AWG](AWG_AC_MAIN) green-insulated, ring terminal at the bus end, ring or fork at the target end.

Bond, from each target to the ground bus on the electronics shelf:

- **Pressure vessel** — ring terminal under the M3 SHCS that already secures one of the foam-shell top-cap screws to a heat-set insert at the cold-core ([`cold-core.md`](/hardware/assembly/cold-core.md)) top face. Pick the top-cap screw position closest to the electronics shelf. Route up through the cold-core / electronics-shelf boundary in the existing wire path used by signal run SIG-1.
- **Compressor body** — ring terminal under one of the four M3 SHCS that bolt the compressor's feet to the enclosure floor ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) Open items 1, "Compressor feet"). The screw bears on the donor grommet's steel bushing, so the ring goes under the head, above the bushing — never pinched into the rubber, which is the isolation element. Route outside the shroud to the compressor body.
- **Compressor shroud** — ring terminal at the Ø ~[6 mm](GND_STUD_HOLE) earth-bond hole on the back face, beside the AC pass-through ([`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Grounding & mounting"). This is run AC-6 in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).
- **Faucet under-counter SS plate** — **not landed at this bench; see Open items 4.** The plate ([`/hardware/cut-parts/faucet/touch-flo-under-counter-plate/`](/hardware/cut-parts/faucet/touch-flo-under-counter-plate/)) has no fastener of its own — it is a Ø54.45 mm disc with a shank pocket and a pill pocket, clamped by the faucet's own factory shank nut — and it ships loose in the install bag, so it does not exist on the appliance at this step. Stage the bus-side ring and leave the conductor coiled and flagged.

At the electronics-shelf end, every bond terminates on a single ring-terminal stack at the ground bus. The bus is bonded to the C14 inlet's earth pin via run AC-1's green conductor (C14 earth → AC distribution block → ground bus), executed in step 2.

Continuity check after this step: ohms-low between every bonded metal surface and the bus.

### 2. AC mains (C14 → distribution → relay #1 → compressor + PSU)

Execute the AC runs in the order they appear in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "AC mains (120 V)": AC-1, AC-2, AC-3, AC-4, AC-5, AC-6. AC-1 lands the rear C14 inlet directly on the AC distribution block; there is no device in series — ground-fault protection is deferred, see [/pie-in-the-sky/gfci.md](/pie-in-the-sky/gfci.md). AC-6 is the shroud chassis-ground done in step 1; it is the third conductor of the 3-conductor bundle through the shroud's cable gland. Build the bundle whole here; the green conductor was landed at the bus end in step 1.

Shroud pass-through (AC-4 + AC-5 + AC-6): pre-build a single [18 AWG](SHROUD_SJOOW_AWG) SJOOW 3-conductor jacketed lead, [~400 mm](SHROUD_LEAD_LEN) long, with the H_switched (from Teyleten relay #1 NO contact), N (from AC distribution block), and G (from electronics-shelf ground bus) conductors. Fit the SS cable gland into the shroud side wall, pass the [18 AWG](SHROUD_SJOOW_AWG) SJOOW lead through, and tighten the gland nut to clamp the jacket — the gland's [6](GLAND_LOW)–[12 mm](GLAND_HIGH) clamping range takes it, per [`/hardware/cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) "Penetrations" item 1. Inside the shroud, fan the three conductors out the last [~50 mm](SHROUD_FAN_OUT): H_switched and N each take a female disconnect onto the appropriate compressor terminal-block spade (the donor's terminal block + clip-on PTC start relay/overload module is already populated from harvest, see [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md) "Powering and control"); G takes a ring terminal at the compressor body's mounting-foot bond from step 1.

At the shelf end of the bundle: H_switched lands on the Teyleten relay #1 NO terminal; N lands at the AC distribution block N pole; G lands on the ground bus. AC distribution-block landings use ferrules into the Wago 221 lever-nut block. Relay screw-terminal landings use fork terminals.

AC-1 (C14 inlet → AC distribution block) is [~150 mm](AC1_LEN), soldered to the inlet's tab pins at the C14 end and ferruled into the Wago block at the distribution end; H, N, and G land directly on the block. AC-2 (distribution block → PSU primary) is [~100 mm](AC2_LEN), ferrule at the block, ring or fork at the PSU; the PSU's chassis ground is bonded by AC-2's green conductor onto the PSU's earth lug. AC-3 is the hot-pickup leg from the distribution block into relay #1's contact common.

Color discipline (AC only): [16 AWG](AWG_AC_MAIN) silicone, black for hot, white for neutral, green for ground. DC and signal wire is all-black (cut-to-length, per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)) — color is reserved for the mains as a safety convention.

### 3. Static dielectric / continuity check on the AC side

After step 2 and before any DC conductor lands, cold-check the AC wiring with the C14 inlet **disconnected from line**, multimeter only. The AC path runs C14 inlet → AC distribution block directly (AC-1), so H and N continuity from the inlet to the distribution block reads end-to-end. Ground-fault protection is deferred — see [/pie-in-the-sky/gfci.md](/pie-in-the-sky/gfci.md).

- **Continuity (ohms-low) — earth, end-to-end:** C14 earth pin to every metal-part chassis-ground target landed in step 1.
- **Continuity (ohms-low) — H/N, C14 → distribution block:** C14 hot pin to AC distribution block H pole. C14 neutral pin to AC distribution block N pole.
- **Continuity (ohms-low) — H/N, distribution block → downstream loads:** AC distribution block H pole to Teyleten relay #1 common. With relay #1 manually held closed (jumper across the input opto), distribution-block H to compressor terminal-block hot spade.
- **Open (ohms-high) — H to N downstream of the distribution block:** distribution block H to distribution block N, both with relay #1 open and with relay #1 closed (with the compressor's motor windings in circuit, this last reads the winding resistance; confirm ~[10](WINDING_R_LOW)–[30 Ω](WINDING_R_HIGH) for a [100 W](COMP_CLASS_W) hermetic, matching the donor compressor's nameplate). With relay #1 open, C14 hot to C14 neutral reads open.
- **Open (ohms-high) — leakage:** Every AC current-carrying conductor to every chassis-ground target. C14 hot pin to chassis-ground, C14 neutral pin to chassis-ground, AC distribution block H pole, AC distribution block N pole, relay #1 NO terminal, compressor terminal-block hot spade — each to chassis-ground. No leakage path.

If any check fails, find and fix it before step 4.

### 4. Cabinet-side [12 V](DC_BUS_V) runs (DC-3, DC-5 through DC-9)

The shelf-internal [12 V](DC_BUS_V) runs (DC-1, DC-2, DC-4) land at [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md); the cabinet-side runs land here, in schedule order:

- **DC-3** (relay #2 contact output → SeaFlo diaphragm pump) — the staged shelf pigtail routes through the cabinet and lands on the pump leads with female disconnects.
- **DC-5** (PUMPS J13 → Kamoer pump A / pump B) — seat the J13 loom's XH housing on the board, route to the pumps, and land the two motor pairs on the pump-motor spade tabs via crimped female faston receptacles ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11).
- **DC-6** (MANIFOLD A J1 → 8 solenoid coils) — a **black sleeved trunk** from the shelf to the manifold: 9 conductors of 22 AWG black (8 OUT + COM), cut-to-length and carried in 3/4" braided sleeve per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md). It breaks out at the manifold: each OUT lands on a female disconnect at its valve; the COM lands in the manifold's 221-420 lever nut, which fans the [12 V](DC_BUS_V) to every valve's other tab. Valve ↔ OUT mapping per [`/hardware/wiring/valve-control.mmd`](/hardware/wiring/valve-control.mmd).
- **DC-7** (MANIFOLD B J2 → 2 solenoid coils) — same pattern on the J2 trunk, 5 of its 6 ways populated (2 OUT + FAN + COM + `OUT3`); the FAN conductor is DC-8, `OUT3` is DC-9, and `OUT4` is a spare board channel left unpopulated.
- **DC-9** (MANIFOLD B J2 `OUT3` + a `COM` tap → V-K) — the water-supply fill/shutoff coil sits away from the manifold, on its cradle in the aft strip by the water bulkhead, so its two conductors leave the J2 trunk and run [~500 mm](VK_RUN_LEN) on to it; female disconnects at the valve. Low-side switching like every manifold valve: `OUT3` sinks V-K's − through the on-board TBD62083 #2 (MCP23017 0x21 PA5), and + taps the shared `COM`. V-K is the only valve outside the manifold — it is what stops water reaching the carbonator on a leak alarm or a power loss.
- **DC-8** (condenser fan) — the fan's + ties to the manifold's COM fan-out; the J2 `FAN` conductor sinks the − side through the on-board TBD62083 #2 channel 5 (MCP23017 0x21 PA3 commands it), flyback through the driver's integrated diode to COM. The branch leaves the J2 trunk at the manifold and runs [~400 mm](FAN_RUN_LEN) to the side-wall fan; female Fastons at the fan.

### 5. Signal looms (SIG-1 through SIG-4, SIG-6 through SIG-12)

Execute the SIG runs from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Sensors and signal", one pre-fabricated loom per board connector. Every board end is a JST XH [2.54 mm](JST_PITCH) housing seated on its labeled wafer — J4 and J7 share the same 7P housing, so land each by its loom label ([`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)); a swap would put J4's 3V3/V5 on J7's reed inputs.

- **SENSORS J4 loom** — three runs share it, GND split near the shelf. **SIG-1**: the 1-wire temperature bus (`IO26` + `3V3` + GND), [22 AWG](AWG_DC_BRANCH), [~600 mm](SIG_COLD_CORE_LEN) to the back of the cold core — a DS18B20 (tank-wall, family 0x28) and a DS18S20 (evap-suction, family 0x10) bussed in parallel and told apart in firmware by family code; the [4.7 kΩ](PULLUP_R) data pull-up is on the board (R9), nothing in the loom. Probes land at the cold core's exit per [`cold-core.md`](/hardware/assembly/cold-core.md). **SIG-4**: the DIGITEN flow meter (`IO25` + `V5` + GND), short internal run — the meter sits in Zone B on the carbonated-water line where it exits the cold core, so this never leaves the enclosure. **SIG-9**: the backflow drip-pan moisture sensor (`IO23` switched VCC + `IO27` DO + GND), [22 AWG](AWG_SIGNAL) to the pan inside the cabinet; `IO23` powers the electrodes only while sampling.
- **REEDS A J6 loom** — **SIG-10**: reservoir A's 4 level reeds + shared GND, [22 AWG](AWG_SIGNAL), [~600 mm](SIG_COLD_CORE_LEN) alongside SIG-1 in the cold-core-exit cable channel; GND explodes in a 221-415 at the reservoir. The reeds ride the on-board MCP23017 internal pull-ups (INPUT_PULLUP, magnet pulls LOW) — no resistors in the loom.
- **REEDS B J7 loom** — three runs share it, GND exploded in a 221-420 at the cold-core end. **SIG-2/SIG-3**: the carbonator low/high reeds (`CLO` / `CHI`). **SIG-11**: reservoir B's 4 reeds (`RB1`–`RB4`). Same internal-pull-up pattern.
- **FAUCET J3 loom** — **SIG-6**: direct TTL UART to the gooseneck-mounted ESP32-S3-Touch-LCD-1.47 faucet display, on the BNTECHGO 28 AWG 4-conductor ribbon (TX / RX / `V5` / GND), [~1 m](SIG_UMBILICAL_LEN) up the umbilical. The ribbon carries no components — the series damping + ESD clamps are on the board ([`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md) "Faucet-display ESD protection").
- **DISPLAY J9 loom** — **SIG-7**: the RS485 link + power to the front-face ESP32-S3-Touch-LCD-4.3B (`B` / `A` / GND / `V12`). The A/B pair lands on the 4.3B's onboard SP3485 terminals; `V12` + GND feed its 7–36 V screw input. Internal run, shelf → front face.
- **I2C J8 loom** — **SIG-8**: the off-board MPR121 cap-sense controller (0x5A) beside the flavor-tube sleeves at the manifold (`GND` / `3V3` / `SDA` / `SCL`), [22 AWG](AWG_SIGNAL). The only off-board I²C device; the bus pull-ups are on the board (R19/R20).
- **GAS J11 loom** — **SIG-12**: the MQ-6 combustible-gas sensor low on the rear cabinet floor (`GND` / `V5` / `DOUT` / `AOUT`). Its 0–5 V outputs are divided to ESP-safe levels on the board (R1–R4), so the loom is a plain sensor cable. This loom also feeds the on-board gas→compressor interlock (U15): the compressor relay cannot energize until it is landed and the sensor warmed.

Continuity-test each signal run end-to-end before zip-tying down.

### 6. Bundle, route, and strain-relieve

Bundle by zone:

- **Shelf-to-cold-core bundle** — the J4 SENSORS loom (SIG-1 + SIG-9 legs), the J6 + J7 reed looms (SIG-2/3/10/11), the J11 gas loom on its rear-wall drop, and the pressure-vessel chassis-ground bond into a single braided-sleeved bundle exiting the back of the shelf and routing along the back wall of the enclosure to the cold core's penetrations ([`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) for the reed columns).
- **Shelf-to-manifold bundle** — the J1 + J2 manifold trunks (DC-6/DC-7/DC-8), DC-3 (diaphragm pump), DC-5 (J13 pump leads), and the J8 MPR121 loom. Braided-sleeve and zip-tie; fan-out happens at the manifold.
- **Shelf-to-shroud bundle** — the [18 AWG](SHROUD_SJOOW_AWG) SJOOW jacketed lead from step 2 is its own bundle; zip-tie tie-down points only.
- **Shelf-to-front-face bundle** — the J9 DISPLAY loom (SIG-7) routed forward through the enclosure interior to the front face. Display end lands on the 4.3B's screw terminals.
- **Shelf-to-umbilical bundle** — the J3 FAUCET loom (SIG-6 on the BNTECHGO ribbon) and the under-counter SS plate chassis-ground bond. Both ride the umbilical together up to the under-counter zone; braided sleeve on the shelf side, separator at the umbilical's bulkhead.
- **Manifold-to-fan branch** — DC-8 leaves the J2 trunk at the manifold and runs alone along the side wall to the condenser fan; female Fastons at the fan.

Strain relief at every cable transition: shelf exit edge, cold-core penetration, manifold entry, shroud gland (the cable gland itself is the strain relief on that one), umbilical bulkhead. Use existing printed-part features. Cable-tie anchors are placed below the cable.

## Output condition

A wired but unenergized chassis:

- The three landable chassis-ground bonds (pressure vessel, compressor body, compressor shroud) land at the single ground bus on the electronics shelf; the bus is bonded to the C14 inlet's earth pin. The faucet under-counter plate's conductor is staged and flagged, not landed — Open items 4
- All AC runs (AC-1 through AC-6) executed and continuity-tested; the AC dielectric / continuity check (step 3) passes
- All DC runs (DC-1 through DC-9) in place — the [12 V](DC_BUS_V) path is contiguous from PSU output to every load, with the fan on the low-side-switched DC-8 branch
- The board's J1, J2, J3, J4, J6, J7, J8, J9, J11, and J13 looms seated on their labeled wafers and landed at their devices; the J5 relay loom verified seated
- All SIG runs (SIG-1 through SIG-4, SIG-6 through SIG-12) landed at both ends
- SIG-7 (4.3B config-display run) seated at the shelf and landed at the front-face display
- SIG-6 (1.47" faucet-display UART run) seated at the shelf and landed up the umbilical at the faucet head
- Wire bundles are black-braided-sleeved or zip-tied by zone, with strain relief at every transition
- The chassis is safe to apply [120 VAC](AC_LINE_V) but no power has been applied

The chassis is the input to [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md).

## Open items

1. **Switched-hot vs unswitched-hot color convention.** [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) does not specify color-coding for switched-hot (AC-4) vs unswitched-hot (AC-3). Pick a convention and roll it into the AC schedule.
2. **Strain relief for bundles crossing the cold-core boundary.** The shelf-to-cold-core bundle enters the foam-shell at a printed pass-through. Pick a strain-relief method and roll it into the foam-shell or the electronics-shelf printed parts.
3. **AC distribution-block hardware.** Open per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "What's not yet decided": Wago 221 vs. screw terminal block vs. PCB-mounted block. Same question applies to the [12 V](DC_BUS_V) distribution block. This procedure assumes Wago 221; pick the production form before unit 1.
4. **The faucet under-counter-plate bond has no landing and no conductor.** Step 1 lists it as one of the four Class I bonds, and nothing downstream can execute it. Two independent blockers:
   - **No fastener to land under.** The plate's generator ([`touch_flo_under_counter_plate.py`](/hardware/cut-parts/faucet/touch-flo-under-counter-plate/touch_flo_under_counter_plate.py)) draws a disc, a shank pocket + channel, and a pill pocket + channel — no bolt holes. Its only clamp is the faucet's factory shank nut, at a thread far larger than the §11 #4 (M3) ring terminal. A ring sized to the shank, a tabbed star washer under the nut, or a small screw feature added to the plate — pick one.
   - **No conductor in the umbilical.** The run is specified as umbilical length + [200 mm](CABINET_SLACK) of cabinet-side slack, riding the bundle beside SIG-6. But [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) builds, sleeves and bags that bundle from three LLDPE tubes and the 28 AWG ribbon only — no green conductor — and the spiral wrap goes on after both ends are terminated. A bond wire has to be in that bundle at FU §4 or it cannot be added later without unwinding the whole run.
   Until both are answered: is the bond required at all? The plate is above the counter, and the only electrical thing at the faucet is the [5 V](LOGIC_V) SELV display. If the answer is no, the run leaves the schedule and step 1 becomes three bonds; if yes, FU has to carry the wire.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_wiring_sync.py`
