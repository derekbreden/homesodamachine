# Pressure Vessel Fabrication

The fabrication and first-article qualification procedure for the carbonator — the 316L stainless body supplied at the **nominal [90 PSI](WORKING_PSI) CO2 feed setting** specified in [`/hardware/README.md`](/hardware/README.md) "Carbonation". That setting does not establish the carbonator's maximum pressure or pressure rating. Its water inlet is a drilled jet cap welded onto the male end of the top inlet elbow; CO2 enters through the plain bottom inlet elbow. The jet fit, its weld procedure, and integrated carbonation performance are unvalidated.

Design intent and material rationale live in [`/hardware/README.md`](/hardware/README.md). The dev-phase task summary lives in [`/hardware/handwork.md`](/hardware/assembly/handwork.md). Snapshots of single-event execution (the first tap, the first weld recipe) live in their own dated files and are referenced by step below.

## Scope

In: commodity 316L SS tube (OnlineMetals #12498) + laser-cut 316L SS end plates (SendCutSend [`endcap-circular-2hole.dxf`](/hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.dxf)) + the small parts listed under "Inputs" below.

Out: one tapped, welded, hydro-tested and passivated carbonator with its captive float, four port elbows and qualified water-inlet jet — ready for evaporator coil wrap. The two end plates are the identical purchased SendCutSend blanks, each with two 7/16-inch tap-pilot holes; the port pattern and foam-shell envelope are unchanged.

The refill pump is the G Ganen B07F35PTFR diaphragm pump, powered by the existing Mean Well supply. Its flow through the jet against carbonator pressure is a bench reading still to be made. The conditional higher-pressure arrangement and its decision criteria live in [`future/carbonation-plan-b.md`](/future/carbonation-plan-b.md).

Not in scope: the evaporator coil wrap itself (boundary with [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)), the cold-core foam pour ([`cold-core.md`](/hardware/assembly/cold-core.md)), and any system-level installation.

## Inputs per carbonator

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §2 (carbonator) + §12 (level sensing — the float rod + donut). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost. Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §1 (carbonator fabrication), §16 (laser welding), §2 (CO2 subsystem), §4 (port-fittings including the new carbonator-port elbows).

| Item | Source | Notes |
|---|---|---|
| 5" OD × 0.065" wall × [152.4 mm](TANK_H) 316L SS welded tube | OnlineMetals #12498 | MTRs required. |
| 1/4"-thick 316L SS circular end plate, 2-hole pattern | SendCutSend [`endcap-circular-2hole.dxf`](/hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.dxf) | 2 per carbonator |
| 1/8" 316L SS rod, [131.1 mm (5.16 in)](ROD_LEN) cut from 12" stock | Tandefio B0CY4DWJFQ | Internal float rod (bom.md §12) |
| Magnetic float | Harvested from YXQ float switch B08HWRMRQR | Slides on rod, captive after top weld (bom.md §12) |
| Water-inlet jet cap, 316 SS | Hosifiy B0FYCJJXCS, nominal 9.5 mm round stock | One drilled slice welded onto Port 2's elbow, fabricated and qualified per [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md). Candidate thickness 2 mm and bore 1/16 inch; cap OD is subject to measured fitting clearance. |
| **TAISHER 316L SS 1/4" NPT 90° street elbow, M×F** | B0CZ38MYL1 (2-pk) | **4 per carbonator — all four ports.** Port 2 carries the jet cap; the other three are plain. Each male end enters its plate from outside. The lateral stacks occupy the ~[30 mm](ELBOW_ENV) envelope above and below the carbonator — see [`foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Carbonator-port fittings". Millrose PTFE tape on every NPT joint. |
| **Control Devices SV-125 safety valve, 1/4" NPT, 125 PSI** | B01G2F6EMY (size SV-125) | **Port 4 dedicated PRV — installed after passivation per step 9 below, via the SS 90° elbow to orient the body laterally.** The 125 PSI set pressure is 1.39× the nominal [90 PSI](WORKING_PSI) CO2 feed setting; that ratio is not a vessel safety factor. 49 SCFM relief capacity. |
| Millrose PTFE thread-seal tape | B07C9ZV4PG | Anti-seize for 4 NPT ports (test plugs during hydro + final fittings after passivation) |
| ER316L .030 filler wire | STARTECHWELD B09BKFBXT9 | Matches 316L parent metal. |
| Cambro 6 QT polycarbonate square container | B001BZEQ44 | Reusable passivation tub; bath condition and reuse limits need qualification |
| Viva Doria food-grade citric acid | B0C5NQM8S1 | Made up to ~4 % solution, sufficient to contact all interior and exterior surfaces |
| Tap Magic EP-Xtra cutting fluid | B00DHMHSGM | ~$0.50 of fluid per carbonator for NPT tapping |
| Cantesco P101S-A red visible dye penetrant (solvent-removable, aerosol) | B00T46ZH5E | Dye-penetrant (PT) weld inspection — step 6. One can does many carbonators. |
| Cantesco D101-A non-aqueous wet developer (white, aerosol) | B008BJCOLK | PT developer — draws the penetrant back out of a defect as a visible red indication. |
| Lint-free cleanroom wipes, 9" × 9" (cellulose/polyester) | B0GD16CMYL | PT wipe-off + reading surface. Excess penetrant wiped with isopropyl alcohol (in stock) dampened on a wipe — never sprayed on the part. |

Tooling (per-carbonator-amortized only — single-asset tools live in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md), not here): XLaserlab X1 Pro laser welder, WEN 4208T drill press, LingGan M35 cobalt 1/4-18 NPT pipe tap + Drill America DWT adjustable tap wrench, Brown & Sharpe spring tap guide, Drill Hulk 9/64" M35 cobalt drill bit (rod register), JNB Pro 82° M35 cobalt countersink set (port-hole chamfer, step 1), Noga NG8150 swivel-blade deburr tool (plate + tube edges, steps 1 and 3), 3M Scotch-Brite 7447 very-fine hand pads (weld-surface prep, step 3), Knipex 70 11 110 diagonal cutters and 1/4"-shank flap wheels in a drill (stuck wire, step 3), argon at the welder, hydro test rig (see step 7).

