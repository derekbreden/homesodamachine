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
| The pump cartridge's 28 AWG 4P cord, its RJ11 pump plug, and both Faston pairs on the pump tabs | The pump jack, its J13-side 22 AWG 4P ribbon, and the +X ridge-wall cable clip |
| | All [6](BOX_TEES) PP0208E tees. Y-A and Y-B butt fixed valves; Y-C, Y-D, Y-F and Y-G are the [4](CARRIER_TEES) tees tied to the moving carrier |
| | The two carrier halves, their [2](TAB_COUNT) integral service tabs, [2](CARRIER_JOINT_SCREWS) center-joint screws and [2](SPRING_COUNT) aft-pushing springs |
| | The integral collet plate, tee-journal wall, carrier guides and both physical stops in `enclosure-front-top` |
| | The [4](BOWED_STUBS) bowed tee-to-fore-valve stubs and [4](MOVING_HAIRPINS) spine hairpins. Their tee ends move with the carrier; their valve ends remain fixed |
| | Every other turn and butted stub inside the pack, and every mouth it spends on a bulkhead or a cap conduit |
| | The funnel, in its throat; the enclosure display; the SeaFlo and both its chains; the cold core itself |

**The manifold stays in the appliance, but its four-tee carrier travels inside front-top.**
[2](TIES_PER_TEE) ties per tee couple Y-C, Y-D, Y-F and Y-G in Y while the fixed wall journals their branch
collars in X and Z. Each integral service tab is a closed finger cup with a thick front bar.
The cups run in the flank openings; their opposed rims retain the joined carrier sideways
and cover the openings throughout travel. The two springs
compress between it and fixed front-top. The tee-side ends of four bowed stubs and four
hairpins follow the same stroke. Nothing in that mechanism rides out on the cartridge: the only
tube ends that cross the bay's mouth are the four the pumps carry with them.

## The [4](JOINT_COUNT_3) joints the plate opens

Derived at every build from `manifold_layout.SEGMENTS` and `manifold_layout.MOUTHS` against
`_scorecard.fastened_by` and `_facts.pump_trays`, then asked a second time of the collet passages — the
plate is bored one hole per barb tee, so what the pieces hold and what the plate releases have
to name one set. A pump that changes seat changes this table, and `_pump_replacement_sync.py`
fails rather than letting it drift.

| Joint | Cartridge end | Staying end | Exposed tube at fore stop | Air-filled by |
|---|---|---|---|---|
| `fluid-11` | pump A's suction barb | Y-C's branch collet | [9.0](LEN_11) mm | states 1 and 2 |
| `fluid-12` | pump A's discharge barb | Y-D's branch collet | [9.0](LEN_12) mm | states 1 and 2 |
| `fluid-21` | pump B's suction barb | Y-F's branch collet | [9.0](LEN_21) mm | states 3 and 4 |
| `fluid-22` | pump B's discharge barb | Y-G's branch collet | [9.0](LEN_22) mm | states 3 and 4 |

**Every joint that parts is one the dry cycle sweeps.** Each of the four stands between a pump
and a tee on that pump's own channel, so either state that runs a pump carries air across both
of its joints. Nothing comes apart wet, nothing drains onto a body beneath it, and no reservoir
is drawn on — the container under the faucet is the only one the procedure asks for.

## How the plate lets go

The collet plate is printed into front-top, with a nominal release section
[200](PLATE_SPAN) mm across and [3.175](PLATE_T) mm thick. Its release face stands
[0.5](REST_GAP) mm fore of the fully extended branch-collet noses at the aft stop. Four Ø8.5 mm
teardrop passages pass the Ø[6.35 mm](TUBE_OD) cartridge tubes while leaving a land under each
release sleeve. The upper cap, outer cheeks, floor joins and front-bottom feet are features of
the printed enclosure. The cartridge's aft notches clear the cheeks as it moves.

