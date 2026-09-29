# c2 — Buy the crimp: factory-crimped XH leads, and what is left to build

A part and product change: contacts arrive already crimped on wire, by JST's
applicators or an RC-accessory maker's. Most variants change the loom's wire;
what remains on the bench is insertion, dressing and the far end. Its genuine
JST lead is also the reference crimp for every other arrangement (below).
Numbers: [`../calc/ctq.out.txt`](../calc/ctq.out.txt) §8.

## Picture it

Three things can arrive, and each leaves a different job on the bench. In
every case the crimp was located, driven and made in someone else's
applicator; on the bench the only thing located is the crimped contact in its
cavity, by the housing itself, and the only force is the insertion push. What
is checked, and how, is under "How it knows it worked".

### (a) JST's own pre-crimped jumper leads

- **What they are.** JST ASXHSXH22K series, sold by Digi-Key.
  - "Black 22 AWG Jumper Lead Socket to Socket Tin".
  - SXH contacts factory-crimped on both ends, no housing.
  - 2, 4, 6, 8, 10 and 12 in.
- **Price and stock.** The 12 in (304.8 mm) lead ASXHSXH22K305 is $0.90 each,
  $0.765 at 10, $0.65 at 100, with **26,279 in stock**
  [source: Digi-Key product page, observed 2026-09-28].
- **The insulation type is not given** on the page. UL1007 PVC is the usual
  wire for these leads [assumption].
- **On the bench:**
  1. Cut one end off (or cut the lead in half for two pigtails).
  2. Push each crimped contact into its XHP cavity until it latches.
  3. Dress the loose wires flat.
  4. Cut to length and make the far end.

  No crimp, no strip at the XH end, no contact placement.
- **What it covers.** Usable single-ended length is ~290 mm.
  - Of the ten looms only **J5 RELAYS (~100 mm)** fits [calc §8;
    repo ac-wiring-schedule.md].
  - J4, J6 and J7 run in or to the cold core, which asks for silicone, not
    PVC [repo bom.md §11]. They are out even if the length fitted.

### (b) RC LiPo balance leads: XH housings already populated on silicone wire

- **The market.** XH is "used by many radio control (R/C) batteries"
  [source S32]. The balance plug of a 3S–8S pack is an XH-4 to XH-9 housing
  (one more contact than cells).
- **What the coordinator's Prime pass found** [sourcing/amazon-prime.md,
  observed 2026-09-28]:

  | Listing | What it is | Length | Price | Volume signal |
  |---|---|---|---|---|
  | elechawk JST-XH 4S (XH-5) balance extension, 5 pieces, https://www.amazon.com/dp/B07Q29TG24 | 22 AWG silicone, JST-XH; "separate insulation", not bonded flat | 200 mm (the only length in the family) | $8.99 | 376 ratings, 50+ bought last month; 3S and 6S siblings with 513 and 154 ratings |
  | 10-piece JST-XH 8S (XH-9) balance extension, https://www.amazon.com/dp/B08L36NDVX | 22 AWG, 9-pin XH | 300 mm | $13.99 | 32 ratings |

  500–600 mm at 22 AWG was not found.
- **What arrives.** A finished XH housing with n contacts crimped on n
  silicone wires, coloured, not bonded flat.
- **On the bench.**
  - Cut to loom length and make the far end.
  - For J2, remove contact 3:
    - with an extraction tool: JST's XJ-06 [mfr S10], $63.69 at Digi-Key
      [xh-facts §2], or the Prime-confirmed JRready kit with an XH2.54 tip,
      $34.00, one rating [sourcing/amazon-prime.md];
    - or a printed lance-release pin through the window;
    - or cut its wire flush and sleeve the stub.

    Only extraction leaves the cavity truly empty. The repo relies on an empty
    cavity 3 as the guard [repo cable-assemblies.md § MANIFOLD B].
- **What it covers.** The gauge is right (22 AWG) and the jacket is right
  (silicone). The lengths are 200–300 mm, so by length only J5 (~100 mm) fits;
  every other loom is 350–600 mm [ctq §8].

### (c) Single pre-crimped XH wires

- **What exists** [sourcing/amazon-prime.md, observed 2026-09-28]: the elechawk
  "XH 2.54 connector kit with 22 AWG pre-crimped silicone cables", 2–6 pin
  housings, contacts crimped on one end, 6 colours × 15, $16.99, 95 ratings,
  100+ bought last month, https://www.amazon.com/dp/B0CM315RFP. The wire length
  is not stated, and it is not black-only.
- **On the bench.** The whole XH job is insertion, which is the territory of
  the into-the-housing explorer, plus laying n wires side by side as a flat
  group.
- **As a supply for a machine it is the hardest form.** Loose flying leads in a
  bag tangle, and each contact's roll about its wire is random. A machine
  inserting them has to singulate floppy parts, which is where the Sogang
  inserter's failures came from (transfer 43/50 against insertion 49/50
  [prior-art]). It reduces the XH job to hand insertion.

**What the person does, in every variant:** insert (or, for (b), extract J2's
contact 3), dress the wires, cut to length, make the far end.
**Steps covered:** strip, place and crimp, by purchase; verify (lot check,
wafer test). **Hands back:** insertion (a, c), extraction (b), dressing, cut to
length, the far end.

## What question it changes

The listed steps assume the contact is crimped on the bench. It can be bought
crimped. That moves the whole priority step into a factory, and shows exactly
which of the repo's needs (cold-core silicone, loom length, J2's guard cavity,
all-black, flat dress) a bought end fails.

## How it knows it worked

- **Incoming lot check.** From each bag or lot, section one contact and
  measure crimp height at the barrel centre with a point micrometer
  [prior-art §6]. Pull two to 39.2 N [mfr S6].
