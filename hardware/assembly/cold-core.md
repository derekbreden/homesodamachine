# Cold Core Assembly

The procedure for assembling the cold core — the back-of-enclosure subsystem that contains the carbonator, its wound evaporator coil, two flavor reservoirs, and the surrounding pour-in-place polyurethane foam, all held together inside a 3D-printed PET-GF shell stack.

Foam-pour geometry, shell architecture, copper feed-throughs, and dry casing seam seals: [`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md).

## Scope

In: one hydro-tested + passivated carbonator (output of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md)), with the water-inlet jet fit and full root fusion qualified and recorded per [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md); GOORY 1/4" OD × 0.031" wall ACR copper tubing for the evaporator coil; 3M 425 aluminum foil tape; the printed coil-winding mandrel; the printed shell stack (foam-shell, top lid, open-topped bottom cap and B-fill bend holder — all PET-GF; reservoir × 2 — PETG); reservoir TPU gaskets × 2; pour-in-place 2 lb closed-cell polyurethane foam (two-part 1:1); M5 × 100 SHCS × 20 and RX-M5×9.5 inserts × 20 for the casing closures, plus four RX-M3×5.7 PCB inserts.

Out: a fully foam-poured cold core, capped with exterior foil-sealed dry joints, with the wound evaporator coil bonded around the carbonator and its inlet/outlet stubs protruding through the foam-shell's copper exits — of inlet stub, of outlet stub, measured from the shell face.

The closed, insulated output is **HSM-0557**. Populating its equipment lid
with the pump, controller, V-B and junctions completes the **HSM-0003 cold
core**, the input to **HSM-0552 refrigeration assembly**. Tubes and conductors
remain free for their later enclosure connections.

Not in scope: refrigerant-loop integration ([`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md)) — brazing of the coil stubs onto the donor unit's cap tube and suction line, vacuum, charge, run-up. Also not in scope: enclosure-side power distribution, compressor and condenser mounting, AC wiring, faucet installation and final integration.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 (refrigeration — GOORY copper tubing for the coil) + §6 (cold-core insulation, 3M 425 foil tape + pour-in-place foam + foam-pour consumables) + §13 (mechanical attach hardware + reservoir-cap vent filter) + §7 (the printed parts themselves, each row on its own stock's $/kg). Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) §6 + §11.

| Item | Source | Status (per purchases.md) |
|---|---|---|
| Carbonator | Output of [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) | Hydro-tested + passivated |
| GOORY 1/4" OD × 0.031" wall ACR copper tubing | B0DKSW5VL9 | ~ per carbonator for coil wrap + tie-in stubs ( of 50 ft roll per build) — ACQUIRED |
| 3M 425 aluminum foil tape | B07BTW7C2N | Coil-to-carbonator thermal interface and dry casing-seal bands; about 21.1 ft per build — ACQUIRED |
| DS18B20 TO-92 (carbonator, family 0x28) + DS18S20 TO-92 (coil, family 0x10) 1-wire sensors | B0FKG3HT9Q / DigiKey DS18S20+-ND | Two bare TO-92 temperature sensors, leads heat-shrunk; potted into the foam against their metal surfaces. Distinct 1-wire family codes let firmware tell them apart deterministically (no per-unit ID map) — see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §5 — ACQUIRED |
| MDSR-7-10-15 reed switch × 2 (carbonator level) | Littelfuse / Mouser 934-MDSR-710-15 | Mounted on the carbonator wall under the foil at the register azimuth; same stock as the reservoirs' eight ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)) — ACQUIRED |
| Carbonator reed bridge (printed PETG) | [`/hardware/printed-parts/cold-core/reed-bridge/`](/hardware/printed-parts/cold-core/reed-bridge/) | Print, 1 per carbonator — holds both reeds on the wall and carries the coil over them |
| Reed-bridge setting gauge (printed PETG) | Same | Print, reusable across builds like the coil mandrel — hangs on the tube's bottom rim, marks the bridge height |
| Coil-winding mandrel (printed PETG) | [`/hardware/printed-parts/cold-core/coil-mandrel/`](/hardware/printed-parts/cold-core/coil-mandrel/) | Print, reusable across builds |
| Foam-shell (printed PET-GF) | [`/hardware/printed-parts/cold-core/foam-shell/`](/hardware/printed-parts/cold-core/foam-shell/) | Print, Bambu H2C, 0.4 mm hardened Standard-flow nozzle on the left hotend — slice the `.stl`, not the `.step` |
| Top lid, bottom cap and B-fill bend holder (printed PET-GF) | Same | Print from their `.stl` files; the bottom cap has an open top and a flat bed face |
| Reservoir TPU gasket × 2 (printed) | [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/) | Print; one wet lid seal per reservoir |
| Flavor reservoir × 2 (printed) | [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/) | Print, Bambu PETG Translucent Clear (32101) — the wall reads fill state; the wetted surface is qualified by [`wetted-surface-test.md`](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md), not by the spool |
| M5 × 100 mm SHCS, 12.9 alloy, black oxide × 20 | SVLING B0GHNNYVDH | Same stock as the enclosure seam screws; see purchases.md |
| M3 × 12 mm SHCS, 304 stainless (18-8) × 12 (reservoir-cap screws) | BNUOK B0DJQGMQZM | ACQUIRED |
| M3 × 8 mm SHCS × 4 (PCB screws) | BNUOK B0DJQGPRPV | ACQUIRED |
| RX-M5×9.5 inserts × 20; RX-M3×5.7 inserts × 16 | Casing closures: 20 M5. PCB: four full-length M3. Reservoir caps: twelve full-length M3 | Check the insert family before pressing; each has its own pilot |
| Pour-in-place 2 lb 2-part closed-cell PU foam, 1 qt kit | Fiberglass Supply Depot B08R7TX8QJ | ACQUIRED |
| Foam-pour consumables (mixing cups × 4, stir sticks × 4, nitrile gloves × 1 pair per build) | B08JHH1DBF / B09H6ZP447 / B0G8SSMVKW | ACQUIRED |

