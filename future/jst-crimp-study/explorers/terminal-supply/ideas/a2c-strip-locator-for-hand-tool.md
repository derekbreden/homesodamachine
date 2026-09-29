# a2c — The strip gives the hand tool the locator it lacks

Branch of [`a2-strip-indexer.md`](a2-strip-indexer.md). **What it changes:** the
crimp is made by an unmodified ratcheting hand tool, the iCrimp SN-2549 Derek
already owns with its XH nest, instead of a punch and anvil in a press. The strip
still feeds and locates. The carrier is cut after the contact is captive in the
jaws and before the wire arrives.

No sketch: the picture is a hand tool with a clip on its jaw.
Numbers: [`../calc/terminal_supply.py`](../calc/terminal_supply.py) §9 [ts §9];
machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
§5 [mtsl §5]; hand-tool-as-press's calc for handle force.

**Related.** The loose-contact counterpart, which gives the same tool a locator
from a header pin, is [x1](x1-post-feeds-the-hand-tool.md). The cradle that
squeezes the tool is hand-tool-as-press
[a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md) (also force-and-form
[f1](../../force-and-form/ideas/f1-motorised-ratchet-crimper.md), borrowed-machines
[b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md), whose strip
sprocket and shear are the same family).

## Picture it

- **Setup.** The SN-2549 is clamped in a printed cradle with its XH nest
  horizontal. A printed clip is screwed to the fixed jaw on its M4 jaw screw, on
  the wire side. It carries a fence the carrier's front edge rests against, and
  a sprung 1.45 mm pin that drops into the leading contact's pilot hole.
- **Loading.** A small stepper pushes the strip's leading contact sideways into
  the open nest until the pin clicks into its hole. The contact now sits where
  the fence and pin put it, not where a fingertip did: axially (bellmouth and
  insulation position), laterally, and in roll, because the flat carrier cannot
  twist.
- **Capture.** A NEMA 17 lead-screw actuator squeezes the handles to the first
  ratchet click. The contact is captive, which is the trick the repo's hand
  procedure already uses [repo cable-assemblies.md].
- **Cutting the carrier, before any wire.** Nothing lies over the tab yet, just
  behind the jaw's rear face. A servo-driven flush cutter closes on it from
  above, or a small drop plate pushes the carrier down against the jaw's rear
  edge. The strip, now free of the captive contact, is drawn back one pitch so
  the next contact is clear of the jaw.
- **Crimping.** The ribbon carriage slides conductor k in axially from the wire
  side, on a path the carrier has left. The actuator completes the ratchet
  cycle, which will not release until the dies bottom, and opens.
- **What the person does.** Threads a strip; clears the cutter's scrap. By hand
  on day one, the clip alone is a locator: Derek pushes the strip in until the
  pin clicks, clicks the ratchet, snips the tab with the KATA cutters, feeds the
  wire and crimps.

## What locates what

| What | Reference | Note |
|---|---|---|
| Contact, axially | carrier's front edge on the clip's fence | the fence is referenced to the jaw via the M4 screw |
| Contact, laterally | sprung pin in the pilot hole | the hole is on the contact's centreline |
| Contact, roll | the flat carrier | cannot twist while the pin is in |
| Contact after capture | the jaws (one click) | the pin and fence give in Z as the contact drops into the lower die |
| Conductor | ribbon carriage, steered by the insulation edge as seen from the wire side | — |
| Crimp height | the SN-2549's dies | if its jaws bottom face to face; otherwise the tool's stiffness |

**The reference for "fixed" is the SN-2549's fixed jaw**, to which the clip, the
fence and the pin are screwed. The cradle holds the tool; it sets nothing.

## What drives and carries the crimp force

The ratchet tool carries the die force inside its own jaws and handles. The
actuator only squeezes the handles. The hand force for XH on a ratchet tool is
unrecorded; ~90–220 N at the handle tips is a reasonable bracket
[hand-tool-as-press calc §1]. A NEMA 17 on a 2 mm-lead screw gives ~280–350 N
[estimate]. The ratchet guarantees full closure, so the actuator needs no
position accuracy at the bottom. The carrier cut is 48–158 N at the edge
[xh-facts C1]: a metal-gear servo on a 3–4:1 lever, or a servo closing a flush
cutter's handles (8–40 N at the handles [ts §9]).

## What the strip buys a cheap tool

JST's WC-110 is the one XH hand tool with a locator: a "flap locator to ensure
the correct positioning of the contact" [xh-facts §2], at $536.51. Neither the
SN-2549 nor any other low-cost tool has one [repo cable-assemblies.md]. The
carrier is a locator attached to every contact: its edge sets the axial
position, its pilot hole the lateral, its flatness the roll. A printed clip
that references it gives the cheap tool the missing function, by hand or by
motor.

## Where the carrier is cut, and why there

The carrier joins the contact at the rear of the insulation barrel, in the
floor plane, on the side the wire enters from. Four places to part it:

- **After the crimp, by bending the strip ±90° about the tab.** This twists the
  strip still held upstream. A 90° twist over one 7.1 mm pitch puts ~1,800 MPa
  of shear into the carrier against ~290 MPa shear yield; over 30 mm it is still
  430 MPa, and ~50 mm of free carrier is needed before the twist is elastic
  [mtsl §5]. The next contact arrives twisted and rolled. Not used.
- **After the crimp, by a drop-shear against the closed jaw's rear face**, with
  the handles held closed after the ratchet releases. It works if the jaw's rear
  face is square and sits at the insulation barrel's rear edge. A variant.
- **After capture and before the wire** (the arrangement above). Nothing lies
  over the tab, so a cutter from above fits, the wire's path is cleared, and the
  strip is never twisted. It is the same move as
  [a6](a6-post-is-the-gripper.md)'s: cut the carrier before a wire exists.
- **At the slot upstream of the station first, then bend off the freed tag
  alone.** A variant.

## How it knows it worked

- The pin's home switch (contact located).
- The actuator's current or force trace through the ratchet, which changes for a
  missing wire or contact.
- The stripped tip seen alone on a backlight before it enters.
- The insulation edge, seen from the wire side as the carriage stops.
- The crimp after the jaws open, with a silhouette crimp height on every crimp
  (machine-that-sees-and-learns [v5](../../machine-that-sees-and-learns/ideas/v5-inspection-booth.md)).

After the first ratchet click the wings are inside the upper die, and no camera
sees strands against wing tips. A strand riding a wing tip is found only after
the crimp; the stripped-tip look and the booth carry that.

## Problems and repairs

1. **Does the carrier fit beside the jaws?** The carrier is ~0.8–1.15 mm behind
   the insulation barrel. If the SN-2549's XH nest is thicker than the barrels
   plus that gap, the jaws close on the tab or carrier. Open until the jaw is
   measured (a caliper on the jaw). It also decides whether a cutter can reach
   the tab after capture.
2. **The ratchet makes the contact captive, so the pin must let go.** As the
   jaws close the contact drops into the lower die; a rigid pin would fight it.
   Repair: the pin is sprung and the fence gives in Z.
3. **The capture must hold the contact against the cut.** The cut's 48–158 N acts
   on the tab at the jaw's rear edge while the contact is held only by partly
   closed dies. Open. A flush cutter's pinch, rather than a drop plate's push,
   keeps most of that force inside the cutter.
4. **The tool's die is a hand tool's die.** JST calls its own hand tools
   prototype and repair tools with no crimp-height adjustment [xh-facts §2].
   What the SN-2549's XH nest gives on this wire is unknown; a2c changes only
   placement. The silhouette crimp height on every crimp shows, the first
   afternoon, whether its jaws bottom face to face.
5. **The nest's fit to strip contacts.** The SN-2549 crimps the kit contacts
   today, so its anvil clears their lance [w3 §4 context]. Genuine SXH or a
   clone reel may differ in wing width and lance position; one crimp of each
   settles it.

## Steps covered, and what it hands back

- **Covers:** placing the contact (by the strip, not by fingers), holding it,
  separating it from the carrier, crimping.
- **Hands back:** splay and strip; presenting the conductor (the ribbon
  carriage, or Derek's hand); insertion.

## Printed and bought

| Part | Printed / bought |
|---|---|
| SN-2549 | on hand [repo tools.md]; a second one ($17.99–20.99 [source]) for the machine |
| Clip with fence and sprung pin; tool cradle; handle yoke; strip track | printed; the pin a 1.448 mm pin gauge (Accusize set, Prime, $45.58 [sourcing/amazon-prime.md]) |
| Handle actuator | Iverntech NEMA 17 with integrated Tr8×2 screw (Prime, $27.99, thin listing) |
| Strip feed | ELEGOO 28BYJ-48 + ULN2003 (Prime, $14.99) |
| Carrier cutter | Hakko CHP-170 pair (Prime, $22.91, 24,508 ratings) closed by a servo, or a small drop plate [sourcing/amazon-prime.md] |
| Contacts | SXH-001T-P0.6 cut strip or clone reel [xh-facts §6] |

## Contribution

The smallest change that removes hand placement: keep the tool, change the
supply form. It is also a manual aid on day one, the strip-contact twin of
[x1](x1-post-feeds-the-hand-tool.md)'s post pen.

## Major unresolved problems

- **The SN-2549's jaw thickness and rear face** relative to contact plus tab.
- **Whether its XH nest suits genuine SXH or the clones better.**
- **Whether a one-click capture holds the contact against the cut.**
- **Ratchet handle force** (not measured).

## What each conclusion rests on

- **Derek:** the SN-2549 is the tool on the bench and the hand procedure uses
  one click to capture [repo cable-assemblies.md].
- **Facts [mfr, source]:** WC-110 and its locator; JST's note on fixed-die hand
  tools [xh-facts §2]; carrier geometry [xh-facts §1]; Prime listings.
- **Calculations [calc]:** twist stress when bending the strip off [mtsl §5];
  cutter handle forces [ts §9].
- **Estimates:** handle force bracket; lead-screw thrust.
- **Assumptions:** the carrier clears the jaws.
