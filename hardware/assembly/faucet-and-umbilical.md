# Faucet and Umbilical

The production procedure for the above-counter fixture stack and the 3-tube umbilical that connects it to the +Y wall of back-top — the visible half of the appliance from the user's perspective. The faucet and the umbilical ship as **one permanently-attached unit**: the retained donor washer and nut are factory-preloaded on the bare shank before the carbonated-water LLDPE tube is clamped into the Westbrass body's upstream compression port, and that tube is never separated again. The two flavor LLDPE tubes route through the faucet-shell's pill slot up into the printed gooseneck's dispense channel where they terminate at the printed tip. The customer (or their installer) drills the 1-3/8" countertop hole, drops the complete faucet+umbilical through it from above and pushes it back until the flavor tubes rest against the hole's wall — the faucet seats itself, nothing is measured, and the gasket still covers the hole behind by [2.993 mm](GASKET_COVER) there — **slides the under-counter plate laterally into the captive mount stack from below** so the shank and tubes enter through the plate's open-edge channels and seat in their terminal pockets, then hand-tightens the same retained nut. At the far end, the three tube tails push into the PP1208E bulkheads on the appliance's +Y wall of back-top.

This bench runs in parallel with the main appliance chain. Its inputs are upstream of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) and its output ships in the carton alongside the finished enclosure produced by [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md). Design intent for the user-facing surface lives in [`/hardware/future.md`](/hardware/future.md) "User-facing elements, by location"; the gooseneck carries one 3/8" soda faucet tube and two 1/4" flavor tubes out over the glass — see [`/hardware/printed-parts/faucet/faucet-shell/`](/hardware/printed-parts/faucet/faucet-shell/) and that part's [`MATERIAL.md`](/hardware/printed-parts/faucet/faucet-shell/MATERIAL.md).

## Scope

