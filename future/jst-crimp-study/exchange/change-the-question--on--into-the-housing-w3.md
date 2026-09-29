# change-the-question on into-the-housing (wave 3)

change-the-question treats the five listed steps as one way to cut the problem: a step can be added in front, a part can be changed, the order can be changed. into-the-housing treats insertion as the dexterous step and arranges every crimp around the moment a contact meets its cavity. This file reads into-the-housing's arrangements as they stand after wave 2:
- [i2](../explorers/into-the-housing/ideas/i2-crimp-in-the-cavity.md), now combination K1 with force-and-form's steel C and knee;
- the new [i2d](../explorers/into-the-housing/ideas/i2d-locator-the-lance-never-touches.md), [i6](../explorers/into-the-housing/ideas/i6-sort-then-push.md), [i6b](../explorers/into-the-housing/ideas/i6b-post-bed-through-the-housing.md) and [k6](../explorers/into-the-housing/ideas/k6-one-gantry-crimps-in-the-fan-then-sorts.md);
- the [handover](../explorers/into-the-housing/handover.md) and their [wave-2 calc](../explorers/into-the-housing/calc/wave2.out.txt).

It does not repeat force-and-form's wave-2 reading ([`force-and-form--on--into-the-housing.md`](force-and-form--on--into-the-housing.md)): the lance under the anvil, the two X locators, the wall rule for narrow dies, the geometric bottom, the hump lever, and the force ladder.

- **Numbers:** **[w3 §n]** is [`../explorers/change-the-question/calc/on_into_the_housing_w3.py`](../explorers/change-the-question/calc/on_into_the_housing_w3.py), output in [`on_into_the_housing_w3.out.txt`](../explorers/change-the-question/calc/on_into_the_housing_w3.out.txt). **[w2 §n]** is this explorer's [`wave2.out.txt`](../explorers/change-the-question/calc/wave2.out.txt), and **[ith §X]** is into-the-housing's wave-2 calc.
- **Coordinates** are into-the-housing's: Y along the contact, +Y toward the mating face; X across the row; Z up, with the barrels opening up and the lance down.

---

## 1. Combinations

### S1: Pre-formed contacts, snapped and crimped in their own cavity (c6 + i2/K1)

Built from change-the-question's [c6](../explorers/change-the-question/ideas/c6-pre-form-the-contact.md) (a keyhole insulation barrel formed on a mandrel before any wire, which the jacket then snaps into) and into-the-housing's [i2](../explorers/into-the-housing/ideas/i2-crimp-in-the-cavity.md) as it stands, K1. K1 has the cavity as locator, a floating nest, a steel C with a knee, and stepped dies that bottom on anvil shoulders. There are two branches: one uses i2b's two loading passes, and one runs on strip.

**Why the pairing does something neither does alone.**
- The stepped crimper that fits beside a seated neighbour at 2.5 mm has an insulation step 2.5–2.7 mm wide.
- That mouth cannot swallow the kit clones' open insulation wings (2.46–3.25 mm, §2 B1 below). It can swallow a pre-formed keyhole of 1.96–2.14 mm with 0.23–0.52 mm to spare [w3 §1].
- c6 alone has no host that crimps at housing pitch without the 0.2 mm conductor-step miss beside open conductor barrels [w2 §2]. i2's one-contact-per-cycle order is such a host: the only neighbour in the plane is a seated contact's round wire.

**Picture it.**

*On the bench, left to right.*
1. **The pre-former** (c6), a palm-sized steel station away from any wire.
   - A kit contact sits box-first in a nest. The nest can be a kit XHP stub, i2d's cut housing, used here only as a box pocket.
   - A Ø1.55–1.60 mm pin slides into the open insulation barrel from behind.
   - A jaw closes the wings around the pin to a keyhole: a 1.3–1.5 mm throat and 1.96–2.14 mm outside. That takes ~10–80 N [w2 §3], from a servo lever or the Prime-confirmed POWERTEC 305CM push-pull toggle clamp ($18.25 a pair, 605 ratings [sourcing/amazon-prime.md, observed 2026-09-28]).
   - The jaw is a second cut of the **same wire-EDM profile as K1's insulation step**, stopped where the arch meets the pin. The final stroke then starts on its own profile.
   - Out come contacts that cannot nest (a box does not enter a 1.3–1.5 mm throat [w2 §5]). They are pushed nose to tail into a printed stick, a 2.1 × 2.6 mm channel with a lance groove. One housing's worth is 23–61 mm.
