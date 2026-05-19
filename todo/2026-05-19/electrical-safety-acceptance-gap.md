# Electrical safety acceptance + GFCI install requirement gap — a Class I plumbed appliance is shipping without an end-of-line earth-bond test, without a leakage-current measurement, and without a customer-side receptacle requirement

**Author:** hourly agent, 2026-05-19 (sixteenth of the day)
**Status:** recommendation only — not for direct execution
**Audience:** Derek, future agents

## Why this is distinct from every sibling today and yesterday

This doc is about a fault path that **none** of the other gap docs touch: the AC-mains-to-exposed-metal fault path on a Class I 120 VAC plumbed appliance.

- [`leak-detection-coverage-gap.md`](leak-detection-coverage-gap.md) and [`water-damage-containment-gap.md`](water-damage-containment-gap.md) — water on the *outside* of the chassis. This doc is about voltage on the *outside* of the chassis. Different failure mode, different mitigation, no overlap.
- [`hydro-test-acceptance-criteria-gap.md`](hydro-test-acceptance-criteria-gap.md) — pressure vessel acceptance. This doc is electrical-system acceptance. Both are "acceptance criteria the procedure currently waves at," but for two different physical subsystems.
- [`integrated-firmware-gap.md`](integrated-firmware-gap.md) — firmware target. The interlocks discussed below assume firmware exists; they are not the firmware gap.
- [`cabinet-heat-rejection-gap.md`](cabinet-heat-rejection-gap.md) — thermal, not electrical.
- Yesterday's [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) names "a 120 V outlet reachable to the rear C14 inlet" as a Phase-A install survey item (line 62). It does **not** name what *kind* of outlet — GFCI, AFCI, standard 5-15R, dishwasher-rated — and does not name a verification step the founder performs on the customer-side circuit before the unit is energized for the first time at the customer's house. The install consult is upstream; this doc is the receptacle/circuit *spec* it would consult.
- Yesterday's [`warranty-and-rma-gap.md`](../2026-05-18/warranty-and-rma-gap.md) is the *post-failure* policy doc. This doc is the *pre-failure* prevention doc. The two pair: a documented end-of-line electrical safety test is what makes RMA root-cause possible at all when the failure mode is "customer feels a tingle when they touch the faucet."

---

## TL;DR

[`hardware/wiring/ac-wiring-schedule.md:99`](../../hardware/wiring/ac-wiring-schedule.md) commits the appliance to **Class I status**:

> The chassis bond gives the appliance Class I status: if a fault energizes any exposed metal part, fault current returns to the building ground through the C14 cord and trips the upstream breaker before the user touches anything.

Class I is a load-bearing safety claim. It says: there is a continuous, low-impedance path from every exposed conductive surface back to the building's protective earth, and that path is the primary protection against electric shock if a hot conductor faults to the chassis.

The appliance has **four** exposed conductive surfaces ([`hardware/assembly/wiring.md:29–37`](../../hardware/assembly/wiring.md), [`hardware/wiring/ac-wiring-schedule.md:97`](../../hardware/wiring/ac-wiring-schedule.md)):

