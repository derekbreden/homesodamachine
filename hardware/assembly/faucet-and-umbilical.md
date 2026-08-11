# Faucet and Umbilical

The production procedure for the above-counter fixture stack and the 3-tube umbilical that connects it to the rear wall — the visible half of the appliance from the user's perspective. The faucet body and the umbilical ship as **one permanently-attached unit**: the carbonated-water LLDPE tube is clamped into the Westbrass body's upstream compression port at this bench and never separated again, and the two flavor LLDPE tubes route through the touch-flo-shell's pill slot up into the printed gooseneck's dispense channel where they terminate at the printed tip. The customer (or their installer) drills the 1-3/8" countertop hole, drops the faucet+umbilical through it from above, **slides the keyhole under-counter plate laterally onto the dangling umbilical from below** so the shank and tubes enter through the plate's open-edge channels and seat in their terminal pockets, slips a washer over the shank, and tightens one nut. At the rear-wall end, the three tube tails push into the PP1208E bulkheads on the appliance's rear wall.

This bench runs in parallel with the main appliance chain. Its inputs are upstream of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) and its output ships in the carton alongside the finished enclosure produced by [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md). Design intent for the user-facing surface lives in [`/hardware/future.md`](/hardware/future.md) "User-facing elements, by location"; the dispense head is the printed touch-flo-shell's gooseneck channel carrying three LLDPE tubes — see [`/hardware/printed-parts/faucet/touch-flo-shell/`](/hardware/printed-parts/faucet/touch-flo-shell/) and that part's [`MATERIAL.md`](/hardware/printed-parts/faucet/touch-flo-shell/MATERIAL.md).

## Scope

