# Cold Core Assembly

The production procedure for assembling the cold core — the back-of-enclosure subsystem that contains the carbonator vessel, its wound evaporator coil, two flavor reservoirs, and the surrounding pour-in-place polyurethane foam, all held together inside a 3D-printed PETG shell stack.

Foam-pour geometry, shell architecture, copper-plug binder-clip cross-section, and TPU-gasket seam analysis: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md).

## Scope

In: one hydro-tested + passivated carbonator vessel (output of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md)); GOORY 1/4" OD × 0.031" wall ACR copper tubing for the evaporator coil; 3M 425 aluminum foil tape; the printed coil-winding mandrel; the printed PETG shell stack (foam-shell, foam-cap × 2, foam-cap-lid × 2, copper-plug × 4, reservoir × 2); TPU 90A gaskets × 2; pour-in-place 2 lb closed-cell polyurethane foam (two-part 1:1); M3 × 25 SHCS × 12 and ruthex M3 inserts × 12 for the caps.

Out: a fully foam-poured cold core, capped + gasketed top and bottom, with the wound evaporator coil bonded around the vessel and its inlet/outlet stubs ([500 mm](STUB_LEN) each) protruding through the foam-shell's copper-plug exits.

Not in scope: refrigerant-loop integration ([`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)) — brazing of the coil stubs onto the donor unit's cap tube and suction line, vacuum, charge, run-up. Also not in scope: enclosure-side assembly (electronics shelf, compressor + condenser + fan placement, AC wiring), faucet install, final integration.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 (refrigeration — GOORY copper tubing for the coil) + §6 (cold-core insulation, 3M 425 foil tape + pour-in-place foam + foam-pour consumables) + §13 (mechanical attach hardware + reservoir-cap vent filter) + §7 (the printed parts themselves, on $/kg-PETG basis). Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6 + §11.

| Item | Source | Status (per purchases.md) |
|---|---|---|
| Carbonator vessel | Output of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) | Hydro-tested + passivated |
| GOORY 1/4" OD × 0.031" wall ACR copper tubing | B0DKSW5VL9 | ~[16 ft](CUT_FT) per vessel for coil wrap + tie-in stubs (1/3 of 50 ft roll per build) — ACQUIRED |
| 3M 425 aluminum foil tape | B07BTW7C2N | Coil-to-vessel thermal interface; applied as continuous skin under the coil; one 180 ft roll covers ~12 builds — ACQUIRED |
| DS18B20 TO-92 (tank, family 0x28) + DS18S20 TO-92 (coil, family 0x10) 1-wire sensors | B0FKG3HT9Q / DigiKey DS18S20+-ND | Two bare TO-92 temperature sensors, leads heat-shrunk; potted into the foam against their metal surfaces. Distinct 1-wire family codes let firmware tell them apart deterministically (no per-unit ID map) — see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §6 — ON-ORDER |
| Gebildet reed switch × 2 (carbonator level) | B0CW9418F6 | Mounted on the vessel wall under the foil at the register azimuth; same SKU as the reservoirs' eight, one 6-pack covers both with spares ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)) — ON-ORDER |
| Coil-winding mandrel (printed PETG) | [`/hardware/printed-parts/cold-core/coil-mandrel/`](/hardware/printed-parts/cold-core/coil-mandrel/) | Print, reusable across builds |
| Foam-shell (printed PETG) | [`/hardware/printed-parts/cold-core/foam-shell/`](/hardware/printed-parts/cold-core/foam-shell/) | Print, Bambu H2C, 0.8 mm nozzle |
| Foam cap × 2 + foam cap lid × 2 (printed PETG) | Same | Print |
| TPU 90A gasket × 2 (printed) | [`/hardware/printed-parts/cold-core/foam-cap/`](/hardware/printed-parts/cold-core/foam-cap/) | Print |
| Copper plug × 4 (printed PETG) | [`/hardware/printed-parts/cold-core/copper-plugs/`](/hardware/printed-parts/cold-core/copper-plugs/) | Print |
| Flavor reservoir × 2 (printed) | [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/) | Print, SunTop food-contact-compliant PETG (FDA 21 CFR 177.1630), 1.75 mm × 1 kg, Clear/Transparent B0FP34MJ94 — ON-ORDER |
| M3 × 25 mm SHCS, 12.9 alloy, black oxide × 12 (foam-cap clamp screws) | BNUOK B0DJQGF665 | ACQUIRED |
| M3 × 12 mm SHCS, 304 stainless (18-8) × 12 (reservoir-cap screws) | BNUOK B0DJQGMQZM | ON-ORDER |
| ruthex M3 short heat-set inserts × 27 per build (12 foam-caps + 12 reservoir + 3 touch-flo-shell) | ruthex B0D39W228K (100-pc bag = ~3.7 builds) | ON-ORDER |
| LVDALAB PTFE membrane filter Ø13 mm × 0.45 µm × 2 (reservoir vent) | B0D41KT345 (100-pc bag = 50 builds) | ON-ORDER |
| Pour-in-place 2 lb 2-part closed-cell PU foam, 1 qt kit | Fiberglass Supply Depot B08R7TX8QJ | ON-ORDER |
| Foam-pour consumables (mixing cups × 4, stir sticks × 4, nitrile gloves × 1 pair per build) | B08JHH1DBF / B09H6ZP447 / B0G8SSMVKW | ACQUIRED |

## Procedure

### 1. Dress the vessel wall, then wind the evaporator coil

Everything that has to touch bare 316L goes on **before** the foil, at the bench, with the vessel in the open:

- The **DS18B20 tank-wall probe** (bare TO-92, family 0x28, leads heat-shrunk) taped flat against the vessel OD, in the bare band below the wind so no wrap has to climb over it. This is the compressor-cycling setpoint sensor, so it reads the vessel wall, not the coil.
- The **two carbonator reed switches**, on the rod-register azimuth ([`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 1) — the line the wall-preloaded float parks its donut against. Both reed heights land inside the wind band, so each reed lies in the channel the wind's pitch leaves between adjacent wraps. **Mounting method is open** — see Open items; it blocks this step.

Both go under the foil skin. Neither can be added later: the reed has only a couple of mm of magnet-to-wall budget ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) "Magnet–reed signal-path geometry", measured on this tube), which nothing mounted above the foil or outside the coil leaves, and after step 4 the vessel wall is at the bottom of a 15 mm-wide, full-height annulus where none of this is a hand operation.

