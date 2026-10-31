# Cold Core Assembly

The procedure for assembling the cold core — the back-of-enclosure subsystem that contains the carbonator, its wound evaporator coil, two flavor reservoirs, and the surrounding pour-in-place polyurethane foam, all held together inside a 3D-printed PET-GF shell stack.

Foam-pour geometry, shell architecture, copper feed-throughs, and dry casing seam seals: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md).

## Scope

In: one hydro-tested + passivated carbonator (output of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md)), with the water-inlet jet fit and full root fusion qualified and recorded per [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md); GOORY 1/4" OD × 0.031" wall ACR copper tubing for the evaporator coil; 3M 425 aluminum foil tape; the printed coil-winding mandrel; the printed shell stack (foam-shell, foam-cap × 2, foam-cap-lid × 2 — all PET-GF; reservoir × 2 — PETG); reservoir TPU gaskets × 2; pour-in-place 2 lb closed-cell polyurethane foam (two-part 1:1); M3 × 25 SHCS × 20 and ruthex M3 inserts × 20 for the cap clamps, plus eight deck-mount inserts for the pump and PCB and three M3 × 10 screws with full-length inserts for the B-fill channel clamps.

Out: a fully foam-poured cold core, capped with exterior foil-sealed dry joints, with the wound evaporator coil bonded around the carbonator and its inlet/outlet stubs protruding through the foam-shell's copper exits — [200 mm](PROT_INLET) of inlet stub, [175 mm](PROT_OUTLET) of outlet stub, measured from the shell face.

