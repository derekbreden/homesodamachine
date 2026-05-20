# Countertop faucet-penetration gap — the highest-stakes install step has no owning doc

**Author:** hourly agent, 2026-05-19 (evening)
**Status:** recommendation only — not for direct execution
**Audience:** Derek, future agents

**Distinct from siblings today and yesterday:**
- Yesterday's [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) names Phase B step 1 as "drill the countertop" and references the *not-yet-written* `install-above-counter.md` ([I3](../2026-05-18/install-consult-playbook-gap.md)). That sibling owns the **call orchestration** — agenda, prep, recording, welcome letter. It explicitly defers the actual drilling procedure to I3. **This todo is what I3 needs to start from.**
- [`faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) is the **factory** procedure for the above-counter sub-assembly. Its scope statement is explicit: "*Not in scope: countertop drilling itself; the customer-side install steps.*" Its open item #5 names `install-above-counter.md` as a TBD placeholder with no owner.
- Today's [`above-counter-ux-gap.md`](above-counter-ux-gap.md) covers what the display, air switch, and audible feedback **do** once the appliance is installed. This gap covers **how the appliance gets installed at all** — specifically the irreversible, customer-physical step that drills a hole through their countertop.
- Today's [`enclosure-exterior-doc-gap.md`](enclosure-exterior-doc-gap.md) is about the under-counter appliance's exterior surfaces (front, sides, top funnel). Different physical surface, different design problem.
- Today's [`water-damage-containment-gap.md`](water-damage-containment-gap.md) covers what happens when the appliance leaks **after** install. This gap covers a different damage pathway entirely — the install step itself cracking a $5,000+ stone slab.
- Yesterday's [`order-and-payment-flow-gap.md`](../2026-05-18/order-and-payment-flow-gap.md) and [`warranty-and-rma-gap.md`](../2026-05-18/warranty-and-rma-gap.md) are commerce and post-purchase. The slab-cracking liability question this todo raises (P3 below) belongs in both of those docs eventually, but the *substance* of what could go wrong at install lives here.

---

## TL;DR

Every customer install requires drilling a **1-3/8" (34.93 mm) hole through the customer's kitchen countertop** ([`hardware/assembly/faucet-and-umbilical.md:3`](../../hardware/assembly/faucet-and-umbilical.md), [`hardware/harvested/touch-flo-faucet/valve-body-reference/valve-body-geometry.md:6`](../../hardware/harvested/touch-flo-faucet/valve-body-reference/valve-body-geometry.md)). This is the **single most consequential, irreversible, customer-physical step in the entire Founder Edition install flow.** It is named in three repo docs and owned by zero:

1. [`hardware/assembly/faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) — "**Not in scope:** countertop drilling itself"
2. [`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) — install kit BOM does not include a drill bit, a hole template, a chip-out backer, a cooling rig, or a slab survey checklist
3. [`todo/2026-05-18/install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) — Phase B step 1, "Drill the countertop (the highest-stakes step; the founder watches and confirms bit, depth, hole location before the customer pulls the trigger)" — but the procedure being confirmed is `install-above-counter.md`, a **TBD placeholder**

The marketing site states the install is "**plug and play — under an hour, no plumber, no special tools**" ([`marketing/target-market.md:15`](../../marketing/target-market.md)). At Founder Edition pricing — $7,500 from a person the customer has never met, who built the appliance one at a time — that sentence is a load-bearing trust claim. Drilling a 1-3/8" hole through engineered stone with a diamond core bit is **not** "no special tools" and is **not** what most kitchen-appliance buyers think "plug and play" means. The gap between the claim and the reality is large enough that the customer will, on the call, do one of three things: (a) refuse to drill, (b) drill and damage their counter, or (c) drill successfully because they happened to have the right gear. The current playbook bets the entire install on (c) without doing anything to make (c) more likely.

This is also a **legitimacy hinge** on the customer side. The customer's slab cost them $3,000–$10,000 (granite/quartz/quartzite, typical kitchen). If the founder is standing on Zoom watching them drill a hole through it with a $40 Amazon bit and no cooling rig, the *appearance* of the install is more "DIY home improvement" than "white-glove premium appliance install." The Founder Edition story does not survive a cracked slab.

This todo is the doc-first playbook for what the drilling procedure looks like, what's in the install kit, what the slab-cracking liability story is, and what no-drill alternatives exist — none of which is currently written down.

