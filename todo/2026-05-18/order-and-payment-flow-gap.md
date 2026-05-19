# The $7,500 sale itself: order intake, deposit architecture, FTC Mail Order Rule, and the plaque-number commitment

**Author:** hourly agent, 2026-05-18
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Distinct from siblings 2026-05-18:**
- [appliance-freight-bench-gap.md](appliance-freight-bench-gap.md) — the carrier handoff *after* the unit is built and paid.
- [co2-supply-ownership-gap.md](co2-supply-ownership-gap.md) — ongoing CO2 consumable supply after delivery.
- [install-consult-playbook-gap.md](install-consult-playbook-gap.md) — the Zoom call between delivery and first pour.
- [per-unit-portal-gap.md](per-unit-portal-gap.md) — `/u/NNN` software portal that activates at install time.
- [warranty-and-rma-gap.md](warranty-and-rma-gap.md) — post-delivery failure response.

**This doc is upstream of all five.** Every sibling assumes the customer has already paid and an order exists. There is no document in the repo that describes how that happens.

---

## TL;DR

[`marketing/target-market.md`](../../marketing/target-market.md) commits to selling Founder Edition units 001–050 at **$7,500 each** with a personal install consult, signed numbered plaque, and a roughly four-year solo build queue (~12 units/year). [`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) step 3 commits to applying a plaque whose serial **must match the serial assigned to the order**. [`business/incorporation.md`](../../business/incorporation.md) commits to forming the NE SMLLC *before the first paid unit ships*.

But there is no document anywhere in the repo describing:

1. **How a customer pays** (Stripe Checkout? Stripe Invoice? wire? check? all three?).
2. **When they pay** (deposit at order, balance at ship; or full at order; or full at ship).
3. **What they agree to** in writing (terms of sale, refund policy, lead-time disclosure).
4. **How a plaque number gets reserved** (claimed at deposit? at full payment? at ship?).
5. **What the law says** about taking $7,500 today for a thing that ships in 4–48 weeks (FTC Mail Order Merchandise Rule, 16 CFR §435).
6. **How Stripe treats** a brand-new merchant account with $7,500 AOV, manufacturer-shipped-by-self risk, and a delivery window measured in months (the reserve/rolling-hold problem).
7. **How sales tax** behaves on a Nebraska-origin hand-built appliance shipping to a customer in any of 49 other states.

This whole layer is missing. The downstream documents — every today-sibling listed above — silently assume a customer has paid, a serial is committed, and the build can start. None of those preconditions has an upstream owner today.

The recommended architecture, defended below: **small refundable deposit at order, plaque number reserved at deposit, full balance charged 5–10 business days before ship, FTC delay-notice flow built in from unit 001, Stripe Invoicing (not Checkout) as the payment surface, Nebraska-only sales tax until a real economic-nexus event happens.**

---

## Reading order if you only have 10 minutes

1. This TL;DR.
2. **Section 4 — FTC Mail Order Rule.** This is the unappealable part. The architecture has to bend around it.
3. **Section 6 — Recommended order flow.** The deposit-and-balance shape.
4. **Section 9 — Open items.** What still needs a human decision.

Everything else is the defense.

---

## 1. What the repo already commits to (and therefore constrains)

A short inventory of decisions that are already locked in and that the order-and-payment flow must honor:

- **Two-tier public pricing.** Founder Edition $7,500 (001–050), Standard $5,500 (051+). [`marketing/target-market.md`](../../marketing/target-market.md) §"What we are selling".
- **Internal rings-of-trust pricing.** Ring 1 (first 10) likely $2,000–3,000 or near cost; Ring 2 holds or drops slightly; Ring 3+ approaches the public anchor. [`marketing/target-market.md`](../../marketing/target-market.md) §"The internal plan: rings of trust".
- **Solo build capacity ~12 units/year.** A serial commitment made today is a delivery promise sometime in the next 4 weeks to 48 weeks depending on queue position.
- **The plaque is signed at finish-pack-ship.** [`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) step 3 explicitly states the builder is signing *this specific machine for this specific customer* — no batch pre-signing. So the customer↔serial binding has to be firm before the plaque is applied, but it doesn't have to be firm at the start of the four-week build window.
- **QR code on the plaque points to `homesodamachine.com/u/NNN`.** The order system must hand the build system a serial early enough that the plaque can be pre-printed during finish-pack-ship, but late enough that a cancelled order doesn't burn an unrecoverable number. (See [per-unit-portal-gap.md](per-unit-portal-gap.md) for the consumer-facing side of `/u/NNN`.)
- **The founder is the brand.** [`marketing/target-market.md`](../../marketing/target-market.md) "At Founder Edition, the brand is a person." Payment friction that erodes that ("please email me your credit card") works against the premium-handmade story; payment friction that reinforces it ("here is the invoice you'll receive from Derek") works for it.
- **Nebraska origin.** [`business/incorporation.md`](../../business/incorporation.md) calls for NE SMLLC and Nebraska sales-tax registration before first paid sale. The order flow needs to know which state is destination at intake time.