2. **K1's press**, as into-the-housing and force-and-form drew it:
   - a fist-sized steel C beside the row, with its throat (~30 mm) facing the row;
   - a knee driven by a NEMA 17 on a Tr8×2 screw. The Iverntech 42HD6039-05 integrated-screw motor is Prime-confirmed [sourcing/amazon-prime.md];
   - the stepped crimper: a 3.1 mm conductor step with ~0.8 mm walls, and an insulation step of 2.5–2.7 mm whose mouth is cut to ~2.2–2.4 mm;
   - an anvil with a lance relief, rising through a lance-grooved channel plate;
   - a 0.001 mm indicator across the dies. The Clockwise Tools DITR-0105 (RS232 port) is Prime-confirmed at $52.99 [sourcing/amazon-prime.md], against the $451–668 Mitutoyo that i2 cites. Its DTCR-01 data cable had no Prime listing;
   - a load cell under the anvil.
3. **The carriage** on one X rail: the web clamp at the back, a saddle comb at 2.5 mm in housing order, and the floating housing nest in front, located only in Y.

*One cycle, cavity n.*
1. **Contact in.** An escapement finger takes the lead contact from the stick's mouth. A servo finger slides it lance-down along the channel plate, box-first, 1.4–2 mm into cavity n. The anvil rises under the barrels, its front edge behind the hanging lance (the lance condition, [ith G]). The backstop bears on the tab stub for −Y.
2. **Tip set.** The camera measures where conductor n's stripped tip lies over the open conductor U. The hump presser corrects it: 1 mm on the hump moves the tip ~2 mm in +Y [ff §12].
3. **Snap.** The presser foot carries two tines.
   - The rear tine pushes the jacket down through the keyhole's throat into its bore: ~0.5–20 N, a few newtons at central values [w2 §4]. The anvil takes the reaction.
   - The front tine lays the strands into the open conductor U.
   - The keyhole's rounded top is the X lead-in (±0.3–0.5 mm), which the saddle comb meets.
4. **Look.** The camera checks four things before any crimp force exists: the jacket in the bore, the insulation edge in the window, the strands in the U, and none over a wing tip.
5. **Foot up.** The conductor stays down and stays at its Y.
   - The throat holds against lift at ~0.3–10 N. The humped conductor's elastic lift is 1–44 mN [w3 §2].
   - The bore grips 0.2–4 N along the wire, so the hump's elastic relaxation after the presser lifts no longer moves the tip.
6. **Crimp** (K1). The knee straightens.
   - The insulation step's mouth meets a keyhole narrower than itself.
   - The conductor step's flare centres the conductor barrel.
   - The walls land on the anvil shoulders; the nest floats and the steel is the master.
   - The press logs force against the true die gap.
7. **Height and proof.** The knee re-touches at ~10 N for crimp height. Pads grip conductor n behind the barrels and pull −Y to ~20 N against the backstop.
8. **Home.** The anvil drops 1.5 mm. A slotted stencil-steel blade drives the contact in; the insertion trace shows the lance fold, snap and bottom. A 5 N pull-back follows, then the carriage indexes. J2's cavity 3 is skipped.

**What locates what.**

| Stage | Located by |
|---|---|
| Pre-form | Box in the nest pocket; bore set by the pin, throat by the jaw profile |
| Contact | Cavity walls (X, Z, roll), backstop on the tab stub (−Y), anvil (Z at the barrels) |
| Conductor | Saddle comb (X); camera plus hump presser (Y), frozen by the snap |
| First touch and bottom | Steel: insulation mouth, conductor flare, anvil shoulders. The printed nest follows |
| Push | Cavity walls |

**What drives the crimp.** The knee inside the C: 60–160 N at the knee, 0.8–2.6 kN at the dies [digest]. The loop is the C; the carriage and nest carry none of it.

**How it knows.** Every step reports something:
- pre-former silhouette: throat and outside width. A Ø1.50 go pin must enter the bore from behind; the Accusize 0.28–1.52 mm pin set is Prime-confirmed [sourcing/amazon-prime.md];
- the camera after the snap;
- force against die gap;
- re-touch height;
- proof pull;
- insertion trace;
- pull-back.

**What the person does.**
- Pre-forms in bulk at the lever, or lets the servo pre-former run: 53 contacts in ~5–9 min while a print runs [c6 estimate].
- Drops sticks into the feed.
- Splits and strips each ribbon end and lays it over the saddles in housing order. J4's and J7's crossings are made by hand, or by i2's loft picker.
- Loads a housing and lifts the finished end out.

