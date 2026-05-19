# The hourly routine is optimizing the org chart of a company that doesn't have a product yet

**Author:** Derek + reviewing agent, 2026-05-19 (third of the day)
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek, and specifically the hourly routine's own prompt
**Distinct from siblings:**
- Morning sibling [`trademark-and-brand-name-usage-gap.md`](trademark-and-brand-name-usage-gap.md) — Lanham Act / FTC exposure around brand-name use.
- Midday sibling [`concentrate-supply-resilience-gap.md`](concentrate-supply-resilience-gap.md) — per-SKU concentrate stockout response.
- 2026-05-18 siblings — six post-sale operational gap docs (freight, CO2 supply, install consult, order+payment, per-unit portal, warranty/RMA).

**This doc is meta.** It is not a new gap in the appliance or the business. It is a gap in the *routine that is generating these todos*. None of the siblings, and none of yesterday's six, will land their recommendation before the appliance pours soda in Derek's kitchen. The single 2026-05-18 finding that actually changed the appliance — front-panel CO2 inlet with the cylinder beside the unit on a short tether, now committed as `7174621` and `5dd6b2c` — came out of the *one* todo whose subject was a customer-visible part of the machine. The other seven are well-researched and currently unactionable.

---

## TL;DR

The single thing worth caring about right now is **the appliance**. Specifically the integrated build in [`hardware/future.md`](../../hardware/future.md) — pressure vessel, refrigeration loop, cold core, faucet — the things that make "turn the handle, soda comes out" real in Derek's kitchen first.

Everything in [`todo/`](..) is downstream of that working. None of it is upstream of it working.

FTC §435 matters when a customer has paid. Carrier liability caps matter when a unit ships. Trademark exposure matters when there is marketing reach. Stripe reserves matter when there is a Stripe account with volume. Concentrate-supply resilience matters when there is a customer whose faucet just went dry. Today there is one founder, a prototype on the counter, and zero customers. Every one of these docs is solvable in an afternoon the week before unit 001 ships, and most are solvable *better* then because the actual answer (which carrier, which payment flow, which kitchen, which SKU) will be known instead of imagined.

The hourly routine is optimizing the org chart of a company that doesn't have a product yet. Derek is building the product. **Keep building.**

---

## What the data says

Eight hourly-routine outputs to date (six on 2026-05-18, two earlier on 2026-05-19). Classify by what the recommendation, if fully executed, would change:

| File | Changes the machine? | Changes a customer-facing surface that exists today? | Result in repo |
| --- | --- | --- | --- |
| `co2-supply-ownership-gap.md` (2026-05-18) | **yes** (front-panel inlet / cylinder placement) | yes | committed in `7174621`, `5dd6b2c` |
| `appliance-freight-bench-gap.md` | no | no (no unit has shipped) | none |
| `install-consult-playbook-gap.md` | no | no (no customer to consult) | none |
| `order-and-payment-flow-gap.md` | no | no (no order intake exists) | none |
| `per-unit-portal-gap.md` | no | no (no plaque has shipped) | none |
| `warranty-and-rma-gap.md` | no | no (no warranty to honor) | none |
| `trademark-and-brand-name-usage-gap.md` (2026-05-19) | partial (firmware bitmap swap) | no (no marketing live at scale) | none |
| `concentrate-supply-resilience-gap.md` (2026-05-19) | no | no (no customer's faucet exists) | none |

One in eight changed the appliance. That one was the only one whose subject was the appliance.

This is not the agents being bad — each doc is researched well and would be useful at its right moment. It is the **routine's framing** producing work whose right moment is months or years out. The selection function ("find something to focus on … there are dozens of areas") is biased toward *naming undone things*, and a pre-revenue project has a near-infinite supply of undone post-revenue things. Naming them generates the appearance of progress without the substance of it.

---

## Why this matters

The cost of the misalignment is not zero. Each hourly run consumes tokens, generates a doc Derek has to skim, and adds repo surface area (eight files, all with cross-links, all referenced from each other's "siblings" section). The *content* compounds — sibling lists grow, future agents read prior gap docs as part of context-building, and the routine drifts further into "post-sale operations consultancy" with every iteration. The natural endpoint is a `todo/` directory that reads like a Fortune-500 risk register attached to a kitchen appliance that does not yet exist.

Meanwhile the actual gaps in `hardware/future.md` — the things that block the next pour from the next prototype — are not getting the hourly agent's attention, because the routine's prompt biases away from "what is the founder building this week" and toward "what important undone area can I name."

---

## What's actually unaddressed today (in the routine, not the appliance)

The routine script at [the project root agent harness] reads, in its current form, approximately as:

> Please find something to focus on. … There are dozens of areas in this repo that are important, and that have not had the appropriate attention to detail that you now have the time to spend.

Three things this framing does not say, that it should:

1. **Bias toward the appliance.** The routine already mandates reading `future.md` and `target-market.md` first. It does not say "your recommendation should change one of those documents, or change a file they reference in `hardware/`, unless you have a strong reason otherwise." Without that bias, the agent's least-resistance path is to find a *named but unwritten* artifact (warranty doc, install script, portal page) and write a gap doc about it. The appliance — which has tons of named open items inside `hardware/assembly/*.md` and `hardware/printed-parts/**/README.md` — is *harder* to make recommendations about because doing it well requires understanding the physical build, not just the org-chart shape.

2. **A pre-revenue stance, explicitly named.** `business/regulatory.md` already establishes that compliance work is voluntary and safety-driven, not regulatory-driven, because the project is pre-revenue. The routine should inherit that stance: a recommendation whose value only materializes after first revenue should be flagged as such by the agent itself, with an explicit "this is future-state reference material" tag, and should be rare relative to recommendations that change the next prototype build.

3. **A cap on the post-sale operations bucket.** Of the eight existing todos, seven are post-sale operations. The marginal eighth, ninth, tenth doc in that bucket adds almost nothing — the surface is already mapped. The routine should be told: *if your topic is post-sale operations and there are already N docs on it, pick something else.* The agent already does sibling-avoidance ("must be distinct from any other files you find in the todo folder for today"); the same logic should extend across days and across buckets, not just across same-day filenames.

---

## Recommendation

Three concrete changes — one to the routine prompt, one to the todo-folder convention, one to the agent's selection heuristic. All cheap, all reversible.

### R1 — Add an appliance-bias clause to the routine prompt

After the line *"You must always start by reading future.md and target-market.md. That is your context. Those are our goals,"* add:

> Your recommendation should, by default, change one of those two documents or change a file they reference in `hardware/` or `firmware/`. The product is pre-revenue and the bottleneck is the appliance itself working in Derek's kitchen, not the operational machinery around selling it. Post-sale operations recommendations (freight, payment, warranty, portal, marketing legal, brand strategy) are allowed but should be rare and should be flagged as `Status: future-state reference material` in the doc itself. If you are about to write your third post-sale operations doc in a row, pick something else.

This is a soft bias, not a hard rule. The CO2 ownership doc was post-sale-coded but produced a real appliance change because the author followed the trail back to the inlet. That should keep being possible. The bias is against *defaulting* to the operational bucket because it's the easier target.

### R2 — Add a `Status:` taxonomy to the todo doc template

Three values, mutually exclusive, named at the top of each todo:

- `Status: prototype-blocker` — if executed, this changes a file in `hardware/` or `firmware/` and unblocks the next physical build.
- `Status: pre-first-sale` — if executed, this changes a customer-facing artifact that must exist before unit 001 ships (e.g. the install consult script, the order intake page, the warranty terms).
- `Status: future-state reference` — research captured for a moment that hasn't arrived. Safe to leave unactioned indefinitely.

The current eight todos sort cleanly: one prototype-blocker (CO2 ownership, already harvested), zero pre-first-sale that are *time-critical*, seven future-state reference. Naming that explicitly lets future agents see the distribution at a glance and weight their own choice accordingly.

### R3 — Teach the agent to ask "what would this change?" before writing

Inside the routine prompt, before the "create one file" instruction:

> Before you commit to a focus area, write one sentence answering: "If a future agent or Derek executes this recommendation in full, what file in the repo changes, and does that change move the next prototype build forward?" If the honest answer is "no file in `hardware/` or `firmware/` changes, and the next prototype build is unaffected," reconsider. You are allowed to pick that topic anyway, but mark the resulting doc `Status: future-state reference`.

This forces the agent to confront, on every run, the same question Derek confronted when reading eight gap docs: *what does this actually do for me right now?*

---

## What this doc is not asking for

- Not asking to delete the existing eight todos. They are good research and will be useful at their moment. The CO2 one already paid for the whole batch.
- Not asking to stop the hourly routine. The routine is cheap, the surface area is real, and one prototype-blocker per eight runs is a fine hit rate if the cost is "Derek skims eight markdown files."
- Not asking the agent to start editing `hardware/future.md` directly. The routine's "I do not trust you to make changes to the repo on your own" clause is correct; the appliance bias is about *what the recommendation targets*, not about who executes it.
- Not asking for a new dashboard, tracker, or meta-document beyond this one. The `Status:` field and the one-sentence "what changes" answer are the whole intervention.

---

## The single thing

If the routine internalized one sentence from this doc, this is the one:

> The worry-wart agent is optimizing the org chart of a company that doesn't have a product yet. Derek is building the product. Keep building.

Everything else is implementation detail.
