# a2e Docked strip through a feedless applicator: every contact placed by one docking, then crimped one by one by bought, aligned dies

## Picture it

A combination of ribbon-as-pallet [a2](a2-two-pallets-meet.md) (placement by
docking a fanned ribbon onto a carrier segment, the carrier as fixture,
continuity before any stroke) and borrowed-machines'
[b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md) (a
bought OTP side-feed applicator in a slow press built around the idle VEVOR
12-ton press, with a force curve and stop-before-bottom). borrowed-machines
named it C1. Its drive is procedure-is-the-machine's short eccentric
([p5](../../procedure-is-the-machine/ideas/p5-camshaft-one-revolution-per-conductor.md)),
and the pilot in the carrier slot and the pull through the box are that
explorer's transfers. Sketch:
[`../sketches/a2e-docked-strip-feedless-applicator.svg`](../sketches/a2e-docked-strip-feedless-applicator.svg)
(schematic).

Against a2, the custom walking head goes away: the docked row travels through a
bought applicator whose feed has been removed. Against b1b, there is no feed,
fork or presser foot: every contact already holds its conductor when it reaches
the anvil.

**Where things start.**
- **The applicator.** An OTP side-feed "XH2.54" mini-applicator ($150–250
  [force-and-form key findings]; no Prime listing) stands on the VEVOR press's
  bed. Removed: the feed finger with its lever and cam roller; the spring
  pressure plate and wing bolt; the shear punch, so tabs are not cut in the
  stroke. Kept: crimpers, anvils and crimp-height dials, the terminal stripper,
  the track and the box guides. **A bullet-nosed pilot** sits in the shear
  punch's pocket, protruding at least ~3.5 mm below the crimper faces, so it
  enters the carrier's rectangular slot beside the anvil contact before the
  crimpers touch [P3 §6; assumption that the OTP unit is laid out like MKS-L].
- **The drive.** With the feed gone, the ram only has to lift its crimpers clear
  of the next open contact's wings (2.75–3.2 mm) plus margin, so a **3–4 mm
  eccentric** replaces the applicator's 30–40 mm stroke. It needs 1.0–1.7 N·m,
  inside a NEMA 17 with a 26.85:1 planetary (3 N·m permissible, $41.91 [Prime];
  "only 1 left" that day), and gives ~40–47 HX711 samples through the last
  0.2 mm at 10 s a turn, against 18–21 for a 15–20 mm crank [P3 §5]. An AS5600
  on the shaft ($7.99 for three [Prime]) and strain gauges on the eccentric rod
  log force against angle. The bench's NEMA 23 and DM542T stay in the cap-weld
  tube rotator [shared-context].
- **The carriage.** A steel plate on an MGN12 rail ($20.49 [Prime]) parallel to
  the strip (X), driven by a NEMA 17 on a Tr8×2 screw ($27.99 [Prime]). A
  **load position** upstream carries a **loading shelf** flush with the
  applicator's track, with **a groove along X under the lance line** (2.2–2.7 mm
  behind each contact's front, ≥1.1 mm deep); on a flat shelf every contact would
  sit propped 7.6–15.9° on its lance [w3 §5]. The carriage floats ±0.5 mm in X on
  a light spring (1–3 N/mm) so the pilot can draw the row.
- **The contacts.** The person lays a segment of N contacts on the shelf,
  barrels up, cut from the strip so that the carrier runs one full slot past
  contacts 1 and N. Two low **grips** drop pins into those **end slots**. Cut in
  sequence from one strip, a segment uses N + 1 positions; a unit takes ~67
  contacts, $1.57 at the reel price [calc F §7].
- **The ribbon.** A ribbon pallet from the preparation stations: parted
  ([a7](a7-zip-station.md)), fanned to strip pitch, flush-cut and ring-stripped
  at the fan block face ([a8](a8-rolling-ring-scorer.md)). A pair comes as two
  pallets.

**What moves.**
1. **Dock.** The person sets the ribbon pallet onto three balls on hardened
   seats on the carriage; magnets pull it home. Every conductor goes into every
   open contact, pressed in by a finger comb if the wings are narrower than the
   jacket [calc F §4]. The contacts' barrels rest on the shelf.
2. **Check.** The far-end pogo port ([a6](a6-housing-as-last-comb.md)) reads
   each conductor to the carrier, grounded through the grips. Every conductor
   must read continuous before anything moves. The camera photographs the row.