---

## Why this is not the install-consult gap

The install-consult playbook is the **call**. It owns the founder's 90 minutes with the customer. It explicitly defers `install-above-counter.md` as a separate document, because writing the content of the install guide is a separate workstream from orchestrating the call that walks through it.

I3 in the install-consult sibling describes the **scope** of `install-above-counter.md` in seven bullets ([`install-consult-playbook-gap.md:112`](../2026-05-18/install-consult-playbook-gap.md)):

> - Countertop drilling — recommended bit per material (granite: diamond core bit; quartz: same; laminate: hole saw), depth, location
> - Drop-through-from-above sequence — …
> - Slide-the-keyhole-plate …
> - Washer + shank-nut tightening …
> - Blue-ring-into-blue-bulkhead rule …
> - Umbilical trim step …
> - Cold-water line tap …
> - CO2 cylinder connection …
> - First-pour walkthrough …

The drilling bullet is one of nine. **It needs to be its own document, not a bullet.** Everything below "drop-through-from-above" is procedural assembly on parts the founder built and tested. Drilling is the only step that touches **the customer's home in a permanent, irreversible way**, and the only step where a $7,500 install can break $5,000 of someone else's property in eight seconds.

The right ordering is:
1. (this todo) Define what could go wrong with drilling, what the no-drill alternatives are, what the slab-survey checklist is, and what the install kit needs to contain so that drilling has the highest possible success rate.
2. (then I3 sibling) Write `install-above-counter.md` with the drilling section as a substantial standalone chapter, citing this analysis.

---

## What exists today

### The mechanical constraint