**The wall behind the plate holds each carried tee square in X and Z; the carrier locates all
four together in Y.** The wall clears each branch collar by `TEE_WALL_BORE_SLIP` on the radius.
Its larger collar bore meets the smaller teardrop passage at the release face. At the fore
stop the sleeves are fully depressed and the tee bodies retain [1.454](BODY_AIR) mm of air to
the fixed wall (`TEE_WALL_BODY_AIR`). The complete stroke is [2.15](STROKE) mm:
[0.5](REST_GAP) mm of nose air plus the PP0208E's measured [1.65](SLEEVE_TRAVEL) mm sleeve
travel ([`reference/tee-connector/`](/hardware/reference/tee-connector/README.md)). The plate,
wall, guides and stops stay fixed throughout a pump swap.

The service operations share two physical stops. Offsets are enclosure +Y, aft, from the
fore stop. The complete appliance is displayed at the aft stop.

| Operation | Carrier offset | Tube relation |
|---|---:|---|
| release | [0](RELEASE_OFFSET) mm | fore stop; fixed plate continuously holds all four sleeves open |
| squeeze | [0](SQUEEZE_OFFSET) mm | same fore stop; the opposed grasp bottoms tubes [10](SQUEEZE_DEPTH) mm beyond the depressed sleeves |
| connected | [+2.15](CONNECTED_OFFSET) mm | aft stop; sleeves extended, tubes gripped |
| park | [+2.15](PARK_OFFSET) mm | same aft stop with the cartridge absent |

A straight cartridge pull carries all four tied tees and the carrier to the fore stop,
a [2.15](CONNECTED_RELEASE_TRAVEL) mm motion. The noses meet the fixed plate and the last
1.65 mm depresses the sleeves; the plate continues holding them while the tubes leave.
With that tensile link gone, the two springs return the empty carrier aft. The two integral
tabs, center joint, tee-side ends of the bowed stubs and tee-side ends of the hairpins travel
with the carrier; the valve ends stay fixed. There is no cartridge lock and no release tool.
At squeezed fore, the tubes bottom while the cartridge is 2.15 mm short of seating. Release
the grips and push it through that final 2.15 mm; the tubes then bottom at the aft stop and
the cartridge face finishes flush. Verify all four tubes are gripped
with a gentle tug.

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
check that both integral tabs are sound and agree in Y, and that the visible portions of all
four bowed stubs and four moving hairpin ends are free of kinks, abrasion and enclosure contact.
Unequal tabs, a reluctant return, a loose center joint or a damaged flexible member stops the
procedure for inspection; neither the cartridge nor a tab is a lever for clearing it.

**1. Run dry mode.** A container under the faucet — states 2 and 4 send a slug of air and residual
syrup out the gooseneck.

**2. Pull the cartridge.** Hook into the cradle pockets and brace the enclosure with a hand, foot or cupboard edge,
or let its weight provide the reaction. Both hands can pull when the enclosure is otherwise
supported. Pull the fore ledge and draw the cradle straight forward along the bay floor.
The four gripped tubes carry the tied tees and carrier from the aft stop to the fore stop.
The fixed plate takes up the nose gap and depresses the sleeves, then holds them continuously
while all [4](JOINT_COUNT_2) tubes leave. The springs must return the empty carrier evenly
to the aft stop. Stop if one tube remains caught, the tabs disagree, or the carrier fails to
return; do not twist the cradle or pry a sleeve. The free cartridge ribbon follows without
passing through the enclosure-side cable clip.

With the cradle clear and power still removed, inspect all four cartridge-tube ends for a
square, unscarred mouth; inspect the four plate holes, the eight carrier ties, the center lap
joint, and the visible travel ends of all eight flexible links. Then reach up through the empty
bay behind the display, press the pump plug's clip from below, pull the plug straight forward
until it is clear of the plate cap, and lower it through the bay before standing the cradle on
its bottom floor. Do not lever the jack or pull either ribbon. The four pump Fastons remain made
off until the cartridge is on the bench.