3. **Travel in.** The carriage moves the row downstream (−X), the direction a
   fed strip travels. The contacts slide off the shelf onto the track as fed
   contacts do, and the leading one arrives on the anvil.
4. **Crimp.** The camera looks at the contact on the anvil. The eccentric turns
   once: the pilot enters the slot and draws the floating row to the strip's
   own X (~1 N on the slot's edge, 13–23 MPa [P3 §6]); the crimpers curl and
   compact both barrels; a curve out of band stops the shaft short of bottom
   and backs it off. Then the shaft backs off and comes down to ~10 N with an
   indicator across ram and base (force-and-form's re-touch; a 0.001 mm
   Clockwise DITR-0105 is $52.99 [Prime]), which reads the crimp's height
   directly. No feed and no shear: the contact stays on its carrier.
5. **Index.** The carriage moves only with the ram up and the pilot out (the
   controller reads the shaft angle), one strip pitch downstream.
6. **Return.** After the last contact the carriage runs back to the load
   position; crimped barrels are lower than open ones, so they pass under the
   raised ram.
7. **Proof pull and tabs.** At the load position a comb of pins drops into
   every carrier slot, and the shear comb's pad comes down on the crimped
   barrels. A hook pulls each conductor in turn to 20 N at the fan block face,
   half of JST's 39.2 N minimum [xh-facts §1]. The pull goes conductor → crimp
   → contact → tab (in compression, 125 MPa) → carrier → slot pins, and the pad
   keeps the contact from pitching about its tab, which it otherwise does at
   2.5–4.6 N [w3 §4; calc F §3]. Held by its end grips alone, a 2.5–3 mm
   carrier would bow 0.2–2.7 mm under that pull [P3 §3]. Then the **shear
   comb** cuts every tab: a hardened bar notched per contact, its edge at the
   contacts' rear, and a lever that drives the carrier down past it.
8. **Lift.** The ribbon pallet lifts off with every contact crimped and all with
   the same roll, and goes to insertion. Carrier scrap goes in a cup.

**What locates what, and the reference for fixed.**
- **"Fixed" is the anvil** during the stroke, and **the carriage** otherwise.
  The carriage finds the anvil once per session with the camera on a contact.
- **The contact on the anvil:** Y and Z by the applicator's track and box guide;
  X by the pilot in the carrier's own slot, the applicator's own principle of
  "the part's feature as the reference at the moment of force". The round pilot
  hole lies under the jacket, so the pilot goes in the slot, which sits 3.55 mm
  from the contact, between conductor paths, and clears the neighbouring
  conductors by 2.1 mm [P3 §6].
- **The conductor in the contact:** the docking, ±0.1 mm at the fan block face;
  capture as [a2](a2-two-pallets-meet.md). Axially, the strip line against the
  carriage's seats, with the carrier on the same carriage (±0.2 mm stacked
  [estimate]).
- **Crimp height:** the applicator's dial, with the eccentric's bottom set once
  to shut height by its bearing blocks (135.78 mm for JST's CDS standard [mfr
  S11]; the OTP unit's own figure unknown).

**What carries the crimp force.** NEMA 17 → planetary → eccentric shaft in
pillow blocks on the VEVOR frame's crosshead → rod → ram → crimpers → contact →
anvil → applicator base → press bed. The carriage, grips and pallets carry only
positioning loads.

**How it knows each crimp worked.**
- **Before:** continuity conductor-to-carrier for every conductor; a camera frame
  per contact.
- **During:** the force curve against shaft angle, with stop-before-bottom;
  crimp height as the peak over the frame's stiffness (±8–23 µm at 13–39 kN/mm
  [calc X §9]) and as the re-touch reading.
- **After:** a camera frame per contact, the 20 N pull per conductor, a
  micrometer on the session's first crimps.

**Insulation crimp height on silicone.** A clone-spec 1.80 mm insulation crimp
squeezes this jacket to 70–80 % of its area and bulges it into the window
[calc W2 §9]. The applicator's insulation dial is set from a sweep on this
ribbon, as force-and-form's [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md)
does per crimp, not left at a PVC setting.

**What the person does, per ribbon end.** Lays a strip segment on the shelf
(~20 s), sets the ribbon pallet on its seats (~10 s), presses start, lifts the
pallet off after the shear. About 1.6–2.1 min of machine time per end, 20–28
min a unit [calc W2 §8].

## Steps it covers and what it hands back