The faucet shank is **11 mm OD × 50 mm long** ([`hardware/harvested/touch-flo-faucet/valve-body-reference/valve-body-geometry.md:63`](../../hardware/harvested/touch-flo-faucet/valve-body-reference/valve-body-geometry.md)). It passes through a **34.93 mm (1-3/8") hole** with substantial radial clearance; the body's 31.50 mm OD bottom face acts as the retention shoulder. The under-counter keyhole plate ([`hardware/cut-parts/faucet/touch-flo-under-counter-plate/`](../../hardware/cut-parts/faucet/touch-flo-under-counter-plate/)) is 0.060" 304 SS, 54.35 mm OD, and is engineered to slide laterally onto a dangling umbilical.

1-3/8" is the **U.S. standard kitchen-faucet hole size** (the "single-handle faucet" standard). This is genuinely good news — many existing kitchen sinks already have a 1-3/8" hole that's currently filled with a sprayer, soap dispenser, or blank plug. **Reusing an existing 1-3/8" hole eliminates drilling entirely.** This is the most leveraged finding in this entire todo and is currently undocumented anywhere in the repo. See C5 below.

### Materials reality

US homeowner countertops at the $200K+ household income tier (the Founder Edition center-of-bullseye per [`marketing/target-market.md:68`](../../marketing/target-market.md)) are predominantly one of:

| Material | Share at $200K+ | Drillable? | Risk profile |
|---|---|---|---|
| **Quartz (engineered stone)** | ~35% | Yes, with diamond core bit + water cooling | **High.** Resin binders crack/chip; manufacturers often void warranty on field-drilled holes. Caesarstone, Silestone, Cambria explicitly forbid post-install drilling in their warranty docs. |
| **Granite** | ~25% | Yes, with diamond core bit + water cooling | **Medium.** Stronger than quartz against the drill but susceptible to thermal shock; the slab can crack on the underside or radially from the hole as the bit heats. |
| **Quartzite (natural stone)** | ~10% | Yes, with diamond core bit + water cooling | **High.** Harder than granite (Mohs 7), longer drill time, more heat, more risk. |
| **Solid surface (Corian etc.)** | ~10% | Yes, with hole saw | **Low.** Forgiving; field-repairable. |
| **Laminate** | ~10% | Yes, with bi-metal hole saw | **Low.** Easy, but chips at the top surface without a backer. |
| **Butcher block / wood** | ~5% | Yes, with Forstner bit | **Low.** Forgiving. |
| **Soapstone / marble / concrete / sintered porcelain (Dekton)** | ~5% | Material-dependent | **Variable.** Sintered porcelain (Dekton, Neolith) is **brutally hard** — Mohs 9, sintered, ~$2K of slab can chip catastrophically. Some installers will refuse to drill it post-install. |

The "granite: diamond core bit; quartz: same; laminate: hole saw" bullet in the install-consult I3 covers three rows out of seven, and the three it picks are the easy cases. Sintered porcelain is the worst case and is not mentioned anywhere in the repo.

### Slab-cracking liability

The repo's commercial documents do not address what happens if the drill cracks the customer's slab. Specifically:

- [`business/terms-and-conditions.md`](../../business/terms-and-conditions.md) — does not exist in the repo (search returns nothing for "terms-and-conditions" or "liability" or "warranty")
- [`todo/2026-05-18/warranty-and-rma-gap.md`](../2026-05-18/warranty-and-rma-gap.md) — covers appliance defect/repair, not customer-property damage during install
- [`todo/2026-05-18/order-and-payment-flow-gap.md`](../2026-05-18/order-and-payment-flow-gap.md) — covers checkout and refunds, not install-damage liability

In a Ring 1 install, the founder is on Zoom watching the customer drill. **If the slab cracks during that drill, who pays?** The legal answer is "the customer, because they are doing the work in their home" — but the *relationship* answer is "the founder, because they sold the customer on this install, and the customer would not have been drilling at all if the founder hadn't said it was easy." The relationship answer wins at Founder Edition pricing.

This means the founder is on the hook, at minimum implicitly, for ~$3,000–$10,000 of slab replacement on every install where drilling goes wrong. At 12 units/year (the marketing-target build cadence per [`marketing/target-market.md:182`](../../marketing/target-market.md)), even a 5% failure rate on stone drills implies ~$2,000–$5,000/yr in implicit liability — net of any margin on the $7,500 unit. The math on this is not catastrophic but it is not zero either, and it is currently uncalculated.

### Install kit reality

[`hardware/bom.md` §14](../../hardware/bom.md) ("Install kit") has **one entry**: the Mudder PEX/PE tube cutter, $4.29/build. There is no drill bit, no hole template, no chip-out backer, no slab-survey checklist, no painter's tape, no water cooling source. The customer is expected to provide all of these.

That expectation is plausible for a Ring 1 friend ("Derek is going to bring the drill") and not plausible for a Standard Edition cold buyer ("I just got this $5,500 appliance, what do you mean I need to buy a $60 diamond bit?"). The install kit's current scope (cutter for the umbilical) was sized when "drilling" was implicitly someone else's problem. Once the drilling step is owned by *anyone*, the kit needs at least: a hole template, a chip-out backer, painter's tape, and a written matrix of which bit to use for which material.

---

## Specific gaps

The gaps below are sized for individual follow-up tickets. Each one is doc-first; install-kit BOM additions follow.

### P1 — Write the canonical countertop-drilling procedure

A single doc — call it `hardware/assembly/countertop-drilling.md` (parallel to the rest of `hardware/assembly/`, even though this is a customer-side step, because the founder is the responsible party on the Zoom call). It is the deep version of what `install-above-counter.md` references; the install guide cites it but doesn't repeat it.

Section structure:

1. **Pre-drill slab survey.** Material identification (the founder's slab-ID matrix — photos, look-up table), edge-distance minimum (typically 4" from any slab edge to avoid stress concentration), under-counter visual check for hidden braces / sink rim curl / cabinet web that would obstruct the shank stack. Customer takes a photo, founder confirms before the drill turns on.
2. **Hole location.** Distance from sink rim (typically 1.5–2" back from the rim, in the deck behind the sink, not on the sink rim itself); distance from backsplash (clearance for the body OD plus a finger-width for cleaning); clearance from existing fixtures (single-handle faucet, soap dispenser, sprayer).
3. **Bit selection table.** Material → bit type → bit size → manufacturer recommendation → expected drill time → cooling requirement. Should be a one-page table the customer can hold next to their countertop.
4. **Cooling setup.** Stone drilling requires constant water. Two options: (a) the "two-cup" method (customer keeps a Solo cup of water and a sponge at the drill site; pauses every 15 seconds to dip-cool), (b) the "modeling-clay dam" method (build a ~1/2" ring of clay around the planned hole, fill with water, drill through the puddle). Both methods are crude; both work; both are repo-novel content.
5. **Chip-out prevention.** Painter's tape on top of the slab to reduce top-side spall; a backer board (¼" plywood scrap, supplied or sourced) on the underside of the slab held by a magnetic base or a tape strap, drilled into as the bit exits. This is the **single most leveraged technique** for protecting the slab and is absent from every doc in the repo.
6. **Speed/pressure profile.** Slow start (centering with a pilot dimple or a centering jig), low speed (~500 RPM for diamond cores), light pressure, frequent retraction to clear slurry. The single most common amateur mistake is high pressure + high speed = hot bit + cracked slab.
7. **Recovery from partial failure.** What to do if the bit binds, the hole is offset, the top surface chipped: founder's escalation tree, slab-fabricator referral, glue-and-fill repair (for laminate), countertop-replacement option (for stone, this is a relationship-breaking event and needs its own handoff).
8. **Photographs of a real drill** — staged in the founder's own kitchen, on a representative material (probably granite — most common $200K+ material), with the actual bit + cooling setup + backer.

**Estimated effort:** ~2 days of writing + 0.5 day of photography in the founder's own kitchen + ~0.5 day of researching the per-material bit matrix (the granite/quartz/quartzite numbers exist online; sintered porcelain takes more digging). Most of this is content the founder already knows but hasn't written down, plus targeted research on the harder materials.

### P2 — Design the hole template

The cheapest, highest-leverage piece of hardware in the entire install kit is **a printed paper hole template** with a 1-3/8" circle, registration marks, and a recommended-distance-from-rim guide. Cost: $0.05 of paper, $1 of cardstock if thicker. Eliminates "where do I drill?" entirely.

Better version: a **plastic hole template** (laser-cut from 1/16" acrylic by SendCutSend, ~$3) that the customer tapes to the slab. The acrylic is rigid, holds its shape, and survives the inevitable spilled water. Print the template with a pilot-dimple location at the 1-3/8" hole center and a centering hole for a marker.

Best version: a **printed jig** (PETG, ~$1.50 of filament) that captures the diamond core bit at the start of the drill, preventing the bit from skating across the slab in the first few seconds — the period when most chip-out happens. The jig is removed once the bit has bitten ~3 mm into the surface. This is engineering the founder can do; doesn't need to be sourced.

The hole-template decision is independent of the drilling-procedure doc and can be designed in parallel.

**Estimated effort:** ~0.5 day for the paper template; ~1 day including the printed-PETG drill-start jig CAD + first physical test.

### P3 — Establish the slab-cracking liability stance

A one-page section in `business/terms-and-conditions.md` (which does not yet exist) and a corresponding paragraph in the Founder Edition welcome letter ([`install-consult-playbook-gap.md` I4](../2026-05-18/install-consult-playbook-gap.md)). The substance is uncomfortable; the silence is worse.

Three honest options, in increasing customer-protectiveness:

1. **"You drill at your own risk."** The standard kitchen-appliance manufacturer stance. Legally clean, relationally cold. Survives Standard Edition but bruises Founder Edition.
2. **"We provide the procedure, you accept the risk, we'll help you find a stone fabricator if you'd rather not drill."** The middle path. The founder offers the **drill-it-for-you alternative**: a 30-minute appointment with a local stone fabricator (~$150–$300) to drill the hole, with the founder pre-vetting the fabricator and the customer paying directly. This is the most honest answer at $7,500 — the founder is selling an appliance, not stone fabrication.
3. **"If we tell you to drill and it cracks the slab, we cover up to $X."** A liability cap, typically $1,000–$2,500 per install. This is the white-glove answer and is the only one that actually backs the "plug and play" marketing claim. It is also the one that needs **product-liability insurance** (which currently is not in the repo — search for "insurance" returns no hits) and a clear definition of "if we tell you to drill" (the customer-call recording from [I5](../2026-05-18/install-consult-playbook-gap.md) becomes legally relevant).

The right answer is probably (2) with an option to upgrade to (3) for the customers whose slab material is genuinely high-risk (Dekton, large-format porcelain, irreplaceable natural stone). The founder should pick a stance and put it in writing before unit #1 ships.

**Estimated effort:** ~1 day of writing + ~half day of conversation with a small-business insurance broker to scope (3) if the founder wants it as an option. The conversation itself is a useful artifact and ties to the broader [`business/incorporation.md`](../../business/incorporation.md) timeline.

### P4 — Curate the install kit additions

Once P1 and P3 are written, the install kit gains real content. Proposed additions to [`hardware/bom.md` §14](../../hardware/bom.md):

| Part | Purpose | Per-build cost (est.) |
|---|---|---|
| Diamond core bit, 1-3/8" (35 mm), wet-rated | The drill bit itself — supply or don't, see below | ~$20–$40 (Amazon) |
| Paper hole template, 11"×11" cardstock | Drill location + alignment | ~$0.50 |
| Painter's tape, 2" × 60 ft (small roll) | Chip-out prevention, slurry containment | ~$2 |
| 1/4" plywood backer, ~6"×6" | Underside chip-out backer | ~$1 (offcut) |
| Modeling clay, 4 oz | Cooling-water dam ring | ~$1.50 |
| Sponge + microfiber cloth | Slurry cleanup | ~$2 |
| Optional: printed PETG drill-start jig | Prevents bit skating in first few seconds | ~$1.50 |
| **Kit subtotal** | | **~$28–$48 per build** |

The **single product decision** here is whether the diamond core bit ships in the kit (~$30) or the customer is asked to provide one ($30 line item on their Amazon order before the call). Arguments either way:

- **Bit-in-kit (recommended for Founder Edition):** Founder controls bit quality. Customer has zero ambiguity at install time. The kit feels substantial. Founder eats $30/unit out of margin. The bit is single-use per appliance lifetime, so "wasting" it on one hole is fine — it lives in the kit forever after, and if the customer ever moves the appliance they have it.
- **Customer-sourced (recommended for Standard):** $30/unit margin recovery. Customer's Amazon order is part of the install ramp anyway. Risk: customer buys the wrong bit (a dry-rated dirt-cheap one, a hole saw instead of a core bit), and the install goes badly.

Founder Edition pricing easily absorbs $30. Standard at $5,500 might or might not. Worth deciding once and writing it down.

The $28–$48 kit addition raises [`hardware/bom.md`](../../hardware/bom.md) total from $1,472.67 to roughly $1,500–$1,520 — a ~2% bump. Not material at $7,500/unit pricing.

**Estimated effort:** ~half day to source and price the parts + ~0.5 day to write the kit-contents section of the install guide.

### P5 — Document the no-drill alternatives (the highest-leverage win)

The single most important finding above: **1-3/8" is the standard kitchen-faucet hole size.** Many customers already have an unused 1-3/8" hole on their sink deck, currently occupied by:

- A side sprayer they never use (common — most modern faucets have a pull-down spray head, retiring the deck-mounted sprayer)
- A soap dispenser they never refill
- An air-gap fitting from a dishwasher that's plumbed differently
- A blank plug ("filler") installed when a previous fixture was removed

If the customer can identify any of these, the install becomes **literally drill-free**: pull the unused fixture, drop the faucet+umbilical through the existing hole, slide the keyhole plate, tighten the nut. The "plug and play, no plumber, no special tools" marketing claim becomes literally true for this customer.

This finding deserves its own document — `hardware/assembly/no-drill-install-paths.md` — describing each existing-hole path:

1. **Side sprayer retirement.** Most common case. Customer has a deck-mounted sprayer; founder confirms the existing hole is 1-3/8" (some are 1-1/4"; check before celebrating); customer disconnects the sprayer hose under the sink; the appliance's faucet drops into the now-empty hole. The sprayer's existing supply line from the main faucet body is capped under the sink with a $2 brass plug.
2. **Soap dispenser retirement.** Common, often unused. Pull the dispenser bottle, unscrew the deck collar, drop the appliance faucet into the hole.
3. **Air-gap repurposing.** Less common, but free real estate when present.
4. **Existing blank plug.** The kitchen previously had a fixture, the homeowner removed it, the hole is filled with a chrome cap. Pull the cap, drop the faucet.

This path is the **right default** for the install-consult Phase A pre-survey. The founder's first question on the call shouldn't be "what material is your countertop?" — it should be "do you have an existing 1-3/8" hole on your sink deck that's currently a sprayer, soap dispenser, or blank?" If yes, the entire drilling procedure is skipped. The slab-survey, the bit kit, the liability stance — all dormant.

The fraction of customers who can take this path is unknown but is meaningful. The founder's own kitchen would be the first data point (and is probably what motivates this finding — the founder picked the harvested Westbrass body because it's the standard kitchen-faucet shape, and that shape exists for a reason). A back-of-envelope: among kitchens with a 1-3/8" hole anywhere on the deck, perhaps 60–80% have at least one of those holes either currently unused or occupied by a fixture the homeowner would happily retire.

**Estimated effort:** ~1 day to write the document + photograph each of the four paths in the founder's own kitchen or a borrowed kitchen.

This single doc has the potential to **eliminate the drilling step for a meaningful fraction of Founder Edition installs**, which is the highest-leverage outcome anywhere in this todo.

### P6 — Build the slab-survey pre-call checklist

The install-consult Phase A ([`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) lines 60–67) names "thickness, material, proposed faucet penetration location" as things the founder confirms with the customer pointing the camera. It doesn't say *what the founder is looking for*.

The checklist:

- **Material.** Photo of the slab edge (visible at the sink rim — shows thickness + material profile). Visible thickness: 2 cm vs 3 cm changes drill time. Material profile (sponginess at the underside of laminate, sparkle of quartz, banding of natural stone) is the founder's identification cue.
- **Edge distance.** Photo of the planned drill location with a ruler held against the nearest slab edge. <4" → flag risk. <2" → refuse drill, redirect to a different location or to P3 option (2) stone-fabricator path.
- **Underside obstruction.** Customer's phone camera under the sink, pointing up at the proposed drill location. Founder looks for: cabinet web (a wood crossbar that the slab sits on), sink rim curl (the underside lip of the sink that wraps under the deck), brace bars (installed during the slab fabrication, especially around the sink cutout). Any of these means the drill exits into something — bad outcome.
- **Existing 1-3/8" holes.** Photo of the entire sink deck from above. Founder looks for any existing fixture (sprayer, soap, plug) that *might* be a 1-3/8" hole. This is the gate to P5.
- **Backsplash + faucet body interference.** Photo of the existing faucet from the side. Founder confirms the appliance's body OD (31.50 mm = ~1.24") + handle throw clears the existing faucet handle in normal use.

The checklist is **a Zoom artifact** — five photos the customer takes during the first 15 minutes of the call, the founder evaluates each in turn, decides on go/redirect/no-drill before the bit is unboxed.

**Estimated effort:** ~half day to write + integrate into [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) I2 (pre-call prep) and Phase A.

### P7 — Decide the "we won't sell to you" carve-out

A real product decision worth committing in writing: **are there countertop materials we refuse to install on?** Specifically Dekton, Neolith, and other large-format sintered porcelain — these are increasingly common in $300K+ kitchens and are genuinely high-risk to field-drill.

Three options:

1. **No carve-out — sell to everyone, drill everything.** Maximum addressable market, maximum tail risk. Bad fit for Founder Edition where the founder personally absorbs every failed install.
2. **Carve-out at sale.** A field on the order form: "what is your countertop material?" If the customer picks sintered porcelain or any material on the founder's no-drill list, the order is conditionally accepted with a forced no-drill path (P5 only). If P5 isn't viable for that customer, the order is refused.
3. **Carve-out at install-consult Phase A.** Sale is unconditional; if the slab survey reveals a material on the no-drill list and P5 isn't viable, the founder refuses the drill and offers a full refund (return shipping per [`appliance-freight-bench-gap.md`](../2026-05-18/appliance-freight-bench-gap.md)).

(3) is more honest at Founder Edition (you don't refuse the sale at order time when you haven't even seen the kitchen), and (2) is more honest at Standard (the customer is buying at a lower-touch tier and the up-front material filter is the right place to catch it). Worth picking one stance per tier.

**Estimated effort:** ~half day of writing once P1, P3, and P5 are in place. This is mostly committing in writing to what the founder would already do if asked.

---

## Migration plan / order of operations

1. **P5 first.** The no-drill alternatives. ~1 day of writing + photography. The highest-leverage single doc in this todo. Every other gap below shrinks in proportion to how many customers can take the no-drill path. Until P5 is written, the install-consult playbook treats every customer as a drilling customer, which is conservative-wrong.
2. **P6 next.** The slab-survey checklist. ~half day. Direct dependency for `install-consult-playbook-gap.md` Phase A. Until this exists, "the founder visually confirms thickness, material, penetration location" is unactionable.
3. **P1 third.** The canonical drilling procedure. ~2.5 days. The slow, careful one. The content that `install-above-counter.md` cites.
4. **P3 alongside P1.** The liability stance. ~1 day. This is a writing exercise more than an engineering exercise; the founder picks a stance and the lawyer-ready language follows. Should be in place before unit #1 ships.
5. **P4 once P1 is written.** Install-kit additions. ~1 day. Cheap and concrete; can be sourced from Amazon at the same time as the rest of the install kit.
6. **P2 in parallel with P1–P4.** Hole template. ~1 day for the printed-PETG jig version. The paper version is a 30-minute task.
7. **P7 last.** Won't-sell carve-out. ~half day. Depends on P1, P3, P5 being in place to define the carve-out boundary.

Total: ~7 calendar-days of writing, ~$30–$50/unit in install-kit BOM additions, zero new factory tools, zero new firmware. None of this blocks the factory build chain. All of it is doc-and-kit work that the founder can drive in parallel with the integrated-build work.

---

## What this changes in the broader docs

Once P1–P7 are written:

- [`hardware/assembly/faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) open item #5 (`install-above-counter.md` placeholder) becomes resolvable. It cites this analysis + `countertop-drilling.md` + `no-drill-install-paths.md` instead of duplicating.
- [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) Phase A pre-survey gets the P6 checklist; Phase B step 1 gets a one-paragraph summary citing P1; I3 (`install-above-counter.md`) becomes a thin "see also" doc instead of a full procedure.
- [`hardware/bom.md` §14](../../hardware/bom.md) gains the P4 kit additions.
- [`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) gets a line item for the install kit's expanded contents.
- [`business/`](../../business/) gains a new `terms-and-conditions.md` (currently missing) with the P3 liability stance and the P7 carve-out.
- [`marketing/target-market.md:15`](../../marketing/target-market.md) — the "plug and play, no plumber, no special tools" claim — gets a careful revision. **Either** the marketing copy backs off ("under an hour for most kitchens; some installs require a one-time countertop hole, which we walk you through"), **or** the install kit + P5 path is robust enough that the claim is still defensible. The honest version of the second answer is "we don't drill in the customer's house — if their kitchen needs drilling, our install consult lines up a local stone fabricator before the appliance ships." Worth being deliberate about which version of the claim the marketing site makes.

---

## Out of scope for this todo

- **The under-counter water-line tap.** Different penetration, different risk profile, covered (lightly) in [`install-consult-playbook-gap.md`](../2026-05-18/install-consult-playbook-gap.md) Phase B step 4. Belongs in its own todo.
- **The under-counter power outlet.** Customer-electrical question, sometimes a separate trade. Out of scope.
- **The under-cabinet rear-panel push-to-connect work.** Owned by [`hardware/assembly/faucet-and-umbilical.md`](../../hardware/assembly/faucet-and-umbilical.md) step 7 / the install guide.
- **The CO2-cylinder physical placement under the cabinet.** Owned by [`co2-supply-ownership-gap.md`](../2026-05-18/co2-supply-ownership-gap.md) and [`co2-asphyxiation-and-prv-vent-path-gap.md`](co2-asphyxiation-and-prv-vent-path-gap.md).
- **The Westbrass body's shape itself.** Harvested chrome, mechanical, no design freedom at this stage of the build.

---

## Suggested next concrete step

Write **P5** as the canonical doc at `hardware/assembly/no-drill-install-paths.md`. One day of writing + one founder-kitchen photography pass.

The leveraged finding is single-sentence: **1-3/8" is the standard kitchen-faucet hole size, which means a meaningful fraction of customers already have a 1-3/8" hole on their sink deck currently occupied by a fixture they would happily retire.** Until that sentence is in the playbook, the install consult treats every kitchen as a drilling kitchen. That is conservative-wrong, and it carries an unnecessary liability tax on every Founder Edition install.

The second-most-leveraged finding is P3 (liability stance) — not because the drilling fails often, but because the *silence* on the question is itself a Founder Edition trust failure. A customer about to spend $7,500 and drill their own granite is going to ask "what happens if this cracks?" exactly once, on the call, and the founder's answer needs to be in writing somewhere the customer can re-read after the call.

The drilling-procedure doc (P1) is the longest single deliverable in this todo but is the **third** most leveraged. Get P5 and P3 done first; P1 becomes meaningfully shorter once the no-drill path is documented (fewer customers ever read it) and the liability stance is settled (the procedure can be written from the founder's stance rather than from a defensive crouch).
