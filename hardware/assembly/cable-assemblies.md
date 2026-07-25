# Cable assemblies

The bench-fabrication procedure for the appliance's internal low-voltage harnesses. Every cable assembly is **built complete and tested off the chassis**, then landed during [`wiring.md`](/hardware/assembly/wiring.md). This doc is the *fabrication* view (cut, terminate, sleeve, test); `wiring.md` is the *install* view (route, land, strain-relieve).

## Why pre-built, tested assemblies

The appliance ships sealed and is **not field-serviced** — a fault returns the whole unit, and the repair is to swap the affected cable assembly for a freshly-built, tested one, never to trace and re-crimp a single conductor (if one termination failed, the assembly is suspect end-to-end). Two consequences drive every choice below:

- **Cut-to-length, not pre-crimped.** Every run length is layout-specific and only grows as the enclosure settles, so each conductor is cut from a bulk spool and terminated at build — pre-crimped fixed-length leads would be scrap. Pre-crimped XH pigtails survive only for short module-to-module hops where ±length doesn't matter.
- **All-black wire.** Per-conductor color is a field-tech's fault-tracing aid, which this model never uses: the build is jig-and-test, the repair is replace-the-assembly, and the conductors are splayed during crimping where color does nothing. All-black also matches the appliance's monochrome language (PETG, PCB, John Guest fittings, LLDPE). **Exception — AC mains:** black hot / white neutral / green ground, a safety/code convention (not a service aid) for the line-voltage runs, and hidden inside the black sleeve anyway.

## Scope

In: the cut list (lengths + terminations) from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Run table"; the assembly endpoints (board connectors J1–J11 + J13) from [`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx); bulk wire, sleeve, ferrules, terminals, and Wago lever nuts from [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11.

Out: a set of labelled, continuity-tested cable assemblies, ready to land per [`wiring.md`](/hardware/assembly/wiring.md).

Not in scope: routing, strain-relief, and landing into the chassis ([`wiring.md`](/hardware/assembly/wiring.md)); the AC mains in-place runs; firmware.

## Stock & tooling

Wire is bulk silicone, 600 V, cut-to-length, all per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11: **22 AWG black** (the manifold trunks, valve branches, low-power DC, and every signal / reed / sensor run — the workhorse), **16 AWG 5-color** (AC mains + branches + 12 V trunk + green ground). A manifold trunk is a bundle of cut 22 AWG conductors carried in braided sleeve, not a multiconductor cable: the trunk's conductor count is its board connector's, and the sleeve column below sizes the bundle. Jacketed runs are only the two that leave the cabinet or the shroud: the BNTECHGO 28 AWG 4-conductor ribbon (faucet umbilical) and the GEARit 18 AWG SJOOW 3-conductor lead (shroud pass-through).

Terminations: insulated bootlace ferrules (Preciva kit) into the Wago 221 lever nuts + screw terminals; female Faston disconnects (6.3 mm / 4.8 mm) at valves, motors, compressor, and fan; ring terminals to the ground bus + shroud stud; JST-XH housings at the board's labeled wafers — every loom XH, J7 (REEDS B) included. J7 and J4 (SENSORS) share the same 7P housing, so **label both looms at the housing** and dress them to their own edges: a swapped pair would put J4's 3V3/5V on J7's MCP reed inputs. Distribution / fan-out: Wago 221 lever nuts — **221-413** (AC mains H/N/G), **221-415** (≤5-conductor fan-outs, incl. MANIFOLD B COM), **221-420** (the >5-conductor MANIFOLD A COM + reservoir-B reed GND).

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

Conductor counts are the board connector pin counts (`pcba.tsx` J1–J11 = {[9](J1_PINS), [6](J2_PINS), [4](J3_PINS), [7](J4_PINS), [4](J5_PINS), [5](J6_PINS), [7](J7_PINS), [4](J8_PINS), [4](J9_PINS), [2](J10_PINS), [4](J11_PINS)}, J13 = [4](J13_PINS); there is no J12, and J14 is the USB programming port — no loom). The fan-out to the 11 valves (10 manifold + V-K) / many reeds happens **at the device end**, downstream of the connector — so each trunk carries its connector's count, never the fanned-out total.