Wind GOORY 1/4" OD × 0.031" wall ACR copper tubing as a single-layer helical coil around the vessel OD — [12.72 ft](WRAP_FT) of wrap per vessel + a [500 mm](STUB_LEN) tail each end for the refrigerant-loop tie-in stubs. The tie-in stubs exit through the foam-shell's copper-plug holes; brazing happens in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md).

Bond the coil to the vessel OD with 3M 425 aluminum foil tape applied as a continuous skin between vessel and coil.

Before closing the foil skin over the coil's outlet (high) end — the suction side, refrigerant leaving as low-pressure gas, the coldest metal — tuck the **DS18S20 coil probe** (bare TO-92, family 0x10, leads heat-shrunk) flat against the copper and tape it down under the foil. This is the freeze-protect sensor; thermally bonding it to the suction-end copper is what lets the −8 °C cutoff see the coldest point. Distinct 1-wire family codes let firmware tell it and the tank probe apart deterministically, with no per-unit ID map.

Wind around the printed [coil-mandrel](/hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py) — hollow PETG cylinder with a shallow [1 mm](GROOVE_DEPTH) helical guide groove, mandrel OD [123 mm](MANDREL_OD), tank OD [127 mm](TANK_OD), net coil undersize [3 mm](NET_UNDERSIZE). Wind length [119.4 mm](WIND_LENGTH), [9.687](TOTAL_WRAPS) wraps, pitch [12.33 mm](PITCH) — [3.877 m](WRAP_LEN) of copper in the wrap. Inlet aligns with the foam-shell copper plug at Y=[47](PLUG_INLET_Y); outlet at Y=[166.4](PLUG_OUTLET_Y). Pull the wound coil off the mandrel and slip it onto the foil-taped vessel. Coil springback: 1–3 mm radial.

The vessel leaves this step with four cables on it — two probes and two reeds — all led toward the +Z penetration slot for routing in step 4.

Dev-phase summary: [`/hardware/handwork.md`](/hardware/assembly/handwork.md) "Bend copper around the pressure vessel".

### 2. Press ruthex inserts into the outer shell

Six ruthex M3 short heat-set inserts pressed into the top face of the outer_shell, six into the bottom face. Each insert seats in a Ø[4 mm](INSERT_POCKET_D) × [4 mm](INSERT_HALF_DEPTH)-deep printed pocket; another [4 mm](INSERT_HALF_DEPTH) of relief below the insert. Soldering iron tip on the insert; press straight down until flush.

These twelve inserts are the only thread anywhere in the cap stack — the cap and the lid both carry clearance holes — so they are also what clamps a lid for its pour at step 3, and they have to be in before it.

