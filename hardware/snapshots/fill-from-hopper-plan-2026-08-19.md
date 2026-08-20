# Fill from hopper — Snapshot 2026-08-19

**This is a point-in-time snapshot, not a living document.** It captures the plan committed to
on the eve of the first operation the appliance performs on valves. The pump prime is the only
actuator the front glass drives today; both MCP23017s are untouched, the eleven valves and the
condenser fan stand high-Z, no reed is read, and a clean cycle is answered `MSG_ERR_UNSUPPORTED`
([`/firmware/README.md`](/firmware/README.md)). The work spans firmware, the fluid topology and
the reservoir's level column, so it is written in one place rather than split across their docs.

The operation: a customer lifts the silicone funnel's bottle-sized mouth, empties a 440 mL
SodaStream concentrate bottle into it in one pour, and the machine draws it down into one of the
two flavour reservoirs. `Fill from Hopper → Reservoir A` opens V-B, V-C and V-F with pump A
running ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)); the
funnel is shared and the manifold picks the channel
([`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md)).

## Two facts that shape it

**A valve state does not name an operation.** In the canonical table, `Dispense A` and
`Clean Flush A` are both V-E + V-G with pump A on — the table says so itself — and
`Fill from Hopper → A` and `Air Purge In → Reservoir A` are both V-B + V-C + V-F with pump A on.
What separates each pair is what is in the reservoir, or whether the hopper holds anything:
facts the machine has no way to read. So the machine cannot report what it is doing by looking
at itself, the display renders from an intent the firmware holds, and an intent lost to a reset
cannot be recovered from the valves. `/hardware/battery-backup/` makes mid-cycle interruption a
designed-for case.

The same fact is why `/hardware/service/pump-replacement.md` step 1 cannot be performed. All four
Air Purge states are canonical and individually specified; what is absent is the thing that holds
intent across them.

**One bottle is not one fill, and the machine cannot see the funnel empty.** Each reservoir
carries four reeds at ~45 mm pitch over ~170 mm of float travel, read as a five-state gauge —
empty, quarter, half, three-quarter, full — each step ≈ 13 servings
([`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)).
A serving draws ~12.5 mL of concentrate, from the ~262.5 mL metered dispense at 1:20
([`/hardware/assembly/acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md)),
so a reed step is ~162 mL and a 440 mL bottle is about two and a half of them. It neither fills
an empty reservoir nor lands on a level.

The only end condition the machine can detect is the top reed asserting. Nothing senses the
funnel, so *the pour has run out* is not a reading. What ends a fill is open below.

## Derek

**1. Pick the fill's end condition.** Four ways, and they differ in what ships:

- run until the top reed asserts or a ceiling elapses, and accept concentrate left standing in
  the funnel
- have the customer confirm the funnel is visibly empty, which they can see and the machine
  cannot
- meter it — a peristaltic pump is volumetric, the bottle is a known 440 mL, so pump that plus a
  margin and then air. The same property already meters the 1:20 dispense
- sense the hopper gate, which is a hardware change

**2. How the channel is chosen, and what stops it being chosen wrong.** One funnel serves both
reservoirs and the manifold picks. A customer who pours Diet Mountain Dew and answers B puts it
in the Diet Pepsi reservoir, and nothing in the machine prevents that or detects it afterwards.
Whether the shared V-B path wants a flush between flavours is the same question.

**3. How far the bench rig goes.** Whether a solenoid and a reed-and-magnet get wired to the
board on the bench, unplumbed, so the operation can be exercised by hand before any fluid exists.

**4. The customer's word for it.** What the glass calls this operation propagates into the
display, the sound and the quick-start sheet.

**5. The build-sequence decision, which is unrelated to this and still the only thing blocking a
unit.** [`/hardware/assembly/enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md)
open item 4: when `enclosure-back-top` closes, whether internal plumbing and wiring run before or
after it, and the motion that assembles the flavour pack. No gate reads it and none can until a
motion per body is stated.

**6. Weld a coupon, then a vessel meant to be destroyed.** Four open items on
[`/hardware/assembly/pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) — weld recipe
validation, hydro pass/fail, weld inspection criteria, the re-weld-vs-scrap tree — and the
refrigerant charge mass for the new coil all resolve the same way. Every tool is ACQUIRED and
nothing has been made.

## Agents

**1. The operation state machine, before any valve is driven.** What operation is running, on
which channel, which step within it, what ends it, what aborts it, and what a reset mid-cycle
leaves behind. The valve table is the actuator layer under it, not the state.

**2. Bring up both MCP23017s** — `IODIR` and `GPPU` on each. No loom carries a resistor and the
board pulls none of the reed inputs, so every reed reads its expander's internal pull-up or
floats. Prove it by turning the pull-up off and confirming the reading goes wrong: a check that
does not fail when it is broken is decoration.

**3. Make the three-valve ceiling unreachable rather than checked.** Eight coils on MANIFOLD A
draw 2.4–3.7 A through J1's `COM` at ~3 A and dissipate it in one SOIC-18. Every canonical state
opens at most three, so the table is already safe; the exposure is a commissioning screen that
composes a state by hand, which
[`/hardware/assembly/firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md)
§9 needs. Canonical states are what the glass selects. A fourth coil refuses, and `refuse` is
already in the sound table, unused.

**4. Read a reed, end to end**, and render the five-state gauge from it.

**5. The fill's own surface.** Progress is the level rising, which is a reading, not a spinner or
a timer — the same move as the prime hold's rising pitch. The end is detected, not elapsed. A
reservoir already full refuses.

**6. The dry-mode sequencer**, which falls out of item 1. It unblocks step 1 of
[`/hardware/service/pump-replacement.md`](/hardware/service/pump-replacement.md), the procedure
the pump cartridge exists to serve.

**7. `/hardware/design-pressures.md` lists field service under Not optimised** and says the pump
swap runs on the bench's own access "rather than on anything placed for it." The cartridge is the
thing placed for it. That document is upstream of what gets built next and the next call in that
region is made against it.

**8. The diff-scoped prose guard.** When a commit deletes a definition, check whether anything
still names it, over comments and docstrings inside `.py` as well as `.md`. A whole-tree version
needs an allowlist and an allowlist rots.

## Not in scope here

The pour. Turn the handle and soda comes out; the faucet head's display carries the flavour and
its toggle, and the front glass is not in it.
