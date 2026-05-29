# Business structure and tax framing

Working note prepared 2026-05-12 for an eventual conversation with a
qualified tax preparer. Not advice — see "Scope" at end.

## Bottom line

Stay a sole proprietor for now. The record-keeping in
[`/hardware/purchases.md`](/hardware/purchases.md) is doing 80% of the
real work here regardless of what entity sits on top of it. Form a
single-member Nebraska LLC *before* the first paid unit ships, not after —
the driver is asset protection for a company shipping a regulated consumer
appliance, not tax savings. S-corp / C-corp aren't worth a thought until
there's real net income to discuss, which is years out on the trajectory in
[`/marketing/target-market.md`](/marketing/target-market.md). Mechanics
for the LLC when the time comes: Nebraska SOS, ~$100 online filing, $13
biennial report. A single-member LLC is disregarded for federal tax —
Schedule C on the personal return, same as today — so formation doesn't
change the tax accounting, only the corporate veil.

## Where the orchard analogy lands

The closest IRS analog to a farmer planting fruit trees and waiting years
for revenue is **IRC §195, "Start-up Expenditures."** §195 capitalizes
costs incurred before a trade or business becomes operational; once the
business begins, $5,000 immediate deduction and straight-line amortization
of the rest over 15 years. Same conceptual shape as the §263A
capitalize-then-depreciate treatment for fruit/nut tree pre-productive
costs — pre-productive build-up recovered against future income — but a
different code section, different recovery method, and without the
§263A(d) farmer election. §195 only fires inside a *bona fide* trade or
business; pre-business expenses don't get §195 treatment, and hobby
expenses don't get deducted at all.

## The §183 question is the real one

The near-term tax question isn't entity choice — it's whether the IRS
would view this as a trade or business or a hobby under **IRC §183.** If
it reads as a hobby, the spend isn't deductible against anything, ever.
The §183 factors look at the kind of documentation a real business
generates as a natural byproduct of operating: a business plan, a BOM, a
capital ledger, supplier records, a customer-acquisition strategy. This
project produces that documentation because the work requires it — the
artifacts live alongside this file in `marketing/`, `hardware/`, and
`business/`.

## §174 and the moving-target caveat

A meaningful share of the spend — prototype iteration, AI-assisted
engineering labor (capitalized per
[`/hardware/purchases.md`](/hardware/purchases.md)), test fixtures,
scrapped vessel revisions — looks like **IRC §174 research and
experimentation.** TCJA changed §174 in 2022 to require 5-year domestic /
15-year foreign amortization. The One Big Beautiful Bill Act (2025) is
reported to have restored immediate expensing for domestic R&D for tax
years beginning after Dec 31, 2024, with a small-business retroactive
election back to 2022. **Confirm current statutory state before any
position is taken on a return** — the framing here is general background
and the area has been moving.

## Sequence

1. Now → first shippable unit: sole prop; ledger discipline.
2. Before first paid sale: form NE SMLLC; product-liability insurance;
   Nebraska sales-tax registration.
3. First sale → operational year: §195 activates for pre-operational
   basis; §174 / §174A on the R&D portion; Schedule C continues under the
   disregarded LLC.
4. Meaningful net income: revisit S-corp election.
5. Institutional capital or retail-channel scale: revisit C-corp. Not the
   current trajectory.

## For the preparer to confirm

- Current state of §174A post-OBBBA, including any 2026 regulations
- Treatment of capitalized AI-assisted contract labor (Anthropic API +
  subscription) — §195 startup vs §174 R&D vs current operating expense
- "Rings of trust" near-cost pricing for the first units (per
  `../marketing/target-market.md`) and any below-market-sale implications
- Nebraska sales-tax registration timing
- Reasonable-compensation analysis if/when S-corp becomes relevant

## Scope

Framework for discussion with a qualified tax preparer, not advice.
Code-section references and the OBBBA framing are general background and
should be verified against current statutory text and regulations.

## Related

- [`regulatory.md`](regulatory.md) — product regulatory posture
  (UL 60335-2-89, EPA §608, SNAP). Separate concern; both this doc and
  that one have something to say about what changes at first customer
  sale.
