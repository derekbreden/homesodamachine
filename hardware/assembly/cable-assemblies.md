# Cable assemblies

The bench-fabrication procedure for the appliance's internal low-voltage harnesses. Every cable assembly is **built complete and tested off the chassis**, then landed during [`wiring.md`](/hardware/assembly/wiring.md). This doc is the *fabrication* view (cut, terminate, sleeve, test); `wiring.md` is the *install* view (route, land, strain-relieve).

## Why pre-built, tested assemblies

The appliance ships sealed and is **not field-serviced** — a fault returns the whole unit, and the repair is to swap the affected cable assembly for a freshly-built, tested one, never to trace and re-crimp a single conductor (if one termination failed, the assembly is suspect end-to-end). Two consequences drive every choice below:

- **A loom is ribbon, cut to its longest leg.** The machine is placed, so every run is measured rather than estimated ([`_run_lengths.py`](/hardware/wiring/_run_lengths.py)), and the longest conductor inside the enclosure is 582 mm. A loom's conductors leave the board together and part only where the branch is, which is what a flat ribbon already is: one cut, no combing, and no length to hold between conductors that share a cruise. The stock is sold in 3P, 4P and 5P, and one or two of them make every count the board's wafers ask for — see § Ribbon pairs. Bulk wire survives downstream of the lever nuts, where a branch has an XH end at neither end.
- **All-black wire.** Per-conductor color is a field-tech's fault-tracing aid, which this model never uses: the build is jig-and-test, the repair is replace-the-assembly, and the conductors are splayed during crimping where color does nothing. All-black also matches the appliance's monochrome language (PETG, PCB, John Guest fittings, LLDPE). **Exception — AC mains:** black hot / white neutral / green ground, a safety/code convention (not a service aid) for the line-voltage runs, and hidden inside the black sleeve anyway.

## Scope

