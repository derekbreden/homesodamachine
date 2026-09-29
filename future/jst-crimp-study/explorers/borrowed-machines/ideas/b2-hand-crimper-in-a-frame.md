# b2 — The ratchet hand crimper in a frame, closed by an actuator, fed from the strip

The mass-produced thing here is the $22 ratchet crimper already on the bench:
the iCrimp SN-2549 with its XH nest. It has everything a press has except a
contact feed, a locator and a hand to close it. Tri-Star's CrimpXpress sells
exactly "loads loose contacts into an ordinary hand crimp tool" for aerospace
contacts [prior-art §3]. This idea does that for XH from the carrier strip: a
pawl feeds the strip, a steel edge shears the tab, a post in the contact's box
carries it into the tool, and a slow actuator closes the tool through a spring
link.

**Related:** [b2b](b2b-pedal-less-hand-station.md) is the person-facing
combination built on this frame. terminal-supply's
[x1](../../terminal-supply/ideas/x1-post-feeds-the-hand-tool.md) puts the same
post head on loose kit contacts from a pocket plate, and its
[a6](../../terminal-supply/ideas/a6-post-is-the-gripper.md) is where the post as
a gripper comes from. hand-tool-as-press's
[a1 squeezer cradle](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md) and
force-and-form's [f1](../../force-and-form/ideas/f1-motorised-ratchet-crimper.md)
are the same cradle from their sides.

Sketch: [`../sketches/b2-hand-crimper-frame.svg`](../sketches/b2-hand-crimper-frame.svg).