- **After insertion.** Every finished housing goes onto the same real-wafer
  tester as c1: order, opens, shorts and J2's empty cavity.

## The one variant that matters to every other arrangement: the reference crimp

- **What it gives.** A $0.90 JST jumper lead carries **two genuine JST
  applicator crimps of SXH-001T-P0.6 on 22 AWG wire.**
- **Why it matters.** JST's crimp height for this contact is licence-gated
  [xh-facts Unresolved 1]. A factory crimp gives every machine in this study a
  target and a sample to hold beside its own:
  - crimp width, bellmouth, brush and window, which transfer directly;
  - the insulation crimp's shape;
  - the pull at 39.2 N as a pass line;
  - **the cut-off tab stub.** The contacts came off JST's reel through JST's
    applicator, so their stub is JST's own. It is the target for every
    severing scheme in the study: terminal-supply's drop-shear and bend-off,
    and any pallet loader that shears before the wire arrives;
  - **insertion into an XHP.** A genuine crimped contact on which to measure
    insertion force and the latch click (xh-facts Unresolved 4) before any
    machine exists.
- **Crimp height transfers roughly.**
  - The lead's wire is not BNTECHGO's 60 × 0.08 mm (0.302 mm² of copper
    [calc C1]). Typical 22 AWG hookup wire carries ~0.33–0.36 mm²
    [assumption] and is commonly 7- or 17/19-strand [assumption; the lead's
    stranding is not stated].
  - Over a ~1.5 mm crimp width the area difference alone moves crimp height by
    ~0.02–0.04 mm [estimate], toward a slightly lower height on the ribbon. A
    coarse-strand bundle also compacts differently from a fine one at the same
    area, so that figure is a floor on the uncertainty.
- **What it calibrates.**
  - hand-tool-as-press's [a1b](../../hand-tool-as-press/ideas/a1b-pawl-out.md)
    grip-position map and [a5](../../hand-tool-as-press/ideas/a5-two-squeeze-plier.md)'s
    per-barrel sweep take the genuine crimp's insulation height and width as
    their target;
  - cut open, its insulation barrel is the real B-crimp against which a
    pre-formed and re-crimped barrel ([c6](c6-pre-form-the-contact.md)) is
    judged;
  - into-the-housing's [i2](../../into-the-housing/ideas/i2-crimp-in-the-cavity.md)
    K1 insulation step copies its closed width and height, and i5's nest takes
    its insertion trace as the reference.
- **Nothing is ordered here.** It is a question for Derek.

## Problems worked through

1. **It does not meet the repo's need everywhere.** It depends on the variant:

     | Variant | Contact | Wire | Length |
     |---|---|---|---|
     | (a) | Genuine | Wrong jacket for the cold-core looms | Short: J5 only |
     | (b) | Unknown maker | Right gauge and jacket (22 AWG silicone); coloured, not bonded flat | 200–300 mm: J5 only |
     | (c) | Unknown maker | 22 AWG silicone, six colours | Unstated |

   - The ribbon's flat dress and the cable-clip channels that take bare
     ribbon [repo cable-assemblies.md, Open item 3] are lost with discrete
     wires unless they are bonded or taped flat.
   - All-black is a stated preference [repo cable-assemblies.md]. RC leads are
     coloured.
2. **Clone crimps from an unknown maker are an unknown.** The lot
   check above is the answer, and it is the same check any home-built machine
   needs. An applicator-made crimp on a known wire is probably more
   consistent than a hand crimp [assumption]. It is not verified.
3. **Buying the ends is not building a machine.**
   - Derek likes building [Derek, weld brief]. This arrangement is here
     because changing what is bought is one way to change the question, and it
     marks where "buy" sits against "build".
   - Two parts of it serve building directly:
     - (a)'s reference crimps;
     - (c)'s reduction of the XH job to insertion, if Derek wants to build
       an inserter first.

## Contribution

- It places the "buy" end of the range with real prices: $0.65 buys a pair of
  genuine factory crimps on 22 AWG.
- It shows exactly where the repo's needs bite: cold-core silicone, loom
  length, the J2 guard cavity, all-black, flat dress.
- It gives every explorer a cheap, genuine calibration sample: crimp form, tab
  stub, pull and insertion.
- **The far end of the axis.** A custom harness house crimping XH onto
  Derek's own ribbon would buy the whole XH end, J2's empty cavity and the
  J4/J7 crossings included [assumption: not sourced]. It is quote-and-wait,
  weeks by post, the opposite of the low-lead-time supply Derek values. It
  marks where "buy" ends rather than a direction.
- Covers crimp and place, by purchase. It hands back insertion (a, c),
  dressing, cut-to-length, and the far end.

## Major unresolved problems

- **Lengths.** Genuine JST leads stop at 12 in; the Prime balance leads found
  are 200–300 mm; the looms are 100–600 mm. Only J5 fits.
- **Wire change.** Every variant swaps BNTECHGO ribbon for discrete, coloured
  wire on the looms it covers: flat dress, the clip channels that take bare
  ribbon, and all-black are lost. Whether that is acceptable anywhere, even on
  J5, is Derek's call.
- **Cold-core looms.** J4, J6 and J7 must be silicone [repo bom.md §11]: that
  rules out (a) there.
- **J2's guard cavity** with a pre-populated XH-6 means an extraction on every
  unit.
- **Crimp quality of (b) and (c)** is an unknown maker's; the lot check above is
  the answer.

## What rests on assumptions

- Balance-lead and pre-crimped-wire listings are as the coordinator's Prime
  pass observed them; their crimp quality is not known.
- The jumper leads' insulation material [assumption].
- The crimp-height transfer estimate [estimate].
