# Pump replacement

The BPT tube around each Kamoer KPHM600's rotor is a consumable and a pump is replaced as a
unit. Both pumps ride in `enclosure-pump-cartridge`, the large lower cradle whose full-height
face fills the bay in the front wall. Pull that cradle against a braced box and both pumps and
their small top clamp come out together. No enclosure quadrant comes off.

[4](JOINT_COUNT) joints part, all four on the flavor path, and the technician opens none of
them — the collet plate opens all four as the cartridge is pulled. No joint on the water, CO2
or carbonated-water path is opened either: every body on those three paths stands aft of the
bay or on the cold core's own lid, so the carbonator stays full, stays under pressure, and
stays connected.

The appliance runs **dry mode** first: a firmware cycle that fills the manifold with air. Air
enters at the funnel and both reservoir cap vents; what it displaces leaves at the
gooseneck's tip. The user's part is a container under the faucet.

## What the cartridge carries

| Rides out on `enclosure-pump-cartridge` | Stays |
|---|---|
| Both Kamoer pumps, [2](CART_PUMPS) stamped brackets bearing in the lower cradle and both bosses located by the top clamp ([`pump-tray/`](/hardware/printed-parts/enclosure/pump-tray/README.md)) | [8](TRAY_VALVES) valves — V-C…V-J, on the two valve trays ([`valve-tray/`](/hardware/printed-parts/enclosure/valve-tray/README.md)) |
| The four barb tubes, on the barbs they were pushed onto | [3](CAP_VALVES) valves — V-A, V-B, V-K, in the cold core's lid cradles (`_cold_core_interface.cap_cradles`) |
| The DC-5 cartridge-side 22 AWG 4P ribbon, its `43025-0400` receptacle, both Faston pairs on the pump tabs, and the two flush motor-pair channels in the cartridge | The fixed `43020-0400` pump connector, its J13-side ribbon, and the +X ridge-wall cable clip |
| | All [6](BOX_TEES) PP0208E tees. Y-A and Y-B butt fixed valves; Y-C, Y-D, Y-F and Y-G are the [4](CARRIER_TEES) tees tied to the moving carrier |
| | The carrier, its [2](SPRING_COUNT) aft-pushing springs, [2](TAB_COUNT) handed service-tab arms and [2](TAB_LOCK_COUNT) top-drop tab locks |
| | The integral collet plate, tee-journal wall, carrier guides and both physical stops in `enclosure-front-top` |
| | The [4](BOWED_STUBS) bowed tee-to-fore-valve stubs and [4](MOVING_HAIRPINS) spine hairpins. Their tee ends move with the carrier; their valve ends remain fixed |
| | Every other turn and butted stub inside the pack, and every mouth it spends on a bulkhead or a cap conduit |
| | The funnel, in its throat; the enclosure display; the SeaFlo and both its chains; the cold core itself |

**The manifold stays in the appliance, but its four-tee carrier travels inside front-top.**
[2](TIES_PER_TEE) ties per tee couple Y-C, Y-D, Y-F and Y-G in Y while the fixed wall journals their branch
collars in X and Z. The service-tab arms and their keys travel with the carrier; the two springs
compress between it and fixed front-top. The tee-side ends of four bowed stubs and four
hairpins follow the same stroke. Nothing in that mechanism rides out on the cartridge: the only
tube ends that cross the bay's mouth are the four the pumps carry with them.

## The [4](JOINT_COUNT_3) joints the plate opens

Derived at every build from `manifold_layout.SEGMENTS` and `manifold_layout.MOUTHS` against
`_scorecard.fastened_by` and `_facts.pump_trays`, then asked a second time of the collet passages — the
plate is bored one hole per barb tee, so what the pieces hold and what the plate releases have
to name one set. A pump that changes seat changes this table, and `_pump_replacement_sync.py`
fails rather than letting it drift.

| Joint | Cartridge end | Staying end | Exposed tube | Air-filled by |
|---|---|---|---|---|
| `fluid-11` | pump A's suction barb | Y-C's branch collet | [7.0](LEN_11) mm | states 1 and 2 |
| `fluid-12` | pump A's discharge barb | Y-D's branch collet | [7.0](LEN_12) mm | states 1 and 2 |
| `fluid-21` | pump B's suction barb | Y-F's branch collet | [7.0](LEN_21) mm | states 3 and 4 |
| `fluid-22` | pump B's discharge barb | Y-G's branch collet | [7.0](LEN_22) mm | states 3 and 4 |