In: one shell + plate + Touch-Flo body sub-assembly (output of [`/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md)) — the shell's printed PET-CF gooseneck carries the tubes out over the glass; the TPU above-counter gasket — slid onto the shank during this bench, sits permanently between the above-counter plate's underside and where the countertop top surface will be at install; one SendCutSend 0.060" SS under-counter plate (ships loose in the install bag — slides onto the umbilical at install through its open-edge channels); 3× 1/4" OD LLDPE umbilical tubes cut to length (1× blue carbonated-water + 2× black flavor); one 3/8" OD black LLDPE soda faucet tube for the gooseneck; one Siptenk 1/4" OD brass tube stiffener for the carbonated-water tube end that lands in the Westbrass body's upstream compression port; CARGEN nitrile foam pipe-insulation segments; PET braid sleeve segments; three printed tube collars; one BNTECHGO 28 AWG 4-conductor signal cable carrying the faucet display link (SIG-6: TX / RX / 5 V / GND) through the countertop.

Out: a complete above-counter fixture stack permanently attached to its umbilical — Westbrass body captured in the faucet-shell; retained donor washer and nut captive on the shank; blue carbonated-water supply connected at the body's lower upstream compression port; 3/8" soda faucet tube sealed into the top port and routed through the gooseneck; two flavor LLDPE tubes routed through the shell's pill slot and gooseneck to the printed tip; three sleeved umbilical tubes terminated bare and push-to-connect-ready at the +Y wall of back-top, each wearing its own printed collar on the bare stretch below the braid; foam insulation only on the cold blue tube; factory-fitted SIG-6 ribbon + tube bundle co-sleeved below the countertop. Bagged together with the loose install-kit parts (one SS under-counter plate, Mudder tube cutter, and two field-run tube collars — the TPU gasket and donor mount hardware are already captive on the faucet), drop-shipped inside the appliance carton.

Not in scope: countertop drilling itself; the customer-side install steps — drop-through from above, slide the under-counter plate laterally above the captive washer, hand-tighten the same retained nut, trim the field ends, push-into-PP1208E at the +Y wall of back-top — covered in the visual quick start that ships with the appliance ([`/hardware/quickstart/`](/hardware/quickstart/README.md); packing and content contract: [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md)). Factory-side SIG-6 termination at the main board is `wiring.md`; there is no field signal-conductor assembly.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9 (Dispensing — Westbrass, under-counter plate, foam insulation) and §8 (Flavor subsystem — Siptenk stiffener for the carbonated-water tube end at the Westbrass upstream port). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost.

The blue 1/4" carbonated-water supply compression-connects to the bottom of the Westbrass body with a Siptenk stiffener under the brass ferrule. Water rises through the body and leaves its top port in a separate 3/8" LLDPE soda faucet tube. That soda faucet tube and the two 1/4" flavor tubes share the printed gooseneck and exit at the tip; only the flavor pair enters through the shell's pill slot.

| Item | Source | Notes |
|---|---|---|
| Touch-Flo shell + plate + body sub-assembly | Output of [`/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md) | Shell printed in PET-CF with M3 heat-set inserts, with the harvested Westbrass R2031-NL body captured between the shell and above-counter plate. Its retained donor washer and shank nut travel with the sub-assembly for the countertop mount. One 3/8" soda faucet tube and two 1/4" flavor tubes route inside and exit at the printed tip. |
| Siptenk 1/4" OD brass tube stiffener × 1 | B0FM77LLM1 (100-pk) | Inside the carbonated-water LLDPE tube end that lands in the Westbrass body's upstream compression port, so the soft tube doesn't crush under the brass ferrule. Only one stiffener per build — the two flavor tubes do not enter any compression port and need no stiffener. |
| TPU above-counter gasket (printed) | [`/hardware/printed-parts/faucet/above-counter-gasket/`](/hardware/printed-parts/faucet/above-counter-gasket/) | Sits between the above-counter plate's underside and the countertop top surface. **Installed at this bench**, slid up the shank from below the plate during step 2 before the retained mount hardware and blue-tube connection go on. Stays permanently on the shank from this point forward. Customer never touches it. |
| Touch-Flo TPU O-ring (printed) | [`/hardware/printed-parts/faucet/tpu-o-ring/`](/hardware/printed-parts/faucet/tpu-o-ring/) | TPU 90A **thimble** (closed bottom with a Ø [6.5 mm](CAP_HOLE_D) centered hole, open top) that seats in the harvested Westbrass body's Ø [10 mm](BODY_PORT_D) top water port. Outer Ø [10.44 mm](ORING_OUTER_D) ([0.22 mm](BODY_SQUEEZE) radial squeeze against the port wall), cylinder ID Ø [9.2 mm](ORING_INNER_D) ([0.1625 mm](LLDPE_INTERFERENCE) interference grip on the 3/8" LLDPE OD), [15.6 mm](TOTAL_H) total height ([2.1 mm](ORING_CAP_T) cap + [13.5 mm](CYL_L) cylindrical sealing band). Two seals in series: radial compression along the cylinder + face seal where the LLDPE's bottom end presses against the cap; cap hole sized between LLDPE ID ([6.35 mm](LLDPE_ID)) and OD ([9.525 mm](LLDPE_OD)) so the tube bottoms out positively and water flows through the cap hole into the LLDPE bore. Install order: thimble cap-down into the port first, then push the 3/8" LLDPE down through the open top until it bottoms on the cap. Consumable — expect to use a fresh thimble on any future re-assembly. |
| 3/8" OD black LLDPE (soda faucet tube) | FWS 25 ft stock, purchase `WEBFWS100673540` ([`purchases.md`](/hardware/ledger/purchases.md)) | Internal to the faucet: sealed into the Westbrass's top water port by the TPU thimble, then routed through the center gooseneck channel to the printed tip. It is not an umbilical tail. |
| SendCutSend 0.060" 316 SS under-counter plate | `touch-flo-under-counter-plate.dxf` ([`/hardware/cut-parts/faucet/touch-flo-under-counter-plate/`](/hardware/cut-parts/faucet/touch-flo-under-counter-plate/)) | Single-piece Ø [54.45 mm](PLATE_D) disc whose hole positions match the TPU above-counter gasket exactly — Ø [12.6 mm](SHANK_HOLE_D) shank pocket and a [13.4 mm](PILL_L) × [7.05 mm](PILL_W) pill pocket (long axis along the plate DXF's Y — the shell's lateral X) at the same XY as the gasket — with two open-edge channels added: a [12.6 mm](SHANK_HOLE_D) wide channel from the shank pocket out to the rim in −Y, and a [7.05 mm](PILL_W) wide channel from the pill pocket out to the rim in −Y. The channels exit the rim at different X positions. The four wall-meets-rim corners are rounded with R [1.5 mm](FILLET_R) fillets. Order qty 1 per appliance. |
| 1/4" OD LLDPE, blue (carbonated water) | FWS neoFlo blue spool ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3) — one of the four the machine is plumbed in, per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) "Umbilical port — tube identification" | Cut to length once; color-coded blue to match the blue-ringed PP1208E bulkhead on the +Y wall of back-top, and the same blue as the riser inboard of it |
| 1/4" OD LLDPE, black (flavor lines) × 2 | FWS bulk spool ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3) | Cut to length once each; bare black, matches the two unmarked PP1208E bulkheads on the +Y wall of back-top |
| CARGEN nitrile foam pipe insulation, 1/4" ID × 3/8" wall, 1-ft segments | B0D2XFK337 ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9) | **Cold tube only.** Foam ships as 1-ft segments and is installed segment-at-a-time. Five segments per umbilical, covering 1425 mm of the blue tube |
| Cable sleeve — Alex Tech 1" PET expandable braid, five 1-ft segments | B075VRDS53 ([`bom.md`](/hardware/ledger/bom.md) §11 "Umbilical sleeve") | Over all three tubes + the signal cable, one segment to each foam segment, on the foam's own run. 1" nominal expanding 50%; the pack opens it to Ø[31.66 mm](SLEEVE_BORE). ~5 ft per build |
| Printed tube collar × 3 | [`/hardware/printed-parts/faucet/tube-collar/`](/hardware/printed-parts/faucet/tube-collar/README.md) | `tube-collar-carb` on the blue tail, `tube-collar-flavor-a` and `-flavor-b` on the two black. The +Y wall of back-top's own chip bored for the tube and run [30 mm](COLLAR_LENGTH) along it — same word, same spool, threaded on end-first up to the braid's own end. The other two stations' collars are in the install kit, for the runs the customer cuts |
| Umbilical signal cable (BNTECHGO 28 AWG 4-conductor ribbon) | B07PNPHWMG ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9) | Single run from the gooseneck faucet display down to the main board, carrying SIG-6 (faucet display: TX / RX / 5 V / GND). |
| 2× low-capacitance ESD TVS (ESD9B3.3-class / PESD3V3-class, SOD-923) — **optional** | onsemi ESD9B3.3ST5G or Nexperia PESD3V3L1BA (≤ 15 pF, 3.3 V, bidirectional) | **Optional** faucet-end ESD clamp (defense-in-depth only). The primary faucet-UART clamp is now on the main board (D10/D11 at U1), so a cable-end TVS is **not required** — fit only if a builder wants a second clamp at the user-touch source (see the ESD note below). |

