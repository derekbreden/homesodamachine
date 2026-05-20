# Workshop-as-factory gap: the residential structure that builds 50 units is never named as a risk surface

**Author:** hourly agent, 2026-05-19
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Distinct from siblings:** 28 prior gap files (22 today + 6 from 2026-05-18) cover the *product* — its acoustic behavior, its leak paths, its CO2 venting, its electrical safety, its faucet penetration, its concentrate microbio, its trademark exposure, etc. — plus the customer-facing surfaces (warranty, RMA, install consult, freight, payment, CO2 supply). **None addresses the physical structure where every Founder Edition unit is fabricated, vented, hydro-tested, brazed, laser-welded, and burned-in.** That structure is Derek's residence. This doc is about the dwelling itself as a risk surface.

---

## TL;DR

The build path documented across [`hardware/assembly/`](../../hardware/assembly/) implies — but never names — a workspace that runs ten distinct process hazards inside what is almost certainly an ISO HO-3 single-family-dwelling homeowner-policy structure:

1. **R-600a venting** of factory hydrocarbon charge from each donor ice-maker (refrigerant-loop.md step 2)
2. **MAP-Pro torch brazing** with continuous argon purge over an open hydrocarbon-bearing loop (refrigerant-loop.md steps 3–5)
3. **180 PSI hydro-test** of welded 316L pressure vessels for 30 min each (pressure-vessel.md step 6)
4. **1500 W handheld fiber laser welding** of stainless plates (XLaserlab X1 Pro per handwork.md)
5. **Hand-tap drilling and threading** of 4 NPT ports × 2 plates × 10 vessels (40 hand-tapped holes — handwork.md)
6. **Stored compressed gas:** argon cylinder + welder-side CO2 cylinder + test-rig CO2 cylinder (regulatory.md "Assembly-time safety"; acceptance-and-burn-in.md "Inputs")
7. **Multi-hour live appliance burn-in** under AC mains + pressurized 90 PSI carbonated-water service (acceptance-and-burn-in.md)
8. **Citric acid passivation** in disposable tubs (future.md "Carbonation subsystem")
9. **Stored food product** — SodaStream concentrate inventory + (eventually) commercial BiB bags
10. **Engineered-filament 3D printing** — PET-CF, ABS, PETG — at scale across hundreds of cumulative hours per unit

[`business/regulatory.md`](../../business/regulatory.md) is comprehensive on **product-level** regulatory posture (EPA 608 carve-out, SNAP approval, UL 60335-2-89 design compliance, CPSC general duty, AIM Act non-applicability, argon purge safety). It is silent on **premises-level** posture: is the workspace zoned for this, insured for this, ventilated for this, fire-rated for this, separated from sleeping/living areas for this?

[`business/incorporation.md`](../../business/incorporation.md) sequences "form NE SMLLC; product-liability insurance" before first paid sale. It does not address the orthogonal exposure — that **all the work happens in a structure whose insurance policy was almost certainly written for someone who does not vent flammable hydrocarbon, fire MAP torches over open refrigerant circuits, hydro-test pressure vessels, or operate Class 4 lasers in their house.**

A grep across the repo for `garage`, `workshop`, `basement`, `shop`, `HO-3`, `business pursuits`, `residence`, `commercial use`, `home business`, `dwelling`, `zoning`, `setback` returns **zero hits** in any context where the workspace itself is the subject. The only "home" in the repo is the *customer's* home (the kitchen the appliance goes into). The dwelling that builds the appliance is invisible.

This is the **biggest single uninsured catastrophic-loss surface in the project today**, and it sits one MAP-torch event away from converting the entire venture from a four-year FE run into a total-loss claim against a homeowner policy that may not pay.

This doc walks the ten process hazards, names what insurance / zoning / code touches each one, and recommends a sequenced response that costs <$500 in the cheap path and ~$1,800–3,000/year in the bonded path.

---

## What's already in the repo (and what it implies about the workspace)

The build path is documented at procedure-level fidelity. Each procedure assumes a workspace exists, and each implies something about it. The reader can reconstruct the workspace by reading sideways across procedures:

### refrigerant-loop.md — the most safety-critical procedure

[hardware/assembly/refrigerant-loop.md](../../hardware/assembly/refrigerant-loop.md) opens with: *"The most safety-critical procedure in the build: the loop is open to a flammable hydrocarbon for several steps, and the argon purge during brazing is load-bearing."*

Step 2 — venting the factory R-600a charge — says: *"Open the valve and vent to atmosphere in a well-ventilated area — outdoors or under a vent hood is preferred — with no ignition sources within 3 m."* That's the only spatial constraint in the entire doc. "Outdoors or under a vent hood is preferred" is permissive — implicitly admitting that the actual venue may be neither.

