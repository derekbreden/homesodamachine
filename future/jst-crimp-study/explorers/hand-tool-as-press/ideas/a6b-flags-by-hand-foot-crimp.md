# A6b — Flags by hand: the SN-2549 pre-forms its own contacts, a snap block puts each on its wire, the foot crimps

## Picture it

**Where things start.**
- The ribbon end is cut, split and stripped at [a6](a6-foot-closed-jig-bench.md)'s
  end jig, the strip length set from one measured contact of the lot.
- Its far end sits in the far-end block, one Wago 221-415 per conductor
  ($28.00 for 25 [prime: B0107SYYGU]), on ESP32 inputs.
- Kit contacts sit loose in a dish.
- There are two SN-2549s: the bench's, and a second one ($22.29, 532 ratings
  [prime: B01N4L8QMW]). Or the one tool is used in two passes.

**Station P, pre-form (no wire anywhere near).**
- The second SN-2549 lies in a cradle. [a1](a1-squeezer-cradle.md)'s locator
  plate on the lower jaw's M4 screw keeps only its front stop; there is no
  blade, because there is no wire.
- Derek drops a contact barrels-up into the XH nest, box against the stop, and
  squeezes to click *k*. Click *k* was chosen once per contact lot, under the
  ELP end-on: the deepest click at which the insulation wings are inside the
  die width and the conductor wings carry no mark.
- He presses the release lever. The jaws open, and a printed plunger pushes the
  contact forward, box first, into a loom-order **stick** clipped at the jaw's
  front face. Moving forward, the lance (tip rearward) leaves the anvil's front
  face and cannot catch.
- What comes out [htq §3, estimate]: the insulation barrel narrowed to about
  the die width, 1.8–2.0 mm plus 0.02–0.05 mm springback; its tips curled
  inward high in the arches, ~2.3–3.0 mm tall; the conductor barrel open and
  untouched. This is the shape the final stroke passes through anyway.
- Contacts this narrow stack nose to tail without nesting: a 1.85–1.95 mm box
  cannot enter a U whose inside is 1.4–1.6 mm. Sticks are printed channels
  (2.1 × 2.6 mm with a lance groove), one per housing and labelled; J2's has a
  blank spacer at position 3, so the stick is the build list.
- About 8–12 s each, 7–11 min per unit, while a print runs [htq §8].

**Station S, snap.** change-the-question's
[c6b](../../change-the-question/ideas/c6b-by-hand-this-week.md) snap block:
- a steel-lined box pocket with a lance groove and a front stop, and a
  backlit window under the pocket;
- a tip stop that is a **steel plate wired as an electrode** (the pocket
  lining is not wired).

Derek pushes the next contact from the stick into the pocket and lays one
stripped conductor over it with its cut tip on the plate. The ESP32 names the
conductor, and buzzes if it is the wrong one. The window shows the stripped tip
against the light: no stray strands, the whole bundle over the U. His printed
thumb tool's rear tine presses the jacket down into the narrowed U; its front
tine lays the strands in the open conductor U. He lifts a **flag**: a contact
held on its wire at the right axial position and roll.

**Station C, crimp.** The bench SN-2549 in a6's cradle, closed by the cord
treadle. The treadle is **single-stage**: there is no hold stage, because
contact and conductor are already one part. The tool carries a **flag seat**:
- on the jaw's rear face, a printed U guide takes the jacket;
- on the front face, c6b's clip carries an open-topped slot keyed to box and
  lance, on a sprung ledge;
- both guide and ledge sit at one height *h* = 1.1–1.7 mm above the anvil, on
  1–3 N springs;
- the front stop is a spring-steel leaf preloaded to 10–30 N, insulated from
  the tool and wired: **green** when the box face touches it;
- the tool's jaws are wired too: **amber** when the punch first touches the
  contact.

Derek lays the jacket in the rear U and slides the flag forward, box first,
**until green, and stops pushing**. He presses the treadle:
1. amber: the punch meets the wings;
2. the contact is pushed down onto the anvil against the 1–3 N springs;
3. the wings curl and coin;
4. the ratchet completes the stroke.

When the tool opens, the springs lift the crimp back to *h*, above the anvil
face that would catch the lance, and he draws it back out through the nest.
The cord's load cell and the pulley's AS5600 log force against travel, as in
a6.

**Then:** a6's pull-and-look jig and keyhole gauge, on every crimp or on
samples, and into-the-housing's i5 nest for insertion, on the same far-end
block.

**What locates what.**

