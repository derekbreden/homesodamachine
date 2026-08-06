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
| DS18B20 TO-92 (tank, family 0x28) + DS18S20 TO-92 (coil, family 0x10) 1-wire sensors | B0FKG3HT9Q / DigiKey DS18S20+-ND | Two bare TO-92 temperature sensors, leads heat-shrunk; potted into the foam against their metal surfaces. Distinct 1-wire family codes let firmware tell them apart deterministically (no per-unit ID map) — see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 — ON-ORDER |
| Gebildet reed switch × 2 (carbonator level) | B0CW9418F6 | Mounted on the vessel wall under the foil at the register azimuth; same SKU as the reservoirs' eight, one 6-pack covers both with spares ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)) — ON-ORDER |
| Carbonator reed bridge (printed PETG) | [`/hardware/printed-parts/cold-core/reed-bridge/`](/hardware/printed-parts/cold-core/reed-bridge/) | Print, 1 per vessel — holds both reeds on the wall and carries the coil over them |
| Reed-bridge setting gauge (printed PETG) | Same | Print, reusable across builds like the coil mandrel — hangs on the tube's bottom rim, marks the bridge height |
| Coil-winding mandrel (printed PETG) | [`/hardware/printed-parts/cold-core/coil-mandrel/`](/hardware/printed-parts/cold-core/coil-mandrel/) | Print, reusable across builds |
| Foam-shell (printed PETG) | [`/hardware/printed-parts/cold-core/foam-shell/`](/hardware/printed-parts/cold-core/foam-shell/) | Print, Bambu H2C, 0.8 mm nozzle |
| Foam cap × 2 + foam cap lid × 2 (printed PETG) | Same | Print |
| TPU 90A gasket × 2 (printed) | [`/hardware/printed-parts/cold-core/foam-cap/`](/hardware/printed-parts/cold-core/foam-cap/) | Print |
| Copper plug × 4 (printed PETG) | [`/hardware/printed-parts/cold-core/copper-plugs/`](/hardware/printed-parts/cold-core/copper-plugs/) | Print |
| Flavor reservoir × 2 (printed) | [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/) | Print, Bambu PETG Translucent Clear (32101) — the wall reads fill state; the wetted surface is qualified by [`wetted-surface-test.md`](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md), not by the spool |
| M3 × 25 mm SHCS, 12.9 alloy, black oxide × 12 (foam-cap clamp screws) | BNUOK B0DJQGF665 | ACQUIRED |
| M3 × 12 mm SHCS, 304 stainless (18-8) × 12 (reservoir-cap screws) | BNUOK B0DJQGMQZM | ON-ORDER |
| ruthex M3 short heat-set inserts × 42 per build (27 foam-caps — 12 clamp bosses plus 15 deck-mount columns — + 12 reservoir + 3 touch-flo-shell) — **39 of them land here** | ruthex B0D39W228K (100-pc bag = 2.4 builds) | ON-ORDER |
| LVDALAB PTFE membrane filter Ø13 mm × 0.45 µm × 2 (reservoir vent) | B0D41KT345 (100-pc bag = 50 builds) | ON-ORDER |
| Pour-in-place 2 lb 2-part closed-cell PU foam, 1 qt kit | Fiberglass Supply Depot B08R7TX8QJ | ON-ORDER |
| Foam-pour consumables (mixing cups × 4, stir sticks × 4, nitrile gloves × 1 pair per build) | B08JHH1DBF / B09H6ZP447 / B0G8SSMVKW | ACQUIRED |

## Procedure

### 1. Dress the vessel wall, then wind the evaporator coil

Everything that has to touch bare 316L goes on **before** the foil, at the bench, with the vessel in the open:

- The **DS18B20 tank-wall probe** (bare TO-92, family 0x28, leads heat-shrunk) taped flat against the vessel OD, in the bare band below the wind so no wrap has to climb over it. This is the compressor-cycling setpoint sensor, so it reads the vessel wall, not the coil.
- The **two carbonator reed switches**, seated in the printed [`reed-bridge`](/hardware/printed-parts/cold-core/reed-bridge/) — one part per vessel that holds each reed's glass on bare steel and stands the coil off it. A reed has to stand **vertical**: the donut is an axially-magnetised ring, so the field radially outside it on its mid-plane is purely axial, and a reed lying circumferentially reads nothing. Fourteen mm of vertical glass cannot fit between wraps at the [12.33 mm](PITCH) pitch — the channel is 5.98 mm — so a wrap crossing it is unavoidable and the bridge carries the crossing instead. Its bottom edge goes 46.12 mm up from the tube's bottom rim on the rod-register azimuth ([`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 1), which is the shell's ±X line; the printed setting gauge hangs on that rim and marks it. The pockets set the heights — 67.12 mm (`CLO`) and 95.25 mm (`CHI`) — not the bench.

Both go under the foil skin. Neither can be added later: the reed has only a couple of mm of magnet-to-wall budget ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) "Magnet–reed signal-path geometry", measured on this tube), which nothing mounted above the foil or outside the coil leaves — the bridge spends none of it, because its reed pockets are cut through to the steel — and after step 5 the vessel wall is at the bottom of a 15 mm-wide, full-height annulus where none of this is a hand operation.

Wind GOORY 1/4" OD × 0.031" wall ACR copper tubing as a single-layer helical coil around the vessel OD — [12.72 ft](WRAP_FT) of wrap per vessel + a [500 mm](STUB_LEN) tail each end for the refrigerant-loop tie-in stubs. The tie-in stubs exit through the foam-shell's copper-plug holes; brazing happens in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md).

Bond the coil to the vessel OD with 3M 425 aluminum foil tape applied as a continuous skin between vessel and coil.

Before closing the foil skin over the coil's outlet (high) end — the suction side, refrigerant leaving as low-pressure gas, the coldest metal — tuck the **DS18S20 coil probe** (bare TO-92, family 0x10, leads heat-shrunk) flat against the copper and tape it down under the foil. This is the freeze-protect sensor; thermally bonding it to the suction-end copper is what lets the −8 °C cutoff see the coldest point. Distinct 1-wire family codes let firmware tell it and the tank probe apart deterministically, with no per-unit ID map.

Wind around the printed [coil-mandrel](/hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py) — hollow PETG cylinder with a shallow [1 mm](GROOVE_DEPTH) helical guide groove, mandrel OD [123 mm](MANDREL_OD), tank OD [127 mm](TANK_OD), net coil undersize [3 mm](NET_UNDERSIZE). Wind length [119.4 mm](WIND_LENGTH), [9.687](TOTAL_WRAPS) wraps, pitch [12.33 mm](PITCH) — [3.877 m](WRAP_LEN) of copper in the wrap. The wrap runs between the two tails at Y=[47](TAIL_INLET_Y) and Y=[166.4](TAIL_OUTLET_Y) — the elbow bands clear of the vessel, not the slot stations; both tails reach the slot along the port lane. Pull the wound coil off the mandrel and slip it onto the foil-taped vessel. Coil springback: 1–3 mm radial. The wraps land where the pitch puts them; the bridge lifts whichever ones cross it, so the coil is clocked only by its two tails, not to the vessel.

The vessel leaves this step with three lead runs on it — the two probes and the reed pair's 3-conductor bundle — all led toward the +Z penetration slot for routing in step 5.

Dev-phase summary: [`/hardware/handwork.md`](/hardware/assembly/handwork.md) "Bend copper around the pressure vessel".

### 2. Press ruthex inserts into the outer shell

Six ruthex M3 short heat-set inserts pressed into the top face of the outer_shell, six into the bottom face. Each insert seats in a Ø[4 mm](INSERT_POCKET_D) × [4 mm](INSERT_HALF_DEPTH)-deep printed pocket; another [4 mm](INSERT_HALF_DEPTH) of relief below the insert. Soldering iron tip on the insert; press straight down until flush.

These twelve inserts are the only thread anywhere in the cap stack — the cap and the lid both carry clearance holes — so they are also what clamps a lid for its pour at step 3, and they have to be in before it.

Geometry detail at [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Cap-to-outer-shell joinery".

### 3. Cap foam pour (top and bottom)

Each cap is a [16 mm](CAP_H)-tall foam-filled cup, poured mouth-up with the foam-cap-lid sealing its open face from above. **Bolt the cap and its lid down onto the shell's top face** — six M3 × 25 SHCS through lid and cap into the step-2 inserts, cap floor on the shell. The screws are the pour clamp; expanding foam lifts an unclamped lid, and nothing else in the stack is threaded. Liquid foam enters through the lid's Ø[20 mm](POUR_D) pour hole; air escapes through two Ø[6 mm](LID_VENT_D) vents. Foam expands to fill and cures. Trim flush after cure, then back the six screws out.

A lid carries a pad at each of the six screw stations, standing off the face that meets the cap. Seat it pads-into-the-cup: each sinks into the relief its boss column leaves at the mouth, and the head goes down inside the pad's counterbore. The lid prints counterbore-side down, so the face the core stands on comes off the plate.

Both caps pour in that same top-face fixture, one after the other. The top cap is bolted there in its installed orientation (floor down, mouth + lid up); the bottom cap is the same operation and flips mouth-down at step 7.

The two caps pour identically but they are **not** the same part: only `foam-cap-top` carries the fifteen **deck-mount columns**, and only `foam-cap-lid-top` carries their clearance holes. Those stand on its floor and are what the whole electronics shelf bolts to in the finished machine, so the foam pours around their shanks and they are trimmed to nothing. Five stations, and they do not end at the same height: the controller board's four, the AC hub's two, relay #1's four and the ground stud's one rise through clearance holes in the lid and stand proud of it — the board's holding its through-hole tails clear, the ground stud's standing tall enough for its lug fan — while the PSU's four stop at the cap's mouth rim under the lid, and the PSU lies on the lid's own face with its screws crossing it. The stations are owned by [`_cold_core_interface.deck_mounts`](/hardware/printed-parts/cold-core/_cold_core_interface.py). Set a ruthex M3 short into each column's top bore before the pour, the same iron and the same feel as the twelve shell-face inserts at step 2. Keep them labeled — the top cap also goes on rotated 180° at step 7. Geometry detail at [`/hardware/printed-parts/cold-core/foam-cap/foam_cap.py`](/hardware/printed-parts/cold-core/foam-cap/foam_cap.py).

### 4. Reservoir subassembly (both, at the bench)

Both flavor reservoirs are built closed here, off the shell, and go into their pockets as finished units at step 5. Nothing in this step touches the foam shell. The geometry — rod length, float travel, reed heights, cap register, vent stack — is owned by [`reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py), [`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) and [`reservoir/vent.md`](/hardware/printed-parts/cold-core/reservoir/vent.md); this step is the order the bench builds in.

**Reed columns — two, one per reservoir.** Each reservoir's level gauge is four Gebildet reeds standing outside the syrup, on the side the pocket's reed channel runs up. Solder all four onto a single 5-conductor 22 AWG spine — four signal lines plus one shared common — running the column's full length, reed 1 lowest. Lace it with heat-shrink between reeds so the column drops into its channel as one stiff piece. Prove every reed with the donor magnet **before** lacing — closed with the magnet alongside, open with it away; a reed that fails after lacing costs the whole column. The columns are not installed here: the channels stay open through the body pour and take their columns at step 7.

**Float rod + float.** Take the two rods cut and deburred at [`handwork.md`](/hardware/assembly/handwork.md) "Cut + seat the reservoir float rods" — every rod end is a seating face, so a burr falsifies the seat and scores the float bore. Harvest each magnetic float from its YXQ float switch, keeping the stainless capsule and its ferrite ring, discarding the switch body and cable. Seat the rod in the body's blind boss on the wet slope: the tip bottoms on solid PETG, so the slope stays unbroken. Slip the float on. It has to ride the cavity's **far** wall — the wall the reed column stands behind — because the magnet-to-reed budget here is the same couple of millimetres the carbonator reeds live with.

**Close the reservoir.** Press six ruthex M3 inserts into the wall-top bosses. Drop the PTFE membrane into the cap's vent pocket and press the TPU retaining ring over it — a light interference fit, no adhesive. Lay the TPU gasket on the wall top, a perimeter ring with a pad at each screw position. Lower the cap over the rod so its register boss swallows the rod tip, vent boss up, and drive six M3 x 12 SHCS into the inserts. The rod is cut short of the seat-to-seat span precisely so it can never hold the cap off its gasket.

A closed reservoir has its rod standing in the slope boss with the float sliding free, the cap flush on a compressed gasket all round, the membrane held under its ring, vent open and syrup path closed.

### 5. Body-side install

With the outer shell open-top-up on the bench, install every internal component:

- **Pressure vessel + coil** (per step 1; coil stubs exit through the foam-shell's copper-plug holes) lowered into the cylindrical center cavity, seated on the printed-in `tank_support_ring`. Its CO2 elbow and that elbow's PTC adapter are already made up on the bottom-plate port (below); they hang inboard of the ring's bore and descend in open space as the vessel seats, so no shell material is in their way
- **Sensor leads** — the two temperature probes and the two carbonator reeds are already bonded to the vessel under foil (step 1); nothing is bonded in the cavity. Route their leads up and out through the shared slot alongside the other penetrations: at the cold-core exit the two 3-conductor probe leads join SIG-1, the IO26 1-wire bus, and the reed leads join J7, per [`wiring.md`](/hardware/assembly/wiring.md). Seat the leads so the copper-plug clamp and the foam over-pour close around them — no air path may follow the leads inward (that path, not the sensor itself, is the only way condensation reaches a potted probe).
- **Reservoirs** seated into the two ±X bag pockets
- **Penetrations routed through the outer shell walls:**
  - CO2 inlet → dedicated Ø[6.5 mm](TUBE_HOLE_D) hole, −X outer wall, its inner bore starting at y=[-19.05](COTWO_INLET_Y) — beside the water outlet and at the same height, one bore run down the shell's centreline through the tank support ring from the bottom plate's lane-side port. **Nothing turns in the cavity.** The vessel's bottom-plate TAISHER NPT elbow and its PP010822E 1/4" PTC × 1/4" NPT M adapter are made up at the bench and hang inboard of the ring; the 1/4" OD LLDPE is pushed in from outside once the vessel is seated, and bottoms in that collet. Tug-test it before the pour — it is the one joint the foam puts out of reach
  - Water outlet → the TOP CAP's conduit over the port lane. The vessel's bottom-plate Port 3 elbow turns the line laterally onto the lane through its own Ø[6.5 mm](TUBE_HOLE_D) bore across the support ring, and from there the 1/4" OD LLDPE climbs the lane the whole height of the shell and out the conduit onto the deck, where the DIGITEN meter takes it. It is the only line in the lane that goes UP — the other four turn west to the front face — so nothing is stacked against it. Lay it before the pour: it is potted the whole way up
  - Reservoir lines (+X, −X) → dedicated Ø[6.5 mm](TUBE_HOLE_D) holes through the bag-pocket −Y wall at x=[±97](FLAVOR_HOLE_X) — the same wall the shared slot pierces, not the ±X far walls. Each reservoir's reed cable does the same through its own Ø[6.5 mm](TUBE_HOLE_D) bore, leaving the pocket wall at x=[±109](CABLE_HOLE_X) outboard of the flavor line ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)). Reservoir A's line and both cables then turn onto the **port lane**, travel west across the pour band to the −X outer wall, and cross it at their own station on the front port field — so the second bore is a height on the shared column, not a hole on the line's own axis, and the pocket-wall X and the outer-wall Z are independent. The two-bore geometry is in [`foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Two-bore front pass-throughs". Reservoir B's line crosses its pocket's **+Y** wall instead, onto the west lane, and climbs that lane to the top cap's `reservoir-b` conduit — one bore in the shell, and the second feature in the cap
  - Refrigerant inlet (low), refrigerant outlet (high), PRV vent LLDPE → shared Z-elongated slot on the port lane, in the −X outer wall, directly above the front port field. The PRV vent LLDPE press-fits into the prv-shroud cap, routes through the slot at its own Z height, and terminates open inside the appliance interior.
  - Water inlet → the TOP CAP's conduit, which stands at the cap's own west end rather than over the vessel's top-plate Port 2. That port carries a TAISHER 316L SS elbow like the other three ([`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 9), with a JG PP010822E 1/4" PTC × 1/4" NPT M made up on its lateral FNPT and the collet turned into the band. A length of 1/4" OD LLDPE leaves that collet, runs the [14](TOP_BAND) mm band between the top plate and the cap's floor, comes about and climbs the conduit's Ø6.5 bore out onto the deck, where the SeaFlo's discharge chain meets it. The band is shallower than the [25.4 mm](LLDPE_BEND_R) arc the tubing wants, so the corner off the elbow is tighter than that — lay it before the pour, because it is potted where it turns
- **PRV vent LLDPE** press-fits into the cap of the [`/hardware/printed-parts/cold-core/prv-shroud/`](/hardware/printed-parts/cold-core/prv-shroud/) subassembly on Port 4 (threaded into the vessel at [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) step 9). The LLDPE routes from the cap, takes a slight bend, and enters the shared slot at its allocated Z height. Far end terminates open inside the appliance interior.
- **Four copper plugs** slid down into the shared slot from above, sealing between and above the four pass-throughs (binder-clip geometry in [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Shared slot and copper plug stack")
All fitting-size transitions (3/8" → 1/4", larger fittings) happen on the warm side of the shell; every penetration through the shell wall is 1/4" OD tubing.

### 6. Body foam pour

Mix the two-part PU foam 1:1. Pour the liquid directly into the body's open +Z top, all at once. Foam falls into the body and reaches every open cavity in parallel: outer foam gap, corner pockets at ±Z, and the tank cavity inside the cylinder. Geometry: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Assembly and foam pour".

The **bag pockets take no foam** — each is occupied by its reservoir at [0.5 mm](RESERVOIR_GAP) clearance on every side and at the top, so the pour has no way in. Their interiors stay air, which is what lets the reed cables be threaded out at step 7. Likewise the two reed channels: they stay open through the pour and receive their columns after cure.

Foam expansion may push small amounts of material out through the 0.5 mm clearance bands around tubes in the slot and the tight-fit tube exits at other penetrations. Trim flush after cure.

The pour encapsulates both temperature probes and their leads against the cold metal. Potted in closed-cell foam with no air gap, they need no separate waterproofing — the foam is the vapor barrier. Ensure the pour fully wets around each probe and up its lead entry with no void: a void is a trapped-air pocket that will condense and frost against the cold surface, and is the only path by which moisture reaches a probe. A void at a probe is an insulation defect first and a probe-fouling risk second.

### 7. Final assembly

With all three pours cured:

- Drop the pre-soldered reed columns into the still-open reed channels, one per ±X side, from above. Feed each column's 5-conductor cable out through the channel's open back face, down through the air space in the bag pocket below the reservoir, out its Ø[6.5 mm](TUBE_HOLE_D) hole at x=[±109](CABLE_HOLE_X) in the pocket's +Z wall, then along the pour band to the outer wall's hole. Lay it in the band before the pour: it is potted where it crosses
- TPU gasket onto the body's top edge — perimeter ring with 8 × 8 mm pads at each of the six screw positions
- Top cap (foam-filled, trimmed from step 3) seated over the gasket **rotated 180° about Z**, which is what stations its fifteen deck-mount columns under the electronics shelf that bolts to them — the six-screw pattern is 180°-symmetric, so it bolts up either way, and the column pattern, which is not symmetric, is what tells you which is right. Six M3 × 25 SHCS through the cap's screw positions and into the top-face inserts
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
- Both carbonator reeds in the reed-bridge on the vessel wall at the register azimuth (`CLO` at [67.12 mm](LOW_LEVEL), `CHI` at [95.25 mm](HIGH_LEVEL) above the tube's bottom rim), under the foil, leads out the +Z slot to J7
- Both reservoirs seated in their bag pockets
- All eight penetrations routed through their designated holes / slot
- Reed columns dropped into the reed channels, their cables out the −X wall, at their own front-field stations
- Both foam caps seated over their TPU gaskets, six M3 × 25 SHCS each into the top- and bottom-face heat-set inserts, every head down in its lid counterbore — run a straightedge across each lid, nothing touches it before the plate does
- External envelope ~[283 mm](OUTER_X) × [181](CCORE_OUTER_Y) × [253.4 mm](CCORE_CAPPED_H) with both caps on — the shell alone is [213.4 mm](OUTER_H) tall, and each face adds a cap and its gasket

## Open items

1. ~~**Carbonator reed mounting method.**~~ **CLOSED.** The printed [`reed-bridge`](/hardware/printed-parts/cold-core/reed-bridge/) is the mount, the retention and the height gauge at once: reed pockets cut through to bare 316L so the mount adds no standoff, a 3 mm plateau the crossing wrap rides over, ramps on all four sides so the coil can be dragged down over it, and its own setting gauge off the tube's bottom rim. Heights `CLO` 67.12 mm / `CHI` 95.25 mm, derived from the wetted column in the part's README. Azimuth locked at [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) open item 6.
2. **Foam data-sheet spec (mix proportions, pot life, cure time, pour temperature window).**
3. **Trim method after foam cure.**
4. ~~**Reservoir-internal assembly procedure.**~~ **CLOSED.** Written up as step 4 — reed columns, rod + float, and the cap / gasket / vent-membrane close. The float-rod cut is [`handwork.md`](/hardware/assembly/handwork.md) "Cut + seat the reservoir float rods"; the geometry is owned by [`reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py), [`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) and [`reservoir/vent.md`](/hardware/printed-parts/cold-core/reservoir/vent.md).
5. **Reservoir final-qualification status.** Pending water + syrup-dwell pass.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_cold_core_sync.py`