Steps 3–5 are open-loop brazing with a Bernzomatic TS8000 MAP-Pro torch — *"flow low-pressure argon (a few PSI, **flowing**, not static) through the open loop during the entire loop-open period, sweeping residual fuel out ahead of the heat."* The argon purge is load-bearing, but it is a process control, not a barrier. If the argon flow stops mid-braze (regulator failure, hose pop-off, operator distraction), the failure mode is a flash fire at the joint.

[`regulatory.md`](../../business/regulatory.md) "Assembly-time safety — argon purge during brazing" confirms the framing — *"a torch is applied to copper near an oil-soaked compressor pocket, the flame front pulls residual hydrocarbon into itself"* — but does not name where this happens.

**Implication:** the workspace must be (a) ventilated enough that an unconfined R-600a vent disperses below 1.8% LFL, (b) free of ignition sources within 3 m for vent step, (c) somehow simultaneously tolerant of an open MAP torch for brazing step. These are not mutually exclusive but they are not free in a typical residential garage either. Per UL 60335-2-89 product-design rationale (regulatory.md), the appliance itself is designed against this hazard — the *workspace* gets no such design.

### pressure-vessel.md — the 180 PSI hydro-test

[hardware/assembly/pressure-vessel.md](../../hardware/assembly/pressure-vessel.md) step 6 calls for hydro-test at 180 PSI for 30 minutes per vessel. A liquid-filled test rather than pneumatic test, which is the right call per the procedure's own commentary: *"pneumatic stores ~200× the failure energy at the same pressure."* The hydro stored energy at 180 PSI in a ~600 mL water-filled vessel is ~74 J — large enough to bruise but not to penetrate a wall. A pneumatic test of the same geometry would store ~15 kJ, comparable to a low-power firearm. The hydro choice is the safer choice.

Open Items §1 of that procedure: *"Hydro pass/fail criteria. No committed PSI-drop tolerance over the 30-min hold."* Marginal failures are scheduled to be re-welded and re-tested. That implies a hydro rig that sees repeat use, not a one-shot proof test.

**Implication:** there is a permanent hydro rig in the workspace. Per `purchases.md` §1 the BEAMNOVA pump (0–726 PSI, 3.17 gal reservoir, ACQUIRED), Milton 727 NPT plugs, and SENCTRL pressure gauge are all in hand. The rig is not transient.

### handwork.md — the laser welder

[hardware/handwork.md](../../hardware/handwork.md) repeatedly invokes the **XLaserlab X1 Pro handheld laser welder** for the carbonator's tube-to-plate welds (40 weld inches per vessel × 10 vessels) and for the float-rod tack on the inside face of each bottom plate. Specifications by class: 1080 nm fiber, 1500 W continuous, Class 4 laser product per ANSI Z136.1 (no enclosure exemption for handheld units).

Class 4 laser regulatory: 21 CFR 1040.10 (FDA performance standard) requires the manufacturer to ship interlock/keylock/emission-indicator features — XLaserlab does. **Use** of a Class 4 laser is not federally regulated at the consumer level. State-level: most states have no occupational eye-protection mandate for solo home use. The OSHA personal-protection rule (29 CFR 1910.133) applies to employee exposure, not to a sole proprietor. So legally the laser welder is fine to operate in a residence; the gap is **insurance** and **safety practice**, not licensure.

Eye injury risk: 1080 nm is at the retinal-hazard wavelength range. A direct beam or specular reflection without proper goggles (OD 6+ at 1080 nm) is a retinal-burn event in <100 ms. The XLaserlab ships goggles. Whether the welding zone has interlocks against accidental triggering, whether reflective surfaces are managed, whether a "laser in use" warning is posted at workspace ingress — all undocumented.

**Implication:** a Class 4 laser is permanently installed in the workspace, used routinely.

### acceptance-and-burn-in.md — the multi-hour live appliance test

[hardware/assembly/acceptance-and-burn-in.md](../../hardware/assembly/acceptance-and-burn-in.md) describes burn-in: *"a multi-hour burn-in (with periodic dispenses on a timer, watching compressor cycle count, watching for nuisance freeze-protect trips, watching for leaks, watching for MQ-6 trips)."*

Multi-hour means measured in hours, plural. The unit is live on AC, water-filled, CO2-pressurized to 90 PSI. The bench has a test-rig CO2 source (separate cylinder from the workshop's argon supply), a 5/16" beer line, and a target glass. The unit is unattended during portions of burn-in (otherwise why is the MQ-6 hydrocarbon-sensor trip on the watch list — that's a fire-watch sensor for an unattended unit).

**Implication:** at any given moment in the FE run, there is at least one fully-built appliance running unattended in the workspace, with pressurized CO2 and live water carrying the same failure modes the in-service product will carry. The burn-in unit is not in a fire-rated enclosure. The MQ-6 sensor that protects against R-600a buildup in *customer* installations also protects against R-600a buildup in *this* installation — but a workshop MQ-6 isn't documented, and the appliance's own MQ-6 protects against the appliance's own R-600a, not against a stored donor unit's vented charge or against an argon-purge-failure event.

