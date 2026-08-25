# Cable assemblies

The bench-fabrication procedure for the appliance's internal low-voltage harnesses. Every cable assembly is **built complete and tested off the chassis**, then landed during [`wiring.md`](/hardware/assembly/wiring.md). This doc is the *fabrication* view (cut, terminate, sleeve, test); `wiring.md` is the *install* view (route, land, strain-relieve).

## Why pre-built, tested assemblies

The appliance ships sealed and is **not field-serviced** — a fault returns the whole unit, and the repair is to swap the affected cable assembly for a freshly-built, tested one, never to trace and re-crimp a single conductor (if one termination failed, the assembly is suspect end-to-end). Two consequences drive every choice below:

- **Factory-crimped leads, cut once.** The machine is placed, so every run is measured rather than estimated ([`_run_lengths.py`](/hardware/wiring/_run_lengths.py)), and the longest conductor inside the enclosure is 582 mm — under twice the 305 mm JST sells a lead in. The board end is therefore not crimped at the bench: each conductor starts as an **ASXHSXH22K** lead, factory-crimped at both ends, and one cut turns it into a finished pigtail. A run past the catalogue breaks at a junction rather than reverting to a hand crimp. Bulk wire survives downstream of the lever nuts, where a branch has an XH end at neither end. See § XH contacts.
- **All-black wire.** Per-conductor color is a field-tech's fault-tracing aid, which this model never uses: the build is jig-and-test, the repair is replace-the-assembly, and the conductors are splayed during crimping where color does nothing. All-black also matches the appliance's monochrome language (PETG, PCB, John Guest fittings, LLDPE). **Exception — AC mains:** black hot / white neutral / green ground, a safety/code convention (not a service aid) for the line-voltage runs, and hidden inside the black sleeve anyway.

## Scope

In: the cut list (lengths + terminations) from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Run table"; the assembly endpoints (board connectors J1–J11 + J13) from [`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx); bulk wire, sleeve, ferrules, terminals, and Wago lever nuts from [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11.

Out: a set of labelled, continuity-tested cable assemblies, ready to land per [`wiring.md`](/hardware/assembly/wiring.md).

Not in scope: routing, strain-relief, and landing into the chassis ([`wiring.md`](/hardware/assembly/wiring.md)); the AC mains in-place runs; firmware.

## Stock & tooling

