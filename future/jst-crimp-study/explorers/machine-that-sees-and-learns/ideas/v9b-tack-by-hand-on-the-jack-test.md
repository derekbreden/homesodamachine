# v9b — The tack by hand on the jack-test applicator: lay in, throw a toggle, look, pump

Explorer: machine-that-sees-and-learns. Branch of [v9](v9-tack-at-the-anvil.md).

Sketch: [`../sketches/w3-v9b-by-hand.svg`](../sketches/w3-v9b-by-hand.svg)
(schematic).
Numbers: [`../calc/w3_final.out.txt`](../calc/w3_final.out.txt) §1, §4
(**[calc: w3_final §n]**); borrowed-machines'
[`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt)
(**[bm W §n]**); this view's [`wave2.out.txt`](../calc/wave2.out.txt)
(**[calc: wave2 §n]**); force-and-form's
[`wave2.out.txt`](../../force-and-form/calc/wave2.out.txt) (**[ff w2 §n]**);
[`xh-facts.md`](../../../context/xh-facts.md). **[Prime]** rows are in
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.

## Picture it

**Where things start.**
- **The press.** An OTP side-feed XH applicator sits on the bed of the idle
  VEVOR 12-ton H-frame press [repo: tools.md], feed cam in **pre-feed**, a
  reel threaded through it. A printed T-slot adapter on the bottle jack's ram
  captures the applicator's ram head. A hard-stop collar on the adapter lands
  on the applicator frame and sets the bottom of the stroke [b1b, estimate].
  A contact waits open on the anvil, still on its carrier.
- **The tack former.** A 1.2–1.5 mm steel plate whose lower edge is the
  applicator's insulation-crimper profile (scanned with the Revopoint, cut
  0.1–0.2 mm wider), in a short printed-and-steel guide doweled to the
  applicator base on the downstream side. A POWERTEC 305CM push-pull toggle
  clamp ($18.25 a pair, 500 lb hold [Prime]) drives it down to a screw stop
  set at the tack height.
- **The look.** The ELP camera on hand [repo], with a close-up lens (NEEWER
  15× clip-on, $24.99 [Prime]; fit over the ELP's lens unverified) or the
  16 MP M12 camera, looks horizontally into a 10 mm first-surface mirror on a
  hinged arm that swings in over the conductor barrel. Two LEDs at 60–75°
  elevation on opposite sides of the barrel, and a backlight across the anvil.
  The live picture is on the Mac.
- **The ribbon end.** Split, stripped to the reel contact's strip length, held
  in Derek's hand or in a simple printed clamp with the other conductors
  folded back out of the way. Optionally the far end in a Wago 221-415 lever
  block ($28.00 for 25 [Prime]) with a buzzer or LED wired to the applicator
  body, as a continuity light.

**What moves, one conductor.**
1. Derek lays the stripped conductor into the waiting contact by hand, jacket
   in the insulation barrel, and holds it there with a fingertip or a light
   printed foot.
2. **Tack.** He throws the toggle. The former closes the insulation wings over
   the jacket to its stop, reacting on the applicator's insulation anvil. He
   releases the toggle and lets go of the wire.
3. **Look.** He swings the mirror in. On the screen: the open conductor barrel
   from straight above, each LED in turn. Every strand between the wing tips,
   the brush past the barrel's front, the insulation edge in the window, and
   the bundle's shadow displaced beside it under each LED. A strand lying on
   the floor has no shadow.
4. **Decide.**
   - Good: swing the mirror out and pump the jack until the collar lands. Both
     barrels are crimped and the tab is sheared. Release the valve; the
     applicator returns and its pre-feed brings the next contact.
   - Bad: draw the conductor straight back out along its axis, flat. The
     carrier holds the box against a 0.4–1.5 N release; the tab bends only at
     4–12 N of pull along the wire, but at 0.5–1.7 N sideways [bm W §4]. Pump
     the empty tacked contact through as a scrap stroke and pick it off the
     anvil with tweezers.
5. Lift the crimp out, glance at it, and go to the next conductor.

**What locates what.** The reference for "fixed" is the applicator base.
- The contact: the applicator's strip track, terminal stop and feed finger.
- The conductor: Derek's fingers until the tack; the tack after it.
- The former: its guide, doweled to the applicator base, in line with the
  insulation crimper. The screw stop sets the tack height.
- Crimp height: the applicator's dial and the collar.

**What drives the crimp and carries its force.** The bottle jack, pumped by
hand, through the adapter and the applicator's own crimpers to the collar; the
12-ton frame carries 0.8–2.6 kN [xh-facts §4] without noticing. The toggle
carries the tack's 33–132 N [calc: wave2 §5] into the insulation anvil.

**How it knows it worked.** The straight-down look, by Derek on the screen
(or logged by [v7](v7-the-run.md)'s capture app and judged later); the
continuity light if wired; a glance at the crimp. No force trace unless the
applicator's ram carries strain gauges (BF350, $6.99 [Prime]) read by an HX711.

**What the person does.** Everything that moves. The contact never has to be
juggled: it waits in the die, and the conductor goes into it under a picture.

**Steps it covers:** supply contacts (the reel, advanced by the stroke),
place the contact on the conductor (by hand, into a contact the die holds),
hold both (the tack), crimp (the applicator), verify by the look.
**What it hands back:** all motion, splitting and stripping, insertion.

**Time** [calc: w3_final §4, estimate]:
- per crimp 31–93 s, of which pumping a 30 mm stroke is 10–60 pump strokes
  (8–60 s) [assumption: a 12 t jack moves its ram 0.5–3 mm per pump stroke];
- 27–82 attended minutes a 53-crimp unit, against ~22 minutes of crimping by
  hand today [hand-tool-as-press wave2 §9].

It is slower than today. Its use is the first week.

## What it changes from v9

Every motor goes. The crank is borrowed-machines'
[b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)
stage 0, the jack test: the shop press's own bottle jack strokes the
applicator. The T-arm's servo becomes a push-pull toggle clamp. The fork and
foot become Derek's fingers. The camera and the look stay. Proposed as A0 in
borrowed-machines'
[exchange on this view](../../../exchange/borrowed-machines--on--machine-that-sees-and-learns-w3.md).

## What it is for

**A crimper that stops the juggling.** Today the contact is held one ratchet
click into the SN-2549 while the wire is fed, with no locator [repo]. Here the
contact waits in the die at its datum and the conductor goes into it under a
look.

**A measuring bench for v9, v8 and b1b**, on the production applicator and
reel:
- **The tack's grip on this silicone.** Tack three contacts at each of a few
  stop heights, pull each off with a hook and the 0.1 g scale. What stop and
  width give 0.2–1.5 N without marking the jacket? That settles v8's and v9's
  first open problem.
- **Tack height against the final height.** Crimp a few untacked, measure the
  insulation height H_f with the Shars point micrometer ($61.95 [Prime]) or v5's
  silhouette, then set the tack at H_f + 0.2–0.5 [calc: w3_final §1].
- **Order and re-form.** Section a tacked-then-crimped contact beside a
  one-pass one (force-and-form's
  [f3b](../../force-and-form/ideas/f3b-two-station-forming.md) method).
- **Room.** With the jack retracted: what hangs below the crimper faces, and
  whether the former's guide (~17 mm) and the mirror (~11 mm) fit under them
  [bm W §3]. That is v9's first open problem.
- **The mouth.** Whether the insulation crimper takes a tacked barrel
  0.1–0.2 mm wider than itself.
- **The shadow test.** Whether a strand on the floor loses its shadow on tin.
- **b1b's own list:** feed-finger timing, shut height, the upstream pressure
  plate's height, genuine against clone strip through one die.

## The pump

A hand-pumped jack's ram moves coarsely per stroke near bottom, so the collar,
not the pump, sets the bottom [b1b; estimate].

**Branch: air over hydraulics.** The BIG RED TA91206 12 t air-over-hydraulic
bottle jack ($136.04 [Prime]; air input 100–175 psi and a manual pump) on the
compressor on hand [repo] turns pumping into holding a valve.
- Whether it fits the VEVOR press's jack mount, and how its lift range suits
  the applicator's height, are unchecked [assumption].
- It is still motorless in the sense Derek's bench means: no controller.

## Printed, steel, bought

- **Printed:** the T-slot adapter (b1b), the former guide body, the mirror arm,
  the LED holder, the wire clamp, the camera bracket.
- **Steel:** the former (1.2–1.5 mm O1 or A2 ground flat stock; sourcing
  request); the stop collar; dowel pins ($6.49 [Prime]); the guide's
  wear strips.
- **Bought:**

| Item | Source |
|---|---|
| OTP side-feed XH applicator and a reel | Not on Prime; eBay or Made-in-China |
| POWERTEC 305CM toggle clamps (pair) | $18.25 [Prime]; plunger stroke not stated on the page |
| First-surface mirror 100 × 100 mm | $20.90 [Prime] |
| NEEWER 15× clip-on macro lens | $24.99 [Prime] |
| Wago 221-415 (continuity light) | $28.00 for 25 [Prime] |
| Shars point micrometer | $61.95 [Prime] |
| Optional: BIG RED TA91206 air-over-hydraulic jack | $136.04 [Prime] |

## Major unresolved problems

- **The applicator itself.** It is not on Prime. Lead time, which contact its
  die is cut for, and its interface (shut height, stroke, ram head) come with
  the part [b1b].
- **The toggle's stroke and force at the former.** The 305CM's plunger stroke
  is not stated; the 500 lb hold rating is far above a tack, so the stop, not
  the clamp, sets the tack.
- **Holding a split conductor in the U by hand** while the other hand throws
  the toggle. A light printed foot on a spring may be needed.
- **Hands near a press.** Slow, and the jack is pumped by the person's own
  hand, but a guard over the crimper faces belongs on it.
- **Everything v9 leaves open** about the tack's grip, the width, the mouth and
  the shadow on tin, which this bench exists to answer.

## What rests on assumptions

- Jack ram travel per pump stroke, 0.5–3 mm.
- That the applicator runs at hand-pump speed [b1b's assumption].
- The air-over-hydraulic jack fitting the press.
- The grip model [ff w2 §5].