## CO2 supply and pressure protection

The CO2 path runs from the cylinder-mounted Wellbom primary regulator through the in-machine Interstate Pneumatics WR1110 1/4" NPT [fixed-90 PSI](REG_FIXED) secondary regulator (B07J2L8LF3, [`bom.md`](/hardware/ledger/bom.md) §4) to the bottom CO2 port. The WR1110's nominal outlet setting is [90 PSI](WORKING_PSI); it needs sufficient inlet pressure and flow to maintain that setting. A lower primary setting limits the available supply, and the actual carbonator pressure is measured at the bench.

**The regulator is not a carbonator pressure ceiling.** Water entering during refill compresses the headspace; heating and regulator faults can also raise pressure. The dedicated SV-125 relief path remains open directly to the carbonator through Port 4. Its 125 PSI setpoint is separate from the regulator's nominal operating setting. Relief suitability and capacity must cover both the water and CO2 sources, including any conditional pump change.

For the cylindrical wall alone, a thin-wall estimate using the 5-inch OD gives approximately 3,460 PSI hoop stress at the [90 PSI](WORKING_PSI) reference pressure. That calculation does not establish the allowable pressure of the flat plates, tapped ports, closure welds or completed carbonator. The specified 180 PSI hydro hold is a fabrication proof test, not a derivation of a pressure rating or operating setpoint.

## Procedure

### 1. Prepare both plates — chamfer ports, tap NPT, drill the rod register, break the OD edge

**Chamfer the port holes before any tap touches them.** The four 7/16" tap-drill holes arrive laser-cut ([`endcap_circular_dxf.py`](/hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py)), which leaves a recast lip at the cut. Break both faces of every hole with the JNB Pro 82° countersink under the drill press. Use the 5/8" or 3/4" body — a 1/2" body spans only 0.031" over the 0.438" hole and leaves no room to set chamfer width deliberately. Run the press slow with Tap Magic; the 5-flute grind chatters if crowded. The chamfer clears the cut lip and gives the taper tap a square seat to start in, which is what keeps the first threads concentric with the hole.

Identify each plate's outside face, then hand-tap 1/4"-18 NPT from that face in both port positions — 2 ports per plate × 2 plates per carbonator. Each finished port receives one male elbow from outside. Target 4.5 turns of engagement, with a 1/4" NPT test fitting snug-firm at 2-3 threads showing; verify actual elbow engagement and final clocking on a trial before the batch.

