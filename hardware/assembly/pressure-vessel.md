# Pressure Vessel Fabrication

The production procedure for the carbonator pressure vessel — the 316L stainless body that holds carbonated water at the **[90 PSI](WORKING_PSI) working pressure** specified in [`/hardware/future.md`](/hardware/future.md) "Carbonation subsystem". This document is the repeatable procedure for taking commodity tube + cut plates to a hydro-tested, passivated vessel ready for the [refrigeration loop](/hardware/assembly/refrigerant-loop.md) downstream.

Design intent and material rationale live in [`/hardware/future.md`](/hardware/future.md). The dev-phase task summary lives in [`/hardware/handwork.md`](/hardware/assembly/handwork.md). Snapshots of single-event execution (the first tap, the first weld recipe) live in their own dated files and are referenced by step below.

## Scope

In: commodity 316L SS tube (OnlineMetals #12498) + laser-cut 316L SS end plates (SendCutSend [`endcap-circular-2hole.dxf`](/hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.dxf)) + the small parts listed under "Inputs" below.

Out: one vessel that has been tapped, welded, hydro-tested at the working-pressure-appropriate setpoint, passivated, and has the internal sparge stone + float assembly installed — ready for evaporator coil wrap.

Not in scope: the evaporator coil wrap itself (boundary with [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)), the cold-core foam pour ([`cold-core.md`](/hardware/assembly/cold-core.md)), and any system-level installation.

## Inputs per vessel

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §2 (carbonator vessel) + §12 (level sensing — the float rod + donut). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost. Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §1 (vessel fabrication), §16 (laser welding), §2 (CO2 subsystem), §4 (port-fittings including the new vessel-port elbows).

| Item | Source | Notes |
|---|---|---|
| 5" OD × 0.065" wall × [152.4 mm](TANK_H) 316L SS welded tube | OnlineMetals #12498 | MTRs required. |
| 1/4"-thick 316L SS circular end plate, 2-hole pattern | SendCutSend [`endcap-circular-2hole.dxf`](/hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.dxf) | 2 per vessel |
| 1/8" 316L SS rod, [131.1 mm (5.16 in)](ROD_LEN) cut from 12" stock | Tandefio B0CY4DWJFQ | Internal float rod (bom.md §12) |
| Magnetic float | Harvested from YXQ float switch B08HWRMRQR | Slides on rod, captive after top weld (bom.md §12) |
| 0.5 µm sintered 316 SS sparge stone (1/4" barb input) | FERRODAY B091C5Y6L9 | Internal CO2 sparge |
| Food-grade silicone tube stub, ~3" of 1/4" ID | Metaland B08L1ST6ST (cut from §5 stock) | Connects bottom-plate barb to sparge stone |
| 1/4" hose-barb × 1/4" MNPT 316 SS adapter | LTWFITTING B017N4TTMA | CO2 inlet barb, installed at sparge step |
| **TAISHER 316L SS 1/4" NPT 90° street elbow, M×F** | B0CZ38MYL1 (2-pk) | **4 per vessel — all four ports.** Turns the line laterally within the ~[30 mm](ELBOW_ENV) vertical envelope around the tank — see [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Tank-port fittings". SS-on-SS thread joints rely on the Millrose PTFE anti-seize tape (above) at every port. |
| **Control Devices SV-125 safety valve, 1/4" NPT, 125 PSI** | B01G2F6EMY (size SV-125) | **Port 4 dedicated PRV — installed after passivation per step 9 below, via the SS 90° elbow to orient the body laterally.** 125 PSI set pressure gives 1.39× margin over the [90 PSI](WORKING_PSI) working pressure. 49 SCFM relief capacity. |
| Millrose PTFE thread-seal tape | B07C9ZV4PG | Anti-seize for 4 NPT ports (test plugs during hydro + final fittings after passivation) |
| ER316L .030 filler wire | STARTECHWELD B09BKFBXT9 | Matches 316L parent metal. |
| Cambro 6 QT polycarbonate square container | B001BZEQ44 | Passivation soak tub, reused build-to-build (one on hand); a mild citric soak doesn't consume it |
| Viva Doria food-grade citric acid | B0C5NQM8S1 | Made up to ~4 % solution, ~1 qt per vessel (~1/20 of 2 lb bag) |
| Tap Magic EP-Xtra cutting fluid | B00DHMHSGM | ~$0.50 of fluid per vessel for NPT tapping |
| Cantesco P101S-A red visible dye penetrant (solvent-removable, aerosol) | B00T46ZH5E | Dye-penetrant (PT) weld inspection — step 6. One can does many vessels. |
| Cantesco D101-A non-aqueous wet developer (white, aerosol) | B008BJCOLK | PT developer — draws the penetrant back out of a defect as a visible red indication. |
| Lint-free cleanroom wipes, 9" × 9" (cellulose/polyester) | B0GD16CMYL | PT wipe-off + reading surface. Excess penetrant wiped with isopropyl alcohol (in stock) dampened on a wipe — never sprayed on the part. |

Tooling (per-vessel-amortized only — single-asset tools live in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md), not here): XLaserlab X1 Pro laser welder, WEN 4208T drill press, LingGan M35 cobalt 1/4-18 NPT pipe tap + Drill America DWT adjustable tap wrench, Brown & Sharpe spring tap guide, Drill Hulk 9/64" M35 cobalt drill bit (rod register), JNB Pro 82° M35 cobalt countersink set (port-hole chamfer, step 1), Noga NG8150 swivel-blade deburr tool (plate + tube edges, steps 1 and 3), 3M Scotch-Brite 7447 very-fine hand pads (weld-surface prep, step 3), argon at the welder, hydro test rig (see step 7).

## CO2 supply (sets working pressure)

The [90 PSI](WORKING_PSI) working pressure this procedure is sized against is set by an in-appliance Interstate Pneumatics WR1110 1/4" NPT [fixed-90 PSI](REG_FIXED) secondary regulator (B07J2L8LF3, [`bom.md`](/hardware/ledger/bom.md) §4) between the shipped Wellbom CGA-320 primary regulator (mounted on the customer's tank) and the vessel CO2 port. The WR1110 holds the appliance-side pressure at [90 PSI](WORKING_PSI) regardless of where the primary is set, eliminating customer-setpoint variance and adding a layer of safety on the highest-energy path in the appliance (the CO2-bottle pressure reservoir). Customer guidance: set the primary regulator anywhere in the 70–100 PSI range; the WR1110 takes care of the rest.

At the 5" OD × 0.065" wall geometry, hoop stress at [90 PSI](WORKING_PSI) is ~3,461 PSI — a ~5.8× safety factor against the 20,000 PSI allowable for 316L SS in vessel-grade service. The 35 PSI margin between the [90 PSI](WORKING_PSI) working setpoint and the SV-125 PRV (above) is the safety margin sized for normal-operation excursions.

## Procedure

### 1. Prepare both plates — chamfer ports, tap NPT, drill the rod register, break the OD edge

**Chamfer the port holes before any tap touches them.** The four 7/16" tap-drill holes arrive laser-cut ([`endcap_circular_dxf.py`](/hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py)), which leaves a recast lip at the cut. Break both faces of every hole with the JNB Pro 82° countersink under the drill press. Use the 5/8" or 3/4" body — a 1/2" body spans only 0.031" over the 0.438" hole and leaves no room to set chamfer width deliberately. Run the press slow with Tap Magic; the 5-flute grind chatters if crowded. The chamfer clears the cut lip and gives the taper tap a square seat to start in, which is what keeps the first threads concentric with the hole.

Hand-tap 1/4"-18 NPT in all four port positions — 2 ports per plate × 2 plates per vessel. Target 4.5 turns of engagement, with a 1/4" NPT test fitting snug-firm at 2-3 threads showing.

The first-tap rig and hand sequence are captured in [`/hardware/tapping-plan-2026-05-03.md`](/hardware/snapshots/tapping-plan-2026-05-03.md) (point-in-time snapshot of the first tap into a 316L plate). That snapshot is single-use Baltic-birch + MDF; the production fixture for the full per-vessel × 10-vessel batch is a downstream design step — see "Open items" below.

**Plate clocking.** Both plates are welded with their port pairs on the same axis, and the rod register — at right angles to each plate's own pair — is what holds them together: the rod is tack-welded into the bottom plate's register and must enter the top plate's at closure, so a plate turned relative to the other has no register to meet. That register is what clocks the two plates to each other, and it is what leaves the vessel ONE port axis instead of two. In the cold core that axis is the foam shell's **±Y** (`_cold_core_interface.vessel_port_offset`). Nothing above the vessel has to stand over a port to be fed: every port turns its line laterally at its own elbow (step 9), so the top cap's water-inlet conduit stands where the run above the lid wants it and reaches the plate through the band under the cap floor ([`cold-core.md`](/hardware/assembly/cold-core.md) step 5).

**Rod register (both plates, same drill-press setup, before any welding).** Drill the level-sensing rod register into the **inside** face: a blind **9/64" hole, 0.10" deep to the drill-point tip**, at **(0, −2.007")** — on the −Y cap axis, clear of both ports. Position / diameter / depth are the source-of-truth constants in [`endcap_circular_dxf.py`](/hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py); the cap drawing carries the REF callout (Note 6). The 0.10" depth leaves 0.15" of the 1/4" plate intact — **this hole must not break through; it is part of the [90 PSI](WORKING_PSI) pressure boundary.** Clamp the disc, run the press at its slowest speed (~740 RPM) with Tap Magic, set the depth stop to 0.10" (to the tip), and prove it on a scrap disc before a real plate. Both plates get the identical hole: the **bottom**-plate register seats and squares the rod for its tack weld (step 2); the **top**-plate register captures the rod tip at closure (step 5). Drilling now — before welding and before the citric passivation (step 8) — lets the fresh-cut 316L passivate with the rest of the vessel.

**Break the plate OD edge — asymmetrically.** Run the Noga NG8150 around the laser-cut perimeter, treating the two faces differently, because only one of them is a weld surface:

- **Inside face** (the register face, above). This edge leads as the plate is pushed down the bore at steps 3 and 5. Chamfer it freely — it is a lead-in that lets the plug find center in the ~0.005" radial slip, and it ends up inside the vessel where no beam reaches it.
- **Outside face.** Break the burr only, no chamfer. This edge is the fillet root: the corner it forms with the tube bore is exactly what the weld fills at steps 3 and 5. Chamfering it widens the root gap the laser has to bridge, working against the penetration the joint depends on.

The register drilled above is what distinguishes the two faces, so each plate carries its own orientation from this step forward. Mark the outside face if the register is not obvious at a glance on the bench.

### 2. Tack-weld float rod to bottom plate

Cut the 1/8" 316L rod to [131.1 mm (5.16 in)](ROD_LEN) — tube length − both 1/4" recesses − both 1/4" plates + both 0.10" registers − 1 mm clearance, with each plate recessed 1/4" below its tube end (`_pressure_vessel_sync.py`). Tack-weld it vertically to the inside face of the bottom plate (the side that will face into the vessel), seating its base in the bottom-plate register from step 1 — the register locates the rod on the donut-wall axis and holds it square for the tack. Set the final rod length so that, fully seated at the bottom, its top will enter the top-plate register at closure (step 5) **without** bottoming out and holding the top plate off its seated depth — the rod locates the plate, it must never hold the fillet root open. Done in the same welding session as the plate-to-tube welds in steps 3 and 5 — heat the welder once.

### 3. Weld bottom plate to tube

**Deburr both tube ends first, ID and OD.** Noga NG8150, both ends in one sitting while the tube is still loose and easy to turn. This is a clearance operation, not a fusion one — the cut edge is not a weld surface, since the fillet sits 1/4" below it. What it buys is insertion: the plate has only ~0.005" of radial slip, and a rolled-over saw burr is enough to catch a plate part-way down and hold it off its seated depth, which the corner geometry below depends on. Keep the chamfer light — the 0.065" wall has little to give.

**Prep the two surfaces the fillet actually sees.** Those are the tube bore, for the 1/4" band below each end, and the plate's outer face out to its perimeter. Not the tube's cut edge and not the plate OD — both are buried in the slip joint. Either the X1 Pro's cleaning mode or ~30 s per joint with a Scotch-Brite 7447 pad reaches both; what the joint needs is clean bare metal, not tooth. Stay off coarse grit on the plate's outer face — that perimeter edge is the fillet root, and an 80-120 grit pass rounds the very corner the weld is there to fill, undoing the burr-break-only treatment from step 1. Keep the pads segregated as stainless-only: embedded free iron rusts and outlives the citric passivation at step 8.

**Joint — ID-fit plug recessed 1/4", closed with a corner fillet.** The end plate is an ID-fit plug: its OD is sized just under the tube ID for a ~0.005" radial slip ([`endcap_circular_dxf.py`](/hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py)). Seat it **recessed 1/4"** — outer face 1/4" below the tube end — so the tube wall stands 1/4" proud and the wall ID plus the plate's outer face form an internal corner. Weld a fillet into that corner. This is the joint the XLaserlab X1 Pro runs best and the most forgiving for a hand weld: the beam fires into the corner onto the thick plate mass — which absorbs the energy and backs the puddle — and washes onto the tube-wall side, instead of trying to fuse the bare 0.065" tube-end edge, which a focused laser tends to cut back rather than fuse. Set the recess depth with a 1/4" spacer / depth-stop on the rim so every plate seats at the same depth (repeatability across the batch). Drive enough penetration to fuse the corner fully and seal the ~0.005" slip gap; the PT check (step 6) + hydro test (step 7) confirm it (a defect weeps up the slip gap to the rim). Keep heat moving — the proud 1/4" lip is unbacked above the weld and will distort if you dwell.

Close one end of the tube with the bottom plate, float rod sticking up into what will become the interior. Current weld recipe: power 60 %, wobble 80 Hz × 2 mm, wire feed 12 mm/s, argon 2 s pre/post, ER316L .030 filler, 8-tack opposite-side-bisecting pattern, trail-off motion at end of bead, joint surfaces prepped per above. Wire-stick fix: keep the trigger held and lift straight up at end of bead — the retract/patch cycle fires after conductance breaks in mid-air, so the wire never re-fuses to a still-molten puddle ([`/marketing/video/dont-let-go.md`](/marketing/video/dont-let-go.md)).

Yellow/brown coloration on the inside surface is acceptable at this stage — chromium oxide under partial argon protection, dissolves in the citric-acid passivation downstream (step 8). Black scale is not acceptable; if seen, increase argon coverage or add an internal back-purge.

### 4. Install magnetic donut float

Slide the donut float over the rod through the still-open top of the tube. After step 5 it is captive between the rod tack at the bottom plate and the rod-end register on the top plate's inside face.

### 5. Weld top plate to tube

Close the open end with the top plate. The blind register drilled into its inside face (step 1) captures the rod's top end as the plate seats to its 1/4" recess — confirm the plate reaches its seated depth against the spacer / depth-stop (the rod must not hold it proud; see the rod-length note in step 2). If the register binds on the rod tip, open that one cap's pocket to 5/32" rather than forcing the plate down — the plate-to-tube joint here is a pressure weld. Same recessed corner fillet as step 3.

### 6. Dye-penetrant (PT) inspection of the closure welds

A surface-NDE pre-screen of the two closure fillet welds before committing to hydro — solvent-removable visible dye, run on the bare welds while they are clean and dry (before any water touches them). It finds and *localizes* surface-breaking lack-of-fusion, cracks, and pinholes, which the hydro test (step 7) alone won't.

1. **Clean + dry.** Wipe the weld and the rim slip-gap line with isopropyl alcohol on a lint-free wipe; let it flash off. PT needs a clean, dry surface.
2. **Penetrant.** Spray Cantesco P101S-A on both rim fillets (and the port-weld areas), dwell ~10 min so it wicks into any defect.
3. **Remove excess.** Wipe off with a **dry** lint-free wipe first, then a wipe **lightly dampened** with IPA — never spray solvent onto the part or flood it, which flushes dye back out of fine defects and hides them.
4. **Develop + read.** Mist a thin coat of Cantesco D101-A developer; read within ~10 min. A red **line** bleeding through the white = a crack or lack-of-fusion (watch the fillet toe and the slip-gap line at the rim); red **dots** = porosity/pinholes; clean white = sound.
5. **Defect → re-weld.** Clean the area, re-weld the indicated spot, and re-PT before moving on. Wipe all penetrant + developer off with IPA before hydro.

PT finds only surface-breaking defects; the **hydro test (step 7)** is the volumetric pressure proof. Standard-grade chemicals are fine here — the downstream water rinse + citric passivation (step 8) strips any sulfur/chloride residue from the stainless.

### 7. Hydro test

Hydro-test the fully welded + tapped vessel — bare, on a bench, with NPT plugs in all four ports. No PRV, no fittings, no cold core, no refrigerant loop. The test is a pre-passivation, pre-assembly bench operation.

Hold pressure: **180 PSI for 30 minutes** (~2× the [90 PSI](WORKING_PSI) working pressure). Beyond the 30-minute minimum, the in-vessel SENCTRL gauge (below) supports hour-scale leak soaks for catching slow weep before passivation.

**Hydro test rig — committed in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §1, all ACQUIRED:**
- **Pressure source:** BEAMNOVA hydrostatic test pump, 0–726 PSI, 3.17 gal reservoir, 1/4" hydraulic hose w/ 1/2" gasket-swivel end. The 180 PSI hydro target reads at ~25 % of the pump's scale — comfortable working range.
- **Pump-to-vessel adapter:** KOOTANS 1/2" NPT male × 1/4" NPT male brass reducing hex nipple (4-pack). 1/2" end seals against the BEAMNOVA swivel gasket; 1/4" end takes PTFE tape and threads into the vessel port.
- **In-vessel soak gauge:** SENCTRL 0–200 PSI glycerin-filled, 2.5" dial, 1/4" NPT lower mount, SS case. Leaves on a vessel port across hour-scale leak soaks for fine-resolution drift. At 180 PSI test the gauge sits at 90 % of scale — above the 60-75 % textbook sweet spot, but still within working range.
- **Port plugs:** ChillWaves brass 1/4" NPT outer-hex pipe plugs (12-pack), rated 1200 PSI — way over the test pressure. The pump takes one port and the soak gauge another, so two plugs hold the rest.
- **Post-hydro pneumatic-leak rig (separate step, post-validation):** Milton 727 industrial M-STYLE® 1/4" MNPT air plug 10-pack — threads into a vessel port and mates with a standard air-compressor coupler for a follow-on pneumatic leak check on vessels that already passed hydro.

**Pass criteria — open.** Working position is "no visible drop on the SENCTRL gauge, no visible weep at welds or threads." Whether to commit to a specific PSI-drop tolerance over the hold is undefined.

**Failure handling — open.** A vessel that weeps at a bead surface is plausibly re-weldable; a weep through parent metal or HAZ is scrap; a vessel that won't hold pressure with no visible weep most likely has a thread leak at a port. The decision tree is undefined.

### 8. Citric acid passivation

One-time soak in ~4 % food-grade citric acid solution, 30-60 minutes, in the reusable polycarbonate tub sized for the vessel. Followed by thorough water rinse.

Restores the chromium oxide layer at the weld zones — what makes 316L resistant to pitting from carbonic acid in long-life carbonated-water service. The yellow/brown weld coloration from step 3/5 dissolves out during this soak. Same treatment commercial brewery bright tanks and commercial carbonators receive.

Done after hydro because failures get re-welded (re-introducing oxide that the passivation needs to handle) and before sparge install because the silicone tube and sintered stone don't belong in a citric soak.

### 9. Install elbows, sparge stone, PRV

After passivation, the vessel receives its permanent port fittings. Per [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Tank-port fittings", every port gets a 1/4" NPT 90° elbow as the first downstream fitting, turning the line laterally so the rest of the stack fits within the ~[30 mm](ELBOW_ENV) vertical envelope above and below the tank.

All four ports get a TAISHER 316L SS elbow. MNPT into the plate's FNPT, Millrose PTFE anti-seize tape on every joint. Downstream stack varies by port:

- **Port 2 (food-contact water inlet, top plate):** the elbow is the first fitting, turning the line laterally into the band under the cap floor. Its downstream PP010822E PTC adapter installs during cold-core integration per [`cold-core.md`](/hardware/assembly/cold-core.md) step 5 — connects to the elbow's lateral FNPT, collet turned into the band the line runs before it climbs the cap's conduit.
- **Port 3 (food-contact carbonated-water outlet, bottom plate):** the elbow is the first fitting. Its downstream PP010822E PTC adapter installs during cold-core integration per [`cold-core.md`](/hardware/assembly/cold-core.md) — connects to the elbow's lateral FNPT.

- **Port 4 (top-plate PRV):** The PRV must have an unobstructed path to the vessel interior at all times — no tee, no shared line. A blockage, fitting failure, or maintenance disconnect on a shared line would compromise the safety relief path. The dedicated-elbow-on-dedicated-port architecture satisfies this. Thread the M-end of the **pre-built [`prv-shroud`](/hardware/printed-parts/cold-core/prv-shroud/) subassembly** into Port 4 FNPT, PTFE tape on the threads. The subassembly = TAISHER M×F elbow + SV-125 + printed shroud + cured silicone caulk seal at the shroud-elbow joint, built independently per the prv-shroud README's "Subassembly procedure" before this step (no prerequisites; the subassembly can be built whenever and sits ready). PRV body extends horizontally inside the shroud, fitting within the cylindrical foam-shell's headroom. The shroud preserves the air cavity around the SV-125's discharge side port and bonnet windows during the body foam pour ([`cold-core.md`](/hardware/assembly/cold-core.md) step 6), so the valve remains a functional relief device after the cold-core is cast.

- **Port 1 (bottom-plate CO2 inlet + internal sparge):** the LTWFITTING B017N4TTMA hose-barb × MNPT adapter handles the internal sparge — barb facing inward, food-grade silicone tube stub connecting it to the FERRODAY B091C5Y6L9 0.5 µm sintered SS sparge stone hanging in the water column. The SS 90° elbow handles the external CO2 line connection from the in-appliance WR1110 secondary regulator (see [`/hardware/future.md`](/hardware/future.md) "CO2 supply"). **The relative install order of LTWFITTING vs elbow on Port 1 is an open item** — see Open items below.

Once the four elbow stacks are in, the vessel is the input to [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) step 4 (coil wind).

### 10. (Optional) Functional pop test against vessel pressure

The mandatory PRV mechanism-free check is the **pull-test inside the prv-shroud subassembly procedure** ([`/hardware/printed-parts/cold-core/prv-shroud/README.md`](/hardware/printed-parts/cold-core/prv-shroud/README.md) "Subassembly procedure" step 2), performed during subassembly build before the shroud is glued on. By the time the subassembly threads into Port 4 at step 9, the pull-ring is permanently enclosed in the shroud and no further manual access is available.

This optional step adds a **functional pop test against pressure** — confirming the SV-125's setpoint is in spec, not just that the mechanism moves freely. Re-use the BEAMNOVA hydro rig from step 7, with the subassembly threaded into Port 4 and the other three ports plugged. Ramp pressure on one of the plugged ports until the PRV cracks — audible pop, gas vented through the shroud's LLDPE port (or out the open cap hole if LLDPE isn't installed yet). Crack pressure should fall within ±3 % of 125 PSI (i.e., 121–129 PSI). The SV-125's silicon O-ring reseats cleanly within ±10 % of setpoint per the manufacturer's spec, so a single bench pop does not degrade the seat for service.

Optional because the pull-ring test in the subassembly procedure confirms the load-bearing mechanism-free property, and the manufacturer's ASME UV mark implies factory setpoint verification; the functional pop only adds confidence that the spring + seat were factory-set within spec on this particular unit.

## Output condition

A finished vessel is:

- Fully welded, hydro-tested, no visible weep
- PT-inspected at the closure welds — no surface-breaking indications
- Tapped with four clean 1/4" NPT ports
- Citric-acid passivated, rinsed dry
- Sparge stone + silicone tube installed via bottom CO2 port
- Float rod welded into bottom plate; magnetic donut captive
- PRV pull-ring tested free and snappy during prv-shroud subassembly build (per that part's README, step 2)
- Externally clean — no scale, no flux, no oxide bloom

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Hydro pass/fail criteria.** No committed PSI-drop tolerance over the 30-min hold.
2. **Hydro failure handling.** Re-weld vs. scrap decision tree, especially for marginal cases (faint weep, slow drift).
3. **Weld inspection acceptance criteria.** The dye-penetrant method + materials are now defined (step 6); the accept/reject criteria for an indication are not — max acceptable porosity/pinhole size, linear-vs-rounded handling, and whether a post-hydro PT re-check is also required. Define against a written standard before unit 1.
4. **X1 Pro weld recipe end-to-end validation.** The recipe in §3 is what we run on unit 1's vessel — same 60 % / 12 mm/s / 8-tack pattern / Don't-Let-Go trigger handling — but it hasn't been run end-to-end on 316L production stock yet. The 304L practice fixtures were where the recipe was developed; first 316L production weld is unit 1.
5. **Port 1 elbow + LTWFITTING install sequence.** [`/hardware/future.md`](/hardware/future.md) "Port 1" describes the LTWFITTING with barb facing inward and MNPT side threaded into the plate. Two assembly orders are geometrically defensible: (a) LTWFITTING first, SS elbow's FNPT threading onto LTWFITTING's externally-protruding MNPT remainder; (b) SS elbow first into Port 1 FNPT, LTWFITTING's MNPT then threading into the elbow's lateral FNPT with the barb on the elbow's lateral side. Path (a) gives a vertical elbow stack on Port 1's exterior; path (b) keeps everything at the elbow's lateral plane. Pick after the elbows are in hand and the LTWFITTING's thread length vs plate thickness can be measured against a fitting.

6. ~~**Reed azimuth ↔ register azimuth.**~~ **CLOSED.** `register_position` stays on the cap's −Y axis, 90° from the port line — that is what keeps the rod, and the donut hanging on it, out from under the top-plate water-inlet jet and off the bottom-plate outlet's draw. In the shell that port line lies on the Y axis: the bottom-plate CO2 elbow descends the notch cut inward from +Y at x = 0, and the carbonated-water outlet exits the −Y wall at x = 0 (`_port_cuts.py`). So the register azimuth is the shell's **±X** line — the only quadrant pair on the vessel OD carrying no penetration, no fitting and no notch, and the one place the reed bridge's 51 mm of arc × 70 mm of height actually exists. Clock it to the reservoir-B side so the carbonator reeds leave the cold core beside reservoir B's, both on J7; the two vessel rotations 180° apart are indistinguishable at the plates, so the clocking is free. The donut's 3 mm wall preload makes azimuth forgiving — 0.7 mm of added gap at 5 mm of arc — while height is not. Mount, heights and tolerances: [`reed-bridge/README.md`](/hardware/printed-parts/cold-core/reed-bridge/README.md).
7. **Production tapping fixture.** The rig in [`/hardware/tapping-plan-2026-05-03.md`](/hardware/snapshots/tapping-plan-2026-05-03.md), cited in step 1, is a single-use Baltic-birch + MDF snapshot of the first tap into a 316L plate. A fixture that holds a plate square and repeatable across the full 4-ports × 10-vessels batch — plate register, tap-axis guide, and whether it drives a hand tap or a machine tap — is still to be designed. Design it before the batch, not during it.

8. **Recessed-port fitting + foam clearance.** With each end plate seated 1/4" below its tube end (step 3), the four NPT ports sit 1/4" down inside the bore and the tube wall stands 1/4" proud past each plate. The proud lip (4.87" ID) clears the fitting bodies radially with room to spare, but confirm the TAISHER elbow stacks thread and seat correctly with the ports recessed, and that the proud lip doesn't foul the foam-shell envelope, before committing the batch.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_pressure_vessel_sync.py`