In: one shell + plate + Touch-Flo body sub-assembly (output of [`/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md)) — the printed PET-CF gooseneck on the shell *is* the dispense head; the TPU mounting gasket — slid onto the shank during this bench, sits permanently between the printed mounting plate's underside and where the countertop top surface will be at install; one SendCutSend 0.060" SS under-counter keyhole plate (ships loose in the install bag — slides onto the umbilical at install through its open-edge channels); 3× 1/4" OD LLDPE tubes cut to length (1× blue carbonated-water + 2× black flavor); one Siptenk 1/4" OD brass tube stiffener for the carbonated-water tube end that lands in the Westbrass body's upstream compression port; CARGEN nitrile foam pipe-insulation segments; cable sleeve; one BNTECHGO 28 AWG 4-conductor signal cable carrying the faucet display link (SIG-6: TX / RX / 5 V / GND) through the countertop.

Out: a complete above-counter fixture stack permanently attached to its umbilical — Westbrass body clamped into the touch-flo-shell with the carbonated-water LLDPE tube push-connected at the body's upstream compression port; two flavor LLDPE tubes routed through the shell's pill slot up into the printed gooseneck's dispense channel and terminating at the printed tip; three sleeved tubes terminated bare and push-to-connect-ready at the rear-wall end; foam insulation only on the cold (carbonated-water) tube; signal cable + tube bundle co-sleeved through the countertop. Bagged together with the install kit (one SS under-counter keyhole plate, factory shank nut + washer, Mudder tube cutter — the TPU gasket is already on the shank from this bench and is not in the install kit), drop-shipped inside the appliance carton.

Not in scope: countertop drilling itself; the customer-side install steps — drop-through from above, slide the keyhole under-counter plate laterally onto the dangling umbilical from below, washer + nut tighten, push-into-PP1208E at the rear wall — covered on the printed quick-start sheet that ships with the appliance (design intent: [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md)). Signal-cable termination at the electronics shelf — that's `wiring.md`.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9 (Dispensing — faucet body, under-counter plate, foam insulation) and §8 (Flavor subsystem — Siptenk stiffener for the carbonated-water tube end at the Westbrass upstream port). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost.

The dispense head is the printed touch-flo-shell's gooseneck channel. The three LLDPE tubes are the wet path end to end; the carbonated-water tube push-connects into the Westbrass body's upstream compression port (with a Siptenk stiffener so the LLDPE doesn't crush under the brass ferrule), and the two flavor LLDPE tubes route through the shell's pill slot up into the printed gooseneck's dispense channel and exit at the printed tip.

| Item | Source | Notes |
|---|---|---|
| Touch-Flo shell + plate + body sub-assembly | Output of [`/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md) | Shell printed in PET-CF with M3 heat-set inserts, factory shank nut clamping the harvested Westbrass R2031-NL body to the printed mounting plate. The shell's printed gooseneck is the visible dispense head; three LLDPE tubes route inside its dispense channel and exit at the printed tip. |
| Siptenk 1/4" OD brass tube stiffener × 1 | B0FM77LLM1 (100-pk) | Inside the carbonated-water LLDPE tube end that lands in the Westbrass body's upstream compression port, so the soft tube doesn't crush under the brass ferrule. Only one stiffener per build — the two flavor tubes do not enter any compression port and need no stiffener. |
| TPU mounting gasket (printed) | [`/hardware/printed-parts/faucet/touch-flo-mounting-gasket/`](/hardware/printed-parts/faucet/touch-flo-mounting-gasket/) | Above-counter gasket between the printed mounting plate's underside and the countertop top surface. **Installed at this bench**, slid up the shank from below the plate during step 2 — the body has already been clamped to the plate at the touch-flo-shell sub-assembly bench, but the shank stub remains accessible from below for the gasket to slide onto. Stays permanently on the shank from this point forward. Customer never touches it. |
| Touch-Flo TPU O-ring (printed) | [`/hardware/printed-parts/faucet/touch-flo-tpu-o-ring/`](/hardware/printed-parts/faucet/touch-flo-tpu-o-ring/) | TPU 90A **thimble** (closed bottom with a Ø [6.5 mm](CAP_HOLE_D) centered hole, open top) that seats in the harvested Westbrass body's Ø [10 mm](BODY_PORT_D) top water port. Outer Ø [10.44 mm](ORING_OUTER_D) ([0.22 mm](BODY_SQUEEZE) radial squeeze against the port wall), cylinder ID Ø [9.2 mm](ORING_INNER_D) ([0.1625 mm](LLDPE_INTERFERENCE) interference grip on the 3/8" LLDPE OD), [15.6 mm](TOTAL_H) total height ([2.1 mm](ORING_CAP_T) cap + [13.5 mm](CYL_L) cylindrical sealing band). Two seals in series: radial compression along the cylinder + face seal where the LLDPE's bottom end presses against the cap; cap hole sized between LLDPE ID ([6.35 mm](LLDPE_ID)) and OD ([9.525 mm](LLDPE_OD)) so the tube bottoms out positively and water flows through the cap hole into the LLDPE bore. Install order: thimble cap-down into the port first, then push the 3/8" LLDPE down through the open top until it bottoms on the cap. Consumable — expect to use a fresh thimble on any future re-assembly. |
| SendCutSend 0.060" 316 SS under-counter keyhole plate | `touch-flo-under-counter-plate.dxf` ([`/hardware/cut-parts/faucet/touch-flo-under-counter-plate/`](/hardware/cut-parts/faucet/touch-flo-under-counter-plate/)) | Single-piece Ø [54.45 mm](PLATE_D) disc whose hole positions match the TPU mounting gasket exactly — Ø [12.6 mm](SHANK_HOLE_D) shank pocket and a [13.4 mm](PILL_L) × [7.05 mm](PILL_W) pill pocket (long axis along the plate DXF's Y — the shell's lateral X) at the same XY as the gasket — with two open-edge channels added: a [12.6 mm](SHANK_HOLE_D) wide channel from the shank pocket out to the rim in −Y, and a [7.05 mm](PILL_W) wide channel from the pill pocket out to the rim in −Y. The channels exit the rim at different X positions. The four wall-meets-rim corners are rounded with R [1.5 mm](FILLET_R) fillets. Order qty 1 per appliance. |
| 1/4" OD LLDPE, blue (carbonated water) | New small-spool SKU, sourcing in flight per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) "Umbilical port — tube identification" | Cut to length once; color-coded blue to match the blue-ringed PP1208E bulkhead on the rear wall |
| 1/4" OD LLDPE, black (flavor lines) × 2 | FWS bulk spool ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3) | Cut to length once each; bare black, matches the two unmarked PP1208E bulkheads on the rear wall |
| CARGEN nitrile foam pipe insulation, 1/4" ID × 3/8" wall, 1-ft segments | B0D2XFK337 ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9) | **Cold tube only.** Foam ships as 1-ft segments and is installed segment-at-a-time. Five segments per umbilical, covering 1425 mm of the blue tube |
| Cable sleeve — spiral wrap, 1" nominal | [`bom.md`](/hardware/ledger/bom.md) §11 "Umbilical sleeve" — **SKU TBD** | Single sleeve over all three tubes + the signal cable from just above the under-counter plate down to ~3" above the rear-wall bulkheads. ~2.5–3 m per build. Spiral, not braid: both ends are terminated before it goes on |
| Umbilical signal cable (BNTECHGO 28 AWG 4-conductor ribbon) | B07PNPHWMG ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9) | Single run from the gooseneck faucet display down to the electronics shelf, carrying SIG-6 (faucet display: TX / RX / 5 V / GND). |
| 2× low-capacitance ESD TVS (ESD9B3.3-class / PESD3V3-class, SOD-923) — **optional** | onsemi ESD9B3.3ST5G or Nexperia PESD3V3L1BA (≤ 15 pF, 3.3 V, bidirectional) | **Optional** faucet-end ESD clamp (defense-in-depth only). The primary faucet-UART clamp is now on the board (D10/D11 at U1), so a cable-end TVS is **not required** — fit only if a builder wants a second clamp at the user-touch source (see the ESD note below). |