Trial-fit the water-inlet jet elbow through its loose top plate per [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md). Confirm cap/weld clearance and a jet exit into headspace. Remove the elbow before the closure welds and bare-carbonator hydro test. A finished port is tapped through a [⌀11.13 mm (0.438")](PORT_BORE) pilot; that pilot diameter is not a measured clearance for the completed cap or weld.

The first-tap rig and hand sequence are captured in [`/hardware/tapping-plan-2026-05-03.md`](/hardware/snapshots/tapping-plan-2026-05-03.md) (point-in-time snapshot of the first tap into a 316L plate). That snapshot is single-use Baltic-birch + MDF; the production fixture for the full per-vessel × 10-vessel batch is a downstream design step — see "Open items" below.

**Plate clocking.** Both plates are welded with their port pairs on the same axis, and the rod register — at right angles to each plate's own pair — is what holds them together: the rod is tack-welded into the bottom plate's register and must enter the top plate's at closure, so a plate turned relative to the other has no register to meet. That register is what clocks the two plates to each other, and it is what leaves the carbonator ONE port axis instead of two. In the cold core that axis is the foam shell's **±Y** (`_cold_core_interface.carbonator_port_offset`). Nothing above the carbonator has to stand over a port to be fed: every port turns its line laterally at its own elbow (step 9), so the top cap's water-inlet conduit stands where the run above the lid wants it and reaches the plate through the band under the cap floor ([`cold-core.md`](/hardware/assembly/cold-core.md) step 5).

The register is on the cap's −Y axis, 90° from its port line, keeping the rod and donut clear of the water-inlet jet and outlet draw. In the foam shell this is the ±X line. Clock the rod to the reservoir-B side so the carbonator reeds leave the cold core beside reservoir B's, both on J7. The reed mount and height tolerances are in [`reed-bridge/README.md`](/hardware/printed-parts/cold-core/reed-bridge/README.md).

**Rod register (both plates, same drill-press setup, before any welding).** Drill the level-sensing rod register into the **inside** face: a blind **9/64" hole, 0.10" deep to the drill-point tip**, at **(0, −2.007")** — on the −Y cap axis, clear of both ports. Position / diameter / depth are the source-of-truth constants in [`endcap_circular_dxf.py`](/hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py); the cap drawing carries the REF callout (Note 6). The 0.10" depth leaves 0.15" of the 1/4" plate intact — **this hole must not break through; it forms part of the carbonator pressure boundary.** The nominal [90 PSI](WORKING_PSI) CO2 feed setting does not rate that boundary. Clamp the disc, run the press at its slowest speed (~740 RPM) with Tap Magic, set the depth stop to 0.10" (to the tip), and prove it on a scrap disc before a real plate. Both plates get the identical hole: the **bottom**-plate register seats and squares the rod for its tack weld (step 2); the **top**-plate register captures the rod tip at closure (step 5). Drilling now — before welding and before the citric passivation (step 8) — lets the fresh-cut 316L passivate with the rest of the carbonator.

**Break the plate OD edge — asymmetrically.** Run the Noga NG8150 around the laser-cut perimeter, treating the two faces differently, because only one of them is a weld surface:

- **Inside face** (the register face, above). This edge leads as the plate is pushed down the bore at steps 3 and 5. Chamfer it freely — it is a lead-in that lets the plug find center in the ~0.005" radial slip, and it ends up inside the carbonator where no beam reaches it.
- **Outside face.** Break the burr only, no chamfer. This edge is the fillet root: the corner it forms with the tube bore is exactly what the weld fills at steps 3 and 5. Chamfering it widens the root gap the laser has to bridge, working against the penetration the joint depends on.

The register drilled above is what distinguishes the two faces, so each plate carries its own orientation from this step forward. Mark the outside face if the register is not obvious at a glance on the bench.

### 2. Prepare the bottom plate — tack the float rod

Cut the 1/8" 316L rod to [131.1 mm (5.16 in)](ROD_LEN) — tube length − both 1/4" recesses − both 1/4" plates + both 0.10" registers − [1 mm](ROD_CLEARANCE) clearance, with each plate recessed 1/4" below its tube end (`_pressure_vessel_sync.py`). Tack-weld it vertically to the inside face of the bottom plate (the side that will face into the carbonator), seating its base in the bottom-plate register from step 1 — the register locates the rod on the donut-wall axis and holds it square for the tack. Set the final rod length so that, fully seated at the bottom, its top will enter the top-plate register at closure (step 5) **without** bottoming out and holding the top plate off its seated depth — the rod locates the plate, it must never hold the fillet root open. Done in the same welding session as the plate-to-tube welds in steps 3 and 5 — heat the welder once.

Leave both bottom ports bare for welding, inspection and hydro. Port 1's plain CO2 elbow installs from outside at step 9.

### 3. Weld bottom plate to tube

**Deburr both tube ends first, ID and OD.** Noga NG8150, both ends in one sitting while the tube is still loose and easy to turn. This is a clearance operation, not a fusion one — the cut edge is not a weld surface, since the fillet sits 1/4" below it. What it buys is insertion: the plate has only ~0.005" of radial slip, and a rolled-over saw burr is enough to catch a plate part-way down and hold it off its seated depth, which the corner geometry below depends on. Keep the chamfer light — the 0.065" wall has little to give.

**Prep the two surfaces the fillet actually sees.** Those are the tube bore, for the 1/4" band below each end, and the plate's outer face out to its perimeter. Not the tube's cut edge and not the plate OD — both are buried in the slip joint. Either the X1 Pro's cleaning mode or ~30 s per joint with a Scotch-Brite 7447 pad reaches both; what the joint needs is clean bare metal, not tooth. Stay off coarse grit on the plate's outer face — that perimeter edge is the fillet root, and an 80-120 grit pass rounds the very corner the weld is there to fill, undoing the burr-break-only treatment from step 1. Keep the pads segregated as stainless-only: embedded free iron rusts and outlives the citric passivation at step 8.

**Joint — ID-fit plug recessed 1/4", closed with a corner fillet.** The end plate is an ID-fit plug: its OD is sized just under the tube ID for a ~0.005" radial slip ([`endcap_circular_dxf.py`](/hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py)). Seat it **recessed 1/4"** — outer face 1/4" below the tube end — so the tube wall stands 1/4" proud and the wall ID plus the plate's outer face form an internal corner. Weld a fillet into that corner, with the beam directed into the thick plate and washing onto the tube wall. Set the recess with a 1/4" spacer / depth-stop on the rim. Full root fusion belongs to the weld qualification; PT (step 6) finds surface-breaking indications and hydro (step 7) checks pressure retention, but neither proves a buried interface is fully fused. Keep heat moving — the proud 1/4" lip is unbacked above the weld and will distort if you dwell.

Close one end of the tube with the bottom plate, float rod sticking up into what will become the interior. Recorded practice settings: power 60 %, wobble 80 Hz × 2 mm, wire feed 12 mm/s, argon 2 s pre/post, ER316L .030 filler, 8-tack opposite-side-bisecting pattern, trail-off motion at end of bead, joint surfaces prepped per above. End-to-end qualification on the 316L production joint is open; these settings are not the jet-cap recipe. A wire that sticks at the end of a bead is snipped, not lasered off: one hand keeps the gun where it stopped, and the other puts the jaw tips of the Knipex 70 11 110 between the wire nozzle and the bead — no wire is fed from the feeder first. The stub left on the bead is dressed with a stainless-only 1/4"-shank flap wheel in a drill, down to the bead and no further: the crater under it is where a crack forms, and grinding can smear one shut before the dye-penetrant read at step 6.

That recipe is a hand's. The fillet is a flat 388.61 mm circle on the tube's own axis, so it is also a joint a turned part closes in one bead under a stationary head — [`weld-rotation-rig.md`](/hardware/assembly/weld-rotation-rig.md) is the rig that does it, what it has to hit, and what could be built or bought to hit it. The tack pattern survives the rig; the fill is what the rotation replaces.

Inspect the root and heat-affected surfaces while accessible. Back-purge coverage and root oxidation are part of the weld qualification. Black scale is a reject. Heat tint needs a qualified removal method before passivation; a citric soak is not evidence that weld oxide or its chromium-depleted layer has been removed. See [BSSA's post-weld cleaning guidance](https://bssa.org.uk/bssa_articles/post-weld-cleaning-and-finishing-of-stainless-steels/).

### 4. Fit out the interior — donut float

Slide the donut float over the rod through the open top. Check free travel, the bottom port openings and the water-inlet jet's clear path. After step 5 the float is captive between the rod tack at the bottom plate and the rod-end register on the top plate's inside face. The plain CO2 inlet opens below the water line; there is no internal gas fitting or diffuser assembly.

### 5. Weld top plate to tube

Close the open end with the top plate. Its blind register (step 1) captures the rod's top end as the plate seats to its 1/4" recess — confirm the plate reaches its seated depth against the spacer / depth-stop (the rod must not hold it proud; see the rod-length note in step 2). If the register binds on the rod tip, open that one cap's pocket to 5/32" rather than forcing the plate down — the plate-to-tube joint here is a pressure weld. Same recessed corner fillet as step 3. Same rig, with the carbonator inverted so this end is up and the fillet is again welded downhand.

### 6. Dye-penetrant (PT) inspection of the closure welds

A surface-NDE pre-screen of the two closure fillet welds before committing to hydro — solvent-removable visible dye, run on the bare welds while they are clean and dry (before any water touches them). It finds and *localizes* surface-breaking lack-of-fusion, cracks, and pinholes, which the hydro test (step 7) alone won't.

1. **Clean + dry.** Wipe the weld and the rim slip-gap line with isopropyl alcohol on a lint-free wipe; let it flash off. PT needs a clean, dry surface.
2. **Penetrant.** Spray Cantesco P101S-A on both rim fillets, dwell ~10 min so it wicks into any defect.
3. **Remove excess.** Wipe off with a **dry** lint-free wipe first, then a wipe **lightly dampened** with IPA — never spray solvent onto the part or flood it, which flushes dye back out of fine defects and hides them.
4. **Develop + read.** Mist a thin coat of Cantesco D101-A developer; read within ~10 min. Record linear and rounded indications, including at the fillet toe and rim slip-gap line. A clean reading means no visible surface-breaking indication under this inspection; it does not establish internal fusion.
5. **Defect → re-weld.** Clean the area, re-weld the indicated spot, and re-PT before moving on. Wipe all penetrant + developer off with IPA before hydro.

PT finds only surface-breaking defects; the **hydro test (step 7)** checks pressure retention under the specified hold. Follow the penetrant system's cleanup instructions and remove its residues before passivation. The citric bath does not replace cleaning or qualify a buried weld root.

### 7. Hydro test

Hydro-test the fully welded and tapped carbonator on the bench, with the pump and gauge on two ports and test plugs on the other two. Its interior carries the float and rod. The four permanent elbows, including the water-inlet jet, and the PRV are absent. Fill completely with water and vent trapped gas before raising pressure. The test is a pre-passivation, pre-assembly operation; the small jet weld is qualified separately per [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md).

Hold pressure: **180 PSI for 30 minutes** (~2× the nominal [90 PSI](WORKING_PSI) CO2 feed setting). This ratio is a reference for the fabrication proof procedure, not a vessel safety factor or pressure rating. Beyond the 30-minute minimum, the in-vessel SENCTRL gauge (below) supports hour-scale leak soaks for catching slow weep before passivation.

**Hydro test rig — committed in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §1, all ACQUIRED:**
- **Pressure source:** BEAMNOVA hydrostatic test pump, 0–726 PSI, 3.17 gal reservoir, 1/4" hydraulic hose w/ 1/2" gasket-swivel end. The 180 PSI hydro target reads at ~25 % of the pump's scale — comfortable working range.
- **Pump-to-vessel adapter:** KOOTANS 1/2" NPT male × 1/4" NPT male brass reducing hex nipple (4-pack). 1/2" end seals against the BEAMNOVA swivel gasket; 1/4" end takes PTFE tape and threads into the carbonator port.
- **In-vessel soak gauge:** SENCTRL 0–200 PSI glycerin-filled, 2.5" dial, 1/4" NPT lower mount, SS case. Leaves on a carbonator port across hour-scale leak soaks for fine-resolution drift. At 180 PSI test the gauge sits at 90 % of scale — above the 60-75 % textbook sweet spot, but still within working range.
- **Port plugs:** ChillWaves brass 1/4" NPT outer-hex pipe plugs (12-pack), rated 1200 PSI — way over the test pressure. The pump takes one port and the soak gauge another, so two plugs hold the rest.
- **Post-hydro pneumatic-leak rig (separate step, post-validation):** Milton 727 industrial M-STYLE® 1/4" MNPT air plug 10-pack — threads into a carbonator port and mates with a standard air-compressor coupler for a follow-on pneumatic leak check on carbonators that already passed hydro.

**Pass criteria — open.** Working position is "no visible drop on the SENCTRL gauge, no visible weep at welds or threads." Whether to commit to a specific PSI-drop tolerance over the hold is undefined.

**Failure handling — open.** A carbonator that weeps at a bead surface is plausibly re-weldable; a weep through parent metal or HAZ is scrap; a carbonator that won't hold pressure with no visible weep most likely has a thread leak at a port. The decision tree is undefined.

### 8. Citric acid passivation

One-time soak in ~4 % food-grade citric acid solution, 30-60 minutes, in the reusable polycarbonate tub sized for the carbonator. Followed by thorough water rinse.

The surfaces enter the bath clean and free of cutting fluid, penetrant, weld scale and unacceptable heat tint. Citric treatment removes free-iron contamination and supports passivation; it is not the weld-oxide removal step. The stated concentration and soak are the current process specification, with cleaning/passivation acceptance still open. See [BSSA's passivation guidance](https://bssa.org.uk/bssa_articles/passivation-of-stainless-steels/).

Done after hydro because any re-weld requires renewed oxide removal, cleaning and passivation.

Rinse through all four open ports, drain and dry. Clean and passivate the welded jet elbow separately while it is accessible, including its bore and 1/16-inch passage, per [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md).

### 9. Install elbows and PRV

After passivation, the carbonator receives its permanent port fittings. Per [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Carbonator-port fittings", every port gets a 1/4" NPT 90° elbow as the first downstream fitting, turning the line laterally so the rest of the stack fits within the ~[30 mm](ELBOW_ENV) vertical envelope above and below the carbonator.

All four ports get a TAISHER 316L SS elbow. MNPT into the plate's FNPT, Millrose PTFE anti-seize tape on every joint. Downstream stack varies by port:

- **Port 2 (food-contact water inlet, top plate):** install the qualified, cleaned jet elbow, with the drilled cap at its male tip facing into the headspace. Confirm its thread engagement, clocking and unobstructed jet exit against the loose-plate fit record. Its PP010822E PTC adapter installs during cold-core integration per [`cold-core.md`](/hardware/assembly/cold-core.md) step 5 — connects to the lateral FNPT, collet turned into the band the line runs before it climbs the cap's conduit. The jet restriction is at the carbonator end of the elbow.
- **Port 3 (food-contact carbonated-water outlet, bottom plate):** the elbow is the first fitting. Its downstream PP010822E PTC adapter installs during cold-core integration per [`cold-core.md`](/hardware/assembly/cold-core.md) — connects to the elbow's lateral FNPT.

- **Port 4 (top-plate PRV):** The PRV must have an unobstructed path to the carbonator interior at all times — no tee, no shared line. A blockage, fitting failure, or maintenance disconnect on a shared line would compromise the safety relief path. The dedicated-elbow-on-dedicated-port architecture satisfies this. Thread the M-end of the **pre-built [`prv-shroud`](/hardware/printed-parts/cold-core/prv-shroud/) subassembly** into Port 4 FNPT, PTFE tape on the threads. The subassembly = TAISHER M×F elbow + SV-125 + printed shroud + cured silicone caulk seal at the shroud-elbow joint, built independently per the prv-shroud README's "Subassembly procedure" before this step (no prerequisites; the subassembly can be built whenever and sits ready). PRV body extends horizontally inside the shroud, fitting within the cylindrical foam-shell's headroom. The shroud preserves the air cavity around the SV-125's discharge side port and bonnet windows during the body foam pour ([`cold-core.md`](/hardware/assembly/cold-core.md) step 6), so the valve remains a functional relief device after the cold-core is cast.

- **Port 1 (bottom-plate CO2 inlet):** install one plain SS elbow, male into the plate from outside, carrying the external CO2 line from the WR1110 secondary regulator. Its bore opens directly below the water line. The external CO2 check valve remains part of the supply chain per [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md).

Once the four elbow stacks are in, the carbonator is the input to [`cold-core.md`](/hardware/assembly/cold-core.md) step 1 (coil wind).

### 10. PRV checks and optional setpoint verification

The mandatory PRV mechanism-free check is the **pull-test inside the prv-shroud subassembly procedure** ([`/hardware/printed-parts/cold-core/prv-shroud/README.md`](/hardware/printed-parts/cold-core/prv-shroud/README.md) "Subassembly procedure" step 2), performed during subassembly build before the shroud is glued on. By the time the subassembly threads into Port 4 at step 9, the pull-ring is permanently enclosed in the shroud and no further manual access is available.

The pull-ring check establishes free mechanism movement; it does not measure opening pressure or relief capacity. A local pressure-actuated setpoint test is **not yet specified or qualified**. Define the maker-appropriate test medium, regulated source, gauge, connections, ramp, discharge arrangement and acceptance before running one. The water-filled hydro rig in step 7 does not establish air/gas pop behaviour. Record valve identification and the applicable manufacturer's pressure/flow specification as part of the completed carbonator's pressure-protection qualification.

## Output condition

A finished carbonator is:

- Fully welded, hydro-tested, no visible weep
- PT-inspected at the closure welds — no surface-breaking indications
- Tapped with four clean 1/4" NPT ports
- Citric-acid passivated, rinsed dry
- Water-inlet jet elbow qualified, cleaned, passivated and fitted to Port 2; jet exit clear into headspace
- Plain CO2 elbow fitted to Port 1; dedicated unobstructed PRV path through Port 4
- Float rod welded into bottom plate; magnetic donut captive
- PRV pull-ring tested free and snappy during prv-shroud subassembly build (per that part's README, step 2)
- Externally clean — no scale, no flux, no oxide bloom

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Hydro pass/fail criteria.** No committed PSI-drop tolerance over the 30-min hold.
2. **Hydro failure handling.** Re-weld vs. scrap decision tree, especially for marginal cases (faint weep, slow drift).
3. **Weld inspection acceptance criteria.** The dye-penetrant method + materials are now defined (step 6); the accept/reject criteria for an indication are not — max acceptable porosity/pinhole size, linear-vs-rounded handling, and whether a post-hydro PT re-check is also required. Define against a written standard before unit 1.
4. **Closure-weld qualification.** The §3 settings have not been qualified end-to-end on the 316L production joint. Root fusion, internal oxidation and a repeatable cleaning method remain to be demonstrated. Use the rotation rig only after its build and dry-commissioning gates pass per [`weld-rotation-rig.md`](/hardware/assembly/weld-rotation-rig.md).
5. **Water-inlet jet fit and small-joint qualification.** Actual elbow bore, tip land, made-up projection, cap/weld passage through the tapped plate, and a sectioned same-material weld are outstanding. The nominal 9.5 mm × 2 mm cap with a 1/16-inch hole is a trial specification, not a measured fit. See [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md).
6. **Integrated operating point.** Refill flow, pressure excursion, temperature, carbonation after refill and overnight idle, and carbonation delivered at the faucet have no integrated measurements. Acceptance belongs to [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md); the conditional pump path is [`carbonation-plan-b.md`](/future/carbonation-plan-b.md).
7. **Production tapping fixture.** The rig in [`tapping-plan-2026-05-03.md`](/hardware/snapshots/tapping-plan-2026-05-03.md) is a single-use Baltic-birch + MDF snapshot. Plate registration, tap-axis guidance and repeatable engagement across 40 ports remain to be demonstrated.
8. **Recessed-port fitting and foam clearance.** Verify the four elbow stacks seat and clock with the plates recessed 1/4 inch and the existing foam-shell envelope. Port 2's completed cap must remain clear of the plate and discharge into the headspace.
9. **Pressure protection and cleaning acceptance.** Establish the completed carbonator's pressure basis and relief suitability for both connected pressure sources. Define acceptance for internal root condition, oxide removal, passivation and rinse cleanliness before the batch.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_pressure_vessel_sync.py`
