# Making XH cable ends — an exploration

A collection of developed possibilities for machines and robots that make the
JST XH cable ends on the appliance's 22 AWG silicone ribbon looms: splay the
conductors, strip them, place the contact on the conductor, crimp, and insert
into the XHP housing. It was produced on 2026-09-28 by one coordinator and nine
explorers, each seeing the whole procedure a different way. The brief is
Derek's, in
[`context/brief.md`](context/brief.md). Its core sentence:

> if this machine works ***VERY*** slowly that is perfectly okay, one single little crimp on one 3P or 4P or 5P cable at a time

The step he most wants automated is "placing the metal bit on the end of the
cable, placing that metal bit and cable in something that crimps and crimping
it"; getting the whole procedure automated "would be ideal" [Derek].

Nothing here is ranked or selected. Families are grouped by how the contact and
the conductor come together, and the order within a family is only the order
the relationships read. Large unresolved problems sit beside the idea they
belong to.

**Conventions.**
- Nothing was built, bought or operated.
- The contact is SXH-001T-P0.6 (JST's strip form) or the loose equivalent in
  the CQRobot kits on the bench, whose origin is unknown.
- The wire is BNTECHGO 22 AWG black silicone flat ribbon in 3P, 4P and 5P, at
  1.7 mm per conductor. A unit takes 53 XH crimps on 14 ribbon ends in 10
  housings, about 3,200 over the program [repo].
- Prices and stock were observed on 2026-09-28. Amazon listings appear only when
  Prime-confirmed on the product page, marked [Prime]
  ([`sourcing/amazon-prime.md`](sourcing/amazon-prime.md)).
- Labels: [Derek]; [repo]; [mfr], a manufacturer document; [source], another
  published source; [calc], an explorer's calculation kept in its `calc/`;
  [estimate]; [assumption].
- Codes such as HT a2 or FF f3 are the [index](ideas-index.md)'s: the
  explorer's two letters and the idea's own id. Every code links to its file
  somewhere below, and the index links them all.

## Where things are

| Path | What it holds |
|---|---|
| `explorers/<name>/summary.md` | Each explorer's account of every arrangement it holds, its transferable mechanisms and its questions for Derek |
| `explorers/<name>/ideas/` | The developed idea files, each opening with "Picture it"; branches have their own files and say what they change |
| `explorers/<name>/sketches/` | SVG sketches, schematic unless drawn from cited dimensions |
| `explorers/<name>/calc/` | Python and notes for every [calc], with the output kept beside it |
| `explorers/<name>/notebook.md` | Running logs, rejected directions and what would revive them |
| `exchange/` | Critic-on-originator files, one view reading another |
| `sourcing/` | The [parts overview](sourcing/README.md) and the [Prime listings](sourcing/amazon-prime.md) |
| `context/` | What the explorers started from: [brief](context/brief.md), [shared context](context/shared-context.md), [working method](context/working-method.md), [XH facts](context/xh-facts.md), [prior art](context/prior-art.md), [digest of shared numbers](context/digest-wave1.md) |
| [`families.md`](families.md) | Every arrangement described in a few sentences, grouped by the map's rows, with the connections that cross families |
| [`ideas-index.md`](ideas-index.md) | Every arrangement, one line each, tagged by steel source, contact supply and the steps it automates |

## The nine views

| Explorer | Way of seeing the whole procedure | Arrangements |
|---|---|---:|
| [hand-tool-as-press](explorers/hand-tool-as-press/summary.md) (HT) | The crimp tool is already the machine | 15 |
| [terminal-supply](explorers/terminal-supply/summary.md) (TS) | How the contact arrives decides everything downstream | 16 |
| [force-and-form](explorers/force-and-form/summary.md) (FF) | A crimp is a small, slow sheet-metal forming operation | 16 |
| [ribbon-as-pallet](explorers/ribbon-as-pallet/summary.md) (RP) | The ribbon is a precision part | 19 |
| [into-the-housing](explorers/into-the-housing/summary.md) (IH) | Insertion is the dexterous step | 15 |
| [borrowed-machines](explorers/borrowed-machines/summary.md) (BM) | Somebody already mass-produces most of this, for another purpose | 13 |
| [procedure-is-the-machine](explorers/procedure-is-the-machine/summary.md) (PM) | The sequence and the division of labor are the design | 15 |
| [machine-that-sees-and-learns](explorers/machine-that-sees-and-learns/summary.md) (SL) | The first stage of a cell is one software can move and observe | 12 |
| [change-the-question](explorers/change-the-question/summary.md) (CQ) | The five steps as listed are one way to cut the problem | 10 |

## A map

Rows: how the contact and the conductor come together. Columns: where the crimp
steel comes from. ◇ marks an arrangement usable without a motor in its first
form. Each arrangement sits in the cell its own explorer tagged, though many
could sit in several.

| | **Hand-tool dies** (SN-2549, JST WC-110, Engineer PA-09) | **Bought applicator or knife set** | **Made dies** (EDM, machined, laser-cut) | **Several or any** | **No crimp dies, or not applicable** |
|---|---|---|---|---|---|
| **[The conductor comes to a fixed die](families.md#the-conductor-comes-to-a-fixed-die)** | HT a2 · HT a2b · HT a2c · HT a2d · HT a4c · HT a6c · ◇TS a2c · ◇TS x1 · ◇FF f1 · ◇FF f1b · BM b2 · ◇CQ c6b | TS a1 · TS a2 · TS a2b · TS a2d · TS a3b · TS a4 · TS x2 · ◇FF f2 · ◇FF f2b · FF f2c · RP a1 · RP a1c · RP a4 · BM b1 · ◇BM b1b · BM b1c · BM b8 · ◇BM b8b · SL v9 · ◇SL v9b | PM p1d · PM p5c | ◇FF f3 · ◇FF f3b · FF f6 · ◇FF f9 · ◇FF f10 · RP a1b · IH i1 · IH i3 · IH k8 · ◇PM p1 · PM p1b · PM p5 · SL v1 · ◇SL v3 · SL v6 · ◇SL v8 · CQ c1 · CQ c1c | |
| **[A die head comes to a still conductor](families.md#a-die-head-comes-to-a-still-conductor)** | HT a3 · HT a4b · PM p1c · PM p5b | BM b3 | IH i1b | FF f4 · IH k6 · PM p2 · PM p3 · PM p3b · ◇PM p6 | ◇CQ c3 (solder) |
| **[Two pallets dock](families.md#two-pallets-dock-every-contact-placed-at-once)** | HT a4d · ◇RP a10b | RP a2 · RP a2d · RP a2e · ◇RP a9 · PM p6b | RP a10 · ◇CQ c1b | ◇FF f9b · RP a2b · ◇RP a2c | |
| **[The housing locates the contact](families.md#the-housing-locates-the-contact)** | ◇IH i2d | TS a4b | TS a4c · TS x3 · FF f8 · IH i2 · IH i2b · IH k7 | TS a5 · IH i2c | CQ c4 (IDC) |
| **[The person presents, the machine takes](families.md#the-person-presents-the-machine-takes)** | ◇HT a1 · HT a1b · ◇HT a4 · ◇HT a5 · ◇HT a6 · ◇HT a6b · ◇IH i5 · BM b2b · PM p4b | | ◇FF f5 · ◇FF f5b | PM p4 | |
| **[A general-purpose arm or gantry hand](families.md#a-general-purpose-arm-or-gantry-hand)** | | TS a6 | | IH i4 · BM b5 · SL v1b | SL v2 |
| **[Supporting stations and modules](families.md#supporting-stations-and-modules)** | | | ◇CQ c6 | ◇FF f7 · CQ c5 | ◇CQ c2 (bought) · TS a3 · TS a7 · ◇RP a3 · ◇RP a5 · ◇RP a6 · ◇RP a7 · ◇RP a7b · ◇RP a8 · ◇RP a8b · IH i3b · IH i6 · IH i6b · BM b4 · BM b4b · ◇BM b6 · ◇BM b7 · ◇PM p7 · SL v4 · ◇SL v4b · ◇SL v5 · ◇SL v7 · ◇CQ c7 |

Read across a row to see one way of bringing contact and conductor together
built on different steel, and down a column to see what one source of steel is
asked to do; the bottom row holds the modules the other rows plug in.

## What the study came to understand

These findings bear on many arrangements at once. Where several explorers
reached one independently, that is noted. The numbering is for reference only.

1. **Force is cheap; crimp height is geometry.**
   - Peak die force is about 0.8–2.6 kN, needed only in the last 0.1–0.2 mm of
     the stroke; the ~0.7 mm of wing curl before it takes tens to a few hundred
     newtons [calc]. Energy is 0.13–0.48 J a crimp. A slow stroke does no harm:
     copper's flow stress is 5–8 % lower at a crawl [source].
   - Almost any slow drive supplies it [calc]: a NEMA 17 through a 30:1 worm on a
     2.5 mm eccentric; a 15 mm crank at under 3.3–4 N·m ([FF f2](explorers/force-and-form/ideas/f2-crank-press-for-an-applicator.md)); a knee
     pushed at 60–160 N ([FF f3](explorers/force-and-form/ideas/f3-knee-micropress.md)); a Tr8×2 pusher at a hand tool's grip,
     ~280 N ([HT a1](explorers/hand-tool-as-press/ideas/a1-squeezer-cradle.md)); a 150–200 mm hand lever at 15–20 N on an eccentric
     ([HT a4](explorers/hand-tool-as-press/ideas/a4-dies-in-a-die-set.md)). On a crank around an applicator, the applicator's return
     springs size the motor, not the crimp.
   - The precision is the bottom of the stroke, ±0.02–0.05 mm [estimate], and it
     comes from geometry: dies that bottom; a hard stop in a short steel loop; a
     crank at bottom dead centre, where 1° off is 3–4 µm; a knee at straight,
     where 0.2 mm short is 1.3–2.7 µm [calc].
   - With stop blocks, a soft outer frame is the design. A 5–10 kN/mm frame pays
     1.05–1.4× the crimp force for its overtravel margin and caps a doubled
     contact at 3.9–5.4 kN; a 40 kN/mm frame pays 1.3–2.6× and puts 14.4 kN into
     one [calc, PM]. A preloaded disc stack is the steel ceiling where one is
     wanted.
   - Printed parts guide, carry and locate coarsely; they never set height or
     carry the crimp.
   - Open: whether the SN-2549's jaws bottom face to face. If not, handle force
     and cradle stiffness set its height.
   - Every explorer that sized a drive reached this.
2. **Crimp height is a compaction target, and a $0.90 genuine crimp is the
   reference.**
   - JST's height for SXH-001T-P0.6 is licence-gated [mfr]. In circulation:
     ~0.88 mm (0.69–1.12) on this ribbon [calc]; 0.73 ±0.05 mm in a clone
     maker's (KONNRA) specification [source]; 0.80 × 1.50 mm for JST's
     similar-size SXA [mfr].
   - These are one compaction at different widths, so the target follows the
     die's channel width: 0.80–0.88 mm at 1.50 mm, 0.74–0.81 at 1.63, 0.69–0.75
     at 1.75 [calc, FF and RP]. Pin-gauging each die's channel and setting
     height for that width makes ±0.05 mm quick-turn EDM usable. No source
     tolerances the roof form.
   - JST's ASXHSXH22K305 lead ($0.90, Digi-Key) is a genuine crimp to measure,
     section and pull ([CQ c2](explorers/change-the-question/ideas/c2-buy-the-crimp.md)). Its stranding differs from this ribbon's, so
     its height transfers through a copper correction at the machine's own
     channel width.
   - Height on the machine: a ~10 N re-touch read by a 0.001 mm indicator
     (Clockwise DITR-0105, $52.99 [Prime], though no Prime listing was found
     for its DTCR-01 data cable; or the AICEYI ACE-Q25, $109.99 [Prime], with
     its USB data cable, $39.99 [Prime], thin); a crank stopped short and read
     by a 14-bit encoder ([SL v3](explorers/machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)); a roll-corrected silhouette ([SL v5](explorers/machine-that-sees-and-learns/ideas/v5-inspection-booth.md)).
3. **Open contacts collide at 2.5 mm pitch.**
   - Clone drawings show open insulation wings 2.46–3.0 mm wide, up to 3.25
     with tolerance [source]; JST's end-view envelope is 1.95 × 2.4 mm [mfr].
     About 3.3 mm is free between the jackets of the two neighbouring
     conductors; an SN-derived punch needs 2.8–4.1 mm, and a crimper narrow
     enough to pass a neighbour has an insulation mouth of only ~2.3–2.6 mm
     [calc, HT and IH].
   - Crimped contacts do fit side by side at 2.5 mm, with 0.45–0.70 mm between
     insulation crimps [calc], so a one-conductor station can fill a pallet at
     housing pitch in cavity order.
   - The pitch strategies, each paid for somewhere else:
     - lift one conductor out of the row: 3.5 mm over a fin from below (FF
       f10, PM p1d), 6.3–9.2 mm into a C-frame arm (HT a4b), 8.7–14.7 mm into
       a hand tool (PM p1c), or 16–20 mm to an ordinary head above the row (IH
       i1);
     - fold the neighbours back behind the tooling (BM b1, RP a1c, SL v9);
     - split into two planes and crimp half-rows at 3.4 or 5.0 mm (CQ c1, CQ
       c1c, FF f5b, FF f9, FF f4);
     - spread to strip pitch and dock every conductor at once (RP a2, RP a2e,
       RP a9, FF f9b);
     - narrow stepped dies in the row, cavity by cavity with spreader fingers
       opening the neighbour wires ~0.5 mm (IH i1b), or odd cavities first and
       then the evens between crimped neighbours (IH i2b, TS x3, TS a4c);
     - narrow the neighbours to ~2 mm first by a tack or a pre-form, then crimp
       in the row with a tongue ≤4.45 mm wide (HT a4d, CQ c1c, IH k8);
     - crimp at the housing's own mouth (FF f8, IH i2, TS a5).
   - About 3.4 mm fits every contact type and 4–6 mm fits common die widths
     [calc].
4. **A crimp head closes along the contact's floor normal.**
   - A head working on a flat row closes normal to the row, and only a fin anvil
     under the conductor needs to pass through the row's plane [FF, PM].
   - **The side-entry jaw law.** A hand tool making upright crimps lies along
     the row. Once the neighbours carry crimps, the working conductor must stand
     out by the jaw half's depth *a* plus 2.7 mm: 8.7–14.7 mm for *a* = 6–12 mm
     [calc, HT; *a* unmeasured].
   - Hung tip-down across a flat row, a hand tool rolls every crimp 90°, and no
     housing can then be slid on; twisting each back takes annealed strands
     2.3–4× past torsional yield, and the roll left after release is unknown
     [calc, IH]. The escapes are the tool on its side, the
     ribbon on edge, or a fin from below.
   - **Copper sets.** The 60 × 0.08 mm strands yield below a ~67 mm bend radius
     [calc]. Every lift, fork, fan or presser leaves a shape: [FF f1](explorers/force-and-form/ideas/f1-motorised-ratchet-crimper.md)'s fork
     bends each neighbour 26–46°; a hand-tool lift wants a 30–35 mm split and a
     squaring push; a 3.5 mm fin lift leaves 0–0.77 mm at 20 mm free. No sprung
     holder can locate a conductor and yield before it sets, so holders come off
     by timing [calc, BM].
   - **Lift once.** Doing everything to conductor *k* in one lifted pose (trim,
     strip, measure, place, crimp, pull) and then squaring it back leaves the
     waiting conductors with no set [PM].
5. **The lance and the neck decide every anvil, nest and pull plate.**
   - The lance is a tongue sprung 0.6–0.9 mm below the box floor, its tip
     ~2.4–2.6 mm behind the box nose [source].
   - The neck (transition *t* between box and conductor barrel) sets a ladder of
     thresholds [calc]: a flat anvil or fin that stops behind the hanging lance
     needs *t* ≥ 0.34–0.74 mm; a neck blade dropped after the crimp,
     0.50–0.70 mm; a blade the strand tips must stay clear of under camera
     depth, 0.70–0.90 mm; a flat pull plate, 0.35–0.5 mm. Readings of the
     drawings run from 0.2 to 2.28 mm.
   - The lance props a contact on any flat face, 7.6–22° depending on the pose
     [calc]; a lance groove 1.0 mm wide and ≥1.0 mm deep along every pocket and
     shelf is the repair.
   - A crimp drawn rearward drives its lance into the anvil's face, so it is
     lifted 1.0–1.7 mm first, or the head leaves toward the box with its anvil
     dropped 1.5 mm.
   - One side photograph of a kit contact beside a steel rule settles most of
     this; nearly every explorer asked for it.
6. **The carrier strip is side-feed, and tabs are cut from below.**
   - Each contact hangs perpendicular to the carrier by a tab at the rear of its
     insulation barrel, with a Ø1.5 mm pilot hole under the wire's path
     [mfr, source]. The pitch is unpublished: 7.1 mm is Würth's smaller analog
     contact, and scaled clone drawings give 7–9.5 mm. One $4.71 strip settles
     it.
   - The wire lies over the carrier, so the space round a strip-fed anvil is
     fixed: fresh contacts stand open one pitch upstream, and downstream is only
     empty carrier. Neighbours fanned over an attached strip land on waiting
     contacts.
   - The tab shears at 48–158 N; a grip on the box cannot react it (3–200× the
     neck's plastic moment) [calc]. It is sheared from below, away from the
     wire, against a steel land at its root, or before any wire exists, or under
     a tack comb held at its stop.
   - A slow crank can wait at any angle: in the dwell after bottom dead centre
     the crimp is withdrawn, pulled and photographed before the feed moves. The
     feed angles move with the applicator's 30 or 40 mm stroke; a hand-cycled
     jack test ([BM b1b](explorers/borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)) measures them.
   - Contacts per unit run from 55 to 111 by how the strip is used; with every
     other contact removed, the whole program uses 0.89 of one 8,000 reel
     [calc].
7. **Placing the contact on the conductor.**
   - Windows at first die touch [calc]: contact axial ±0.1 mm, lateral
     ±0.15–0.3 mm; conductor axial ±0.2–0.3 mm; roll 5–11°.
   - A 0.64 mm post finds a contact by its box entry (0.60–0.70 mm): a 0.1 mm
     chamfer captures ±0.08–0.13 mm and a near-pointed pin ±0.18–0.31 mm,
     against ±0.04–0.07 mm needed by a camera-steered head [calc, TS].
   - A hand tool holding a contact at its first ratchet tooth pinches the
     insulation wings to 1.4–1.6 mm. Modelled, the bore interferes with a
     1.7 mm jacket by 0.03–0.17 mm on floors of 1.6–1.7 mm, is borderline at
     1.8 and clears at 1.9 or more; the jacket then rolls under a wing or
     stalls [calc, FF]. Today's one-click hand procedure shows that some
     capture height works on the bench's contacts. The repairs: hold short of
     the first tooth, at wing touch; or put the contact on the conductor first
     with its barrels open.
   - The camera's view of the bare length is the axial reference: a fixed depth
     gives ±0.21 mm, a camera correction ±0.07–0.09 mm [calc, PM].
   - **Strip length belongs to the contact.** JST's WC-110 specification strips
     2.4 mm [mfr]; KONNRA's clone specification says 1.6–2.1 mm [source]. The
     2.4 mm figure implies a genuine conductor barrel of 1.80–2.05 mm, against
     1.25–1.5 mm on the clone drawings [calc, HT and SL separately]. It is a
     per-lot recipe value in every stop.
   - The conductor barrel grows 0.03–0.11 mm under coining [estimate], so a
     front stop preloaded to 10–30 N, or one that retracts, gives way.
8. **A tack or a pre-form lets the contact ride on its own conductor.**
   - A single-stroke die meets the insulation wings before, or close to, the
     conductor wings [calc, HT and SL]. A loose close of the insulation barrel is
     a state the full stroke passes through, so the conductor crimp can come
     later, elsewhere, in any tool.
   - **The tack**: a former 0.1–0.2 mm wider than the final insulation crimper,
     stopped 0.2–0.5 mm above the final height [calc, SL]. It wants 0.2–1.5 N of
     grip; estimates of what it gives span 0.1–50 N.
   - A flag (a contact hanging from its conductor) must not drag its lance, so
     it rides 1.1–1.7 mm above the anvil on a sprung seat, which needs 3.6–4.9 mm
     of jaw opening at the nest [calc, HT]. The SN-2549's opening is unmeasured;
     the PA-09 is the fallback.
   - **The pre-form**: a mandrel sized from the measured jacket (1.56–1.57 mm for
     a 1.70 mm jacket) gives a 1.96–2.14 mm keyhole gripping 0.13–3.5 N [calc,
     CQ]. A B-profile die pinches a round keyhole into an O, which needs its own
     qualification; a tall keyhole leaves the tips for the die to finish into a
     B.
   - What it changes: placement becomes a light step that can be watched; the
     heavy crimp goes to a keyed nest, a hand tool, a foot bench or an
     applicator; a camera can look straight down into a still-open conductor
     barrel; narrowed neighbours allow crimping in the row.
   - Open: whether a tacked-then-re-formed crimp equals one pass (sectioning).
     Folding and then soldering instead ([CQ c3](explorers/change-the-question/ideas/c3-fold-and-solder.md)) is not a crimp and sits
     outside JST's support.
9. **Silicone tears: cut shallow and tear the rest, strip before splitting, split
   in tension.**
   - Tensile strength 8–11 MPa, tear strength 15–25 N/mm, and it does not melt
     [source, estimate]. Each conductor is a ~0.72 mm bundle in a ~0.49 mm wall.
   - A 0.15–0.3 mm ligament tears at 3–15 N, and a ring scored to 0.58–0.63 mm
     radius tears off at 2.6–9.2 N [calc]. V-blades come within 0.02 mm of the
     strands at four points; die-hole blades leave an even ring ([BM b7](explorers/borrowed-machines/ideas/b7-borrowed-strip-head-one-conductor.md)).
   - Strip before splitting: two razors close across the whole webbed end and
     the slug of every jacket and web pushes off in one piece, ~20–75 N for
     3P–5P; one backlit frame then measures every bare length ([PM p7](explorers/procedure-is-the-machine/ideas/p7-strip-before-split.md)).
   - A tear stays in the web's neck while the neck is under ~0.6 of the wall
     [calc, RP]. Split in tension: pierce at the root and draw the ribbon so the
     blade runs toward the tip ([BM b6](explorers/borrowed-machines/ideas/b6-pierce-at-the-root-pull-to-the-tip.md)); the clamp face stops the tear
     ([RP a7](explorers/ribbon-as-pallet/ideas/a7-zip-station.md)).
   - At 455 nm copper absorbs ~65 %, so a diode laser can only score [source,
     assumption]. A 40 mm free end off a 25 mm spool hub radius rises 3–15 mm
     out of plane [calc].
   - Open, and large: every explorer names stripping this silicone as
     unresolved. It rests on the unmeasured web neck (repo Open item 5), strand
     offset in the jacket and how this silicone tears. Three hand trials settle
     most of it (see the measurements under starting points).
10. **The insulation crimp on this silicone is set by position and is not the
    strain relief.**
    - The strands slip inside the squeezed jacket at 0.4–9 N [calc, FF]; the
      insulation crimp is invisible in the force trace.
    - A clone-spec 1.80 × 2.05 mm insulation crimp, a PVC figure, squeezes this
      jacket to ~70–80 % of its area [calc, FF and RP separately]. The window on
      1.7 mm silicone is modelled at roughly 2.0–2.2 mm tall by 1.8–1.9 mm wide,
      with ~0.1–0.3 mm of room under JST's 2.4 mm envelope.
    - So insulation height is a position: [FF f6](explorers/force-and-form/ideas/f6-two-blades-two-drives.md) gives it its own drive and
      load cell; [HT a5](explorers/hand-tool-as-press/ideas/a5-two-squeeze-plier.md) squeezes it separately.
    - Strain relief goes elsewhere: [RP a3](explorers/ribbon-as-pallet/ideas/a3-backshell-that-ships.md)'s printed backshell folds the
      ribbon 180° round a bar, and a 3 N cover resists 14–69 N of loom pull.
    - Bent over a 2 mm pin with the tail away from the wing tips, a cut jacket
      gapes 0.23–0.56 mm [calc]. Five SN-2549 crimps bent this way show where
      today's insulation crimp lands.
11. **What the finished loom keeps: split length and the fan.**
    - How long a split behind the housing is acceptable is Derek's call, and
      every pitch strategy answers it differently [calc and estimate, each
      file]:

      | Split behind the housing | Where it comes from | Arrangements |
      |---|---|---|
      | none to 25 mm | one conductor lifted 3.5 mm over a fin | FF f10, PM p1d, PM p5c |
      | 12–20 mm for the split jaws; 6–12 mm (4P) to 15–26 mm (J1) for row B's push | half-rows at 3.4 mm | CQ c1, CQ c1c |
      | 8–15 mm | crimped conductors folded back | BM b1, BM b8 |
      | 9–26 mm | strip over a crown | TS a2d, TS x2 (plus a 6–10 mm set step), BM b8b (~16–20 mm) |
      | 12–20 mm | half-row cassettes and planes | FF f4, FF f5b, FF f9 |
      | 12–20 mm | a hinged pallet taking each crimp at 2.5 mm | FF f2c |
      | 9–18 mm (4P, 5P), 23–36 mm (J1); 23–30 mm in RP a1c | 5 mm crimp pitch | RP a1c, IH i3, IH k6 |
      | 21–33 mm | strip pitch, or a reel dock with equal paths | RP a2, RP a2e, RP a10, RP a10b, FF f9b, RP a9, PM p6b |
      | 25–30 mm during the build | a sort for J4 and J7 | IH i6, IH k8 |
      | 25–35 mm | waiting conductors pressed down, or a hand tool beside the row | PM p1, PM p5, HT a2, HT a2b, HT a4b, HT a4c, SL v8 |
      | 30–35 mm | hand tool on its side, or ribbon on edge | PM p1c, PM p5b, PM p2, PM p3, PM p6, HT a3 |
      | 30–47 mm | a lay-in tongue per conductor | RP a1, RP a1b |

    - Cutting after a wide fan leaves the outer conductors long: a 5P fanned to
      7.1 mm keeps 2.46 mm of excess, a 3–5 mm arc [calc, RP]. An equal-path fan
      (a hump in each inner groove) keeps every tip on one line, and cutting the
      strip line while the ribbon is flat puts every contact the same distance
      along its conductor [calc, RP and BM].
    - [RP a5](explorers/ribbon-as-pallet/ideas/a5-part-fan-strip-in-the-pallet.md) sets out the three consistent preparation orders.
12. **Buckling, and where an insertion push comes from.**
    - A free conductor buckles at ~6 N over 5 mm and ~40 N over 2 mm [calc], so
      a push comes from within ~2 mm of the insulation barrel, from a blade
      behind the barrel, or by moving the housing onto a held row.
    - Insertion and retention forces are not public [mfr]. KONNRA's clone
      specification gives ≤9.8 N insertion and ≥19.6 N retention [source].
      Sogang's printed inserter succeeded 98 % at insertion, with most failures
      in transferring the floppy cable [source].
    - The feed-length rule: inserting contacts one at a time stores each 6–9 mm
      insertion stroke as length in its own conductor, a hump; a single push
      after every crimp stores nothing [IH, FF]. Two half-rows merged at 2.5 mm
      interleave exactly, so one housing move inserts both.
    - A summed force hides one unlatched contact. Per-contact checks: a 5 N
      pull-back, the lit cavity square going dark, a wired post bed, or clamps
      staggered on constant-force springs so one push shows a step per contact.
13. **The proof pull: a force ladder, and where the reaction goes.**
    - A ≤5 N latch tug < a latched contact's retention (14.7 N on a Molex
      analog; ≥19.6 N in the clone specification) < a ~20 N proof pull < JST's
      39.2 N pull-out minimum at 22 AWG [mfr] < the 85–100 N conductor break. So
      the proof pull comes before insertion.
    - Never in a hand tool: a few newtons at the grip is 30–200 N at the dies
      [calc, HT and SL].
    - On the contact: a backed plate on the box's rear walls with the lance
      relieved, a neck blade or fork, a stepped plate, or the strip tab with a
      pad on the barrels.
    - On the wire: strands slip at 0.5–6.3 N per mm of grip, so a clamp reacting
      20 N squeezes 15–30 % over 5–20 mm to a hard stop, or the whole reel
      anchors it [calc, FF and PM].
    - Open: [FF f8](explorers/force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md) has no pull before insertion; on loose kit contacts a
      per-crimp pull depends on the neck, or falls back to sampling.
14. **What sensing can and cannot see.**
    - Force monitoring sees gross faults: a missing conductor, insulation in the
      conductor barrel, a missing, high or rolled contact. One strand of 60 is
      ~1.7 % of force against a ±4 % band [calc], so a cut strand does not show.
    - The strand guard is a picture taken before the barrel closes: a backlit
      tip silhouette; one frame of a whole-end strip; or a look straight down
      into an open conductor barrel with LEDs at 60–75°, where a hovering bundle
      throws a shadow and a strand on the floor casts none ([SL v8](explorers/machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md); untested
      on tin).
    - Identity through the far end: with the far end in a terminal block, a pogo
      block or through the reel, a grounded die, blade or stop names the
      conductor before any force. HT, RP and PM reached this separately.
    - Where the limits live [calc]:
      - on the station microcontroller, because through a hand tool's gain a
        0.5 s stall of the Mac is 108–857 N extra at the dies;
      - in a steel force ceiling in series with every drive, its switch in the
        drivers' enable line ([SL v7](explorers/machine-that-sees-and-learns/ideas/v7-the-run.md));
      - a stalled 1,500–2,000 N actuator on a hand tool's handle is 12–40 kN at
        the dies, so a spring link preloaded to ~1.25× the needed force caps it
        near 3.2 kN ([BM b2](explorers/borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md));
      - near bottom dead centre a crank pushes an obstruction through at
        8–10 kN on a stiff frame; a disc stack in the rod keeps every case under
        5.4 kN ([BM b1b](explorers/borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)).
15. **J4 and J7 cross only because of two pin orders.**
    - Eight of ten housings take their ribbons in ribbon order. J4 and J7 cross
      between the two ribbons of a pair [repo: `hardware/pcb/pcba/pcba.tsx`], at
      least five crossing contacts a unit. IH, PM and CQ found this separately.
    - Changes that remove them ([CQ c7](explorers/change-the-question/ideas/c7-straight-across.md)): swap J4's pins 2 and 5 and move J7's
      GND to pin 5 (a board revision); wire J4 by pin block and put J7's GND on
      the 3P (no board change); one housing per ribbon (~9–11 mm more board
      edge); or wider ribbon (6P is on Prime, $62.98 per 100 ft [Prime],
      enough for J2; 7P and 9P were not found).
    - Machines that make them treat a crossing as an order of placement: wait
      high, place low, lower layers first. Routes: a loft, a sort, a gantry
      hand, bow-and-push, a humped feed, crossing conductors laid last.
    - One end type dominates: 4P into XHP-4 (J3, J5, J9, J11, J13) is 5 of 10
      housings and 38 % of crimps, with no pair, skip or crossing. It is the
      scope of the spool-fed single-type machines ([CQ c5](explorers/change-the-question/ideas/c5-ends-as-stock.md), [FF f2c](explorers/force-and-form/ideas/f2c-applicator-station-makes-t4-ends.md), [BM b8](explorers/borrowed-machines/ideas/b8-spool-fed-borrowed-line.md),
      [BM b8b](explorers/borrowed-machines/ideas/b8b-flat-spool-line-over-a-crown.md)).
16. **A bad crimp costs a whole ribbon end: terminate first, cut last.**
    - No single-conductor re-crimp exists; a bad crimp cuts the whole end back
      ~6 mm. With cut-first orders and a 12 mm length allowance per loom (two
      redos), 0.4 (at 2 % bad) to ~35 (at 10 %) looms are scrapped over the
      program; with no allowance, 65 to 288 [calc, PM]. The rate on this
      silicone is unknown.
    - Making the XH end on the spool's free end, before the cut that frees the
      loom, makes a redo cost reel, never a loom. The rest of the spool is the
      test lead, through a slip ring ($9.99 [Prime]) or a hub socket, and the
      whole reel anchors the pull. RP, PM and CQ reached this separately.
    - It costs reaching the spool's inner end (or a rewind), pairs that wait
      half-housed, larger machines, and batching by ribbon type. It works by
      hand too: [PM p6](explorers/procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md) at stage 0 is ~51 attended minutes against ~46 today
      [estimate].
17. **Person time is loading, not crimping.**
    - Where estimated, the person's time is cutting, peeling, laying ribbon ends
      into fixtures and inserting. Machine time, from ~20 min to ~6.6 h a unit,
      is small against a week of printing; what matters is how often the machine
      calls the person back.
    - Two baselines count different things [estimate]: ~46 attended minutes a
      unit for the whole XH procedure on PM's task library (the ledger gives
      45 min for every harness [repo]); ~22 min for strip-and-crimp alone (HT).
      Compare stages within one arrangement, not figures across explorers.
    - Person-paced stations buy consistency, checks and a log, not minutes.
      Minutes fall when splitting, stripping and insertion leave the person:
      cut-loom machines reach ~19–44 min a unit, the reel orders ~12–24 (PM
      p3, p3b, p6 from stage 4, p6b; RP a9), and BM b8 ~33 with non-T4 looms by
      hand [estimate, each file's own library].
    - [SL v7](explorers/machine-that-sees-and-learns/ideas/v7-the-run.md) estimates 5–11 asks a unit at first and 1–2 later.
18. **Contact supply splits the arrangements.**
    - Of ~85 contact-handling arrangements, about half need strip, a fifth need
      loose contacts and a third take either; pre-formed contacts are a fourth
      supply [estimate, [TS a7](explorers/terminal-supply/ideas/a7-if-the-contacts-switch-to-strip.md)].
    - Genuine SXH-001T-P0.6 is plentiful at distributors, and the ~3,200 crimps
      of the program are under half of one 8,000 reel; a 100-piece strip covers
      ~1.9 units. No XH contact on strip is on Prime.
    - The kit contacts on hand are of unknown origin; a tab stub at the rear of
      the insulation barrel would show they came off a reel.
    - Bowl and screw feeders do not orient an XH contact [estimate]
      ([borrowed-machines](explorers/borrowed-machines/summary.md)). Every automatic
      loose path rests on a lance-grooved pocket, a hanging rail, a post pick, a
      camera-checked plate or a person.

## Starting points on today's bench

These are the arrangements whose first form needs no motor, or only tools
already on the bench: the SN-2549, the Klein 11063W, the caliper, the ELP camera,
the 0.1 g scale, the idle 12-ton shop press, the WEN drill press, the NEMA 23
with its DM542T (which sits in the cap-weld tube rotator), and the two H2C
printers for fixtures. None of these first forms uses an H2C as a stage. Person
minutes are each explorer's own [estimate]; compare stages within one
arrangement. Several say in their own numbers that they buy a stop for every
placement, a check and a record, not minutes. None of these has a Prime
listing: an OTP applicator, a knife set, XH contacts on strip or reel, an SN jaw
set alone, the WC-110.

**Frames that hold the whole end**
- **[PM p6](explorers/procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md), stage 0: the spool-end bench.** Reels with hub sockets behind the
  bench, a clamp whose face guides the flush cutters, a test board of real XH
  headers on an ESP32, a length rail. Each end is made by hand on the reel,
  tested pin to pin, drawn to its peg and cut. ~$25–45 [estimate]. Grows stage by
  stage into a powered crimp, steppers and posts, strip, puller and guillotine,
  and split ([PM p3](explorers/procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md)); branch [PM p6b](explorers/procedure-is-the-machine/ideas/p6b-reel-end-docks-on-a-strip.md).
- **[PM p1](explorers/procedure-is-the-machine/ideas/p1-cassette-and-benches.md), stage 1: the cassette alone.** Key *k* = cavity *k*, a blank for
  J2's cavity 3, a loft for the crossings, the far end in a pogo block (P75-E2
  pins, $6.49 per 100 [Prime]); the person crimps with the SN-2549 one key at a
  time. Grows into the squeezer, bench B's three forms, the carousel and the
  camshafts.
- **[HT a6](explorers/hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md): the foot-closed jig bench.** Feeler leaves, 1095 shim, Dyneema
  cord, springs, Wago 221s, a light pad and pin gauges, all Prime, plus a header
  PCB. Every jig carries the interface a later motor takes: the cord to a winch
  or a NEMA 17 ([HT a1](explorers/hand-tool-as-press/ideas/a1-squeezer-cradle.md), [HT a1b](explorers/hand-tool-as-press/ideas/a1b-pawl-out.md)), the end jig to [HT a2c](explorers/hand-tool-as-press/ideas/a2c-one-baseplate-strip-crimp-insert.md), the nest to a
  servo lever.
- **[BM b2b](explorers/borrowed-machines/ideas/b2b-pedal-less-hand-station.md)'s first stage** (one actuator, so not motorless): a second SN-2549
  ($22.29 [Prime]) on edge, a Justech 1,500 N actuator ($29.99 [Prime]) through a
  spring link, the far end in a pogo block, contacts set with [TS x1](explorers/terminal-supply/ideas/x1-post-feeds-the-hand-tool.md)'s post pen.
  Each of its five stages is a working bench tool.
- **[SL v7](explorers/machine-that-sees-and-learns/ideas/v7-the-run.md)'s ladder.** Rung 0 is [SL v5](explorers/machine-that-sees-and-learns/ideas/v5-inspection-booth.md)'s booth on Derek's hand crimps;
  rung 0.5 logs a6's foot bench, or [SL v9b](explorers/machine-that-sees-and-learns/ideas/v9b-tack-by-hand-on-the-jack-test.md) on the applicator route; then the
  tack station, the heavy crimp and the rest.
- **[RP a9](explorers/ribbon-as-pallet/ideas/a9-reel-end-docks.md), stage 0.** p6's reel clamp on a hand-slid plate with detents at
  strip pitch; p7's lever, a7's hand comb, an equal-path fan on a lever, a strip
  segment docked by lever. The crimp is [RP a10b](explorers/ribbon-as-pallet/ideas/a10b-tacked-row-into-the-hand-tool.md)'s tack and shear, then the
  SN-2549, until an applicator arrives.

**Splitting and stripping**
- [BM b6](explorers/borrowed-machines/ideas/b6-pierce-at-the-root-pull-to-the-tip.md)'s hand rip board: a hinged bar of needles at 1.7 mm pierces every
  web at the root, and pulling the clamp back tears them to the strip line, about
  25 s an end. Music wire ($7.24 [Prime]) or cut sewing needles, and a JLCPCB
  stencil needle plate.
- [RP a7](explorers/ribbon-as-pallet/ideas/a7-zip-station.md)'s hand zip comb (blunt laminated tines diverging 1.7 to 2.5 mm) and
  [RP a7b](explorers/ribbon-as-pallet/ideas/a7b-plough-station.md)'s plough, each slid by hand.
- [PM p7](explorers/procedure-is-the-machine/ideas/p7-strip-before-split.md)'s lever: two single-edge razors ($12.90 per 100 [Prime]) on a hinged
  jaw close to shim stops across the whole webbed end, and one pull takes the
  slug. Useful the day it is printed.
- [RP a8](explorers/ribbon-as-pallet/ideas/a8-rolling-ring-scorer.md)'s bench block and [RP a8b](explorers/ribbon-as-pallet/ideas/a8b-spindle-with-touch-off.md)'s knob-turned spindle; [BM b7](explorers/borrowed-machines/ideas/b7-borrowed-strip-head-one-conductor.md)'s
  die-hole blades in a hand lever with a printed sleeve as a wired tip stop; the
  Klein with a clipped-on length stop at [HT a6](explorers/hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md)'s end jig.

**Getting contacts oriented**
- [SL v4b](explorers/machine-that-sees-and-learns/ideas/v4b-pocket-plate.md)'s pocket plate brushed full by hand while a print runs, picked with
  curved tweezers ($12.76 [Prime]) beside the SN-2549.
- [RP a2c](explorers/ribbon-as-pallet/ideas/a2c-loose-contact-cassette.md)'s keyed nest bar, loaded by tweezers.
- [CQ c6](explorers/change-the-question/ideas/c6-pre-form-the-contact.md)'s lever pre-former, the first station of [CQ c6b](explorers/change-the-question/ideas/c6b-by-hand-this-week.md).

**Placing the contact and holding both for the crimp**
- *A locator for the SN-2549:* [TS x1](explorers/terminal-supply/ideas/x1-post-feeds-the-hand-tool.md)'s post pen (a header pin in a printed
  pen, a fence on the jaw screw); [IH i2d](explorers/into-the-housing/ideas/i2d-locator-the-lance-never-touches.md)'s housing stub cut from a kit XHP-2
  on a flexure; [TS a2c](explorers/terminal-supply/ideas/a2c-strip-locator-for-hand-tool.md)'s strip clip (a $4.71 strip, a 1.448 mm pin gauge as
  the pilot); [HT a1](explorers/hand-tool-as-press/ideas/a1-squeezer-cradle.md)'s insulated blade in the neck, reading amber and green
  through the far end; [FF f1](explorers/force-and-form/ideas/f1-motorised-ratchet-crimper.md)'s cradle and flap with a hand on the handles;
  [FF f1b](explorers/force-and-form/ideas/f1b-wc110-in-the-cradle.md)'s WC-110 by hand.
- *The contact on the wire before the tool:* [CQ c6b](explorers/change-the-question/ideas/c6b-by-hand-this-week.md) (pre-former, snap block,
  flag seat with a lamp; POWERTEC toggles $18.25 [Prime], HSS blanks $9.99
  [Prime]); [HT a6b](explorers/hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md) (a second SN-2549 as the click pre-former); [SL v8](explorers/machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md) by
  hand (a toggle-driven former and a straight-down look, then the SN-2549);
  [CQ c1b](explorers/change-the-question/ideas/c1b-tack-first.md) (a tack comb on a lever over a half-row); [FF f9](explorers/force-and-form/ideas/f9-tack-station-feeds-crimp-station.md) with a person at
  station C; [FF f3b](explorers/force-and-form/ideas/f3b-two-station-forming.md)'s curl on a hand lever.
- *Every contact of an end at once:* [RP a2d](explorers/ribbon-as-pallet/ideas/a2d-by-hand.md) (dock, photograph and meter
  before any crimp tool exists); [RP a10b](explorers/ribbon-as-pallet/ideas/a10b-tacked-row-into-the-hand-tool.md) (two toggle levers dock, tack and
  shear; then the SN-2549); [FF f9b](explorers/force-and-form/ideas/f9b-tack-on-the-strip.md) by hand, with a box-keyed clip on the jaw
  or a die cartridge in the AP-1.

**The crimp stroke**
- *Today's hand tools, hands freed or stroke split:* [HT a6](explorers/hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md)'s treadle (up to
  ~120 N at the toe); [HT a5](explorers/hand-tool-as-press/ideas/a5-two-squeeze-plier.md)'s PA-09 ($38.99 [Prime]) with two printed stops.
- *Steel dies closed by a hand lever or a press already owned:* [HT a4](explorers/hand-tool-as-press/ideas/a4-dies-in-a-die-set.md) (SN jaws
  from icrimptools.com at $4.99–9.99, or inside the IWS-0723K set, $46.59
  [Prime]; a 500 kg button cell, $74.99 [Prime], thin, and the DITR-0105,
  $52.99 [Prime]); [FF f3](explorers/force-and-form/ideas/f3-knee-micropress.md)
  (~$150–350 in all [estimate]); [FF f7](explorers/force-and-form/ideas/f7-where-the-steel-comes-from.md)'s cartridges in the AP-1 ($61.90
  [Prime]); [FF f10](explorers/force-and-form/ideas/f10-lift-once-fin-from-below.md) by levers; [FF f5](explorers/force-and-form/ideas/f5-die-cassette-and-the-shop-press.md) and [FF f5b](explorers/force-and-form/ideas/f5b-half-row-cassette.md) in the shop press or
  the AP-1; [RP a2b](explorers/ribbon-as-pallet/ideas/a2b-gang-press-stop-die.md) in the shop press (an air-over-hydraulic BIG RED jack,
  $136.04 [Prime], might pump it; its fit is not stated).
- *A bought applicator:* [BM b1b](explorers/borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)'s jack test, which is also the measuring bench
  for every applicator arrangement (stroke, shut height, feed timing, which
  contact the die is cut for, two supplies through one die); [SL v9b](explorers/machine-that-sees-and-learns/ideas/v9b-tack-by-hand-on-the-jack-test.md)'s hand
  tack on it; [FF f2](explorers/force-and-form/ideas/f2-crank-press-for-an-applicator.md) with a handwheel (pillow blocks $26.99 [Prime]);
  [FF f2b](explorers/force-and-form/ideas/f2b-arbor-press-with-a-hard-stop.md) in a VEVOR AP-3 ($255.90 [Prime]); [BM b8b](explorers/borrowed-machines/ideas/b8b-flat-spool-line-over-a-crown.md)'s knife set on a crown
  under the AP-1; [RP a1b](explorers/ribbon-as-pallet/ideas/a1b-hand-shuttle.md)'s hand shuttle.
- *Not a crimp, or not made here:* [CQ c3](explorers/change-the-question/ideas/c3-fold-and-solder.md)'s fold and solder with the Hakko
  already on the bench; [CQ c2](explorers/change-the-question/ideas/c2-buy-the-crimp.md)'s bought leads, whose lasting use is the JST
  lead as the reference crimp.

**Checking, insertion and the finished end**
- [SL v5](explorers/machine-that-sees-and-learns/ideas/v5-inspection-booth.md)'s booth (a razor back as blade, a light pad $16.99, a first-surface
  mirror $20.90, a gauge pin, all [Prime]), which works first on Derek's own
  crimps; [IH i5](explorers/into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md)'s fork and pocket; [HT a6](explorers/hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md)'s pull-and-look jig; [SL v3](explorers/machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md) on
  the jack test with a shimmed stop.
- [IH i5](explorers/into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md)'s sensing nest (bar cells with HX711 $9.99, AS5600 $7.99, both
  [Prime]; headers from Newark or Digi-Key); [RP a6](explorers/ribbon-as-pallet/ideas/a6-housing-as-last-comb.md)'s closing block and wafer
  test; [CQ c7](explorers/change-the-question/ideas/c7-straight-across.md) (not a build); [RP a3](explorers/ribbon-as-pallet/ideas/a3-backshell-that-ships.md)'s backshell.

### Measurements that settle many unknowns

Most take minutes with the caliper, the ELP camera, the 0.1 g scale and a
luggage scale.

1. **The SN-2549, characterised once.** Held closed against a light: do the jaws
   meet face to face? Handle force and travel at ratchet release. The depth *a*
   of the anvil jaw half behind the XH nest. How wide the nest opens (a flag
   needs 3.5–4.9 mm). Closed one click at a time on an empty contact, looked at
   end-on: where the insulation-first window and the first tooth fall. The anvil
   from the side: plain block or lance relief. Clamped closed by one handle with
   a known weight hung from the other grip: how far the grip moves (handle
   stiffness). One crimp with the tool held tip-down over a flat row, jaws
   closing along the row, photographed end-on: the 90° roll. These decide every
   powered SN route, the flag seats, the stub locator and the lift heights.
2. **Kit contacts under the camera and caliper.** Side-on beside a rule: the
   neck, lance root and barrel length. End-on: the insulation floor width. Three
   open-wing widths. One contact barrels-up on a card: does it rock on its lance?
   The same contact barrels-up on the 0.1 g scale with a probe on the box top:
   the lance's force at 0.1, 0.3 and 0.6 mm of travel, and whether it springs
   back. The overall length of five contacts from one bag. A tab stub at the
   rear? Twenty on a light pad for spread and pose odds.
3. **Five SN-2549 crimps on the ribbon**, calipered, pulled with a hook and
   scale, and bent over a 2 mm pin with the tail away from the wing tips: what
   today's tool makes, and whether today's looms already carry cut jackets. Then
   five with the box nose touching a feeler leaf across the front of the nest
   and five with the nose free, photographed side-on: does the transition bow
   under barrel growth?
4. **The web.** Peel a metre each of 3P and 5P, and look at a fresh cut face:
   neck thickness, valley depth, strand offset. Caliper the jacket OD of five
   split conductors along the spool.
5. **The housing.** One kit contact into one kit housing on the 0.1 g scale:
   push at the click, the tug that pulls it out, where its rear sits. A header pin
   in a kit contact with weights hung until it slides off, and the pin's section
   calipered: are the header pins really 0.64 mm square? An XHP-4 against a
   torch with a long pin pushed through from the front.
6. **Two-minute strip tests.** Two razors on shims across a fresh 5P end, the
   slug pushed off with and without toothed pads; a razor on a 1.45 mm drill
   blank rolled one turn across a conductor and pulled.
7. **The tack, the pre-form and the shadow.** Three contacts closed loosely on
   conductors with smooth-jaw pliers, pulled and twisted, crimped, pulled again.
   A kit contact's wings squeezed round a ~1.55 mm pin and a conductor pressed
   in. A stripped conductor in an open contact photographed from above under one
   LED at ~65°, before and after pushing one strand to the floor.
8. **A 20 N pull through the box on a conductor held in a TPU clamp**: does the
   copper creep inside the jacket?
9. **Copper set.** Offset one split conductor 12 mm sideways for a minute, let
   go, and measure the kink.
10. **The spool**: hub diameter, whether the inner end is reachable, curl near
    the hub. **The shop press**: a gauge, and flat bed plates. **The loom
    order**: is each far end free and stripped while its board end is made?

**Purchases that settle more:** one 100-piece SXH-001T-P0.6 strip (Digi-Key,
$4.71: carrier pitch, pilot hole, tab length, genuine wings, barrel and neck);
five JST ASXHSXH22K305 leads (~$4.50: the reference crimp; count and caliper
the lead's strands for the copper correction); a second SN-2549
($22.29 [Prime]); one OTP applicator and a reel ($150–250 plus shipping, eBay or
Alibaba) for the jack test; the Accusize pin gauge set ($45.58 [Prime]) and the
DITR-0105 indicator ($52.99 [Prime]). Not a purchase: JST's XH handling manual
(CHM-1-151), requested through JST's licence form, carries the genuine crimp
height.

## Sourcing in brief

- **Genuine contacts and housings are plentiful at distributors.** Digi-Key has
  ~1.33 million SXH-001T-P0.6 on reels and 100-piece strips at $4.71; Newark,
  TME, Heilind and LCSC stock it too, and clone reels at LCSC start at $0.0073 a
  contact [source]. XHP-4 to XHP-7 sit in the tens to hundreds of thousands;
  XHP-9 is thinner (3,408 at Digi-Key). The program is under half of one 8,000
  reel.
- **On Prime, delivered in one to five days:** the SN-2549 (532 ratings), the
  Engineer PA-09 (1,719 ratings), the CQRobot kits, VEVOR arbor presses (the 1 t
  at 300+ a month; the 3 t models thin), steppers, gearboxes, servos, load cells,
  rails, cameras, light pads, pin gauges and 1095 shim. No XH contact on strip is
  on Prime.
- **Quick-turn services:** JLCPCB stainless stencils from $3 in about a day;
  SendCutSend laser-cut steel in 2–4 days; JLCPCB boards for post beds and header
  nests.
- **Only with shipping time or quotes:** the OTP applicator (eBay $150–167 plus
  $80–91 shipping, Alibaba $200–250, Sanao $125–150); its knife set (price not
  read); applicator presses from $310 to $2,950, and JST's AP-K2N at $12,500
  with a 116-day lead; wire EDM, ~$50–200 a part in 1–3 weeks [estimate]; JST's
  WC-110 at $536.51 (147 at Digi-Key), and JST applicators at $3,439–4,599 with
  none in stock.
- **Not found anywhere:** an IDC housing that mates the XH wafer; a
  point-and-blade crimp-height micrometer; a ribbon splitter near 1.7 mm pitch;
  22 AWG silicone ribbon in 7, 9 or 10 conductors; a hardened 0.64 mm square pin;
  thin ground tool steel and small hardened dowels, for which a McMaster-class
  supplier is assumed [assumption].
- **Not public:** JST's crimp height for SXH-001T-P0.6, the SXH carrier pitch and
  XHP insertion and retention forces sit behind JST's licence form [mfr].
- The full picture, by function, is in the [parts overview](sourcing/README.md),
  and every Prime listing with its delivery and volume signals is in
  [`sourcing/amazon-prime.md`](sourcing/amazon-prime.md).

## Questions for Derek

Choices only Derek can make. The bench looks and purchases that settle the rest
are listed under [starting points](#measurements-that-settle-many-unknowns); until
answers come, each arrangement carries the range its file states.

**The contacts and the crimp**
- Which contact do the machines run on: the kit contacts, genuine SXH on strip or
  reel, a clone reel, loose BXH, or pre-formed kit contacts? Are kit contacts kept
  for hand repair either way? Would removing every other contact from a strip be
  acceptable if it lets the ribbon lie flat ([TS a2d](explorers/terminal-supply/ideas/a2d-skip-pitch-crown.md), [TS x2](explorers/terminal-supply/ideas/x2-crown-then-sort.md), [BM b8b](explorers/borrowed-machines/ideas/b8b-flat-spool-line-over-a-crown.md))?
  [TS a7](explorers/terminal-supply/ideas/a7-if-the-contacts-switch-to-strip.md) maps what each choice opens and closes.
- What does a machine's crimp aim at: today's SN-2549 crimp, or JST's profile
  judged by the reference lead at the machine's own channel width? Does every
  production crimp get a proof pull and a bend-and-look, or a sample per end?
- Is a soldered, non-crimp XH joint acceptable in principle ([CQ c3](explorers/change-the-question/ideas/c3-fold-and-solder.md), [FF f3b](explorers/force-and-form/ideas/f3b-two-station-forming.md))?
- Made or harvested steel (a knife set, a traced profile sent for EDM, laser-cut
  plate, a fin of ground stock), or does every crimp head stay a bought hand tool?
  Would you request JST's handling manual through the licence form?

**The loom and the board**
- How long a split behind the housing is acceptable on a finished loom (the table
  under finding 11)? Is ~2 mm of slack stored behind a housing acceptable
  ([HT a2d](explorers/hand-tool-as-press/ideas/a2d-batch-then-gang-push.md), [HT a3](explorers/hand-tool-as-press/ideas/a3-tool-travels-to-ribbon.md))?
- Would J7's GND move onto the 3P with CLO and CHI, the 5P's fifth conductor
  trimmed? Which of J7's 3P conductors is the trimmed "third"?
- How is J4 made: in the least-crossing order into-the-housing proposes
  recording in
  [`cable-assemblies.md`](../../hardware/assembly/cable-assemblies.md) (V5,
  IO25, 3V3, IO26 | GND, IO27, IO23), by pin block, or with its three crossing
  contacts a unit left to a hand insertion?
- Is a board revision of J4's and J7's pin orders on the table, or ~9–11 mm more
  board edge for one housing per ribbon? BNTECHGO 6P is on Prime ($62.98 per
  100 ft [Prime]), which would make J2 one ribbon. Would you use it, and would
  you use 7P or 9P if one turned up ([CQ c7](explorers/change-the-question/ideas/c7-straight-across.md))?
- Stock ends or one unit at a time? Would you hold XH-ended ribbon or looms ahead
  of units, make each end on the reel before the cut (a rewind per spool, a bad
  crimp costing ~6 mm of reel at a single-conductor station, ~22–35 mm where
  the end is docked), and start with a machine that makes only 4P into
  XHP-4? How much shorter than its cut length may a loom end up, and what is J3's
  length ([CQ c5](explorers/change-the-question/ideas/c5-ends-as-stock.md), [PM p3](explorers/procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md), [PM p6](explorers/procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md), [RP a9](explorers/ribbon-as-pallet/ideas/a9-reel-end-docks.md))?
- Would a printed backshell with an IDC-style fold on every loom be welcome as
  strain relief and label ([RP a3](explorers/ribbon-as-pallet/ideas/a3-backshell-that-ships.md))? Is a quarter to half turn of twist in a
  stripped stub acceptable ([RP a8b](explorers/ribbon-as-pallet/ideas/a8b-spindle-with-touch-off.md))? Is one extra mating cycle per contact
  acceptable ([IH i5](explorers/into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md), [IH i6b](explorers/into-the-housing/ideas/i6b-post-bed-through-the-housing.md), [TS a4c](explorers/terminal-supply/ideas/a4c-post-bed-one-push.md))?

**Working with a machine**
- Person-paced or unattended? Is a station where you poke each conductor in and
  seat each crimp at a lit cavity, never holding a contact, an end state you would
  use, or is running unattended while the printers run the goal?
- Would a foot treadle under the bench suit how you sit or stand there
  ([HT a6](explorers/hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md), [HT a6b](explorers/hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md), [HT a6c](explorers/hand-tool-as-press/ideas/a6c-flags-by-machine-foot-crimp.md))? Would a hand rip board be welcome in place of
  peeling ([BM b6](explorers/borrowed-machines/ideas/b6-pierce-at-the-root-pull-to-the-tip.md))?
- Guards and lasers: an interlocked guard over the crimper faces on anything built
  round the shop press or a relay-fired press? A Class 4 diode laser station on
  the bench in a light-tight box ([BM b4b](explorers/borrowed-machines/ideas/b4b-diode-heads-at-the-station.md)), or lasers only inside the H2C
  enclosure ([BM b4](explorers/borrowed-machines/ideas/b4-laser-slits-and-scores.md))?
- Which control stack feels like home: your own PlatformIO firmware beside a
  printer as bought, FluidNC, or Klipper? A Mac left awake for a run, or its own
  small computer? Its own NEMA 23 and DM542T, or the weld rotator's?
- How much may Claude decide: pass a borderline crimp on its own, logged and later
  checked, or only propose? Do asks come as a push to your phone with a photo,
  through a Claude session you follow, or only at the bench ([SL v7](explorers/machine-that-sees-and-learns/ideas/v7-the-run.md))?

## Blind spots

Where the study could not picture a workable variant, and what it covered
thinly.

- **Crimping in the row at 2.5 mm beside open neighbours.** Every arrangement
  lifts, stands out, fans, splits, folds back or narrows the neighbours first;
  beside two crimped neighbours a narrow crimper takes only pre-formed or
  narrow-winged contacts. An SN-2549 kept as bought crimps upright from a flat
  row only with 8.7–14.7 mm of lift.
- **J4, J7 and the two-ribbon housings in automated insertion.** Most
  arrangements hand the crossings back; the routes that place them are
  undemonstrated on silicone or need a 25–39 mm split during the build. Two
  ribbons into one housing from spools appears only in [PM p3b](explorers/procedure-is-the-machine/ideas/p3b-ribbon-ams-whole-unit.md)'s merging
  lanes. [CQ c7](explorers/change-the-question/ideas/c7-straight-across.md) removes the crossings by a choice, not a mechanism.
- **Short splits with docking.** Every docking arrangement needs 21–33 mm.
- **Loose kit contacts without a person, rail, post, plate or camera.** Putting
  kit contacts back onto a carrier tape is undeveloped.
- **A proof pull on a loose contact with a short neck**, and on [FF f8](explorers/force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md)'s crimp
  in the cavity. Below a ~0.34 mm neck, the fins, nests and neck blades have no
  worked variant.
- **Handling a crimped contact for insertion.** Post, housing and post bed all
  want the box front; the barrel grips in [IH i1](explorers/into-the-housing/ideas/i1-lift-to-the-head.md), [IH i4](explorers/into-the-housing/ideas/i4-gantry-hand-with-eyes.md), [IH i6](explorers/into-the-housing/ideas/i6-sort-then-push.md) and
  [IH k8](explorers/into-the-housing/ideas/k8-half-rows-crimped-then-sorted.md) are drawn, not designed.
- **Rework.** No single conductor can be re-crimped; extracting a seated contact
  after a failed latch is not developed.
- **Seeing inside a closed crimp.** Voids and strand distribution need sections;
  applicator lines have no cheap in-line height gauge; the shadow test on tin is
  unverified.
- **The insulation crimp as its own setting** exists only in [FF f6](explorers/force-and-form/ideas/f6-two-blades-two-drives.md), on a
  modelled window.
- **Steel with a known profile, quickly.** JST's profile is licence-gated; knife
  set and EDM profiles and prices are unobserved.
- **Person time for cut looms.** With the crimp automated, cutting, peeling,
  laying ends into fixtures and inserting remain most of the person's time. The
  lowest estimates, ~12–24 min a unit, come from the reel orders (BM b8's T4
  line ~33), which bring
  batching and half-housed pairs, and from [PM p1b](explorers/procedure-is-the-machine/ideas/p1b-carousel-joins-the-benches.md)'s carousel (~19), whose
  machine splitting is untested.
- **Covered thinly:** splitting and stripping (every module rests on the
  untested neck and tear, and no bought stripper is known to work on this
  jacket); loading ~14 ribbon ends a unit; the far ends (Fastons, ferrules into
  Wago lever nuts, 110 IDC, screw terminals), where the one worked route is a
  squeezer saddle per far-end hand tool, person-paced, which buys a record, not
  minutes (a second applicator for Fastons at [RP a4](explorers/ribbon-as-pallet/ideas/a4-spool-as-magazine.md)'s guillotine is named but
  not developed); cutting to length, labelling and
  housing supply; wear over ~3,200 crimps; jam recovery in a gang push; identity
  without a free far end; cheap guarding; equal-path fan blocks, which could not
  be judged without printing one.

Much of what stays open comes back to a few unmeasured things: the kit contact's
neck and wing width, whether the SN-2549's jaws bottom and how wide they open,
the web's neck and how this silicone tears, the strip's pitch, and the housing's
insertion forces.