Tooling (per-build-amortized only; single-asset tools live in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md), not here): Mudder PEX/PE tube cutter (also in the installer's install kit, [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14 — same cutter SKU lives in both places).

### Faucet-display ESD protection (on the board — no build step here)

The faucet flavor LCD is the one user-touched surface on the appliance, at the far end of a ~1 m
umbilical — so its two TTL UART lines are the most ESD-exposed nets on the board. The **primary**
clamp is now **on the main PCBA, at the ESP32**: each TTL line is clamped by a low-cap TVS shunting
the U1-side of its series resistor to the GND plane — **D10 on IO33 (TX), D11 on IO35 (RX)**, onsemi
**ESD9B3.3ST5G** (SOD-923, 3.3 V, bidirectional, ~15 pF), each with a via-in-pad straight to the
plane (shortest loop). A strike up the ribbon is current-limited by the 220 Ω series resistor (R26/
R27) and clamped to ~3.3 V at the ESP32 pin. **This means no ESD build step is required at the faucet
end.**

- **Optional (defense-in-depth only):** a builder may still fit **2× low-cap ESD TVS** at the
  faucet-display connector — one from each TTL line to the faucet-side GND — for a second clamp at the
  user-touch source. Same part class (**ESD9B3.3 / PESD3V3, ≤ 15 pF, SOD-923**, e.g. onsemi
  ESD9B3.3ST5G or Nexperia PESD3V3L1BA), mounted on the last ~10 mm of ribbon (the connector's
  carrier/adapter PCB or a small flex/dead-bug tab, since the stock **Waveshare
  ESP32-S3-Touch-LCD-1.47** module carries no spare pad), GND stub **< 5 mm**. This is not required —
  the board already clamps the ESP32 pin.
- The 5 V and GND conductors are not clamped (rail + return); only the two TTL signals.

Full spec and part rationale: [`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)
"Faucet-display ESD protection (SIG-6)", with the board placement in
[`/hardware/pcb/pcba/jlcpcb-parts.md`](/hardware/pcb/pcba/jlcpcb-parts.md) (D10/D11) and
[`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) (FAUCET block).

## Procedure

### 1. Cut the three LLDPE tubes to length

Cut to **two** lengths: **2× black flavor at 1900 mm** and **1× blue carbonated-water at 1540 mm**. One cut per tube with the Mudder cutter, square-end, no burr.

The two terminate 362 mm apart inside the faucet. The flavor tubes run up the gooseneck's dispense channel to the printed tip — 311.74 mm of centreline above the mounting plate, plus the 4 mm plate, the 2 mm TPU gasket and the countertop slab — while the blue tube lands on the Westbrass body's upstream compression port at the bottom of the shank, 44 mm *below* the countertop's top surface. That 362 mm is set by the faucet's own CAD and does not move with the kitchen. The two factory numbers round it to 360 — cut to them and all three tails land flush at the rear-wall end within a couple of mm, so a blue tube that does not reach the bundle end is a mis-cut, visible before it is sleeved.

The design length sums a measured half and an assumed half:

| Term | mm | Basis |
|---|---:|---|
| Drop, countertop underside → appliance top plane | 418 | 34.5" carcass − 4" toe kick − 3/4" deck = 755.7 mm interior clear, less the enclosure height |
| Down the rear face to the flavor-bulkhead axis | 42 | CAD |
| Turn-in at the wall — lead + 90° at R12 + collet | 62 | CAD; the collet stands 9.5 mm proud of the port ring it bears on, and that ring stands 2 mm off the wall (`printed-parts/enclosure/port-ring/`) |
| Horizontal inside the cabinet, faucet hole → drop line | 380 | 36" sink base: faucet on the sink centreline, appliance at one end |
| Service loop — the appliance comes forward to reach its own rear wall | 300 | pull-forward to put the rear wall at the cabinet face |
| **Below-counter subtotal** | **1202** | |
| Countertop slab | 30 | 3 cm stone (range 19–38) |
| TPU gasket + mounting plate | 6 | CAD |
| Gooseneck centreline, shell foot → printed tip | 312 | CAD |
| **Flavor tube, nominal installed** | **1550** | |
| **Blue tube, nominal installed** | **1185** | its top end sits 14 mm below the countertop underside |

**Installer-trim allowance: 350 mm per tube**, held separately from the sum — 8 mm for a slab up to 38 mm, 25 mm for cabinet-height variance, 300 mm for an appliance at the far end of the sink base rather than the near end, 20 mm for two square cuts. Factory cut = nominal + allowance.

The installer makes a *second* cut on each tube at field install — trimming the rear-wall end to fit the customer's actual cabinet depth before pushing each tube into its PP1208E bulkhead. The factory length is sized long with that installer-trim allowance baked in; do not cut tight here.

### 2. Route the three LLDPE tubes through the touch-flo-shell

The shell sub-assembly arrives from [`/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md) with the Westbrass body already clamped to the printed mounting plate inside the shell. This step threads the three LLDPE tubes into their final positions and locks them down — the printed gooseneck *is* the dispense head, and the LLDPE tubes are the wet path end to end. The shell's CAD script describes the dispense channel and gooseneck geometry the three tubes route through.

- **Carbonated water (blue tube).** Insert a Siptenk 1/4" brass stiffener fully into the blue LLDPE tube end that will land in the Westbrass body. Push that stiffened end into the Westbrass body's upstream compression port (the supply side that takes carbonated water *in*). The body's factory ferrule + nut clamp the LLDPE around the stiffener; hand-snug + 1/4 turn with a wrench.
- **Flavor lines (black tubes × 2).** Each black LLDPE tube routes through the shell's pill slot (which passes through both the printed mounting plate and the TPU gasket per the upstream sub-assembly's ASSEMBLY.md step 5) up into the printed gooseneck's dispense channel, terminating at the printed tip. The tubes push through dry, retained by the channel's bore-to-OD interference fit at the dispense tip and by the pill slot's geometry at the bottom.

At the rear-wall end of all three tubes: **leave them bare and square-cut.** The installer pushes each tube directly into the matching PP1208E bulkhead's collet at field install; PP1208E's internal grab-ring + EPDM O-ring make the seal around the tube OD (same seal mechanism already in use on the reservoir-cap bulkhead per [`/hardware/printed-parts/cold-core/reservoir/reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py)).

