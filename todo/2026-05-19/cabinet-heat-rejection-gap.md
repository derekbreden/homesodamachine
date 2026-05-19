# Cabinet heat rejection — the condenser exhausts into a closed kitchen cabinet and no doc says how the heat gets out

**Author:** hourly agent, 2026-05-19 (ninth of the day; replaces a deleted earlier file)

## What I picked and why

I am the ninth hourly agent today. The eight earlier files cover concentrate supply, foam-pour procedure, front-panel CAD, hydro-test acceptance, integrated firmware, leak detection, the meta-critique of the hourly routine, and trademark usage. Yesterday's files cover freight, CO2 supply ownership, install consult, order/payment, per-unit portal, warranty/RMA.

What none of them touch is the heat path between the condenser exhaust grille and the kitchen — specifically, what happens to the warm air after it leaves the side of the appliance and enters the closed cabinet around it.

I went looking for this because [`hardware/future.md`](../../hardware/future.md) "Enclosure layout" specifies side-to-side condenser airflow with intake on one enclosure face and exhaust on the opposite enclosure face, both faces sitting inside the under-sink cabinet. The cabinet itself is a typical 36" base cabinet — closed back wall, closed sides, hinged door on the front. The condenser is the part of the refrigeration loop that has to *reject* heat to ambient; if the air it sees is the cabinet's recirculated air rather than the kitchen's room air, the condenser is sitting in its own waste heat.

## What the docs currently say

**Heat output is acknowledged but not quantified.**

[`hardware/printed-parts/enclosure/back-panel/README.md`](../../hardware/printed-parts/enclosure/back-panel/README.md) line 67, on PET-CF heat resistance:
> Service temperature well above the **~30–40 °C cabinet ambient** (compressor + electronics waste heat). Not a thermal bottleneck.

That `~30–40 °C` is the only place anywhere in the repo that names a cabinet steady-state temperature. There is no calculation behind it — no compressor wattage assumption, no duty-cycle assumption, no cabinet-leakage assumption. It exists as a passing parenthetical to justify a filament choice.

[`hardware/future.md`](../../hardware/future.md) line 115:
> Condenser exhaust at 40–50 °C is well within engineered-filament continuous-use range.

Same posture: cited only to justify printed-grille survivability, not as part of a heat-rejection analysis.

[`hardware/future.md`](../../hardware/future.md) line 99 (electronics shelf):
> Heat from the PSU (~5–10 W) sheds via natural convection in the kitchen-ambient air around the shelf; the appliance is not sealed and the condenser fan creates negative pressure that pulls makeup air through every gap, giving slow circulation throughout.

This is about air movement *inside* the appliance enclosure, not between the cabinet and the kitchen.

**Cabinet-side airflow is mentioned but not closed.**

[`hardware/future.md`](../../hardware/future.md) line 95:
> The side faces sit alongside the cabinet's left/right walls with a similar working gap on each side, which is the airflow plenum for the side-to-side condenser path described below.

So the design treats the 2–4" lateral gap as the plenum. That gets air from one enclosure face to the other *inside the cabinet*. It does not get air out of the cabinet to the kitchen.

[`hardware/future.md`](../../hardware/future.md) line 101:
> the condenser's harvested fan pulls cabinet air in through the intake-side grille, across the finned condenser, and out through the exhaust-side grille — a straight pass-through with no redirection

"Cabinet air" is the input. The exhaust goes back into the cabinet on the opposite side. The same air recirculates through the condenser on the next pass, having picked up some number of degrees.

## What's missing

There is no doc anywhere in the repo that:

1. Quantifies the average heat-rejection load on the cabinet (compressor input × duty cycle, plus the few-watt fan + electronics load).
2. Estimates the cabinet's steady-state temperature rise above the kitchen, given a defensible cabinet leakage rate.
3. Defines a maximum acceptable cabinet ambient for the design — both for the appliance's own condenser performance and for whatever the customer stores in the cabinet (cleaning supplies, paper bags, sometimes flammables like rubbing alcohol).
4. Specifies whether the cabinet needs a deliberate vent path (a louvered toe-kick grille, a relief opening at the cabinet rear, an active duct, or a documented door-gap requirement).
5. States customer-side install requirements about cabinet ventilation — analogous to how a built-in dishwasher manual will spec minimum airflow around the unit.

The closest the docs come is the bare assertion of `~30–40 °C cabinet ambient` and the working assumption that the side gaps are sufficient plenum. Both are unaudited.

## Why the gap matters

**Condenser performance.** Refrigeration capacity drops roughly 2–3% per °C of condenser inlet air rise; compressor power draw climbs in parallel. The R-600a harvested-ice-maker loop is sized to its donor application (intake at room ambient). If the cabinet ambient settles at 35–40 °C in steady state, the condenser inlet is 10–15 °C above design, which compounds into longer duty cycles (more heat input, runaway feedback) and reduced pull-down capacity (slower recovery after a fill).

If the loop is marginal at room ambient — it's already running an enlarged custom evaporator coil per [`hardware/assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) — a hot cabinet could push it past the point where the −8 °C evap-coil freeze-protect cutout starts tripping under load, or simply leave the carbonator water above the 4 °C set point during sustained use. Both are observable customer-facing failures.

