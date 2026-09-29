# x1 — The post feeds the hand tool: kit contacts into the SN-2549's XH nest with no fingers

**A combination** of this explorer's [a6](a6-post-is-the-gripper.md) (a 0.64 mm
post as a travelling gripper that picks loose contacts from a pocket plate) with
hand-tool-as-press's [a1 squeezer cradle](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md)
(the bench's iCrimp SN-2549 on its side in a printed cradle, closed by a NEMA 17
lead-screw pusher through a load cell). force-and-form's
[f1](../../force-and-form/ideas/f1-motorised-ratchet-crimper.md) and
borrowed-machines' [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md)
are the same cradle from their sides. The stub-pen variant below adds
into-the-housing's [i2d](../../into-the-housing/ideas/i2d-locator-the-lance-never-touches.md)
(a cut-down housing stub as the locator).

Each of those cradles hands the loose contact to a person or to a strip: a1's
person presses it onto a locator, f1's drops it into a keyed flap, b2's tweezer
takes it off a strip after a shear. x1 puts a6's post head there instead, so the
contact is placed in the tool, the conductor in the contact, and the tool crimps,
with the tool Derek owns and the contacts he owns. Its motorless form, the **post
pen**, gives the SN-2549 a locator for loose contacts on the first day.

Sketch: panel 3 of [`../sketches/a6-post-is-the-gripper.svg`](../sketches/a6-post-is-the-gripper.svg) (schematic).
Numbers: [`../calc/wave2.py`](../calc/wave2.py) §5, §11 [w2 §n];
[`../calc/w3.py`](../calc/w3.py) §1, §2, §4 [w3 §n]; into-the-housing's
[`wave2`](../../into-the-housing/calc/wave2.out.txt) calc §H [ith-w2 H].

**Related.** The strip-contact twin is [a2c](a2c-strip-locator-for-hand-tool.md):
a clip on the same jaw with a pin in the carrier's pilot hole.

## Picture it

- **Where things start.** Kit contacts lie on a6's pocket plate over the light
  pad, in lance-grooved channels. The SN-2549 lies on its side in hand-tool-as-press
  a1's cradle, jaw plane vertical and the XH nest's axis horizontal, with the
  NEMA 17 pusher on the upper handle. The ribbon end, split and stripped, is in a
  ribbon carriage behind the tool, and its far end in a push-in terminal block
  (hand-tool-as-press's far-end block).
- **Picking.** The post head spears a barrels-up contact in its channel, lifts it
  and holds it over a backlight. The camera measures the distance from the holder
  face (the box front) to the conductor barrel's rear edge, and checks U-up, roll
  and wings.
- **Placing it in the tool.** The pusher has opened the jaws. The head carries the
  contact in along its own axis through the gap between the open jaws, barrels
  first, from the tool's front face. It stops when the conductor barrel's rear
  edge stands where the bellmouth wants it relative to the nest: a fiducial on the
  jaw's front face, taught once, plus the offset measured on the post. The box and
  the holder stay in front of the jaw's front face. The head lowers the contact
  until its Z float compresses ~0.1 mm, so the floor sits on the lower nest; the
  float's ±0.2 mm in Z lets it follow a nest that sits lower than taught.
- **Capture.** The pusher closes the handles until the force trace shows the first
  ratchet tooth: the repo's "one click, contact captive" [repo
  cable-assemblies.md], done by a machine. The head's float lets the closing dies
  centre the barrels. The pin stays in the box.
