# Cable assemblies

The bench-fabrication procedure for the appliance's internal low-voltage harnesses. Every cable assembly is **built complete and tested off the chassis**, then landed during [`wiring.md`](/hardware/assembly/wiring.md). This doc is the *fabrication* view (cut, terminate, sleeve, test); `wiring.md` is the *install* view (route, land, strain-relieve).

## Why pre-built, tested assemblies

The appliance ships sealed and is **not field-serviced** — a fault returns the whole unit, and the repair is to swap the affected cable assembly for a freshly-built, tested one, never to trace and re-crimp a single conductor (if one termination failed, the assembly is suspect end-to-end). Two consequences drive every choice below:

- **Cut-to-length, not pre-crimped.** Every run length is layout-specific and only grows as the enclosure settles, so each conductor is cut from a bulk spool and terminated at build — pre-crimped fixed-length leads would be scrap. Pre-crimped XH pigtails survive only for short module-to-module hops where ±length doesn't matter.
- **All-black wire.** Per-conductor color is a field-tech's fault-tracing aid, which this model never uses: the build is jig-and-test, the repair is replace-the-assembly, and the conductors are splayed during crimping where color does nothing. All-black also matches the appliance's monochrome language (PETG, PCB, John Guest fittings, LLDPE). **Exception — AC mains:** black hot / white neutral / green ground, a safety/code convention (not a service aid) for the line-voltage runs, and hidden inside the black sleeve anyway.

## Scope

In: the cut list (lengths + terminations) from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Run table"; the assembly endpoints (board connectors J1–J11) from [`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx); bulk wire, sleeve, ferrules, terminals, and Wago lever nuts from [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11.

Out: a set of labelled, continuity-tested cable assemblies, ready to land per [`wiring.md`](/hardware/assembly/wiring.md).

Not in scope: routing, strain-relief, and landing into the chassis ([`wiring.md`](/hardware/assembly/wiring.md)); the AC mains in-place runs; firmware.

## Stock & tooling

Wire is bulk silicone, 600 V, cut-to-length, all per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11: **22 AWG black** (valve branches, low-power DC, J4/J5 signal — the workhorse), **24 AWG black** (reeds, sensors), 18 AWG red/black (COM trunk + AC device branches; black used for DC), 16 AWG 5-color (AC mains + 12 V trunk + green ground). Jacketed runs: the KWANGIL 22 AWG UL2464 black multiconductor (manifold trunks), the BNTECHGO 28 AWG 4-conductor ribbon (faucet umbilical), and the GEARit 18 AWG SJOOW 3-conductor lead (shroud pass-through).

Terminations: insulated bootlace ferrules (Preciva kit) into the Wago 221 lever nuts + screw terminals; female Faston disconnects (6.3 mm / 4.8 mm) at valves, motors, compressor, and fan; ring terminals to the ground bus + shroud stud; JST-XH housings at module pin headers. Distribution / fan-out: Wago 221 lever nuts — **221-413** (AC mains H/N/G), **221-415** (≤5-conductor GND fan-outs), **221-420** (the >5-conductor manifold COM + reservoir-B reed GND).

Dress: **black PET braided sleeve** — 1/2" for most bundles, 3/4" for the manifold trunk, 1/4" for thin runs; every cut sleeve end finished with heat-shrink so it can't fray; black UV-nylon zip ties, **flush-cut** (no proud tail). Tools: ferrule crimper (Preciva 28–5), Faston/insulated-terminal crimper (Haisstronica 22–10), JST-XH crimper (iCrimp SN-2549), wire stripper (Klein 11063W), flush cutters, heat gun, multimeter — see [`/hardware/ledger/tools.md`](/hardware/ledger/tools.md).

## Procedure (per assembly)

For each cable assembly in the schedule below:

1. **Cut to length.** Pull each conductor from the bulk spool; cut to the run length from the AC wiring schedule plus a service loop. All-black except the AC mains trio.
2. **Strip & terminate.** Strip to the termination's barrel length and land each end: an insulated ferrule for a Wago/screw landing (correct barrel length, one conductor per ferrule unless a twin-entry ferrule is called for where two share one lever); a female Faston at a valve/motor tab; a ring at a ground stud; an XH pin into its housing. No solder splices on any field-serviceable branch.
3. **Fan-out / distribution.** Where a shared rail feeds many devices, land the feed and all branches in the assembly's Wago lever nut. The COM and GND fan-outs live at the **device-cluster end** of the assembly (manifold, reservoir) — you carry one rail wire out and explode it there, never run N parallel wires from the board.
4. **Sleeve & dress.** Slip the bundle into black braided sleeve sized to it; heat-shrink each cut end; comb the conductors parallel; flush-cut every zip tie.
5. **Test.** Continuity end-to-end, pin-to-pin against the schedule; confirm no short between adjacent conductors; on the manifold and reed assemblies verify the Wago commons exactly the intended pins. **Label the assembly by name, not per-conductor.**
6. **Bag & stage** for [`wiring.md`](/hardware/assembly/wiring.md).

## Assembly schedule

Conductor counts are the board connector pin counts (`pcba.tsx` J1–J11 = {9, 6, 4, 6, 9, 5, 7, 2, 3, 2, 4}). The fan-out to the 12 valves / many reeds happens **at the device end**, downstream of the connector — so each trunk carries its connector's count, never the fanned-out total.

| Assembly | Board conn. | Conductors | Wire | Terminations | Sleeve |
|---|---|---|---|---|---|
| Manifold A | J1 | 9 (8 OUT + COM) | jacketed KWANGIL | Fastons at 8 valves; COM → **221-420** fan-out at the manifold | 3/4" |
| Manifold B | J2 | 6 (4 OUT + FAN + COM) | jacketed KWANGIL | Fastons at 4 valves + fan; COM → **221-420** | 3/4" |
| Reservoir A reeds | J6 | 5 (4 reed + GND) | 24 AWG black | reed leads; GND → **221-415** at the reservoir | 1/4" |
| Reservoir B + carb reeds | J7 | 7 (6 reed + GND) | 24 AWG black | reed leads; GND → **221-420** | 1/4" |
| Sensors | J4 | 7 | 22 / 24 AWG black | DS18B20 / flow / moisture (DO + switched VCC); GND → **221-415** near the shelf | 1/4" |
| Driver | J5 | 9 | 22 AWG black | XH / screw to L298N + both relays; GND → **221-415** | 1/2" |
| Faucet display | J3 / SIG-6 | 4 (TX / RX / 5 V / GND) | 28 AWG ribbon | TTL UART up the umbilical | jacketed ribbon |
| Config display | J9 / SIG-7 | 3 (RS485 A / B / earth) | 22 AWG black | A/B to the 4.3B transceiver; display 12 V is a separate power run | 1/2" |
| Gas sensor | J11 | 4 (GND / V5 / AOUT / DOUT) | 24 AWG black | MQ-6 leads | 1/4" |
| 5 V / 12 V inputs | J8 / J10 | 2 each | 16 / 18 AWG | power feed-in to the board | — |
| AC mains | AC-1…6 | per run | 16 / 18 AWG (black/white/green) + SJOOW | ferrules → **221-413**; Fastons at compressor; rings to ground | SJOOW jacket on the shroud lead |

## Open items

1. **Manifold trunk cable.** The KWANGIL 22 AWG UL2464 is black and on-hand but 12-conductor (populate to 9 / 6) and unshielded — fine for valve power. Confirm whether to keep it depopulated or source a right-count jacketed cable.
2. **Shielded reed pairs.** The ~600 mm reed / 1-wire runs pass alongside the switching solenoid trunk; consider shielded twisted pair (foil + drain, single-end grounded) over plain 24 AWG.
3. **AC mains wire grade.** Confirm the line-voltage runs use a recognized appliance-grade wire (UL1015 / UL1028, 600 V, 105 °C) rather than hobby silicone — the discipline already applied to the SJOOW shroud lead.
## Sources

Run lengths + terminations: [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md). Stock: [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11, tooling [`/hardware/ledger/tools.md`](/hardware/ledger/tools.md). Install: [`/hardware/assembly/wiring.md`](/hardware/assembly/wiring.md).