**3. Unscrew the top clamp, then swap the pumps.** Back out the [2](CAP_SCREWS)
M3×[10](CAP_SCREW_LEN) between the pumps and lift the complete clamp straight up. Remove the two
Faston pairs from the old motor tabs, then lift each pump out of its cradle well. Lower each replacement until three sides of its stamped
bracket lie flat on the cradle lands, lower the clamp until its two octagonal collars surround
the bosses and its pressing plates meet the bracket tops, then draw both screws down evenly.
The brackets carry pump weight into the cradle; the clamp prevents lift and fixes X, Y and yaw.
If it does not sit flat, lift and reseat the pump instead of using a screw to force it. Tug-test
each pump once the clamp is closed.

**4. Land 1/4" OD LLDPE in the new heads** — the tube runs around the rotor, and the LLDPE goes
**into the tube's own bore** at each of its two ends, not onto the moulded barb. Zip-tie the tube
down onto the LLDPE at all [4](JOINT_COUNT_4) joints and leave each length standing aft off the
face. After securing each pump-end joint, set its free tip [19.03 mm](TUBE_PROJECTION) beyond
the pump outlet tip; this includes the tee insertion and the final cartridge seating stroke.
That LLDPE is what the plate's hole passes and the branch collet grips. **The zip tie is
load-bearing here** — this joint takes the release tension when the cartridge is next drawn, so
tug-test each of the four before the deck goes back in.

**5. Connect, squeeze, release and seat.** Put both Faston pairs back on the replacement
motor tabs first — they are unreachable once the cradle is in. With power removed, reach behind
the display and push the pump plug into the pump jack until it clicks; tug the plug, not the
cord, to prove it is home. Set the cradle on the bay
floor and present all four tubes squarely through their plate holes. Each hand spans the
cartridge pocket and the service tab on the same side: thumb pushes the cartridge aft, fingers
pull the tab fore. Squeeze both hands evenly until all four tubes reach their 10 mm bottoms
at the fore stop, with the cartridge still 2.15 mm short of seating. Relax both hands together:
the springs return the carrier aft, fully extending the sleeves and leaving 0.5 mm of nose air.
Push the cartridge through its final 2.15 mm to seat it with the tubes bottomed at the aft
body stops. Both tabs must settle evenly. Gently tug the cartridge to prove all four connections; if a tube is loose, withdraw
it, inspect its end and alignment, and reconnect. The cartridge face should finish flush.

**6. Re-prime.** Both channels through the funnel-fill path, then a dispense on each until it
runs clean. While each channel flows, inspect both replacement-head connections and all visible
carrier flex links for seepage, rubbing or a link pulled taut.

## Output condition

- Both pumps replaced, each bracket bearing in the lower cradle with the top clamp closed, tug-tested
- The pump plug clicked into the pump jack behind the display; the fixed J13-side ribbon retained
  in the ridge-wall clip and the cartridge's cord free to follow the next withdrawal
- During removal, all four tubes released together at the fore stop and the empty carrier
  returned evenly to the aft stop; both integral tabs and the center joint remained sound
- Four LLDPE ends secured in the pump tubing and all [4](JOINT_COUNT_4) joints bottomed together at
  the fore stop with the cartridge 2.15 mm short of seating; cartridge fully seated and tubes
  bottomed at the aft stop after release, both tabs even and all four tubes tug-checked
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
4. **Bowed-stub stock lengths.** The four tee-to-valve links have 12 mm exposed paths across
   sleeve faces 10 mm apart in height and 1.75 mm apart fore/aft at squeeze. Their stock blanks also include both fittings' insertion depths;
   the valve-side depth is not recorded. Factory assembly fits and records these lengths in
   [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) step 5.

## Sources
[value](NAME) texts are updated by:
- `/hardware/service/_pump_replacement_sync.py`