| Pair | Reference |
|---|---|
| Contact to the pre-forming die | Box face on the locator's front stop, in the same XH profile that later crimps it |
| Conductor tip to contact | The snap block's box stop and tip stop (electrode); afterwards the snap's grip |
| Flag to the crimp die, axially | Box face on the wired front-stop leaf (green) |
| Flag laterally and in roll | The keyed slot on box and lance; the rear U on the jacket |
| Flag vertically | The sprung supports at *h*, then the punch presses it onto the anvil |
| Crimp height | The SN-2549's dies and ratchet, as today |

"Fixed" is the lower jaw at P and C, and the snap block's pocket at S.

**What drives and carries the crimp force.** The foot, through the cord and a
2:1 treadle: 55–122 N at the toe for 100–220 N at the grip [calc w2 §5]. The
tool's linkage multiplies it; the force closes jaw to jaw inside the head. The
ratchet guarantees full closure. The pre-form at P takes a small part of a
hand squeeze.

**How it knows it worked.**
- The stick's order and gaps are the build list.
- The tip electrode confirms identity and tip position before the snap.
- The backlit window shows stray strands before they are hidden.
- Green means the box is at its stop. Amber marks die touch; amber before the
  foot moves means the flag is touching a jaw.
- The force–travel curve.
- The pull-and-look jig and the keyhole gauge.
- i5 pairs each conductor with its cavity.

**What the person does.** Every motion, by hand and foot: pre-form away from
any wire; snap; slide the flag to green, press the treadle, draw it back; pull
and gauge, if sampled; insert and label.

**Time** [htq §8, estimates]: 22–34 s per contact, of which 14–22 s at the
wire; 19–30 min per unit, 7–11 of them pre-forming while a print runs; against
~22 min today and ~31 min for a6 with pull and gauge. What it buys is one part
and one stop per act, and a check at each stop. It does not buy minutes.

Sketch: [`../sketches/flag-seat.svg`](../sketches/flag-seat.svg) (schematic).

## Steps it covers and what it hands back

**Covers (by jig and electronics):** contact supply in loom order (sticks),
placing the contact on the conductor against two stops, holding them together
(the snap), identity before the snap, the crimp's axial reference, die touch
and force log, pull, height and fit checks, pin-order pairing at insertion.

**Hands back:** every motion. There is no motor.

## How it relates

- Branch of [a6](a6-foot-closed-jig-bench.md). It changes one thing: the
  contact meets its conductor before the crimp tool, so a6's neck blade, its
  first-tooth question, and steering a floppy conductor into a captive contact
  all drop out.
- Combines change-the-question's
  [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md) (narrow the
  insulation barrel before any wire, so the conductor snaps in and the contact
  travels as a flag) and
  [c6b](../../change-the-question/ideas/c6b-by-hand-this-week.md) (the snap
  block, the loom-order sticks and the box-keyed clip). Proposed as K1 in this
  explorer's
  [exchange](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md).
- The new move from this view: **the pre-former is the crimp tool itself,
  stopped early.**
- Its machine-made sibling: [a6c](a6c-flags-by-machine-foot-crimp.md), where a
  tack station makes the flags and the same seat takes them.
- How it grows:

| Hand piece | Its motorised or shared form |
|---|---|
| The click pre-former | [a1b](a1b-pawl-out.md)'s pawl-out cradle stopping at a taught grip position. The force rise on the pre-form stroke gives each contact's wing height, which sorts mixed-maker contacts |
| The sticks | [a2b](a2b-gravity-tool-flat.md)'s chute; the feed of [a4d](a4d-tongue-under-a-windowed-pallet.md)'s pallet |
| The snap block | change-the-question c1c's pallet with a presser comb ([a4d](a4d-tongue-under-a-windowed-pallet.md)) |
| The flag seat and wired stop | A head feeding flags along the guide (a2), where the side-entry jaw law still applies |
| The treadle | a1's pusher |

## Why the pre-former is the crimp tool

- **A single-stroke tool shapes the insulation barrel first.** The tall
  insulation wings (2.75–3.20 mm open) meet the die before the short conductor
  wings (1.50–1.60 mm). On an edge model of the die, the insulation wings are
  pushed inside the die width over 0.65–1.7 mm of stroke before the conductor
  die touches anything: 2–10 mm of grip travel, likely one or more ratchet
  clicks [htq §3, estimate].
- **A round keyhole is a shape the die neither makes nor re-forms.** c6's
  keyhole (a 1.57–1.65 mm bore with a 1.3–1.5 mm throat) puts its highest metal
  0.14–0.52 mm below the 1.80 mm closed insulation height of the clone spec,
  with 104–146° of the jacket's top uncovered [htq §1]. A B-profile die closing
  to 1.80 mm meets the jacket first and dips at its central cusp, where there
  is only jacket, so it squeezes the sides and indents the jacket through the
  throat; it does not turn the tips over [assumption: the SN's insulation
  section is a B]. A B die's own stroke gives a narrowed U with tips high, and
  never passes through a round bore with an open throat.