Tooling (per-build-amortized only; single-asset tools live in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md), not here): Mudder PEX/PE tube cutter (also in the installer's install kit, [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14 — same cutter SKU lives in both places).

### Faucet-display ESD protection (on the board — no build step here)

The faucet display is the one user-touched surface on the appliance, at the far end of a ~1 m
umbilical — so its two TTL UART lines are the most ESD-exposed nets on the board. The **primary**
clamp is now **on the main board, at the ESP32**: each TTL line is clamped by a low-cap TVS shunting
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
  the main board already clamps the ESP32 pin.
- The 5 V and GND conductors are not clamped (rail + return); only the two TTL signals.

Full spec and part rationale: [`/hardware/assembly/cable-assemblies.md`](/hardware/assembly/cable-assemblies.md)
"Faucet-display ESD protection (SIG-6)", with the board placement in
[`/hardware/pcb/pcba/jlcpcb-parts.md`](/hardware/pcb/pcba/jlcpcb-parts.md) (D10/D11) and
[`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx) (FAUCET block).

## Procedure

### 1. Cut the three LLDPE tubes to length

Cut to **two** lengths: **2× black flavor at 1900 mm** and **1× blue carbonated-water at 1540 mm**. One cut per tube with the Mudder cutter, square-end, no burr.

The two terminate 362 mm apart inside the faucet. The flavor tubes run up the gooseneck's dispense channel to the printed tip — 311.74 mm of centreline above the above-counter plate, plus the 4 mm plate, the 2 mm TPU gasket and the countertop slab — while the blue tube lands on the Westbrass body's upstream compression port at the bottom of the shank, 44 mm *below* the countertop's top surface. That 362 mm is set by the faucet's own CAD and does not move with the kitchen. The two factory numbers round it to 360 — cut to them and all three tails land flush at the +Y wall of back-top within a couple of mm, so a blue tube that does not reach the bundle end is a mis-cut, visible before it is sleeved.

The design length sums a measured half and an assumed half:

| Term | mm | Basis |
|---|---:|---|
| Drop, countertop underside → appliance top plane | 418 | 34.5" carcass − 4" toe kick − 3/4" deck = 755.7 mm interior clear, less the enclosure height |
| Down the rear face to the flavor-bulkhead axis | 42 | CAD |
| Turn-in at the wall — lead + 90° at R12 + collet | [60](TURN_IN) | CAD |
| Horizontal inside the cabinet, faucet hole → drop line | 380 | 36" sink base: faucet on the sink centreline, appliance at one end |
| Service loop — the appliance comes forward to reach its own +Y wall of back-top | 300 | pull-forward to put the +Y wall of back-top at the cabinet face |
| **Below-counter subtotal** | **1200** | |
| Countertop slab | 30 | 3 cm stone (range 19–38) |
| TPU gasket + above-counter plate | [6](PLATE_GASKET) | CAD |
| Gooseneck centreline, shell foot → printed tip | 312 | CAD |
| **Flavor tube, nominal installed** | **1548** | |
| **Blue tube, nominal installed** | **1183** | its top end sits 14 mm below the countertop underside |

**Installer-trim allowance: 350 mm per tube**, held separately from the sum — 8 mm for a slab up to 38 mm, 25 mm for cabinet-height variance, 300 mm for an appliance at the far end of the sink base rather than the near end, 20 mm for two square cuts. Factory cut = nominal + allowance.

The installer makes a *second* cut on each tube at field install — trimming the +Y wall of back-top end to fit the customer's actual cabinet depth before pushing each tube into its PP1208E bulkhead. The factory length is sized long with that installer-trim allowance baked in; do not cut tight here.

### 2. Preload the mount hardware; route the tubes and SIG-6

The shell sub-assembly arrives from [`/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md) with the Westbrass body captured between the faucet shell and the above-counter plate. This step puts the retained donor mount hardware in its permanent captive state before any line blocks the end of the shank, then routes the three LLDPE tubes and fitted SIG-6 ribbon into their final positions. The three LLDPE tubes are the wet path end to end. The shell's CAD script describes the dispense channel and gooseneck geometry the three tubes route through.

- **Above-counter gasket.** Slide the TPU gasket up the still-bare shank until it sits flat against the above-counter plate. It stays there permanently.
- **Retained countertop hardware first.** Slide the donor washer onto the bare threaded shank, then thread the donor nut on loosely. Leave the clear gap above them that receives the countertop and the open under-counter plate at field install. From this point forward the washer and nut remain captive; they are never loose customer parts.
- **Carbonated water (blue tube).** Insert a Siptenk 1/4" brass stiffener fully into the blue LLDPE tube end that will land in the Westbrass body. Push that stiffened end into the Westbrass body's upstream compression port (the supply side that takes carbonated water *in*). The body's factory ferrule + nut clamp the LLDPE around the stiffener; hand-snug + 1/4 turn with a wrench.
- **Dispense water (3/8" tube).** Feed the 3/8" black LLDPE through the center gooseneck channel with its outlet proud of the printed tip. Seat a fresh TPU thimble cap-down in the body's top water port, then push the tube's lower end into the thimble until it bottoms on the cap. Square-cut the outlet flush with the printed tip.
- **Flavor lines (black tubes × 2).** Each black LLDPE tube routes through the shell's pill slot (which passes through both the above-counter plate and the TPU gasket per the upstream sub-assembly's ASSEMBLY.md step 6) up into the printed gooseneck's dispense channel, terminating at the printed tip. The tubes push through dry, retained by the channel's bore-to-OD interference fit at the dispense tip and by the pill slot's geometry at the bottom.
- **SIG-6 ribbon.** Land the faucet end on the faucet display and route the flat four-conductor ribbon through its designed passage beside the three tubes. The lower end is terminated at the main board during `wiring.md`. Both ends are factory work; the customer receives the ribbon assembled and physically fitted.

At the +Y wall of back-top end of all three tubes: **leave them bare and square-cut.** The installer pushes each tube directly into the matching PP1208E bulkhead's collet at field install; PP1208E's internal grab-ring + EPDM O-ring make the seal around the tube OD (same seal mechanism already in use on the reservoir-cap bulkhead per [`/hardware/printed-parts/cold-core/reservoir/reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py)).

### 3. Insulate and sleeve the run, a segment at a time

Per [`/hardware/printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) "Umbilical bundle construction": **foam goes on the blue tube only.** The carbonated-water tube is the temperature-critical run.

First lay the umbilical signal cable alongside the three tubes, so it is inside every braid segment that follows. It is the BNTECHGO 28 AWG 4-conductor ribbon and carries the SIG-6 faucet-display link (TX / RX / 5 V / GND) through the countertop, per [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md). It rides in the lane the braid leaves between itself and the tubes.

Then work up the run from the bare wall end, **one foam segment and one braid segment at a time**:

1. Slide a CARGEN foam segment up the blue tube to butt the one above it. The segments are a snug interference fit over 1/4" OD LLDPE; lubricate with a wipe of water if friction is high (no solvents — nitrile is solvent-sensitive). No gap at the butt.
2. Gather the three tubes into their triangular dense pack — three round tubes pack no other way — with the ribbon in the pack, and slide one braid segment up over all four to butt the braid segment above it.

Each braid segment crosses bare tube and its own foam, and nothing already seated. A segment cut to cover one foam segment when it is opened over the bundle is longer than the foam segment: braid shortens as it expands, and how much is a bench measurement on the first build.

**Five of each** for the standard build, covering 1425 mm of the blue tube's 1540 mm — bare 40 mm at the compression end and the last [75 mm](COLLAR_SLEEVE_TAIL) at the wall, where the installer flexes the three tubes apart for the three-bulkhead push-connect. A nominal kitchen keeps four; the installer pulls one whole foam segment and its braid segment off with the trim, which is what the 1-ft granularity buys.

Foam OD is 25.4 mm — it does not pass the countertop hole and does not need to, since the blue tube is entirely below the counter. The braid opens to Ø[31.66 mm](SLEEVE_BORE) over the pack, [99.47 mm](SLEEVE_GIRTH) of girth, and lies on the tubes rather than standing off them in a circle.

What the blue (foamed) tube carries is identification, not orientation — it goes into the blue-ringed union, which is the east end of the row.

### 4. Thread a collar onto each tail

Slide one printed collar down each tube from its bare rear-wall end: `carb` on the blue, `flavor-a` and `flavor-b` on the two black. A collar comes off the plate bored Ø[6.63](COLLAR_BORE_PRINTED) on Ø[6.35](COLLAR_TUBE_OD) LLDPE, so each goes on by hand down the whole [30 mm](COLLAR_LENGTH) of it. Nothing goes on with force here: a collar that needs it is bored under its figure, and forcing it scores the same stretch of tube that has to seal in the union.

Run each collar up the tube until it butts the braid's own end — [75 mm](COLLAR_SLEEVE_TAIL) short of the tail — and turn its flag outward, away from the bundle's axis, so no two face each other. The three come out level. Each stays where it is put on the bend the tube came off the spool with: the tube is never straight through [30 mm](COLLAR_LENGTH) of bore, so it stands against the wall at both ends of one. The installer's second cut is below all of them, so a trimmed tube keeps its collar.

The bundle, the sleeve over it and the three collars on the bare tails are drawn in [`/hardware/faucet-layout/faucet_assembly.py`](/hardware/faucet-layout/faucet_assembly.py), which carries the terminated end at full size and the metre and a half of straight between it and the faucet as a figure rather than a length.

### 5. Bag the sub-assembly with installer kit

Lay the bundled umbilical down with the faucet at one end and the three bare tube tails + lower signal-cable end at the other. Coil the umbilical loosely (8–12" loop diameter).

The TPU gasket is already on the shank from step 2 and is not in the install kit. Into the bag with the umbilical, add the install-kit parts the customer needs at countertop install:

- **One SendCutSend 0.060" 316 SS under-counter plate** — the single-piece plate that slides laterally onto the dangling umbilical from below at install.
- One Mudder PEX/PE tube cutter (the per-appliance install-kit tool from [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14, same SKU as the bench-side cutter)
- **Two printed tube collars — `tube-collar-water` and `tube-collar-co2`** ([`/hardware/printed-parts/faucet/tube-collar/`](/hardware/printed-parts/faucet/tube-collar/README.md)). The other two stations on that wall take a tube the customer cuts in their own kitchen: the tap-water run to their angle stop and the tether to their cylinder's regulator. Each collar threads onto its run and carries the station's word — `TAP`, `CO2` — to the end that has no ring on it

The customer-facing install instructions live in the visual quick start that ships at the top of the appliance carton ([`/hardware/quickstart/`](/hardware/quickstart/README.md)); its packing and content contract is [`/marketing/unboxing-and-quickstart.md`](/marketing/unboxing-and-quickstart.md).

Bag, seal, label with build number and the part identifier `FAUCET-UMBILICAL-SUBASSEMBLY`, set aside for [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md) (TBD).

## Output condition

A bagged sub-assembly that is:

- One above-counter fixture stack with the three umbilical tubes installed
- The umbilical is **permanently attached** to the faucet assembly — the blue carbonated-water tube is connected at the body's lower upstream compression port; a separate 3/8" soda faucet tube leaves the top port through the gooseneck; only the two black flavor tubes pass through the above-counter plate's pill slot and continue up the gooseneck. Below the counter, the three umbilical tubes share one sleeve with foam on the cold blue tube only and the fitted SIG-6 ribbon alongside.
- Three tubes terminated bare and square-cut at the +Y wall of back-top, ready for push-into-PP1208E at install
- One printed collar on each tail, below the sleeve's end and above the installer's trim — `SODA` on the blue, `FLAVOR` on each black, each in the colour of the ring its tube goes into
- SIG-6 ribbon assembled and fitted at the faucet; its lower end is terminated at the main board during `wiring.md` at appliance final assembly (the bagged sub-assembly is brought to the wiring bench, the lower end is terminated, and the bag re-closed for shipping). No signal conductor is cut or terminated in the field.
- TPU above-counter gasket already in place on the shank between the above-counter plate's underside and where the countertop top surface will be (installed at this bench, not in the install kit; customer never touches it)
- Retained donor washer and shank nut captive on the bare shank above the permanent blue-tube connection; the same nut is hand-tightened at field install
- Loose install-kit parts bagged together: **one SS under-counter plate**, Mudder tube cutter, and the two `TAP` and `CO2` tube collars
- Labeled, sealed, ready to drop into the appliance carton at [`finish-pack-ship.md`](/hardware/assembly/finish-pack-ship.md)

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_faucet_and_umbilical_sync.py`