Geometry detail at [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Cap-to-outer-shell joinery".

### 3. Cap foam pour (top and bottom)

Each cap is a [16 mm](CAP_H)-tall foam-filled cup, poured mouth-up with the foam-cap-lid sealing its open face from above. **Bolt the cap and its lid down onto the shell's top face** — six M3 × 25 SHCS through lid and cap into the step-2 inserts, cap floor on the shell. The screws are the pour clamp; expanding foam lifts an unclamped lid, and nothing else in the stack is threaded. Liquid foam enters through the lid's Ø[20 mm](POUR_D) pour hole; air escapes through two Ø[6 mm](LID_VENT_D) vents. Foam expands to fill and cures. Trim flush after cure, then back the six screws out.

Both caps pour in that same top-face fixture, one after the other. The top cap is bolted there in its installed orientation (floor down, mouth + lid up); the bottom cap is the same operation and flips mouth-down at step 6.

The two caps pour identically but they are **not** the same part: only `foam-cap-top` (and `foam-cap-lid-top`) carries the CO2 bore + boss. Keep them labeled — the top cap also goes on rotated 180° at step 6. Geometry detail at [`/hardware/printed-parts/cold-core/foam-cap/foam_cap.py`](/hardware/printed-parts/cold-core/foam-cap/foam_cap.py).

### 4. Body-side install

With the outer shell open-top-up on the bench, install every internal component:

- **Pressure vessel + coil** (per step 1; coil stubs exit through the foam-shell's copper-plug holes) lowered into the cylindrical center cavity, seated on the printed-in `tank_support_ring`. Its CO2 elbow is already made up on the bottom-plate port (below) and rides down the ring's notch as the vessel seats
- **Sensor leads** — the two temperature probes and the two carbonator reeds are already bonded to the vessel under foil (step 1); nothing is bonded in the cavity. Route their leads up and out through the shared +Z slot alongside the other penetrations: at the cold-core exit the two 3-conductor probe leads join SIG-1, the IO26 1-wire bus, and the reed leads join J7, per [`wiring.md`](/hardware/assembly/wiring.md). Seat the leads so the copper-plug clamp and the foam over-pour close around them — no air path may follow the leads inward (that path, not the sensor itself, is the only way condensation reaches a potted probe).
- **Reservoirs** seated into the two ±X bag pockets
- **Penetrations routed through the outer shell walls:**
  - CO2 inlet → enters from above through the foam-cap-top boss + foam-cap-lid-top Ø[6.5 mm](TUBE_HOLE_D) hole at (x=0, z=[-72.75](COTWO_INLET_Z)) — the top cap goes on rotated 180°, which is what puts its bore on the doorway's side; inside the cavity the line drops to a John Guest PP0308E 1/4" PTC 90° elbow standing in the [18](COTWO_NOTCH_W) mm notch cut through the −Z side of the tank support ring, and continues to the vessel's bottom-plate TAISHER NPT elbow via a PP010822E 1/4" PTC × 1/4" NPT M adapter. **That elbow, its adapter and the stub between them are made up on the vessel at the bench**, before the vessel is lowered: the notch is open to the ring's top plateau so the assembled elbow descends with the tank, and nothing has to be reached in under a seated vessel
  - Water outlet → dedicated Ø[6.5 mm](TUBE_HOLE_D) hole, +Z outer wall
  - Reservoir lines (+X, −X) → dedicated Ø[6.5 mm](TUBE_HOLE_D) holes at x=[±97](FLAVOR_HOLE_X), through the bag-pocket +Z wall and the +Z outer wall — the same wall the shared slot pierces, not the ±X far walls. Each reservoir's reed cable leaves through its own Ø[6.5 mm](TUBE_HOLE_D) hole in that wall at x=[±109](CABLE_HOLE_X), outboard of the flavor line ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md))
  - Refrigerant inlet (low), refrigerant outlet (high), water inlet, PRV vent LLDPE → shared Y-elongated slot at x=0 on the +Z outer wall. The water-inlet line transitions from the warm-side GASHER 1/4" NPT check valve via a JG PP010822E 1/4" PTC × 1/4" NPT M adapter before entering the slot as 1/4" OD LLDPE; downstream of the slot a second JG PP010822E (PTC → NPT) takes the LLDPE back to NPT before threading into the TAISHER 1/4" NPT 90° vessel-port elbow on Port 2 (top plate). The PRV vent LLDPE press-fits into the prv-shroud cap, routes through the slot at its own Y height (per foam-shell penetration #8), and terminates open inside the appliance interior.
- **PRV vent LLDPE** press-fits into the cap of the [`/hardware/printed-parts/cold-core/prv-shroud/`](/hardware/printed-parts/cold-core/prv-shroud/) subassembly on Port 4 (threaded into the vessel at [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 9). The LLDPE routes from the cap, takes a slight bend, and enters the +Z shared slot at its allocated Y height. Far end terminates open inside the appliance interior.
- **Four copper plugs** slid down into the shared +Z slot from above, sealing between and above the four pass-throughs (binder-clip geometry in [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Shared +Z slot and copper plug stack")
All fitting-size transitions (3/8" → 1/4", larger fittings) happen on the warm side of the shell; every penetration through the shell wall is 1/4" OD tubing.

### 5. Body foam pour

Mix the two-part PU foam 1:1. Pour the liquid directly into the body's open +Y top, all at once. Foam falls into the body and reaches every open cavity in parallel: outer foam gap, corner pockets at ±Z, and the tank cavity inside the cylinder. Geometry: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Assembly and foam pour".

The **bag pockets take no foam** — each is occupied by its reservoir at [0.5 mm](RESERVOIR_GAP) clearance on every side and at the top, so the pour has no way in. Their interiors stay air, which is what lets the reed cables be threaded out at step 6. Likewise the two reed channels: they stay open through the pour and receive their columns after cure.

Foam expansion may push small amounts of material out through the 0.5 mm clearance bands around tubes in the +Z slot and the tight-fit tube exits at other penetrations. Trim flush after cure.

The pour encapsulates both temperature probes and their leads against the cold metal. Potted in closed-cell foam with no air gap, they need no separate waterproofing — the foam is the vapor barrier. Ensure the pour fully wets around each probe and up its lead entry with no void: a void is a trapped-air pocket that will condense and frost against the cold surface, and is the only path by which moisture reaches a probe. A void at a probe is an insulation defect first and a probe-fouling risk second.

### 6. Final assembly

With all three pours cured:

- Drop the pre-soldered reed columns into the still-open reed channels, one per ±X side, from above. Feed each column's 5-conductor cable out through the channel's open back face, down through the air space in the bag pocket below the reservoir, and out its Ø[6.5 mm](TUBE_HOLE_D) hole at x=[±109](CABLE_HOLE_X) in the +Z wall
- TPU gasket onto the body's top edge — perimeter ring with 8 × 8 mm pads at each of the six screw positions
- Top cap (foam-filled, trimmed from step 2) seated over the gasket **rotated 180° about Z**, so its CO2 bore lands over the CO2 line already standing in the body — the six-screw pattern is 180°-symmetric, so it bolts up either way and only the bore tells you which is right. Six M3 × 25 SHCS through the cap's screw positions and into the top-face inserts
- Second gasket + bottom cap (mouth-down) onto the body's underside, six M3 × 25 SHCS into the bottom-face inserts

## Warm-side check valves

Water-inlet and CO2-inlet lines each carry an inline 1/4" NPT SS PTFE-on-metal check valve (GASHER B0FV2D2FFX) on the warm side, upstream of the shared +Z slot.

- **Water-side check** between the SeaFlo pump's MAACFLOW 1/4" NPT adapter and the first JG PP010822E PTC adapter.
- **CO2-side check** between the DERPIPE 5/16"-tube × 1/4"-NPT push-to-connect and the LTWFITTING bottom-plate barb adapter.

## Output condition

A finished cold core:

- The body foam pour cured, flush-trimmed at visible surfaces and tube exits
- Vessel + bonded coil installed, seated in the cylinder cavity, surrounded by foam; coil inlet/outlet stubs ([500 mm](STUB_LEN) each) protruding through the foam-shell's copper-plug exits
- Both temperature probes potted in the foam against their metal surfaces — DS18B20 (tank-wall, 0x28) on the vessel OD, DS18S20 (coil, 0x10) at the suction end of the coil — leads routed out the +Z slot and sealed, joining SIG-1 at the cold-core exit
- Both carbonator reeds mounted on the vessel wall at the register azimuth, under the foil, leads out the +Z slot to J7
- Both reservoirs seated in their bag pockets
- All eight penetrations routed through their designated holes / slot
- Reed columns dropped into the reed channels, their cables out the +Z wall
- Both foam caps seated over their TPU gaskets, six M3 × 25 SHCS each into the top- and bottom-face heat-set inserts
- External envelope ~[283 mm](OUTER_X) × [181](CCORE_OUTER_Y) × [213.4 mm](OUTER_H)

## Open items

1. **Carbonator reed mounting method — blocks step 1.** The two reeds have to be fixed to the vessel wall on the register azimuth, under the foil skin, in the channel between two coil wraps, and stay put through the wind, the drop into the cavity and the pour. Fixture, retention and the two heights are all unresolved ([`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) open item 6, which also locks the azimuth). Every later station buries the wall, so this method has to land before a vessel is skinned.
2. **Foam data-sheet spec (mix proportions, pot life, cure time, pour temperature window).**
3. **Trim method after foam cure.**
4. **Reservoir-internal assembly procedure.** The reservoir arrives already assembled (cap installed, six M3×12 SHCS into ruthex inserts clamping a TPU gasket, PTFE vent membrane installed). The float-rod cut + seat is specified in [`handwork.md`](/hardware/assembly/handwork.md) "Cut + seat the reservoir float rods" with the rod / float / reed geometry in [`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md); the cap / gasket / vent-membrane / reed-column steps are still to be written here.
5. **Reservoir final-qualification status.** Pending water + syrup-dwell pass.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_cold_core_sync.py`