**Every joint that parts is one the dry cycle sweeps.** Each of the four stands between a pump
and a tee on that pump's own channel, so either state that runs a pump carries air across both
of its joints. Nothing comes apart wet, nothing drains onto a body beneath it, and no reservoir
is drawn on — the container under the faucet is the only one the procedure asks for.

## How the plate lets go

The collet plate is printed into front-top, with a nominal release section
[200](PLATE_SPAN) mm across and [3.175](PLATE_T) mm thick. Its release face stands
[1.5](REST_GAP) mm fore of the four branch-collet noses at the squeeze datum. Four Ø8.5 mm
teardrop passages pass the Ø[6.35 mm](TUBE_OD) cartridge tubes while leaving a land under each
release sleeve. The upper cap, outer cheeks, floor joins and front-bottom feet are features of
the printed enclosure. The cartridge's aft notches clear the cheeks as it moves.

**The wall behind the plate holds each carried tee square in X and Z; the carrier locates all
four together in Y.** The wall clears each branch collar by `TEE_WALL_BORE_SLIP` on the radius.
Its larger collar bore meets the smaller teardrop passage at the release face, and its aft face
leaves each tee body [3.15](STROKE) mm of modeled release travel from squeeze plus
[1.454](BODY_AIR) mm of body air (`TEE_WALL_BODY_AIR`). That release stroke is the
[1.5](REST_GAP) mm gap plus the PP0208E's measured [1.65](SLEEVE_TRAVEL) mm sleeve travel
([`reference/tee-connector/`](/hardware/reference/tee-connector/README.md)). The plate, wall,
guides and stops stay fixed throughout a pump swap.

The service motion has four named carrier states. Offsets are enclosure +Y, aft, from the
squeeze datum. Only release and park are physical stops.

| State | Carrier offset | Tube relation |
|---|---:|---|
| release | [−3.15](RELEASE_OFFSET) mm | fore stop; the fixed plate holds all four sleeves open |
| squeeze | [0](SQUEEZE_OFFSET) mm | both tabs held together; tubes bottom at [10](SQUEEZE_DEPTH) mm |
| connected | [+1.5](CONNECTED_OFFSET) mm | floats under spring load at the [8.5](CONNECTED_DEPTH) mm grip depth |
| park | [+3](PARK_OFFSET) mm | empty aft stop, corresponding to [7](PARK_DEPTH) mm first resistance and therefore beyond connection reach |

At connected, the four tee teeth grip the four cartridge tubes. A straight cartridge pull
therefore carries all four tied tees and the carrier fore from +1.5 mm to release at −3.15 mm,
a [4.65](CONNECTED_RELEASE_TRAVEL) mm connected-to-release motion. The noses meet the fixed
plate and the last 1.65 mm of sleeve travel opens the teeth; the tubes continue through the
holes and leave the tees. With that tensile link gone, the two springs send the empty carrier
aft to park at +3 mm. The two tab arms, their keys, the tee-side ends of the bowed stubs and the
tee-side ends of the hairpins travel with the carrier throughout; their fixed valve ends do
not. There is no cartridge lock and no release tool. The cartridge face may finish flush after
reconnection, but neither that face nor the plate is a final seat or proof that four tubes are
gripped.

## Dry mode

Four states in order, both pumps forward, every valve inlet to outlet.

| # | Canonical state | Open | Pump | Path |
|---|---|---|---|---|
| 1 | Air Purge In → Reservoir A | V-B, V-C, V-F | A | funnel → crossbar → V-C → hairpin `fluid-9` → Y-C → **pump A** → Y-D → V-F → `fluid-14` → reservoir A |
| 2 | Air Purge Through A | V-B, V-C, V-G | A | same head, then Y-D → hairpin `fluid-17` → V-G → `fluid-18` → out the tip |
| 3 | Air Purge In → Reservoir B | V-B, V-D, V-I | B | mirror of 1, into reservoir B |
| 4 | Air Purge Through B | V-B, V-D, V-J | B | mirror of 2, out the tip |