- **The tool-made pre-form** keeps its tips above the closed height, so the
  final stroke finishes the curl it started. Its outer width (1.8–2.05 mm)
  keeps c6's pitch gains.

## Why the flag rides a sprung seat, and why green means stop

- **What holds the flag on its wire.** c6's grip model, at the bore that
  springback leaves and at the ribbon's 1.7 ±0.1 mm conductor OD, gives
  0.08–3.8 N axially, and nothing at the low end of the OD [htq §2]. The
  tool-made U's walls are ~2.3–3.0 mm tall and ~12–33 N/mm stiff against c6's
  ~80 N/mm curled wings [estimate, 3EI/L³]; the silicone (2.5–5.5 MPa) still
  yields before the wall does. The grip in a U rather than a round bore is
  unmeasured.
- **What a flag dragged on the anvil does.** Pushed box-first from the wire
  side with its floor on the anvil, the flag's lance (0.6–0.9 mm proud, tip
  rearward) meets the lower jaw's rear edge and is folded and dragged across
  the jaw's thickness. The fold takes 1–5 N [ith ex §3], more than the grip
  across most of both ranges, so the contact stops and the jacket keeps
  moving: the strip position the snap block set is lost without any sign
  [htq §4].
- **The seat.** Carried level at *h* = 1.1–1.7 mm the lance clears the anvil
  on entry (lance + 0.2 = 0.8–1.1 mm), and the springs give back the
  1.0–1.7 mm lift a crimped lance needs before drawing back [ith ex §2]. The
  springs are 1–3 N; the wings start to curl only at tens of newtons, so the
  punch seats the flag on the anvil before it forms anything [calc w3 §5].
- **Green, then stop pushing.** The flag's grip is small, so the event that
  ends the push matters more than the stop that receives it. The leaf's
  10–30 N preload makes it a stop for every ordinary push and a detent that
  yields rather than crush a contact that has grown.

## Major unresolved problems

- **Whether the window exists** on this SN-2549. On the edge model it is
  0.65–1.7 mm of die stroke; on a pessimistic apex model it runs from −0.12 to
  +0.78 mm and can vanish [htq §3]. One slow close, click by click, on an empty
  contact under the ELP settles it.
- **What throat the chosen click leaves** after springback, and the snap's
  grip in a U rather than a round bore.
- **Whether the SN-2549 opens 3.6–4.9 mm at the nest** for a flag carried at
  *h* [calc w3 §5]. Unmeasured. If it falls short, the flag enters from the
  front with its conductor threaded back through the nest (c6b's alternative),
  or is dragged at full opening (2.4–2.6 mm) with a pusher behind the box's
  rear shoulder, which a person cannot place through a nest.
- **The SN-2549's insulation profile:** B or not, and its closed height
  (assumed 1.8–2.1 mm). An ELP or Revopoint image of the die, or one crimp on a
  bare jacket cut through, settles it.
- **The release lever at a mid-cycle click.** The SN family's release lug frees
  the pawl mid-cycle [source: forum; IWISS video title]; that it does so at
  every click is assumed.
- **The jacket's real OD.** It sets the snap's grip; caliper five split
  conductors, not the ribbon pitch.
- **Far end first:** the far end must be stripped and in the block before the
  XH end is crimped (a6's open item).

## Parts

- **Printed:** P's front-stop plate and plunger; sticks; the snap block body,
  window and thumb tool; C's rear U guide, sprung ledge and keyed clip;
  a6's cradle, treadle and jigs.
- **Steel:** the snap block's pocket lining and tip plate (stencil steel or a
  feeler leaf); the front-stop leaf (1095 blue-tempered shim, $53.39 for the
  assortment [prime: B00065V062]).
- **Bought:** the second SN-2549; light compression springs, ~1–3 N at
  1–2 mm, 3–5 mm OD (the $6.99 assortment [prime: B0BVTDP29W] has wire sizes
  unread; a mini-spring request is in `sourcing-requests.md`); Wago 221-415s;
  the ELP on hand; LEDs, buzzer, ESP32.

## Rests on

- **[estimate]** The insulation-first window (edge model) [htq §3].
- **[estimate]** The flag's grip 0.08–3.8 N [htq §2, change-the-question's
  model at the bore after springback].
- **[estimate]** Lance fold force 1–5 N [ith ex §3].
- **[assumption]** The SN's insulation section is a B profile.
- **[assumption]** A thumb press seats a 1.7 mm jacket into a 1.4–1.6 mm-wide
  U without cutting it on the sheared wing edges.

---

Citation keys: **[calc w2 §n]** is [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[htq §n]** is [`../calc/exchange_ctq_w3.out.txt`](../calc/exchange_ctq_w3.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