- **Machine:** placement of every contact of an end by one docking, placement
  check, crimp with bought aligned dies, in-line crimp height, proof pull, tab
  cut; with [a7](a7-zip-station.md), [a8](a8-rolling-ring-scorer.md) and
  [a6](a6-housing-as-last-comb.md), split, strip and insert.
- **Person:** cut and load, strip segments, docking, far ends.
- **Where the person's time goes.** On procedure-is-the-machine's task library,
  with preparation by hand at [a1b](a1b-hand-shuttle.md)'s seats the person
  spends ~178 s per end (cut, load, prepare the next end, insert the previous
  one) against the machine's ~108 s, ~60 attended minutes a unit, and the
  machine calls every ~1.8 minutes [P3 §7, estimate]. The person sets the pace,
  so a second docking shelf buys nothing. With preparation on
  [a1](a1-pallet-tour.md)'s stage it is ~43 minutes; at the reel clamp
  ([a9](a9-reel-end-docks.md)), ~12. The crimp is a small share of the person's
  time in every docking arrangement.

## Why this combination holds together

- **The applicator's function guarantees room on one side.** A pre-feed
  side-feed applicator crimps one contact while the next open contact waits one
  strip pitch upstream, so its lowest tooling fits within ~5.1–5.7 mm of
  half-width at 6.8–7.1 mm pitch on that side [calc X §4]. A docked row at strip
  pitch is that geometry, with a conductor lying in each open contact below its
  wing tips.
- **Placement and crimping come apart.** Docking places every contact at once,
  checked before any force. The applicator then only closes dies on something
  already assembled, which is what its dies, dials and terminal stripper were
  made and aligned for.
- **No custom dies.** a2's head and a2b's N matched pairs are both answered by
  one bought applicator.
- **No pause needed.** Without a feed there is no pre-feed collision; nothing
  reaches the anvil except by the carriage.

## Physics and geometry at the moments that matter

| Moment | What must be right | Set by | Tolerance |
|---|---|---|---|
| Dock | strands in the conductor barrel, jacket in the insulation barrel | fan block ±0.1, seat ±0.01–0.02 | capture ~0 to ±0.5 mm (open-wing reading [P3 §2]); finger comb if ~0 |
| Dock, axial | insulation edge in the ~0.5–0.8 mm gap [estimate] | strip line at the fan block face; carrier on the same carriage | ±0.2 mm stacked |
| Travel onto the anvil | barrels slide shelf → track → anvil | shelf flush with the track; lance groove continuous with the track's | ≤0.05 mm step [estimate] |
| First crimper touch | contact seated, X on the anvil | pilot in the slot (X); track and guides (Y, Z) | ±0.02–0.05 mm [assumption, stamping] |
| Bottom of stroke | crimp height ±0.05 mm | dial and eccentric bottom | ±0.008–0.024 mm frame scatter [calc X §9] |
| Index out | crimped contacts free to move −X | the applicator's downstream side | unknown until scanned |

- **Downstream reach.** When the last contact is on the anvil, the crimped ones
  and the grip reach ~18–21 mm (3P), ~25–28 mm (4P) and ~32–35 mm (5P) past it
  with grips in the end slots; with grips in spare contacts it would be 28, 35.5
  and 42.6 mm [P3 §4].
- **Parted length:** 21 / 25 / 30 mm (3P / 4P / 5P) [calc §2].
- **The fan's recession:** at 7.1 mm a 5P's outer conductors recede 2.77 mm
  [calc W2 §3], so the flush cut and strip are made at the fan block face after
  fanning (order A of [a5](a5-part-fan-strip-in-the-pallet.md)). Closed to
  2.5 mm, the outer conductors keep 1.85 mm (4P) or 2.46 mm (5P) of excess, a
  4–5 mm arc in the finished split [calc F §5].
- **The tab window.** A cantilevered contact's tab yields after ~0.1 mm of lift
  [calc X §5]. Here the contacts never cantilever: they rest on the shelf, the
  track and the anvil, as fed contacts do.

## Parts