### 3. Slide foam segments onto the carbonated-water tube only

Per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) "Umbilical bundle construction": **foam goes on the blue tube only.** The carbonated-water tube is the temperature-critical run.

Slide CARGEN 1-ft segments onto the blue tube end-to-end. The segments are sized as a snug interference fit over 1/4" OD LLDPE; lubricate with a wipe of water if friction is high (no solvents — nitrile is solvent-sensitive). Butt the segments together along the run with no gap; the braided sleeve installed in step 4 holds the butts compressed.

Segment count for the standard build is **five**, covering 1425 mm of the blue tube's 1540 mm — bare 40 mm at the compression end and the last 75 mm at the wall. A nominal kitchen keeps four; the installer pulls one whole segment off with the trim, which is what the 1-ft granularity buys. Foam OD is 25.4 mm — it does not pass the countertop hole and does not need to, since the blue tube is entirely below the counter.

### 4. Sleeve the three tubes + signal cable into one bundle

Bundle the three LLDPE tubes (one foamed blue + two bare black) into the natural triangular dense-pack arrangement — three round tubes in a sleeve pack no other way. The three PP1208E bulkheads stand on **one line** across the rear wall, so the bundle does not present to them as a triangle: the installer flexes the three tubes apart at the un-sleeved end and pushes each into its own union. What the blue (foamed) tube carries is identification, not orientation — it goes into the blue-ringed union, which is the east end of the row.

Run the umbilical signal cable alongside the three-tube triangle, sitting in the void between the three triangle-packed tubes and the sleeve's inner wall. It is the BNTECHGO 28 AWG 4-conductor ribbon and carries the SIG-6 faucet-display link (TX / RX / 5 V / GND) through the countertop, per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

