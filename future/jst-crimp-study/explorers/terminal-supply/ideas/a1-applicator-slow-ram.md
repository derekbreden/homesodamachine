# a1 — A stock side-feed applicator, driven by a slow screw ram

Sketch: [`../sketches/a1-applicator-slow-ram.svg`](../sketches/a1-applicator-slow-ram.svg) (schematic).
Numbers: [`../calc/terminal_supply.py`](../calc/terminal_supply.py), output beside it,
cited as [ts §n].

**Related.** The same bought module sits at the centre of borrowed-machines
[b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md),
[b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md),
[b1c](../../borrowed-machines/ideas/b1c-one-shaft-applicator-press.md) and
[b8](../../borrowed-machines/ideas/b8-spool-fed-borrowed-line.md),
force-and-form [f2](../../force-and-form/ideas/f2-crank-press-for-an-applicator.md)
and [f2b](../../force-and-form/ideas/f2b-arbor-press-with-a-hard-stop.md), and
ribbon-as-pallet [a1](../../ribbon-as-pallet/ideas/a1-pallet-tour.md). Their files
develop the presses and the wire presenters around it. What changes if the
contact supply changes is in [a7](a7-if-the-contacts-switch-to-strip.md).
[a2](a2-strip-indexer.md) takes the same functions apart into separate slow
stations.

## Picture it

- **Where things start.** A reel of XH contacts on their carrier strip hangs on
  a printed arm beside a small press. The strip threads into the side of a stock
  side-feed "XH2.54" applicator: the OTP-style mould sold for Chinese 1.5–2 t
  terminal presses, or JST's own MKS-L. The ribbon's end has already been
  splayed and stripped, and waits in a ribbon carriage in front of the
  applicator.
- **At rest.** The applicator's pre-feed has already put the next contact on
  the anvil, open, barrels up. Its feed finger sits in that contact's pilot
  hole. Two guide plates hold the strip so it has "no movement front to back",
  and a sprung pressure plate stops it sliding back [mfr: JST MKS-L manual §2,
  §6-6, §6-7].
- **What moves.**
  - The carriage slides conductor k along the contact's axis, over the carrier,
    into the open barrels. Its first stop is a taught position; the camera then
    steers it until the insulation edge sits in the window between the barrels.
  - Every other conductor is parked out of the tooling plane, as in
    borrowed-machines b1 (folded back at the split root). The applicator's own
    feed track holds fresh contacts upstream at strip pitch, so they must not
    land there.
  - A stepper then drives the applicator's ram down through its 30–40 mm stroke
    in about half a minute. One stroke:
    - closes both barrels;
    - parts the tab with the floating shear, which pushes the carrier down,
      away from the wire;
    - keeps the crimped contact from lifting with the punch (stripper plate);
    - on the way up, advances the strip one pitch (cam feed).
- **What locates what.**
  - The applicator's feed finger, guide plates and pressure plate locate the
    contact against its anvils.
  - The applicator's dials set crimp height, provided the ram reaches the same
    bottom every stroke.
  - The conductor is placed by its own insulation edge as the camera sees it,
    not by a wire stop at its tip.
  - **The reference for "fixed" is the applicator's base plate**: its anvils and
    the hard-stop face sit on it. The frame around it only pushes.
- **What drives and carries the crimp force.** A slow drive pushes the ram
  through a preloaded disc-spring stack onto a hard stop on the applicator's
  own base. The 0.8–2.6 kN crimp closes through the applicator; the stop sets
  the bottom; the springs cap the force if the drive overruns. The frame opens
  to the applicator's shut height plus its stroke, 166–176 mm for an OTP
  mini-applicator [force-and-form f2b]. Frames that fit:
  - a NEMA 23 and a ball screw in a laser-cut steel O-frame;
  - a slow crank in the idle VEVOR 12-ton press frame, bottom dead centre set by
    the rod length (borrowed-machines b1b);
  - a built crank press turning at ~2 rpm (force-and-form f2);
  - a taller 2–3 t arbor press, whose opening is unverified.

  1-ton arbor presses do not open far enough: Harbor Freight 59766 opens
  139.7 mm [source, via force-and-form f2b], and the VEVOR AP-1 150 mm
  [sourcing/amazon-prime.md, observed 2026-09-28]. Both fit a knife-set die
  block ([a2](a2-strip-indexer.md)).
- **How it knows it worked.**
  - The camera looks at the waiting contact before the wire arrives, from the
    front and above: present, straight, not bent up.
  - The stripped tip is checked alone on a backlight before the carriage
    enters.
  - The ram lands on its stop (a switch in the spring stack), with a force trace.
  - The crimp is photographed after the carriage lifts it out: brush, window,
    bend.
