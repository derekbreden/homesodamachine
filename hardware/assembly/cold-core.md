# Cold Core Assembly

The production procedure for assembling the cold core — the back-of-enclosure subsystem that contains the carbonator vessel, its wound evaporator coil, two flavor reservoirs, and the surrounding pour-in-place polyurethane foam, all held together inside a 3D-printed PETG shell stack.

Foam-pour geometry, shell architecture, copper-plug binder-clip cross-section, and lid joinery: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md).

## Scope

In: one hydro-tested + passivated carbonator vessel (output of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md)); GOORY 1/4" OD × 0.031" wall ACR copper tubing for the evaporator coil; 3M 425 aluminum foil tape; the printed coil-winding mandrel; the printed PETG shell stack (foam-shell, foam-lid × 1, copper-plug × 3, reservoir × 2); pour-in-place 2 lb closed-cell polyurethane foam (two-part 1:1); M3 × 12 SHCS × 6 and ruthex M3 inserts × 6 for the lid.

Out: a fully foam-poured cold core, closed on top by the thin foam lid, with the wound evaporator coil bonded around the vessel and its inlet/outlet stubs (~2 ft each) protruding through the foam-shell's copper-plug exits.

Not in scope: refrigerant-loop integration ([`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)) — brazing of the coil stubs onto the donor unit's cap tube and suction line, vacuum, charge, run-up. Also not in scope: enclosure-side assembly (electronics shelf, compressor + condenser + fan placement, AC wiring), faucet install, final integration.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 (refrigeration — GOORY copper tubing for the coil) + §6 (cold-core insulation, 3M 425 foil tape + pour-in-place foam + foam-pour consumables) + §13 (mechanical attach hardware + reservoir-cap vent filter) + §7 (the printed parts themselves, on $/kg-PETG basis). Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6 + §11.

| Item | Source | Status (per purchases.md) |
|---|---|---|
| Carbonator vessel | Output of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) | Hydro-tested + passivated |
| GOORY 1/4" OD × 0.031" wall ACR copper tubing | B0DKSW5VL9 | ~24 ft per vessel for coil wrap + tie-in stubs (1/2 of 50 ft roll per build) — ACQUIRED |
| 3M 425 aluminum foil tape | B07BTW7C2N | Coil-to-vessel thermal interface; applied as continuous skin under the coil; one 180 ft roll covers ~12 builds — ACQUIRED |
| DS18B20 TO-92 (tank, family 0x28) + DS18S20 TO-92 (coil, family 0x10) 1-wire sensors | B0FKG3HT9Q / DigiKey DS18S20+-ND | Two bare TO-92 temperature sensors, leads heat-shrunk; potted into the foam against their metal surfaces. Distinct 1-wire family codes let firmware tell them apart deterministically (no per-unit ID map) — see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §6 — ON-ORDER |
| Coil-winding mandrel (printed PETG) | [`/hardware/printed-parts/cold-core/coil-mandrel/`](/hardware/printed-parts/cold-core/coil-mandrel/) | Print, reusable across builds |
| Foam-shell (printed PETG) | [`/hardware/printed-parts/cold-core/foam-shell/`](/hardware/printed-parts/cold-core/foam-shell/) | Print, Bambu H2C, 0.8 mm nozzle |
| Foam lid × 1 (printed PETG) | Same | Print |
| Copper plug × 3 (printed PETG) | Same | Print |
| Flavor reservoir × 2 (printed) | [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/) | Print, SunTop food-contact-compliant PETG (FDA 21 CFR 177.1630), 1.75 mm × 1 kg, Clear/Transparent B0FP34MJ94 — ON-ORDER |
| M3 × 12 mm SHCS, 304 stainless (18-8) × 6 (foam-lid screws) | BNUOK B0DJQGMQZM | ON-ORDER |
| M3 × 12 mm SHCS, 304 stainless (18-8) × 12 (reservoir-cap screws) | BNUOK B0DJQGMQZM | ON-ORDER |
| ruthex M3 short heat-set inserts × 21 per build (6 foam-lid + 12 reservoir + 3 touch-flo-shell) | ruthex B0D39W228K (100-pc bag = ~3.8 builds) | ON-ORDER |
| LVDALAB PTFE membrane filter Ø13 mm × 0.45 µm × 2 (reservoir vent) | B0D41KT345 (100-pc bag = 50 builds) | ON-ORDER |
| Pour-in-place 2 lb 2-part closed-cell PU foam, 1 qt kit | Fiberglass Supply Depot B08R7TX8QJ | ON-ORDER |
| Foam-pour consumables (mixing cups × 4, stir sticks × 4, nitrile gloves × 1 pair per build) | B08JHH1DBF / B09H6ZP447 / B0G8SSMVKW | ACQUIRED |

## Procedure

### 1. Wind the evaporator coil around the vessel

Wind GOORY 1/4" OD × 0.031" wall ACR copper tubing as a single-layer helical coil at ~1/8" pitch around the vessel OD — ~22 ft of wrap per vessel + ~2 ft each end for the refrigerant-loop tie-in stubs. The tie-in stubs exit through the foam-shell's copper-plug holes; brazing happens in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md).

Bond the coil to the vessel OD with 3M 425 aluminum foil tape applied as a continuous skin between vessel and coil.

Before closing the foil skin over the coil's outlet (high) end — the suction side, refrigerant leaving as low-pressure gas, the coldest metal — tuck the **DS18S20 coil probe** (bare TO-92, family 0x10, leads heat-shrunk) flat against the copper and tape it down under the foil. This is the freeze-protect sensor; thermally bonding it to the suction-end copper is what lets the −8 °C cutoff see the coldest point. Lead its 3-conductor cable toward the +Z penetration slot for routing in step 3.

Wind around the printed [coil-mandrel](/hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py) — hollow PETG cylinder with a shallow [1 mm](GROOVE_DEPTH) helical guide groove, mandrel OD [123 mm](MANDREL_OD), tank OD [127 mm](TANK_OD), net coil undersize [3 mm](NET_UNDERSIZE). Wind length [120.4 mm](WIND_LENGTH), [9.687](TOTAL_WRAPS) wraps, pitch [12.43 mm](PITCH). Inlet aligns with the foam-shell copper plug at Y=[46](PLUG_INLET_Y); outlet at Y=[166.4](PLUG_OUTLET_Y). Pull the wound coil off the mandrel and slip it onto the foil-taped vessel. Coil springback: 1–3 mm radial.

Dev-phase summary: [`/hardware/handwork.md`](/hardware/assembly/handwork.md) "Bend copper around the pressure vessel".

### 2. Press ruthex inserts into the outer shell

Six ruthex M3 short heat-set inserts pressed into the top face of the outer_shell. Each insert seats in a Ø[4 mm](INSERT_POCKET_D) × [4 mm](INSERT_HALF_DEPTH)-deep printed pocket; another [4 mm](INSERT_HALF_DEPTH) of relief below the insert. Soldering iron tip on the insert; press straight down until flush. The bottom face carries no inserts.

Geometry detail at [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Lid-to-outer-shell joinery".

### 3. Body-side install

With the outer shell open-top-up on the bench, install every internal component:

- **Pressure vessel + coil** (per step 1; coil stubs exit through the foam-shell's copper-plug holes) lowered into the cylindrical center cavity, seated on the printed-in `tank_support_ring`
- **Temperature probes** — tape the **DS18B20 tank-wall probe** (bare TO-92, family 0x28, leads heat-shrunk) flat against the vessel OD under a patch of 3M 425 foil tape; this is the compressor-cycling setpoint sensor, so it reads the vessel wall, not the coil. The **DS18S20 coil probe** (0x10) is already tucked under the coil foil tape at the suction end (step 1). Route both 3-conductor leads up and out through the shared +Z slot alongside the other penetrations; at the cold-core exit they join SIG-1, the IO26 1-wire bus, per [`wiring.md`](/hardware/assembly/wiring.md). Seat the leads so the copper-plug clamp and the foam over-pour close around them — no air path may follow the leads inward (that path, not the sensor itself, is the only way condensation reaches a potted probe).
- **Reservoirs** seated into the two ±X bag pockets
- **Penetrations routed through the outer shell walls:**
  - CO2 inlet → enters from above through the foam-lid Ø[6.5 mm](TUBE_HOLE_D) hole at (x=0, z=[-68.75](COTWO_INLET_Z)); inside the cavity, a John Guest PP0308E 1/4" PTC 90° elbow seats in the Ø16 doorway in the −Z support arch, and the line continues to the vessel's bottom-plate TAISHER NPT elbow via a PP010822E 1/4" PTC × 1/4" NPT M adapter
  - Water outlet → dedicated Ø[6.5 mm](TUBE_HOLE_D) hole, +Z outer wall
  - Reservoir lines (+X, −X) → dedicated Ø[6.5 mm](TUBE_HOLE_D) holes in the bag_pocket_shell ±X far walls
  - Refrigerant inlet (low), refrigerant outlet (high), water inlet, PRV vent LLDPE → shared Y-elongated slot at x=0 on the +Z outer wall. The water-inlet line transitions from the warm-side GASHER 1/4" NPT check valve via a JG PP010822E 1/4" PTC × 1/4" NPT M adapter before entering the slot as 1/4" OD LLDPE; downstream of the slot a second JG PP010822E (PTC → NPT) takes the LLDPE back to NPT before threading into the TAISHER 1/4" NPT 90° vessel-port elbow on Port 2 (top plate). The PRV vent LLDPE press-fits into the prv-shroud cap, routes through the slot at its own Y height (per foam-shell penetration #8), and terminates open inside the appliance interior.
- **PRV vent LLDPE** press-fits into the cap of the [`/hardware/printed-parts/cold-core/prv-shroud/`](/hardware/printed-parts/cold-core/prv-shroud/) subassembly on Port 4 (threaded into the vessel at [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 8). The LLDPE routes from the cap, takes a slight bend, and enters the +Z shared slot at its allocated Y height. Far end terminates open inside the appliance interior.
- **Four copper plugs** slid down into the shared +Z slot from above, sealing between and above the four pass-throughs (binder-clip geometry in [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Shared +Z slot and copper plug stack")
- **In-cavity PP0308E elbow** angled in through the −Z support-arch doorway from above before the vessel drops into the cavity.

All fitting-size transitions (3/8" → 1/4", larger fittings) happen on the warm side of the shell; every penetration through the shell wall is 1/4" OD tubing.

### 4. Body foam pour

Mix the two-part PU foam 1:1. Pour the liquid directly into the body's open +Y top, all at once. Foam falls into the body and reaches every cavity in parallel: outer foam gap, bag pockets, corner pockets at ±Z, and the tank cavity inside the cylinder. Geometry: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Assembly and foam pour".

Foam expansion may push small amounts of material out through the 0.5 mm clearance bands around tubes in the +Z slot and the tight-fit tube exits at other penetrations. Trim flush after cure.

The pour encapsulates both temperature probes and their leads against the cold metal. Potted in closed-cell foam with no air gap, they need no separate waterproofing — the foam is the vapor barrier. Ensure the pour fully wets around each probe and up its lead entry with no void: a void is a trapped-air pocket that will condense and frost against the cold surface, and is the only path by which moisture reaches a probe. A void at a probe is an insulation defect first and a probe-fouling risk second.

### 5. Final assembly

With the body pour cured:

- Drop the pre-soldered reed columns into the still-open reed channels
- Screw the thin foam-lid on last, covering the cured foam: six M3 × 12 SHCS through the lid's screw positions and into the top-face inserts

## Warm-side check valves

Water-inlet and CO2-inlet lines each carry an inline 1/4" NPT SS PTFE-on-metal check valve (GASHER B0FV2D2FFX) on the warm side, upstream of the shared +Z slot.

- **Water-side check** between the SeaFlo pump's MAACFLOW 1/4" NPT adapter and the first JG PP010822E PTC adapter.
- **CO2-side check** between the DERPIPE 5/16"-tube × 1/4"-NPT push-to-connect and the LTWFITTING bottom-plate barb adapter.

## Output condition

A finished cold core:

- The body foam pour cured, flush-trimmed at visible surfaces and tube exits
- Vessel + bonded coil installed, seated in the cylinder cavity, surrounded by foam; coil inlet/outlet stubs (~2 ft each) protruding through the foam-shell's copper-plug exits
- Both temperature probes potted in the foam against their metal surfaces — DS18B20 (tank-wall, 0x28) on the vessel OD, DS18S20 (coil, 0x10) at the suction end of the coil — leads routed out the +Z slot and sealed, joining SIG-1 at the cold-core exit
- Both reservoirs seated in their bag pockets
- All seven penetrations routed through their designated holes / slot
- Reed columns dropped into the reed channels
- Foam lid installed with six M3 × 12 SHCS into the top-face heat-set inserts
- External envelope ~[283 mm](OUTER_X) × [181](CCORE_OUTER_Y) × [213.4 mm](OUTER_H)

## Open items

1. **Foam data-sheet spec (mix proportions, pot life, cure time, pour temperature window).**
2. **Trim method after foam cure.**
3. **Reservoir-internal assembly procedure.** The reservoir arrives already assembled (cap installed, six M3×12 SHCS into ruthex inserts clamping a TPU gasket, PTFE vent membrane installed). The float-rod cut + seat is specified in [`handwork.md`](/hardware/assembly/handwork.md) "Cut + seat the reservoir float rods" with the rod / float / reed geometry in [`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md); the cap / gasket / vent-membrane / reed-column steps are still to be written here.
4. **Reservoir final-qualification status.** Pending water + syrup-dwell pass.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_cold_core_sync.py`
