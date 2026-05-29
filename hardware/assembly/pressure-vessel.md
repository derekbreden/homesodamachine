# Pressure Vessel Fabrication

The production procedure for the carbonator pressure vessel — the 316L stainless body that holds carbonated water at the **90 PSI working pressure** specified in [`/hardware/future.md`](/hardware/future.md) "Carbonation subsystem". This document is the repeatable procedure for taking commodity tube + cut plates to a hydro-tested, passivated vessel ready for the [refrigeration loop](refrigerant-loop.md) downstream.

Design intent and material rationale live in [`/hardware/future.md`](/hardware/future.md). The dev-phase task summary lives in [`/hardware/handwork.md`](/hardware/handwork.md). Snapshots of single-event execution (the first tap, the first weld recipe) live in their own dated files and are referenced by step below.

## Scope

In: commodity 316L SS tube (OnlineMetals #12498) + laser-cut 316L SS end plates (SendCutSend [`endcap-circular-2hole.dxf`](/hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.dxf)) + the small parts listed under "Inputs" below.

Out: one vessel that has been tapped, welded, hydro-tested at the working-pressure-appropriate setpoint, passivated, and has the internal sparge stone + float assembly installed — ready for evaporator coil wrap.

Not in scope: the evaporator coil wrap itself (boundary with [`refrigerant-loop.md`](refrigerant-loop.md)), the cold-core foam pour ([`cold-core.md`](cold-core.md)), and any system-level installation.

## Inputs per vessel

Per-unit BOM lives in [`/hardware/bom.md`](/hardware/bom.md) §2 (carbonator vessel) + §12 (level sensing — the float rod + donut). The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost. Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`/hardware/purchases.md`](/hardware/purchases.md) §1 (vessel fabrication), §16 (laser welding), §2 (CO2 subsystem), §4 (port-fittings including the new vessel-port elbows).

