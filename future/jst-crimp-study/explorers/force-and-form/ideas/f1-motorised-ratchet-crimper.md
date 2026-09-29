# f1 — The hand tool is the press: a ratchet crimper closed by a slow actuator

Explorer: force-and-form. Sketch: [`../sketches/f1-motorised-ratchet.svg`](../sketches/f1-motorised-ratchet.svg) (schematic).
Numbers: [`../calc/drives.out.txt`](../calc/drives.out.txt) §E,
[`../calc/force_loop.out.txt`](../calc/force_loop.out.txt),
[`../calc/placement_budget.out.txt`](../calc/placement_budget.out.txt),
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) §1, §11,
[`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) §3, §4, §10 [calc final §n],
[`../calc/exchange_procedure_w3.out.txt`](../calc/exchange_procedure_w3.out.txt) [calc FP §n];
change-the-question's [`on_force_and_form.out.txt`](../../change-the-question/calc/on_force_and_form.out.txt)
[change-the-question calc off §n].
**[Prime]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
Branch: [`f1b-wc110-in-the-cradle.md`](f1b-wc110-in-the-cradle.md). Related:
[`f9`](f9-tack-station-feeds-crimp-station.md) and
[`f9b`](f9b-tack-on-the-strip.md) (a tacked contact as f1's supply),
[`f10`](f10-lift-once-fin-from-below.md) (a flat row worked without a hand tool).

## Picture it

A second iCrimp SN-2549, the tool Derek crimps XH with today [repo], lies flat
on a steel plate. A printed cradle clamps its lower handle. A 12 V linear
actuator (or a NEMA 17 lead-screw pusher) stands over the end of the upper
handle, with a load cell in its rod. Extending the actuator squeezes the
handles as a hand does, and the tool's own compound toggle and ratchet do the
forming.

Because the tool lies flat, the XH nest's axis is vertical: the wire hangs
straight down through the jaws, and the contact stands box-down under them.

- **Contact supply.** One of four, and the choice sets how often the machine
  calls the person (table below): a keyed stick magazine loaded at leisure; a
  strip with a shear that cuts one contact off over the flap; a contact already
  tacked to its conductor by another station; or a contact dropped in by hand.
- **Locator: a swinging flap** under the jaws, hinged outside the tool's
  outline. In its outer position it takes a contact box-down into a keyed slot
  (box outline plus a notch for the lance, so the contact fits one way round).
  It then swings in under the open nest and lifts, carrying the barrels up into
  the nest from below. The slot's steel floor sets how far the contact stands
  into the dies. This is how JST's own flap locator carries a contact into the
  WC-110 [mfr S6, S7]. A contact never passes down through the nest.
- **Hold, short of the first tooth.** The actuator closes the jaws to a
  measured position just short of the ratchet's first tooth: the nest's walls
  now surround the barrels and the flap holds the box, but no wing is pinched
  and the ratchet is not yet engaged. (The hand procedure's "one click" pinches
  the insulation wings; see "the bore at capture" below.)
- **The ribbon** hangs from a clamp on a small X/Z carriage above the tool,
  split and stripped, strands lightly twisted. A fork under the clamp holds the
  other conductors up and out of the jaw plane, all bent to the same side.
  Tines enter from the free tips and slide rootward, because at 1.7 mm pitch
  neighbouring split conductors touch; or the ribbon has been split into two
  planes 3.4 mm apart (change-the-question c1) and the tines drop straight in.
- **Look.** Before threading, the ELP camera with a backlight photographs
  conductor *i*'s hanging tip: the silhouette gives its bare length and whether
  the brush is whole.
- **Thread.** The carriage lowers conductor *i* through a printed funnel into
  the fully open barrels with a small side-to-side wiggle, to the Z that puts
  its insulation edge mid-window. Z is referenced to the flap's slot floor, and
  the camera's bare length turns the strip's ±0.2 mm scatter into ±0.1 mm on
  the brush and ±0.1 mm on the window, instead of an exact brush and ±0.2 mm on
  the window [calc final §10].
- **Crimp.** The actuator completes the stroke. The ratchet engages on the way
  and releases only at full closure.
- **Proof pull.** The actuator backs off to open the jaws. A 0.3 mm neck blade
  (a feeler-gauge leaf) on a small servo drops in from the side between the box
  and the conductor barrel, and the carriage lifts the conductor to ~20 N with
  the blade bearing on the box's rear face. The blade touches only after the
  crimp, so the tips never meet it.
- **Release.** The blade withdraws, the flap swings out, and the carriage lifts
  the crimped contact clear.
- **What is logged.** Actuator force against travel on every stroke (the crimp
  curve seen through the tool's linkage), the bare length, the pull force and a
  camera frame.
- **The person** loads the magazine or strip, clamps a pre-split, pre-stripped
  ribbon end in the carriage, and inserts the crimped contacts afterwards.

## What locates what, and the reference for fixed

- **Fixed:** the tool's fixed jaw. The cradle holds the handle near the head so
  the head does not rock.
- **Contact to dies.** Laterally, the flap's steel-faced keyed slot and then
  the nest walls and crimper flare: a ±0.15–0.3 mm window [calc
  placement_budget]. Axially, the slot floor: ±0.1 mm needed.
- **Conductor to contact.** Laterally, the U walls centre the 0.72 mm bundle.
  Axially, carriage Z from the slot floor plus the camera's bare length:
  ±0.1 mm on each of brush and window.
- **Crimp height.** The tool's. If the jaws bottom face to face (unmeasured),
  jaw compliance scatters it by ±0.01–0.02 mm for ±25 % force variation [calc:
  force_loop §2, stiffness estimated].
- **Where precision is needed.** At loading: the flap slot. At first die touch:
  the tool's jaw alignment. At the bottom: the jaw faces. At release: none.

## What drives the crimp and carries the force

- **Force loop.** Entirely inside the tool: jaws, pivots, toggle links,
  ratchet. The cradle and actuator supply only handle force and travel.
- **Handle force.** Not published for the SN-2549. At an assumed 15–40:1 near
  closure and 0.75–2.4 kN at the die, roughly **40–250 N at the grip** [calc:
  drives §E]. hand-tool-as-press's bound from hand force (89–222 N) agrees. The
  actuator's stroke covers the grip point's ~40–60 mm [estimate].
- **Actuators** [Prime]:
  - Justech 1,500 N, 50 mm, 12 V, self-locking, limit switches, no position
    feedback, $29.99 (230 ratings);
  - Progressive Automations PA-01-POT, ~750 N with a potentiometer, 50 mm,
    $155.39 (thin);
  - or a NEMA 17 on a Tr8×2 screw, ~230–280 N [calc drives §C] (Iverntech
    42HD6039-05, $27.99, thin).
- **Force sensing.** An S-beam load cell in the actuator's rod [Prime: S-type
  load cell, 100 kg variant, $37.71, thin] and an HX711 [Prime: SparkFun HX711,
  $11.50].
- **Speed** does not matter: a 10 s close is ~100× slower than a hand squeeze,
  and slowness only lowers copper's flow stress by a few percent [calc:
  stroke_model §3].

## How it knows it worked

- The force-against-travel curve through the ratchet sees a missing conductor,
  insulation in the conductor barrel, and a missing, high or rolled contact.
  It does not see one strand of sixty (~1.7 % of force against a monitor's ±4 % band [digest]).
- The bare-length silhouette before threading is the strand guard.
- The proof pull at ~20 N, before any insertion.
- Crimp height is the tool's; a caliper sample per ribbon end checks it.

## Contact supply and how often the person is called

The contact's form sets the call rate more than any mechanism does
[change-the-question calc off §7]:

| Supply | Calls per unit | What it costs |
|---|---:|---|
| Loose contact dropped in by hand, per crimp | ~67 (14 ribbon loads + 53 drops) | An attended station: it buys location, consistency and a log, not minutes. It saves minutes only as one of two heads the person alternates between (procedure-is-the-machine p4b) |
| Keyed stick magazine: a printed stick with the flap's box-and-lance profile, loaded with 53 contacts in one sitting; an escapement releases one into the flap | ~15 | The 53 handlings remain, now in one sitting away from the machine |
| Strip over the flap: a strip track ends above the flap's outer position; a servo shear cuts the lead contact off, leaving a tab of one to two stock thicknesses, and it drops into the slot | ~14 | A shear whose tab length meets JST's "not none, not too much" [mfr S5]; a reel every ~150 units |
| Tacked contact on its conductor ([`f9`](f9-tack-station-feeds-crimp-station.md), [`f9b`](f9b-tack-on-the-strip.md)) | ~14–34, none paced by the crimp | The flap becomes the heavy crimp's locator; the carriage lowers contact and wire together, box-first. The SN-2549's open nest must pass box plus lance, 2.8–3.25 mm (one pin gauge) |

The strip-over-flap and terminal-supply's a2c (a pin clip on the jaw that
locates a strip's lead contact in the nest) are two ways to give the SN-2549 a
locator from strip: a2c keeps the contact on its carrier until the crimp and
bends the carrier off after; the flap route cuts first and drops.

## Printed and bought

| Part | Printed or bought | Evidence |
|---|---|---|
| iCrimp SN-2549 ratcheting crimper (second unit) | bought | [Prime: iCrimp SN-2549, $22.29, 532 ratings, 100+ bought in past month]; $20.99 at iCrimp's own store, jaws wire-EDM cut [source: icrimptools.com]. Derek owns one [repo] |
| Linear actuator or NEMA 17 pusher; S-beam load cell; HX711 | bought | [Prime] rows above |
| Swinging flap (steel seat face, printed body); neck blade from a feeler leaf; small servos | printed body; bought blade and servos | [Prime: Hotop feeler gauge, 0.02–1.00 mm, $8.99]; [Prime: Miuzei MG90S, 4 pack, $13.88] |
| X/Z ribbon carriage, fork, funnel, cradle, stick magazine or strip track | printed, printer-class steppers | — |
| Backlight for the silhouette | bought | [Prime: XIAOSTAR A5 light pad, $16.99] |

Rough total: $80–250 of bought parts plus printing, depending on the actuator
[estimate].

## What was tried against it, and where it stands

1. **The bore at capture.** At the first click the insulation wing tips are
   pinched to the insulation crimper's channel, 1.4–1.6 mm apart. The tips
   stand 0.7–1.0 mm above a 1.7 mm conductor's top, so the conductor meets the
   wings at its equator, where a wing hinged at its root is still near the
   floor's width. Modelled that way, the least clearance runs from −0.17 mm
   (floor 1.6 mm) to +0.17 mm (floor 2.0 mm): clear at 1.9 mm or more, ±0.05 mm
   at 1.8, 0.03–0.17 mm of interference at 1.6–1.7 [calc wave2 §1]. The hand
   procedure (one click, then feed the wire) is the existence proof that some
   capture height works. Holding the jaws short of the first tooth removes the
   question: the barrels stay fully open while the conductor goes in.
2. **The ratchet cannot let go.** Once engaged, the tool will not open until
   full closure. Holding short of the first tooth means a failed thread never
   meets an engaged ratchet. If the stroke must be aborted after engagement:
   complete it empty and discard the contact ($0.01–0.04), or a servo on the
   pawl's release lug (hand-tool-as-press a1b).
3. **No wire stop in the tool.** Continuity from the far end fails as a depth
   sensor, because the strands touch the barrel on the way in. A neck blade
   used as a stop sets the brush exactly but leaves the insulation edge to the
   strip's scatter (±0.2 mm), and a lead screw pushing tips against a blade can
   fold strands back inside the barrel (a 2.4 mm bare bundle buckles at ~6 N
   free [calc FP §5]). So depth comes from the camera and the carriage, and the
   blade only reacts the pull.
4. **Loading through the nest.** A flap fixed under the jaws would have to be
   filled through the open nest: box plus lance is 2.8–3.25 mm across the jaw
   opening, and the box (1.85–1.95 mm) is wider than the conductor crimper's
   channel. The swinging flap loads outside the jaws and carries the contact up
   from below. *Left:* the nest gap at full open (one pin gauge).
5. **The neighbours take a set.** The jaw plate spans ±10–15 mm around the XH
   nest, and conductor *i*'s barrels sit 3–4 mm into it, so the neighbours'
   tips must stand 4–6 mm higher [estimate]. Every conductor has the same
   length from the web, so each neighbour is bent 37–46° at the fork line over a
   20 mm split, 30–37° over 30 mm, 26–32° over 40 mm. Bent in one arc above
   copper's ~67 mm set radius, a 30 mm conductor shortens only 0.25 mm: the set
   is unavoidable [calc final §4]. What the fork chooses is its direction: every
   non-working conductor bent to the same side, so the ribbon end leaves with
   one uniform set for an insertion comb (ribbon-as-pallet a6) or the person to
   take out.
6. **Which jaw is the anvil.** Unknown here. The cradle can clamp either handle
   and the actuator push the other.
7. **Quality is the tool's.** The machine reproduces today's hand crimp with
   better location and a logged curve. It cannot make the crimp more
   JST-correct than the SN-2549's XH nest is. [`f1b`](f1b-wc110-in-the-cradle.md)
   takes that up; the JST reference lead ($0.90), copper-corrected at the SN's
   own crimp width, says whether it matters [calc final §7].
8. **The insulation step is fixed**, and on 1.7 mm silicone the window between
   cutting the jacket and overfilling the cavity is roughly 2.0–2.2 mm tall at
   1.8–1.9 mm wide [calc wave2 §5]. Where the SN's step lands is unmeasured;
   five hand crimps bent **down** over a 2 mm pin and photographed answer it
   ([`f6`](f6-two-blades-two-drives.md)).

## Contribution

- **A route to "place and crimp without hands"** on a tool Derek already
  trusts, for $80–250 of bought parts plus printing.
- **A swinging keyed flap** that orients a loose contact by its lance and
  carries it into a nest that has no locator of its own.
- **Hold short of the first tooth:** the jaws locate without pinching and the
  ratchet cannot trap a failed thread.
- **A neck blade that reacts a proof pull on the box's rear face**, needing no
  far-end wiring.
- **The tool is also a crimp head**, ~0.3 kg plus actuator with its force loop
  closed in the tool, which a gantry could carry.
- **Motorless first build:** the cradle, flap, neck blade and a hand on the
  handles are a locator jig for today's hand procedure before any actuator is
  fitted.

## How it connects to the whole procedure

| Step | Who does it |
|---|---|
| Cut | the person |
| Splay | the person pre-splits; the fork holds the rest aside at crimp time |
| Strip | the person, or another explorer's stripper |
| Supply contacts | magazine, strip shear, or a tack station |
| Place the contact | the swinging flap |
| Present the conductor | **automated** (carriage, camera-set depth) |
| Crimp | **automated** |
| Proof pull | **automated** (carriage against the neck blade) |
| Insert, test | the person, or a sibling's insertion station and a real-wafer tester |

## Major unresolved problems

- **Handle force and travel of the SN-2549**, which size the actuator.
- **Whether the SN-2549's XH nest meets JST's crimp height** on this ribbon,
  for the machine and for today's hand crimps alike.
- **Where its fixed insulation step lands** in this wire's window.
- **The position short of the first tooth:** whether the nest walls locate the
  barrels there, or only the flap does.
- **Whether the neck** takes a 0.3 mm blade in front of the brush: the
  transition *t* ≥ 0.50–0.70 mm [calc final §3].
- **The fork's set** on every neighbour, and who takes it out.
- **Whether the force curve through a ratchet** is clean enough to flag
  faults.

## Which conclusions rest on assumptions

- **Actuator sizing** rests on the assumed tool ratio. At 10:1 a 500 N actuator
  still covers the high case.
- **The bore at capture** rests on the wing-as-hinged-plate model and an
  unmeasured floor width.
- **The keyed slot** assumes the lance is on the floor side and stands
  0.6–0.9 mm proud [source: xh-facts §1].
- **The neighbours' height** (4–6 mm) is an estimate of how deep the barrels
  sit in the jaw plate.