Every conductor that lands on a board wafer is a **JST ASXHSXH22K** lead — black 22 AWG, factory-crimped socket at both ends, bought at 305 and 254 mm (§ XH contacts). Bulk silicone, 600 V, cut-to-length covers what the leads do not, per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11: **22 AWG black** for the fan-out branches downstream of the lever nuts — a valve's COM leg, a reed's GND leg, XH at neither end — and **16 AWG 5-color** (AC mains + branches + 12 V trunk + green ground). A manifold trunk is a bundle of cut 22 AWG conductors carried in braided sleeve, not a multiconductor cable: the trunk's conductor count is its board connector's, and the sleeve column below sizes the bundle. Jacketed runs are only two: the BNTECHGO 28 AWG 4-conductor ribbon (faucet umbilical) and the GEARit 18 AWG SJOOW 3-conductor lead (power column to the compressor's factory-external electrical interface and terminal-box earth screw).

Terminations: insulated bootlace ferrules (Preciva kit) into the Wago 221 lever nuts + screw terminals; female Faston disconnects (6.3 mm / 4.8 mm) at valves, motors, and fan; the current Frigidaire donor's factory-external electrical interface is Open item 5 in [`wiring.md`](/hardware/assembly/wiring.md); ring terminals to the ground bus + the compressor's terminal-box earth screw; JST-XH housings at the main board's labeled wafers — every loom XH, J7 (REEDS B) included. J7 and J4 (SENSORS) share the same 7P housing, so **label both looms at the housing** and dress them to their own edges: a swapped pair would put J4's 3V3/5V on J7's MCP reed inputs. Distribution / fan-out: Wago 221 lever nuts — **221-413** (AC mains H/N/G), **221-415** (≤5-conductor fan-outs, incl. MANIFOLD B COM), **221-420** (the >5-conductor MANIFOLD A COM + reservoir-B reed GND).

Dress: **black PET braided sleeve** — 1/2" for most bundles, 3/4" for the manifold trunk, 1/4" for thin runs; every cut sleeve end finished with heat-shrink so it can't fray; black UV-nylon zip ties, **flush-cut** (no proud tail). Tools: ferrule crimper (Preciva 28–5), Faston/insulated-terminal crimper (Haisstronica 22–10), JST-XH crimper (iCrimp SN-2549), wire stripper (Klein 11063W), flush cutters, heat gun, multimeter — see [`/hardware/ledger/tools.md`](/hardware/ledger/tools.md).


### XH contacts

Every board-end termination inside the enclosure arrives already crimped. JST sells the -001T on
black 22 AWG as **ASXHSXH22K\***, socket-to-socket, in 51, 102, 152, 203, 254 and 305 mm — under a
dollar each at single quantity, and 305 mm is the whole catalogue.
[`_lead_cuts.py`](/hardware/wiring/_lead_cuts.py) reads the measured runs and emits both the buy and
the cut: **61 leads, about $54**, covering all 49 in-box conductors with no hand crimp on any of them.

Two properties of the lead shape the scheme, and both are easy to trip over:

- **A lead carries two crimps, and cutting destroys one.** So a lead yields at most two
  terminations, and that cap — not the copper — is what the order buys. About a fifth of the crimps
  in this order are orphaned, mostly on the 250–302 mm runs where a single pigtail consumes a whole
  lead. Recovering them costs more in connectors than the leads are worth.
- **Both ends are sockets, so two leads cannot be joined.** XH is a wire-to-board family: its only
  male part is a PCB header (`B*B-XH-A`, `S*B-XH-A`). A run longer than one lead therefore breaks at
  a **junction** — headers back to back on a carrier — and the board-side half has to be a lead
  nobody cut, which locks it to a catalogue length. Junctions land on catalogue distances, not at the
  middle of a run.

Twenty-four conductors break that way, in four clusters: the cold core (J6, J7 and J11, twelve
conductors between them), MANIFOLD B, the display, and the pumps. The break doubles as the quadrant
seam — the enclosure telescopes and cross-pins from the side faces, and a loom that parts at the
seam lets a quadrant come away without being unthreaded.

Twelve more conductors measure 304 to 323 mm against the 302 mm a cut lead yields. The routed factor
in `_run_lengths.py` is calibrated on a single point, so those are not meaningfully longer than the
pigtail; they are bought at 302 and give up their service loop (Open item 3).

The contact itself is **SXH-001T-P0.6** — conductor #28 to #22, insulation OD 0.9 to 1.9 mm, tin. It
is crimped by hand only for J3 and for rework. What holds a contact square in the die is a
**locator**, and no low-cost tool has one: the contact is placed by hand and held there. JST's own
hand tools do — **WC-110** (#22–#28, side entry) covers both gauges in this build. With a ratcheting
tool and no locator, close the ratchet one click onto the contact so it is captive, then feed the
wire. The umbilical's 28 AWG has a second contact option: **SXH-002T-P0.6** is the #30 to #26 part,
insulation OD 0.9 to 1.3 mm, and its barrel closes on 0.08 mm² near the middle of its range rather
than at the floor of the -001T's.

## Procedure (per assembly)

For each cable assembly in the schedule below:

1. **Cut to length.** For a conductor landing on a board wafer, take the lead [`_lead_cuts.py`](/hardware/wiring/_lead_cuts.py) names and make its single cut — the surviving factory crimp is the board end, and an uncut lead is one that spans to a junction. For a fan-out branch or an AC run, pull from the bulk spool and cut to the run length from the AC wiring schedule plus a service loop. All-black except the AC mains trio.
2. **Strip & terminate.** Strip to the termination's barrel length and land each end: an insulated ferrule for a Wago/screw landing (correct barrel length, one conductor per ferrule unless a twin-entry ferrule is called for where two share one lever); a female Faston at a valve/motor tab; a ring at a ground stud; an XH pin into its housing. No solder splices on any field-serviceable branch.
3. **Fan-out / distribution.** Where a shared rail feeds many devices, land the feed and all branches in the assembly's Wago lever nut. The COM and GND fan-outs live at the **device-cluster end** of the assembly (manifold, reservoir) — you carry one rail wire out and explode it there, never run N parallel wires from the main board. Each nut has a well printed into the side wall by its own cluster (`enclosure._side_wells`); press it butt-first into its well, ports and levers to the room. Every well stands clear enough of its neighbours that a seated lug's levers still swing fully up (`enclosure.wago_pitch`), so a conductor can be added or moved without pulling the lug. The stations are tabled in [`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Loom terminations".
4. **Sleeve & dress.** Slip the bundle into black braided sleeve sized to it; heat-shrink each cut end; comb the conductors parallel; flush-cut every zip tie.
5. **Test.** Continuity end-to-end, pin-to-pin against the schedule; confirm no short between adjacent conductors; on the manifold and reed assemblies verify the Wago commons exactly the intended pins. **Label the assembly by name, not per-conductor.**
6. **Bag & stage** for [`wiring.md`](/hardware/assembly/wiring.md).

## Assembly schedule

Conductor counts are the main board's connector pin counts (`pcba.tsx` J1–J11 = {[9](J1_PINS), [6](J2_PINS), [4](J3_PINS), [7](J4_PINS), [4](J5_PINS), [5](J6_PINS), [7](J7_PINS), [4](J8_PINS), [4](J9_PINS), [2](J10_PINS), [4](J11_PINS)}, J13 = [4](J13_PINS); there is no J12, and J14 is the USB programming port — no loom). The fan-out to the 11 valves (10 manifold + V-K) / many reeds happens **at the device end**, downstream of the connector — so each trunk carries its connector's count, never the fanned-out total.

| Assembly | Board conn. | Conductors | Wire | Terminations | Sleeve |
|---|---|---|---|---|---|
| Manifold A | J1 | [9](J1_PINS) (8 OUT + COM) | 22 AWG black | Fastons at 8 valves; COM → **221-420** fan-out at the manifold | 3/4" |
| Manifold B | J2 | 5 of [6](J2_PINS) (2 OUT + FAN + COM + OUT3) | 22 AWG black | **XHP-6 housing, contact 3 (`OUT4`) left empty** — see below; Fastons at 2 valves + fan; V-K's `OUT3` + a `COM` tap branch off to the aft strip (DC-9); COM → **221-415** | 1/2" |
| Reservoir A reeds | J6 | [5](J6_PINS) (4 reed + GND) | 22 AWG black | reed leads; GND → **221-415** at the reservoir | 1/4" |
| Reservoir B + carb reeds | J7 | [7](J7_PINS) (6 reed + GND) | 22 AWG black | reed leads; female JST-XH housing (XHP-7) + XH contacts — the same 7P housing as SENSORS (J4), so **label both looms at the housing** (a swap would put J4's 3V3/5V on the MCP reed inputs); GND → **221-420** | 1/4" |
| Sensors | J4 | [7](J4_PINS) | 22 AWG black | DS18B20 / flow / moisture (DO + switched VCC); GND → **221-415** on the −X wall aft, where all three land | 1/4" |
| Relays | J5 | [4](J5_PINS) (`IO19` / `IO2` / `V5` / GND) | 22 AWG black | XH at J5; screw terminals at both relay modules, `V5`/GND teed to both at the relay end (LV-1/2/3 — lands in the column at [`power-column.md`](/hardware/assembly/power-column.md)) | 1/4" |
| Faucet display | J3 / SIG-6 | [4](J3_PINS) (TX / RX / 5 V / GND) | 28 AWG ribbon | TTL UART up the umbilical; **the TTL lines are ESD-clamped on the main board at U1** (D10/D11, 2× low-cap TVS — see the ESD note below); a faucet-end TVS is now optional | jacketed ribbon |
| Enclosure display | J9 / SIG-7 | [4](J9_PINS) (`B` / `A` / GND / `V12`) | 22 AWG black | A/B pair to the 4.3B's RS485 terminals; `V12` + GND to its 7–36 V screw input on the same loom | 1/2" |
| Gas sensor | J11 | [4](J11_PINS) (GND / `V5` / `DOUT` / `AOUT`) | 22 AWG black | MQ-6 leads | 1/4" |
| Pumps | J13 / DC-5 | [4](J13_PINS) (`AM2` / `AM1` / `BM2` / `BM1`) | 22 AWG black | female Faston receptacles onto the pump-motor spade tabs | 1/2" |
| 12 V input | J10 / DC-4 | [2](J10_PINS) (`V12` / GND) | 16 AWG | ferrules under the J10 screw clamps; from the power column's 12 V distribution block (lands in the column at [`power-column.md`](/hardware/assembly/power-column.md)) | — |
| AC mains | AC-1…6 | per run | 16 AWG (black/white/green) + 18 AWG SJOOW | ferrules → **221-413**; current-donor external-interface connector TBD at compressor; rings to ground | SJOOW jacket on the compressor lead |

### MANIFOLD B — the empty contact

J2 is the one loom whose housing is wider than its conductor count. The main board's wafer is [6](J2_PINS)-way, labelled from contact 1 `COM`, `FAN`, `OUT4`, `OUT3`, `OUT2`, `OUT1` ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx)) — and `OUT4` drives no valve. It is a fully-routed spare channel, so the harness crimps **five contacts into an XHP-6 and leaves contact 3 empty**.

**Contact 3 is in the middle of the housing, not on an end.** Crimp the five in their labelled positions and skip the third; do not close the gap. A loom that fills contacts 1–5 consecutively lands every conductor one position off — `FAN` on `OUT4`, `COM` on `FAN` — which puts the shared 12 V rail on a driver output. The empty cavity is the guard, so leave it empty and verify it at the step-5 continuity test.

## Faucet-display ESD protection (SIG-6)

The faucet flavor LCD is the one user-touched surface at the far end of a ~1 m umbilical, so its
TTL UART pins are the main board's most exposed ESD path. The **primary** clamp is now **on the main board, at
the ESP32** — so no cable-assembly step is required for ESD; the faucet-end TVS drops to an optional
belt-and-braces extra. The protection is:

- **On the main board (primary — required, already placed):** each faucet TTL line is clamped at U1 by a
  low-capacitance TVS shunting the U1-side of its series resistor to the GND plane — **D10 on IO33
  (TX) and D11 on IO35 (RX)**, onsemi **ESD9B3.3ST5G** (SOD-923, 3.3 V working / bidirectional,
  ~15 pF, LCSC C96512). Each sits after its series resistor (topology: J3 → 220 Ω → clamp-at-the-IC →
  U1), with the shunt riding a **via-in-pad straight to the GND plane** — the shortest possible loop,
  which is what sets clamp effectiveness. A strike arriving up the ribbon is current-limited by the
  220 Ω and clamped to ~3.3 V at the ESP32 pin. See `pcb/pcba/jlcpcb-parts.md` (D10/D11) and
  `pcb/pcba/pcba.tsx` (FAUCET block). This mirrors the RS485 side, where D1 (SM712) clamps the A/B
  pair at J9.
- **At the driver end (series backstop — already on the main board):** R26 (IO33) and R27 (IO35), ~220 Ω
  0402 in series in each line, give series damping on the long-cable edges and set the current limit
  that lets the on-board clamp do its job. They are the series element of the clamp topology, not a
  standalone protection.
- **At the faucet-display end (optional — NOT required):** because the main board now clamps the ESP32
  pin, a cable-end TVS is no longer needed. If a builder wants defense-in-depth at the user-touch
  source, the same low-cap part class works: **2× ESD9B3.3-class / PESD3V3-class, ≤ 15 pF, SOD-923**
  (e.g. onsemi ESD9B3.3ST5G or Nexperia PESD3V3L1BA), one from each TTL line to the faucet-side GND on
  the last ~10 mm of ribbon, shortest loop. This is a build-time option, not a build requirement.

The 5 V and GND ribbon conductors need no clamp (5 V is a rail, GND is the return); only the two TTL
signals are protected.

## Open items

1. **Shielded reed pairs.** The reed / 1-wire runs pass alongside the switching solenoid trunk; consider shielded twisted pair (foil + drain, single-end grounded) over plain 22 AWG.
2. **AC mains wire grade.** Confirm the line-voltage runs use a recognized appliance-grade wire (UL1015 / UL1028, 600 V, 105 °C) rather than hobby silicone — the discipline already applied to the SJOOW compressor lead.
3. **The squeezed runs.** J1's eight valve conductors (309 mm), J4's moisture pair (304) and J7's carb-reed pair (323) are bought at the 302 mm a cut lead yields, with no service loop. Confirm each reaches with the enclosure assembled before the order goes in; one that does not takes a junction like the other twenty-four.
4. **Junction carrier.** The four breaks need `B*B-XH-A` headers back to back on something mountable, and nothing is drawn yet. The clusters take different circuit counts, which is also the keying — no two junctions in the box should accept the same housing.
5. **Lead insulation grade.** §11 specifies 22 AWG silicone for its flexibility and its 1.7 mm OD. The ASXHSXH22K leads come on JST's own wire and the grade is unconfirmed; confirm it before the order, since it governs the whole in-box harness rather than a branch of it.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_cable_assemblies_sync.py`