## Procedure

### 1. Dress the carbonator wall, then wind the evaporator coil

This operation takes the **HSM-0004 carbonator** and produces the
**HSM-0554 instrumented carbonator and coil assembly**. The vessel, bonded
coil, attached probes and reeds, and earth lead move together into the casing;
support their loose tails and conductors during that move.

Everything that has to touch bare 316L goes on **before** the foil, at the bench, with the carbonator in the open:

- The **carbonator earth lead**, green 16 AWG, with its steel-side closed ring clamped to the existing upper vessel rim per [the metal attachment procedure](/hardware/assembly/pressure-vessel.md#upper-rim-earth-bond). Point the crimp barrel upward and dress the lead toward the shared west-side seven-core sensor passage. Keep the lid-side end unterminated for threading through the lid. Check steel-to-free-wire continuity before the connection is covered; the lid-side ferrule is crimped after final threading and dressing at step 7.
- The **DS18B20 carbonator-wall probe** (bare TO-92, family 0x28, leads heat-shrunk) taped flat against the carbonator OD, in the bare band below the wind so no wrap has to climb over it. This is the compressor-cycling setpoint sensor, so it reads the carbonator wall, not the coil.
- The **two carbonator MDSR-7-10-15 reeds**, vertical on bare steel in the printed [reed bridge](/hardware/printed-parts/cold-core/reed-bridge/README.md), on the rod-register azimuth. The provisional bridge bottom is above the bottom tube rim, with pocket centers (`CLO`) and (`CHI`). Water targets remain and. [Calibrate finished-float immersion and directional crossings](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration) before fixing the final bridge, foil and coil. The 14 mm mounting envelope crosses the space between copper wraps, so the bridge carries the crossing.

Both go under the foil skin. The bridge's through-pockets put the reeds against bare steel at the specified radial datum. The [RC62 bench reach and installed calibration scope](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md#running-room-and-magnetic-path) apply to this float; foil and coil placement must preserve the measured switching positions. After step 5 the carbonator wall is at the bottom of a 14.62 mm-wide, full-height annulus, so install and prove the sensors before the pour.

Wind GOORY 1/4" OD × 0.031" wall ACR copper tubing as a single-layer helical coil around the carbonator OD — of wrap per carbonator as it lies on the carbonator, plus one tie-in allowance per end: at the inlet, at the outlet. **The two are not the same length, and neither is spare copper.** Each is that tail's own run — off the helix, down its lane, out through the shell wall — plus the length that protrudes past the shell for the brazier to work with; the outlet's in-shell run is the longer of the two, its protrusion the shorter. The tie-in stubs exit through the foam-shell's copper holes; brazing happens in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md).

Bond the coil to the carbonator OD with 3M 425 aluminum foil tape applied as a continuous skin between carbonator and coil.

Before closing the foil skin over the coil's outlet (high) end — the suction side, refrigerant leaving as low-pressure gas, the coldest metal — tuck the **DS18S20 coil probe** (bare TO-92, family 0x10, leads heat-shrunk) flat against the copper and tape it down under the foil. This is the freeze-protect sensor; thermally bonding it to the suction-end copper is what lets the −8 °C cutoff see the coldest point. Distinct 1-wire family codes let firmware tell it and the carbonator probe apart deterministically, with no per-unit ID map.

Rough-form with the printed [coil mandrel](/hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.rs),
a hollow PETG drum of OD. Set the finished winding on the
foil-taped vessel: right-hand turns over
, pitch. Feed material from the long
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

### 2. Press the casing and PCB inserts

Press ten RX-M5×9.5 inserts into each face of the taller shell. Each Ø6.4 × 10.5 mm
pilot has 2.6 mm radial host stock. The blind Ø5.2 passages beyond the pilots keep
foam off the long screw tails. Press the brass squarely until its mouth is flush.

Press four RX-M3×5.7 inserts into the top lid's Ø4 × 7.4 mm PCB pilots. Their
posts stand 3.6 mm above the equipment face and retain 3.6 mm backing below the
blind bores. The PCB takes M3 × 8 screws. Its posts belong to the lid.

### 3. Attach and fill the bottom cap

The bottom cap is one open-topped printed part with a 2 mm floor and a
 central foam depth. There is no ceiling in it: the shell's
fixed floor forms the cavity's upper boundary. Its four Ø
pour holes form a 2 × 2 pattern. Two Ø holes vent air.

Bolt the cap directly to the empty shell with ten M5 × 100 screws. Every head
seats below the flat underside. Mask the dry perimeter and outward-open head
pockets with removable tape. Invert the empty shell onto its open upper rim;
keep the equipment lid and vessels off during this operation.

Distribute the measured foam charge among the four local pour points. Work
within the foam manufacturer's mixing and working-time instructions, placing
each portion near the quarter it must fill. Use the measured charge and its
distribution as the fill basis; foam appearing at a small vent is not a fill
indicator. Let it cure, trim the ports flush and apply the exterior foil patches
and perimeter band. Return the casing upright after cure. The bottom cap stays bolted on during the body assembly.

The top side is filled through the shell's open mouth at step 6. The uniform
 equipment lid prints on its flat underside. Its pump,
V-B wall, junction wells, PCB posts and retainers build above that face. Keep the
lid off until the body pour is cured and its foam is trimmed to the lid seat.

Prepare the top-lid equipment with the lid off. The bare pump uses the integral
half-pipe saddle and its separate upper snap cap. Follow the current
[pump installation](../reference/g-ganen-pump/installation/README.md) for removing
the rubber feet and legs, seating the motor and closing its snap. V-B and the four
junction wells travel with the lid; thread B-fill through its separate bend holder
at step 6.

### 4. Reservoir subassembly (both, at the bench)

The closed units are **HSM-0555 fitted reservoir A** and **HSM-0556 fitted
reservoir B**. Each carries its cap, gasket, captive float and guide, grips and
closure hardware. Continuous tubes are fitted during body-side installation;
the dry reed columns enter after the foam cure.

Both flavor reservoirs are built closed here, off the shell, and go into their pockets as finished units at step 5. Nothing in this step touches the foam shell. The geometry — rod length, float travel, reed heights, cap register, vent stack — is owned by [`reservoir.rs`](/hardware/printed-parts/cold-core/reservoir/reservoir.rs), [`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) and [`reservoir/vent.md`](/hardware/printed-parts/cold-core/reservoir/vent.md); this step is the order the bench builds in.

**Reed columns — two, one per reservoir.** Each reservoir's level gauge is four MDSR-7-10-15 reeds standing outside the syrup, on the side the pocket's reed channel runs up. Calibrate their liquid crossings per the [float installation procedure](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration), then solder all four onto a single 5-conductor 22 AWG spine — four signal lines plus one shared common — running the column's full length, reed 1 lowest. Lace it with heat-shrink between reeds so the column drops into its channel as one stiff piece. Prove every reed with the printed RC62 float **before** lacing — closed with the magnet alongside, open with it away; a reed that fails after lacing costs the whole column. The columns are not installed here: the channels stay open through the body pour and take their columns at step 7.

The prepared columns are **HSM-0348 J6** and **HSM-0349 J7**. Each includes
its attached reservoir reeds. J7's carbonator reeds travel with **HSM-0554**;
the column's carbonator branch stays free for connection. Leave board ends
free for lid threading, then complete the board housings and shared common
during core closure.

**Float and guide.** Use the one-piece 36 × 28 mm ASA Aero float with a midplane RC62 and 4.8 mm bore. Reservoir rods stand 20 mm from the wet far wall, at (±106.25, 32.5) mm. The cap register and body boss share that axis. Check free travel and calibrate liquid switching before fixing reed heights; [current datums and procedure](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md).

**Prepare the cap.** Fit two liquid-tube TPU spools and one air-tube spool into
the lid's matching 45° seats; both ends sit flush with the 4 mm plate.
The cap with its captured grips forms **HSM-0568 reservoir cap assembly A** or
**HSM-0569 reservoir cap assembly B**. It moves onto the body over the guide.
The perimeter gasket, body inserts and screws complete the reservoir closure.

**Close the reservoir.** Press six ruthex M3 full-length inserts into the wall-top
bosses, in the 7 mm pockets. Lay the perimeter TPU gasket on the body rim,
lower the prepared cap over the rod and drive six M3 × 12 SHCS into the inserts. The rod remains short of its
seat-to-seat span so it cannot hold the lid off the gasket.

The closed reservoir has a freely sliding float, a clamped rim gasket, two
captured liquid-tube grips and a flush air-tube grommet. Nothing
pierces the body below the cap. Print four liquid-tube spools and two air-tube
spools in Bambu TPU 90A per machine.

### 5. Body-side install

With the outer shell open-top-up on the bench, install every internal component:

- **Carbonator + coil.** Leave both long tails free for feeding, with straight, deburred ends. Lower the carbonator partway into the center cavity with its coil clocked to the two lanes. Feed each bare tail through its Ø7.5 mm shell hole from inside, then lower the carbonator in stages while drawing the tails outward and forming broad curves. Keep the copper approximately normal to the wall through each hole; hold the tube itself while forming it, so the printed wall does not act as the bending tool. Seat the carbonator on the printed-in `carbonator_support_ring` and form the final lane bends. Retain the modeled R15 centerline tail bends and reject a kinked, creased or visibly flattened section. Leave the specified 200 mm inlet and 175 mm outlet working lengths outside the shell for refrigeration integration. Its two bottom-plate push-fit elbows are already made up and aimed (below); they hang inboard of the ring and descend in open space as the carbonator seats, so no shell material is in their way
- **Sensor leads** — the two temperature probes and two carbonator reeds are bonded to their specified metal surfaces before the carbonator descends into the shell. Keep the reeds at their fixed east-side positions. Feed the three-wire temperature bus at the coil probe first, continuing to the carbonator-wall probe. Turn the coil-side feed aft below the PRV vent at world Z184, then rise at Y347. Transfer CLO, CHI and their common over the open vessel head at world Z225/Y352 to the west side. Bring these six signal conductors and the green 16 AWG carbonator earth lead together at world X−48/Y347. Their shared Ø7.5 mm `sensor-cable` guide bends at R5.5 inside the upper shell to the lid mouth at world X−78/Y320/Z253.4. Lay the internal transitions while the body is open, before the pour. Seat the leads so foam closes around them, and keep the free ends ready for threading through the lid. The temperature bus joins J4 and its sensor-common WAGO; the reed leads join J7 and its existing reed-common WAGO. The reservoir reed channels carry only their own five-conductor columns.
- **Reservoirs** seated into the two ±X bag pockets
- **Earth termination.** Thread the free earth-wire end through the lid; its ferrule for the rear PE WAGO goes on outside the lid after dressing, so it never passes through the cable bore. With the lid still loose on the loom and the steel accessible, repeat and record steel-to-free-end continuity before the body pour.
- **Penetrations.** Fluid lines cross the upper casing boundary: straight risers pass through the equipment lid and B-fill enters laterally at the fore-facing opening. The shell's −X face is mated against the refrigeration base — the condenser flush on it, the compressor's plate just short of that plane — so a bore struck there would open into that base rather than into the machine. What crosses that face is the **two copper evaporator lines, each through its own round hole**. Reservoir A's reed ribbon and the shared seven-core sensor/earth loom use two lid passages. Reservoir B's ribbon leaves through the fore side window.

  **The carbonator and both reservoirs fill high and draw low.** Their water or flavor fill enters above the liquid and their draw leaves at the lowest point. That is what the air-purge and clean-flush service modes in [`fluid-topology.md`](/hardware/topology/fluid-topology.md) run on.

  - Water inlet → the equipment lid's plain `water-in` guide. The carbonator's top-plate Port 2 carries the TAISHER 316L SS elbow and JG PP010822E 1/4-inch PTC × 1/4-inch NPT male adapter in their fixed clocking. One continuous white 1/4-inch LLDPE tube leaves that adapter, turns upward at nominal R14 clear of the PRV and passes straight through world (−82.5, 420, 253.4) mm. Above the guide, an R14 approach reaches the pump discharge/check assembly; the guide adds no fitting, insertion or physical cut. Lay this route before the pour. The [water-inlet jet](/hardware/assembly/water-inlet-jet.md) is welded onto the metal elbow's downward male tip, after the 90° turn, and discharges into headspace above the water line. Confirm its qualified assembly record and outlet clearance before the pour. Use the combined internal/warm path and actual receiving-end marks per [Internal plumbing](internal-plumbing.md#parts-and-cut-lengths); the CAD span split at the lid does not create separate tube blanks.
  - CO2 inlet → the equipment lid's `co2-in` conduit. **The lane end is fed from above:** the line falls the shell's whole height down the port lane, runs along the lane's floor, and leans in across the shell's floor through **one of the carbonator support ring's own slots** — the 307° one — to the bottom plate's lane-side port at y=, passing outboard of reservoir A's pocket corner. The carbonator's bottom-plate neoFit AME4-N2-E push-fit male elbow is made up at the bench, aimed along this line, and hangs inboard of the ring; the tube bottoms in its socket, so **nothing is made up in the cavity**. Lay it down the lane before the lid goes on — it is not pushed in from outside — and tug-test it before the pour, because it is the one joint the foam puts out of reach. Inside the carbonator Port 1 is a plain opening below the liquid. Gas flows only while its supply pressure exceeds local carbonator pressure, then rises toward the headspace; there is no internal barb, silicone hose or stone.
  - Carbonated-water outlet → the equipment lid's `carb-water-out` conduit, and the carbonator's own drain. **It has no bore in this shell at all.** The bottom-plate Port 3 push-fit elbow takes the blue tube in its own socket and turns the line laterally under the carbonator, and it leaves the carbonator support ring through **one of the ring's own slots** — the 217° one, which already exists to let the pour reach the under-carbonator floor and which lies on the route to this lid passage. The CO2's lean crosses at the 307° slot, one each. So neither crossing costs a bore and all four bearing segments stay whole. From there the 1/4" OD LLDPE climbs beside the coil, in the middle of the annulus between the coil and reservoir B's pocket wall and inboard of the port lane because the CO2 owns the lane's own strip at the bottom of the shell, turns above the tank at world Z219.4 while the main body is open, and rises straight through the upper shell and lid at world (77.5, 359.51, 253.4) mm. The same uncut tube continues above the guide through its accepted R14 printed bend holder directly into the meter inlet. The guide adds no insertion, joint or physical cut. Lay it before the pour: it is potted the whole way up
  - Reservoir draws → install both continuous black 1/4" OD LLDPE dip tubes through their reservoir-cap grips before the body pour. Each runs from its draw valve, through the equipment lid's `reservoir-a` or `reservoir-b` opening and its reservoir grip, to the reservoir floor, with its lower end cut at 45° ([floor and dip tube](/hardware/printed-parts/cold-core/reservoir/floor-and-dip-tube.md)). Temporarily locate the exposed upper ends on their lid-hole axes while pouring. Foam surrounds only the short dry spans above the closed reservoir caps; the dip sections inside the reservoirs remain free.
  - Reservoir fills → install the fill tubes before the body pour. A-fill has an aligned lid opening and reservoir seat at shell (102.5, −61) mm. At step 6, thread B-fill through its separate R14 holder, place its horizontal run on the fore-facing entry axis and seat its lower end in reservoir B's flush TPU fill grip. Its tip finishes at world Z228.15, 1 mm below the plate in the **headspace**. Both liquid entries use the flush TPU grips.
  - Reservoir air → two straight white 4 mm OD / 2.5 mm ID tubes, nominally 31.25 mm each. Install each in its reservoir's air grip before the body pour and locate its upper end on its lid-hole axis, leaving 6 mm above the equipment lid. Its lower tip stands 1 mm below the reservoir plate, open to the headspace. Keep both ends open; [air-tube installation](/hardware/printed-parts/cold-core/reservoir/vent.md).
  - Reed cables → each column drops into its dry channel from the raised shell rim before the equipment lid is fitted. Reservoir A's leads rise through the aligned lid opening; Reservoir B's leads leave through the fore side window below the rim. Keep both channels masked and clear through the pour ([`reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)).
  - Refrigerant inlet and outlet → two Ø7.5 mm holes in the −X outer wall at native Y ±77.5 mm, Z 28.425 mm. The inlet takes the port lane and the outlet the west lane. Feed the tails during the carbonator descent described above, before installing the reservoirs and the other potted routes.
