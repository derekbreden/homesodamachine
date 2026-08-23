# Fill from the funnel — Snapshot 2026-08-19

**This is a point-in-time snapshot, not a living document.** It captures the plan committed to
on the eve of the first operation the appliance performs on valves. The pump prime is the only
actuator the front glass drives today; both MCP23017s are untouched, the eleven valves and the
condenser fan stand high-Z, no reed is read, and a clean cycle is answered `MSG_ERR_UNSUPPORTED`
([`/firmware/README.md`](/firmware/README.md)).

The operation: a customer lifts the silicone funnel's bottle-sized mouth, empties a 440 mL
SodaStream concentrate bottle into it in one pour, and the machine draws it down into one of the
two flavour reservoirs. `Fill from the funnel → Reservoir A` opens V-B, V-C and V-F with pump A
running ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md)); the
funnel is shared and the manifold picks the channel
([`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md)).

## What the operation runs into

**A valve state does not name an operation.** In the canonical table, `Dispense A` and
`Clean Flush A` are both V-E + V-G with pump A on — the table says so itself — and
`Fill from the funnel → A` and `Air Purge In → Reservoir A` are both V-B + V-C + V-F with pump A
on. What separates each pair is what is in the reservoir, or whether the funnel holds anything: facts
the machine has no way to read. The display renders from an intent the firmware holds, and an
intent lost to a reset cannot be recovered from the valves. `/hardware/battery-backup/` makes
mid-cycle interruption a designed-for case.

The same fact reaches `/hardware/service/pump-replacement.md` step 1. All four Air Purge states
are canonical and individually specified; what is absent is the thing that holds intent across
them.

**One bottle is not one fill, and the machine cannot see the funnel empty.** Each reservoir
carries four reeds at ~45 mm pitch over ~170 mm of float travel, read as a five-state gauge —
empty, quarter, half, three-quarter, full — each step ≈ 13 servings
([`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)).
A serving draws ~12.5 mL of concentrate, from the ~262.5 mL metered dispense at 1:20
([`/hardware/assembly/acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md)),
so a reed step is ~162 mL and a 440 mL bottle is about two and a half of them. It neither fills an
empty reservoir nor lands on a level. The top reed asserting is the one end condition the machine
can detect; nothing senses the funnel.

## The bench rig — Derek

What has to exist in the world before the firmware below can be run. The level chain and the fluid
path come up separately, and the level chain is the one that gates firmware: what the fill needs
to see is four reeds asserting in order as a magnet rises. That rig is dry — no water, no syrup,
no cap, no bulkhead, no funnel.

Everything below is on hand except where marked.

### The dry rig

**1. J1 MANIFOLD A harness.** JST XH 2.54 mm 9-pin housing (`COM` + `OUT1`–`OUT8`), board end,
crimped on the iCrimp SN-2549's XH nest. The fill uses `COM`, `OUT2`, `OUT3` and `OUT6` — V-B,
V-C and V-F respectively, per [`valve-control.mmd`](/hardware/wiring/valve-control.mmd) — and the
housing takes all nine whenever the rest get populated. Valve end: female spade disconnects.
`COM` explodes into a WAGO 221-420 so every coil shares the 12 V. Run DC-6 in
[`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md), which carries the live figures.

**2. Three Beduan 12 V 1/4" NC solenoids** off the stack of 13, labelled V-B, V-C, V-F. Each
coil's `+` to the `COM` Wago, `−` to its own `OUT` conductor — low-side switching, so `COM` is the
only conductor shared across valves. They click dry.

**3. J6 REEDS A harness.** JST XH 2.54 mm 5-pin housing (`GND` + `RA1`–`RA4`), board end, landing
on MCP23017 0x20 PB0–3. `GND` explodes into a WAGO 221-415 at the reservoir end. No resistor
anywhere in it — every reed rides the expander's internal pull-up. Run SIG-10 in
[`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md).

**4. The reed column.** Four Gebildet 14 mm NO reeds, each standing with its glass envelope
**vertical**, both leads soldered to its own signal conductor and to the shared common, laced with
heat-shrink between reeds into one stiff pre-assembled piece. ~45 mm pitch. **Six reeds are on
hand and four go here** — four short of the 10 a whole machine takes, so worth reordering on the
next run.

**5. A float on a rod.** One YXQ 45 mm float switch off the stack of four, torn down for the
commodity ⌀27.75 mm crimped SS donut; 1/8" 316L rod off the Tandefio pack, cut square on the WEN
band saw. The donut rides within ~2 mm of the wall the reeds stand behind: it trips at ~2 mm and
gives nothing by ~3 mm.

**6. A reservoir to hold the rod.** The printed body from attempt 3 serves, ahead of its own
watertight qualification. It carries the rod standing in it, and the reed column held against its
outer wall at the pitch above, with the float raised and lowered by hand.

### The wet rig, when it comes

**7.** 1/4" LLDPE off the 100 ft roll; a bulkhead into the reservoir (neoFit ABU44-E, or one of
the two JG PI1208S on hand) with its silicone face washer; the Kamoer already wired for prime;
and anything standing in for it — **the silicone funnel is not cast yet.**

## Firmware and decisions — mine

What I am building, for review rather than approval.

**1. The operation state machine, before any valve is driven.** What operation is running, on
which channel, which step within it, what ends it, what aborts it, and what a reset mid-cycle
leaves behind. The valve table is the actuator layer under it.

**2. Both MCP23017s up** — `IODIR` and `GPPU` on each. No loom carries a resistor, so a reed with
its pull-up unwritten floats. Bring-up turns the pull-up off and confirms the reading goes wrong,
then turns it back on.

**3. The fill is metered, with the top reed as the hard stop.** A peristaltic pump is volumetric
and the bottle is a known 440 mL — the same property that already meters the 1:20 dispense. The
fill runs the bottle's volume plus a margin of air, and the top reed asserting ends it early
whatever the count says.

**4. The customer names the flavour, not the channel.** The glass asks which flavour is about to
be poured and says it back in the flavour's own name. Whether the shared V-B path wants a flush
between flavours goes to the topology doc.

**5. Canonical states are what the glass selects, and a fourth coil refuses.** Eight coils on
MANIFOLD A draw 2.4–3.7 A through J1's `COM` at ~3 A and dissipate it in one SOIC-18 — the
solenoid COM current budget in
[`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md). Every canonical state opens at
most three. The commissioning screen
[`/hardware/assembly/firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md)
§9 needs is where a state gets composed by hand. `refuse` is already in the sound table, unused.

**6. Read a reed end to end** and render the five-state gauge from it.

**7. The fill's own surface.** Progress is the level rising — the same move as the prime hold's
rising pitch. The end is detected, not elapsed. A reservoir already full refuses.

**8. The dry-mode sequencer**, which falls out of item 1. It reaches step 1 of
[`/hardware/service/pump-replacement.md`](/hardware/service/pump-replacement.md), the procedure
the pump cartridge exists to serve.

**9. `/hardware/design-pressures.md` lists field service under Not optimised** and says the pump
swap runs on the bench's own access "rather than on anything placed for it." The pump cartridge is the
thing placed for it. That document is upstream of what gets built next.

**10. The diff-scoped prose guard.** When a commit deletes a definition, check whether anything
still names it, over comments and docstrings inside `.py` as well as `.md`.

## Not in scope here

The pour. Turn the handle and soda comes out; the faucet head's display carries the flavour and
its toggle, and the front glass is not in it.

Unrelated to this operation and unchanged: the build-sequence decision at
[`/hardware/assembly/enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) open
item 4, which wants a stated motion per body; and the carbonator, whose four open items and
the new coil's charge mass all resolve by making one. Every tool for that is ACQUIRED and nothing
has been made.