### purchases.md — the durable equipment inventory

A read across [`hardware/purchases.md`](../../hardware/purchases.md) §1, §2, §16 produces this durable-equipment inventory in the workspace (status: ACQUIRED unless noted):

- XLaserlab X1 Pro fiber laser welder (Class 4) with argon flow setup
- BEAMNOVA hydrostatic test pump (0–726 PSI)
- WEN 4208T drill press
- Bernzomatic TS8000 torch + MAP-Pro 3-pack
- Toptes PT520A hydrocarbon leak detector
- Argon cylinder (welder feed + brazing purge regulator)
- 5 lb CO2 cylinder (Airgas, food-grade, in service three months for the running prototype per purchases.md §2)
- Multiple 3D printers (Bambu A1 / X1C per posts/)
- Various hand tools, taps, dies

This is a small commercial fabrication shop running inside a residential structure.

### What the repo does *not* say

It does not say which room. It does not say whether the room is attached to or separated from sleeping areas. It does not say whether the structure is single-family or attached. It does not say whether the residence has a current homeowner policy, who the carrier is, or whether the carrier has been notified of any of the above activity. It does not say what the local jurisdiction's home-occupation ordinance permits. It does not say whether Derek personally owns the structure (vs. rents — though [`marketing/target-market.md`](../../marketing/target-market.md) "Founder Edition" frames Derek's August 2025 home purchase as the trigger event for the project, so ownership is implied). It does not say whether the structure has the natural-gas service, the electrical service, the ventilation, or the egress that the activity assumes.

---

## The ten process hazards, mapped to insurance and code

For each of the ten hazards, the relevant question is: which insurance policy is supposed to respond if this hazard produces a loss, and does it actually respond?

### Hazard 1 — R-600a venting

The vent is a deliberate atmospheric release of ~15–30 g of pure isobutane per donor unit. The factory release in a 50-unit run produces 0.75–1.5 kg of total release across four years; the per-vent release in a typical 2-car garage of ~7 × 6 × 2.5 m = 105 m³ free-air volume produces a peak concentration of ~0.04 vol % — below the 1.8 % LFL by ~45×. **In ideal mixing.** Real mixing in an unstirred garage with R-600a denser than air (vapor density ~2.0) is not ideal. The gas pools at floor level and disperses slowly.