Lay the spiral wrap (1" nominal) on over the full length of the bundle, winding it around radially. It is spiral and not braid because both ends of the bundle are already terminated when this step runs — the faucet body at the top, the SIG-6 ribbon's break-out at the bottom — so braid could only be threaded up from the wall end over five butted foam segments, which is the one thing the sleeve exists to prevent. Sleeve runs from just above the under-counter plate (top end, where the bundle emerges out the bottom of the faucet body's pill slot) to ~3" above the rear-wall end (bottom end, where the installer trims to fit). Leaving the last 3" un-sleeved at the rear-wall end is so the installer can flex the three tubes apart by a few inches for the three-bulkhead push-connect.

### 5. Bag the sub-assembly with installer kit

Lay the bundled umbilical down with the faucet body at one end and the three bare tube tails + signal-cable unterminated end at the other. Coil the umbilical loosely (8–12" loop diameter).

The TPU gasket is already on the shank from step 2 and is not in the install kit. Into the bag with the umbilical, add the install-kit parts the customer needs at countertop install:

- **One SendCutSend 0.060" 316 SS under-counter keyhole plate** — the single-piece plate that slides laterally onto the dangling umbilical from below at install.
- Factory shank nut + washer (loose — installed below the keyhole plate)
- One Mudder PEX/PE tube cutter (the per-appliance install-kit tool from [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14, same SKU as the bench-side cutter)

The customer-facing install instructions live on the printed quick-start sheet that ships at the top of the appliance carton; design intent for the sheet is [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md).

Bag, seal, label with build number and the part identifier `FAUCET-UMBILICAL-SUBASSEMBLY`, set aside for [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md) (TBD).

## Output condition

A bagged sub-assembly that is:

- One above-counter fixture stack with the three umbilical tubes installed
- The umbilical is **permanently attached** to the faucet body — three LLDPE tubes (1× blue carbonated-water + 2× black flavor) connected at the body's compression ports, routed up through the upper mounting plate's pill slot, inside a single sleeve with foam insulation on the cold tube only, signal cable (SIG-6 faucet display) alongside the three tubes inside the same sleeve
- Three tubes terminated bare and square-cut at the rear-wall end, ready for push-into-PP1208E at install
- Signal cable unterminated at the above-counter end (gets cut to length at the customer's countertop position during install); rear-wall end terminated at the electronics shelf during `wiring.md` at appliance final assembly (the bagged sub-assembly is brought to the wiring bench, signal conductors broken out, terminated, and the bag re-closed for shipping)
- TPU mounting gasket already in place on the shank between the printed mounting plate's underside and where the countertop top surface will be (installed at this bench, not in the install kit; customer never touches it)
- Loose install-kit parts bagged together: **one SS under-counter keyhole plate**, factory shank nut + washer, Mudder tube cutter
- Labeled, sealed, ready to drop into the appliance carton at [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md)

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. ~~**Umbilical design length.**~~ **CLOSED.** Factory cut is **1900 mm** per black flavor tube and **1540 mm** for the blue, each carrying a **350 mm** installer-trim allowance; the stack-up and the basis of every term are in §1. The CARGEN segment count falls out at five. One real install settles the four assumed terms — tape-measure the sink base, set the appliance where it will live, and measure faucet hole → bulkhead with a string.
2. ~~**Cable sleeve selection.**~~ **CLOSED — spiral wrap, 1" nominal.** Both ends of the bundle are already terminated when step 4 runs, so braid could only be threaded up from the wall end, over five butted foam segments — the one thing the sleeve exists to prevent. Spiral lays on radially over an assembled ~⌀32 mm bundle, unwinds for the SIG-6 break-out at [`wiring.md`](/hardware/assembly/wiring.md), and unwinds again past the installer's trim. ~2.5–3 m per build.
3. ~~**Blue LLDPE small-spool sourcing.**~~ **CLOSED.** John Guest blue 1/4" OD LLDPE, 100 ft, FWS `WEBFWS100677333` — [`bom.md`](/hardware/ledger/bom.md) §3 at ~5 ft per build, [`purchases.md`](/hardware/ledger/purchases.md) §3.
4. **Umbilical cable strain relief through the countertop.** The 1-3/8" countertop hole that takes the faucet shank is sized for the shank + gasket + plate stack; the umbilical signal cable piggybacks through the same hole alongside the tubes. Whether the cable needs a separate grommet, a printed strain-relief collar, or just rides loose through the gasket's pill-slot region is undefined.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_faucet_and_umbilical_sync.py`