| Assembly | Board conn. | Conductors | Wire | Terminations | Sleeve |
|---|---|---|---|---|---|
| Manifold A | J1 | [9](J1_PINS) (8 OUT + COM) | 22 AWG black | Fastons at 8 valves; COM → **221-420** fan-out at the manifold | 3/4" |
| Manifold B | J2 | 5 of [6](J2_PINS) (2 OUT + FAN + COM + OUT3) | 22 AWG black | **XHP-6 housing, contact 3 (`OUT4`) left empty** — see below; Fastons at 2 valves + fan; V-K's `OUT3` + a `COM` tap branch off to the aft strip (DC-9); COM → **221-415** | 1/2" |
| Reservoir A reeds | J6 | [5](J6_PINS) (4 reed + GND) | 22 AWG black | reed leads; GND → **221-415** at the reservoir | 1/4" |
| Reservoir B + carb reeds | J7 | [7](J7_PINS) (6 reed + GND) | 22 AWG black | reed leads; female JST-XH housing (XHP-7) + XH contacts — the same 7P housing as SENSORS (J4), so **label both looms at the housing** (a swap would put J4's 3V3/5V on the MCP reed inputs); GND → **221-420** | 1/4" |
| Sensors | J4 | [7](J4_PINS) | 22 AWG black | DS18B20 / flow / moisture (DO + switched VCC); GND → **221-415** near the shelf | 1/4" |
| Relays | J5 | [4](J5_PINS) (`IO19` / `IO2` / `V5` / GND) | 22 AWG black | XH at J5; screw terminals at both relay modules, `V5`/GND teed to both at the relay end (LV-1/2/3 — lands on-shelf at [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md)) | 1/4" |
| Faucet display | J3 / SIG-6 | [4](J3_PINS) (TX / RX / 5 V / GND) | 28 AWG ribbon | TTL UART up the umbilical; **the TTL lines are ESD-clamped on the board at U1** (D10/D11, 2× low-cap TVS — see the ESD note below); a faucet-end TVS is now optional | jacketed ribbon |
| Config display | J9 / SIG-7 | [4](J9_PINS) (`B` / `A` / GND / `V12`) | 22 AWG black | A/B pair to the 4.3B's RS485 terminals; `V12` + GND to its 7–36 V screw input on the same loom | 1/2" |
| Gas sensor | J11 | [4](J11_PINS) (GND / `V5` / `DOUT` / `AOUT`) | 22 AWG black | MQ-6 leads | 1/4" |
| Cap-sense | J8 / SIG-8 | [4](J8_PINS) (GND / `3V3` / `SDA` / `SCL`) | 22 AWG black | MPR121 header at the manifold | 1/4" |
| Pumps | J13 / DC-5 | [4](J13_PINS) (`AM2` / `AM1` / `BM2` / `BM1`) | 22 AWG black | female Faston receptacles onto the pump-motor spade tabs | 1/2" |
| 12 V input | J10 / DC-4 | [2](J10_PINS) (`V12` / GND) | 16 AWG | ferrules under the J10 screw clamps; from the shelf's 12 V distribution block (lands on-shelf at [`electronics-shelf.md`](/hardware/assembly/electronics-shelf.md)) | — |
| AC mains | AC-1…6 | per run | 16 AWG (black/white/green) + 18 AWG SJOOW | ferrules → **221-413**; Fastons at compressor; rings to ground | SJOOW jacket on the shroud lead |

### MANIFOLD B — the empty contact

J2 is the one loom whose housing is wider than its conductor count. The board's wafer is [6](J2_PINS)-way, labelled from contact 1 `COM`, `FAN`, `OUT4`, `OUT3`, `OUT2`, `OUT1` ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx)) — and `OUT4` drives no valve. It is a fully-routed spare channel, so the harness crimps **five contacts into an XHP-6 and leaves contact 3 empty**.

**Contact 3 is in the middle of the housing, not on an end.** Crimp the five in their labelled positions and skip the third; do not close the gap. A loom that fills contacts 1–5 consecutively lands every conductor one position off — `FAN` on `OUT4`, `COM` on `FAN` — which puts the shared 12 V rail on a driver output. The empty cavity is the guard, so leave it empty and verify it at the step-5 continuity test.

## Faucet-display ESD protection (SIG-6)

The faucet flavor LCD is the one user-touched surface at the far end of a ~1 m umbilical, so its
TTL UART pins are the board's most exposed ESD path. The **primary** clamp is now **on the board, at
the ESP32** — so no cable-assembly step is required for ESD; the faucet-end TVS drops to an optional
belt-and-braces extra. The protection is:

- **On the board (primary — required, already placed):** each faucet TTL line is clamped at U1 by a
  low-capacitance TVS shunting the U1-side of its series resistor to the GND plane — **D10 on IO33
  (TX) and D11 on IO35 (RX)**, onsemi **ESD9B3.3ST5G** (SOD-923, 3.3 V working / bidirectional,
  ~15 pF, LCSC C96512). Each sits after its series resistor (topology: J3 → 220 Ω → clamp-at-the-IC →
  U1), with the shunt riding a **via-in-pad straight to the GND plane** — the shortest possible loop,
  which is what sets clamp effectiveness. A strike arriving up the ribbon is current-limited by the
  220 Ω and clamped to ~3.3 V at the ESP32 pin. See `pcb/pcba/jlcpcb-parts.md` (D10/D11) and
  `pcb/pcba/pcba.tsx` (FAUCET block). This mirrors the RS485 side, where D1 (SM712) clamps the A/B
  pair at J9.
- **At the driver end (series backstop — already on the board):** R26 (IO33) and R27 (IO35), ~220 Ω
  0402 in series in each line, give series damping on the long-cable edges and set the current limit
  that lets the on-board clamp do its job. They are the series element of the clamp topology, not a
  standalone protection.
- **At the faucet-display end (optional — NOT required):** because the board now clamps the ESP32
  pin, a cable-end TVS is no longer needed. If a builder wants defense-in-depth at the user-touch
  source, the same low-cap part class works: **2× ESD9B3.3-class / PESD3V3-class, ≤ 15 pF, SOD-923**
  (e.g. onsemi ESD9B3.3ST5G or Nexperia PESD3V3L1BA), one from each TTL line to the faucet-side GND on
  the last ~10 mm of ribbon, shortest loop. This is a build-time option, not a build requirement.

The 5 V and GND ribbon conductors need no clamp (5 V is a rail, GND is the return); only the two TTL
signals are protected.

## Open items

1. **Shielded reed pairs.** The ~600 mm reed / 1-wire runs pass alongside the switching solenoid trunk; consider shielded twisted pair (foil + drain, single-end grounded) over plain 22 AWG.
2. **AC mains wire grade.** Confirm the line-voltage runs use a recognized appliance-grade wire (UL1015 / UL1028, 600 V, 105 °C) rather than hobby silicone — the discipline already applied to the SJOOW shroud lead.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_cable_assemblies_sync.py`
