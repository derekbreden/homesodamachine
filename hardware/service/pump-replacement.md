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
| Both DC-5 spade pairs, once they are off the motor tabs | All [6](BOX_TEES) PP0208E tees — each butts a valve that stays |
| | The integral printed collet plate and its four tee-collar bores (`enclosure._tee_wall`) |
| | Every hairpin, turn and butted stub inside the pack, and every mouth it spends on a bulkhead or a cap conduit |
| | The funnel, in its throat; the enclosure display; the SeaFlo and both its chains; the cold core itself |

**The manifold does not move.** Every valve, tee and tube in the pack stands on a seat the box
keeps, so the only tube ends that cross the bay's mouth are the four the pumps carry out with
them. The funnel stays in its throat, the enclosure display stays in its bezel, and the pack is never
handled.

## The [4](JOINT_COUNT_3) joints the plate opens

Derived at every build from `manifold_layout.SEGMENTS` and `manifold_layout.MOUTHS` against
`_scorecard.fastened_by` and `_facts.pump_trays`, then asked a second time of the release face — the
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

The collet plate is a [3.175 mm](COLLET_PLATE_T) PET-GF release section printed into front-top’s
tee wall, [209](PLATE_SPAN) mm across and continuous with the floor and both flanks. Each tube
passage opens onto a flat annular land inside its tee’s collar bore. The four short tubes share
the tee axes and slide through the passages without a vertical jog.

The gap between each barb and collet contains [2.305](BARB_AIR) mm of barb air, the
[3.175 mm](COLLET_PLATE_T) release section and [1.5](REST_GAP) mm of nose air. Pulling the cradle draws the
tees forward through that nose air. Their noses then stop on the printed lands while the bodies
continue far enough to depress the sleeves and release the tubes. The design uses the John Guest
union’s measured sleeve travel; the assembled tee release and compliance of its butted joints
are physical fit checks.

The collar bores locate each tee across its axis and leave it free along Y. At full design
travel, the broad wall behind the release face remains 1 mm clear of the tee shoulders.
Pushing the cartridge home threads the four tubes back into their collets. One hand pulls or
pushes the cradle and the other braces the enclosure; the continuous floor, wall and flanks
carry the release reaction.

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

**1. Run dry mode.** A container under the faucet — states 2 and 4 send a slug of air and residual
syrup out the gooseneck.

**2. Pull the cartridge.** Hook the pulling hand into either recessed cradle pocket at the
tube-centre elevation and brace the box with the other hand. Pull on its fore ledge and draw
the cradle straight forward along the bay floor: the [4](JOINT_COUNT_2) joints let go against
the plate in the first few millimetres, and the rest of the stroke is the cradle leaving the
bay. Pull the two DC-5 spade pairs off the motor tabs and stand the cradle on its bottom floor.

**3. Unscrew the top clamp, then swap the pumps.** Back out the [2](CAP_SCREWS)
M3×[10](CAP_SCREW_LEN) between the pumps and lift the complete clamp straight up. Then lift
each pump out of its cradle well. Lower each replacement until three sides of its stamped
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

**5. Push the cartridge home.** Spade pairs back on the motor tabs first — they are unreachable
once the cradle is in. Then set the cradle on the bay floor, feed the four tubes through the
plate holes and into the branch collets, and push firmly on the face with one hand bracing the
box. Confirm that the exterior face sits flush and all four tubes are fully inserted.

**6. Re-prime.** Both channels through the funnel-fill path, then a dispense on each until it
runs clean.

## Output condition

- Both pumps replaced, each bracket bearing in the lower cradle with the top clamp closed, tug-tested
- Four fresh barb tubes on the barbs and all [4](JOINT_COUNT_4) joints threaded home, the
  cartridge's face flush in the bay
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
4. **Confirm the complete four-joint release on the assembled cartridge.** The design stroke
   includes the nose gap and sleeve travel measured on the John Guest union. The anchor tees'
   required travel and the compliance of their butted valve joints need a physical fit check.

## Sources
[value](NAME) texts are updated by:
- `/hardware/service/_pump_replacement_sync.py`
