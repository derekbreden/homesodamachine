# Lillium cutover

The new prototype is connected and serving soda, per Derek's
[October 18 report](/hardware/printed-parts/enclosure/lillium-prototype-2026-10-18/physical-observation.json).
The photographs show a temporary countertop arrangement with exposed pump heads and
external tubing. Fit issues require assembly workarounds; the next milestone is to
resolve those issues and button up this working prototype. The report does not
identify installed revisions or establish complete cutover acceptance.

The intended under-sink build is fed by the Lillium: two flavors, two pumps, the
white faucet, the machine display, and the flow meter that starts each pour. The Lillium makes
the cold carbonated water; this build adds no carbonator, refrigeration, CO2 or tap-water feed.

The flavor manifold carries the eight valves front-top holds, V-C through V-J, and all six
tees. V-A (tap water) belongs to back-top; V-B (funnel) stands on the cold-core cap. This cutover build leaves those integrated-machine subassemblies out.
V-A's tee port takes a plug and V-B's takes a dip tube, so a bottle refills a reservoir through
the firmware's own Fill. When tap water and the funnel come in, V-A goes onto the plugged port
and V-B and the funnel onto the dip-tube line; nothing inside front-top changes. The Lillium's
own filtered tap-water outlet ([plumbing](/docs/plumbing.md#water-supply)) can feed V-A then.

The build follows the machine's own procedures. Each step below names the procedure and says
what this build does differently. The parts list and steps specify that build; the
October 18 observation does not establish completion of individual steps or identify
every part used in the working assembly.

## In and out

**In this build:**
- The four enclosure quadrants, the pump cradle and its clamp, and the tee carrier
  ([prototype record](/hardware/printed-parts/enclosure/lillium-prototype-2026-10-07/README.md),
  [back top](/hardware/printed-parts/drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/README.md)).
- Front-top's manifold: V-C–V-J, Y-A–Y-G, both KPHM600 pumps.
- Both reservoirs in the foam shell, with their caps, gaskets, floats, rods and reed columns.
- The DIGITEN meter; the rear wall's TAP, SODA and two FLAVOR fittings, the C14 inlet and the
  RJ11 keystone.
- The electronics bay's Mean Well IRM-90-12ST, main board, ground stack and five Wago 221-413
  lever nuts.
- The machine display in front-top's facet, and the funnel frame.
- The white Sculpted faucet with its display, and its umbilical.

**Left out:**
- V-A, V-B, V-K and the foam cap and lid.
- The funnel, its cover, its drain elbow and cradle.
- The carbonator, refrigeration loop, compressor, condenser and fan.
- The CO2 path, the ASSE 1022, its vent and the OVER line.
- Both relays and the J5 loom, the temperature probes, the carbonator reeds and the MQ-6.

## Parts

**On hand.** Every part below is in [purchases](/hardware/ledger/purchases.md), by
[BOM](/hardware/ledger/bom.md) section:
- §1: main board, its CR2032, the Waveshare 4.3B and 1.47 displays, the IRM-90-12ST.
- §5: the MXR C14 inlet and the NEMA 5-15P → C13 cord.
- §8: both Kamoer KPHM600; eight of the fourteen Beduan valves; six PP0208E tees; four PP1208E
  bulkheads (TAP, SODA, two FLAVOR); two PureSec draw bulkheads with their silicone wet washers;
  the Siptenk stiffener.
- §9: the Westbrass donor, an SS under-counter plate, the DIGITEN meter, CARGEN foam, black, blue
  and white 1/4" LLDPE, white 3/8" LLDPE, and the 28 AWG umbilical ribbon.
- §11: the 22 AWG 3P, 4P and 5P ribbons and black spool, JST XH kits, female spades, ring
  terminals, ferrules, heat-shrink, braided sleeve, 16 AWG stranded silicone plus solid black/white stock, Wago 221-413, -415 and -420,
  the RJ11 keystone and plugs, and 4", 6" zip ties.
- §12: the RC62 magnets, MDSR-7-10-15 reeds and the 1/8" 316 rod.
- §13: ruthex short and full-length M3 inserts, M3×8, ×10, ×60 and 304 ×12 screws.
  Print the flush TPU tube grips and cut the independent air tubes from existing stock.

**To buy:**
- One John Guest PI0808S 1/4" stem plug for V-A's port
  ([B003NUUKL8](https://www.amazon.com/dp/B003NUUKL8), 10-pack).
- Two John Guest PP0408W 1/4" straight unions, joining the white faucet's flavor runs to the black
  umbilical runs ([B005S4MTXO](https://www.amazon.com/dp/B005S4MTXO), one per listing).
- 16 AWG solid tinned-copper black and white hookup wire for AC-2 and DC-1/4,
  with Prime links in [BOM §11](/hardware/ledger/bom.md#11-wiring--fasteners).

**Printed:**
- **Fit together, per Derek's October 7 report
  ([observation](/hardware/printed-parts/enclosure/lillium-prototype-2026-10-07/physical-observation.json)):**
  front-top, front-bottom, back-bottom, the foam shell, the pump cradle and clamp, the tee carrier
  and the funnel frame.
- **Faucet:** the white Sculpted faucet's shell, display cover and above-counter plate
  (September 18), and its lever (September 20).
- **Machine display cover:** printed September 29.
- **Reservoirs and gaskets:** both reservoir bodies and caps (October 6 and 7). The October 8 TPU
  prints: both reservoir cap gaskets, dry bulkhead washers and vent rings, the machine display
  gasket, the faucet's thimble and its counter gaskets
  ([prototype gaskets](/hardware/printed-parts/prototype-gaskets-2026-10-08/README.md)).
- **Back-top:** the October 10 print
  ([record](/hardware/printed-parts/drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/README.md)),
  whose sliding-groove supports grew up from the plate and stuck in its walls.
- **Printing:** three ASA Aero floats, two of them this build's, with their RC62s going in at the
  print's pause.
- **Not printed:** the rear wall's chips at its current width, for TAP, SODA and both FLAVOR
  fittings, plus the tube collars and the DATA plate
  ([label plates](/hardware/printed-parts/drain-readiness/README.md#identification-plates): White,
  Blue and Black). Each chip sits under its bulkhead's flange, so print them before the rear wall
  goes together. The earlier chips are narrower than this back-top's pockets.
- **Not needed here:** the funnel, its cover and elbow cradle, and the faucet's vent bungs.

## 1. Inserts

Press them per [enclosure mechanical §1](enclosure-mechanical.md#1-stage-the-printed-pieces),
in every piece before anything goes in the box:
- **Short M3:** the C14 tunnel's two; and the electronics-bay bosses for
  the main board (four, recessed by §1's own depth procedure), the PSU (four) and the ground
  stack (one). The eight relay bosses can stay empty.
- **Full-length M3:** the lower pump cradle's two, under the clamp's M3×60s; and six in each
  reservoir's wall-top bosses.
- **M5:** four Y-seam inserts, two in back-bottom's knuckles under the Z seam and two in front-top's knuckles under the funnel frame.
- **The faucet:** the three short M3 in the shell base
  ([faucet assembly](/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md#base-joint)).

The condenser's two M3 and the compressor's four M5 are not pressed.

## 2. Front-top on the bench

Front-top is the fixture for the whole flavor side.

1. **The manifold** per
   [internal plumbing §3](internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps),
   whose steps 1–4 seat the machine's four pump tees in front-top's tee wall. This build's
   dock is the tee carrier with Y-C, Y-D, Y-F and Y-G
   ([tee carrier](/hardware/printed-parts/enclosure/tee-carrier/README.md#assembly)); the aft
   valves V-C, V-D, V-G and V-J and their window covers; the fore valves V-E, V-F, V-H and V-I
   with the four bowed stubs; Y-A and Y-B butted to V-C and V-D, with the crossbar between them;
   the four hairpins.
2. **Y-A port 1**, V-A's: the PI0808S plug. **Y-B port 1**, V-B's: the dip tube, black 1/4"
   LLDPE, left long.
3. **The machine display** in its facet: TPU ring on the glass, both cover wings in their
   pockets, leads loose (§8).
4. **The funnel frame** remains off until the box's final connections are complete.
   Bring the prototype dip tube through its drain opening, then lower the frame vertically
   and fit its four M3 × 12 screws. The tube reaches the bottom of a bottle beside the
   machine; between fills its end rests up in the opening. The integrated drain
   cradle, elbow and stub are omitted for this prototype dip-tube arrangement.

Cuts, black 1/4" LLDPE:

| Run | Joins | Cut |
|---|---|---|
| fluid-6, 7, 8 | the Y-A–Y-B crossbar; Y-A → V-C; Y-B → V-D | butts: both insertion depths, no exposed tube |
| fluid-9, 19 | V-C → Y-C; V-D → Y-F | the inner hairpin ([the lower returns](/hardware/manifold-layout/README.md#the-lower-returns)) |
| fluid-17, 27 | Y-D → V-G; Y-G → V-J | the outer hairpin (the same) |
| fluid-10, 13, 20, 23 | the four bowed stubs | fit at the bench (§3 step 2) |
| dip tube | Y-B port 1 → bottle | at the bench |

## 3. Back-top on the bench

Populate it inverted, ceiling down
([enclosure mechanical §1–§2, §5](enclosure-mechanical.md#2-seat-the-y-walls-seven-connection-bodies)).

1. **The rear wall:** the four PP1208E bulkheads (TAP, SODA, both FLAVOR) with their chips; the
   C14 from inside, two M3×8 into the tunnel; the RJ11 keystone. The CO2 and OVER openings stay
   empty.
2. **The meter** in its two roof anchors, one 6" zip tie each, arrow toward SODA
   ([internal plumbing §4](internal-plumbing.md#4-rear-beverage-connections)).
3. **The soda runs**, blue 1/4" LLDPE. TAP's inboard collet → the meter's inlet is the one run
   with no model: TAP stands west of SODA on the top row and the meter hangs by SODA's column,
   so cut it on the parts, across the empty water deck, bends no tighter than R14, clear of the
   electronics bay. The meter's outlet → SODA is `carb-2`, its developed length in
   [the assembly facts](/hardware/manifold-layout/enclosure-assembly.facts.json). Sleeve both in
   CARGEN: the line is cold and the cabinet is not.
4. **The electronics bay** ([electronics bay](electronics-bay.md)). The five Wago 221-413 lever nuts
   press into their wall wells, labeled H, N, G, +, GND. Then bolt up the bodies: the
   IRM-90-12ST on its four bosses after preforming and landing its unpowered solid-wire pigtails, the main board on its four (ESD-safe), and the ground stack
   under its M3×10.
5. **Mains and 12 V:**

   | Run | From → to | Termination |
   |---|---|---|
   | AC-1 | C14 tabs → the H, N, G Wagos | 16 AWG solid black/white/green, soldered at the C14 ([wiring §2](wiring.md#2-ac-mains-c14--distribution--relay-1--compressor--psu)); stripped directly in the Wagos |
   | AC-2 | the H and N WAGOs → PSU L and N | 16 AWG solid black/white, stripped directly in both clamps; the PSU has no earth terminal |
   | G leg | the G Wago → the ground stack | ferrule; ring at the stack |
   | DC-1 | PSU + and − → the + and GND WAGOs | 16 AWG solid black, stripped directly in both clamps |
   | DC-4 | the + and GND WAGOs → J10 | 16 AWG solid black, stripped directly in both clamps; `V12` and `GND` each in the clamp beside its silk label |

   AC-3 to AC-6 (the compressor's), DC-2 and DC-3 (the water pump's) and the J5 loom are not built.
   Run [electronics bay §7](electronics-bay.md#7-pre-power-continuity--isolation-check)'s
   continuity checks: no H–N, H–G or N–G continuity, J10's `V12` to PSU +, the stack to the C14
   earth pin.

## 4. The pump cradle

Build it upright on the bench and keep it out of the box until the box is closed
([internal plumbing §3](internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps)):
- Both KPHM600s go into the cradle wells, under the clamp and its two M3×60.
- Pull Kamoer's barbed connectors and push 1/4" LLDPE into both silicone ends under the loosened
  pump-head housing, then tighten the housing; it clamps the tube (§3 step 5). Set the free tips
  as §3 gives.

## 5. The reservoirs

Build both closed before they go into the shell ([cold core §4](cold-core.md#4-reservoir-subassembly-both-at-the-bench)):

1. **The draw:** a PureSec bulkhead up through the trough floor, silicone wet washer above, TPU
   dry washer below, the elbow clocked to its own pocket wall (A at −Y, B at +Y), the nut
   hand-tight from inside ([floor and bulkhead as printed](https://github.com/derekbreden/homesodamachine/blob/20e19fc573/hardware/printed-parts/cold-core/reservoir/floor-and-bulkhead.md)).
2. **The float:** cut each 1/8" rod ([handwork](handwork.md#cut--seat-the-reservoir-float-rods)),
   seat it in the body boss, the float over it.
3. **The reeds:** run the
   [reed calibration](/hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md#reed-calibration)
   with the real float, in water and in the actual syrup, before soldering. Then solder each
   column's four reeds onto its 5P ribbon, lace it with heat-shrink and prove every reed with
   the float.
4. **Close:** the flush liquid/air TPU spools in their double countersinks, the TPU gasket on the
   wall top, the cap over the rod, six 304 M3×12.
5. **Water test now:** fill each with water and leave them a few hours over a towel. The current
   reservoir recipe's water results are in the
   [reservoir record](/hardware/printed-parts/cold-core/reservoir/README.md).

## 6. Close the box

Dry-fit every slide with the box empty first
([enclosure mechanical §1](enclosure-mechanical.md#1-stage-the-printed-pieces)), then close it in
the order [§4](enclosure-mechanical.md#4-close-the-front-column) and
[§6](enclosure-mechanical.md#6-close-the-box) give.

1. **The front column:** front-top, carrying its manifold and display, slides aft onto
   front-bottom. The compressor bay stays empty.
2. **The foam shell:** both reservoirs in their pockets, the reed columns down their channels,
   each draw out through its own pocket wall and up the forward band
   ([foam shell as printed](https://github.com/derekbreden/homesodamachine/blob/b20e7d208/hardware/printed-parts/cold-core/foam-shell/README.md)). It stands on the slab
   where the cold core does, its front corners in front-bottom's blocks.
3. **The reservoir runs** cross the Y seam, made up before the back column rides
   ([internal plumbing §3](internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps)):
   - V-F → reservoir A's fill bore
   - reservoir A's draw → V-E
   - V-I → reservoir B's fill bore
   - reservoir B's draw → V-H

   With no cap, each fill tube ends in its reservoir cap's own bore. Tie it so it cannot lift
   out. The modeled `fluid-14`, `16`, `24` and `26` end at the cap's conduits, so cut these at
   the bench.
4. **The back column:** back-top slides fore onto a bare back-bottom, then rides forward over the
   shell. Four vertical M5 screws, each with one flat washer, close the box through the printed clearance holes
   ([enclosure mechanical §6](enclosure-mechanical.md#6-close-the-box)).
5. **The FLAVOR risers:** V-G and V-J to the two FLAVOR bulkheads, `fluid-18` and `fluid-28`, at
   their developed lengths in the assembly facts
   ([internal plumbing §4](internal-plumbing.md#4-rear-beverage-connections)).
6. **The pump cradle** goes in last, through the front bay
   ([internal plumbing §3](internal-plumbing.md#3-flavor-manifold-v-a-through-v-j--y-a-y-b-y-c-y-d-y-f-y-g--pumps)
   step 7): the J13 ribbon's free end through front-top's lead bore, its four Fastons
   crimped and landed on the motor tabs, `AM2`, `AM1` on pump A at +X and `BM2`, `BM1` on
   pump B, then the cradle pushed home until its four tubes bottom in the tees, with the
   slack drawn back from behind, and J13 plugged.

## 7. Wiring

Build the looms per [cable assemblies](cable-assemblies.md) and land them per
[wiring §4–§6](wiring.md#4-cabinet-side-12-v-runs-dc-3-dc-5-through-dc-9):

| Loom | This build |
|---|---|
| J1 MANIFOLD A | All nine conductors. OUT3–OUT8 to V-C–V-H, COM into the 221-420 at its +X well. OUT1 (V-A) and OUT2 (V-B) folded back and labeled. |
| J2 MANIFOLD B | OUT1 to V-I, OUT2 to V-J, COM into the 221-415. OUT3 (V-K) and FAN folded back and labeled; contact 3 stays empty. |
| J13 | The pump ribbon, already landed with the cradle (§6 step 6). |
| J6, J7 | Reservoir A's and B's reed columns, GND into their lever nuts. J7's CLO and CHI conductors trimmed at the housing. |
| J4 | The meter only, SIG-4: IO25, V5, GND. |
| J9 | The machine display: B, A, GND, V12 to the 4.3B's terminals. |
| J3 | SIG-6 to the keystone's 110 IDC, punched to the jack's own pin labels. |
| J5, J11 | Not built. |

Continuity-test each loom pin to pin before it lands, and bundle by zone (wiring §6).

## 8. The faucet and umbilical

Follow [faucet and umbilical](faucet-and-umbilical.md) and the
[faucet assembly](/hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md), with these differences.

- **This faucet has no vent chamber.** The white Sculpted faucet printed September 18 takes no
  vent bungs and no 4 mm drain tube. Its step 6 is: route the soda tube, both flavor tubes and
  the unterminated ribbon through the neck pieces, feed them into the tip, close the lap.
- **Its seals** are the TPU thimble and the counter gasket printed October 8 for this faucet's
  footprint ([prototype gaskets](/hardware/printed-parts/prototype-gaskets-2026-10-08/README.md)).
- **The umbilical** carries the blue tube, the two flavor runs and the SIG-6 ribbon, and no
  OVER:
  - The blue tube takes the Siptenk stiffener into the Westbrass's lower compression port.
  - Each white flavor run joins its black run in a PP0408W union.
  - CARGEN foam goes on the blue tube only, with the braid and collars over the bundle.
  - A 3-prong RJ11 plug is crimped onto the ribbon.
- **The display wiring:** VBUS, GND, TXD, RXD to J3's V5, GND, IO35, IO33
  ([display wiring](faucet-and-umbilical.md#display-wiring-sig-6)).
- **Cut lengths** come from faucet and umbilical §1. Its reach covers a cabinet run, so do not
  cut it short.

## 9. Power-up and commissioning

Follow [firmware and commissioning](firmware-and-commissioning.md):

- **§1–§2:** plug into a GFCI-protected outlet. The machine has no ground-fault protection of its
  own ([GFCI](/future/pie-in-the-sky/gfci.md)). Then read 12 V at the + Wago and 5 V and 3.3 V at
  J4's pins.
- **§3–§5:** flash the main board, the 4.3B and the 1.47 from `main`, one board on USB at a time
  or naming the port ([firmware](/firmware/README.md#building-and-flashing)).
- **§6:** the I²C ACKs; the eight reservoir reeds with a magnet; the faucet's touch switching the
  flavor. No probes, carbonator reeds or MQ-6 here. The meter's ports are both made up, so its
  pulses wait for the first pour in §11.
- **§7:** `selftest`. Eight valves click and both pumps turn; the V-A, V-B, V-K and fan steps
  drive nothing.
- **§9:** `rtc set` and the sound checks.
- **§8,** the relay and compressor, is not run.

## 10. Under the sink

- **Placement:** the top and the rear wall need to stay reachable — the display and the dip tube
  are on top, and every connection is on the rear wall.
- **Connections:**
  - The Lillium's cold carbonated outlet → blue 1/4" LLDPE → TAP. The Lillium's outlets are 1/4"
    push-connect.
  - The umbilical's blue tube → SODA, its flavor tubes → the FLAVOR fittings, its plug → the
    keystone.
  - The cord → the GFCI outlet.
- **Mount the faucet** in the counter per faucet and umbilical: the SS plate slides on from below,
  then the captive washer and nut.
- **The old prototype:** label its lines and keep its pumps, controller, faucet and meter together
  until the new one passes the checks below.

## 11. Water, then soda, then syrup

1. **Soda:** with the flavor side still dry, open the Lillium and pour plain carbonated water.
   Watch the TAP, meter, SODA and faucet joints over towels. `status` shows the meter's pulses
   while it flows.
2. **Water through the flavor side:** a bottle of water through the dip tube with Fill A, then
   Fill B. Prime each until water reaches the faucet, then pour both flavors as water. Watch
   every joint.
3. **Syrup:** run `purge a` and `purge b` with the dip tube in air, so the water leaves through
   the faucet. Then Fill each reservoir from its own syrup bottle and Prime each until syrup
   reaches the faucet.

## What the firmware does here

The main board runs `b79be4d54` or later. Nothing is configured for this build.

- **Pour.** Flow at the meter opens the selected flavor's pair, V-E/V-G or V-H/V-J, and bursts its
  pump into the stream.
- **Prime.** A held Prime opens the pair, then runs the pump.
- **Fill.** Dip tube to the bottom of a 440 mL bottle, then Fill A or B on the machine display. The
  pump draws the bottle into that reservoir and then air through the line, and stops at 80 s or
  at the reservoir's full reed. A reservoir's usable window holds two bottles, so one bottle into a
  reservoir at half or lower cannot overflow it, with or without calibrated reeds. Refill one
  flavor at a time and let each fill draw its bottle empty, so air follows the syrup through the
  line the two flavors share ([concerns](/hardware/concerns.md), "One flavor carried into the
  other").
- **Dry**, `AIR:DRY` on the machine display's USB console: the dip tube out of the bottle, in
  air.
- **Clean** is not for this build. Its first step pumps whatever the dip tube stands in out
  through the faucet. With V-A's port plugged no water comes in, and its flush step pumps the
  reservoir out through the faucet.
- With no probes the cold loop reports a fault and asks for nothing. With no gas sensor the alarm
  input reads clear. Neither stops a pour.

## Before guests use it

1. **The first glass.** Leave it idle overnight, then pour each flavor without priming.