States 2 and 4 are the ones that carry air out the gooseneck without drawing on a reservoir, so a pump
swap costs no concentrate. Three valves is the most any state opens, and states 1 and 2 sit entirely
on MANIFOLD A — inside the shared-COM budget in
[`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

Every state is timed with overrun. A reservoir's float travel begins above its wet slope
([`level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)) and the draw
port is the bulkhead in the trough below it, so no reed stands at the line a purge drains to; the
DIGITEN meter stands on the carbonated-water line, not the flavor path.

The states themselves are canonical in
[`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) "Operations — Valve
States"; this doc names the order they run in.

## Procedure

**Do not force a carrier that is racked or operate one service tab by itself.** Before a swap,
look through both service openings: both rigid tab arms and both top-drop keys must be fully
seated, the two tabs must agree in Y, and the visible portions of all four bowed stubs and four
moving hairpin ends must be free of kinks, abrasion and enclosure contact. A displaced key,
unequal tabs, a reluctant return or a damaged flexible member stops the procedure for
inspection; neither the cartridge nor a tab is a lever for clearing it.

**1. Run dry mode.** A container under the faucet — states 2 and 4 send a slug of air and residual
syrup out the gooseneck.

**2. Pull the cartridge.** Hook the pulling hand into either cradle pocket, centred on the
cradle's flank at the tube-centre elevation, and brace the box with the other hand. From the
connected +1.5 mm state, pull the fore ledge and draw the cradle straight forward along the bay
floor. The four gripped tubes carry the tied tees and carrier to release at −3.15 mm against
the fixed plate. Its lands hold all four sleeves while the last 1.65 mm opens the teeth; all
[4](JOINT_COUNT_2) tubes must leave together. As soon as they are clear, the two springs must
return the empty carrier evenly to park at +3 mm. Stop if one tube remains caught, the tabs
disagree, or the carrier fails to park; do not twist the cradle or pry a sleeve. Continue the
straight pull only after release. The connector-to-cartridge service loop follows without
passing through the enclosure-side cable clip; its two peeled motor-pair branches remain
positively retained in the flush channels which leave with the cartridge.

With the cradle clear and power still removed, inspect all four cartridge-tube ends for a
square, unscarred mouth; inspect the four plate holes, the eight carrier ties, both tab/key
joints, and the visible travel ends of all eight flexible links. Then reach up through the empty
bay behind the display, press the Micro-Fit's downward-facing thumb latch, pull the cartridge
housing straight forward until the pair is clear, and lower it through the bay before standing
the cradle on its bottom floor. Do not lever the fixed half or pull either ribbon. The four pump
Fastons remain made off until the cartridge is on the bench.

**3. Unscrew the top clamp, then swap the pumps.** Back out the [2](CAP_SCREWS)
M3×[10](CAP_SCREW_LEN) between the pumps and lift the complete clamp straight up. Its two
top-open flank reliefs rise clear of the retained motor-pair branches without asking either
branch to leave its cartridge channel. Remove the two Faston pairs from the old motor tabs,
then lift each pump out of its cradle well. Lower each replacement until three sides of its stamped
bracket lie flat on the cradle lands, lower the clamp until its two octagonal collars surround
the bosses and its pressing plates meet the bracket tops, then draw both screws down evenly.
The brackets carry pump weight into the cradle; the clamp prevents lift and fixes X, Y and yaw.
If it does not sit flat, lift and reseat the pump instead of using a screw to force it. Tug-test
each pump once the clamp is closed.

**4. Land 1/4" OD LLDPE in the new heads** — the tube runs around the rotor, and the LLDPE goes
**into the tube's own bore** at each of its two ends, not onto the moulded barb. Zip-tie the tube
down onto the LLDPE at all [4](JOINT_COUNT_4) joints and leave each length standing aft off the
face; that LLDPE is what the plate's hole passes and the branch collet grips. **The zip tie is
load-bearing here** — this joint takes the release tension when the cartridge is next drawn, so
tug-test each of the four before the deck goes back in.

**5. Connect, squeeze, insert and release.** Put both Faston pairs back on the replacement
motor tabs first — they are unreachable once the cradle is in. Lay each peeled pair back into
its own flush cartridge channel and tug the free service loop at the connector end; neither
Faston may take that pull. With power removed, reach behind
the display and push the cartridge's `43025-0400` onto the fixed `43020-0400` until the thumb
latch clicks; tug the housing, not the ribbon, to prove it is closed. Set the cradle on the bay
floor and present all four tubes squarely through their plate holes. Squeeze both service tabs
together and hold the carrier at 0 mm. Advance the cartridge without twisting it and push all
four tubes to their 10 mm bottoms. Release both tabs together: the two springs move the carrier
aft until all four teeth grip at connected, +1.5 mm carrier offset and 8.5 mm tube depth.

Both tabs must settle evenly at connected. A carrier that remains at park with the cartridge
presented means at least one tube missed its tee; squeeze again, withdraw, inspect and retry
rather than forcing the cartridge farther aft. The cartridge face should appear flush only
after the carrier state and four grips are proved. Face flushness and contact with the plate
are not insertion datums, final seats or proof of connection.

**6. Re-prime.** Both channels through the funnel-fill path, then a dispense on each until it
runs clean. While each channel flows, inspect both replacement-head connections and all visible
carrier flex links for seepage, rubbing or a link pulled taut.

## Output condition

- Both pumps replaced, each bracket bearing in the lower cradle with the top clamp closed, tug-tested
- DC-5 Micro-Fit latched behind the display; fixed J13-side ribbon retained in the ridge-wall
  clip, both cartridge motor-pair branches retained in their flush pump-well channels, and the
  connector-to-channel service loop free to follow the next withdrawal
- During removal, all four tubes released together at −3.15 mm and the empty carrier returned
  evenly to park at +3 mm; both rigid tab arms and both tab locks remained seated
- Four fresh barb tubes on the barbs and all [4](JOINT_COUNT_4) joints bottomed together at
  squeeze, 0 mm; both tabs released evenly to connected, +1.5 mm, with all tubes gripped at
  8.5 mm. The cartridge face is visually flush, but was not used as the connection proof
- Four bowed stubs and four moving hairpin ends clear, unscarred, unkinked and slack through
  the observed stroke; all eight carrier ties intact and flush-cut
- Both channels re-primed and dispensing clean
- No joint on the water, CO2 or carbonated-water path opened; the carbonator never depressurised

## Open items

1. **Nothing sequences these four states.** Each is canonical on its own — they are the two
   `Air Purge In` and two `Air Purge Through` rows of
   [`fluid-topology.md`](/hardware/topology/fluid-topology.md) "Operations — Valve States" — but
   the cycle that runs them in order is named only here. `firmware/src_appliance` carries no
   purge and no dry mode: what it has is a per-channel PRIME (`machinePrimeBegin`,
   `machineIsPriming`, `HOLD_PRIME`), and priming FILLS where this EMPTIES. Step 1 of this
   procedure cannot be performed until something sequences them.
2. **Dry-run wear on a KPHM600's BPT tube is not characterised.** Every one of the four states
   turns a rotor on air.
3. **A customer-facing transit mode is not written.** This procedure leaves the carbonator charged.
   The carbonator's only liquid outlet climbs to the faucet, and the factory's transit sequence is
   [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) step 13.
4. **The complete carrier mechanism is not yet physically qualified.** Before this procedure
   is released for production service, the four tee-to-valve bows must be bench-fitted to
   12 mm exposed/developed paths across their 10 mm sleeve-face chords; 12 mm is not a stock
   cut length, and the blank remains TBD by that fixture. Cycle and force-measure the complete
   four-tee mechanism through release, squeeze, connected and park with all eight ties, two
   springs, both tab arms and keys, four bowed stubs, four moving hairpin ends and four real
   cartridge tubes installed. It must release four together, return empty to park, settle
   repeatably at connected and remain leak-free, without racking, rubbing, coil bind, buckling,
   spring escape, key withdrawal or tube damage. Catalog force calculations and collision-free
   CAD do not close this gate; record it under
   [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) Open item 7.

## Sources
[value](NAME) texts are updated by:
- `/hardware/service/_pump_replacement_sync.py`