- **PRV vent LLDPE** pushes into the barrel bore of the [`prv-shroud`](/hardware/printed-parts/cold-core/prv-shroud/) subassembly on Port 4. The short tube falls from the downward barrel bore, turns once and crosses the shell's **+Y flank** at the station defined by [`_internal_routes.py`](/hardware/printed-parts/cold-core/_internal_routes.py). Cut its free mouth flush with the flank so it opens into the enclosure's west-wall relief chase. The chase carries discharge outside the cabinet. Keep the tube and chase clear; geometry establishes the route, while installed relief backpressure and capacity remain unqualified.
- **Copper exit seals.** After the final bends are formed, close each annulus with a burnished 3M 425 foil-tape collar bonded to the clean shell and copper. Use two overlapping pieces, with at most two foil layers on the casing face so the collar stays inside its 0.30 mm foil allowance. Press the collar continuously around the copper; the closed collar contains the body pour and seals this dry insulation boundary. Keep the copper mouths and insert pockets open. Inspect the collars after refrigeration integration and replace any heat-damaged tape before the enclosure closes.

All fitting-size transitions (3/8" → 1/4", larger fittings) happen on the warm side of the shell; every fluid penetration is 1/4" OD tubing.

### 6. Open-body foam pour

Complete and prove the body-side tubing, vessel sensors and protective-earth bond
before potting. Keep both dry reservoir reed channels masked and clear; their
mouths remain accessible at the raised shell rim. Reservoir B's upper leads leave
through the fore side window. The three-dimensional tube routes and vessel
positions are the [cold-core assembly](../cold-core-layout/README.md).

