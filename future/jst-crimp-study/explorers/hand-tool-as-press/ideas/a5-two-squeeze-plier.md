# A5 — A precision plier with no ratchet, squeezed twice by a machine that knows when to stop

## Picture it

**Where things start.** An **Engineer PA-09** micro connector crimping plier
lies in an [a1](a1-squeezer-cradle.md)-style cradle:
- 175 mm long, non-ratchet, spring-opened;
- dies 1.0, 1.4, 1.6 and 1.9 mm wide, the 1.6 and 1.9 dies 1.8 mm thick
  [mfr S18];
- S55C carbon steel, made in Japan;
- $38.99, 1,719 ratings, 200+ bought in the past month, next-day delivery
  [prime: B002AVVO7K].

Engineer lists it for SXH-001T-P0.6 [xh-facts §2]. The PA-09 crimps the
conductor barrel and the insulation barrel **in separate squeezes**. For XH,
the 1.6 mm die takes the conductor barrel and the 1.9 mm die the insulation
barrel [estimate in xh-facts §2]. Engineer's rule is that die thickness equals
barrel length [mfr S18], which points to a genuine conductor barrel of
~1.8 mm, matching what JST's 2.4 mm strip implies [sl w3 §4].

**What moves.**
- The upper handle, driven by a1's NEMA 17 Tr8×2 pusher through a load cell.
- Between squeezes, the conductor and contact together, carried by a carriage
  like [a2](a2-ribbon-to-fixed-tool.md)'s. In a person-fed version, the
  person's hand moves them from one die to the other, guided by a printed stop
  for each die.

**What locates what.** "Fixed" is the lower jaw.
- **First squeeze.** The contact sits in the 1.6 die. A printed stop places
  the conductor barrel's rear edge 0.1–0.2 mm proud of the die's rear face, the
  bellmouth offset Engineer's users describe [prior-art §4]. The PA-09 holds
  the contact lightly when closed a little, "securely enough for the wire to be
  inserted" [source: experimental-engineering.co.uk review].
- **Second squeeze.** After the first, the contact is joined to the wire. The
  wire carries it: the carriage moves it sideways to the 1.9 die and axially
  ~1.5–2.5 mm, so the insulation barrel sits in the die [calc §11].

**What drives and carries the crimp force.** The pusher, through the plier's
single pivot. The plier's gain is ~5–8 [estimate in xh-facts §5]. So a
conductor-barrel crimp at 0.75–2.3 kN needs ~95–460 N at the grip [calc §11].
- The upper half of that exceeds a hand, and people crimp XH with a PA-09 by
  hand. So either the die force is in the lower half of the estimate, or the
  gain is higher.
- A NEMA 17 Tr8×2 gives ~280 N. The NEMA 23 on hand gives ~940 N.

**How it knows it worked.** Two force curves per crimp, one per barrel, run and
checked on the station ESP32. The conductor curve carries no insulation signal
and the insulation curve carries no strand signal, so each is simpler to band
than a1's combined curve. The camera, the far-end block and a6's pull jig are
as in a1.

**What the person does.** In the person-fed version:
- places the contact in the 1.6 die against its stop;
- feeds the conductor to the blade;
- presses the pedal;
- moves the crimp to the 1.9 die against its stop;
- presses the pedal again.

With a carriage, as in a2. **The first build is the PA-09 in the hand with the
two printed stops on its jaw:** today's hand use, with a reference for each
placement.

Sketch: [`../sketches/a5-two-squeeze.svg`](../sketches/a5-two-squeeze.svg).

## Steps it covers and what it hands back

**Covers:** the crimp, each barrel separately, crimp height as a setting, two
force curves, and the host role for a per-barrel crimp-height sweep.

**Hands back:** whatever a1, a2 or a3 hands back; the second placement in the
person-fed version; teach-in by sectioning or micrometering sample crimps.

## How it relates

- A different tool in [a1](a1-squeezer-cradle.md)'s cradle; it slots in
  wherever a1's squeezer sits: alone with a person, behind a2's carriage, or on
  [a3](a3-tool-travels-to-ribbon.md)'s gantry as a module.
- The two-barrel host for machine-that-sees-and-learns'
  [v3](../../machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md);
  [a1b](a1b-pawl-out.md) is the same host with SN dies.