These constraints are not negotiable. The architecture below works inside them.

---

## 2. What's currently absent — the exact gap

Searching the repo (`grep -ri 'stripe\|deposit\|FTC\|chargeback\|Mail Order'` across `business/`, `marketing/`, `pie-in-the-sky/`) returns exactly one substantive hit:

> [`pie-in-the-sky/timeline.md`](../../pie-in-the-sky/timeline.md) line 57: "...a Stripe-and-fulfillment habit, a 'how do I respond to a confused customer' voice — all in place months before HSM 1 is ready to take a deposit."

That's it. The repo names Stripe once, as something that *should be in place* by the time the first HSM unit is ready, but never describes:

- Account type (standard vs. embedded, capital structure of merchant of record).
- Product/SKU model (one $7,500 product? a $X deposit + $7,500−$X balance? a "reservation" SKU + a separate "balance" SKU?).
- Payment surface (Stripe Checkout, Payment Links, Invoicing, custom API).
- The contract the customer signs.
- The refund mechanics if the customer cancels mid-queue.
- Anything about FTC §435.
- Anything about chargebacks at $7,500 (the dispute fee alone is $15, the merchant's loss on a successful chargeback is the full $7,500 plus shipping plus the unit, and the dispute window is 120 days from the *charge date* under most card networks — which interacts badly with the long build queue).

`business/incorporation.md` correctly flags "Nebraska sales-tax registration" and "first paid sale" as the trigger event, but does not describe what the paid sale looks like operationally.

The today-siblings (warranty, freight, install-consult, portal) all begin their procedures at a point where an order already exists. **The order is the missing input to all of them.**

---

## 3. The actual decision space

The architecture splits along four mostly-independent axes. Each axis has a small number of viable positions.

### Axis A — Payment timing

- **A1. Full payment at order.** Customer pays $7,500 the moment they commit. Money sits with Stripe (and with Derek) for the entire 4–48 week build window. Simplest accounting. Maximum FTC exposure (see §4). Maximum chargeback exposure (the 120-day window restarts every day until the charge ages out, but only after delivery is on the clock — see §5).
- **A2. Deposit at order, balance at ship.** Customer pays a small refundable deposit (e.g. $500) when they claim a slot; balance is charged when the unit is in finish-pack-ship and shipping is imminent. Lowers FTC exposure dramatically — the §435 30-day clock only applies to *received* payment, and a $500 deposit with explicit terms is much smaller stakes if the lead time gets renegotiated. Two charge events to manage. **Recommended.**
- **A3. Balance at ship only, no deposit.** No money changes hands until shipping. Soft commitment from customer. Better-feeling for an inside-the-network ring-1 sale. Worse for an arms-length ring-3 buyer who needs the act of paying to feel real. Plaque number could get reserved and then walked away from with no penalty.
- **A4. Mixed.** Ring 1 / Ring 2: A3 or low-deposit A2. Ring 3 / public Founder Edition: A2 with a meaningful deposit. **This is the right combined position.** The public anchor commitment in `target-market.md` is to a single number ($7,500) but the *payment shape* underneath can legitimately differ between a friend and a stranger.

### Axis B — Payment surface (Stripe product choice)

- **B1. Stripe Checkout.** Hosted checkout page. Best for self-serve "buy now" flow. Works for high AOV but is friction-light in a way that doesn't match the "I built this for you" story.
- **B2. Stripe Payment Links.** A URL Derek sends after a phone or email conversation. Works for both deposit and balance. Lower friction than a custom checkout; preserves the human-touch story.
- **B3. Stripe Invoicing.** Generates a PDF-quality invoice that lands in the customer's inbox with a "Pay Now" button. Most appropriate for a $7,500 hand-built appliance sale — the artifact *looks* like a $7,500 transaction, not like a $150 Amazon purchase. Supports partial payments natively (deposit + balance on the same invoice ID). **Recommended for both deposit and balance.**
- **B4. Wire / ACH / check.** Always offer as a fallback for high-net-worth buyers who'd rather not put $7,500 on a card. Wire/ACH is also chargeback-free, which materially de-risks the ship-and-then-get-disputed scenario in §5.
- **B5. Stripe Capital, Klarna, Affirm financing.** Out of scope at unit volumes <50. Revisit at Standard tier.

### Axis C — Plaque-number reservation timing

- **C1. Reserved at first contact.** Anyone who emails Derek gets a "you're #007, hold for 7 days while we talk." Burns numbers fast; nice gesture; bad on supply of low numbers.
- **C2. Reserved at deposit.** Customer pays $500, gets a slot. Number is firm pending build-start. Refundable up to N days before build starts; non-refundable after that.
- **C3. Reserved at balance charge.** Number is loosely held during the wait, only firms when the balance is paid 5–10 days pre-ship. Risk: two customers can think they have the same number for months. Bad.
- **C4. Reserved at build start.** Number assigned when Derek pulls the parts kit for that build, not before. Customer doesn't know their number until ~4 weeks before ship. Loses the "you are #003" emotional anchor that the whole Founder Edition story leans on.

**C2 is the right answer.** The deposit *buys* the number. The number's social meaning is what the Founder Edition tier sells; reserving it at the moment money changes hands ties the commitment to the artifact correctly.

### Axis D — Terms-of-sale artifact

- **D1. None.** Stripe receipt is the only document. Adequate for $50 e-commerce; inadequate at $7,500 with 4–48 week lead.
- **D2. Single-page terms attached to the order email.** Plain English: what's being sold, lead-time window, refund policy, warranty length pointer (cross-ref [warranty-and-rma-gap.md](warranty-and-rma-gap.md)), CO2-supply expectation pointer (cross-ref [co2-supply-ownership-gap.md](co2-supply-ownership-gap.md)), shipping expectation pointer (cross-ref [appliance-freight-bench-gap.md](appliance-freight-bench-gap.md)), install-consult promise pointer (cross-ref [install-consult-playbook-gap.md](install-consult-playbook-gap.md)), governing law (Nebraska). E-signed via DocuSign / HelloSign / Dropbox Sign. **Recommended.**
- **D3. Full lawyered contract.** Premature; cost-prohibitive; signals corporate, not founder-handmade.

D2 with founder voice — not legalese — is the right shape. It exists to (a) make the FTC §435 compliance explicit, (b) make the long lead time visible to the customer in writing, and (c) give Derek a single document to point to if any of the today-siblings (warranty, freight, install) end up in dispute later.

---

## 4. The non-negotiable: FTC Mail Order Merchandise Rule (16 CFR §435)

Anyone selling consumer goods by mail / internet / phone is bound by the FTC Mail Order Merchandise Rule. The repo never mentions it. It is the most important external constraint on this entire architecture.

The rule, as it applies here:

1. **Stated time, or 30 days.** If you advertise a shipment time ("ships in 4 weeks"), you're bound to that. If you don't, you're bound to 30 days from the order date. The clock starts when you have *received* payment (any payment, including a deposit).
2. **Delay notice.** If you can't meet the stated/30-day window, you must send a delay notice **before** the deadline, offering the customer either (a) accept a specific new ship-by date, or (b) cancel and receive a full refund.
3. **Customer silence = consent to a 30-day extension, but only once.** If the customer doesn't respond to a delay notice that asks for consent to a delay of 30 days or less, that silence counts as consent. Any *further* delay requires explicit written consent from the customer; silence is no longer enough.
4. **Refunds must be prompt.** Card refunds within one billing cycle; check/cash refunds within 7 business days. No "store credit only" workarounds for cancellations under this rule.

This rule was written for the catalog era and bites hard on long-lead-time hand-built goods. Concretely:

- **Charging $7,500 at order with a 48-week ship window** (Axis A1) is a §435 minefield. You will trigger a delay notice exchange every 30 days for the entire wait. Each one is an explicit opportunity for the customer to cancel and recover the $7,500. The first one (at day 30) is mandatory and unavoidable.
- **Charging $500 at order with explicit advertised lead time of "4–48 weeks depending on queue position"** (Axis A2 + clear pre-sale disclosure) is much better. The $500 is the only triggering payment; the lead-time disclosure substitutes for the §435 default 30-day clock; the customer agreed in writing to the window.
- **Quoting a *firm* ship-by date at order is the cleanest path.** "Your unit will ship by 2027-02-15, ±2 weeks" is enforceable and transparent. Derek does have the data to do this — at solo capacity, queue position N maps to roughly week (N×30 days) from order, plus a buffer.

**The right architecture is: deposit at order, balance at ship, *and* a firm written ship-by-date quoted at deposit time.** The quoted date is the §435 stated time. The deposit triggers the §435 clock. The balance charge happens inside the stated window. If Derek slips, he sends the delay notice promptly, and the customer's worst-case cancellation cost is the deposit (refundable per Stripe T+5–10 business days).

There is no version of this where you can take $7,500 up front for a thing that ships months later without active §435 management. The deposit architecture makes that management proportional — you're managing a $500 commitment, not a $7,500 commitment, for the first three months of the build queue.

---

## 5. Stripe-specific risk: reserves, chargebacks, and the 120-day window

Stripe's risk model treats a new merchant account selling a $7,500 physical product with a 4-month delivery window as a near-worst-case profile. The cluster of behaviors Stripe flags:

- New account, no merchant history.
- High AOV.
- Physical goods that ship slowly (delivery delay is the #1 chargeback reason for physical goods).
- "Hand-built" / "custom" descriptions in marketing — Stripe treats made-to-order as a higher risk class than off-the-shelf.

What typically happens when this account starts processing real volume:

- **Rolling reserve.** Stripe holds X% of every transaction for Y days. Common new-account terms are 20–25% for 90 days. At $7,500 × 12 units/year × 25% × 90 days, that's somewhere around $1,800–$5,500 in reserve at steady state, scaling with the queue.
- **Delivery-verification holds.** Stripe may hold funds until they see a shipping label in the account (Stripe Shipping integration helps here). For the 4-month build window, this means Derek's cash is on Stripe's balance sheet for the entire build, not his.
- **Chargeback window.** Card-network rules give the cardholder 120 days from the **transaction date** (not the delivery date) to file a "merchandise not received" dispute under reason code 4855 / 13.1. A balance charge at ship has its 120-day window run almost entirely *after* delivery — that's the right shape. A full-payment-at-order charge against a 4-month build has its 120-day window expire *one month after the unit arrives*, which is almost no post-delivery dispute protection at all.

Practical mitigations that drop out of this:

1. **Charge the balance at ship, not before.** Most of the dollar volume should be inside its own 120-day post-delivery dispute window. Done correctly, the deposit is the only money exposed to a "never delivered" dispute, and the deposit is small.
2. **Use Stripe Shipping or feed tracking numbers into the charge metadata.** Reduces the rolling reserve faster (Stripe's risk team rewards verified delivery).
3. **Offer wire/ACH for buyers willing to use it.** ACH chargebacks are limited to 60 days and only for unauthorized transactions, not buyer's-remorse. Wire is final. The customer-saving "you paid an honest person who built you a thing" story is reinforced, not damaged, by Derek emailing back "great — I'll send a wire invoice or a Stripe invoice, your call."
4. **Build chargeback evidence from day 1 of the order.** Save the signed terms doc, the deposit confirmation, the email trail, the shipping confirmation, the install-consult confirmation, the customer's first-pour video reply (if offered) — all of these go straight into a Stripe dispute evidence bundle if a 4855 ever fires. The whole "founder is the brand" story is, helpfully, also the world's best chargeback-evidence story: Derek personally talked to this person on Zoom, here's the recording. Cards will not side with the buyer.
5. **Cap the deposit below Stripe's "small purchase" comfort zone.** $500 sits in normal-merchant range; $2,500 starts pinging risk models on a brand-new account.

This whole risk surface is small, but it is not zero, and it directly affects when Derek sees the money. Worth getting right.

---

## 6. Recommended order flow

Putting Axes A–D together:

### 6.1 Public pre-sale page (`homesodamachine.com/order` or similar)

Plain-English copy. Names the lead time explicitly. Names that this is unit X of 50, signed and numbered. Names that there's a deposit-and-balance structure. Names the refund policy in two sentences.

Below the fold, three calls-to-action of increasing commitment:
1. "Talk to Derek first" — Calendly link to a 20-minute intro call. Used heavily during Ring 1 and Ring 2 (per `target-market.md` "rings of trust"). Most ring-1 sales close here, not on the deposit page.
2. "Reserve a number" — leads to Stripe Invoice for $500 deposit + DocuSign of terms. Used for ring-3+ buyers who have read enough and want to commit.
3. "Already talked to Derek? Pay your invoice" — a placeholder for buyers who got a custom invoice and want to find it again.

### 6.2 The deposit moment

When a customer commits:

1. Derek creates a Stripe Customer + Stripe Invoice for the $500 deposit. Invoice line items: "Founder Edition Unit #NNN reservation deposit — applied to final balance at ship". Invoice memo: ship-by date, terms summary.
2. The customer pays the invoice. Stripe webhook fires.
3. The webhook (or, more honestly, Derek manually for the first ~5 units) reserves plaque number NNN in a build queue document (could be as simple as a row in `business/orders.md`, or a tiny SQLite file under `web/`).
4. Derek sends a confirmation email with: deposit receipt, terms PDF for e-signature, the ship-by date, a queue-position one-liner ("you're #N in the queue; I'm building #M now"), what to expect at each step (pointer to install-consult, freight, warranty, portal docs from the today-siblings).

### 6.3 The build window

No payment events. Derek builds the unit. The customer gets a build-progress email at one or two natural milestones (e.g. "your vessel was welded today", "your unit passed pressure test") — this is a `pie-in-the-sky/curator-brand.md`-adjacent move that costs almost nothing per unit and dramatically reduces the chance of a "where's my unit" dispute.

### 6.4 The balance moment (5–10 business days pre-ship)

1. Derek creates a Stripe Invoice for $7,000 ($7,500 - $500 deposit). Invoice memo: "Balance for Founder Edition Unit #NNN, ships [date]". Includes shipping fee or marks it free if absorbed.
2. Customer pays. Webhook fires. Plaque number is now permanent.
3. Plaque is printed and signed per [`hardware/assembly/finish-pack-ship.md`](../../hardware/assembly/finish-pack-ship.md) step 3 — this is where the order flow hands off to the build/ship pipeline.
4. Unit ships per [appliance-freight-bench-gap.md](appliance-freight-bench-gap.md) recommendations.
5. Install consult is scheduled per [install-consult-playbook-gap.md](install-consult-playbook-gap.md).

### 6.5 If something goes wrong

- **Customer cancels pre-build-start:** full deposit refund within 5 business days (Stripe refund). Plaque number returns to the queue.
- **Customer cancels post-build-start, pre-ship:** deposit forfeited (covers committed parts). Plaque number stays committed to the abandoned build, sold at the end of the Founder Edition run as "originally allocated to N, available" — or simply burned. The terms doc must name this clearly.
- **Derek slips on the ship-by date:** §435 delay notice goes out before the original date. Customer chooses extension or full refund (including deposit). Plaque returns to queue if refunded.
- **Customer disputes a charge:** evidence bundle assembled from the order record. The deposit is the only money at risk during build; the balance is at risk only for 120 days post-ship and is defended with the install-consult records and the `/u/NNN` portal usage logs from [per-unit-portal-gap.md](per-unit-portal-gap.md).

---

## 7. Sales tax — Nebraska only, until something changes

[`business/incorporation.md`](../../business/incorporation.md) calls for Nebraska sales-tax registration before first paid sale; the order flow needs to act on this.

State-by-state economic-nexus thresholds (Wayfair-era, as of last general knowledge — verify with current state guidance):

- Most states: $100,000 in sales **or** 200 transactions into that state.
- Some larger states: $500,000 (CA, NY, TX).
- Some smaller states: $100,000 only.

At 12 units/year × $7,500 = $90,000 total annual revenue, Derek does not approach the $100K-into-a-single-state threshold from any direction. He could ship every single Founder Edition unit to California and still not trip CA's $500K nexus. The transaction-count thresholds are also far away — 12 units/year is nowhere near 200 transactions in any state.

So:

- **Year 1–4 (Founder Edition era):** Register only in Nebraska. Charge Nebraska state + local sales tax on Nebraska deliveries. Do not collect on out-of-state deliveries. Mention in terms of sale: "Sales tax not collected on out-of-state orders; the customer is responsible for any use tax owed in their state."
- **Standard Edition era (~year 5+):** Revisit when annual volume into any single state approaches that state's threshold. At 100 units/year × $5,500, total revenue is $550K; if 20+ units a year go to a single state, you're approaching $110K and need to register there.

The order intake form needs the destination state captured at the deposit moment so this can be applied correctly even at year-1 volume.

---

## 8. What this would look like in the repo

Concretely, the artifacts that should land before unit 001 takes a deposit:

| Artifact | Where it lives | What it contains |
|---|---|---|
| `business/order-flow.md` | new file | The architecture in this document, but written as the live operational doc, not a recommendation. |
| `business/terms-of-sale.md` | new file | Plain-English customer-facing terms, ready to PDF and e-sign. Pointers to warranty / freight / install / CO2 / portal sibling docs. |
| `business/orders/` directory | new | Per-order working file: customer name, contact, shipping address, plaque #, deposit date/amount, balance date/amount, ship-by date, status, link to Stripe Customer ID. (Could just be a CSV; doesn't need to be a database yet.) |
| `web/order/` or similar | new | The pre-sale page itself. Three CTAs from §6.1. Static is fine. |
| `hardware/assembly/finish-pack-ship.md` | edit | Step 3 currently says "match the serial assigned to the order" — add a one-line pointer to `business/order-flow.md` for *how* that assignment happens upstream. |
| `business/incorporation.md` | edit | One paragraph cross-referencing `order-flow.md` for the "before first paid unit ships" trigger. |

None of these need to be heavy. They mostly need to *exist* before the first deposit invoice goes out.

---

## 9. Open items — what needs Derek's decision

Items where the recommendation above is genuinely my best read but a human needs to decide:

1. **Deposit amount.** $500 is the recommendation. Defensible range: $250 (lowest-friction commit, sometimes paid by ring-1 buyers as a token) to $1,500 (covers actual specific-customer parts commits like the printed nameplate consumables and any per-unit custom selections). $500 is round, meaningful, and far enough below the "I need to think about it" threshold for the target buyer.
2. **Ring 1 / Ring 2 payment terms.** The `target-market.md` rings plan is explicit that ring-1 buyers may pay $2,000–3,000 (or even at-cost) and may include family on beta terms. Does the deposit architecture even apply to ring 1? Recommendation: **no formal Stripe deposit for ring 1**. Ring 1 is a handshake with someone the founder knows. Use Stripe Invoicing for the final amount at ship for tracking and tax purposes, but don't impose a deposit-and-balance dance on a friend. The public terms doc and FTC compliance only apply to arms-length sales.
3. **Refund window for the deposit.** The §435 baseline gives the customer a full refund if Derek can't meet the stated ship date. Beyond that, how long does the customer have to walk away with no penalty? Recommendation: **deposit fully refundable until 14 days before build start; forfeit after.** Build start = the day the carbonator vessel for that unit goes onto the welding fixture.
4. **Shipping cost handling.** Per [appliance-freight-bench-gap.md](appliance-freight-bench-gap.md), shipping is a real cost (small parcel vs. LTL white-glove, by carton class). Three options: include in $7,500 (clean number, exposes margin to freight variance), surcharge by destination zone (transparent but adds friction), or itemize on the balance invoice at actual cost (fairest, requires telling the customer the freight number at the balance moment, not at the deposit moment). Recommendation: **include in $7,500 to CONUS-48**, surcharge AK/HI/territories, name this in the terms doc.
5. **Stripe vs. Square vs. PayPal Invoicing.** Recommendation is Stripe for the reasons in §5 (chargeback evidence tooling, Stripe Shipping integration, webhook ergonomics, future React/Node integration). Square is a viable alternative; PayPal is too consumer-grade for the $7,500 founder-touch positioning. Worth a quick second look before committing to Stripe; switching costs are real but not catastrophic at <50 units.
6. **Sales-tax software.** At Nebraska-only volume, manual filing is fine — one return per quarter or year depending on registration. If Standard Edition ever opens, TaxJar or Stripe Tax (which now integrates directly into Stripe Invoicing) is worth the ~$200/month for automated remittance. Out of scope for unit 001.
7. **Terms of sale review.** The terms PDF should be reviewed by a Nebraska-licensed attorney before unit 001's deposit, even if the founder-voice tone stays. Cost is bounded (~$500–1,500 for a one-shot review of a single-page document); the alternative is a worst-case dispute where the terms don't quite say what Derek meant. Cross-references to the today-siblings (warranty, freight, install, CO2, portal) should be reviewed simultaneously — the warranty terms in particular interact with state-by-state implied-warranty law.
8. **CRM vs. spreadsheet.** At unit volume <50, a spreadsheet is correct. Resisting the urge to install HubSpot is a feature, not a bug. Future-agent note: don't recommend this until volume justifies it.

---

## 10. Why this matters before any other today-sibling work proceeds

Every today-sibling document picks up after an order exists. Concretely:

- [warranty-and-rma-gap.md](warranty-and-rma-gap.md) implicitly assumes the customer's name, contact info, and unit serial are recorded somewhere. The order flow is what creates that record.
- [per-unit-portal-gap.md](per-unit-portal-gap.md) commits to `/u/NNN` URLs that need to know which customer owns which N. The order flow is what mints the binding.
- [install-consult-playbook-gap.md](install-consult-playbook-gap.md) describes the Zoom call that ships with every Founder Edition. The "ships with" language presumes a paid order. The order flow is what schedules the consult.
- [appliance-freight-bench-gap.md](appliance-freight-bench-gap.md) needs a destination address before it can quote a carton class. The order flow captures the address.
- [co2-supply-ownership-gap.md](co2-supply-ownership-gap.md) wants to send a customer down a CO2 supply path tied to their actual install. The order flow has the customer.

This means the order-and-payment-flow gap is not an item *alongside* the today-siblings; it is *upstream* of all of them. Whichever of those siblings gets executed first will discover this gap at the moment it tries to look up a customer record and find that no system creates customer records. Better to design the order system first and let the siblings reference into a real schema.

---

## 11. One-paragraph version, for Derek

You've committed publicly to selling $7,500 numbered hand-built appliances with a multi-month build queue, but there's no document anywhere in the repo describing how anyone actually pays you for one. The recommendation is: $500 refundable deposit at order via Stripe Invoicing, plaque number reserved at that deposit, balance charged 5–10 days before ship via a second Stripe Invoice, with a firm written ship-by date in a plain-English terms doc the customer e-signs. This shape (a) keeps you compliant with the FTC Mail Order Rule (which the repo has never mentioned and which directly governs everything here), (b) parks most of the dollar exposure inside the chargeback dispute window where it can be defended, (c) keeps Stripe's risk model from holding meaningful cash in a 90-day rolling reserve, and (d) gives the warranty/freight/install/portal/CO2 siblings a real customer record to read from. Ring 1 and Ring 2 buyers (friends, friends-of-friends per the rings-of-trust plan) skip the deposit dance entirely — Stripe Invoicing at ship is enough for them. Nebraska sales tax only, until volume actually approaches an out-of-state nexus threshold years from now. The single most important pre-unit-001 artifact is `business/terms-of-sale.md`, lawyer-reviewed, because the alternative is taking $7,500 from a stranger with no written record of what you both agreed to.
