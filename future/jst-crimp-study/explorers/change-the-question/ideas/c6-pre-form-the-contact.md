# c6 — Pre-form every contact before it meets a wire: an insulation barrel the conductor snaps into

A new step in front of the five, done in bulk with no wire present.
Branch: [c6b](c6b-by-hand-this-week.md) (the same step by hand this week, with
a steel pre-former and the SN-2549). Combination: [c1c](c1c-crimp-in-the-row.md)
(half-rows crimped in the row). Other explorers' files built on it are listed
under "Hosts". Sketches: [`../sketches/c6-pre-form.svg`](../sketches/c6-pre-form.svg)
and [`../sketches/c6-shapes.svg`](../sketches/c6-shapes.svg) (both schematic;
the end views are drawn from the cited dimensions). Numbers:
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) [w2 §n],
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) [w3b §n], and
hand-tool-as-press's [`exchange_ctq_w3.out.txt`](../../hand-tool-as-press/calc/exchange_ctq_w3.out.txt) [htq §n];
the labels K1–K6 and H1–H7 are that explorer's reading of this one,
[`../../../exchange/hand-tool-as-press--on--change-the-question-w3.md`](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md).

## Picture it

**Where the contact starts.** One of three ways, each already developed by
another explorer up to the point where a contact sits in a known pose:
- **On strip.** An SXH strip indexes through the pre-former on its pilot
  holes (terminal-supply [a2](../../terminal-supply/ideas/a2-strip-indexer.md)'s
  track and pins).
- **Loose, oriented by a machine.** Kit contacts come off terminal-supply's
  [a3 hanging rail](../../terminal-supply/ideas/a3-hanging-rail.md), its
  [a6 post](../../terminal-supply/ideas/a6-post-is-the-gripper.md), or
  machine-that-sees-and-learns'
  [v4b pocket plate](../../machine-that-sees-and-learns/ideas/v4b-pocket-plate.md).
  Those orient by the wide open wings, so orientation comes **before** the
  pre-form.
- **Loose, by hand.** Derek drops each one into the pre-former's nest at a lit
  bench, away from any wire ([c6b](c6b-by-hand-this-week.md)).

**The pre-former.** A palm-sized steel station; the reference for "fixed" is
its nest block.
- **Nest.** A slot the shape of the box, with a relief so nothing touches the
  lance, and a stop for the box's front face. It can be ground steel, stacked
  laser-cut stencil steel, or a cut kit XHP housing used only as a box pocket
  (into-the-housing's [i2d](../../into-the-housing/ideas/i2d-locator-the-lance-never-touches.md)
  stub): the box fits at product tolerance and the lance never bears. The only
  force on the front stop is the friction of a 10–80 N forming load, so the
  conductor barrel's growth problem of a crimp never arises here.
- **Mandrel.** A hardened pin slides in along the contact's axis from behind
  until it lies in the open insulation barrel (on strip, above the tab, which
  joins the barrel floor at the rear). Two mandrel shapes give two pre-forms
  (below): a **round pin** gives a keyhole; a **flat blade** 1.5–1.6 mm wide and
  ~2.5 mm tall gives a tall keyhole with straight walls.
- **Jaws.** Two small steel side jaws, or one top jaw, curl the insulation
  wings around the mandrel and leave their tips a throat apart. They overbend
  ~2° for springback [w2 §3].
- **Release.** The jaws open, the mandrel withdraws rearward, and a plunger
  pushes the contact forward, box first, into a stick. A strip contact indexes
  on.

**What drives it and carries the force.** Bending two 0.2 mm wings takes
~1.5–12 N per wing at the plastic hinge and ~10–80 N at the jaws with friction
and overbend [w2 §3]. A metal-gear servo on a short lever, a cam, or a toggle
clamp by hand does it. The force closes through the jaws, the contact's floor
and the nest block; the mandrel sets the bore and the jaw profile sets the
throat, so there is no height precision to hold.

**The mandrel is chosen from the ribbon, not from its nominal pitch**
[w3b §3]. Caliper the jacket OD of a few split conductors (the ribbon is
1.7 ±0.1 mm per conductor [source S29]). The bore after springback should sit
0.08–0.12 mm under that OD, a 5–7 % squeeze:

| Jacket OD measured | Bore target | Mandrel that stays in the window over 0.02–0.05 mm springback | Go pin (must enter from behind) | No-go pin (must not) |
|---|---|---|---|---|
| 1.60 | 1.48–1.52 | 1.46–1.47 | 1.47 | 1.52–1.55 |
| 1.70 | 1.58–1.62 | 1.56–1.57 | 1.57 | 1.62–1.65 |
| 1.80 | 1.68–1.72 | 1.66–1.67 | 1.67 | 1.72–1.75 |

At the target bore the axial grip is ~0.1–3.5 N whatever the OD [w3b §3]. A
bore chosen from the nominal 1.70 would grip nothing on a 1.60 jacket
[htq §2].

**What comes out** [w2 §2; w3b §2; htq §3]:

| Pre-form | Outside width | Height at the insulation barrel | Made by |
|---|---|---|---|
| Open, as bought (clone drawings) | 2.46–3.25 | 2.75–3.2 | — |
| **Keyhole** (round mandrel) | 1.96–2.14 | metal to 1.28–1.66; the snapped jacket stands ~1.9 | this pre-former |
| **Tall keyhole** (blade mandrel) | ~1.9–2.05 | ~2.5–2.9 (tips turned in above the blade) | this pre-former |
| **Tool-made U** (the crimper's own stroke stopped early) | 1.82–2.05 | 2.3–3.0 | the crimp tool itself: hand-tool-as-press [a6b](../../hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md) |

The conductor barrel and box are unchanged in every case.

**Where the contacts go.** Into short printed **sticks** in loom order, one per
housing, nose to tail: 2.1 × 2.6 mm channels for keyholes, ~2.1–2.2 × 3.1–3.2 mm
for the two taller shapes [w3b §2], each with a lance groove; 23–61 mm long
[w2 §5]. J2's stick has a blank spacer at position 3, so the stick is the build
list (terminal-supply's loom-order magazine). On strip, the contacts stay on
the carrier.

**Placing the contact on the conductor: a snap.** At whatever station hosts
the next step, a pre-formed contact sits barrels-up in a pocket, box on a front
stop, the pocket's floor under both barrels and a relief under the lance. The
stripped conductor lies over it, located by a comb.
- A **presser** comes down on the jacket over the insulation barrel. The
  jacket squeezes through the throat into the bore: ~0.3–30 N depending on
  throat and silicone, a few newtons at central values [w2 §4]. The pocket
  floor under the insulation barrel takes it; the lance takes none.
- A **front tine** on the same presser lays the strands in the open conductor
  U. The copper keeps the shape it is pressed into.
- The force is across the wire, onto a supported contact, so nothing buckles.

**What holds them together afterward.**
- Against lifting off: the throat. Taking retention as half to all of the
  push-in [assumption], a 1.5 mm throat gives ~0.15–11 N, 1.4 mm ~0.25–20 N,
  1.3 mm ~0.35–30 N [w3b §4]. A humped conductor lifts with only 1–44 mN
  ([`on_into_the_housing_w3.out.txt`](../calc/on_into_the_housing_w3.out.txt) §2).
- Along the wire: the bore's squeeze, ~0.1–3.5 N at a bore set by the rule
  above. A flag has to resist its own weight (0.4 mN), a keyed slot's friction
  (0.1–0.5 N) or a post push-on (0.2–1.6 N) [w2 §4]. The low end does not
  resist a person pushing the jacket against a stop, which is why the crimp
  stations downstream signal "at the stop" rather than relying on feel
  ([c6b](c6b-by-hand-this-week.md)).
- Roll: by friction on the jacket, until something keyed to the box squares
  it.

**What locates what.**

| Pair | Located by | Reference for fixed |
|---|---|---|
| Contact in the pre-former | box in the nest slot, front face on its stop | nest block |
| Bore | mandrel diameter, plus springback | mandrel, chosen from the measured jacket |
| Throat or tip gap | jaw profile at closure | jaw stop |
| Conductor over the contact at the snap | comb slot at the insulation; the keyhole's rounded top is the lead-in (±0.3–0.5 mm) | the host's pocket |
| Conductor tip along the contact | tip stop at the snap, then the bore's grip | the host's snap station |

**How it knows it worked.**
- At the pre-former: the ELP camera takes an end-view silhouette against a
  gauge pin in frame and measures outside width and throat. The go pin must
  enter the bore from behind and the no-go pin must not (table above). Failing
  contacts drop to a reject cup.
- After the snap: a camera looks down on jacket in the barrel, insulation edge
  in the window, strands in the U, none over a wing tip. A light tug
  (0.2–0.5 N) shows a contact that slides.
- After the crimp: whatever the host checks.

**What the person does.** Nothing at the pre-former if strip, rail, post or
plate feeds it; otherwise drops contacts into its nest in bulk, at leisure,
53 per unit in ~5–9 min while a print runs [estimate]. Sticks go to the next
station.

**Steps covered:** a new pre-form step, contact supply (sticks), place (snap).
**Hands back:** the crimp and insertion to a host; orienting loose contacts to
a rail, plate, post or person.

## What question it changes

The listed steps start from the contact as it comes out of the bag, wings
open. Re-shaping the insulation barrel first, with no wire present, changes
three later things at once:
1. **Open contacts become narrow**, ~2 mm, about JST's own catalog envelope
   (1.95 mm) instead of the kit clones' 2.46–3.25 mm. They sit at 3.4 mm with
   room for an ordinary punch and at 2.5 mm without touching.
2. **Placing the contact becomes a snap**, the motion Derek already makes with
   this ribbon at the 110 IDC keystone.
3. **Loose contacts stop nesting.** A 1.85–1.95 mm box enters neither a
   1.3–1.5 mm throat nor a 1.4–1.65 mm U [w2 §5; w3b §2], so pre-formed
   contacts stack nose to tail.

## What the final crimp does to each pre-form

This decides which pre-form suits which use. The final crimper's insulation
section is taken to be a B (two arches and a central cusp) closing to about
1.8 mm [assumption: the SN-2549's XH insulation section is unmeasured; 1.80 mm
is the KONNRA clone spec's closed insulation height and J.S.T. UK's insulation
width for SXA and SXH-002, mfr S13, S14]. A B-die forms an open barrel by
pushing the wing tips inside its width, running them up the arches to the
cusp, and driving them down into the jacket [htq §1].

- **Keyhole (round mandrel).** Its metal ends at 1.28–1.66 mm, 0.14–0.52 mm
  below the closed height, and 104–146° of the jacket's top is uncovered; the
  snapped jacket stands ~1.9 mm, proud of the tips [htq §1]. The die's arches
  never reach the tips. Its cusp meets the jacket and presses it down through
  the throat. Its side walls, reaching down to near the anvil, squeeze the
  ring's widest point; each wing turns about its root and the tip, higher up,
  moves inward 1.3–2.2 times as far [w3b §1].
  - With a 1.80–1.90 mm insulation section the throat closes from 1.3–1.5 mm
    to ~0.75–1.4 mm, pressing the tips into the jacket's shoulders.
  - With a 2.00 mm section the ring is barely touched.
  - Either way the result is an O with a narrowed gap on top, not the B the
    die was made for. The tips are never turned over the jacket.
  - It may still be an adequate insulation crimp. JST's criterion is that the
    insulation crimp holds the insulation without cutting through to the
    strands and survives 60–90° bends several times [xh-facts §5]. The test:
    pull along the wire, bends toward the throat, and a vibration soak, on this
    ribbon, beside [c2](c2-buy-the-crimp.md)'s genuine JST lead cut open as the
    reference B-crimp.
- **Tall keyhole (blade mandrel).** The walls stay straight and the tips are
  turned in at ~2.5–2.9 mm, above the closed height. The die's arches meet
  the tips and carry on the curl as they would on an open contact, so the
  final crimp is the die's own B. What it costs:
  - height: the stick channel and any passage through an open tool are
    ~0.6 mm taller, and a punch working in a row beside it must stay narrow
    higher up (2.6–3.3 mm above the anvil for a one-nest tongue [htq §5]);
  - softer walls: ~12–33 N/mm against ~80 N/mm for the keyhole's curled wings
    [hand-tool-as-press H1; w3b §2]. The silicone still yields first, so the grip is about
    the same (0.02–3.5 N axially at 0.02–0.2 mm interference per side [w3b §2]),
    but the jacket can rise ~0.6–0.9 mm inside the U before it meets the tips.
- **Tool-made U.** The crimp tool's own stroke, stopped inside the window where
  the insulation wings are inside the die width and the conductor wings are not
  yet touched: 0.65–1.7 mm of die travel on the edge model, possibly none on
  the pessimistic apex model [htq §3]. The final stroke finishes the curl it
  started. It needs no separate steel, and it is made by the tool that will
  crimp it. hand-tool-as-press develops it as a bench in
  [a6b](../../hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md) and as
  a motorised grip stop in [a1b](../../hand-tool-as-press/ideas/a1b-pawl-out.md).
  - With the tips still vertical the U has no undercut: it holds the jacket
    against lift only by wall friction, ~0.02–3.5 N. A click deep enough to
    start the curl (tip gap 1.2–1.4 mm) gives an undercut and ~0.3–27 N of
    retention [w3b §2].
  - In a machine, a host's own one-nest press can make it too, on strip before
    the tab is sheared, or on loose contacts held at ≥ ~4 mm pitch. At 3.4 mm
    a ≤4.45 mm tongue meets the open neighbours' wing tips; it clears them
    from 3.6–4.0 mm pitch up [w3b §7].

| | Keyhole | Tall keyhole | Tool-made U |
|---|---|---|---|
| What the final B-die does | pinches the sides; throat 0.75–1.4 mm or untouched; no B | finishes a B | finishes a B |
| Retention against lift | 0.15–30 N (throat) | 0.3–27 N at the turned-in tips, after 0.6–0.9 mm of free lift | 0.02–3.5 N (tips vertical) to 0.3–27 N (curl started) |
| Axial grip | 0.1–3.5 N (bore by the rule) | 0.02–3.5 N | 0.02–3.5 N |
| Stick channel | 2.1 × 2.6 mm | ~2.1 × 3.2 mm | ~2.2 × 3.2 mm |
| Gap to a neighbour at 2.5 mm | 0.36–0.54 mm | ~0.45–0.6 mm | 0.45–0.68 mm |
| Needs | a mandrel matched to the jacket | a ground blade | a window in the crimper's stroke |

## Hosts: where pre-formed contacts change another arrangement

| Arrangement | Its problem with open contacts | With pre-formed contacts |
|---|---|---|
| change-the-question [c1](c1-half-rows.md) (half-rows at 3.4 mm) | clone wings leave 0.15–0.60 mm between tips; the punch needs a lift [ctq §3–4] | ~1.25 mm between contacts; the insulation punch has 0.23–0.42 mm and the conductor punch 0.33–0.65 mm to spare beside a keyhole [w2 §2]: crimp in the row, no lift. Developed as [c1c](c1c-crimp-in-the-row.md); hand-tool-as-press's one-nest SN tongue for it is [a4d](../../hand-tool-as-press/ideas/a4d-tongue-under-a-windowed-pallet.md) |
| change-the-question [c1b](c1b-tack-first.md) (tack first) | a gang tack stroke on the wire | the snap does the tack's job with a presser |
| force-and-form [f9](../../force-and-form/ideas/f9-tack-station-feeds-crimp-station.md), machine-that-sees-and-learns [v8](../../machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md) | station T needs a steel former, a steel insert and 100–500 N over the wire | station T becomes a presser; the forming moves upstream, away from the wire |
| into-the-housing [i2](../../into-the-housing/ideas/i2-crimp-in-the-cavity.md)/K1 and [i2b](../../into-the-housing/ideas/i2b-preload-the-whole-housing.md) | the stepped crimper's 2.5–2.7 mm insulation step cannot swallow clone wings; pass-2 loading collides above ~2.8 mm wings | the mouth swallows a keyhole with 0.23–0.52 mm to spare. Developed by into-the-housing as [k7](../../into-the-housing/ideas/k7-pre-formed-contacts-crimped-in-the-cavity.md) |
| into-the-housing i2b, one-pass preload of a whole housing | clone wings clash at 2.5 mm (−0.30 to −0.75 mm) | 0.36 mm between keyholes, so every cavity mouth takes one; a conductor punch beside an open conductor barrel at 2.5 mm still has only 1.32–1.50 mm of half-width, up to 0.2 mm short for the narrow punches drawn so far [w2 §2] |
| force-and-form [f5b](../../force-and-form/ideas/f5b-half-row-cassette.md), ribbon-as-pallet [a2c](../../ribbon-as-pallet/ideas/a2c-loose-contact-cassette.md) | pockets loaded by tweezers | pockets filled from a stick by one pusher; the snap holds each conductor through the move to the press |
| hand-tool-as-press [a2b](../../hand-tool-as-press/ideas/a2b-gravity-tool-flat.md) (contacts dropped into the tool) | boxes nest into open wings, hence a revolver disc | a stick stood over the nest is the chute; an escapement at its foot singles them |
| The SN-2549 by hand, today | contact, conductor and tool juggled at once | snap first, then crimp a flag: [c6b](c6b-by-hand-this-week.md), and hand-tool-as-press's foot-closed [a6b](../../hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md) |
| Side-feed applicators (terminal-supply a1, force-and-form f2, borrowed-machines b1) | none | no use: an applicator expects open wings for a wire laid from above |

## References and tolerances

| What | Set by | Needed | Comes from |
|---|---|---|---|
| Bore | mandrel plus springback | inside 0.08–0.12 mm under the measured jacket | ground pin; go and no-go pins |
| Throat | jaw profile at closure | ±0.05–0.1 mm: it sets snap force and retention | steel jaw on a stop; silhouette |
| Contact in the pre-former | box in the nest, front face on the stop | ±0.1 mm axially, so the pre-form lands on the insulation barrel and not on the window | nest |
| Conductor over the contact at the snap | comb slot | ±0.3–0.5 mm | printed comb |
| Axial position of the conductor | tip stop at the snap, then the grip | ±0.3 mm keeps the insulation edge in the window | the snap station |

## Printed and bought

**Steel** (wing edges on a printed face would gouge it: a line contact of
220–770 MPa against 48–80 MPa yields [terminal-supply exchange calc §8, via
c3]):
- **Mandrel.** A ground pin at the size the table gives. The Prime-confirmed
  Accusize 0.28–1.52 mm pin set ($45.58, 167 ratings, 60–62 HRC
  [sourcing/amazon-prime.md]) holds a mandrel and both pins only if the jacket
  measures ~1.60 mm; at 1.70 mm the 1.56–1.65 mm pins are requested
  ([`../sourcing-requests.md`](../sourcing-requests.md)).
- **Blade mandrel.** Ground from a 3 × 3 mm HSS blank (Prime-confirmed, five
  for $9.99, 47 ratings [sourcing/amazon-prime.md]) to 1.5–1.6 × ~2.5 mm.
- **Jaws.** Cut and stoned from the same HSS blanks.
- **Nest.** Ground steel, laminated stencil steel (JLCPCB stainless stencils
  from $3, ~24 h [into-the-housing source]), or a cut kit XHP housing.

**Printed:** the frame, lever, servo mount, reject cup, sticks.

**Bought:** a metal-gear servo (the 35 kg·cm DS3235 is Prime-confirmed at
$27.99 [sourcing/amazon-prime.md]) or the POWERTEC 305CM push-pull toggle
clamp (Prime-confirmed, $18.25 a pair, 605 ratings).

## Problems worked through

1. **The final crimp over a pre-formed barrel.** Set out above, by shape. The
   keyhole is not re-formed into a B; the tall keyhole and the tool-made U
   are. What stays open for all three is re-registration: a pre-formed barrel
   meets the die already narrow, so it is not centred by the flare the way an
   open one is. The conductor section's flare still centres the contact
   before the insulation section bottoms (S1 in
   [`../../../exchange/change-the-question--on--into-the-housing-w3.md`](../../../exchange/change-the-question--on--into-the-housing-w3.md)), and a floating
   nest or pallet lets it. Sectioning and pull tests, pre-formed against
   open, in the same tool, settle it (machine-that-sees-and-learns'
   [v3](../../machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)
   sweep, one more arm).
2. **Snapping the jacket in springs the wings open.** Each curled wing is
   ~80 N/mm elastically [estimate]; a few newtons open it ~0.03 mm and it
   closes again. The silicone (2.5–5.5 MPa [w2 §4]) does the yielding. At a
   1.2 mm throat and hard silicone a wing root could yield, so the throat is
   kept at 1.4–1.5 mm.
3. **The sheared wing edges cut the silicone as it passes.** The line load is
   a few N/mm against silicone's 15–25 N/mm tear strength [estimate; source
   Primasil via ribbon-as-pallet]. Curling the tips far enough that the throat
   is formed by the wings' rounded outer faces turns the sheared edges down
   and inside.
4. **Pre-forming removes the wide head that rails, pocket plates and posts
   orient by.** The pre-former comes after them in the line.
5. **Genuine JST contacts may already be 1.95 mm wide.** Then open genuine
   contacts already sit at 2.5 mm with 0.55 mm between them [ctq §3], and the
   pre-form matters mainly for the kit's clones and for the snap. One caliper
   reading of each settles it.
6. **It is a sixth step and a sixth machine.** It runs without the ribbon, at
   10–80 N, unattended, and its output waits in sticks.
7. **Roll is held only by friction** once a flag leaves its pocket. Hosts
   that keep the contact in its pocket through the crimp (c1c, k7) do not
   depend on it; hosts that move a loose flag need something keyed to the box
   (c6b's seat, a cut housing stub).
8. **The grip depends on the jacket.** A bore chosen from the nominal 1.70 mm
   grips nothing on a 1.60 mm jacket. The mandrel is chosen from the measured
   OD (table above). If the OD wanders ±0.1 mm along one spool, one mandrel
   cannot follow it, and the grip spans ~0–6 N across the spool [htq §2].

### Sub-variant: close the ring

- Close the wings to a full ring of ID ~1.75–1.8 mm, just over the jacket.
  The conductor is then **threaded along its axis**, strands first, with the
  ring as a guide that centres the jacket and the open conductor U ahead of it
  to receive the strands.
- It suits arrangements that thread a still conductor into a captured
  contact: force-and-form [f3](../../force-and-form/ideas/f3-knee-micropress.md)
  and [f4](../../force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md), and
  into-the-housing's [k6](../../into-the-housing/ideas/k6-one-gantry-crimps-in-the-fan-then-sorts.md)
  head.
- It gives up the snap and asks ±0.05 mm between a 1.7 mm jacket and a
  1.8 mm ring unless the rear edge is flared. The ring's metal stands ~2.2 mm,
  above the 1.80 mm closed height, so the die does re-form it, into an oval
  rather than a B (hand-tool-as-press K3). Untested.

## Contribution

- It makes "place the metal bit on the end of the cable" a **light lay-in and
  snap**, without a tack stroke on the wire.
- It dissolves the open-wing collision that shapes every gang and preload idea
  in the study.
- It turns loose kit contacts into a stackable, ordered supply.
- It separates the light, pitch-sensitive forming (ahead, in bulk) from the
  heavy, precise forming (the crimp).
- It sets out three pre-form shapes against what the final die does to them,
  so the choice is made on the crimp, not on the pre-former.

## Major unresolved problems

- **Which pre-form, and whether its final crimp is sound.** The keyhole's
  final crimp is an O with a narrowed gap, not a B, and needs qualifying on
  bends and vibration. The tall keyhole and the tool-made U are re-formed into
  a B, but re-registration of a narrowed barrel is unmeasured. Sectioning and
  pull tests, beside a genuine JST crimp.
- **Whether the SN-2549 has an insulation-first window at all** (for the
  tool-made U): 0.65–1.7 mm of die travel on the edge model, possibly none on
  the apex model [htq §3]. One slow close on an empty contact, looked at
  end-on, decides it.
- **The SN-2549's insulation section**, B or not, and its width (assumed
  1.8–2.0 mm): it sets how far the keyhole's throat closes.
- **Snap force and retention** span more than an order of magnitude on
  estimates (0.3–30 N push, 0.1–3.5 N axial). Five minutes with a kit
  contact, a pin, pliers and the bench scale narrows it.
- **The jacket's real OD, and how much it varies along a spool.** It sets the
  mandrel.
- **Springback scatter** between kit clones (phosphor bronze or brass,
  unknown) sets how repeatable the throat is.
- **The crimp beside open neighbours at 2.5 mm** in the one-pass preloaded
  housing is still short by up to 0.2 mm for the narrow punches drawn so far.
- **Roll is held only by friction** once a flag leaves its pocket.

## What rests on assumptions

- Contact dimensions are clone drawings [source S19–S22]; the kit contacts are
  unmeasured.
- The final crimper's insulation section is a B closing to ~1.8 mm, 1.8–2.0 mm
  wide [assumption].
- Stock yield (450–650 MPa phosphor bronze, 300–420 MPa if brass) and modulus
  [estimate].
- Silicone modulus from Shore hardness by Gent's relation [estimate]; the snap,
  grip and throat-closure models are order-of-magnitude [estimate].
- Rigid-wing kinematics for the throat closure [estimate, w3b §1].
- That the insulation barrel's rear is open to a mandrel on strip, above the
  tab [assumption from the side-feed geometry, xh-facts §1].