- **What the person does.**
  - Mounts a reel once. An 8,000-piece reel covers about 150 units, the whole
    program [ts §1].
  - Empties the scrap cup.
  - Splays and strips, and folds the parked conductors, unless other stations
    or the carriage do.
  - Inserts into the housing, unless another station does.

## The mechanism, from the supply side

- **Why a stock applicator.** It is the industry's finished answer to "place
  the contact on the conductor, hold both, crimp", packaged as a module that
  needs only a vertical push. Mini-applicators weigh about 4 kg; JST's MKS-L is
  6.4 kg with a 30 mm maximum feed [prior-art §3; mfr MKS-L §2].
- **Nothing in the stroke depends on speed.**
  - The pre-feed cam, the pressure plate's drag, the shear and the crimp are all
    quasi-static. At 30 s per stroke instead of 0.4 s they do the same thing.
  - Copper's flow stress is 5–8 % lower at crawl speed, and there is no inertia
    at the bottom [force-and-form, source cited there].
  - The feed follows the ram at any speed, so a stepper that stalls halfway
    leaves the feed halfway, not mis-indexed.
- **Pre-feed plus dwell.** The contact sits exposed on the anvil for as long as
  the machine wants before the wire comes, which is when the camera checks it.
- **Crimp height rides on the bottom of the stroke.** The dials change crimp
  height about 0.05 mm per graduation, and the manual says to adjust the dials,
  not the press [mfr MKS-L §5]. The slow ram must reach the same bottom every
  time to about ±0.02 mm.
  - The ram adapter lands on a face on the applicator's own base, so the
    frame's stretch under 2–3 kN is outside the loop.
  - The disc-spring stack between the screw nut and the ram adapter lets the
    drive overrun the stop by a millimetre without raising the force much, and a
    switch trips when the stack compresses. The stepper's position then does not
    matter.
  - The stop can sit on a stepper-driven wedge (machine-that-sees-and-learns
    [v3](../../machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)).
    The machine then sweeps the bottom in 0.02 mm steps on this ribbon, finer
    than a dial graduation, photographs and pulls each test crimp, and finds the
    window on the production die itself.
- **Force.** The crimp needs about 0.8–2.6 kN, plus 50–160 N to shear the tab
  [xh-facts §4]. On a crank, the applicator's return springs, not the crimp, set
  the motor size (borrowed-machines b1b: 3.8 N·m for the crimp, up to 5.4 N·m
  for the springs mid-stroke).
- **Strip path and scrap.** The reel feeds the applicator from the side. The
  MKS-L chops the cut-off carrier into pieces under a scrap cover [mfr MKS-L
  §6-12-3]; other applicators pass the empty carrier out whole. A unit leaves
  about 1.5 g and 0.38 m of carrier [ts §3].
- **Refill and cost.** An 8,000-piece JST reel covers ~151 units, a 9,000-piece
  clone reel ~170. Contacts cost $0.42–0.67 per unit at LCSC reel or strip
  prices [ts §1; prices xh-facts §6].

## Lines of sight inside an applicator

- **What a look can reach.** At top dead centre the crimpers are 30–40 mm above
  the anvil, so a front-oblique look at the waiting contact is available: the
  contact is present, the insulation edge is in the window.
- **What it may not reach.** Along the strip at wing height stand the next
  contact, the feed finger, the strip guides and, downstream, the shear.
  Whether any line across the anvil at wing height reaches a backlight is not
  shown in any public drawing.
- **Consequence.** A strand riding a wing tip may show only after the crimp. The
  strand check moves upstream: the stripped tip alone on a backlight before the
  carriage enters.
- **Settled on arrival.** A photograph of the applicator from the side at anvil
  height shows whether a vane or backlight can reach the gap.

## Problems and repairs

1. **A screw drive's bottom position wanders with frame stretch and backlash.**
   Repair: the hard stop local to the applicator and the preloaded spring stack,
   so the actuator only has to overrun. The stop face's wear and the
   applicator's own ram play remain; the applicator already tolerates both in a
   2 t press.
2. **The cheapest presses are too short.** Repair: one of the frames above.
3. **Which contact the die fits.** An "XH2.54" OTP die is presumably cut for
   clone-sized contacts [assumption]. Clone insulation barrels are drawn
   2.46–3.0 mm open against JST's 1.95 × 2.4 envelope [xh-facts §1], so genuine
   SXH may crimp differently in it. Buying the vendor's clone reel (under a cent
   a contact) is one answer; one crimp of each supply in the same die, with the
   swept stop, settles it. [a7](a7-if-the-contacts-switch-to-strip.md) sets out
   what else follows from the choice.
4. **The applicator expects a hand to hold the wire.** The ribbon carriage
   stands in for the hand, approaching over the carrier from the side a person
   would. The other conductors are parked out of the tooling plane; otherwise
   they meet the guide plates, the ram and the fresh contacts in the feed track.
   borrowed-machines b1 puts the fold at the split root, which sets an 8–15 mm
   split.