- **The conductor.** The ribbon carriage feeds conductor k in axially from the
  back of the jaw, through a1's printed funnel, until the far-end block reads
  closed (strand tips on a1's neck blade) or the camera sees the brush at the box
  end of the conductor barrel.
- **Crimp.** The pusher completes the ratchet cycle; the dies bottom and the
  ratchet releases at full closure. Force against lead-screw position is logged
  and compared with taught curves.
- **Release.** The pin draws back through the holder and the head moves away. The
  jaws open, and the ribbon carriage lifts the crimp off the anvil and draws it
  back, as a1 does.
- **What the person does.** Pours a unit's contacts on the plate; splays and
  strips, unless other stations do; inserts.

## The post pen (no motors)

- **The pen.** A header pin in a printed pen body, 1.5–1.8 mm proud of a steel
  face, so its tip stays inside the box; the tip is ground near-pointed. A thumb
  slider draws the pin back through the face, so the face pushes the contact off.
- **The spear block.** A printed block on the bench with three or four of a6's
  channels, each with a lance groove, and a backstop wall. Derek tips a few
  contacts on it and brushes them in with a finger, then presses the pen into the
  box of one lying barrels-up; the wall takes the push. The groove holds the
  contact flat so the pen meets the entry, not the box face [w3 §2].
- **The jaw fence.** A printed fence clipped to the SN-2549's jaw on the existing
  M4 lower-jaw screw [hand-tool-as-press a1; source: Chief Delphi / Printables],
  with a face for the pen's steel face. Derek slides the contact into the open
  nest until the pen's face meets the fence. The box front, and so the barrels,
  stand in the same place every time, to within the contact's own box-to-barrel
  spread. He clicks the ratchet once, thumbs the slider, withdraws the pen, feeds
  the wire and crimps.
- **What it gives.** An axial locator for loose kit contacts in the tool the repo
  builds with today. It does what the WC-110's flap locator does for JST's own
  tool [xh-facts §2], and what [a2c](a2c-strip-locator-for-hand-tool.md)'s pin
  clip does for strip contacts.
- **Its exposure.** The pen places the barrels from the box front, so it depends
  on the lot's box-to-barrel spread: ±0.05 mm within a lot [estimate], up to
  ±0.25 mm between clone brands [xh-facts §1], against a ±0.1 mm bellmouth window.
  One light-pad photograph of twenty kit contacts measures the bag's spread once.
  The machine form measures each contact on the post and is not exposed.
- **Cost:** a header pin and two prints.

### The stub pen (variant, with into-the-housing's i2d)

A cut XHP stub (the front wall plus 1.0–1.5 mm of cavity) is bonded to the pen's
steel face, so the pin passes through the stub's own post opening and the box
front stops on the stub's front wall, as it will in the housing. The stub's walls
add roll (±1.5–4.4°) and cross-axis location [ith-w2 H] to the pin's grip and
stripping; the jaw fence takes the stub's outer face. With the pin wired to an
ESP32 input and the loom's far end in the terminal block, the circuit closes when
the conductor lies in the barrels: this conductor is in this contact, before the
squeeze (i2d's ″ form). Open: the stub's depth against the lance root (0.74–1.74 mm
allowed [ith-w2 H]), and the same box-to-barrel spread.

## What locates what

| What | Set by | Note |
|---|---|---|
| Contact along its axis | holder face = box front; head position (or pen face on the fence) = jaw fiducial + measured offset | ±0.1 mm bellmouth window; the pen relies on the lot's spread |
| Contact across and in roll | the pin in the box, then the closing dies; the float lets the dies win | — |
| Conductor | ribbon carriage, steered by far-end continuity or the brush as seen | as hand-tool-as-press a1 |
| Crimp height | the SN-2549's dies if they bottom face to face; otherwise the cradle's stiffness | the study's open question; x1 does not change it |

**The reference for "fixed" is the SN-2549's fixed jaw**: its front face carries
the fiducial (or the pen's fence), and the cradle holds the tool.

## What drives and carries the crimp force

The ratchet tool carries the die force in its own jaws; the NEMA 17 pusher
squeezes the handles (~90–220 N at the handle tips [hand-tool-as-press, estimate])
and the ratchet guarantees full closure. The post head carries only 0.2–2 N at the
pick and release. The tool's XH anvil already crimps the kit contacts, so its
front edge clears their lance [w3 §4].

## How it knows it worked

The post silhouette before the tool, and the head's force trace at the pick; a1's
force curve through the ratchet and its continuity event; the after-crimp picture
and a silhouette crimp height in a booth (machine-that-sees-and-learns
[v5](../../machine-that-sees-and-learns/ideas/v5-inspection-booth.md)). With the
stub pen, continuity before the squeeze.

## Problems and repairs

1. **Does the box stay outside the jaw?** The hand procedure crimps XH in the
   SN-2549 with the box outside the nest, so the jaw's front face lies at or behind
   the neck, and the holder face, 0–0.3 mm in front of the box front, sits ~2 mm in
   front of the jaw. Open until the jaw is measured.
2. **The ratchet cannot let go after capture** if the conductor never arrives
   (inherited from a1 and f1). Repair there: a servo on the release lug, or a1b's
   pawl out. The post can strip the contact at any time.
3. **The neck blade and the pin together.** a1's blade drops into the neck from
   above and the pin is in the box from the front, so they do not meet. If the
   neck is too short for a blade (a1's own open question), the brush seen by the
   camera replaces the continuity signal.
4. **A contact rocking on its lance** in the spear block or on the plate. Repair:
   the lance groove.
5. **Capture at the box entry** is ±0.1–0.3 mm [w3 §1]; by hand the pen's tip
   finds the entry by feel, and the groove sets the height.
6. **The pen by hand, if the pin grips hard.** The slider strips the contact; no
   pull on the contact is needed.

## Steps covered, and what it hands back

- **Covers:** supply of loose kit contacts, singulation, orientation, placing the
  contact in the tool, capture, placing the conductor, crimp, release, checks. The
  pen covers placing the contact precisely, by hand.
- **Hands back:** pouring contacts; split and strip; insertion; the queue. With the
  pen, everything but the axial placement stays with the person.

## Printed and bought

| Part | Printed / bought |
|---|---|
| SN-2549 | on hand; a second one ($17.99–20.99 [source]) for the machine |
| Cradle, pusher yoke, funnel | printed (hand-tool-as-press a1) |
| Pusher | Iverntech NEMA 17 with integrated Tr8×2 screw (Prime, $27.99) through a ShangHJ 5 kg cell (Prime, $9.99) |
| Post head | as [a6](a6-post-is-the-gripper.md) |
| Pen, spear block with lance grooves, jaw fence | printed; one header pin (Prime strips, $7.99); a steel face from a feeler-gauge leaf (Hotop, Prime, $8.99) |
| Stub pen | a kit XHP housing cut on a printed sanding jig (i2d) |
| Far-end block | a push-in terminal strip on an ESP32 input |

## Contribution

Derek's priority step made automatic with the SN-2549 and the kit contacts, by
giving the cradle a pick tool that holds the contact by its own socket. It is also
a day-one hand jig from a header pin for the tool on the bench now.

## Major unresolved problems

- The SN-2549's jaw front face and nest position relative to the box and the neck.
- The ratchet's behaviour on a failed feed (a1, f1).
- The kit contact's grip on a 0.64 mm pin.
- The kit bag's box-to-barrel spread, for the pen.
- Whether the SN-2549's XH nest makes a good crimp on this ribbon at all, which x1
  does not change.

## What each conclusion rests on

- **Derek:** the SN-2549 and the kit contacts are what the bench uses; one click
  captures the contact [repo cable-assemblies.md].
- **Facts [mfr, source]:** WC-110's flap locator [xh-facts §2]; clone contact
  lengths [xh-facts §1]; the SN-2549 jaw screw mount [source, via
  hand-tool-as-press]; Prime listings.
- **Calculations [calc]:** post capture and the lance groove [w3 §1, §2]; lance
  window [w3 §4]; silhouette resolution and time [w2 §5, §11]; stub geometry
  [ith-w2 H].
- **Estimates:** within-lot box-to-barrel spread ±0.05 mm; handle force; post grip
  0.2–2 N.
- **Assumptions:** the box sits outside the jaws in the SN-2549 as in the hand
  procedure.