| Part | Source | Note |
|---|---|---|
| OTP side-feed XH applicator | bought | eBay $150–167 plus $80–90 shipping; Alibaba $200–250; no Prime listing |
| Eccentric drive | built, bought motor | NEMA 17 + 26.85:1 planetary $41.91; UCP204 pillow blocks $26.99 for two; AS5600 $7.99; BF350 gauges $6.99; HX711 $11.50 [Prime] |
| Pilot | turned from a hardened pin | in the shear punch's pocket |
| Carriage, rail, screw | bought | MGN12 rail $20.49; Iverntech NEMA 17 Tr8×2 $27.99 [Prime] |
| Loading shelf, grips, seats | printed with steel faces, balls, magnets | 52100 balls $6.65 / 100; 8 mm case-hardened rod $6.99 [Prime] |
| Slot-pin comb, shear comb | laser-cut or ground tool steel, printed levers | precision ground flat stock requested for the Prime pass ([`../sourcing-requests.md`](../sourcing-requests.md)) |
| Re-touch indicator | bought | Clockwise DITR-0105, 0.001 mm, $52.99 [Prime] |
| SXH-001T-P0.6 strip | bought | Digi-Key 100-piece $4.71; reel $0.0235 each [xh-facts §6]; no Prime listing for strip |

## Variants kept beside it

- **The reel instead of segments.** The reel feeds the shelf directly, a small
  carrier guillotine cuts each row's segment off after docking, and the contact
  count falls to N a end. At the reel clamp this becomes
  [a9](a9-reel-end-docks.md).
- **The shop press's jack, by hand, first.** With a hard-stop collar on a
  printed adapter (b1b's zero-build test), the person pumps one stroke per
  contact and slides the carriage between detents. It tests docking, travel onto
  the anvil and the crimp on this ribbon before any motor exists.
- **A crown downstream,** if the scan shows no room there. The carrier is bent
  down over a crown just past the anvil, so crimped contacts drop 3.6–4 mm below
  the tooling (crown radius 5.8–7.0 mm, 1.4–1.7 % carrier strain [w3 §10], from
  force-and-form's [f8](../../force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md)).
  The carrier then leaves bent, so the pull and shear move to the downstream
  side.
- **The pull through the box.** A thin blade drops into the neck behind each
  box and takes the 20 N on the box's rear face (~25 MPa [calc F §3]), so the
  carrier sees none of it. It needs the neck t to take a ~0.3 mm blade.
- **A harvested knife set instead of the applicator,** in a holder Derek makes;
  the tooling envelope becomes his, and so does its alignment.

## What it contributes

- Derek's priority step split into **placing** (one docking motion for every
  contact of a ribbon end, checked electrically before any force) and
  **crimping** (bought, aligned dies with dials, stroked slowly with a force
  curve and a height reading).
- **One bought applicator does N crimps per ribbon end** with no feed, fork,
  foot, finger or custom die.
- **The carrier stays the fixture** through crimp, pull and shear.

## Major unresolved problems

- **Which OTP parts unbolt**, what is left over the carrier line and around the
  anvil, whether the shear punch's pocket takes a pilot, and whether the ram
  has a return spring. The Revopoint MINI 2 on hand can scan the applicator.
- **The downstream side:** ~18–35 mm of room past the anvil, and whether the
  terminal stripper lets a crimped contact leave along X.
- **The eccentric's frame:** pillow blocks on the VEVOR crosshead at the
  applicator's shut height, with a stiffness still to be found (b1b's
  13–39 kN/mm is an estimate).
- **The shear comb's tab length** against JST's cut-off criteria [xh-facts §5].
- **21–30 mm of split with a 4–5 mm arc** in the outer conductors, Derek's
  question.
- **Genuine SXH against the applicator vendor's clone:** the dies are set up for
  one contact, and the strip must match its box guide and pitch.
- **Guarding** a press that starts on software's command, at walking pace.

## Related ideas

- Parents: [a2](a2-two-pallets-meet.md); borrowed-machines
  [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md).
- At the reel clamp: [a9](a9-reel-end-docks.md). Without the carrier through the
  crimp: [a10](a10-dock-tack-then-nest.md). With the feed kept:
  [a1c](a1c-crimp-upstream-first-park-after.md).
- Other explorers: procedure-is-the-machine
  [p5](../../procedure-is-the-machine/ideas/p5-camshaft-one-revolution-per-conductor.md);
  force-and-form [f3](../../force-and-form/ideas/f3-knee-micropress.md) (re-touch),
  [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md),
  [f8](../../force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md) (crown).

## What rests on assumptions

- Strip pitch ~7.1 mm [Würth analog; JST's figure is licence-gated].
- The shelf-to-track transfer [estimate]; pilot correction forces [P3 §6].
- That the OTP applicator's layout follows the MKS-L manual's
  [assumption, borrowed-machines].
- Person-time figures [estimate, one task library].

## Labels

As [a1](a1-pallet-tour.md#labels) and [a2](a2-two-pallets-meet.md#labels).