| Item | Source | Notes |
|---|---|---|
| 5" OD × 0.065" wall × [152.4 mm](TANK_H) 316L SS welded tube | OnlineMetals #12498 | MTRs required. |
| 1/4"-thick 316L SS circular end plate, 2-hole pattern | SendCutSend [`endcap-circular-2hole.dxf`](/hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.dxf) | 2 per vessel |
| 1/8" 316L SS rod, ~6" cut from 12" stock | Tandefio B0CY4DWJFQ | Internal float rod (bom.md §12) |
| Magnetic donut float | Harvested from DEVMO MINI float switch B07T18PGJ4 | Slides on rod, captive after top weld (bom.md §12) |
| 0.5 µm sintered 316 SS sparge stone (1/4" barb input) | FERRODAY B091C5Y6L9 | Internal CO2 sparge |
| Food-grade silicone tube stub, ~3" of 1/4" ID | Metaland B08L1ST6ST (cut from §5 stock) | Connects bottom-plate barb to sparge stone |
| 1/4" hose-barb × 1/4" MNPT 316 SS adapter | LTWFITTING B017N4TTMA | CO2 inlet barb, installed at sparge step |
| **TAISHER 316L SS 1/4" NPT 90° street elbow, M×F** | B0CZ38MYL1 (2-pk) | **4 per vessel — all four ports.** Turns the line laterally within the ~[30 mm](ELBOW_ENV) vertical envelope around the tank — see [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Tank-port fittings". SS-on-SS thread joints rely on the Millrose PTFE anti-seize tape (above) at every port. |
| **Control Devices SV-125 safety valve, 1/4" NPT, 125 PSI** | B01G2F6EMY (size SV-125) | **Port 4 dedicated PRV — installed after passivation per step 8 below, via the SS 90° elbow to orient the body laterally.** 125 PSI set pressure gives 1.39× margin over the 90 PSI working pressure. 49 SCFM relief capacity. |
| Millrose PTFE thread-seal tape | B07C9ZV4PG | Anti-seize for 4 NPT ports (test plugs during hydro + final fittings after passivation) |
| ER316L .030 filler wire | STARTECHWELD B09BKFBXT9 | Matches 316L parent metal. |
| Cambro 6 QT polycarbonate square container | B001BZEQ44 | One-time-use passivation soak tub per vessel |
| Viva Doria food-grade citric acid | B0C5NQM8S1 | Made up to ~4 % solution, ~1 qt per vessel (~1/20 of 2 lb bag) |
| Tap Magic EP-Xtra cutting fluid | B00DHMHSGM | ~$0.50 of fluid per vessel for NPT tapping |

Tooling (per-vessel-amortized only — single-asset tools live in [`/hardware/purchases.md`](/hardware/purchases.md), not here): XLaserlab X1 Pro laser welder, WEN 4208T drill press, LingGan M35 cobalt 1/4-18 NPT pipe tap + Drill America DWT adjustable tap wrench, Brown & Sharpe spring tap guide, argon at the welder, hydro test rig (see step 6).

## CO2 supply (sets working pressure)

The 90 PSI working pressure this procedure is sized against is set by an in-appliance Interstate Pneumatics WR1110 1/4" NPT fixed-90 PSI secondary regulator (B07J2L8LF3, [`bom.md`](/hardware/bom.md) §4) between the customer's CGA-320 primary regulator and the vessel CO2 port. The WR1110 holds the appliance-side pressure at 90 PSI regardless of where the customer sets their primary, eliminating customer-setpoint variance and adding a layer of safety on the highest-energy path in the appliance (the CO2-bottle pressure reservoir). Customer guidance: set the primary regulator anywhere in the 70–100 PSI range; the WR1110 takes care of the rest.

At the 5" OD × 0.065" wall geometry, hoop stress at 90 PSI is ~3,461 PSI — a ~5.8× safety factor against the 20,000 PSI allowable for 316L SS in vessel-grade service. The 35 PSI margin between the 90 PSI working setpoint and the SV-125 PRV (above) is the safety margin sized for normal-operation excursions.

## Procedure

### 1. Tap NPT in both end plates

Hand-tap 1/4"-18 NPT in all four port positions — 2 ports per plate × 2 plates per vessel. Target 4.5 turns of engagement, with a 1/4" NPT test fitting snug-firm at 2-3 threads showing.

The first-tap rig and hand sequence are captured in [`/hardware/tapping-plan-2026-05-03.md`](/hardware/tapping-plan-2026-05-03.md) (point-in-time snapshot of the first tap into a 316L plate). That snapshot is single-use Baltic-birch + MDF; the production fixture for the full per-vessel × 10-vessel batch is a downstream design step — see "Open items" below.

### 2. Tack-weld float rod to bottom plate

Cut the 1/8" 316L rod to ~6". Tack-weld it vertically to the inside face of the bottom plate (the side that will face into the vessel). Done in the same welding session as the plate-to-tube welds in steps 3 and 5 — heat the welder once.

### 3. Weld bottom plate to tube

Close one end of the tube with the bottom plate, float rod sticking up into what will become the interior. Current weld recipe: power 60 %, wobble 80 Hz × 2 mm, wire feed 12 mm/s, argon 2 s pre/post, ER316L .030 filler, 8-tack opposite-side-bisecting pattern, trail-off motion at end of bead, 30 s plate prep with 80-120 grit on the cut edge. Wire-stick fix: keep the trigger held and lift straight up at end of bead — the retract/patch cycle fires after conductance breaks in mid-air, so the wire never re-fuses to a still-molten puddle ([`/marketing/video/dont-let-go.md`](/marketing/video/dont-let-go.md)).

Yellow/brown coloration on the inside surface is acceptable at this stage — chromium oxide under partial argon protection, dissolves in the citric-acid passivation downstream (step 7). Black scale is not acceptable; if seen, increase argon coverage or add an internal back-purge.

### 4. Install magnetic donut float

Slide the donut float over the rod through the still-open top of the tube. After step 5 it is captive between the rod tack at the bottom plate and the rod-end register on the top plate's inside face.

### 5. Weld top plate to tube

Close the open end with the top plate. The top plate's inside face has a small register that captures the rod's top end as the plate seats against the tube end. Same weld recipe as step 3.

### 6. Hydro test

Hydro-test the fully welded + tapped vessel — bare, on a bench, with NPT plugs in all four ports. No PRV, no fittings, no cold core, no refrigerant loop. The test is a pre-passivation, pre-assembly bench operation.

Hold pressure: **180 PSI for 30 minutes** (~2× the 90 PSI working pressure). Beyond the 30-minute minimum, the in-vessel SENCTRL gauge (below) supports hour-scale leak soaks for catching slow weep before passivation.

**Hydro test rig — committed in [`/hardware/purchases.md`](/hardware/purchases.md) §1, all ACQUIRED:**
- **Pressure source:** BEAMNOVA hydrostatic test pump, 0–726 PSI, 3.17 gal reservoir, 1/4" hydraulic hose w/ 1/2" gasket-swivel end. The 180 PSI hydro target reads at ~25 % of the pump's scale — comfortable working range.
- **Pump-to-vessel adapter:** KOOTANS 1/2" NPT male × 1/4" NPT male brass reducing hex nipple (4-pack). 1/2" end seals against the BEAMNOVA swivel gasket; 1/4" end takes PTFE tape and threads into the vessel port.
- **In-vessel soak gauge:** SENCTRL 0–200 PSI glycerin-filled, 2.5" dial, 1/4" NPT lower mount, SS case. Leaves on a vessel port across hour-scale leak soaks for fine-resolution drift. At 180 PSI test the gauge sits at 90 % of scale — above the 60-75 % textbook sweet spot, but still within working range.
- **Port plugs:** ChillWaves brass 1/4" NPT outer-hex pipe plugs (12-pack), rated 1200 PSI — way over the test pressure. Three plugs hold the three unused vessel ports during the test.
- **Post-hydro pneumatic-leak rig (separate step, post-validation):** Milton 727 industrial M-STYLE® 1/4" MNPT air plug 10-pack — threads into a vessel port and mates with a standard air-compressor coupler for a follow-on pneumatic leak check on vessels that already passed hydro.

**Pass criteria — open.** Working position is "no visible drop on the SENCTRL gauge, no visible weep at welds or threads." Whether to commit to a specific PSI-drop tolerance over the hold is undefined.

**Failure handling — open.** A vessel that weeps at a bead surface is plausibly re-weldable; a weep through parent metal or HAZ is scrap; a vessel that won't hold pressure with no visible weep most likely has a thread leak at a port. The decision tree is undefined.

### 7. Citric acid passivation

One-time soak in ~4 % food-grade citric acid solution, 30-60 minutes, in a disposable plastic tub sized for the vessel. Followed by thorough water rinse.

Restores the chromium oxide layer at the weld zones — what makes 316L resistant to pitting from carbonic acid in long-life carbonated-water service. The yellow/brown weld coloration from step 3/5 dissolves out during this soak. Same treatment commercial brewery bright tanks and commercial carbonators receive.

Done after hydro because failures get re-welded (re-introducing oxide that the passivation needs to handle) and before sparge install because the silicone tube and sintered stone don't belong in a citric soak.

### 8. Install elbows, sparge stone, PRV

After passivation, the vessel receives its permanent port fittings. Per [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Tank-port fittings", every port gets a 1/4" NPT 90° elbow as the first downstream fitting, turning the line laterally so the rest of the stack fits within the ~[30 mm](ELBOW_ENV) vertical envelope above and below the tank.

All four ports get a TAISHER 316L SS elbow. MNPT into the plate's FNPT, Millrose PTFE anti-seize tape on every joint. Downstream stack varies by port:

- **Ports 2 + 3 (food-contact: water inlet on top, carbonated-water outlet on bottom):** the elbow is the first fitting. Downstream (water-side GASHER check valve + MAACFLOW adapter for Port 2, VALVENTO compression adapter for Port 3) installs during cold-core integration per [`cold-core.md`](cold-core.md) — connects to the elbow's lateral FNPT.

- **Port 4 (top-plate PRV):** The PRV must have an unobstructed path to the vessel interior at all times — no tee, no shared line. A blockage, fitting failure, or maintenance disconnect on a shared line would compromise the safety relief path. The dedicated-elbow-on-dedicated-port architecture satisfies this. Thread the M-end of the **pre-built [`prv-shroud`](/hardware/printed-parts/cold-core/prv-shroud/) subassembly** into Port 4 FNPT, PTFE tape on the threads. The subassembly = TAISHER M×F elbow + SV-125 + printed shroud + cured silicone caulk seal at the shroud-elbow joint, built independently per the prv-shroud README's "Subassembly procedure" before this step (no prerequisites; the subassembly can be built whenever and sits ready). PRV body extends horizontally inside the shroud, fitting within the cylindrical foam-shell's headroom. The shroud preserves the air cavity around the SV-125's discharge side port and bonnet windows during the body foam pour ([`cold-core.md`](cold-core.md) step 5), so the valve remains a functional relief device after the cold-core is cast.

- **Port 1 (bottom-plate CO2 inlet + internal sparge):** the LTWFITTING B017N4TTMA hose-barb × MNPT adapter handles the internal sparge — barb facing inward, food-grade silicone tube stub connecting it to the FERRODAY B091C5Y6L9 0.5 µm sintered SS sparge stone hanging in the water column. The SS 90° elbow handles the external CO2 line connection from the in-appliance WR1110 secondary regulator (see [`/hardware/future.md`](/hardware/future.md) "CO2 supply"). **The relative install order of LTWFITTING vs elbow on Port 1 is an open item** — see Open items below.

Once the four elbow stacks are in, the vessel is the input to [`refrigerant-loop.md`](refrigerant-loop.md) step 4 (coil wind).

### 9. (Optional) Functional pop test against vessel pressure

The mandatory PRV mechanism-free check is the **pull-test inside the prv-shroud subassembly procedure** ([`/hardware/printed-parts/cold-core/prv-shroud/README.md`](/hardware/printed-parts/cold-core/prv-shroud/README.md) "Subassembly procedure" step 2), performed during subassembly build before the shroud is glued on. By the time the subassembly threads into Port 4 at step 8, the pull-ring is permanently enclosed in the shroud and no further manual access is available.

This optional step adds a **functional pop test against pressure** — confirming the SV-125's setpoint is in spec, not just that the mechanism moves freely. Re-use the BEAMNOVA hydro rig from step 6, with the subassembly threaded into Port 4 and the other three ports plugged. Ramp pressure on one of the plugged ports until the PRV cracks — audible pop, gas vented through the shroud's LLDPE port (or out the open cap hole if LLDPE isn't installed yet). Crack pressure should fall within ±3 % of 125 PSI (i.e., 121–129 PSI). The SV-125's silicon O-ring reseats cleanly within ±10 % of setpoint per the manufacturer's spec, so a single bench pop does not degrade the seat for service.

Optional because the pull-ring test in the subassembly procedure confirms the load-bearing mechanism-free property, and the manufacturer's ASME UV mark implies factory setpoint verification; the functional pop only adds confidence that the spring + seat were factory-set within spec on this particular unit.

## Output condition

A finished vessel is:

- Fully welded, hydro-tested, no visible weep
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
3. **Post-hydro visual inspection.** What gets inspected, with what aid (loupe? dye penetrant?), against what criteria.
4. **X1 Pro weld recipe end-to-end validation.** The recipe in §3 is what we run on unit 1's vessel — same 60 % / 12 mm/s / 8-tack pattern / Don't-Let-Go trigger handling — but it hasn't been run end-to-end on 316L production stock yet. The 304L practice fixtures were where the recipe was developed; first 316L production weld is unit 1.
5. **Port 1 elbow + LTWFITTING install sequence.** [`/hardware/future.md`](/hardware/future.md) "Port 1" describes the LTWFITTING with barb facing inward and MNPT side threaded into the plate. Two assembly orders are geometrically defensible: (a) LTWFITTING first, SS elbow's FNPT threading onto LTWFITTING's externally-protruding MNPT remainder; (b) SS elbow first into Port 1 FNPT, LTWFITTING's MNPT then threading into the elbow's lateral FNPT with the barb on the elbow's lateral side. Path (a) gives a vertical elbow stack on Port 1's exterior; path (b) keeps everything at the elbow's lateral plane. Pick after the elbows are in hand and the LTWFITTING's thread length vs plate thickness can be measured against a fitting.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_pressure_vessel_sync.py`