Not in scope: refrigerant-loop integration ([`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)) — brazing of the coil stubs onto the donor unit's cap tube and suction line, vacuum, charge, run-up. Also not in scope: enclosure-side assembly (electronics bay, compressor + condenser + fan placement, AC wiring), faucet install, final integration.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 (refrigeration — GOORY copper tubing for the coil) + §6 (cold-core insulation, 3M 425 foil tape + pour-in-place foam + foam-pour consumables) + §13 (mechanical attach hardware + reservoir-cap vent filter) + §7 (the printed parts themselves, each row on its own stock's $/kg). Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6 + §11.

| Item | Source | Status (per purchases.md) |
|---|---|---|
| Carbonator | Output of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) | Hydro-tested + passivated |
| GOORY 1/4" OD × 0.031" wall ACR copper tubing | B0DKSW5VL9 | ~[15.78 ft](CUT_FT) per carbonator for coil wrap + tie-in stubs ([1/3](ROLL_SHARE) of 50 ft roll per build) — ACQUIRED |
| 3M 425 aluminum foil tape | B07BTW7C2N | Coil-to-carbonator thermal interface and dry casing-seal bands; about 21.1 ft per build — ACQUIRED |
| DS18B20 TO-92 (carbonator, family 0x28) + DS18S20 TO-92 (coil, family 0x10) 1-wire sensors | B0FKG3HT9Q / DigiKey DS18S20+-ND | Two bare TO-92 temperature sensors, leads heat-shrunk; potted into the foam against their metal surfaces. Distinct 1-wire family codes let firmware tell them apart deterministically (no per-unit ID map) — see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 — ACQUIRED |
| MDSR-7-10-15 reed switch × 2 (carbonator level) | Littelfuse / Mouser 934-MDSR-710-15 | Mounted on the carbonator wall under the foil at the register azimuth; same stock as the reservoirs' eight ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)) — ACQUIRED |
| Carbonator reed bridge (printed PETG) | [`/hardware/printed-parts/cold-core/reed-bridge/`](/hardware/printed-parts/cold-core/reed-bridge/) | Print, 1 per carbonator — holds both reeds on the wall and carries the coil over them |
| Reed-bridge setting gauge (printed PETG) | Same | Print, reusable across builds like the coil mandrel — hangs on the tube's bottom rim, marks the bridge height |
| Coil-winding mandrel (printed PETG) | [`/hardware/printed-parts/cold-core/coil-mandrel/`](/hardware/printed-parts/cold-core/coil-mandrel/) | Print, reusable across builds |
| Foam-shell (printed PET-GF) | [`/hardware/printed-parts/cold-core/foam-shell/`](/hardware/printed-parts/cold-core/foam-shell/) | Print, Bambu H2C, 0.4 mm hardened Standard-flow nozzle on the left hotend — slice the `.stl`, not the `.step` |
| Foam cap × 2 + foam cap lid × 2 (printed PET-GF) | Same | Print, same plate figures as the shell; slice the smooth caps’ `.stl` |
| Reservoir TPU gasket × 2 (printed) | [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/) | Print; one wet lid seal per reservoir |
| Flavor reservoir × 2 (printed) | [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/) | Print, Bambu PETG Translucent Clear (32101) — the wall reads fill state; the wetted surface is qualified by [`wetted-surface-test.md`](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md), not by the spool |
| M3 × 25 mm SHCS, 12.9 alloy, black oxide × 20 (foam-cap clamp screws) | BNUOK B0DJQGF665 | ACQUIRED |
| M3 × 12 mm SHCS, 304 stainless (18-8) × 12 (reservoir-cap screws) | BNUOK B0DJQGMQZM | ACQUIRED |
| ruthex M3 **full-length** heat-set inserts × [43](CC_INSERTS) — every one this procedure presses ([31](CAP_INSERTS) foam-caps: [20](CAP_CLAMP_INSERTS) face clamps, [8](CAP_DECK_INSERTS) equipment columns and [3](B_FILL_CLAMPS) B-fill channel clamps, + [12](RES_INSERTS) reservoir). **RX-M3x5.7, not the short RX-M3Sx4.0** — both bags are brass M3 in a ⌀4 hole and only the body length tells them apart, so check the trough label before the iron goes on. Every pocket in this procedure was already bored deep enough for the long body. The faucet plate, PSU and wall relays use their separately specified short inserts; the cap equipment uses the full-length family. `bom.md` §13 carries the appliance total. | ruthex B08BCRZZS3 (100-pc bag) | ACQUIRED |
| Pour-in-place 2 lb 2-part closed-cell PU foam, 1 qt kit | Fiberglass Supply Depot B08R7TX8QJ | ACQUIRED |
| M3 × 10 mm SHCS × [3](B_FILL_CLAMPS), with the full-length inserts counted above | BNUOK B0DJQGGDP2 | ACQUIRED; close the B-fill channel clamps before threading the tube or installing the PCB |
| Foam-pour consumables (mixing cups × 4, stir sticks × 4, nitrile gloves × 1 pair per build) | B08JHH1DBF / B09H6ZP447 / B0G8SSMVKW | ACQUIRED |

## Procedure

### 1. Dress the carbonator wall, then wind the evaporator coil

Everything that has to touch bare 316L goes on **before** the foil, at the bench, with the carbonator in the open:

- The **carbonator earth lead**, green 16 AWG, with its steel-side closed ring clamped to the existing upper vessel rim per [the metal attachment procedure](/hardware/assembly/pressure-vessel.md#upper-rim-earth-bond). Point the crimp barrel upward and dress the lead toward the shared west-side seven-core sensor passage. Keep the lid-side end unterminated for threading through the cup and lid. Check steel-to-free-wire continuity before the connection is covered; the lid-side ring is crimped after threading at step 5.
- The **DS18B20 carbonator-wall probe** (bare TO-92, family 0x28, leads heat-shrunk) taped flat against the carbonator OD, in the bare band below the wind so no wrap has to climb over it. This is the compressor-cycling setpoint sensor, so it reads the carbonator wall, not the coil.
- The **two carbonator MDSR-7-10-15 reeds**, vertical on bare steel in the printed [reed bridge](/hardware/printed-parts/cold-core/reed-bridge/README.md), on the rod-register azimuth. The provisional bridge bottom is [38.18 mm](BRIDGE_Z_BOTTOM) above the bottom tube rim, with pocket centers [58.332 mm](REED_LOW_Z) (`CLO`) and [86.484 mm](REED_HIGH_Z) (`CHI`). Water targets remain [67.1 mm](LOW_LEVEL) and [95.25 mm](HIGH_LEVEL). [Calibrate finished-float immersion and directional crossings](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration) before fixing the final bridge, foil and coil. The 14 mm mounting envelope crosses the [5.976 mm](INTER_WRAP_CLEAR) space between copper wraps, so the bridge carries the crossing.

Both go under the foil skin. The bridge's through-pockets put the reeds against bare steel at the specified radial datum. The [RC62 bench reach and installed calibration scope](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md#running-room-and-magnetic-path) apply to this float; foil and coil placement must preserve the measured switching positions. After step 5 the carbonator wall is at the bottom of a 14.62 mm-wide, full-height annulus, so install and prove the sensors before the pour.

Wind GOORY 1/4" OD × 0.031" wall ACR copper tubing as a single-layer helical coil around the carbonator OD — [13.15 ft](LAID_FT) of wrap per carbonator as it lies on the carbonator, plus one tie-in allowance per end: [354.4 mm](STUB_INLET) at the inlet, [446.9 mm](STUB_OUTLET) at the outlet. **The two are not the same length, and neither is spare copper.** Each is that tail's own run — off the helix, down its lane, out through the shell wall — plus the length that protrudes past the shell for the brazier to work with; the outlet's in-shell run is the longer of the two, its protrusion the shorter. The tie-in stubs exit through the foam-shell's copper holes; brazing happens in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md).

Bond the coil to the carbonator OD with 3M 425 aluminum foil tape applied as a continuous skin between carbonator and coil.

Before closing the foil skin over the coil's outlet (high) end — the suction side, refrigerant leaving as low-pressure gas, the coldest metal — tuck the **DS18S20 coil probe** (bare TO-92, family 0x10, leads heat-shrunk) flat against the copper and tape it down under the foil. This is the freeze-protect sensor; thermally bonding it to the suction-end copper is what lets the −8 °C cutoff see the coldest point. Distinct 1-wire family codes let firmware tell it and the carbonator probe apart deterministically, with no per-unit ID map.

Rough-form with the printed [coil mandrel](/hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py),
a hollow PETG drum of OD [123 mm](MANDREL_OD). Set the finished winding on the
foil-taped [127 mm](TANK_OD) vessel: [9.500](TOTAL_WRAPS) right-hand turns over
[119.4 mm](WIND_LENGTH), pitch [12.57 mm](PITCH). Feed material from the long
unfinished ends while setting that diameter and pitch. The lower helix end is
on −Y at Z47.00 mm; the upper end is on +Y at Z166.40 mm. Form both complete
R15 mm tangent tails per EVAP-01: opposite plan offsets to the two lanes,
an inlet vertical dogleg, and an outlet vertical drop. Both exits retain their
−X direction at Y=±77.50 mm, Z28.425 mm. The winding eases over the reed bridge
at the drawing's specified radial relief and contacts the vessel elsewhere.

The carbonator leaves this step with the two temperature probes, fixed east-side reed pair and upper-rim earth lead attached. The coil probe is the temperature bus's incoming feed point. Their seven free conductors gather at the shared west-side `sensor-cable` riser during the open-body routing in step 5.

The [EVAP-01 production drawing](/hardware/cold-core-layout/evaporator-coil-drawing.pdf)
controls the complete formed tube, all tail bends and straights, exit coordinates,
working lengths and inspection before foam. Sheet 2 gives the tangent stations
and bend data. Coil-forming instructions: [`handwork.md`](/hardware/assembly/handwork.md)
"Bend copper around the pressure vessel".

### 2. Press ruthex inserts into the outer shell

[10](CAP_FACE_SCREWS) ruthex M3 heat-set inserts pressed into the top face of the outer_shell, [10](CAP_FACE_SCREWS) into the bottom face — the **full-length** RX-M3x5.7. Each insert seats in a Ø[4 mm](INSERT_POCKET_D) pocket, [5.7 mm](INSERT_LEN) of body with [4.8 mm](INSERT_RELIEF) of relief below it. Soldering iron tip on the insert; press straight down until flush.

These twenty shell inserts supply the cap-clamp threads — the cap and the lid both carry clearance holes — so they also clamp each lid for its pour at step 3, and must be in before it. The eight deck-mount inserts belong to the top cap's pump and PCB columns.

Geometry detail at [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Cap-to-outer-shell joinery".

### 3. Cap foam pour (top and bottom)

Each cap is a foam-filled cup, poured mouth-up with the foam-cap-lid sealing its open face from above — [15.7 mm](CAP_H) of pour at the bottom end and [12.3 mm](CAP_H_TOP) at the top, where the lid's own plate stands in the last head pad of the cup's wall. **Bolt the cap and its lid down onto the shell's top face** — [10](CAP_FACE_SCREWS) M3 × 25 SHCS through lid and cap into the step-2 inserts, cap floor on the shell. Mask the exterior cap/lid joint and open-sided head pockets with removable tape before pouring; the 0.15 mm rigid-fit gap is not a liquid-foam seal. Keep the pour and vent openings clear. The ten face screws engage the shell inserts and hold the lid down while the foam expands. Liquid foam enters through the lid's Ø[20 mm](POUR_D) pour hole; air escapes through two Ø[6 mm](LID_VENT_D) vents. Foam expands to fill and cures. Trim flush after cure, then back all ten screws out.

The **bottom lid** carries a pad at each of the [10](CAP_FACE_SCREWS) screw stations, standing off the face that meets the cap. Seat it pads-into-the-cup: each sinks into the relief its boss column leaves at the mouth, and the head goes down inside the pad's counterbore. It prints counterbore-side down, so the face the core stands on comes off the plate.

The **top lid** has no pads. Its nominal plate is [5.4 mm](FOAM_CAP_LID_H) thick and its cup is one pad shorter for it, so what meets the cap's mouth rim is the plate's own flat underside — and that underside is the face it prints on, with the V-B upright socket wall, V-A feed clip, check bridge, V-B return restraint, two paired Reservoir A tube seats, wiring wells and deck-mount bores building up from it. The B-fill channel crosses the plate beneath its retaining roof.

Both caps pour in that same top-face fixture, one after the other. The top cap is bolted there in its installed orientation (floor down, mouth + lid up); the bottom cap is the same operation and flips mouth-down at step 7.

Only `foam-cap-top` carries the eight cup-rooted equipment columns: four pump feet and four PCB posts, all defined by the native component holes in [`_above_core_mounts.py`](/hardware/printed-parts/cold-core/_above_core_mounts.py). Press one full-length ruthex RX-M3x5.7 into each Ø4 × 9.75 mm blind pilot before the pour. The PCB posts pass through the lid to a 3.6 mm standoff. The pump columns stop below the 5.4 mm lid. The [cap schedule](/hardware/printed-parts/cold-core/foam-cap/README.md) specifies their screw stacks and tolerance allowances.

Seat three full-length RX-M3x5.7 inserts in the cup's B-fill clamp pilots. Fit the lid and close the three recessed M3 × 10 screws before threading the tube or installing the PCB. Feed reservoir B's continuous black 1/4-inch LLDPE fill tube through the fore-facing entry, around the guide and out the cup floor, with its V-I end free. The lower tube enters the TPU fill grip at world X−43.5/Y233.3 and finishes nominally at Z228.15, 1 mm below the reservoir plate in the headspace; its short tip may remain slightly angled. Mask every tube/cable passage and the dry B-fill passage joint for the cap pour; clear the masks after cure. Keep the source end loose until the populated core and front-top are staged for their final connection. Terminate both J10 power leads on the loose PCB before fastening it to its posts, then land their free ends at the core WAGOs.

V-B presses into the lid's upright wall east of the PCB using the shared [V69 socket fit](/hardware/printed-parts/valve-seat/README.md). Its wall travels with the populated core. V-A and V-K, their fitted elbows and the inlet header are prepared on back-top at [internal plumbing](/hardware/assembly/internal-plumbing.md); they do not mount on this lid. Four DC/sensor connector wells belong to the core lid. The selected native layout and its qualification limits are recorded in the [cap reference](/hardware/printed-parts/cold-core/foam-cap/README.md). Keep both cap orientations labeled; the top cap and lid install rotated 180° at step 7.

The G Ganen's four identical rubber feet have nominal 7 mm pads and slide independently along the casing rails. Their full clips reach the fore/aft rail ends, with slot centers at reference X = 9.5 and 67.5 mm and Y = ±38.5 mm. Each M3 × 20 screw sits 1.5 mm outward within its slot so its Ø9 × 0.8 mm washer lies flat clear of the raised shoulder. Align the feet with the printed lid holes and fasten the pump while its four driver approaches are open. Close and seal the cap-clamp screws before installing the PCB over them. Check actual screw passage, flat washer seating, thread engagement and rubber compression during assembly. The [installation reference](/hardware/reference/g-ganen-pump/installation/README.md) carries the cap axes and native checks. The cap's mount stations and conduit pattern identify its installed rotation.

The V-B return has its own integral lid restraint and one six-inch narrow tie.
Thread its holder before seating the fitting. Fasten the pump before making
up the reinforced PVC joints and discharge stem check, following
[internal plumbing](internal-plumbing.md) §2. The meter, rear snap seat and
cap, continuous inlet, R14 holder and single 61 mm square-ended foam piece
belong to back-top. Prepare them on the open shell. The meter's short rear
tube joins SODA directly. The inlet continues through the core's plain guide
without a tube joint or cut. Seat the two 4 mm flavor lines in their separate
upward-opening lid clips after the larger plumbing is in place.

At the final upper connections, seat the straight white V-A feed in the lid's
upward-opening C2 clip before finally dressing `PE-carbonator` and `J4-V5`.
Press the continuous tube downward into the clip with the funnel frame absent;
keep the two leads clear of the loading approach. The run is logical `fluid-3`,
drawn as `above-core-va-fore-feed`; its fittings and tube path retain their
existing datums. Release it from the lid before moving back-top for service.
[Internal plumbing](internal-plumbing.md#5-final-connections-through-the-funnel-opening)
gives the connection sequence.

The main PCB uses the full-length inserts prepared here. The PSU mounts in back-top's shallow ceiling recess; both relays mount on its dry west wall. Their short inserts are installed during enclosure assembly.

The Reservoir A fill/draw pair uses two integral fore C2 clips on one broad lid
base at Y209.75, Z258.5 mm, with draw at X50.5 and fill at X64.0 mm. Press each
continuous tube downward through its open +Z mouth. For removal, release the
exposed jaws and lift the tube upward. At the aft station, Y304 mm, thread one four-inch narrow tie
through the empty transverse slot before laying in the pair; one common tie retains
both tubes there. Its slot has 3 mm of seat floor above it. Their plain cap guides add
no joint or physical tube cut; follow the combined warm/internal preparation in
[internal plumbing](internal-plumbing.md). Tighten the pump screws before threading
the continuous draw tube, which crosses one driver approach; remove the tube for that
screw’s service. The selected quarter-inch C2 bore and spring section have
[accepted coupon fit](../../future/snap-fit-tests/2026-10-26-mark2-combined/physical-result.json).
The complete widened station's print, installed access, numerical insertion and
retention forces, and lifetime remain unqualified; the aft tie witness does not
qualify threading, head engagement or retention.

### 4. Reservoir subassembly (both, at the bench)

Both flavor reservoirs are built closed here, off the shell, and go into their pockets as finished units at step 5. Nothing in this step touches the foam shell. The geometry — rod length, float travel, reed heights, cap register, vent stack — is owned by [`reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py), [`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) and [`reservoir/vent.md`](/hardware/printed-parts/cold-core/reservoir/vent.md); this step is the order the bench builds in.

**Reed columns — two, one per reservoir.** Each reservoir's level gauge is four MDSR-7-10-15 reeds standing outside the syrup, on the side the pocket's reed channel runs up. Calibrate their liquid crossings per the [float installation procedure](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration), then solder all four onto a single 5-conductor 22 AWG spine — four signal lines plus one shared common — running the column's full length, reed 1 lowest. Lace it with heat-shrink between reeds so the column drops into its channel as one stiff piece. Prove every reed with the printed RC62 float **before** lacing — closed with the magnet alongside, open with it away; a reed that fails after lacing costs the whole column. The columns are not installed here: the channels stay open through the body pour and take their columns at step 7.

**Float and guide.** Use the one-piece 36 × 28 mm ASA Aero float with a midplane RC62 and 4.8 mm bore. Reservoir rods stand 20 mm from the wet far wall, at (±106.25, 32.5) mm. The cap register and body boss share that axis. Check free travel and calibrate liquid switching before fixing reed heights; [current datums and procedure](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md).

**Close the reservoir.** Press six ruthex M3 full-length inserts into the wall-top
bosses, in the 7 mm pockets. Fit two liquid-tube TPU spools and one air-tube
spool into the lid's matching 45° seats; both ends sit flush with the 4 mm
plate. Lay the perimeter TPU gasket on the body rim, lower the lid over the
rod and drive six M3 × 12 SHCS into the inserts. The rod remains short of its
seat-to-seat span so it cannot hold the lid off the gasket.

The closed reservoir has a freely sliding float, a clamped rim gasket, two
captured liquid-tube grips and a flush air-tube grommet. Nothing
pierces the body below the cap. Print four liquid-tube spools and two air-tube
spools in Bambu TPU 90A per machine.

### 5. Body-side install

With the outer shell open-top-up on the bench, install every internal component:

- **Carbonator + coil.** Leave both long tails free for feeding, with straight, deburred ends. Lower the carbonator partway into the center cavity with its coil clocked to the two lanes. Feed each bare tail through its Ø7.5 mm shell hole from inside, then lower the carbonator in stages while drawing the tails outward and forming broad curves. Keep the copper approximately normal to the wall through each hole; hold the tube itself while forming it, so the printed wall does not act as the bending tool. Seat the carbonator on the printed-in `carbonator_support_ring` and form the final lane bends. Retain at least the modeled R12.7 centerline bend radius and reject a kinked, creased or visibly flattened section. Leave the specified 200 mm inlet and 175 mm outlet working lengths outside the shell for refrigeration integration. Its two bottom-plate push-fit elbows are already made up and aimed (below); they hang inboard of the ring and descend in open space as the carbonator seats, so no shell material is in their way
- **Sensor leads** — the two temperature probes and two carbonator reeds are bonded to their specified metal surfaces before the carbonator descends into the shell. Keep the reeds at their fixed east-side positions. Feed the three-wire temperature bus at the coil probe first, continuing to the carbonator-wall probe. Turn the coil-side feed aft below the PRV vent at world Z184, then rise at Y347. Transfer CLO, CHI and their common over the open vessel head at world Z225/Y352 to the west side. Bring these six signal conductors and the green 16 AWG carbonator earth lead together at world X−48/Y347. Their shared Ø7.5 mm `sensor-cable` guide is straight through the upper cup and lid; its upper mouth is on Z253.4. Lay the internal transitions while the body is open, before the pour. Seat the leads so foam closes around them, and keep the free ends ready for threading through the cap and lid. The temperature bus joins J4 and its sensor-common WAGO; the reed leads join J7 and its existing reed-common WAGO. The reservoir reed channels carry only their own five-conductor columns.
- **Reservoirs** seated into the two ±X bag pockets
- **Earth termination.** Thread the free earth-wire end through both the upper cup and lid before crimping its lid-side M3 ring. With both prints still loose on the loom and the steel accessible, repeat and record steel-to-ring continuity before the body pour. Keep that ring outside the lid for the final earth stack; the finished ring does not need to pass through the cable bore.
- **Penetrations.** Fluid lines cross this core's boundary through the top cap, including B-fill's fore-facing entry. The shell's −X face is mated against the refrigeration base — the condenser flush on it, the compressor's plate just short of that plane — so a bore struck there would open into that base rather than into the machine. What crosses that face is the **two copper evaporator lines, each through its own round hole**. Reservoir A's reed ribbon and the shared seven-core sensor/earth loom use two passages through the upper cup and lid. Reservoir B's ribbon leaves through the shell-rim notch.

  **The carbonator and both reservoirs fill high and draw low.** Their water or flavor fill enters above the liquid and their draw leaves at the lowest point. That is what the air-purge and clean-flush service modes in [`fluid-topology.md`](/hardware/topology/fluid-topology.md) run on.

  - Water inlet → the top cap's plain `water-in` guide. The carbonator's top-plate Port 2 carries the TAISHER 316L SS elbow and JG PP010822E 1/4-inch PTC × 1/4-inch NPT male adapter in their fixed clocking. One continuous white 1/4-inch LLDPE tube leaves that adapter, turns upward at nominal R14 before the cup floor and passes straight through world (−53, 288.7265, 253.4) mm. Above the guide, an accessible R18 arch enters the check's upward outlet elbow; the guide adds no fitting, insertion or physical cut. Lay this route before the pour. The [water-inlet jet](/hardware/assembly/water-inlet-jet.md) is welded onto the metal elbow's downward male tip, after the 90° turn, and discharges into headspace above the water line. Confirm its qualified assembly record and outlet clearance before the pour. Use the combined internal/warm path and actual receiving-end marks per [Internal plumbing](internal-plumbing.md#parts-and-cut-lengths); the CAD span split at the lid does not create separate tube blanks.
  - CO2 inlet → the top cap's `co2-in` conduit. **The lane end is fed from above:** the line falls the shell's whole height down the port lane, runs along the lane's floor, and leans in across the shell's floor through **one of the carbonator support ring's own slots** — the 307° one — to the bottom plate's lane-side port at y=[-19.05](COTWO_INLET_Y), passing outboard of reservoir A's pocket corner. The carbonator's bottom-plate neoFit AME4-N2-E push-fit male elbow is made up at the bench, aimed along this line, and hangs inboard of the ring; the tube bottoms in its socket, so **nothing is made up in the cavity**. Lay it down the lane before the top cap goes on — it is not pushed in from outside — and tug-test it before the pour, because it is the one joint the foam puts out of reach. Inside the carbonator Port 1 is a plain opening below the liquid. Gas flows only while its supply pressure exceeds local carbonator pressure, then rises toward the headspace; there is no internal barb, silicone hose or stone.
  - Carbonated-water outlet → the top cap's `carb-water-out` conduit, and the carbonator's own drain. **It has no bore in this shell at all.** The bottom-plate Port 3 push-fit elbow takes the blue tube in its own socket and turns the line laterally under the carbonator, and it leaves the carbonator support ring through **one of the ring's own slots** — the 217° one, which already exists to let the pour reach the under-carbonator floor and which lies where a line heading for this conduit's column wants to go. The CO2's lean crosses at the 307° slot, one each. So neither crossing costs a bore and all four bearing segments stay whole. From there the 1/4" OD LLDPE climbs beside the coil, in the middle of the annulus between the coil and reservoir B's pocket wall and inboard of the port lane because the CO2 owns the lane's own strip at the bottom of the shell, turns above the tank at world Z219.4 while the main body is open, and rises straight through the cup and lid at world (50, 342.4148, 253.4) mm. The same uncut tube continues above the guide through its accepted R14 printed bend holder directly into the meter inlet. The guide adds no insertion, joint or physical cut. Lay it before the pour: it is potted the whole way up
  - Reservoir draws → nothing to route here. Each reservoir's draw line is its own dip tube: one length of black 1/4" OD LLDPE from its draw valve, down the top cap's `reservoir-a` or `reservoir-b` conduit and the draw bore in that reservoir's cap to its floor, the end cut at 45° ([floor and dip tube](/hardware/printed-parts/cold-core/reservoir/floor-and-dip-tube.md)). Feed each tube down its open cap passage from above once the top cap is on; Both draw passages and reservoir bores share one straight axis. The dip tubes remain unpotted
  - Reservoir fills → A-fill has an aligned straight cap passage and reservoir seat at shell (102.5, −61) mm. B-fill's continuous tube is threaded through the top cap's fore-entry passage at step 3. Guide its lower end through reservoir B's flush TPU fill grip as the cap seats at step 7; its tip finishes at world Z228.15, 1 mm below the plate in the **headspace**. Both liquid entries use the flush TPU grips.
  - Reservoir air → two straight white 4 mm OD / 2.5 mm ID tubes, nominally 31.25 mm each. Feed each through its dedicated foam-cap passage and the reservoir's air grip, leaving 6 mm above the outer cap. Its lower tip stands 1 mm below the reservoir plate, open to the headspace. Keep both ends open; [air-tube installation](/hardware/printed-parts/cold-core/reservoir/vent.md).
  - Reed cables → **neither crosses a pocket wall.** Each leaves by the top of the channel its own column stands in, up through the conduit the cap carries over that mouth ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)). The channel is open floor to top face, so the cable's whole run inside the core is the slot it was laced into. No pocket wall is opened at all
  - Refrigerant inlet and outlet → two Ø7.5 mm holes in the −X outer wall at native Y ±77.5 mm, Z 28.425 mm. The inlet takes the port lane and the outlet the west lane. Feed the tails during the carbonator descent described above, before installing the reservoirs and the other potted routes.
- **PRV vent LLDPE** pushes into the barrel bore of the [`prv-shroud`](/hardware/printed-parts/cold-core/prv-shroud/) subassembly on Port 4. The short tube falls from the downward barrel bore, turns once and crosses the shell's **+Y flank** at the station defined by [`_internal_routes.py`](/hardware/printed-parts/cold-core/_internal_routes.py). Cut its free mouth flush with the flank so it opens into the enclosure's west-wall relief chase. The chase carries discharge outside the cabinet. Keep the tube and chase clear; geometry establishes the route, while installed relief backpressure and capacity remain unqualified.
- **Copper exit seals.** After the final bends are formed, close each annulus with a burnished 3M 425 foil-tape collar bonded to the clean shell and copper. Use two overlapping pieces, with at most two foil layers on the casing face so the collar stays inside its 0.30 mm foil allowance. Press the collar continuously around the copper; the closed collar contains the body pour and seals this dry insulation boundary. Keep the copper mouths and insert pockets open. Inspect the collars after refrigeration integration and replace any heat-damaged tape before the enclosure closes.

All fitting-size transitions (3/8" → 1/4", larger fittings) happen on the warm side of the shell; every fluid penetration is 1/4" OD tubing.

### 6. Body foam pour

The passive tube passages are Ø[7.5 mm](TUBE_HOLE_D), leaving 0.5 mm radial
air around the measured 6.5 mm tube. Before pouring, mask the gaps around
the installed tubes at the outer exits with removable tape on the dry side. Keep tube mouths, collets and reed channels
open. The faucet and organizer keep their separately specified gripping fits.

The three potted tubes and shared seven-core sensor/earth loom rise out of the
foam into the top cap's passages at step 7. Hold each one at its conduit's station in the shell
(`cap_conduit_shell_xy` in [`_cold_core_interface.py`](/hardware/printed-parts/cold-core/_cold_core_interface.py))
through the free-rise pour with strips of removable tape across the open top; a line
that drifts off its station does not enter its 7.5 mm passage.

Mix the two-part PU foam 1:1. Pour the liquid directly into the body's open +Z top, all at once. Foam falls into the body and reaches every open cavity in parallel: outer foam gap, corner pockets at ±Z, and the carbonator cavity inside the cylinder. Geometry: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md) "Assembly and foam pour".

The **bag pockets take no foam** — each is occupied by its reservoir at [0.25 mm](RESERVOIR_GAP) clearance on every side and at the top, so the pour has no way in. The two reed channels stay open through the pour and receive their columns after cure.

After cure, remove the temporary passage masks and trim external foam flush. Keep the tubes and relief discharge path open.

The pour encapsulates both temperature probes and their leads against the cold metal. Ensure the pour fully wets around each probe and up its lead entry without a connected air void. Such a void lets cabinet moisture reach a cold surface directly. Closed-cell foam resists moisture but is not automatically a vapor barrier or probe-waterproofing qualification: water vapor can also permeate the material. Seal the dry casing joints as specified below; the [seam moisture review](/hardware/printed-parts/cold-core/foam-shell/README.md#why-the-operating-cores-seams-are-sealed) explains their role and the scope of the local foil bands.

### 7. Final assembly

With all three pours cured:

- Drop the pre-soldered reed columns into the still-open reed channels, one per ±X side, from above, each column's 5P ribbon standing free above its channel. **This is done before the cap goes on**, and nothing about it is potted
- Lay reservoir B's five conductors into the shell's 8 mm-wide, 6 mm-deep rim notch, the top of its reed channel opened through the fore face. They turn out of the dry reed channel below the cap floor, its four signals and continuous common together. Keep them clear of the cap's bearing faces.
- Thread the top cap (foam-filled, trimmed from step 3) over the remaining lines before seating it. Hold it above the body **rotated 180° about Z**, in its labeled installed orientation, and feed each line up its own cap passage from the preserved lower entry to its upper guide: the water-inlet, carbonated-water and CO2 tubes, the seven-core sensor/earth loom, and reservoir A's reed ribbon, which rises straight to [reed-cable-a (134.5, 32.5)](REED_CONDUIT_XY) in the shell's frame. The water and soda tubes, A-fill and both draws pass through straight cap guides. Lower the cap, drawing each line through; guide the cap-carried B-fill tube into reservoir B's TPU fill grip while its V-I end stays free. Seat it on its dry printed-face allowance, carrying its equipment columns and the V-B socket wall into their installed positions. Dress A's ribbon above the lid before turning toward its electrical terminals. The B ribbon runs forward out of the rim, rises outside the B-fill block and turns aft above the board. Dress its four signals to J7 and its common to the existing reservoir-B common WAGO, retaining service slack. The screw pattern is 180°-symmetric; use the labeled cap orientation. [10](CAP_FACE_SCREWS) M3 × 25 SHCS through the cap's screw positions and into the top-face inserts
- Bottom cap (mouth-down) onto the body's underside with its dry printed-face allowance, [10](CAP_FACE_SCREWS) M3 × 25 SHCS into the bottom-face inserts
- Seal the dry exterior cap/shell and cap/lid seams with 3M 425 foil tape per [Dry casing seams](/hardware/printed-parts/cold-core/foam-shell/README.md#dry-casing-seams). Use one band per assembled end on its plain smooth perimeter, within the 0.30 mm per-face envelope allowance, with at most two foil layers at the 25 mm end overlap. The band spans the head pockets' small side openings. At the top end, the aft Reservoir A seat's outboard block (world X90.2–97.7, Y299–309) stands past the lid's east face from the lid's underside, the lid/cup seam plane: wrap the band around the block's underside and sides over those 10 mm. Burnish around the corners and keep the axial driver openings, flat bearing faces, mounting seats and fluid passages clear. The cup provides 0.15 mm static room at each rigid seat; the foil is outside the mechanical stack.

- Close the warm side: once every line and cable is in place, press a 3M 425 foil collar from each tube or cable onto its casing face round the annulus, including B-fill's fore-facing entry, both copper exits and B's conductors at the rim notch. Seal them into the top perimeter band. Lay a foil patch over each cap-screw head pocket and the three recessed B-fill clamp screws and over any cap foam left showing. Burnish each collar onto the tube or cable as well as the casing.

The bands restrict cabinet-air entry at the perimeter joints and the collars and patches at every other way in, for refrigerated operation. Together they are the cold core's warm-side moisture boundary; their effect on condensation inside the core is unmeasured. The [complete enclosure readiness assessment](/hardware/printed-parts/enclosure/print-readiness.md#remaining-work-for-the-complete-working-appliance) carries the closure.

## Warm-side check valves

The water and CO2 lines each carry a warm-side check outside the shell.

- **Water-side check:** one [neoFit ACVUS44 stem check](/hardware/reference/neofit-acvus44-check/README.md) inserts into the pump discharge elbow after its clamped PVC joint and reducer. Its outlet feeds the continuous white tube through the west cap guide to the carbonator inlet.
- **CO2-side check:** one ACVUS44 stem check inserts directly into the PISCO outlet, with flow toward the carbonator. The continuous red tube bends into its cap guide. The [production arrangement](/hardware/manifold-layout/above-core.md) defines both fittings and their receiving depths.

## Output condition

A finished cold core:

- The body foam pour cured, flush-trimmed at visible surfaces and tube exits
- Each cap's pour and vent openings trimmed flush, with no foam bloom past the shell or lid surface
- Carbonator with qualified top water-inlet jet and plain bottom CO2 opening; identical plate pattern and four port stations retained
- Carbonator + bonded coil installed, seated in the cylinder cavity, surrounded by foam; coil stubs protruding through the foam-shell's copper exits — [200 mm](PROT_INLET) at the inlet, [175 mm](PROT_OUTLET) at the outlet
- Both temperature probes potted in the foam against their metal surfaces — DS18B20 (carbonator-wall, 0x28) on the carbonator OD, DS18S20 (coil, 0x10) at the suction end of the coil — leads routed through the shared top-cap sensor conduit and sealed, joining SIG-1 at the cold-core exit
- Both carbonator reeds in the reed-bridge on the carbonator wall at the register azimuth (`CLO` water target [67.1 mm](LOW_LEVEL), `CHI` water target [95.25 mm](HIGH_LEVEL); reed centres require the float offset and directional switching calibration), under the foil, their leads transferred over the open head before foaming and carried through the shared straight west riser to J7
- Both reservoirs seated in their bag pockets
- The carbonator's three cap conduits carrying their lines, and the four reservoir conduits open for theirs; water and flavor fill above the liquid, and each draw leaves from its lowest point
- The carbonated-water outlet crossing the carbonator support ring at the ring's own 217° slot and the CO2 at the 307° slot, with all four bearing segments whole
- Reservoir reed columns dropped into their dry channels; A's ribbon rises through its aligned cap passage, while B's ribbon leaves through the shell-rim notch and stays outside the B-fill block
- Both foam caps secured at their dry seats, [10](CAP_FACE_SCREWS) M3 × 25 SHCS each into the top- and bottom-face heat-set inserts, every head down in its lid counterbore — run a straightedge across each lid, nothing touches it before the plate does
- External envelope ~[282.4 mm](SHELL_OUTER_X) × [180.4](CCORE_OUTER_Y) × [253.4 mm](CCORE_CAPPED_H) with both caps on — the shell alone is [213.4 mm](OUTER_H) tall, and the complete envelope includes both cups and lids

## Open items

1. **Carbonator reed placement.** The [bridge](/hardware/printed-parts/cold-core/reed-bridge/README.md) provides through-pockets to bare steel, coil ramps and a rim-referenced setting gauge. Current pocket centers are provisional; finished-float liquid immersion and directional switching calibration set the final operating heights. The 4 mm upper-register stop holds the float below the inlet jet. Rod/drilling XY datums are specified in [installation.md](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md).
2. **Foam data-sheet spec (mix proportions, pot life, cure time, pour temperature window).**
3. **Trim method after foam cure.**
4. **Reservoir final-qualification status.** Pending water + syrup-dwell pass.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_cold_core_sync.py`