A naïve venting-then-igniting failure mode requires a floor-level ignition source (a pilot light on a water heater, a gas dryer's standing flame, an extension cord arc, a static-discharge from a synthetic-soled shoe). The mitigation in [`regulatory.md`](../../business/regulatory.md) and the procedure ("no ignition sources within 3 m") addresses sources but not floor-level pooling under thermally stratified conditions, and doesn't address ambient ignition sources outside the 3 m radius if vapor migrates (e.g., into an attached living space).

Insurance angle: most HO-3 policies cover "fire and lightning" as Coverage A peril without exclusion for ignition cause. A fire that originates from R-600a ignition during a vent operation is, on its face, covered. **The exclusion that bites is Section II liability** — if the fire spreads to a neighbor's house or injures a neighbor, the standard ISO HO-3 Section II form has a "business pursuits" exclusion (Exclusion 2.b) that voids liability coverage for damage arising out of or in connection with a business activity. A four-year unfunded run of an under-development consumer appliance is, under any standard reading, a business pursuit. Coverage A pays for *your* house. Coverage E does not pay for *theirs*.

### Hazard 2 — MAP-Pro brazing over an open hydrocarbon-bearing loop

This is the most concentrated ignition hazard in the build. The TS8000 produces a 3,730 °F flame. The braze is on a loop with residual hydrocarbon. The argon purge is the only barrier; the purge cylinder regulator failing or running empty mid-braze is a single-fault-to-fire path.

Insurance: same Section II concern as Hazard 1. Plus a fire that originates here may not be claimable under Coverage A if the carrier's investigator can show "intentional act" or "expected loss" — courts have generally protected accidental ignition during otherwise lawful activity, but a sustained pattern of brazing inside a residence is the kind of fact pattern that turns a coverage dispute into litigation. The carrier doesn't have to deny coverage to make life expensive; they can reserve rights, demand examinations under oath, retain coverage counsel, and effectively gate the customer's recovery on litigation that takes 12–36 months while the customer carries replacement-housing costs out of pocket.

### Hazard 3 — 180 PSI hydro-test

The energy stored is small (~74 J per test); rupture risk is low. The procedure runs 30-min holds × 10 vessels in the FE run prep stock, plus re-tests for marginal failures. Per pressure-vessel.md, the rig is in service.

Insurance: hydro-test failure scenarios that splash water inside a finished space are property-of-yours claims (Coverage A or B). Not high concern. The bigger issue is **operator injury** — a vessel that lets go at a port plug under hand-test pressure can produce an eye injury or a hand laceration. As a solo proprietor with no employees, Derek's own injury is **not** an HO-3 covered event (Section II excludes injury to "you and family members") and is **not** a workers' comp event (no employees, no policy). Personal medical care comes from personal health insurance. Disability-during-recovery comes from personal LTD if Derek carries it (TBD — not documented in repo).

### Hazard 4 — Class 4 fiber laser welding

Worker eye injury (Derek's eye) is the dominant risk. Fire from a misdirected beam on flammable shop material is secondary. The laser itself is a tool; the FDA performance standard puts the safety burden on the manufacturer (XLaserlab), not the operator.

Insurance: an eye injury to Derek is a personal-health-insurance event. A fire is Coverage A (if it stays within the dwelling) and Section II for any spread; same Section II business-pursuits exclusion as above.

### Hazard 5 — Hand-tap drilling and threading

Low hazard. Cut injuries to fingers, eye-debris injuries from breaking taps, small-scale events. Personal-health-insurance.

### Hazard 6 — Stored compressed gas

The argon cylinder (used for laser welder + brazing purge — capacity TBD per purchases.md §16 entry), the welder-side CO2 cylinder, and the test-rig CO2 cylinder are all permanent residents of the workspace. Compressed-gas cylinders that are valve-broken (knocked over, mechanical impact) become uncontrolled propellants — the textbook "torpedo" failure mode that the National Fire Protection Association cites in NFPA 55. Probability is small but consequence in a residential structure is severe (cylinder propagation through interior partitions).

Mitigation is mechanical: chain-securement of cylinders against a structural element. Whether the workspace's cylinders are chained is undocumented. The XLaserlab and brazing setups likely have stands; the test-rig and prototype-runner cylinders are loose unless someone explicitly cared.

Insurance: a cylinder-torpedo event is Coverage A for own-house damage, Section II business-pursuits exclusion for neighbor damage or injury.

### Hazard 7 — Multi-hour unattended live appliance burn-in

[acceptance-and-burn-in.md](../../hardware/assembly/acceptance-and-burn-in.md) puts a powered, water-filled, CO2-pressurized appliance in the workspace for hours, often unattended (otherwise the MQ-6 isn't needed as a watch sensor).

Failure modes the in-service appliance is designed against — backflow vent weep, CO2 leak, water leak, compressor fault — apply equally to a burn-in unit. The in-service appliance is in a kitchen cabinet over a finished floor; the burn-in unit is on a bench over concrete in a workshop. The water-damage exposure for a burn-in leak is lower (concrete vs. finished floor). The CO2-asphyxiation exposure depends on workspace volume + ventilation — see today's sibling [co2-asphyxiation-and-prv-vent-path-gap.md](co2-asphyxiation-and-prv-vent-path-gap.md) for the analysis on the in-service side; the workspace runs the same physics, with worse air-exchange than a kitchen.

Insurance: water damage to the dwelling is Coverage A. CO2 asphyxiation injuring Derek is not covered. Asphyxiation injuring a visitor (a friend dropping by during burn-in) is Section II business-pursuits exclusion territory unless the visitor's presence is non-business — coverage litigation.

### Hazard 8 — Citric acid passivation

Low hazard. ~4 % food-grade citric solution in a disposable plastic tub. Mild eye/skin irritation. Personal-health-insurance.

### Hazard 9 — Stored food product

SodaStream concentrate is stable for months at ambient. Storage is unremarkable. BiB inventory (if Derek goes that route for future ring-2+ acceptance testing) would be commercial-format syrup, also stable at ambient. No insurance hook.

### Hazard 10 — 3D printing fumes

PET-CF, ABS, and PETG release small amounts of styrene, butadiene, and other VOCs during print. Long-duration cumulative exposure to ABS is the most-studied; the consensus is that hobby-scale printing in a ventilated space is below acute-toxicity thresholds but above the noise floor for chronic respiratory irritation. The FE run involves hundreds of hours of cumulative print time per unit across enclosure shells, foam-shells, faucet shells, hopper, nameplate, etc.

Insurance: chronic personal exposure is not insurance-coverable; it's a personal-health-management issue (an AC Infinity exhaust kit at <$200 closes the gap).

---

## The homeowner policy and the business-pursuits exclusion

The standard ISO HO-3 policy form has two relevant exclusions that converge on this scenario:

**Section II — Liability Coverage, Exclusion 2.b:** *"Personal Liability and Medical Payments to Others do not apply to bodily injury or property damage arising out of or in connection with a business engaged in by an insured."* "Business" is defined elsewhere in the form as a trade, profession, or occupation, including a part-time or occasional one. ISO has tightened this language across the 2011 and 2022 form revisions to reduce the wiggle room courts previously found for hobbyist/occasional carve-outs.

**Section II — Exclusion 2.l (or similar in 2022 form):** Excludes liability arising from professional services rendered for a fee. Less relevant — Derek isn't selling professional services — but the install-consult deliverable promised in [`target-market.md`](../../marketing/target-market.md) Founder Edition framing arguably triggers this if a customer is injured by advice Derek gave on the Zoom call.

**The "incidental business" exception** in some carriers' HO-3 variants (Allstate, State Farm, USAA, others) permits up to $2,000–5,000 in annual revenue from incidental home-based activities with no additional premium, provided no employees, no customer visits, no on-site sales, no inventory above a threshold. The threshold is the variable that disqualifies this project — at the FE Edition price point, **one sale per year exceeds the incidental-business cap by 1.5–3.75×.**

**The two clean paths around the exclusion:**

1. **Endorsement for home-based business**, sometimes called "in-home business" or "home enhancement business endorsement." Costs $50–250/year. Increases the Section II limit to $25,000–50,000 for business-arising claims and removes the exclusion for the specific listed activity. Underwriting question matrix at application is the gate: most home-business endorsements are scoped for tutoring, ebay reselling, freelance writing, photography studios. **A small-batch manufacturer of refrigerated pressure vessels with hydrocarbon refrigerant and Class 4 laser welding is outside the scope of every "home-business endorsement" the author has been able to research.** Carriers route this to the standalone commercial form.

2. **Standalone commercial general liability (CGL) + product liability policy.** Costs in the $1,500–3,000/year range for a sole proprietor / SMLLC at this scale with no employees, no premises away from home, and a low-volume hand-built product. Carriers writing this space include Hartford, Hiscox, Next Insurance, Thimble, biBERK (a Berkshire subsidiary), Coterie. The underwriter's no-go list will include hydrocarbon refrigerant in some cases, pressure vessels in some cases, food-contact equipment in some cases. **Underwriting submission for this project will require a custom-narrative cover letter that pre-empts the obvious objections** — the UL 60335-2-89 design compliance work, the ASSE 1022 backflow standard, the hydro-test program, the argon purge regimen, the SS material selection rationale, etc. — i.e., the work documented in [`regulatory.md`](../../business/regulatory.md) and [`pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) is **also the insurance application's strongest exhibit.**

A clean CGL + product policy at $2K/year that pays out on a Section II-equivalent business-related claim is the right answer once the FE run starts shipping; the question is timing. Per [`incorporation.md`](../../business/incorporation.md) sequence step 2 ("Before first paid sale: form NE SMLLC; product-liability insurance"), insurance is already named as a pre-first-sale gate. **What is not in the repo is what to do *before* the first paid sale**, during the 6–24 month FE-prep window where the workshop is fully operational with no insurance and no LLC.

---

## Zoning and home-occupation ordinance

Nebraska (Derek's state per [`incorporation.md`](../../business/incorporation.md) reference to "NE SMLLC") delegates land-use regulation to municipalities and counties. The actual operative rule is local. Without knowing Derek's specific municipality this analysis is necessarily generic, but the common pattern across Nebraska's larger cities (Omaha, Lincoln, Bellevue, Grand Island, Kearney) for residential zoning home-occupation ordinances is:

**Common permissive provisions** — most home occupations are permitted as accessory uses subject to:
- No on-premises customer traffic (or limited, by appointment)
- No employees other than household residents
- No outdoor storage of equipment or materials
- No visible signage beyond a small name plaque
- No noise, vibration, fumes, or hazardous activity perceptible at the property line
- Limited percentage of dwelling floor area dedicated to the use (typically 25–50 %)

**Common prohibited provisions** that this project may trigger:
- "No use of flammable or combustible materials beyond ordinary household quantities" — argon and compressed-gas cylinders may or may not count, depending on jurisdiction; a hydrocarbon-charged donor refrigerator with its R-600a still in it is more clearly a regulated material
- "No manufacturing, assembly, or fabrication" — sometimes specifically prohibited, sometimes permitted only for "handcrafts and personal artisan production"; an FE production line of 12+ units/year sits at the ambiguous edge
- "No commercial equipment requiring three-phase electrical service or industrial ventilation" — likely not triggered (the XLaserlab and BEAMNOVA both run on single-phase 120/240 V)
- "No activities producing detectable odor, smoke, or particulate beyond the property line" — citric passivation smell is mild, MAP-torch combustion produces minimal odor, R-600a vent is odorless (it's odorized in some natural-gas applications but isobutane refrigerant grade typically is not); the practical risk is a neighbor smelling brazing flux smoke and complaining

**The enforcement reality:** zoning enforcement in Nebraska (and most US jurisdictions) is **complaint-driven, not patrolling-driven.** A workshop that produces no neighbor-visible nuisance can run for years without zoning attention. A neighbor complaint about smoke, noise, traffic, or unusual deliveries (FedEx/UPS dropping ice maker cartons, USPS dropping consumable-grade cylinders) triggers a code-enforcement visit, after which the operator is given a curative window (typically 30–90 days) to either come into compliance or face escalating fines. **Few home-occupation operators receive criminal charges.** The cost is administrative — fines, forced cessation, and the conversion of a permitted "incidental" activity into one that requires relocation.

The Standard Edition will not be feasible from a residential workshop. The FE run might be. The decision to relocate to a small commercial space — **a non-residential 200–400 ft² unit at $300–600/month in a Nebraska secondary market** — is sequenced behind FE revenue, but should be **identified in advance** so the move isn't reactive after a zoning complaint.

---

## Local code: building, fire, and mechanical

Nebraska adopts the International Codes (IBC, IFC, IMC) with state amendments. Municipalities further amend locally. The provisions that touch this workspace, listed by code:

**IFC (International Fire Code) — chapters that touch the workspace:**

- **Ch 50 (Hazardous Materials, general):** sets thresholds for permit-required quantities of hazardous materials. R-600a is a Class IA flammable gas; the permit threshold is typically 150 lb (~68 kg) for storage in a residential occupancy. The project's worst-case storage moment is a single donor ice maker waiting for vent (~30 g charge) — three orders of magnitude under threshold. **No permit needed.**
- **Ch 53 (Compressed Gases):** sets requirements for cylinder securement (chain or strap to non-combustible support), separation distances between oxidizers and fuels (argon is inert — not a fuel, not an oxidizer — but stored adjacent to an oxidizer would matter for some shops), and labeling. The project's argon + CO2 inventory falls below the permit threshold; **practice requirements still apply** (cylinder chaining, valve caps, separation from heat sources).
- **Ch 26 (Welding and Other Hot Work):** requires hot-work permits for fixed installations in commercial buildings. Residential workshops are excluded. *But* a homeowner-insurance carrier's investigator can still cite hot-work practice failures (no spark blanket, no charged fire extinguisher within reach, no fire watch for ≥30 min post-work) as policy-noncompliance for a fire originating from brazing. The IFC chapter 26 practice list is the de-facto checklist a carrier's investigator will consult.

**IMC (International Mechanical Code):** requires mechanical ventilation in occupancies handling flammable refrigerants. Specifically NFPA 55 + IMC chapter 11 set air-change-per-hour requirements for refrigerant-using equipment rooms. **Residential garages are excluded from the chapter 11 requirements** (chapter 11 applies to commercial refrigeration); but the underlying physics — flammable gas wants air exchange — doesn't care about the code's occupancy distinction.

**Practical fire-watch and ventilation checklist that the workspace should pass, regardless of whether code requires it:**

1. A 10-lb ABC dry-chemical fire extinguisher within 10 ft of the brazing station, inspected annually, tag-current
2. A second extinguisher within 10 ft of the laser welding station
3. A non-combustible (welder's spark blanket or stainless table) work surface for all hot-work operations
4. Workspace ventilation: a passive vent (door open + window open at opposite ends) producing ≥4 air-changes-per-hour during vent-and-braze operations; an active vent (AC Infinity Cloudline or equivalent in-line duct fan) at ≥150 CFM is the upgrade
5. A floor-level R-600a detector with audible alarm (Honeywell SX-200, MQ-6 dev module, or similar — under $100)
6. A non-combustible storage cabinet for the SodaStream concentrate inventory + the BiB inventory; commodity Justrite/Eagle yellow flammables cabinet is overkill for the actual flammability (Pepsi concentrate is not flammable) but signals to a future insurance inspector that the workspace was operated with the right hygiene
7. Chained securement of every compressed-gas cylinder against a structural element
8. A post-hot-work 30-min fire watch after every braze session before leaving the workspace
9. A workspace separation from sleeping areas with a minimum 1-hour-fire-rated assembly (residential garage drywall typically achieves 5/8" Type X = 1 hour; if the workshop is a basement it may share unfinished structure with bedrooms, which is the worst-case configuration)

This is not a code-mandated checklist for a residential occupancy. It is the **defensible-operation checklist** that closes the insurance / liability gap from "amateur did something stupid" to "informed operator followed industry hot-work practice." The materials cost is <$500 (extinguishers $80, cylinder chains $30, R-600a detector $35, exhaust fan $150, spark blanket $40, fire-rated drywall assembly varies). The procedure cost is the 30-min fire watch on every braze session.

---

## Sequenced recommendations

Aligned with the project-stance frame [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md) uses: pre-revenue, safety-driven, voluntary compliance, no insurance until first sale. The recommendations below are sized to that posture.

### Cheap and immediate (this week, <$500)

**W1. Add a `business/workshop.md` doc** that names the workspace explicitly and inventories the ten process hazards. The document is the artifact. It also serves §183 hobby-vs-business defense (per [`incorporation.md`](../../business/incorporation.md) "The §183 question is the real one") by demonstrating that the workspace is operated with informed safety practice, not casually.

**W2. Buy and place the defensive-operation checklist items above** (W1–W9): two extinguishers, cylinder chains, R-600a detector, spark blanket, fire-rated drywall verification, flammables cabinet decision. Each is sub-$200, all together ~$450 plus the exhaust fan if not present.

**W3. Establish a written hot-work procedure** that lives alongside [`refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) and references the workspace doc from W1. The procedure formalizes the 30-min fire watch, the spark-blanket placement, the argon-flow verification before strike, the extinguisher proximity check. This is one page of text. It closes the "informed operator" gap for any future insurance underwriter or post-loss adjuster, and the project has already done the equivalent work for every other safety-critical procedure (the regulatory.md "Assembly-time safety" section is the template).

**W4. Photograph the workspace as-built**, dated, with the W2 items in place. Archive in the per-project log directory (alongside `logs/` if that convention extends to the workshop). Photos are the evidence of "the workspace was operated this way as of date" — useful for insurance application, useful for §183 defense, useful for the eventual day Derek needs to demonstrate a years-long pattern of safety practice.

### Pre-first-sale (closing the LLC + insurance gate from `incorporation.md`)

**W5. Insurance application narrative.** Per the "Standalone CGL + product policy" path above. Write a 2–3 page cover narrative that pre-empts the obvious underwriter objections, citing the UL 60335-2-89 design work, the ASSE 1022 backflow, the SS 316L material selection, the hydro-test regimen, the argon purge protocol, the workshop fire-watch protocol from W3. Submit to Hartford, Hiscox, Next, biBERK, Coterie in parallel. Expect 2–4 declinations and 1–2 quotes. **The work to write this narrative is largely already done in the repo** — the cover letter is mostly a project-summary that links to the regulatory.md, pressure-vessel.md, and (new) workshop.md documents.

**W6. Notify the homeowner-insurance carrier** in writing that an incidental home-based manufacturing business is operating from the premises, and request either an in-home business endorsement (likely declined per the analysis above) or written acknowledgment that no incremental coverage is needed. Notification preserves coverage if a non-business-related claim later arises (a kitchen fire unrelated to the workshop — covered with notification, potentially contested without it). **Failure to notify is the single biggest preserves-the-claim/loses-the-claim variable** in any future loss event. Cost: $0 plus a phone call.

**W7. Personal LTD insurance review** — if Derek's day job carries group LTD (employer-paid disability), confirm whether off-the-job injury during this side activity is covered. Most group LTDs are no-fault on injury cause; some have exclusions for "intentional acts" or "hazardous avocations." If the policy excludes, supplement with an individual LTD policy ($50–150/month) before the FE run starts shipping.

### As FE revenue arrives (during the four-year FE run)

**W8. Reassess workshop relocation** as soon as the FE run is generating cash flow sufficient to support $400–700/month in commercial rent. A small commercial unit in a Nebraska secondary market — light-industrial zoning, 200–400 ft², with concrete floor, garage door, single-phase 240 V service — runs $300–600/month. **The economic case for moving lands somewhere between unit 10 and unit 25 of the FE run**, depending on whether ring-1/ring-2 pricing actually clears $7,500 ASP (per [`order-and-payment-flow-gap.md`](../2026-05-18/order-and-payment-flow-gap.md) and [`target-market.md`](../../marketing/target-market.md) "rings of trust"). Three reasons to move beyond the obvious zoning/insurance arguments:
  - Standard Edition build cadence will require it anyway
  - The neighbor-complaint risk grows with output volume
  - The structural separation of "home" and "factory" simplifies §183 defense and §174 R&D expensing (the commercial space rent is a clean line-item; a home-office percentage is a more contested deduction)

**W9. Workers' comp + business owner's policy (BOP)** at the point Derek has any non-Derek person doing build work for cash — including a single part-time helper. This is the trigger that converts the entire insurance regime from "sole proprietor solo" to "small employer" and adds workers' comp as a state-mandated additional policy. **Decision point only — do not pre-buy.**

### As Standard Edition opens (years 4–5)

**W10. Recall coverage** as a separate endorsement on the CGL+PL policy. Most general product-liability policies do *not* cover recall costs — only third-party-injury costs from an injury that did happen. A recall cost (notifying customers, retrieving units, repairing, re-shipping) is typically a separate endorsement at $500–2,000/year. This is the right time to add it because the field population grows past the founder's personal-Rolodex limit.

**W11. The Standard Edition workspace will not be residential.** Plan around that. This is not a recommendation; it is a fact the project should internalize four years before it bites.

---

## Why this matters at Founder Edition specifically

[`target-market.md`](../../marketing/target-market.md) frames the FE pitch as: *"a hand-built, numbered kitchen appliance"*, *"hand-built by the founder one at a time"*, *"the founder is the factory"*, *"the brand is a person"*. The marketing copy is committing the founder's personal time to each of fifty units. **The marketing copy is also implicitly committing the founder's personal liability surface to each of fifty units**, because the founder is sole-prop until incorporation and the structure that produces each unit is the founder's personal residence.

A loss event that destroys the workshop also destroys:
- The XLaserlab welder (~$3,500 replacement, plus 8–12 weeks lead-time)
- The hydro-test rig and its calibration
- Any work-in-progress vessels at any stage of welding/passivation
- Any donor ice makers in inventory
- Any concentrate inventory
- The per-serial log archive (if local-only, per Open Items in `finish-pack-ship.md`)
- The founder's personal residence
- Most relevantly: **the production capacity** for the remainder of the FE run

The FE run is the entirety of the project's revenue path for ~4 years. A six-month workshop outage to find a replacement venue and re-equip is not a recoverable interruption from a customer-relationship standpoint. The customer at unit 27 is reading the radio silence in real time. The FE buyer at unit 41, who deposited 36 months ago, has standing to demand a refund — and per [`order-and-payment-flow-gap.md`](../2026-05-18/order-and-payment-flow-gap.md) the project hasn't decided what its refund policy is yet.

The FE pitch's specific framing of *"hand-built by the founder"* makes the workshop existentially load-bearing in a way that a contract-manufactured product would not be. **Insuring the dwelling against catastrophic loss with the right policy is not a generic small-business hygiene item; it is the single biggest production-continuity lever the project has.** The cost to close the gap is $0 (cheap path: W1–W4, W6) up to ~$2,500/year (full path: add CGL+PL at first sale).

---

## What this doc does not address

By scope:

- **The actual identity and condition of Derek's workspace** — square footage, garage vs. basement vs. detached structure, current ventilation, current electrical service, current fire-rated separation. The doc assumes generic residential garage parameters. Derek can sanity-check each section against the actual space.
- **Carrier-by-carrier comparison shopping** — the listed carriers (Hartford, Hiscox, Next, biBERK, Coterie) are the major players writing micro-manufacturer policies, but the specific quote depends on submission and is not predictable from this analysis. Plan for 4–6 weeks of broker / direct-carrier conversation before binding.
- **The §174 R&D expensing implications** of capitalized workshop tools (XLaserlab, BEAMNOVA) — out of scope; addressed at [`incorporation.md`](../../business/incorporation.md) "§174 and the moving-target caveat" pending preparer confirmation.
- **The interaction with the rings-1-and-2 pricing** — selling units below the public-facing $7,500 to friends and family does not change the workshop's risk surface, but may affect the insurance-application narrative (the underwriter cares about per-unit AGI, not per-unit pricing). Cross-link to [`target-market.md`](../../marketing/target-market.md) "rings of trust" and [`order-and-payment-flow-gap.md`](../2026-05-18/order-and-payment-flow-gap.md).
- **Catastrophic event response plan** — if the workshop does burn or the founder is incapacitated, what happens to in-progress orders, deposited customers, the carrier-tracking log, the per-serial archive. This is the bus-factor gap. Out of scope for this doc; flagged here for a future hourly agent.

---

## Cross-references

Repo files referenced or directly relevant:

- [`hardware/assembly/refrigerant-loop.md`](../../hardware/assembly/refrigerant-loop.md) — hydrocarbon venting and brazing procedure
- [`hardware/assembly/pressure-vessel.md`](../../hardware/assembly/pressure-vessel.md) — hydro-test procedure
- [`hardware/assembly/acceptance-and-burn-in.md`](../../hardware/assembly/acceptance-and-burn-in.md) — multi-hour live appliance burn-in
- [`hardware/handwork.md`](../../hardware/handwork.md) — XLaserlab Class 4 laser welding
- [`hardware/purchases.md`](../../hardware/purchases.md) — durable workshop equipment inventory
- [`business/regulatory.md`](../../business/regulatory.md) — product-level regulatory posture; silent on premises-level
- [`business/incorporation.md`](../../business/incorporation.md) — LLC sequencing; names "product-liability insurance" as a pre-first-sale gate but doesn't scope it
- [`marketing/target-market.md`](../../marketing/target-market.md) — "founder is the factory" framing

Sibling 2026-05-18 todo files this doc complements but does not duplicate:

- [`appliance-freight-bench-gap.md`](../2026-05-18/appliance-freight-bench-gap.md) — cargo insurance for the freight leg (different policy, different exposure)
- [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md) — hazmat shipping for cylinder service (different policy, different exposure)
- [`warranty-and-rma-gap.md`](../2026-05-18/warranty-and-rma-gap.md) — post-delivery failure response (different surface)
- [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) — the Zoom call at customer install
- [`order-and-payment-flow-gap.md`](../2026-05-18/order-and-payment-flow-gap.md) — payment, FTC, Stripe reserves
- [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md) — `/u/NNN` software portal

Sibling 2026-05-19 todo files this doc does not duplicate: all 22 — none of them addresses the dwelling itself.