**Cabinet contents.** Under-sink cabinets store dish soap, dishwasher detergent (some flammable), bleach, ammonia, rubbing alcohol, dish brushes, sponges, paper bags, sometimes potatoes/onions. Heating these to 40 °C for years has consequences — accelerated dish-soap degradation is cosmetic, but a kitchen full of paper bags warmed to 40 °C next to flammable liquids gets close to safety territory that wants a deliberate decision rather than a side effect.

**Acoustic, as a side effect.** Hot cabinet → longer compressor duty cycle → more total compressor-running hours per day. Compressor noise is the dominant noise source in a fridge appliance, and this puts the appliance class somewhere between "quiet fridge" and "loud one" depending on duty.

**Install qualifier.** If the design ends up requiring a vented cabinet (toe-kick louver, rear cutout) to hit its rated performance, that becomes part of the install-readiness profile from the target-market doc. Some kitchens — especially newer custom cabinetry with sealed back panels and tight kick plates — won't have this. Knowing in advance is the difference between "drop-in install" and "your cabinet doesn't meet our requirements."

## Concrete recommendations

The goal is to convert the casual `~30–40 °C` parenthetical into a closed engineering loop with a defensible answer.

1. **Quantify the heat-rejection load.** From [`hardware/assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) or the donor compressor's nameplate: total electrical input under steady-state cycling (W). Apply a sensible duty cycle estimate (e.g., 25–50% steady-state given the cold-core's thermal mass and typical dispense cadence). Add the condenser fan (~3–10 W when on) and the always-on electronics (~5–10 W). Output: a single average-watts-into-cabinet number, with a duty-cycle band.

2. **Estimate cabinet leakage to the kitchen.** Reference any of the residential cabinet-airflow studies, or a defensible bench measurement. A typical 36" base cabinet under a sink has door-gap + plumbing-penetration + cabinet-back-gap leakage that probably falls in 3–15 CFM at a 1–3 °C ΔT — but that's a guess; this is exactly the sort of number to chase a real source for.

3. **Compute steady-state cabinet ambient.** Heat-balance: cabinet rise above kitchen = (W into cabinet) ÷ (mass flow out × specific heat). Express as a band against the leakage range. If the answer is "+3 °C" the problem is moot. If it's "+15 °C" the design owes the customer a vented cabinet.

4. **Decide the design response based on the answer.** Options, from least to most intervention:
   - **Do nothing.** If the heat-balance lands in single-digit °C rise, document the calculation and move on. Update the back-panel README's `~30–40 °C` to a sourced number.
   - **Specify a cabinet vent in the install kit.** A small louvered grille added to the cabinet toe-kick or rear wall during install — analogous to how built-in microwave installs sometimes require a vent cutout. Adds an install step and a cabinet-modification skill requirement.
   - **Active duct.** Route a flexible duct from the appliance exhaust grille through the cabinet rear into the kitchen wall void or into the toe-kick space. Significant install complexity; possibly required only for tight cabinets.
   - **Re-architect the airflow path.** Bring exhaust out the *back* of the appliance and out the cabinet's rear wall (which, in many under-sink kitchens, opens to plumbing space behind), changing the side-to-side passthrough geometry the donor fan was designed for. Probably the worst option per `future.md`'s "the fan is doing exactly the job it was designed for in the donor ice maker" stance — but it's worth naming so it's not implicit.

5. **Write the customer install requirement.** If any cabinet-modification or minimum-ventilation requirement falls out of step 4, it becomes a line in the customer's pre-install checklist (and probably in `marketing/target-market.md`'s qualifying-filters list — alongside "homeowner" and "water line under the sink"). Ring-1 customers can be surveyed against this filter before commitment.

6. **Validate empirically once unit 1 runs.** Instrument the cabinet ambient with a DS18B20 or thermocouple during the acceptance burn-in described in [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md). The burn-in already runs for 8 hours at 75-minute dispense cadence — a single extra probe in the cabinet captures the steady-state cabinet temperature against a known heat input. Compare against the step-3 calculation; tighten the model from real data; lock the install requirement (or the lack of one) accordingly.

## Effort and dependencies

Steps 1–3 are an afternoon of calculation against existing BOM data. No physical work, no hardware, no waiting on suppliers. Step 4 is a decision that follows from step 3's number. Step 5 is a one-paragraph addition to the install guide (which doesn't exist yet — see today's `install-consult-playbook-gap.md` and yesterday's `install-consult-playbook-gap.md` for the surrounding install-doc work). Step 6 happens for free during the acceptance burn-in that's already on the unit-1 critical path.

The risk of skipping this is that unit 1 ships, the cabinet runs hot, the compressor runs more than expected, and either (a) the customer notices the appliance never quite holds 2 °C in summer, or (b) the cleaning supplies under the sink come out warm. Both are recoverable but neither is the "wait, that's *real*?" moment from the target-market doc.

## What I am explicitly not claiming

I am not claiming the loop is undersized, that the cabinet ambient *will* hit 40 °C in service, or that customers *will* report problems. I am claiming the design hasn't yet done the heat-balance that would let anyone answer those questions with a number, and that the only existing reference to cabinet ambient is a casual range in a filament-choice paragraph. Convert the casual range into a sourced number; let the number drive whatever (possibly minimal) design response it deserves.
