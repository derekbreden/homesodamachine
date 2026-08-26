# Pump replacement

The BPT tube around each Kamoer KPHM400's rotor is a consumable and a pump is replaced as a
unit. Both pumps ride `enclosure-pump-cartridge`, the printed piece whose face fills the bay in
the front wall: pull the face against a braced box and both heads come out on its deck. No
quadrant comes off and nothing is unscrewed.

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
| Both Kamoer pumps, [2](CART_PUMPS) heads in the deck's printed trays ([`pump-tray/`](/hardware/printed-parts/enclosure/pump-tray/README.md)) | [8](TRAY_VALVES) valves — V-C…V-J, on the two valve trays ([`valve-tray/`](/hardware/printed-parts/enclosure/valve-tray/README.md)) |
| The four barb tubes, on the barbs they were pushed onto | [3](CAP_VALVES) valves — V-A, V-B, V-K, in the cold core's lid cradles (`_cold_core_interface.cap_cradles`) |
| Both DC-5 spade pairs, once they are off the motor tabs | All [6](BOX_TEES) PP0208E tees — each butts a valve that stays |
| | The collet plate, in the slot through the bay floor, and the printed wall behind it the four tees stand in (`enclosure._tee_wall`) |
| | Every hairpin, turn and butted stub inside the pack, and every mouth it spends on a bulkhead or a cap conduit |
| | The funnel, in its throat; the enclosure display; the SeaFlo and both its chains; the cold core itself |

**The manifold does not move.** Every valve, tee and tube in the pack stands on a seat the box
keeps, so the only tube ends that cross the bay's mouth are the four the pumps carry out with
them. The funnel stays in its throat, the enclosure display stays in its bezel, and the pack is never
handled.

## The [4](JOINT_COUNT_3) joints the plate opens

Derived at every build from `manifold_layout.SEGMENTS` and `manifold_layout.MOUTHS` against
`_scorecard.fastened_by` and `_facts.pump_trays`, then asked a second time of the steel — the
plate is bored one hole per barb tee, so what the pieces hold and what the plate releases have
to name one set. A pump that changes seat changes this table, and `_pump_replacement_sync.py`
fails rather than letting it drift.

| Joint | Cartridge end | Staying end | Exposed tube | Air-filled by |
|---|---|---|---|---|
| `fluid-11` | pump A's suction barb | Y-C's branch collet | [5.7](LEN_11) mm | states 1 and 2 |
| `fluid-12` | pump A's discharge barb | Y-D's branch collet | [5.7](LEN_12) mm | states 1 and 2 |
| `fluid-21` | pump B's suction barb | Y-F's branch collet | [5.7](LEN_21) mm | states 3 and 4 |
| `fluid-22` | pump B's discharge barb | Y-G's branch collet | [5.7](LEN_22) mm | states 3 and 4 |

**Every joint that parts is one the dry cycle sweeps.** Each of the four stands between a pump
and a tee on that pump's own channel, so either state that runs a pump carries air across both
of its joints. Nothing comes apart wet, nothing drains onto a body beneath it, and no reservoir
is drawn on — the container under the faucet is the only one the procedure asks for.

## How the plate lets go

The collet plate is a waterjet 1/8" 304 flat ([`/hardware/manifold-layout/`](/hardware/manifold-layout/README.md)
`collet-plate.dxf`), [208.4](PLATE_SPAN) mm wall to wall and [3.175](PLATE_T) mm thick, standing
on edge in a slot that passes clean through the bay floor and opens on front-top's own Z− face.
The slot locates it fore and aft over the floor's whole section and narrows at that mouth to
the foot's own width, so the two shoulders the foot leaves come up onto the floor's top and
that is what carries the plate; the printed wall behind it takes the push across its whole face.
The floor is not asked to keep the top from pitching: at the plate's
two outer tails, stationary L-section cheeks stand just fore of the steel and return round
its ends into front-top's fixed aft side-wall stock. Each cheek is a wedge in plan, deepest
where it is rooted in that side wall, so the section taking the moment stands where the
cheek is carried and not where it is free. Each cheek's crown reaches aft to the tee wall over
the tail, one running clearance over the steel's top, and holds it down. They remain with the
enclosure while the cartridge moves and the four collet noses load the plate. **A pump swap
never touches the steel** — it is inside the closed front column, and nothing in this
procedure opens that.

Seated, the steel stands in the berth between the barbs and the collets, and that berth is
spent three ways: [1.025](BARB_AIR) mm of air off the barb plane, the plate's own
[3.175](PLATE_T) mm, and [1.5](REST_GAP) mm of nose air under the four branch collet faces.
Its four large holes stand on the four branch collets' own axes and each is bored to two figures
at once — wide enough to pass the Ø[6.35 mm](TUBE_OD) tube it has to let slide, narrow enough
to leave land under the collet nose it has to stop. Nothing else is cut in it.
`enclosure_assembly.check_collet_plate` holds those bores to both jobs at once.