- change-the-question's [c2](../../change-the-question/ideas/c2-buy-the-crimp.md)
  JST lead is the sweep's target [htq, K6].
- Pre-formed insulation barrels ([a6b](a6b-flags-by-hand-foot-crimp.md),
  change-the-question's [c1b](../../change-the-question/ideas/c1b-tack-first.md))
  change the second squeeze (below).

## Major unresolved problems

- **The 1.8 mm die over a clone-length conductor barrel.** With a clone barrel
  of 1.25–1.5 mm and the rear edge placed 0.1–0.2 mm proud for a bellmouth, the
  die's front face lands 0.40–0.75 mm ahead of the barrel's front edge. Across
  a 0.2–0.5 mm transition that reaches the box's rear by up to 0.55 mm; placed
  flush with the box instead, the die loses the bellmouth [sl w3 §5]. On a
  ~1.8 mm barrel it fits. So a5 is a genuine-contact arrangement (SXH or BXH)
  unless the kit contacts' barrel measures ~1.8 mm.
- **The PA-09 has no stop.** Crimp height is whatever closure the squeeze
  reaches: "squeeze too tightly & the contact deforms, not tightly enough & the
  wire will pull out" [source: review]. The machine has to decide when to stop
  on every crimp, from force and position.
- **Scissor action.** The dies close on an arc about one pivot. A
  scissors-action tool makes a nonsymmetrical crimp [source: Assembly Magazine
  95079, Pressmaster].
- **Two placements per crimp**, each a chance to be off.
- **The insulation squeeze has a floor and a ceiling**, ~0.1–0.3 mm apart on
  this wire (below).

## What the machine gives a non-ratchet tool

The review's point is that the PA-09's crimp depends on a feel for when it is
done. That feel is a force-against-position judgement, the thing a slow
machine with a load cell and a lead screw measures directly:
- **Stop on a knee.** Strand compaction shows as a steep rise in force over the
  last 0.10–0.20 mm of die travel [xh-facts §4]. The machine stops at a set
  force, or a set position past the knee's onset. Either is taught from crimps
  that measured well. The stop is enforced on the station MCU, sample by
  sample, as in [a1b](a1b-pawl-out.md).
- **Crimp height becomes a setting.** A fixed-die ratchet tool has no crimp
  height to adjust. JST says its own hand tools have none, and that some wires
  "may not be crimped properly" [xh-facts §2]. Here crimp height is the grip
  position the machine stops at.
- **Conductor and insulation separately.** The insulation crimp on soft
  silicone can be set just past where the wings wrap the 1.7 mm OD without
  cutting in. The conductor crimp can be as firm as the strands want. The
  SN-2549's single squeeze couples them through its stepped die.
- **Backing out.** No ratchet, nothing to release.

Getting the setting starts with Derek sectioning or micrometering a handful of
crimps at different stop forces or positions. A crimp micrometer, or the
caliper's knife edges, gives crimp height; a luggage scale on the wire gives
pull-out. The stop that gives JST-like crimp height (0.8–0.9 mm estimated
[xh-facts §1]) with pull-out over 39.2 N becomes the setting.

## The second squeeze has a floor as well as a ceiling

"Gentle on the silicone" is bounded from below by the housing [ith ex §9]:
- **What the barrel does on this wire.** A 1.7 mm silicone conductor inside a
  closed insulation barrel of 0.2 mm stock is squeezed into a section between
  an ellipse and a rectangle. The ellipse is the tallest reading [sl w3 §9]:
  - at a closed width of 1.95 mm: 2.03–2.26 mm tall outside (rectangle-ish to
    ellipse);
  - at 1.90 mm: 2.08–2.33 mm;
  - at 1.80 mm: 2.20–2.46 mm, where the ellipse is over JST's 2.4 mm end-view
    envelope [mfr S1].
- **The margin.** The room under 2.4 mm is ~0.1–0.3 mm with no silicone flow,
  and more if silicone leaves as collars (force-and-form: 0.15–0.3 mm lower at
  10–20 % flow). A wing tip that does not tuck spends it.

So the insulation squeeze stops on two limits:
- **A minimum closure:** wing tips tucked, and height ≤ ~2.3 mm, or whatever
  the kit housing's rear entry measures.
- **A maximum:** the closure that starts to cut the silicone, shown by the
  insulation curve's slope rising as the wings bite, and by tests: pulls, and
  JST's bend criterion (the insulation crimp survives 60–90° bends several
  times [mfr S5]), since a cut jacket can still pass a pull.