5. **The operator's wire stop is where the tip lands.** On torn silicone the
   insulation edge then lands wherever the tear put it, ±0.2 mm or so
   [estimate]. With a camera, the carriage references the insulation edge
   instead, or splits the error between brush and window.

## Steps covered, and what it hands back

- **Covers:** refilling from a reel; placing the contact (the pre-feed);
  holding it (feed finger, guides, pressure plate, crimpers); crimping;
  separating it from the carrier; verifying before and after the stroke.
- **Hands back:** splaying and stripping; presenting each conductor, which
  needs a ribbon carriage (a two-axis slide with a fork, after the JCW-2TE in
  prior-art) and a way to park the other conductors; insertion.
- **Carries on into:** any insertion station. The crimped contact leaves on its
  conductor in a known pose, lifted out by the carriage.

## Printed and bought

| Part | Printed / bought | Evidence |
|---|---|---|
| Side-feed XH applicator | bought | eBay OTP XH applicator ~US$150–167 + ~$80–91 shipping [prior-art §4; force-and-form, borrowed-machines, source]; no Prime listing found 2026-09-28 [sourcing/amazon-prime.md]. JST APLMK SXH001-06 $3,439.52, 0 stock [xh-facts §2] |
| Contacts on reel | bought | SXH-001T-P0.6 reel, Digi-Key 1,329,000 in stock, $0.0235 @ 8k; CJT A2501-TP clone at LCSC, 665,523 at $0.0079 [xh-facts §6] |
| Frame and drive | built or borrowed | Steel O-frame with NEMA 23 and an SFU1605 ball-screw kit (CHUANGNENG, BK12/BF12, $41.59, Prime [sourcing/amazon-prime.md]); or b1b's crank in the VEVOR 12-ton frame with Derek's NEMA 23 and DM542T [repo tools.md]; or f2's crank press |
| Hard stop, ram adapter, disc-spring stack, stepper wedge | steel stop and springs bought; adapter machined, or printed PET-CF with a steel face | The Prime pass found only a light stainless Belleville assortment (Hilitchi, $14.99); a heavy DIN 2093 35.5 mm series is in [`../sourcing-requests.md`](../sourcing-requests.md) #27 |
| Reel arm, scrap cup, camera bracket, ribbon carriage, fold-back parking | printed | — |
| Force trace | a 5 t compression cell with indicator (Prime, $129, thin listing [sourcing/amazon-prime.md]) under the applicator plate, or strain gauges on the ram adapter | — |

## Contribution

The route in which the whole "place, hold, crimp, sever" problem is solved by a
mass-market part, and the only new work is a slow, stiff push, a hard stop and a
wire presenter. It is also the benchmark every printed arrangement in the study
separates into stations.

## Major unresolved problems

- **The applicator's die on this wire.** Whether the "XH2.54" OTP crimpers and
  anvils give a JST-like crimp height on 60 × 0.08 mm strands, and whether the
  insulation crimper closes on 1.7 mm silicone without cutting it. 1.7 mm is
  near the top of XH's 0.9–1.9 mm range.
- **Which contact the die is cut for,** and how genuine SXH crimps in it.
- **Shut height and ram interface** of the OTP applicator. The mini-applicator
  standard is 135.8 mm [prior-art §3]; JST MKS-L is 160 mm [mfr]. Measured on
  arrival.
- **Feed pitch.** Adjustable on the applicator, but the reel's pitch is
  unconfirmed: the Würth 2.5 mm analog is 7.10 mm, and the clone drawings scale
  to ~7.0 and ~8.5 [ts §2].
- **Wire presentation** into a die surrounded by guide plates and a stripper,
  with the other conductors parked.
- **Lines of sight** at wing height inside the applicator.
- **Lead time.** eBay or AliExpress shipping from China, days to weeks.

## What each conclusion rests on

- **Derek:** slowness is acceptable; the study's volume (about 3,200 crimps)
  [brief].
- **Facts [mfr, source]:** MKS-L feed, guide plates, pressure plate, dial
  graduation and scrap cover [mfr MKS-L]; clone and genuine envelopes, reel
  prices and stock [xh-facts]; arbor press openings [source, Prime listing].
- **Calculations [calc]:** reel coverage and cost per unit [ts §1]; carrier mass
  and length per unit [ts §3].
- **Estimates:** crimp force 0.8–2.6 kN and tab shear 50–160 N [xh-facts calc
  C1]; speed independence of the feed and crimp (with force-and-form's
  strain-rate source); ±0.2 mm tear scatter.
- **Assumptions:** the OTP applicator has a mechanical cam feed like the
  WERI/JST designs (listings say "side feeding"); the OTP die is cut for clone
  contacts.