**The wall behind the steel is what holds a tee square while that happens.**
`enclosure-front-top` carries a section of its own material aft of the plate, wall to wall and
the whole height of the bay, bored once per anchor tee (`enclosure._tee_wall`). Each bore
closes on the round collar the tee's branch arm carries — `TEE_WALL_BORE_SLIP` on the radius,
a running fit and not a grip — so a tee is located across its own axis by printed material and
free along it, which is the one direction the release moves it. The wall's fore face IS the
steel's aft face, struck as one figure, so every bore is stopped at its fore mouth by steel
and the nose that lands there lands on steel and not on plastic. Its aft face stands one whole
stroke plus `TEE_WALL_BODY_AIR` fore of the tee's own body, so at full release there is still
air behind the tee: what the wall holds is the collar, and what stops the tee is the steel.

Pull the cartridge and the gripped tubes drag the tees forward [1.5](REST_GAP) mm — each tee
running in its own bore — until each nose lands on that land. The body keeps coming, the nose
is held, the grip opens, and the tube draws out through the hole it entered by. Push the
cartridge home and the same four tubes thread the same four holes back into the same collets,
the cap's own aft face landing on the plate's fore face as the last one bottoms. **The user's two hands are the whole mechanism**:
one pulls the cartridge, the other braces the box, and the box carries that brace to the plate
through its fixed wall and the two wedge cheeks. There is no cartridge lock and no tool in
this pump-replacement motion.

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

**2. Pull the cartridge.** Hook the pulling hand into either recessed flank grip and brace
the box with the other hand. Pull on the grip's raked fore ledge and draw the cartridge
straight forward along the bay floor it rides: the [4](JOINT_COUNT_2) joints let go
against the plate in the first few millimetres, and the rest of the stroke is the deck coming
out of the bay. Pull the two DC-5 spade pairs off the motor tabs and set the cartridge
face-down on the bench.

**3. Unscrew the cap, then swap the pumps.** Back out the [2](CAP_SCREWS)
M3×[10](CAP_SCREW_LEN) on the lane between the pumps and lift the cap away — it closes on both
heads and it is the only thing holding either up, so nothing else has to be cut or released.
Then lift each boss out of its [53 mm](PUMP_SOCKET) octagon bore. The new pump goes in the same
way: boss lowered until the head's crown lands all the way round, cap back on, both screws drawn
up. **What carries a pump is its own stamped bracket**, lapping the cap's top face all round the
head — so a cap that will not sit down flat is a pump that is not seated, and forcing the screws
puts the load on the block instead of the bracket. Tug-test each pump once the cap is closed.

**4. Route 1/4" OD LLDPE through the new heads** — onto the BPT barbs directly, around the
rotor, zip-tied tight. Then push a fresh barb tube fully over each of the four barbs and leave
it standing aft off the face; that stub is what the plate's hole passes and the branch collet
grips.

**5. Push the cartridge home.** Spade pairs back on the motor tabs first — they are unreachable
once the deck is in. Then the deck onto its ledges, the four tubes through the plate's holes
and into the branch collets, and a firm push on the face with one hand bracing the box. The
cap's face landing on the steel is the seat: a face standing proud of the wall is a tube that has
not gone home.

**6. Re-prime.** Both channels through the funnel-fill path, then a dispense on each until it
runs clean.

## Output condition

- Both pumps replaced, each standing in the cartridge with the cap closed on its bracket, tug-tested
- Four fresh barb tubes on the barbs and all [4](JOINT_COUNT_4) joints threaded home, the
  cartridge's face flush in the bay and the cap's aft face on the steel
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
2. **Dry-run wear on a KPHM400's BPT tube is not characterised.** Every one of the four states
   turns a rotor on air.
3. **A customer-facing transit mode is not written.** This procedure leaves the carbonator charged.
   The carbonator's only liquid outlet climbs to the faucet, and the factory's transit sequence is
   [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) step 13.
4. ~~**The stroke is not clear, so the cartridge cannot come out.**~~ **CLOSED.**
   `release-travel` offers each anchor tee the whole stroke and all four clear it. The stroke
   is the rest gap alone — the nose presses the moment it reaches the steel, the grip opens on
   contact, and the tee stops there while the tube draws out of it. The tee is the only body
   that moves: the tube stub flexes inside the two collets that hold it, and the valve on its
   far end stands where it was seated. That the stub bends is stated and not derived — no body
   in the model has compliance in it, and `check_release_travel` is where the premise is marked. `check_insertion_backing` reads the other direction: a
   tube pushed into a branch collet drives its tee aft, and the step in the wall's own bore
   takes the collar, so a joint seats to depth instead of shoving the tee out of the tube's
   path. Steps 2 and 5 run on the two of them.

## Sources
[value](NAME) texts are updated by:
- `/hardware/service/_pump_replacement_sync.py`
