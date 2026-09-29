# v8 — Tack, look, then crimp: a light watched station pins the contact to the conductor, and the heavy crimp comes after

Explorer: machine-that-sees-and-learns.

Combines change-the-question's [c1b](../../change-the-question/ideas/c1b-tack-first.md),
force-and-form's [f9](../../force-and-form/ideas/f9-tack-station-feeds-crimp-station.md)
and this view's [v1](v1-watched-nest.md).

Related:
- [v9](v9-tack-at-the-anvil.md): the tack made at the anvil of a stopped crank
  applicator, so T and C are one place; its by-hand branch is
  [v9b](v9b-tack-by-hand-on-the-jack-test.md).
- Hosts for C developed by other explorers from this station:
  hand-tool-as-press's [a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md)
  (a one-nest SN die set on the same stage) and
  [a6c](../../hand-tool-as-press/ideas/a6c-flags-by-machine-foot-crimp.md)
  (tacked by the machine, crimped by Derek's foot).
- Tacking a whole docked strip segment in one stroke: force-and-form's
  [f9b](../../force-and-form/ideas/f9b-tack-on-the-strip.md).
- The by-hand relatives: hand-tool-as-press's
  [a6b](../../hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md) and
  change-the-question's [c6b](../../change-the-question/ideas/c6b-by-hand-this-week.md).
- Runs on [v7](v7-the-run.md); rung 1 of v7's ladder.

Sketches:
- [`../sketches/w2-v8-tack-look-crimp.svg`](../sketches/w2-v8-tack-look-crimp.svg)
  (schematic stations and the stroke after a tack);
- [`../sketches/w3-v8-shadow-test.svg`](../sketches/w3-v8-shadow-test.svg)
  (end view at the open conductor barrel, from cited dimensions);
- [`../sketches/w3-t-then-c.svg`](../sketches/w3-t-then-c.svg) (station C as
  a one-nest die set between lifted neighbours).

Numbers:
- **[calc: w3_final §n]** [`../calc/w3_final.out.txt`](../calc/w3_final.out.txt);
- **[calc: wave2 §n]** [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
- **[calc: w3htp §n]** [`../calc/w3_on_hand_tool_as_press.out.txt`](../calc/w3_on_hand_tool_as_press.out.txt);
- **[calc: vision_budget §n]** [`../calc/vision_budget.out.txt`](../calc/vision_budget.out.txt);
- **[bm W §n]** borrowed-machines'
  [`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt);
- **[ff w2 §n]** force-and-form's [`wave2.out.txt`](../../force-and-form/calc/wave2.out.txt);
- **[rap P §n]** ribbon-as-pallet's
  [`exchange_on_machine_that_sees.out.txt`](../../ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt);
- **[Prime]** a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
  observed 2026-09-28.

## Picture it

**Where things start.**
- A ribbon end sits in v1's pallet on [v1b](v1b-printer-as-stage.md)'s stage:
  - flush-cut, split 25–35 mm, stripped to the length that suits the contact
    in use (1.6–2.1 mm for clone-drawn kit contacts, 2.4 mm for genuine SXH
    [calc: w3htp §4]), by hand today or by [v6](v6-patient-cell.md)'s stations;
  - fanned to 5 mm pitch, each conductor in its own hinged key;
  - the waiting conductors held 5 mm above the working floor;
  - the far end, unterminated because the XH end is made first, in a push-in
    or pogo block on the station MCU.
- Contacts wait on [v4b](v4b-pocket-plate.md)'s pocket plate (loose from the
  kit, picked by v4's nozzle), on a genuine SXH strip on pilot pins, or on a
  hand-filled plate.

**Station T, the tack.** A printed frame on the bench holds:
- **A nest.** A box slot with a front stop, a lance relief, and a rear shoulder
  bearing on the rear edges of the box's side walls. A hardened steel insert
  (a 3 mm HSS square blank, $9.99 for five [Prime]) sits under the insulation
  barrel, because 33–132 N on ~2.3 mm² is 14–57 MPa, at or above PETG's yield
  [calc: wave2 §5]. A 20 kg bar load cell sits **under the insert**, so it
  reads the forming force only.
- **A former.** A 1.2–1.5 mm steel plate whose lower edge is C's own
  insulation-crimper profile, cut 0.1–0.2 mm wider than that crimper. It
  slides vertically in a guide over the **insulation barrel only**. A DS3235
  35 kg·cm servo ($27.99 [Prime]) on a 1:1 lever pushes it (137–172 N
  [calc: w3_final §2]) to a screw stop set at **C's final insulation height
  plus 0.2–0.5 mm**. The stop carries the servo's excess, not the contact.
- **A top camera straight down** over the conductor barrel and the window
  between the barrels: the 16 MP IMX298 M12 board ($69.99 [Prime]) with a
  12 mm lens ($9.99 [Prime]), ~122 px/mm at 100 mm [calc: vision_budget §2].
  Nothing else stands above that part of the contact. Round it, LEDs lit one
  at a time, two of them at 60–75° elevation on opposite sides.
- **v1's cam 2** across at wing height, under the lifted neighbours, with a
  backlight on the far side. A black shroud round the nest.

**Station C, the heavy crimp,** 20–40 mm along the stage. Which hosts can take
a tacked contact from this pallet is set out under "Station C" below: a
narrow-punch die fed straight from the pallet (hand-tool-as-press's a4c, or
force-and-form's f3 knee with f9's keyed nest), or the SN-2549 as sold with the
ribbon end leaving the pallet (a6c), or, for strip, an applicator, which
becomes [v9](v9-tack-at-the-anvil.md).

**What moves, one conductor.**
1. **A contact goes into T's nest,** by the nozzle from the plate or by the
   strip's index. *Look:* box on its stop, lance standing, wings upright. The
   top camera also measures this contact's box front to conductor-barrel rear
   edge, which C uses.
2. **The stage brings key *k* over the nest.**
   - *Hover look:* the tip and the torn insulation edge. X and Y are predicted
     from the pallet and corrected once or twice from the picture.
   - The plunger presses key *k* down to its hard stop.
   - *Side look:* the bundle in the U, the jacket over the insulation barrel,
     the edge in the window, nothing above the conductor wing tips. Far-end
     continuity to the grounded contact names the conductor.
3. **Tack.** The former comes down at ~1 mm/s to its stop and closes the
   insulation wings around the jacket. The cell under the insert records a
   plateau of wing forming and a rise as the silicone is met.
4. **The look that matters.** Straight down into the still-open conductor
   barrel, each LED in turn. It checks:
   - every strand between the wing tips, none on a tip;
   - no silver on the black shroud outside the contact;
   - the bundle's displaced shadow under each 60–75° LED: a strand lying on the
     floor casts none (below);
   - the brush past the barrel's front, and the insulation edge in the window;
   - the tack closed symmetrically over the jacket.

   Cam 2 checks that nothing rises above the conductor wing tips. The look can
   take as long as it likes; nothing is waiting to move.
5. **Decide.**
   - *Pass:* the plunger releases, the key lifts, and the tacked contact rides
     up on its conductor, the box leaving the slot straight up with the lance
     in its relief. The stage carries it to C.
   - *Fail:* back out (below), then retry with a fresh contact, or ask.
6. **At C.** The host's own sequence: the contact is set down on C's seat or
   slot, one side frame confirms the box seated and the tack where T left it,
   the stroke crimps both barrels and the insulation crimper re-forms the
   tack, and [v5](v5-inspection-booth.md)'s silhouette reads the result with
   the box as its own roll gauge.

**What locates what.**

| At | Contact located by | Conductor located by | Reference for "fixed" |
|---|---|---|---|
| T | The nest: slot, front stop, rear shoulder | The key's groove, then the picture (tip and edge) | T's frame, with fiducials in every frame |
| Between T and C | — | The tack fixes the conductor in the contact: axial position and roll | The pallet |
| C | C's seat or slot, set against C's die by the picture | Carried by the contact | C's lower die holder |

The former's stop sets only the tack height, loose on purpose, so ±0.05–0.1 mm
is enough.

**What drives the crimp and carries its force.**
- T: 33–132 N through the former, the steel insert, the cell and the printed
  frame; the servo's excess into the stop.
- C: 0.8–2.6 kN [xh-facts §4] in C's own frame, to C's own geometric bottom.
- The stage and the keys carry neither.

**How it knows the crimp worked.**
- T's forming curve: no jacket reads low, a jacket off centre reads lopsided
  [estimate].
- T's top-down look with the shadow test, and cam 2.
- C's seat frame, force trace and after-crimp silhouette.
- A proof pull where the contact form allows one (strip tab, or a plate in a
  neck long enough for it).

**What the person does.** Loads pallets, fills the plate or threads the strip,
answers v7's asks, and inserts into housings. With a6c as C, the person also
crimps each tacked contact with the foot.

**Steps it covers:** place the contact on the conductor (key and picture),
hold both together (the tack) and in something that crimps (C's seat), crimp
(C's host), verify (forming curve, straight-down gate, seat frame, after-crimp
silhouette). **What it hands back:** cutting and palleting, splitting and
stripping unless v6 does them, contact supply if the plate is filled by hand,
insertion.

## Where it comes from

A combination of change-the-question's
[c1b](../../change-the-question/ideas/c1b-tack-first.md) (a light stroke closes
the insulation barrels first; the conductor crimp comes later), force-and-form's
[f9](../../force-and-form/ideas/f9-tack-station-feeds-crimp-station.md) (that
tack station feeding a crimp station with a keyed nest), and this view's
[v1](v1-watched-nest.md) (a stage steered by pictures, keys that lower one
conductor while the neighbours wait 5 mm up, the strictest look before the step
that cannot be undone). What this view adds: one conductor at a time; a camera
looking straight down into the open conductor barrel between the tack and the
crimp; a back-out after the tack that costs a contact, not a ribbon end.

## Why a tack changes what the camera can do

- **In [v1](v1-watched-nest.md) the look before the stroke is crowded:**
  oblique, under a raised punch, beside a key and between lifted neighbours.
  At T nothing stands over the conductor barrel. The former covers only the
  insulation barrel and rises vertically behind it.
- **The strictest look moves between a cheap irreversible act and a dear
  one.** The tack is irreversible for the contact, but a loose tack slides off
  the tip and costs only the contact. The conductor crimp costs a ribbon end cut
  back 6–10 mm. The look sits between the two.
- **C does not need to see the lay-in.** Once the tack holds them, nothing
  shifts between conductor and contact. C's look is one frame.
- **The look has time.** Eight lighting states cost seconds [calc: wave2 §4].

## The tack, defined against C's final crimp

**Height.** The tack is set as a height *above C's final insulation crimp
height at the same contact and wire*, H_t = H_f + 0.2–0.5 mm, not as an
absolute figure [calc: w3_final §1]:
- estimates of H_f on this silicone run 2.0–2.3 mm [ff w2 §5] up to
  2.03–2.46 mm with an elliptical section as the upper bound [calc: w3htp §9];
  the tack then sits at 2.2–3.0 mm;
- a fixed 2.3–2.5 mm can land at or under the final height where the crimp is
  narrow, and would then be a crimp, not a tack [bm W §1];
- H_f is measured on C's own sample crimps (micrometer or v5's silhouette);
  [v3](v3-press-that-runs-experiments.md)'s tack arm steps the tack in 0.05 mm
  increments above it.

**Width.** The former is cut **0.1–0.2 mm wider than C's insulation crimper**,
not to its width. The physics [calc: w3_final §1]:
- a closed barrel at the crimper's own width squeezes the 1.7 ±0.1 mm jacket
  sideways by 3–22 %, which force-and-form's thin-layer grip model puts at up to
  ~7 N [ff w2 §5];
- a back-out needs the tack to slide off at ~1.5 N or less;
- 0.1–0.2 mm wider brings the side squeeze to 0–17 % or 0–11 %, and more of
  the grip then comes from the wing tips on the jacket's top, which the stop's
  height sets.

The grip model spans a factor of eight, so the pair of numbers (width offset,
height offset) is found on the bench by pulling tacked contacts off with the
0.1 g scale. What it asks of C: its insulation crimper's mouth takes a tacked
barrel 0.1–0.2 mm wider than itself [assumption: a flared B-crimper entry
does].

**Where the profile comes from.** The insulation section of a spare SN jaw
piece, widened ([a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md)
makes the same choice so the tack and final crimper share a profile family);
a laser-cut plate [c1b]; or, on an applicator, a Revopoint scan of its own
insulation crimper ([v9](v9-tack-at-the-anvil.md)).

## The stroke at C after a tack

With both crimpers on one ram, on clone dimensions [calc: w3_final §1]:
- the conductor wings are met first, with 0.62–0.87 mm of stroke left;
- the insulation crimper meets the tacked barrel with 0.2–0.5 mm left, after
  the conductor wings have curled for 0.12–0.67 mm;
- compaction, the last 0.1–0.2 mm, begins with that retouch or after it.

The jacket is held by the tack through compaction either way. An untacked
stroke on this silicone meets the insulation wings at 0.29–1.40 mm left, before
or after the conductor wings depending on the final height, so neither order is
"the ordinary one" here. Whether a barrel closed loosely and then re-formed ends
up like one formed in one pass is a sectioning question; force-and-form's
[f3b](../../force-and-form/ideas/f3b-two-station-forming.md) has the arms, and
[v9b](v9b-tack-by-hand-on-the-jack-test.md) makes sections on an applicator.

## The look: a shadow, not a focus slice

Sketch: [`../sketches/w3-v8-shadow-test.svg`](../sketches/w3-v8-shadow-test.svg).
- Held by its tacked jacket, the gathered 0.72 mm bundle hovers **0.30–0.52 mm
  above the conductor-barrel floor**, its top 0.98–1.25 mm up against wing
  tips at 1.50–1.60 mm [bm W §2; floors of the two barrels taken as one plane].
  A strand lying on the floor has left the bundle.
- Focus cannot separate that: depth of field is ~0.55–0.76 mm at 122 px/mm and
  ~1.1–1.5 mm at 86 px/mm [bm W §2, estimate].
- An LED at 60–75° elevation throws the bundle's shadow 0.08–0.30 mm aside on
  the floor: 10–36 px at 122 px/mm, 7–26 px at 86 px/mm. The lowest elevations
  that still light the floor past the walls are 53–66° along the axis and
  58–62° across [bm W §2].
- The judge looks for silver with no displaced shadow beside it, under two LEDs
  on opposite sides in turn. Silver outside the outline on black, and anything
  above the wing tips in cam 2, are the other two strand checks.
- **Unproven:** whether tinned strands on a tin floor give a shadow edge a fit
  can find. One photograph of a tacked conductor with two LEDs at ~65°
  settles it.

## The tack's grip window

- **What handling asks** [calc: wave2 §5, estimate]: the contact weighs
  0.043 g; lowering it box-first into a chamfered slot asks under 0.05–0.2 N of
  friction and under 0.05 N·mm of squaring torque.
- **What a tack gives** [ff w2 §5, estimate]: 0.4–3.1 N at 10 % squeeze,
  1.1–9.4 N at 30 %; the jacket never slips in the barrel before the strands
  slip in the jacket.
- **Roll.** 0.4 N of grip resists ~0.34 N·mm at the jacket's radius; the
  parted conductor's own torsion is 0.33–0.58 N·mm/rad [rap P §5]. A light tack
  holds roll unless handling twists the conductor more than ~0.6–1 rad.
- **The window is 0.2–1.5 N**: enough to carry the contact, loose enough to
  slide off.
- **The T-to-C carry** adds a load case: a snag during the carry under C's
  punch is resisted only by the tack. C's seat look exists to catch a contact
  that moved on the way.

## Backing out after a failed look

**The motion.** The contact leaves the conductor forward, off the tip. The
nest's rear shoulder holds the box while the stage draws the conductor back
through the key's grip at 0.4–1.5 N.

**The shoulder** bears on the rear edges of the box's side walls, with the lance
relief carried under it. The lance tip stands 0.24–0.64 mm behind the box and
0.6–0.9 mm below its floor [into-the-housing's [`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt) §1, CJT drawing 2.44 ±0.20 mm; xh-facts §1]. Whether a shoulder fits depends on the neck between
the box and the conductor barrel, which no drawing constrains (summed clone
lengths give −0.7 to +2.0 mm of free gap [rap P §3]; a reading of how the parts
look gives 0.2–0.5 mm [into-the-housing, estimate]). One kit contact under the
camera settles it.

**What the jacket does** [calc: wave2 §5, estimate]. The jacket between the
key's grip and the tack stretches while the tack slides: 0.06–0.3 mm for a
0.4–1.0 N release over 1.5 mm, up to ~1 mm for 1.5 N over 3 mm. Silicone
recovers. The look after the back-out decides: edge back where it was, a fresh
contact on the same strip; edge moved or torn, re-strip that conductor 0.2 mm
or cut back the end.

On strip, the carrier holds the box instead of a shoulder: the tab bends only at
4–12 N of pull along the wire, against a 0.4–1.5 N release [bm W §4]. That is
the back-out [v9](v9-tack-at-the-anvil.md) uses.

## Station C: which hosts fit

The pallet holds the neighbours 5 mm up at 5 mm pitch. That decides which
crimpers can take a tacked contact straight from it [calc: w3htp §3, §7]:

- **Narrow-punch hosts, fed from the pallet.** The punch body must stay under
  **7.45 mm** wide for the first ~5.9 mm above the crimping edge (crimped
  neighbours either side, 0.3 mm clearance).
  - hand-tool-as-press's [a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md):
    an SN-2549 jaw set cut to one nest, 6–7 mm wide, in a die set with an
    eccentric (e 2.0–2.5 mm), a disc stack and a button cell. The tacked
    contact is carried in 1.0–1.7 mm high and set down on a floor ledge; the
    picture sets it against the die along the wire.
  - force-and-form's [f3](../../force-and-form/ideas/f3-knee-micropress.md)
    knee with a narrow punch and f9's keyed nest.
- **The SN-2549 as sold.** Its jaw spans the neighbours' positions at their
  height, so clearing them from the side needs a stand-out of a + 2.7 mm. The
  ribbon end therefore leaves the pallet at C: hand-tool-as-press's
  [a6c](../../hand-tool-as-press/ideas/a6c-flags-by-machine-foot-crimp.md), in
  which the machine tacks every conductor of an end and Derek crimps each
  tacked contact with the foot on a flag seat, or Derek's hand with the tool
  as it is. The contact is already on the wire at the right depth, so today's
  close-one-click-then-feed juggling goes.
  - **Box-first along the wire** (borrowed-machines'
    [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md) on
    edge): the tacked contact enters the open jaws from the wire side and
    travels box-first to a front stop, the lance trailing so it slides over the
    die edges in its folding direction. It uses b2's actuator and spring link
    instead of a nest fed from above. It saves no jaw opening: box plus lance,
    2.8–3.3 mm, must pass either way.
- **An applicator.** A tacked loose contact lowered onto an applicator's anvil
  has nothing to stop it along the wire, and the side-feed track leaves no room
  for a keyed slot. For strip the tack moves to the applicator's own anvil:
  [v9](v9-tack-at-the-anvil.md).

## By hand, first

With no motor: T's nest and former on the bench, the servo replaced by a
push-pull toggle clamp (POWERTEC 305CM pair, $18.25 [Prime]) to the screw
stop; the ELP or the M12 camera looking straight down, two LEDs at ~65°, the
picture on the Mac. Derek lays each conductor in with his fingers, throws the
toggle, looks, then crimps the tacked contact in today's SN-2549. It measures
the tack's grip, height and width, and the shadow test, on kit contacts, before
anything is motorised. hand-tool-as-press's
[a6b](../../hand-tool-as-press/ideas/a6b-flags-by-hand-foot-crimp.md) and
change-the-question's [c6b](../../change-the-question/ideas/c6b-by-hand-this-week.md)
develop the by-hand flow further; this view's addition is the straight-down
look before the squeeze.

## Supply to T, by contact form

| Form | How it reaches T | What changes |
|---|---|---|
| Kit contacts, loose | [v4b](v4b-pocket-plate.md)'s plate, picked from lance-relieved pockets where the contact already lies flat, or a hand-filled plate | The nest's slot and rear shoulder do all the holding |
| SXH strip | On pilot pins as [terminal-supply a2](../../terminal-supply/ideas/a2-strip-indexer.md) holds it; the tack is made with the contact still on its carrier | After a pass a drop-shear cuts the tab and the tack holds the contact on the wire. After a fail the carrier holds the box for the back-out. Fresh contacts wait upstream at one strip pitch (7.1–9.5 mm [xh-facts §1, estimate]) with wings up to 3.2 mm tall, under the neighbours' 4.15 mm underside |
| Contacts on 0.64 mm posts ([terminal-supply a4](../../terminal-supply/ideas/a4-post-held-contacts.md)) | The post holds the box at T | Post grip (0.2–1.6 N, estimated) and tack grip are the same size, so a stripper fork pushes the box off the post; the tack is not asked to |

## Timing and person time

- T side of one conductor 29–81 s [calc: wave2 §5]; C adds its stroke,
  after-look and pull, ~40–80 s. Per conductor 69–161 s; per 53-crimp unit
  **1.0–2.4 h** unattended [calc: w3_final §3].
- With a6c at C, Derek's foot crimps take 9–15 min a unit plus pallet loading
  [calc: w3htp §8].

## Printed and bought

**Printed:** T's frame, former guide, lever and servo mount; the pallet and
keys (v1); the shroud and camera brackets.

**Steel:** the former (1.2–1.5 mm O1 or A2 flat stock, or a spare SN jaw's
insulation section; sourcing request for the flat stock; the SN jaw set
alone is not on Prime, only inside the IWS-0723K kit at $46.59 [Prime]); the
anvil insert (3 mm HSS blank, $9.99 [Prime]); a stop screw with lock nut.

**Bought:**

| Item | Source |
|---|---|
| DS3235 35 kg·cm servo | $27.99 [Prime] |
| 20 kg bar load cell with HX711 | sourcing request; the Prime 5 kg pair ($9.99) tops out at 49 N |
| 16 MP IMX298 M12 camera, 12 mm lens | $69.99, $9.99 [Prime] |
| WS2812B 16-LED rings | $18.99 for five [Prime] |
| POWERTEC 305CM toggle clamps (by-hand version) | $18.25 a pair [Prime] |

## Contribution

- It splits Derek's priority step into its parts: placing the contact on the
  conductor and holding the two together, which is light and watched (T); and
  crimping, which is heavy and needs no camera at the nest (C).
- The camera gets its clearest view at the one moment it matters, and the
  costly irreversible act comes after the look.
- It is a first motorised rung that is useful on its own, and a by-hand rung
  before that.
- It takes loose kit contacts, genuine strip or posts, each with its own
  hand-over.

## Major unresolved problems

- **The tack's grip window on this silicone:** 0.2–1.5 N wanted; the width and
  height offsets that give it are unknown within a factor-of-eight grip model.
  A pliers-and-scale afternoon, or the by-hand T.
- **Whether C's insulation crimper takes a tacked barrel 0.1–0.2 mm wider than
  itself.**
- **Tacked then re-formed, against one pass,** for the insulation crimp:
  sections.
- **The rear shoulder for the back-out** needs a neck gap nobody has measured.
- **The shadow test on tin.** One photograph.
- **The T-to-C carry** rides on a 0.2–1.5 N tack.
- **C hosts:** the narrow-punch hosts are built things (a4c's cut jaw pieces,
  f3's knee); the SN-2549 as sold takes the ribbon off the pallet.

## What rests on assumptions

- Tack forces from xh-facts' insulation estimate, 33–132 N.
- The grip model [ff w2 §5] and the jacket's ±0.1 mm.
- First touches on clone dimensions, without the crimper's mouth flare.
- The two barrel floors in one plane (shadow geometry).
- Handling loads [estimate].