The separate insulation curve is where both are taught.
[a6](a6-foot-closed-jig-bench.md)'s keyhole, the cavity's section, checks the
result on every crimp. The kit housing's rear entry is unmeasured.

**Insulation first, as a branch.** If the insulation barrel arrives already
narrowed, by a part-closure of the PA-09's own 1.9 die before the conductor
squeeze or by [a6b](a6b-flags-by-hand-foot-crimp.md)'s click in an SN-2549,
the second squeeze only finishes a curl the die started, and the window
between floor and ceiling may widen. It reverses JST's conductor-first order
for two-step tools (force-and-form's f9 point); whether that changes the
insulation crimp is untested.

## The plier as the press that finds its own setting

machine-that-sees-and-learns'
[v3](../../machine-that-sees-and-learns/ideas/v3-press-that-runs-experiments.md)
sweeps crimp height on coupons, pulls each to failure, and leaves a window and
a force signature behind. a5 is a press with a settable stop at $38.99.
- **What a stop is here.** Each stop is a pusher position or a force, not a
  length.
- **Mapping it to a length.** Each level's coupons are micrometered, or
  silhouetted in v5's booth with the box as its own roll gauge, to map stop to
  crimp height. The map is re-checked whenever the knee drifts in position at
  a fixed force.
- **Two sweeps.** a5 sweeps the conductor squeeze and the insulation squeeze
  separately, which a one-squeeze tool cannot. The insulation sweep finds the
  floor and the ceiling above, with bend tests beside the pulls.
- **Pulls to failure grip copper,** not jacket: a soldered far-end lug or bare
  copper on a pin (a capstan at 100 N shears the silicone [ribbon-as-pallet
  calc P §4]).
- **The target** is change-the-question's c2 lead, a genuine JST crimp on
  22 AWG.

## Tried against it

- **"Scissor action makes an asymmetric crimp."** It does in general. Engineer
  sells the PA-09 for these contacts, and its dies are narrow (1.6 mm). Across
  a 1.6 mm die at ~50–100 mm from the pivot, the angle between the die faces
  at closure is small [estimate]. The machine does not change it. A
  parallel-action two-step tool also exists, JST's own YRS-110 at $1,565.93
  [xh-facts §2], and goes in the same cradle. That variant is not developed
  here.
- **"The pivot wears and the stop position drifts."** The PA-09 has an
  adjustable joint screw [source]. The machine sees drift as the knee moving in
  position at the same force. A force stop is immune to it. A position stop
  needs re-teaching.
- **"Moving a half-crimped contact by its wire rotates it."** The conductor
  crimp holds the contact to the strands. Silicone between the carriage's grip
  and the contact can twist a few degrees. The 1.9 die's profile squares the
  insulation barrel as it closes, as it does in hand use.
- **"Twice the placements."** The second placement is by the wire, which the
  carriage already holds. Its error is the carriage's error plus the twist.
  The 1.9 die is 1.8 mm thick against an insulation barrel of ~0.8–1.5 mm
  [xh-facts §1–2], which leaves ~±0.15–0.5 mm of axial room. That room holds
  for the insulation die, where overhang onto the jacket or the finished
  conductor crimp touches nothing; the conductor die is the constraining one
  (above).

## Rests on

- **[source]** The PA-09 holds a contact before the first squeeze well enough
  for a conductor to be pushed in (the review says it does, by hand).
- **[estimate]** The 1.6 and 1.9 dies are the right ones for this contact on
  this wire [xh-facts §2].
- **[estimate]** Die force for the conductor barrel alone is within what a NEMA
  17 pusher delivers through the PA-09's gain. If not, the NEMA 23 on hand is
  the pusher.
- **[estimate]** Kit contacts have clone-length conductor barrels
  (1.25–1.5 mm); one side photograph settles it.

---

Citation keys: **[calc §n]** is [`../calc/hand_tool_press.out.txt`](../calc/hand_tool_press.out.txt);
**[sl w3 §n]** is machine-that-sees-and-learns'
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[htq, K6]** is a combination in
[`hand-tool-as-press--on--change-the-question-w3.md`](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