**Conflicts found by combining, and repairs.**
- **Nose-to-tail sticks against the crimper's footprint.**
  - With contacts nose to tail, the next contact's box sits against the lead contact's keyhole, inside the crimper's rear footprint.
  - Repair: an escapement finger singles the lead contact out of the stick onto the channel plate (i2's servo finger, one position upstream). The stick never feeds the cavity directly.
- **Snap force reacted through the lance.**
  - The rear tine's 0.5–20 N must go into the anvil, not into the lance.
  - The anvil's front edge is already behind the lance tip ([ith G]; t ≥ 0.34–0.74 mm). The snap lands on the insulation barrel, over the anvil's rear section, so the lance carries none of it.
- **Re-registration of a pre-curled barrel.**
  - c6's open problem is that a pre-formed barrel meets the arch already closed, so it is not centred by an open mouth.
  - Here the keyhole was cut from this crimper's own profile. The floating nest and the conductor step's flare centre the contact before the insulation step bottoms.
  - What stays unmeasured is what the jacket, already squeezed 6–9 % in the bore, does under the rest of the stroke.

**Branch S1b (with i2b, two passes).**
- **Pass 1: odd cavities.** Pre-formed contacts are loaded, snapped and crimped with empty neighbours.
- **Pass 2: even cavities, between crimped odds.**
  - Loading: pre-formed contacts leave +0.43 to +0.52 mm to the crimped neighbours. Open clone wings leave −0.12 to +0.27 mm [w3 §1].
  - Crimping: the insulation mouth has +0.08 to +0.37 mm to spare, where typical and wide clone wings are 0.05–0.48 mm short [w3 §1].
  - The conductor step clears the crimped conductor barrels by ~0.2 mm a side [ff on i2b].
- **One-pass preload** of a whole pre-formed housing still does not crimp. The conductor step's half-width (1.55 mm) against an open conductor-barrel neighbour has 1.32–1.50 mm of room, up to 0.23 mm short [w2 §2].

**Branch S1c (on strip).**
- SXH strip indexes through the pre-former on its pilot holes, with the pin passing above the tab. It then wraps over i2's crowned block to the cavity.
- No sticks, and orientation is never lost.
- A 100-piece strip is 1.9 units [digest].

**What it leaves uncertain.**
- The insulation crimp over a pre-curl on 1.7 mm silicone: sectioning and pull.
- The snap force band (0.5–20 N) on real kit contacts.
- K1's dies: 0.8 mm walls by quick-turn EDM at ±0.05 mm.
- The transition t on kit contacts.
- Crimping 0.2–0.4 mm from PA6.
- Whether the kit contacts' open wings are narrow enough to make the pre-form unnecessary for the mouth. At ≤ ~2.3 mm they are, and S1 then keeps the pre-form only for the snap. Derek's caliper settles it.

### S2: Half-rows crimped in pallets, sorted into one row, housing pushed on (c1c + i6)

Built from change-the-question's [c1c](../explorers/change-the-question/ideas/c1c-crimp-in-the-row.md) and into-the-housing's [i6](../explorers/into-the-housing/ideas/i6-sort-then-push.md).
- **c1c brings:** interlaced jaws split the ribbon end into two planes. A presser comb snaps or tack-lays a whole half-row into carriers at 3.4 mm. A fixed steel C crimps each contact where it lies with an ordinary single-nest punch, and the carrier holds box, roll and lance groove through the crimp.
- **i6 brings:** a carrier sort into a 2.5 mm target comb in housing order, a backing blade, and the housing pushed onto the row.

**Why it exists.**
- c1c ends in two sequential row pushes with the web clamp and housing still. By into-the-housing's feed-length rule, every conductor of a pushed row must then carry the ~7 mm push as a bow of 4–9 mm over the split [w3 §7]. That is the same zone where c1c's presser comb, pallets and row B's carriers work (§4, the feed-length rule).
- i6 pushes the housing onto one merged row and stores nothing.
- In the other direction, i6's open problems ease:
  - "the staging plane depends on the crimp arrangement upstream";
  - "gripping a 0.043 g contact without roll".

  Here every crimped contact waits in a keyed pocket, at known roll, with open access from above and below.

**Picture it, briefly.**
1. Steps 1–4 of c1c: split, lay and snap row A, crimp it in the row, park pallet A, then lay and crimp row B. Both rows are crimped and proof-pulled on the pocket's rear shoulder.
2. **Pick.** The carrier's upper pad closes on the crimp's two lobes. The lower pad comes up through the carrier's **anvil window**, the path the anvil blade used. The pad pair lifts the contact out of its open-topped pocket with roll unchanged.
3. **Place.** Pallet B, in the working plane, is sorted first; pallet A is swung up into the working plane and sorted second.
   - With J4 laid V5, IO25, 3V3, IO26 | GND, IO27, IO23 and J7 laid RB1–RB4, GND | X, CLO, CHI (X is the trimmed conductor), every upper-layer conductor sits at an odd ribbon position, so in pallet A: J4's 3V3 and GND, J7's GND.
   - "B first, then A, upper layer last" therefore satisfies i6's rule.
   - Straight looms (T4, J1, J2) have no crossing when placed centre outward [ith C]. Their drop need only clear the comb's tines, ~2–4 mm [estimate], not i6's 8–10 mm.
4. **Push.** The backing blade drops and the housing nest drives onto the row. It could instead end on i6b's post bed, which names each conductor before the latch. Then the per-wire 5 N pull-back.

**Person:** keeps the pre-formed sticks (or strip) and the housings stocked; lays each ribbon end in the clamp; lifts ends out. No crossing is made by hand.

**Conflicts and repairs.**
- **Pallet A's path.** Parked down and back, pallet A swings up through the forward-down space where sorted row-B conductors now lie. Sorted conductors travel up to 6.7 mm sideways into row A's vertical planes [ith B], so the swinging row would drag across them.
  - Repair: park A up and back, over the root, if the press's punch and presser comb leave room there.
  - Otherwise: sort row A first while row B is parked, and choose ribbon orders that put upper-layer conductors in B.
- **Length spread.** The rigid backing blade meets a length spread in the push (§2 B6). Repair: sprung tines.
- **Split.** c1c's split jaws need 12–20 mm. i6's sort needs ~25–30 mm on J4 and J7 only.

**Uncertain:**
- the lower pad through a window that was sized for an anvil blade;
- two pallets and a sort stage on one slide;
- everything c1c leaves: the final crimp over the pre-form or tack, and 0.5 mm carrier walls.

### Others, briefly

- **S3: c6b + i2d. The housing stub is the box-keyed clip on the SN-2549.**
  - i2d's cut XHP-2 on its parallelogram flexure, on the lower jaw's M4 screw, is the front stop and roll key c6b wanted from a printed clip: molded at product tolerance, costing cents, never touching the lance.
  - The snapped flag from c6b's snap block goes box-first through the open jaws into the stub. Then one squeeze; there is no one-click captive juggling.
  - Conflict: the stub blocks c6b's fallback of entering from the front with the conductor threaded back. So the SN-2549's open XH nest must pass box plus lance, 2.8–3.25 mm (c6b's open question, now decisive).
  - The stub squares the flag's roll to ±1.2–6.5° [w3 §4], which the snap's friction alone does not.
  - The nose-on-front-wall reference meets the growth problem (§2 B4). In PA6 it dents rather than bends the contact.
- **S4: c5 + S1 for T4 spool runs.**
  - T4 ends (J3, J5, J9, J11, J13) are one layer and straight. A fixed 1.7 → 2.5 mm saddle comb therefore replaces the person's lay-in; the automatic splay that i6 says fails J4 and J7 is fine here.
  - A long run is 21 ends, 84 contacts and 21 XHP-4 [w2 §7]. That is one 100-piece strip through S1c's in-line pre-former and a 120–163 mm housing stick escaping into K1's floating nest: one visit per run.
  - Missing: unattended split, strip and hump-forming of each spool end.
- **S5: c2's genuine JST lead as K1's reference.**
  - ASXHSXH22K305 ($0.90) carries JST's own closed insulation width and height. That is the dimension K1's insulation step has to copy (the handover's item 3).
  - It also carries the tab stub that i2's backstop and i6's blade bear on, and a genuine insertion trace for i5's nest.
- **S6: c6's closed-ring sub-variant in k6's head.**
  - A ring of ID 1.75–1.8 mm centres the jacket while f4's head slides a captured contact along the still conductor, with the strands leading.
  - It trades the snap for a guide; the rear edge needs a flare.

---

## 2. What still breaks in their revised and new ideas

**B1. i2 (K1), i1b, i2b and k6's 2.5 mm variant: the insulation step cannot swallow clone wings** [w3 §1].
- **The conflict.**
  - Open insulation wings stand 2.75–3.20 mm tall, above the conductor wings (1.50–1.60) [source S19–S22]. The insulation step therefore touches first, before the conductor flare has centred anything.
  - Its mouth must be wider than the wing spread plus a capture margin plus a wall land, and that outer width then passes down beside the neighbour to the floor.
  - Beside a seated neighbour's jacket there is a half-width of 1.65 mm. Wings of 2.80 mm have +0.10 to −0.10 mm of margin, 3.00 mm 0.00 to −0.20, and 3.25 mm −0.13 to −0.33.
  - Between crimped insulation barrels (i2b pass 2; k6 at 2.5 mm, where one neighbour is crimped) the half-width is 1.50 mm. Clone spreads fail from 2.46 mm up under the generous margins (−0.08 to −0.48 mm), and from ~2.7 mm up under the tight ones.
  - The drawn step, 2.5–2.7 mm outside, has a mouth of at most ~2.3–2.6 mm.
- **Consequence.** A wing tip that lands on the wall's end face folds outward. The result is a flared insulation barrel that snags the cavity entry or will not enter it (the handover's item 3: "tucked, not flared"), and a jacket held on one side.
- **Repairs and branches.**
  - (a) Pre-form the insulation barrel to 1.96–2.14 mm: S1, with 0.23–0.52 mm to spare.
  - (b) Genuine contacts, if their open wings are near JST's 1.95 mm envelope.
  - (c) In i2 only, let the crimper's outer face push the seated neighbour's jacket aside by up to 0.33 mm. Force-and-form's 0.1 mm shim-sheath branch covers the low end; silicone scraping at 0.33 mm is untested. There is no such relief in i2b, whose neighbours are bronze barrels in cavities.
  - (d) i1b's spreader fingers (~0.5 mm) help beside wires, not beside crimped barrels.
- **Left uncertain.** The kit contacts' open wing width; one caliper reading.

**B2. i2 (K1): the camera-set tip is held only by copper set until the crimper arrives.**
- The hump presser moves the tip ~2 mm per mm of hump. The presser foot then lays the strands into an open U and must leave before the crimper comes down, because they occupy the same space.
- The copper keeps most of the pressed hump. The elastic part recovers when the presser lifts and carries the tip back by its share of the correction [estimate: tens of percent; unmeasured].
- An open U holds the conductor by nothing; the lift force is only 1–44 mN [w3 §2], so the conductor stays roughly in the U, but its Y and Z are unconstrained.
- **Repair: S1's snap.** The bore grips 0.2–4 N the moment the corrected tip reaches it, and the throat resists lift at 0.3–10 N. Without pre-forming, a sprung wire-holder pad inside the crimper, as in applicators, keeps the conductor down through first touch.
- **Uncertain:** the elastic fraction of a pressed hump in 60 × 0.08 mm strands.

**B3. i2b: pass-2 loading between crimped odds collides with wide clone wings.**
- The gap is 2.5 − s/2 − 1.0: +0.27 mm at 2.46 mm wings, +0.10 at 2.80, 0.00 at 3.00, −0.12 at 3.25 [w3 §1].
- i2b's Repair A assumes the evens fit once the odds are crimped. That holds only for wings up to ~2.8 mm, and the insulation mouth (B1) fails for most clones at the same moment.
- Repair: pre-formed contacts (+0.43 to +0.52 mm, and the mouth fits). Or Repair B's two depths, whose shallower contacts have 1.4 mm of wall to hold them.

**B4. i2d and i2d″ (and change-the-question's c1c and c6b): a stop at the box nose blocks the conductor barrel's forward growth** [w3 §3].
- **The conflict.**
  - Coining after the barrel fills lengthens the conductor barrel. Its front edge moves ~0.03–0.11 mm toward the box [estimate].
  - Die friction can push with ~80–520 N [estimate]. The transition yields at ~90–310 N [estimate].
  - With the box nose against the stub's front wall, the growth has to go somewhere:
    - i2d in PA6: the nose bears 54–173 MPa on the stub face, around PA6's yield, so the face dents and the axial reference walks forward with use;
    - i2d″, the steel pocket and post: nothing yields except the transition, which bows ~0.07–0.19 mm. That is JST's bend-up/down fault, ahead of a latch.
- **What is safe.**
  - i2 itself is growth-safe: the box sits 1.4–2 mm into the cavity with its nose free, and −Y is held from behind on the tab stub.
  - hand-tool-as-press's neck blade, bearing on the box's rear shoulder, is safe while the gap between the blade and the conductor barrel's front exceeds the growth. For a 0.3 mm blade that gap is t − 0.3 mm, which is 0.04–0.44 mm for t = 0.34–0.74 mm, so it is marginal at the short end.
- **Repairs.**
  - The stub holds Y only until the first click or capture, then backs off ~0.2 mm by a cam, or retracts on the flexure.
  - Or the stub's Y is a detent at 10–30 N: above the person's 1–2 N push, below the transition's yield.
  - Or i2d's own second version: the stub keeps X, Z and roll, and a 0.3 mm blade on the box shoulder takes Y.
- **Uncertain:** whether the growth is 0.03 mm or 0.1 mm, and how it divides front and back. One test settles it: five SN-2549 crimps with the box nose against a steel feeler leaf (Hotop 0.02–1.00 mm set, Prime-confirmed, $8.99 [sourcing/amazon-prime.md]) and five with the nose free, compared side-on under the ELP camera.

**B5. i2d: roll play with the kit's clone boxes** [w3 §4].
- The stub's roll figure (±1.5–4.4°) uses JST's 1.95 mm box width both as the box and as the lever.
- Clone boxes are 1.85–1.90 wide and 2.2–2.35 tall [source S19–S22]. With the lever as box height, in a 2.00–2.10 mm cavity, they roll ±2.4–6.5°. The top of that range is above the 5° lower bound of the digest's 5–11° window.
- Consequence: a stub from the same kit is still inside the window for most combinations; a loose cavity and a small box is not.
- Repair: pick the stub from the tighter housings by trial, as the stub-depth trial already does, or add a thin shim on the floor side.

**B6. i6: a rigid backing blade against the contact length spread** [w3 §8].
- **The conflict.** The blade sets every **rear** on one line. When the housing advances, the longest contact bottoms first; the shortest is still short by the spread.
  - Clone drawings run 5.8–6.73 mm, each ±0.25 [source S19–S22], and the within-lot spread is unknown.
  - After the first bottoms, the drive either stops, leaving the short contacts perhaps unlatched, or crushes the long one between the front wall and the steel tine.
- **Consequence.** A 0.1–0.25 mm spread is the size of a lance's catch travel [assumption]. The per-wire 5 N pull-back finds it, after the fact.
- **Repair.** i6 already names this mechanism for another purpose: tines on constant-force springs preloaded at 1.25 × single insertion ([i3b](../explorers/into-the-housing/ideas/i3b-staggered-row-one-push.md)). Each contact then seats under its own force and rides back when bottomed, so length spread and stagger are one repair. The springs are Amazon, Prime to be confirmed (into-the-housing's request).
- **Also.** i6's optional proof pull grips each wire "behind the comb". On J4 the last crossing is V5 under GND at 73 % of the span [w3 check of ith B positions], which leaves ~7–8 mm of uncrossed wire next to the comb on a 25–30 mm span. The grip has to fit there, above and below, or the proof pull moves upstream to the pallet (S2) or the crimp head (k6).

**B7. i6b: the post material as sourced** [w3 §10].
- i6b's stiffness (0.06 mm per N at 8 mm free) is for steel.
- The posts come from pulled extra-long header pins: into-the-housing's own sourcing row, and the uxcell 25 mm-pin headers confirmed on Prime. That listing states neither the pin's cross-section nor its material [sourcing/amazon-prime.md]. Header pins are usually brass or bronze [assumption]: 0.12 mm per N at 8 mm, twice the deflection.
- Round 0.025 in music wire (K&S 5005, Prime-confirmed, $7.24 [sourcing/amazon-prime.md]) gives 0.107 mm per N. Its flats-to-flats match the 0.64 mm post; the box's grip on round wire is untested.
- Threading a box at 0.5–1 N of side load then costs 0.05–0.12 mm of the ±0.2 mm capture.

**B8. k6's 2.5 mm variant.**
- Crimping in web order with K1's narrow dies puts a crimped neighbour (insulation 1.9–2.0 mm wide) on one side.
- The insulation-mouth limit on that side is B1's 1.50 mm half-width. Clone wings above ~2.5 mm fail there, and pre-formed contacts pass.

---

## 3. Consistency

- **i6b's 2.54-against-2.50 error.**
  - "Over nine positions that would be 0.36 mm off" counts nine intervals. XHP-9 has eight: first to last is **0.32 mm**, ±0.16 mm if centred; XHP-7 is 0.24 mm [w3 §5].
  - The conclusion stands (2.54 would eat most of the ±0.2 mm capture). The number is 0.32.
- **i6b posts:** steel stiffness quoted, header pins sourced (B7). Which is right depends on the pin material, which the Prime row did not record.
- **i2d's roll** (calc H) uses JST's envelope and the box width as the lever. For the kit's clone boxes, lever = height gives ±2.4–6.5° [w3 §4]; for JST's own envelope, ±1.2–3.6°. Both files agree the window is 5–11°.
- **Silicone modulus.**
  - into-the-housing's calc D and F bracket E at 1, 3 and 10 MPa [estimate]. This explorer's c6 calc uses 2.5–5.5 MPa from Shore 50–70A by Gent's relation [w2 §4; Shore via ribbon-as-pallet's Primasil source].
  - On the Shore-derived range:
    - the target-slot hold is 1.4–20 N [w3 §6]; at the stiff end a 1.50 mm slot over 10 mm holds 10–20 N, the size of the 9.8 N clone insertion figure;
    - the jacket takes 33–52 % of a grip mismatch over 2 mm and 13–24 % over 3 mm.
  - Neither changes a conclusion: the blade still reacts the push, and the fingers still go loose. The narrower range is the one with a source behind it; BNTECHGO states no hardness.
- **"Change-the-question's least-crossing layout"** in [ith A] is scored with a different metric than the one it came from.
  - The two metrics, for J4 [w3 §9]:

    | Metric | What it counts | J4 laid 3V3, IO26, V5, IO25 \| GND, IO27, IO23 | J4 laid V5, IO25, 3V3, IO26 \| GND, IO27, IO23 |
    |---|---|---|---|
    | c1's order search | off-parity conductors and in-plane crossings after the parity split into two planes | 2 and 2 | **2 and 2** |
    | into-the-housing's | layers and crossings in one plane | 3 layers, 5 crossings | 2 layers, 5 crossings |

    Both counts are right for their own machines.
  - The useful result: **V5, IO25, 3V3, IO26 | GND, IO27, IO23** is the two-layer order for i6 and a least-crossing order for half-rows (c1, c1c, S2). It is one 4P order Derek can fix in `cable-assemblies.md` for every family.
  - For J7, which 3P conductor is trimmed does not matter in one plane (2 crossings either way). In half-rows, trimming the conductor next to the 5P gives (0 off-parity, 1 crossing); trimming the far one gives (2, 1) [w3 §9]. The repo says "third conductor trimmed", which names one end only once the 3P's orientation is fixed.
- **Seated rear depth.**
  - The handover's 0.2–1.25 mm inside the rear face uses contacts of 6.1–6.73 mm. The HDGC clone drawing (5.8 ±0.25) puts the rear up to **1.8 mm** inside [w3 §8].
  - The finishing blades of i1, i2 and i5 must reach ~0.55 mm further, and i6b's housing travel along the posts shrinks by the same amount.
- **Carrier pitch in i2's crown.**
  - i2's crown radius (6.3–12.5 mm for 7.1–9.5 mm strip pitch) inherits the digest's "~7.1 mm (Würth's public drawing of the analog part)".
  - Section C-C of that drawing gives a 1.45 × 2.00 mm box. It is a smaller contact, not an XH analog [w2 §1, mfr Würth drawing rev H].
  - What stands for SXH is xh-facts' 7–9.5 mm scaled from clone drawings that are not to scale. i2's crown range still spans it; only the attribution changes.
- **Agreements checked:**
  - XHP-9 overall width 24.8 mm [mfr S2];
  - the lance tip at 2.24–2.64 mm behind the front (xh-facts gives 2.4–2.6 across S19–S22, and S22's ±0.20 gives i2's lower bound);
  - the force ladder: 5 N latch test, 14.7 N (analog) or 19.6 N (clone spec) retention, 19.6 N proof pull, 39.2 N pull-out;
  - J1's 13.2 mm outer travel at 5 mm pitch;
  - supply per strip (1.9 units).

---

## 4. Transfers

### From change-the-question into into-the-housing

- **Pre-form the part before it meets the wire** (c6).
  - For K1, i1b, i2b and k6's 2.5 mm variant it is the repair for the insulation mouth (B1) and for i2b's pass-2 loading (B3).
  - The snap freezes the camera-set tip in place (B2).
  - Pre-formed contacts do not nest, so i2's contact feed becomes a stick instead of a pocket tape the person fills. For identical contacts, the stick's order carries only count and J2's blank.
- **Take the keyhole from the tool.** K1's insulation step is custom EDM anyway. The pre-former's jaw is a second cut of the same profile, stopped at the pin, so the final stroke starts where it would have been.
- **Change the pin map instead of the machine** (the c4 move applied to the board).
  - i6's sort, i4's loft and i2's loft picker are there chiefly because J4 and J7 cross; pairs and J2's gap are one layer [ith A]. Board pin orders that make each ribbon one layer [w3 §9]:
    - J4 = 3V3, IO26, V5, IO25, GND, IO27, IO23 (or V5, IO25, 3V3, IO26, GND, IO27, IO23);
    - J7 = RB1, RB2, RB3, RB4, GND, CLO, CHI.
  - procedure-is-the-machine's J7 rewire (GND on the 3P) needs no board change. A J4 reorder does: `pcba.tsx` routes IO25, IO26 and IO27 so that the present west-to-east order "lands uncrossed" [repo], so it costs routing work.
  - With both changed, every loom is one layer, and a fixed comb per loom (i3's fan plate, with J2's gap as a blank slot) places the whole unit. Derek's question.
- **Size the supply to the run** (c5). A T4 run of 21 ends needs 84 contacts, one 100-piece strip and a 120–163 mm housing stick. That gives K1 or i6 one visit per spool (S4).
- **A genuine factory crimp as the reference** (c2). The JST lead's insulation width and height, tab stub and insertion trace are K1's die target, i6's blade seat and i5's reference trace (S5).

### From into-the-housing into change-the-question

- **The feed-length rule breaks c1's and c1c's two sequential row pushes.**
  - With the web clamp and housing still, each pushed row stores its ~7 mm of travel as a 4–9 mm bow per conductor over a 6–26 mm split [w3 §7]. Neither idea file provides it.
  - Repairs:
    - S2: merge both crimped rows into one target row and move the housing, storing nothing;
    - or a hump bar under each row, released by the pusher, which puts a 4–9 mm hump where the presser comb works;
    - or the housing moves onto row A, and only row B stores its travel.
  - Of everything in this exchange, it reaches furthest into change-the-question's arrangements: c1's and c1c's last steps change.
- **The lance condition** [ith G], t ≥ 0.34–0.74 mm or a slot:
  - c1c's anvil blade must stop behind the lance tip. Its lance groove "out through the open front" clears the lance in the carrier, not over the blade;
  - c6's pre-former nest and c6b's snap-block pocket must react 10–80 N and 0.5–20 N on the barrels, never on the lance.
- **The housing stub as a pocket** (i2d). c6's pre-former nest and c6b's snap-block pocket can be cut kit XHP housings: box fit at product tolerance, costing cents, lance never touched. For the pre-former, force against the front wall is only the 10–80 N forming load's friction, so B4 does not arise there.
- **Rear references are growth-safe** (i2's backstop, i2d's shoulder-blade version).
  - c1c's hardened box-face front stop and c6b's clip front stop become stops that hold until capture and then back off ~0.2 mm, or detents at 10–30 N (B4).
  - c1c's carrier spring, 0.1–0.5 N, may stay in contact through the stroke.
- **Steel as master in X** (i2, Break 2 repair A). c1c's printed pallet on a stepping slide has the same two-locator conflict as i2's nest: printed pocket ±0.1 mm, screw step ±0.02 mm. The pallet floats in X on a flexure, and the punch's flare centres each contact.
- **A crossing is an order of placement** (i6).
  - c1c's presser comb gets one tine that can be held back. With J7 laid RB1–RB4, GND | X, CLO, CHI, plane A has one crossing (GND over CLO) [w3 §9]: stroke 1 lays and snaps everything but GND, and stroke 2 lays GND over CLO.
  - J4 still needs its two off-parity conductors moved between planes at the split jaws (a J4 jaw insert), or S2's sort.
- **The post bed** (i6b). If c1c keeps pushing rows into a housing, the housing standing on posts guides row B's boxes past row A's wires, and names each conductor before the latch.

---

## Questions this exchange adds for Derek

- **Open-wing width.** Caliper the open insulation-wing width of three kit contacts, as asked before. It now also decides whether K1's narrow insulation step can crimp them without pre-forming (B1). The threshold is ~2.3 mm.
- **Growth against a nose stop.** Five SN-2549 crimps with the box nose touching a steel feeler leaf held across the front of the nest, and five with the nose free, then side photos. Does the transition bow (B4)?
- **J4's 4P order.** Fix it as V5, IO25, 3V3, IO26 | GND, IO27, IO23 in `cable-assemblies.md`? It suits the sort (two layers) and the half-rows (two off-parity conductors, two crossings) alike.
- **J7's trimmed conductor.** Which one is "third": the one beside the 5P, or the far one?
- **Board pin order.** Would a board revision of J4's and J7's pin order, making every loom straight across, be on the table?