Bridge each closed reservoir cap's perimeter to its surrounding pocket rim with
burnished 3M 425 foil tape. Close the 0.25 mm cap-to-pocket running gap before
pouring so foam stays out of the vessel-pocket clearance and reed sensing windows.
Keep the tube lumens and dry reed-channel entry mouths open.

Thread B-fill through its separate R14 bend holder and seat its end in the reservoir
TPU grip. The guide has a 2 mm wall and no straight outlet leg. Its lower exit
clears the reservoir cap; its horizontal inlet follows the fore-facing tube run.
Keep the source end free for the V-I connection. The holder stays with the tube
and cured foam. It carries no clamp screws.

Mask the gaps around the external tube and copper exits. Temporarily support the
straight risers at their lid-hole axes. Mask the ten upper insert mouths and keep every tube lumen, reed channel and
screw-tail passage clear. The top is open: distribute the measured PU charge
across the cavity instead of feeding it through the lid. Follow the manufacturer's
working-time and cure instructions. Foam closes around the outside of the installed
tubes and the lower B-fill holder.

After cure, trim foam below the Z246 mm appliance lid underside. Keep the printed
Z245.85 mm rim and the ten insert mouths clean. Clear the temporary masks and prove
all tubes and sensing leads before closing the top.

### 7. Close and populate the top lid

