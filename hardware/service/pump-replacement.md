# Pump replacement

The BPT tube around each Kamoer KPHM400's rotor is a consumable and a pump is replaced as a unit.
This procedure runs on the access the factory bench uses: `enclosure-front-top` comes off, and the
whole flavor manifold comes off with it.

Every joint that parts is a flavor line. No joint on the water, CO2 or carbonated-water path is
opened — every body on those three paths stands aft of the seam or on the cold core's own lid — so
the carbonator stays full, stays under pressure, and stays connected.

The appliance runs **dry mode** first: a firmware cycle that fills the manifold with air. Air enters
at the hopper funnel and both reservoir cap vents; what it displaces leaves at the faucet's
gooseneck tip. The user's part is a vessel under the faucet.

## What the quadrant carries

| Rides up with `enclosure-front-top` | Stays |
|---|---|
| [8](LIFT_VALVES) valves — V-C…V-J, on the two printed panels ([`valve-panel/`](/hardware/printed-parts/enclosure/valve-panel/README.md)) | [3](CAP_VALVES) valves — V-A, V-B, V-K, in the cold core's lid cradles (`_cold_core_interface.cap_cradles`) |
| Both Kamoer pumps, in their printed trays ([`pump-tray/`](/hardware/printed-parts/enclosure/pump-tray/README.md)) | The SeaFlo and both its chains, on the core's cap |
| All [6](LIFT_TEES) PP0208E tees — each butts a valve that rides | The ASSE chain, the water split, the flow regulator, the WR1110, the DIGITEN meter |
| Every hairpin, turn and butted stub inside the pack | Every rear-wall bulkhead, and the cold core itself |
| The display housing | The hopper funnel — lifted out first, step 2 |

**The manifold comes out as one body.** No tube inside the pack crosses the seam: the four
[180° hairpins](/hardware/manifold-layout/README.md), the two source turns and every butted collet
join bodies on the same side of it. Break the [8](JOINT_COUNT_4) joints below and the pack — valves, tees, pumps,
tube — lifts on the ceiling.

## The [8](JOINT_COUNT_3) joints that part

Derived at every build from `manifold_layout.SEGMENTS` and `manifold_layout.MOUTHS` against
`_scorecard.fastened_by`. A valve that changes seat changes this table, and
`_pump_replacement_sync.py` fails rather than letting it drift.

| Joint | Lifting end | Staying end | Tube | Air-filled by |
|---|---|---|---|---|
| `fluid-5` | Y-B-1 | V-B-O | [51.8](LEN_5) mm | every state — it is the air inlet |
| `fluid-14` | V-F-O | reservoir A fill conduit | [369.4](LEN_14) mm | state 1 |
| `fluid-24` | V-I-O | reservoir B fill conduit | [183.3](LEN_24) mm | state 3 |
| `fluid-18` | V-G-O | `bulkhead-flavor-a` | [450.5](LEN_18) mm | state 2 |
| `fluid-28` | V-J-O | `bulkhead-flavor-b` | [331.5](LEN_28) mm | state 4 |
| `fluid-16` | V-E-I | reservoir A draw conduit | [123.2](LEN_16) mm | no state — comes apart wet |
| `fluid-26` | V-H-I | reservoir B draw conduit | [123.2](LEN_26) mm | no state — comes apart wet |
| `fluid-3` | Y-A-1 | V-A-O | [51.9](LEN_3) mm | no state — comes apart wet |

**`fluid-3` holds tap water.** Its supply side runs V-A → `fluid-2` → flow regulator → `fluid-1` →
water split → `water-2` → ASSE 1022 → rear bulkhead → the customer's stop, a closed column at house
pressure with no atmospheric opening on it, so opening V-A admits water. The run crests at
[281.3](SOURCE_CREST) mm between its two ends: broken at the tee it drains its descending leg out
and its ascending leg back onto V-A's closed seat, which stays with the core.

**The two draw lines hold syrup.** Each runs from the bulkhead in its reservoir's trough, under the
liquid, up the cap conduit to its valve — so the air a purge could push into one has to reach a port
with concentrate standing on it. The published `Air Purge Out` states reach it by running the
reservoir dry through the nozzle.

**A reservoir does not siphon when its draw line is broken.** `fluid-16` and `fluid-26` crest at
[281.3](DRAW_CREST) mm on the way to their valves and the cold core's crown is
[268.6](CORE_CROWN) mm, so the crest stands [12.7](SIPHON_MARGIN) mm over the highest point liquid
inside the core reaches. A draw line is broken at the valve end whatever the reservoir holds, and
what comes out is the descending leg.

## Dry mode