In: the cut list (lengths + terminations) from [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Run table"; the assembly endpoints (board connectors J1–J11 + J13) from [`/hardware/pcb/pcba/pcba.tsx`](/hardware/pcb/pcba/pcba.tsx); bulk wire, sleeve, ferrules, terminals, and Wago lever nuts from [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11.

Out: a set of labelled, continuity-tested cable assemblies, ready to land per [`wiring.md`](/hardware/assembly/wiring.md).

Not in scope: routing, strain-relief, and landing into the chassis ([`wiring.md`](/hardware/assembly/wiring.md)); the AC mains in-place runs; firmware.

## Stock & tooling

Every loom is **BNTECHGO 22 AWG black silicone ribbon** — 3P, 4P and 5P, one or two ribbons per loom (§ Ribbon pairs). Its conductors are hand-crimped into **SXH-001T-P0.6** contacts and seated in the XH housing its wafer takes; [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 carries housings and loose terminals in 4, 5, 6, 7 and 9-way kits. Bulk silicone, 600 V, cut-to-length covers what a loom is not: **22 AWG black** for the fan-out branches downstream of the lever nuts — a valve's COM leg, a reed's GND leg, XH at neither end — **28 AWG 4P black ribbon** for the umbilical and the pump cartridge's cord, and **16 AWG 5-color** (AC mains + branches + 12 V trunk + green ground). The other bought multiconductor run is the GEARit 18 AWG SJOOW 3-conductor compressor lead. A ribbon pair lies flat where a cut bundle lies round, so the sleeve sizes to the pair and a cable clip's channel takes the bare ribbon — Open item 3.

Terminations: insulated bootlace ferrules (Preciva kit) into the Wago 221 lever nuts + screw terminals; female Faston disconnects (6.3 mm / 4.8 mm) at valves, motors, and fan; 110 IDC punchdown on the pump jack and a 3-prong RJ11 6P4C plug on the pump cartridge's cord; the current Frigidaire donor's factory-external electrical interface is Open item 5 in [`wiring.md`](/hardware/assembly/wiring.md); ring terminals to the ground bus + the compressor's terminal-box earth screw; JST-XH housings at the main board's labeled wafers — every loom XH, J7 (REEDS B) included. J7 and J4 (SENSORS) share the same 7P housing, so **label both looms at the housing** and dress them to their own edges: a swapped pair would put J4's 3V3/5V on J7's MCP reed inputs. Distribution / fan-out: Wago 221 lever nuts — **221-413** (AC mains H/N/G), **221-415** (≤5-conductor fan-outs, incl. MANIFOLD B COM), **221-420** (the >5-conductor MANIFOLD A COM + reservoir-B reed GND).

Dress: **black PET braided sleeve** — 1/2" for most bundles, 3/4" for the manifold trunk, 1/4" for thin runs; every cut sleeve end finished with heat-shrink so it can't fray; black UV-nylon zip ties, **flush-cut** (no proud tail). A cable clip's channel takes the bare ribbon, not the braid over it, so DC-5's flat ribbon is not sleeved at its panel connector, in the ridge-wall clip, or in any of front-top's three +X flank clips, and SIG-7's is unsleeved through those same flank clips. Tools: ferrule crimper (Preciva 28–5), Faston/insulated-terminal crimper (Haisstronica 22–10), JST-XH crimper (iCrimp SN-2549), impact punchdown tool (Klein VDV427-300) and modular-plug crimper (VCE) for the two RJ11 stations, wire stripper (Klein 11063W), flush cutters, heat gun, multimeter — see [`/hardware/ledger/tools.md`](/hardware/ledger/tools.md).


### Ribbon pairs

The stock is 3P, 4P and 5P. One or two of them make every count from three to ten — 6 = 3+3,
7 = 3+4, 8 = 4+4, 9 = 4+5, 10 = 5+5 — and the board's wafers ask for {4, 5, 6, 7, 9}, so every
loom in the box is one ribbon or two side by side. A 6P is made in this gauge and is not bought:
two 3P cover the one six-way wafer and reach four counts besides.

| Loom | Conductors | Ribbon | Carries |
|---|---:|---|---|
| J1 MANIFOLD A | [9](J1_PINS) | 5P + 4P | `OUT1`–`OUT8` to the eight coils, `COM` to the 221-420 |
| J2 MANIFOLD B | [6](J2_PINS) | 3P + 3P | five populated; the conductor that would land in contact 3 is trimmed at the housing, not crimped |
| J3 FAUCET | [4](J3_PINS) | 4P | the inboard half only, board to the keystone on the +Y wall |
| J4 SENSORS | [7](J4_PINS) | 4P + 3P | the 1-wire and flow pairs (`3V3`/`IO26`, `V5`/`IO25`) on the 4P; the moisture pair and the shared `GND` on the 3P |
| J5 RELAYS | [4](J5_PINS) | 4P | both Teyleten modules |
| J6 REEDS A | [5](J6_PINS) | 5P | reservoir A's column entire — four reeds and the common |
| J7 REEDS B | [7](J7_PINS) | 5P + 3P | reservoir B's column on the 5P; `CLO`/`CHI` on the 3P, third conductor trimmed |
| J9 DISPLAY | [4](J9_PINS) | 4P | the 4.3B's RS485 pair and its 12 V |
| J11 GAS | [4](J11_PINS) | 4P | the MQ-6 |
| J13 PUMPS | [4](J13_PINS) | 4P | the pump jack's fixed half |

A pair is two ribbons, not a spliced one: they are cut to the same length, laid edge to edge and
dressed as one until the branch point. **Which ribbon carries which conductor is set by where the
conductors part, not by the wafer's pin order** — J7's 5P is the five that climb reservoir B's reed
channel together and J4's 3P is the three that end at the moisture board, so a ribbon is peeled at
one place rather than unpicked at three. Where a pair overfills its wafer by one — J2 and J7 — the
spare conductor is trimmed back at the housing and never crimped.

A loom is cut to its longest leg and the shorter legs are peeled off the web early and trimmed.
The longest run in the box is J11's 582 mm, and a ribbon is cut from a 15.2 m spool, so no loom
needs a junction to reach. Four clusters sit on the quadrant seam — the cold core, MANIFOLD B, the
display and the pumps — where the enclosure's columns slide apart and its halves unscrew from the
side faces, and a loom that parts at the seam lets a quadrant come away without being unthreaded.
Whether any loom is broken for that is Open item 4.

### XH contacts

Every board-end termination inside the enclosure is hand-crimped: a ribbon conductor cannot arrive
pre-crimped, since the crimp is what joins it to the housing it shares with its neighbours. The
contact is **SXH-001T-P0.6** — conductor #28 to #22, insulation OD 0.9 to 1.9 mm, tin — and the
ribbon's 1.7 mm conductor sits mid-range in it. Housings and loose terminals come in the CQRobot
XH kits, 4, 5, 6, 7 and 9-way ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11).

What holds a contact square in the die is a **locator**, and no low-cost tool has one: the contact
is placed by hand and held there. JST's own hand tools do — **WC-110** (#22–#28, side entry) covers
both gauges in this build. With a ratcheting tool and no locator, close the ratchet one click onto
the contact so it is captive, then feed the wire. Splay the ribbon's conductors at the housing end
before crimping so each one enters its die straight; a conductor still webbed to its neighbour
enters at an angle. Rework on a 28 AWG XH termination has a second contact option:
**SXH-002T-P0.6** is the #30 to #26 part, insulation OD 0.9 to 1.3 mm, and its barrel closes on
0.08 mm² near the middle of its range rather than at the floor of the -001T's.

## Procedure (per assembly)

For each cable assembly in the schedule below:

1. **Cut to length.** For a loom, take the pair § Ribbon pairs names for that wafer and cut both ribbons to the loom's longest leg from the AC wiring schedule, plus a service loop. For a fan-out branch or an AC run, pull from the bulk spool and cut to the run length plus a service loop. All-black except the AC mains trio.
2. **Strip & terminate.** Strip to the termination's barrel length and land each end: an insulated ferrule for a Wago/screw landing (correct barrel length, one conductor per ferrule unless a twin-entry ferrule is called for where two share one lever); a female Faston at a valve/motor tab; a ring at a ground stud; an XH pin into its housing. No solder splices on any field-serviceable branch.
3. **Fan-out / distribution.** Where a shared rail feeds many devices, land the feed and all branches in the assembly's Wago lever nut. The COM and GND fan-outs live at the **device-cluster end** of the assembly (manifold, reservoir) — you carry one rail wire out and explode it there, never run N parallel wires from the main board. Each nut has a well printed into the side wall by its own cluster (`enclosure._side_wells`); press it butt-first into its well, ports and levers to the room. Every well stands clear enough of its neighbours that a seated lug's levers still swing fully up (`enclosure.wago_pitch`), so a conductor can be added or moved without pulling the lug. The stations are tabled in [`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md) "Loom terminations".
4. **Sleeve & dress.** Lay a pair edge to edge, web flat, and slip it into black braided sleeve sized to the pair; heat-shrink each cut end; flush-cut every zip tie. A ribbon needs no combing — that is what it is for — and a run that lands in a cable clip is not sleeved through it.
5. **Test.** Continuity end-to-end, pin-to-pin against the schedule; confirm no short between adjacent conductors; on the manifold and reed assemblies verify the Wago commons exactly the intended pins. **Label the assembly by name, not per-conductor.**
6. **Bag & stage** for [`wiring.md`](/hardware/assembly/wiring.md).

## Assembly schedule

Conductor counts are the main board's connector pin counts (`pcba.tsx` J1–J11 = {[9](J1_PINS), [6](J2_PINS), [4](J3_PINS), [7](J4_PINS), [4](J5_PINS), [5](J6_PINS), [7](J7_PINS), [4](J8_PINS), [4](J9_PINS), [2](J10_PINS), [4](J11_PINS)}, J13 = [4](J13_PINS); there is no J12, and J14 is the USB programming port — no loom). The fan-out to the 11 valves (10 manifold + V-K) / many reeds happens **at the device end**, downstream of the connector — so each trunk carries its connector's count, never the fanned-out total.

| Assembly | Board conn. | Conductors | Wire | Terminations | Sleeve |
|---|---|---|---|---|---|
| Manifold A | J1 | [9](J1_PINS) (8 OUT + COM) | 22 AWG black 5P + 4P ribbon | Fastons at 8 valves; COM → **221-420** fan-out at the manifold | 3/4" |
| Manifold B | J2 | 5 of [6](J2_PINS) (2 OUT + FAN + COM + OUT3) | 22 AWG black 3P + 3P ribbon | **XHP-6 housing, contact 3 (`OUT4`) left empty** — see below; Fastons at 2 valves + fan; V-K's `OUT3` + a `COM` tap branch off to the aft strip (DC-9); COM → **221-415** | 1/2" |
| Reservoir A reeds | J6 | [5](J6_PINS) (4 reed + GND) | 22 AWG black 5P ribbon | one ribbon board to column, a conductor given up at each reed height; GND → **221-415** at the reservoir | 1/4" |
| Reservoir B + carb reeds | J7 | [7](J7_PINS) (6 reed + GND) | 22 AWG black 5P + 3P ribbon | reservoir B's column on the 5P, the two carbonator reeds on the 3P; female JST-XH housing (XHP-7) + XH contacts — the same 7P housing as SENSORS (J4), so **label both looms at the housing** (a swap would put J4's 3V3/5V on the MCP reed inputs); GND → **221-420** | 1/4" |
| Sensors | J4 | [7](J4_PINS) | 22 AWG black 4P + 3P ribbon | the DS18B20 and flow pairs on the 4P; moisture (DO + switched VCC) and the shared GND on the 3P; GND → **221-415** on the −X wall aft, where all three land | 1/4" |
| Relays | J5 | [4](J5_PINS) (`IO19` / `IO2` / `V5` / GND) | 22 AWG black 4P ribbon | XH at J5; screw terminals at both relay modules, `V5`/GND teed to both at the relay end (LV-1/2/3 — lands in the column at [`electronics-bay.md`](/hardware/assembly/electronics-bay.md)) | 1/4" |
| Faucet display | J3 / SIG-6 | [4](J3_PINS) (TX / RX / 5 V / GND) | 22 AWG black 4P ribbon | **Ends at the wall, not at the faucet** — XH on J3, 110 IDC on the back of the keystone jack the umbilical plugs into, the same punchdown DC-5 makes at the pump jack. The ribbon outboard of that jack is the umbilical's, built at [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md). **The TTL lines are ESD-clamped on the main board at U1** (D10/D11, 2× low-cap TVS — see the ESD note below); a faucet-end TVS is now optional | 1/2" |
| Enclosure display | J9 / SIG-7 | [4](J9_PINS) (`B` / `A` / GND / `V12`) | 22 AWG black 4P ribbon | A/B pair to the 4.3B's RS485 terminals; `V12` + GND to its 7–36 V screw input on the same loom | 1/2" |
| Gas sensor | J11 | [4](J11_PINS) (GND / `V5` / `DOUT` / `AOUT`) | 22 AWG black 4P ribbon | MQ-6 leads | 1/4" |
| Pumps — fixed half | J13 / DC-5 | [4](J13_PINS) (`AM2` / `AM1` / `BM2` / `BM1`) | 22 AWG black 4P ribbon, 350 mm | XH contacts at J13; 110 IDC punchdown on the pump jack | — |
| Pumps — cartridge cord | pump plug / DC-5 | 4, same order | 28 AWG black 4P ribbon, 400 mm | 3-prong RJ11 6P4C plug at the jack; female Fastons stay on the pump-motor tabs | — |
| 12 V input | J10 / DC-4 | [2](J10_PINS) (`V12` / GND) | 16 AWG | ferrules under the J10 screw clamps; from the electronics bay's 12 V distribution block (lands in the column at [`electronics-bay.md`](/hardware/assembly/electronics-bay.md)) | — |
| AC mains | AC-1…6 | per run | 16 AWG (black/white/green) + 18 AWG SJOOW | ferrules → **221-413**; current-donor external-interface connector TBD at compressor; rings to ground | SJOOW jacket on the compressor lead |

### Pump jack — DC-5

Two cables, and two terminations the bench already makes. The **fixed half** is 350 mm of the
BNTECHGO 22 AWG 4P ribbon: J13's XH contacts at one end, and at the other the four conductors
punched down on the pump jack's 110 IDC exactly as SIG-6's J3 loom is punched down on the
umbilical's keystone (Klein VDV427-300, the jack held in the punch-down stand), conductor 1 on
the ribbon's marked edge to the jack's position 2. The **cartridge cord** is 400 mm of the
BNTECHGO 28 AWG 4P ribbon, the umbilical's own stock: at the jack end a 3-prong EZYUMM RJ11 6P4C
plug, crimped as [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) step 2
crimps the umbilical's, the last 15 mm shimmed so the strain-relief bar bottoms; at the pump end
the four female Fastons that stay on the motor tabs.

| plug position | ribbon conductor | J13 net | Device |
|---:|---:|---|---|
| 2 | 1, marked edge | `AM2` | pump A |
| 3 | 2 | `AM1` | pump A |
| 4 | 3 | `BM2` | pump B |
| 5 | 4 | `BM1` | pump B |

The 28 AWG conductor is under the red Faston's 22–16 AWG barrel. Strip it 12 mm, fold the bare
strands back on themselves twice so the barrel closes on a full bundle, crimp, and pull each of
the four to the kit's rating before the deck goes in; section one spare first and build the four
only after it passes. Continuity-test plug position to pump tab, verify no adjacent short, and
verify J13 net-to-tab polarity. The jack is a dead-circuit service joint: never plug or unplug it
while either pump is energized.

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
3. **Sleeve and clip on a flat pair.** The sleeve sizes in the schedule were cut for round bundles — 3/4" for nine loose conductors on J1, 1/4" for a reed run. A 4P + 5P pair lies flat at 15.3 mm across and 1.7 mm thick, and a cable clip's channel takes bare ribbon rather than braid. Measure a made-up pair against each sleeve size and each clip before the sizes are called final.
4. **Whether a loom still parts at the quadrant seam.** No loom breaks for length any more, so the four junctions are now only a disassembly convenience: the cold core, MANIFOLD B, the display and the pumps each sit where a quadrant comes away. If the break is kept it needs `B*B-XH-A` headers back to back on something mountable, nothing is drawn yet, and the clusters' differing circuit counts are the keying — no two junctions in the box should accept the same housing.
5. **That the web zips.** A loom is cut to its longest leg and the short legs are peeled off the web by hand. BNTECHGO publishes the section (1.7 mm per conductor) and no tear strength, and this build has only ever used the 4P whole. Peel a metre of each of the 3P and 5P off the spool when they land and confirm the web parts cleanly without nicking insulation; if it does not, a loom is cut at the branch instead and the legs land as separate pieces.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_cable_assemblies_sync.py`