Drop the two proved reservoir reed columns into their dry channels. Route A's leads
through its lid opening and B's leads through the fore side window. Feed the exposed
tubes and sensor/earth loom through their lid openings. Lower the lid
in its specified 180° installed orientation, clearing the B-fill holder with its
plain window. The flat equipment face stays at appliance Z253.4 mm. Ten M5 × 100
screws seat in Ø9 recesses and engage the raised shell-face inserts. Tighten these
before the PCB covers any driver path. Apply 3M 425 to the dry exterior perimeter
and guide-window boundary without covering functional tube or vent lumens.

The closed casing, cured insulation, installed sensing columns and supported
free lines form **HSM-0557 insulated cold-core assembly**. It moves together
to equipment population. The pump, controller, V-B and junctions complete
**HSM-0003**, with their installation order below.

Terminate J10 on the loose PCB before fastening it to its four lid posts with
M3 × 8 screws. Fit the pump and V-B plumbing, then dress the connector branches
and tube retainers per [internal plumbing](internal-plumbing.md). Seat the V-A
feed in its C2 clip before dressing the earth and J4 branches across that area.
The reservoir A fill/draw pair retains its two fore C2 clips and aft tied seat.
After final threading and dressing, crimp the carbonator earth lead's ferrule and
land it in the rear PE WAGO before the enclosure is closed.