Four states in order, both pumps forward, every valve inlet to outlet.

| # | Open | Pump | Path |
|---|---|---|---|
| 1 | V-B, V-C, V-F | A | hopper → crossbar → V-C → hairpin `fluid-9` → Y-C → **pump A** → Y-D → V-F → `fluid-14` → reservoir A |
| 2 | V-B, V-C, V-G | A | same head, then Y-D → hairpin `fluid-17` → V-G → `fluid-18` → out the tip |
| 3 | V-B, V-D, V-I | B | mirror of 1, into reservoir B |
| 4 | V-B, V-D, V-J | B | mirror of 2, out the tip |

States 2 and 4 are the ones that carry air to a nozzle without drawing on a reservoir, so a pump
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

**1. Run dry mode.** Vessel under the faucet — states 2 and 4 send a slug of air and residual syrup
out the gooseneck.

**2. Lift the hopper funnel out.** Its throat is cut through the top wall of both top pieces
(`enclosure._hopper_cut`), so the basin clears before the seam parts. Thumb the union's collet off
the stub and the basin lifts away with its stub and clamp still on it. `fluid-4` stays on V-B, dry —
it is the cycle's own air inlet.

**3. Break the [8](JOINT_COUNT_5) joints.** Press each collet ring and draw the tube out. Pull **`fluid-18` and
`fluid-28` at the bulkheads**, not at V-G and V-J, so the two longest runs ride up with the quadrant
instead of dangling; the rest release at whichever end reaches. Cloth under `fluid-3`, `fluid-16`
and `fluid-26`.

**4. Lift the quadrant.** Set it panels-down on the bench.

**5. Swap the pumps.** Cut the two 8" straps under each pump's stamped mounting bracket and lift the
boss out of its [53 mm](PUMP_SOCKET) octagon bore — no tool, no fastener. Pull the DC-5 spade pairs
off the motor tabs. The new pump goes in the same way: straps threaded through the plate's four
channels and left lying open **first**, then the boss lowered until the plate lands on the head's
crown all the way round, then each strap closed round plate and bracket together and flush-cut.
Cinch on **the bracket only** — never a barb, never the motor can. Tug-test each.

**6. Route 1/4" OD LLDPE through the new heads** — onto the BPT barbs directly, around the rotor,
zip-tied tight.

**7. Reassemble.** Quadrant down, all [8](JOINT_COUNT_7) joints pushed fully home and tug-tested, funnel back in its
throat and its union onto the stub.

**8. Re-prime.** Both channels through the hopper-fill path, then a dispense on each until it runs
clean.

## Output condition

- Both pumps replaced, each hanging on two straps under its own bracket, tug-tested
- All [8](JOINT_COUNT_6) joints remade and tug-tested; funnel reseated
- Both channels re-primed and dispensing clean
- No joint on the water, CO2 or carbonated-water path opened; the carbonator never depressurised

## Open items

1. **Whether the Beduan passes flow outlet to inlet is unknown.**
   [`fluid-topology.md`](/hardware/topology/fluid-topology.md) states the manifold's valves as
   inlet-to-outlet only, and nothing in the tree says whether the B07NWCQJK9 is direct-acting or
   pilot-operated. A direct-acting seat energised at low differential passes either way; a pilot
   needs forward differential to lift at all. Settling it opens a reverse loop for the two draw
   lines — headspace out the fill bore, backwards across the pump, in at the draw port under the
   liquid, syrup returned to its own reservoir and the cap's PTFE vent carrying the imbalance — which
   would take those two joints dry without spending concentrate. A bench reading on one valve
   answers it, and a second reading answers whether the pump pushes air down a filled draw column
   against its standing head or churns at the interface.
2. **The reel's bore is not in this tree.** Every figure here is a tube length; `_routing.STOCKS`
   carries 1/4" LLDPE's [6.35 mm](TUBE_OD) OD and the bend floor, and no ID. At a nominal 0.170"
   the [8](JOINT_COUNT_2) joints come to [25](JOINT_ML) mL between them and `fluid-3` to
   [0.8](WET_ML) mL — arithmetic on `_pump_replacement_sync.NOMINAL_BORE` rather than a reading.
   Measure a reel and these become volumes.
3. **Dry-run wear on a KPHM400's BPT tube is not characterised.** States 1, 2, 4 and 5 turn both
   rotors on air.
4. **A customer-facing transit mode is not written.** This procedure leaves the carbonator charged.
   The carbonator's only liquid outlet climbs to the faucet, and the factory's transit sequence is
   [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md) step 13.

## Sources
[value](NAME) texts are updated by:
- `/hardware/service/_pump_replacement_sync.py`