1. The 316L SS carbonator pressure vessel (touchable through the cold-core foam shells via service access; wetted by carbonated water inside).
2. The compressor body (touchable through the compressor shroud's grommet area and during service).
3. The compressor shroud itself (sheet metal — the only sheet-metal panel in the appliance).
4. The faucet under-counter SS plate, which is mechanically bonded to the **Westbrass Touch-Flo faucet** — the surface the customer touches every time they pour soda, with one wet hand, while standing on a kitchen floor that may also be wet.

Each of those four surfaces has its own discrete 16 AWG green wire back to a single ring-terminal stack on the electronics-shelf ground bus, which is in turn bonded to the C14 inlet's earth pin via run AC-1.

That is four independent bonds in series with the cord and the building wiring. Each is a separate failure point. None of them has a documented end-of-line acceptance test, none has a documented in-life monitor, and none has a customer-side mitigation requirement (a GFCI on the upstream branch circuit) called out in any shippable customer document.

The build procedure ([`hardware/assembly/wiring.md:56`](../../hardware/assembly/wiring.md)) explicitly says:

> After step 2 and before any DC conductor lands, cold-check the AC wiring with the C14 inlet **disconnected from line**. No 120 VAC is applied — this is a multimeter check, not a hipot.

That sentence is correct as a **build-time** check. It is **insufficient** as an **end-of-line acceptance** check. The two checks measure different things at different stages of the build, and the second one is missing entirely.

This doc proposes three concrete additions:

1. A **bonded earth continuity test** at end-of-line, with a numeric pass criterion in milliohms, at a documented test current. Lives in [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) as a new Step 2.5 between "Power on + interlock check" and "First water fill of the carbonator."
2. A **leakage-current measurement** under operating conditions during the burn-in window (one reading per check-in, recorded to the per-serial log). Same doc, new sub-bullet under Step 11.
3. A **customer-side circuit requirement** (GFCI on the appliance's branch circuit) documented in the Phase-A install survey, the install consult playbook, and the per-serial portal. Plus the corresponding interior-side mitigation if the customer's house cannot deliver it (cord-and-plug to a kitchen-counter GFCI, or an integrated LCDI cord).

Below: what each one is, why it's needed, what the equipment costs, and what passes/fails look like.

---

## Part 1 — The end-of-line earth-bond continuity test

### What's there today

[`hardware/assembly/wiring.md:40`](../../hardware/assembly/wiring.md) Step 1:

> Continuity check after this step: ohms-low between every bonded metal surface and the bus, before any other wire lands.

"Ohms-low" is operationally undefined. A handheld multimeter reads in the range of ~0.2–0.5 Ω at its own lead resistance — meaning a chassis bond that is actually 0.4 Ω (a corroded crimp on a ring terminal at the faucet plate after six months) reads "ohms-low" on a multimeter the day the unit ships and reads "ohms-low" on the same multimeter at the moment a customer's faucet is energized through the corroded bond.

[`hardware/assembly/wiring.md:58`](../../hardware/assembly/wiring.md) Step 3:

> **Continuity (ohms-low):** C14 earth pin to every metal-part chassis-ground target from step 1.

Same problem. This is the *only* AC-side bond verification in the entire build documentation.

### What it needs to be

A **dedicated earth-bond test** with three properties the multimeter check doesn't have:

1. **A defined test current.** The published Class I appliance standards (UL 60335-1 §27.5, IEC 60335-1 §27.5) test the protective earth circuit at **25 A** for 1 minute, with the maximum allowed resistance being **0.1 Ω** between the earth pin and any accessible metal part. At 25 A the test injects ~62 V drop across a 0.1 Ω bond, which exposes a single bad crimp that "looks fine" to a multimeter. The test current matters because the failure mode being caught is the bond that holds at 1 mA but vaporizes at 5 A of fault current.

2. **A defined acceptance threshold in milliohms.** "Less than 0.1 Ω" is the standard. For our four bonds — pressure vessel, compressor body, compressor shroud, faucet plate — that's the same number on all four because each one is its own independent fault path to the same earth pin.

3. **A defined fixture.** Either a benchtop ground-bond tester (Hipotronics / Slaughter / Vitrek / Associated Research) at $1.5–3K, or — for a Founder Edition's ~12 units/year — a far cheaper alternative: a 25 A AC source (a current-limited welding power supply, or a hand-wound transformer that drops 120 V to 5 V at high current) into the C14 ground pin, with a Kelvin-clip 4-wire microhmmeter (Extech 380462 ~$500) reading the drop across each bond. Either approach yields a number. The number, not "ohms-low," is what gets logged.

A practical fixture for the founder bench would be: pick up a used **HypoT-Test Inc QuadCheck**, **Slaughter 105 series**, or **Associated Research HypotULTRA** off the secondhand market for ~$400–800. They do ground bond, hipot, and insulation resistance in one box and are the standard for end-of-line testing at this kind of volume. Founder Edition's safety story benefits visibly from "every unit is hipot tested" in marketing — see Part 4 below.

### Where the test inserts in the procedure

[`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) currently jumps from Step 2 ("Power on + interlock check") straight to Step 3 ("First water fill of the carbonator"). Insert **Step 2.5 — Ground bond + dielectric verification**:

> With the C14 cord disconnected from the wall outlet (the appliance is powered down — Step 2 just verified the firmware boot and interlock state, then was de-energized), connect the bench safety tester's high-current source to the C14 inlet's earth pin via a chassis-clip lead.
>
> Run the ground-bond cycle: 25 A AC at 60 Hz, 1 second per probe, with the return probe clipped in turn to:
>
> 1. The exposed lip of the compressor shroud (any unpainted edge).
> 2. The compressor body's mounting foot (the same one that takes the chassis-bond ring terminal — but the Kelvin probe goes on a *different* exposed point on the body, not the bond ring itself, so the test current actually traverses the bond rather than shorting it).
> 3. The pressure-vessel top plate, accessed through the service port at the top of the foam shell.
> 4. The under-counter SS faucet plate.
>
> **Pass:** all four bonds read ≤ 0.1 Ω. **Fail:** any single bond > 0.1 Ω — return to wiring; reseat the ring terminal; if reseating doesn't fix it, replace the green-wire run end-to-end.
>
> Immediately follow with the dielectric withstand cycle: 1250 V AC RMS for 1 second between the L+N pins (tied together at the tester) and the earth pin, with the appliance's main power switch in the ON position (there is no switch — the C14 inlet is always live when plugged in, so the dielectric is across the AC side at every point downstream of the inlet). Maximum allowed leakage during the test: 1.0 mA. **Pass:** leakage stays below 1.0 mA across the 1-second window. **Fail:** leakage ≥ 1.0 mA OR audible breakdown — return to wiring; check for pinched conductors at the shroud grommet edge, the foam-shell penetrations, and the PSU's input lead routing.

### Why this isn't already in the doc

Best guess: the acceptance procedure was written by someone (Derek) who knows the AC build is correctly executed and is therefore optimizing for the steps that *vary* between units (water leak, refrigerant charge, flavor pump calibration). The AC build genuinely is the same wire-by-wire on every unit. But the *quality* of each crimp is not: a single bad ring terminal at the faucet plate makes the unit unsafe and is the failure mode that a 25 A test catches and a multimeter test does not. The procedure already pays the cost of a per-serial test rig (graduated cylinder, refractometer, thermocouple, 8-hour bench occupancy); adding ground bond + dielectric is one fixture and ~60 additional seconds per unit.

---

## Part 2 — Leakage current during operation

### What it measures

Even with a clean ground bond, an appliance with capacitive coupling between its AC mains and its accessible metal (every appliance, including this one — the Mean Well IRM-90-12ST PSU has Y-class line filter caps from L/N to its earth lug, by design) leaks a small steady-state current to earth during normal operation. UL 60335-1 §13 limits earth-leakage current on a Class I cord-and-plug appliance to **0.75 mA** for stationary equipment and **0.5 mA** for hand-held / portable. Plumbed under-sink appliances are not handheld but they are touched (faucet) by wet hands.

This is the test that catches:

- A PSU with a degraded Y-cap that has shifted out of spec (rare but observed in low-end Chinese supplies; less of a risk on Mean Well, more of a risk on the unbranded 5 V / 3.3 V regulator stack downstream).
- A pinch on the 18 AWG SJOOW jacketed lead through the shroud grommet that has *not yet* progressed to a hard fault but is allowing capacitive coupling between the AC conductors and the shroud body.
- A signal-side wire that is touching the chassis-ground bus at an unintended point and is providing a return path for an EMI-coupled current.

None of these are caught by the multimeter check at build, the 25 A ground-bond test at acceptance, or the 8-hour burn-in's leak-watch as currently specified (it watches for *water*, not current).

### How to measure

Two practical options:

1. **A clamp-on AC leakage meter** (Fluke 368 / Extech MA200 / Klein CL220 — $200–500) clamped around the H+N conductors of the C14 cord during steady-state operation. The vector sum of H and N currents is zero in a fault-free appliance; any non-zero reading on the clamp is the current returning through the earth conductor (or escaping to the customer via the appliance's accessible metal — which is what we want to detect).
2. **A bench leakage-current tester** (Slaughter 105, Associated Research HypotULTRA — the same box recommended above for ground bond + dielectric). Higher accuracy, but the clamp approach is sufficient for the regulatory threshold of 0.5–0.75 mA and is dramatically easier to add to the existing burn-in workflow.

Insert as a watch-item in [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) Step 11 "Multi-hour burn-in":

> - Clamp-on AC leakage meter on the C14 cord, recorded at the 1-hour, 4-hour, and 8-hour check-ins (the same intervals the operator already pulls in to read compressor cycle count and check the shop towel under the chassis). Acceptance: < 0.5 mA at every check-in. Fail: ≥ 0.5 mA at any check-in — escalate to electrical investigation before the unit moves to finish-pack-ship.

### Why not just rely on the customer's GFCI?

A 5 mA-trip GFCI catches a fault that *appears* during the appliance's life. It does not catch a steady-state 1.5 mA capacitive leak that has been there since day one — the GFCI sits below its trip threshold, the customer never knows, but the appliance is leaking current to their faucet every time it's plugged in. The day-zero acceptance reading is the test for steady-state leakage; the GFCI is the test for everything else. **Both are needed; neither replaces the other.**

---

## Part 3 — The customer-side GFCI requirement, and what to do when the customer's house can't provide one

### Background — what NEC says about under-sink receptacles in 2026

The relevant code points:

- **NEC 210.8(D)** — since the 2020 cycle, dishwashers in dwelling units require GFCI protection. The appliance is not a dishwasher but it is a plumbed under-sink load in a kitchen; the *spirit* of 210.8(D) clearly applies, the letter is ambiguous.
- **NEC 210.8(A)(6)** — kitchen receptacles serving countertop surfaces require GFCI. The under-sink receptacle is *not* a countertop receptacle and is therefore not required to be GFCI by 2026 NEC absent the 210.8(D) interpretation.
- **Older homes** (pre-2020 construction, never remodeled to current code) commonly have a non-GFCI, non-AFCI single receptacle under the sink that was installed for the disposal and the dishwasher. Many of the Founder Edition target buyers (per [`marketing/target-market.md`](../../marketing/target-market.md) "$200K+ household income, 2-4 diet sodas/day, homeowner") live in homes built between 1990 and 2015 — exactly the cohort with non-GFCI under-sink receptacles by default.

### The shippable requirement

The appliance is sold to homes whose receptacle inventory we do not control. The requirement we *can* control is what we say in the customer-facing documents:

> The Soda Faucet I plugs into a standard 120 V NEMA 5-15R receptacle on a GFCI-protected branch circuit. If the receptacle under your kitchen sink is not GFCI-protected (most pre-2020 construction is not), you have three options:
>
> 1. **Replace the receptacle with a GFCI** (~$25, ~15 min — electrician or capable homeowner). Recommended; it also protects your disposal and dishwasher.
> 2. **Add a portable GFCI between the wall outlet and our cord** ($20–40, Leviton GFCI 5-15 plug-in adapter). Works immediately; survives the install consult.
> 3. **Route our cord up to a kitchen-counter GFCI receptacle through a cord pass-through** in your cabinet wall (~$5 for the grommet; no electrician). The kitchen-counter receptacles in your house are GFCI-protected by code if they are within 6 feet of the sink.

The install consult (per yesterday's [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) Phase A) should add a single question to the survey:

> **Q: Is the under-sink receptacle GFCI-protected?** (Trip-test it by pressing TEST and verifying the RESET button pops out. If there is no TEST button on the receptacle, it is not GFCI — but check for a GFCI receptacle upstream on the same circuit, often near the kitchen counter.)

If the answer is no, the install consult triggers a pre-ship mitigation: ship the Founder Edition with the portable GFCI adapter (Option 2 above) in the box, at ~$25 BOM-add per unit, until the customer chooses to do Option 1 at their convenience. This converts a customer-side risk into a ship-side risk we control.

### The hardware alternative — an integrated LCDI on the cord

Air conditioners and pool pumps ship with **LCDI (Leakage Current Detection Interrupter)** cords — a cord that has the GFCI built into the plug head. UL 943 listed. ~$15 wholesale, ~$30 retail. If the cord-and-plug supply chain can be moved to an LCDI-equipped cord (typically a NEMA 5-15P → C13 with the LCDI module in the plug body), the appliance becomes self-protecting on any receptacle, and the install-consult question becomes informational rather than gating.

This is the recommended long-term path. The customer-side mitigation (Option 2) is the bridge while the LCDI cord is sourced.

Both paths converge on the same Customer Promise: **this appliance will not deliver a shock to your wet hand, even if the receptacle you plug it into pre-dates code that would have required GFCI protection at construction.**

---

## Part 4 — Putting it on the per-unit portal

Per yesterday's [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md), the `/u/NNN` page exists (in spec, not yet in code) to translate the Founder Edition trust promise into something the buyer can verify. The electrical safety tests proposed above are exactly the kind of data that page should show:

> **Unit 003 of 050 — Electrical safety acceptance, March 14 2026**
>
> - Ground bond, faucet plate to earth pin: **0.038 Ω** (limit 0.100 Ω) ✓
> - Ground bond, pressure vessel to earth pin: **0.041 Ω** (limit 0.100 Ω) ✓
> - Ground bond, compressor shroud to earth pin: **0.052 Ω** (limit 0.100 Ω) ✓
> - Ground bond, compressor body to earth pin: **0.047 Ω** (limit 0.100 Ω) ✓
> - Dielectric withstand 1250 V AC 1 s, leakage: **0.12 mA** (limit 1.0 mA) ✓
> - Steady-state earth leakage, 8-hour mean: **0.07 mA** (limit 0.5 mA) ✓

This is what "buying from a person you trust" looks like with the receipts attached. At Founder Edition price ($7,500), the buyer is paying for the assurance that *this specific unit* was tested, not that a sister unit somewhere passed a certification a year ago. The per-serial log already exists in the procedure ([`acceptance-and-burn-in.md` Step 12](../../hardware/assembly/acceptance-and-burn-in.md)); the electrical numbers belong in that file too.

---

## Part 5 — In-life monitoring (open item, not a recommendation)

Once the unit has been in the customer's kitchen for 18 months, the four ground bonds are out of sight, the customer cannot test them, and the only feedback the customer gets that one has failed is the day they touch the faucet and feel a tingle.

The appliance has an ESP32, an MCP23017, and a 12 V bus. A continuity-monitor circuit (a current-injection on the chassis-bond ring terminal pair, sensed at the ESP32) is electrically straightforward — but mechanically it is the kind of feature that absorbs design time disproportionate to its likelihood of being the failure mode that actually trips. The customer-side GFCI is the much cheaper mitigation for the in-life path.

I am *not* recommending an in-life ground-bond monitor in this doc. I am recommending:

1. The end-of-line tests in Parts 1 and 2 (catches day-zero defects).
2. The customer-side GFCI requirement in Part 3 (catches in-life ground-bond degradation).

The combination is the affordable Founder Edition safety posture. The in-life monitor is the Standard Edition / volume-product feature when the BOM headroom exists.

---

## What I'd commit if this were execution, not recommendation

In the *appliance* repo (not customer-facing yet):

- [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md): add **Step 2.5 — Ground bond + dielectric verification** (Part 1 above), and add the leakage-current watch-item to Step 11 (Part 2 above). Update Open items §1 to reference the electrical thresholds.
- [`hardware/wiring/ac-wiring-schedule.md`](../../hardware/wiring/ac-wiring-schedule.md): under "Grounding strategy," append a paragraph naming the end-of-line ground-bond test as the production gate; cite the ≤ 0.1 Ω threshold.
- [`hardware/bom.md`](../../hardware/bom.md): add a line under "Tooling, bench-shared not per-unit" for the safety tester (used Slaughter 105 or equivalent, ~$500–800).
- [`hardware/bom.md`](../../hardware/bom.md) under "Per-unit consumables" or "Cord assembly": flag the LCDI-cord option (Part 3) as an open BOM decision, with the portable GFCI adapter as the interim mitigation if the LCDI cord is not yet sourced.
- [`business/regulatory.md`](../../business/regulatory.md): under "CPSC general safety duty," append a paragraph naming UL 60335-1 §27.5 (ground bond), §16 (leakage current), and §13 (dielectric withstand) as the design-and-test references the project follows without pursuing the listing, parallel to how UL 60335-2-89 is already cited for the hydrocarbon-refrigerant clauses.

In the *customer-facing* docs (which mostly don't exist yet; per yesterday's siblings):

- The install-consult playbook ([`todo/2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md)) Phase A survey adds the GFCI question and the three remediation options.
- The per-unit portal ([`todo/2026-05-18/per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md)) `/u/NNN` page surfaces the per-serial electrical readings, alongside the burn-in dispense + temperature data already discussed there.
- The nameplate ([`hardware/printed-parts/enclosure/nameplate/README.md`](../../hardware/printed-parts/enclosure/nameplate/README.md)) does not need an electrical safety marking because the project is not pursuing a listed mark; the regulatory text already on it ("120 V 60 Hz") is sufficient.

---

## What I'd want to read before committing

1. Whether **Mean Well IRM-90-12ST**'s declared Y-cap leakage on its datasheet (typically 0.25 mA per cap to PE, 0.5 mA total) leaves headroom under the 0.5 mA threshold once the rest of the appliance's downstream coupling is added. If it does not, the threshold has to move from "we picked 0.5 mA from UL 60335-1" to "we picked 0.75 mA which is the stationary-equipment limit and the PSU eats most of it." Datasheet review is ~10 minutes.
2. Whether a used **safety tester** in the $400–800 band is available locally (Lincoln, NE — the founder's bench location), or whether shipping a 40 lb instrument from a national surplus dealer is required. This is the kind of fixture that lives on the bench for a decade and pays for itself on Founder Edition unit 4. Even at $1500 new, it is < 1 % of unit revenue at the Founder price.
3. Whether the **LCDI cord** is available off-the-shelf as a NEMA 5-15P → C13 (rather than the more common 5-15P → bare-wire pigtail used in air conditioners). Quick supplier check — Tripp Lite, Quail Electronics, Volex. If the C13 variant is not stocked, the in-box portable GFCI (Part 3 Option 2) is the immediate path.
4. Whether the **founder's homeowner insurance** covers personal injury caused by a sold product. This is genuinely a "before unit 1 ships" question independent of this doc, but it sits adjacent — the electrical safety acceptance is the project's *first* defense; insurance is the second. The two are complementary.

---

## Bottom line

The appliance is a Class I plumbed 120 VAC consumer product. It commits to that classification in the wiring schedule. The build procedure verifies the bonds with a multimeter check that is insufficient for the failure mode it is meant to catch. The acceptance procedure does not measure ground-bond resistance, dielectric withstand, or operating-state leakage current. The customer-facing documents do not specify a receptacle requirement that mitigates in-life degradation of the bonds.

None of those gaps are technically difficult to close. A used safety tester, four lines in [`acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md), a $25-per-unit portable GFCI in the box, and one paragraph in [`regulatory.md`](../../business/regulatory.md) close the entire surface. The total dollar cost is well under one percent of a single Founder Edition unit's revenue, and the value added is "the safety claim the appliance already makes is actually verified before the unit leaves the bench, and the customer's hands stay safe even if their 1997 under-sink receptacle is not what NEC would require today."

This belongs in the build before unit 001 ships. Estimated effort: one bench day for the procedure work and the test, plus the lead time on whichever safety tester gets sourced.