Labels: [calc presses §n], [calc geometry §n], [calc wave3 §n] are this
explorer's [`presses.out.txt`](../calc/presses.out.txt),
[`geometry.out.txt`](../calc/geometry.out.txt) and [`wave3.out.txt`](../calc/wave3.out.txt);
[TS §n] is terminal-supply's
[`w3_on_borrowed.out.txt`](../../terminal-supply/calc/w3_on_borrowed.out.txt) and
[TS wave2 §n] their [`wave2.out.txt`](../../terminal-supply/calc/wave2.out.txt);
[procedure calc §n] is procedure-is-the-machine's
[`exchange_borrowed.out.txt`](../../procedure-is-the-machine/calc/exchange_borrowed.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it

**Where things start.** A second SN-2549 ($22.29 [Prime]), dedicated to the
machine, stands on edge on an aluminium base plate:
- its jaws lie in a vertical plane across the wire axis (X);
- its fixed handle is clamped in a printed saddle;
- a 12 V linear actuator is pinned to its moving handle **through a spring
  link** (below).

In front of the jaws (the box side, +X):
- **Strip track.** A steel-lined track runs across the tool (along Y) a few
  millimetres in front of the jaw face. A cut strip of SXH contacts lies in it,
  barrels toward the jaws, so the carrier (joined at each contact's rear) lies
  nearest the jaws.
- **Pawl feed.** A pawl on a flat run of the track pushes the strip one pitch
  per cycle, the applicator's own feed-finger principle. A tapered pin then
  enters a neighbouring pilot hole, so the lead contact's position does not
  depend on the pawl's backlash or the carrier's pitch error.
- **Shear.** At the station the lead contact's insulation barrel rests on a
  steel land whose edge is at the tab root. The carrier beside it lies on a
  **drop section** hinged 2–3 mm upstream of the station tab, which a DS3218
  servo ($14.99 [Prime]) on a 3–4:1 lever pushes down ~1.5 mm.
- **Post head.** A 0.64 mm square header pin in a floating holder on a small X
  slide with a Z lift, with a stripper sleeve around it (the post head of
  terminal-supply's a6).
- **Flap blade.** A 0.3–0.4 mm feeler-gauge leaf (Hotop set, $8.99 [Prime]) on a
  servo flap that drops into the neck between the conductor barrel and the box,
  as the WC-110's flap locator does.
- **Camera.** The ELP camera looks at the jaw face from below and in front, and
  at the post against a backlight.

Behind the jaws (the wire side, −X): a printed funnel on the tool, facing the
conductor.

**One contact.**
1. The pawl advances the strip; the tapered pin seats.
2. The post comes in along −X into the lead contact's box until the holder's
   face meets the box front.
3. **Shear.** The drop section pushes the carrier down. The tab shears against
   the steel edge at its root. The shear force, 48–158 N [facts C1], is reacted
   by the steel land under the insulation barrel, with no lever arm through the
   contact's neck; the post only keeps the contact down.
4. **Measure.** The camera takes the contact's silhouette on the post: the
   distance from the holder face (box front) to the conductor barrel's rear
   edge, and roll [TS wave2 §5].
5. **Place.** The post carries the contact −X over the dropped carrier,
   **barrels first**, into the gap between the open dies, stopping where the
   conductor barrel's rear edge meets a fiducial on the jaw's front face plus
   the offset just measured. The box and holder stay outside the front face.
   Nothing comes down from above, where the upper die is.
6. **Captive.** The actuator closes the handles to the first ratchet click,
   the one-click close a person uses by hand. The holder's float lets the
   closing dies centre the barrels.
7. The flap blade drops into the neck behind the box. The stripper sleeve holds
   the box front while the post draws back.
8. The conductor arrives along the wire axis through the funnel until its
   strands touch the blade. It is presented by the person
   ([b2b](b2b-pedal-less-hand-station.md)) or by b1's shuttle and band.
9. The actuator closes the handles fully; the dies bottom.
10. The actuator reverses, the flap lifts, and the crimped conductor is drawn
    out.
11. The drop section returns up. The carrier's kink from the drop lies at the
    hinge line, which the next index carries downstream of the new station tab,
    into scrap [TS wave2 §9]. The scrap carrier leaves the track's far end as a
    staircase of small steps into a bin.

**What locates what; the reference for "fixed."** Everything is the tool body.

| What | Set by | Reference |
|---|---|---|
| Strip along the track | tapered pin in a pilot hole | track, bolted to the base plate |
| Tab cut line | the steel land's edge, relative to the contact's rear | track |
| Contact across and up-down | the lower die nest; the captive click finishes the seating | tool body |
| Contact along the axis | post holder face on the box front, the silhouette offset, the jaw-face fiducial; held by the captive click and then the flap blade | tool body (via the camera) |
| Brush | the flap blade in the neck stops the strands | tool body |
| Conductor lateral | the funnel, bolted to the tool | tool body |
| Crimp height | the fixed dies, if they bottom face to face | tool body |

Whether the SN-2549's XH nest lets the box through its front face or stops it
is unknown. The contact's own open conductor barrel is 1.68–1.90 mm wide on
clone drawings and the box 1.85–1.95 mm [facts §1], but the nest's width is a
property of the tool, and only a look at the tool settles it (terminal-supply's
x1 asks the same). The post's stop does not depend on it.

**What drives the crimp and carries its force.** The tool's own compound
leverage, closed by the actuator through the spring link.
- **Handle force.** 40–325 N for a 0.8–2.6 kN crimp at a handle-to-die ratio of
  8–20. The SN-2549's ratio is unmeasured [calc presses §4].
- **The spring link.** An actuator stalled at 1,500–2,000 N would put 12–40 kN
  through the tool's pivots once the dies bottom, 5–7× a hand's force
  [procedure calc §4]. A spring link between the actuator's clevis and the
  handle, preloaded to ~1.25× the largest handle force the crimp needs (~160 N
  at a ratio of 20, ~410 N at 8), caps the die force near 3.2 kN. A microswitch
  on the link's travel says "tool closed" by force.
- **Bottom.** If the dies bottom face to face, the tool sets bottom dead centre
  and the spring link only limits force.

**How it knows it worked.**
- The contact's silhouette on the post before it goes in.
- **Camera before closing:** contact at its place, strands at the blade,
  insulation edge between the barrels.
- **Camera after:** the brush and the closed wings.
- **Spring-link switch:** the close reached force. The actuator's position at
  that moment is repeatable when the dies bottom, so a missing wire, a doubled
  contact or a jam shows as a different end position.
- **Crimp height** by micrometer on sample crimps.

**What the person does.**
- **Hand-presented** ([b2b](b2b-pedal-less-hand-station.md)): holds the ribbon
  and pokes each stripped conductor into the funnel. They never touch a contact.
- **Shuttle-presented:** loads cassettes as in b1.
- **Both:** loads strips into the track, measures samples, inserts into
  housings.

## Steps it covers and what it hands back

- **Covers:** supply contacts (strip feed and tab cut), place the contact
  (post head, captive click, flap blade), crimp (hand-tool dies through a spring
  link), verify the crimp (silhouette, pictures, spring-link switch and end
  position).
- **Hands back:** presenting each conductor (by hand, or by b1's shuttle and
  band), splitting and stripping unless b6 or b7 are added, loading strips,
  sampling crimp height, inserting into housings.

## Why the hand tool and not a press

- **Size and cost.** Small, quiet, $22, and already proven on this bench for XH.
- **Guarding.** The actuator moves at a few mm/s, so the hazard is a slow
  pinch, not a 2 t stroke.
- **The captive click.** Closing one click to trap the contact is what a machine
  needs so the post can let go before the wire arrives.
- **What it lacks.** No crimp-height adjustment and no locator. JST calls even
  its own hand tools "prototype and repair tools" with fixed dies [facts §2].
  The machine adds the locator; crimp height is left to the dies.

## Closing drives

| Drive | Thrust | Speed and position | Fits |
|---|---:|---|---|
| Justech 12 V, 50 mm stroke, limit switches, self-locking, $29.99 [Prime] (230 ratings) | 1,500 N | 7 mm/s loaded, so ~5.7 s to close or open over ~40 mm of handle travel [calc wave3 §6]; **no feedback**: an AS5600 on the handle pivot ($7.99 [Prime]) finds the captive click | carries the spring link at any ratio |
| Progressive Automations PA-01-POT, $155.39 [Prime] (no ratings) | ~750 N | built-in potentiometer; speed not on the page | carries the link at any ratio |
| NEMA 17 with integrated Tr8×2 screw (Iverntech, $27.99 [Prime]) | ~280–380 N | ~5 s over 40 mm [estimate]; position from step count | carries the link only if the tool's ratio is ≥ ~10 [calc wave3 §6] |

## Branches inside this idea

- **Tool choice.**
  - **SN-2549** ($22.29 [Prime]): multi-nest jaws; the XH nest has no locator
    [repo].
  - **iCrimp IWS-0723K** interchangeable-die set with a 2549 die ($46.59,
    [Prime], thin): a second 2549 die in a different frame. Whether the die
    carries its own pivot is not stated.
  - **JST WC-110:** $536.51 at Digi-Key, 147 in stock [facts §2]; no Prime
    listing. JST's own dies for SXH-001T-P0.6 and 22 AWG, with a flap locator and
    wire stop, and a spare locator WC-110P at $51.23. The machine operates the
    flap instead of adding a blade.
  - **Engineer PA-09:** $38.99, genuine, next day [Prime]. A non-ratchet plier
    that crimps the conductor and insulation barrels in separate squeezes [facts
    §2]: two strokes and a second placement.
- **Contact source.**
  - **From the strip** (above): SXH cut strip, Digi-Key 100 / 500 / 1,000 lots
    [facts §6], or a clone reel.
  - **The strip as the locator, not cut first** (terminal-supply's
    [a2c](../../terminal-supply/ideas/a2c-strip-locator-for-hand-tool.md)): the
    lead contact is pushed into the nest with its carrier on, a sprung pin in
    the pilot hole fixes it, and the carrier is bent off after the crimp. It
    removes the post head and the shear, if the jaws clear the carrier.
  - **Loose kit contacts**, picked by the same post head from a pocket plate
    (terminal-supply's x1), or dropped into a keyed flap (force-and-form f1).

## References and tolerances

| Quantity | Needed | Provided by |
|---|---|---|
| Contact across and up-down in the nest | die clearance, ~0.1–0.2 mm [estimate] | die nest; the captive click finishes the seating |
| Contact along the axis | barrels centred in their dies, ~±0.1 mm [hand-tool-as-press calc §7] | post holder face plus the silhouette offset against a fiducial on the jaw face; the post is placed by a stepper to ~±0.02–0.05 mm [TS wave2 §5] |
| Tab stub | about one stock thickness, 0.2–0.3 mm [facts §1] | the steel edge's position relative to the contact's rear, set from one measured strip |
| Conductor depth | strands to the blade, brush set | flap blade in the neck |
| Conductor lateral | 0.72 mm strands into a partly closed barrel funnel | printed funnel on the tool |
| Die force | ~3 kN cap | spring-link preload × tool ratio |
| Crimp height | JST's value ±0.05 | fixed dies (not adjustable) |

## Printed and bought

- **Printed.** Saddle and actuator clevis; spring-link housing; track body
  (steel land and edge inserted); drop section and its lever; post holder,
  slide and sleeve; flap; funnel; camera and backlight mount.
- **Bought.** A second SN-2549; an actuator (table above); compression springs
  for the link and a microswitch; DS3218 and MG90S servos ($14.99, $13.88
  [Prime]); a 28BYJ-48 or small NEMA 17 for the post slide; header pins for posts
  ($7.99 [Prime]); feeler gauges; ESP32; H-bridge; an AS5600 if the actuator has
  no feedback.
- **On hand:** camera, 24 V / 12 V supply.
- **Cost:** about $100–150 with the SN-2549, about $650 with the WC-110
  [estimate].

## Problems and their repairs, as they stand

- **Where the contact enters.** Sliding it in from behind would put the box
  through the anvil channel; lowering it from above meets the upper die, since
  the jaw opening is a few millimetres and the open wings are 3.2 mm tall. It
  enters along the axis from the front, barrels first.
- **A fixed blade would block a barrels-first entry.** The blade is on a flap
  and drops after placement, as JST's WC-110 flap does.
- **Reacting the tab shear.** A gripper on the box cannot do it: the tab root
  is 4.8–5.7 mm behind the box, so 48–158 N makes 230–905 N·mm there, 3–200×
  the neck's plastic moment, and far beyond what tweezers resist by friction
  [TS §1]. The steel land at the tab root reacts it with no lever.
- **A wrapped sprocket rolls the lead contact.** At 7.1 mm pitch an 8-tooth
  printed sprocket bends the 0.2 mm carrier to 1.1 % strain, beyond its
  0.41–0.59 % yield; a sprocket the carrier wraps needs ≥22 teeth (R ≈ 25 mm)
  [TS §9]. The pawl on a flat run and the tapered pin avoid it.
- **An actuator stalled on bottomed dies overloads the tool** by 5–7×; the
  spring link is the repair, and its switch replaces the ratchet's "no half
  crimps" guarantee if the pawl is removed for jams.
- **The ratchet locks if a cycle jams.** Remove the pawl (the actuator and the
  link switch guarantee a full close), or add a small solenoid on the release lug
  (hand-tool-as-press a1b).
- **Neighbour conductors hit the jaws.** The SN-2549's jaw plates span ~20–40 mm
  across the wire [estimate]; every neighbour in the plane collides [calc
  geometry §1]. By hand, fingers hold them aside; with the shuttle, b1's band.
- **Is the SN-2549's XH die right for 1.7 mm silicone on 60 × 0.08 strands?**
  Unknown. The first job is ten crimps by hand, sectioned and pulled. If they
  fail, the frame carries over to the WC-110.

## Contribution

- The smallest machine that takes the contact out of the person's hands, the
  step Derek most wants gone, while keeping the tool the bench already trusts.
- Four things that transfer to any arrangement using a hand-tool die:
  - the captive click as a machine state;
  - the contact held by a post in its box, placed along the axis from the
    front, the box front as the axial datum;
  - the tab cut against a steel edge at its root before any wire exists;
  - the spring link, which makes an oversized actuator safe on a hand tool and
    gives a "closed by force" switch.

## Major unresolved problems

- **SN-2549 crimp quality** on this ribbon is untested.
- **Jaw bottoming.** If the jaws do not bottom face to face, a force-limited
  close makes crimp height follow force; it must then come from the actuator's
  position, and 0.5 mm of handle resolution through a ratio of 8–20 is
  ±0.025–0.06 mm at the die, borderline against ±0.05 [procedure calc §4].
  Holding the closed tool to a light settles which case applies.
- **Carrier geometry.** Tab length, pitch and the pilot hole's position set the
  steel edge, the pawl and the pin; one $4.71 strip measures them.
- **The neck.** Whether it takes a 0.3–0.4 mm blade without the conductor die's
  edge crushing it.
- **Front clearance.** Whether the track, drop section, post head and flap fit
  in front of the SN-2549's jaw face.
- **The box and the nest's front face** (above).
- **Tool life.** Pivot wear over ~3,200 program crimps is unknown; at $22 a tool,
  replacing it is the plan.

## What rests on what

- **Derek:** placing, holding and crimping is the step he most wants
  automated; the SN-2549 is on the bench [repo].
- **Facts:** contact dimensions and tab shear force [facts §1, C1]; JST's hand
  tools and their notes [facts §2]; stock and prices [facts §6].
- **Calculations:** handle force [calc presses §4]; drive cycle times and link
  margins [calc wave3 §6]; shear moment, sprocket strain [TS §1, §9]; post
  capture and silhouette [TS wave2 §5]; drop kink [TS wave2 §9].
- **Estimates:** jaw-plate span; die clearance; costs.
- **Assumptions:** handle-to-die ratio 8–20; the dies bottom face to face; an
  AS5600 or step count repeats the captive click.