Check both ten-screw closures, the four foil-covered bottom pour ports and two
vent patches, free tube lumens, and intact reed-channel access. Prove the sensors
and PCB connections before [refrigerant-loop integration](refrigerant-loop.md).


## Warm-side check valves

The water and CO2 lines each carry a warm-side check outside the shell.

- **Water-side check:** one [neoFit ACVUS44 stem check](/hardware/reference/neofit-acvus44-check/README.md) inserts into the pump discharge elbow after its clamped PVC joint and reducer. Its outlet feeds the continuous white tube through the west cap guide to the carbonator inlet.
- **CO2-side check:** one ACVUS44 stem check inserts directly into the PISCO outlet, with flow toward the carbonator. The continuous red tube bends into its cap guide. The [production arrangement](/hardware/manifold-layout/above-core.md) defines both fittings and their receiving depths.

## Output condition

A finished cold core:

- The body foam pour cured, flush-trimmed at visible surfaces and tube exits
- The bottom cap's pour and vent openings trimmed flush, with no foam bloom past the bottom cap's outside face
- Carbonator with qualified top water-inlet jet and plain bottom CO2 opening; identical plate pattern and four port stations retained
- Carbonator + bonded coil installed, seated in the cylinder cavity, surrounded by foam; coil stubs protruding through the foam-shell's copper exits — at the inlet, at the outlet
- Both temperature probes potted in the foam against their metal surfaces — DS18B20 (carbonator-wall, 0x28) on the carbonator OD, DS18S20 (coil, 0x10) at the suction end of the coil — leads routed through the shared equipment-lid sensor conduit and sealed, joining SIG-1 at the cold-core exit
- Both carbonator reeds in the reed-bridge on the carbonator wall at the register azimuth (`CLO` water target, `CHI` water target; reed centres require the float offset and directional switching calibration), under the foil, their leads transferred over the open head before foaming and carried through the shared west passage and lid exit to J7
- Both reservoirs seated in their bag pockets
- The carbonator's three cap conduits carrying their lines, and the four reservoir conduits open for theirs; water and flavor fill above the liquid, and each draw leaves from its lowest point
- The carbonated-water outlet crossing the carbonator support ring at the ring's own 217° slot and the CO2 at the 307° slot, with all four bearing segments whole
- Reservoir reed columns dropped into their dry channels; A's ribbon rises through its aligned cap passage, while B's ribbon leaves through the fore side window and stays clear of the B-fill holder
- Top lid and bottom cap secured at their dry seats, M5 × 100 SHCS each into the top- and bottom-face heat-set inserts, every head recessed below its closure face
- External envelope ~ × × with the top lid and bottom cap installed; the shell rim stands above its own floor

## Open items

1. **Carbonator reed placement.** The [bridge](/hardware/printed-parts/cold-core/reed-bridge/README.md) provides through-pockets to bare steel, coil ramps and a rim-referenced setting gauge. Current pocket centers are provisional; finished-float liquid immersion and directional switching calibration set the final operating heights. The 4 mm upper-register stop holds the float below the inlet jet. Rod/drilling XY datums are specified in [installation.md](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md).
2. **Foam data-sheet spec (mix proportions, pot life, cure time, pour temperature window).**
3. **Trim method after foam cure.**
4. **Reservoir final-qualification status.** Pending water + syrup-dwell pass.
