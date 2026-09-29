# b1 — The bought press and applicator, operated by a printer-axis ribbon shuttle

The small-shop wire industry already mass-produces the machine that places an
XH contact under the dies and crimps it: a 1.5–2 t bench terminal press with a
side-feed mini-applicator. The same industry also knows how a machine, rather
than a hand, brings the wire to it. The applicator's feed cam is set to
**post-feed**, which the WERI manual calls the **"automatic"** configuration
and ships as the default, and the wire is held above the anvil until the ram
brings it down [mfr: WERI mini-applicator manual §7,
[we-online](https://www.we-online.com/components/products/datasheet/600662403.pdf),
read 2026-09-28]. Here a slow shuttle built from 3D-printer parts is that
machine. The press is unmodified except for a relay across the pedal and a
small spring finger bolted to the applicator's ram.

**Branches:** [b1b](b1b-applicator-in-slow-crank-press.md) keeps the
applicator and drives it with a slow crank Derek builds;
[b1c](b1c-one-shaft-applicator-press.md) puts the whole sequence on b1b's
crankshaft; [b8](b8-spool-fed-borrowed-line.md) feeds the same applicator from
the spool. Prep stations that feed it: [b6](b6-pierce-at-the-root-pull-to-the-tip.md)
(split), [b4b](b4b-diode-heads-at-the-station.md) (laser score and slit),
[b7](b7-borrowed-strip-head-one-conductor.md) (strip one conductor).

Sketches: [`../sketches/b1-press-shuttle.svg`](../sketches/b1-press-shuttle.svg)
(the machine in elevation and plan) and
[`../sketches/w2-b1-post-feed.svg`](../sketches/w2-b1-post-feed.svg) (the
post-feed stroke in four frames).

Labels: [calc wave2 §n], [calc geometry §n], [calc presses §n] are this
explorer's [`wave2.out.txt`](../calc/wave2.out.txt),
[`geometry.out.txt`](../calc/geometry.out.txt) and
[`presses.out.txt`](../calc/presses.out.txt);
[TS §n] is terminal-supply's
[`w3_on_borrowed.out.txt`](../../terminal-supply/calc/w3_on_borrowed.out.txt);
[procedure calc §n] is procedure-is-the-machine's
[`exchange_borrowed.out.txt`](../../procedure-is-the-machine/calc/exchange_borrowed.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it

**Where things start.**
- **The press.** A Chinese "mute" terminal press (the Sanao SA-2.0T / WIREPRO
  TU-N02 class: 38–55 kg, 30 mm stroke, 110 V, foot switch) stands on the
  bench. On its bed is an OTP side-feed applicator for XH contacts, with its
  feed cam in the **post-feed** position. At rest the anvil is empty; the next
  contact waits one pitch upstream on the carrier.
- **The contacts.** A **reel** of XH contacts on carrier strip hangs on the
  press's reel arm and threads sideways through the applicator. It is the
  contact the applicator's vendor set the die for, or one named when ordering.
- **The ribbon end** sits in a printed **cassette**:
  - an under-width channel (~0.2 mm under nominal) with a centred datum, after
    AMP US 4,230,008, which registers every conductor to ~0.1–0.23 mm
    [ribbon-as-pallet calc, via this explorer's exchange];
  - the tip flush-cut in the cassette's own guillotine slot;
  - the end already split to the clamp edge and stripped to the reel's strip
    length Ls at a prep station ([b6](b6-pierce-at-the-root-pull-to-the-tip.md)'s
    rip plus a whole-tip strip, [b4b](b4b-diode-heads-at-the-station.md)'s
    laser, or by hand);
  - an ungrooved hinged lid that has folded all the split conductors back 180°
    over the clamp edge in one motion, so they lie on the cassette's top plate
    as **one flat band**, in ribbon order, pointing away from the press. A row
    of pockets at the band's tip end takes each crimped contact's box when it
    comes back.

**What moves.**
- **Shuttle.** Two MGN12 rails ($20.49 [Prime]) with NEMA 17 / Tr8×2 lead
  screws ($27.99 [Prime]) give Y across the applicator and X toward it, run by
  a BTT SKR Pico ($35.99 [Prime]) or an MKS DLC32 ($38.50 [Prime]). It is
  bolted to the press table in front of the applicator; the cassette drops onto
  it on two pins and a magnet.
- **Valley-tine fork.** A servo-swung fork (DS3218, $14.99 [Prime]) pivots on a
  line along Y at the cassette's clamp edge, on the applicator's axis. Its two
  blunt 0.25 mm steel shim tines, 1.7 mm apart, descend into the V-valleys
  either side of the target conductor in the band. It holds the target
  laterally only; its slot is open downward, so the conductor can slide down
  between the tines.
- **Ram finger.** A spring-loaded V-finger (printed body, steel V insert)
  bolted to the applicator's ram beside the insulation crimper, over the
  insulation just behind the insulation barrel. It protrudes ≥1.75 mm below the
  insulation crimper's forming face [calc wave2 §1]. If the OTP unit has a slot
  for a factory **wire hold spring**, as JST's MKS-L does, the bought spring is
  used [mfr: MKS-L manual p. 19].

**One conductor.**
1. **Look at the waiting contact.** At rest, before the fork moves, the camera
   looks at the contact waiting one pitch upstream on the carrier: present,
   upright, wings open. A bad one stops the cycle. Whether the strip guides
   leave its barrels in view is measured on the applicator that arrives.
2. The shuttle indexes Y until conductor *i* of the band sits under the fork.
   The tines descend into the valleys either side of it.
3. The fork swings 180° and lays that conductor forward over the empty anvil,
   holding its centre ~4.6 mm above the barrel floor, over the wing tips of a
   contact that is not there yet [calc wave2 §1]. The conductor rises 14–25°
   from the root to reach that height, depending on the split length.
4. The ELP camera photographs the tip over the anvil landmarks: X within
   ±0.3 mm, Y within the finger's ±1 mm capture.
5. A relay fires the press. On the downstroke:
   - the post-feed cam slides the next contact onto the anvil, under the held
     conductor;
   - the ram finger lands on the conductor, catches it in its V and pushes it
     down into both open barrels (the fork's open slot lets it descend);
   - the crimpers form both barrels and the shear cuts the tab.
6. The ram rises and the finger lifts with it. Nothing feeds on the upstroke;
   the crimped contact stays on the anvil with its conductor.
7. The camera photographs the brush, bellmouth and closed insulation wings.
8. **Proof pull.** The shuttle backs off 7–12 mm in X. The contact slides out
   along its own axis; a thin steel fork drops into the neck behind the box
   (the crimped conductor barrel there is ~1.5 mm wide and ≤1.1 mm tall), and
   the shuttle pulls 20 N through a load cell in the cassette mount (bar cell
   with HX711, $9.99 [Prime]). The fork bears on the box's rear face above the
   floor, clear of the lance [TS §11].
9. The fork swings back and lays the crimped conductor into its own place in
   the band, box in its pocket. Y indexes to the next conductor.

**What locates what; the reference for "fixed."** The applicator body is the
reference for the contact and, at the moment that matters, for the conductor.

| What | Set by | Reference |
|---|---|---|
| Contact on the anvil | strip track, terminal stop, feed finger, hold-down | applicator |
| Conductor, lateral, during lay-in | fork tines, within ±1 mm | fork pivot, bolted to the applicator base |
| Conductor, lateral, at first die touch | the ram finger's V, bolted to the ram and so to the crimpers | applicator ram |
| Conductor, axial | tip flush-cut in the cassette slot; strip line referenced to it; shuttle X; confirmed by the picture | cassette datum |
| The band | the clamp edge is the split root, so every fold happens in free conductor | cassette |
| Crimp height | applicator dial, set once against micrometer readings; press bottom dead centre | applicator and press |

**What drives the crimp and carries its force.** The press motor, its crank and
its cast frame, through the applicator's own crimpers: 1.5–2 t capacity
against a 0.8–2.6 kN crimp [facts §4].

**How it knows it worked.**
- **Before firing:** the waiting contact upstream looks right; the conductor is
  over the anvil at the right X and Y. On a fast press nothing can be seen
  between lay-in and crimp; [b1b](b1b-applicator-in-slow-crank-press.md) can
  stop there.
- **After:** brush, bellmouth, closed wings, and the insulation edge in the
  window between barrels, compared with taught good crimps.
- **Continuity.** The loom's far end sits in a pogo block on its cut face
  (ribbon-as-pallet a6; P75-E2 conical pogo pins, $6.49 per 100 [Prime]), and the
  applicator body is grounded. After the crimp, far-end channel *i* to the
  applicator reads continuous through the contact: the right conductor, and
  connected, before the contact leaves the anvil.
- **Proof pull:** 20 N, half JST's 39.2 N minimum [facts §1], with the punch
  already lifted, so it tests the crimp and not the tool's grip.
- **Crimp height:** measured by the person with a crimp micrometer on the first
  crimps of a session. The press and applicator hold bottom dead centre
  mechanically.

**What the person does.**
- Cuts the ribbon, lays it in the cassette channel and closes the clamp: ~20 s
  per end [estimate].
- Docks the cassette at the prep station and starts it (~20 s per end), closes
  the fold lid (~5 s) and seats the cassette on the shuttle.
- Inserts the contacts into the housing by hand, or loads a housing for the
  insertion extension below.
- Changes reels and measures crimp height each session.
- About **27 attended minutes per unit** with hand insertion and **22** with
  the insertion extension, against **46** for today's hand method, all counted
  with procedure-is-the-machine's task library [calc wave2 §5]. Compare the
  rows, not the absolute minutes.

## Steps it covers and what it hands back

- **Covers:** supply contacts (reel), place the contact on the conductor
  (post-feed, fork, ram finger), crimp both barrels and cut the tab in one
  stroke, verify the crimp (pictures, continuity, proof pull), and with the
  extension, insert.
- **Partly covers:** splay. The band and tines handle conductors that are
  already split.
- **Hands back:** cutting and loading cassettes, the fold lid, splitting and
  stripping unless a prep station is built, insertion unless the extension is
  built, reels, crimp height by sample.

## The borrowed machine

| Part | What it is | Evidence (observed 2026-09-28) |
|---|---|---|
| 1.5 / 2 t mute press | Motor-driven bench crimp press, foot switch, 30 mm stroke, interchangeable applicators, 110/220 VAC, 38–169 kg by model, "automatic terminal feeding"; the operator "put[s] the wire into terminal, then press[es] foot switch" | Sanao on Made-in-China: **US$310 at MOQ 1**, $300 at 10+; applicator not included (US$125–150); freight "contact supplier"; 50 kg crate ([Made-in-China](https://sanaoelectronic.en.made-in-china.com/product/LtTrEpiOqDkW/China-1-5t-2t-Mute-Terminal-Crimping-Machine-Wire-Terminal-Crimp-Cable-Crimper-Equipment-for-Jst-Terminal-Crimping.html); [Sanao specs](https://www.sanaoequipment.com/1-5t-2t-mute-terminal-crimping-machine-product/)). eBay 1.5 T semi-automatic at $968.30 (search result, not opened). **No Prime listing found** [Prime] |
| OTP side-feed applicator for XH | Cam-fed horizontal applicator; feeds, crimps both barrels, shears the tab | eBay listings for "XH2.54 / 1.25 / SM / 3.96 / 5557 / PH2.0" at **$163.99–166.99 plus $80–90 shipping** (search result; eBay blocked fetch); Sanao US$125–150. **No Prime listing found** [Prime] |
| XH contacts on reel | SXH-001T-P0.6 or a clone on its carrier | Digi-Key reel 1,329,000 in stock at $0.0235 at 8k; LCSC CJT clone reel 665,523 at $0.0079 [facts §6]. No Prime listing for reels [Prime] |
| Post-feed cam | The mini-applicator's feed cam has two mounting positions: "post-feed" or "automatic" (the default) and "pre-feed" or "manual" | WERI manual §7 [mfr]. JST's CDS SXH001-06/CMKS-L also lists post-feed or pre-feed cams [facts §2]. Whether the OTP unit carries both is unconfirmed [assumption: OTP units follow the WERI pattern] |
| Wire hold spring | A sprung leaf in the ram stack that holds the wire during the stroke | JST MKS-L manual p. 19 [mfr]. The OTP unit's slot is unconfirmed |

The press cycles once per pedal closure in roughly half a second, with
adjustable speed [source: Sanao]. Presses of this class are cycled by hand with
a spanner for setting up, as the WERI manual instructs [mfr]. The applicator
does all of "place the contact": feed, locate, hold down, shear [prior-art §3].

**What adapting it takes.**
- **Trigger.** A relay across the foot-switch circuit. The pedal on these
  presses is a plain contact closure [assumption; check the socket].
- **Cam.** Move the feed cam to post-feed if the unit arrives in pre-feed.
- **Ram finger.** A bracket on the ram's T-head, or the factory wire hold
  spring.
- **Mounting.** A bracket so the fork pivot bolts to the applicator base.
- **Guard.** An enclosure with an interlocked door, because the press now fires
  with nobody's foot on it.
- **Contacts.** A reel matched to the applicator.

## Why post-feed with a ram finger

A pre-feed applicator advances the next contact on the upstroke. On a fast
press that happens 50–90 ms after the punch clears the crimped contact
[procedure calc §2], while the crimped contact and its conductor are still on
the anvil axis, and the incoming contact shoves them sideways.

**A compliant fork has no force window** [calc wave2 §1]:
- The 60 strands slide on each other and bend one by one. Their plastic moment
  is 0.36–0.51 N·mm, so a side push of **24–85 mN** at the contact, 6–15 mm
  from where the conductor is held, sets a permanent bend.
- Lay-in side loads on the fork are 8–330 mN for a 0.1–0.5 mm offset at a
  4–8 mm lever, and 250–2,000 mN wherever a presser foot presses the
  insulation down.
- A holder that yields below 24–85 mN cannot hold the conductor during lay-in;
  one that holds it bends the conductor before it yields. Whatever holds the
  conductor must be **off** it before the feed moves.

On a fast press that can only happen in the ram's own timing. **Post-feed**
brings the next contact on the downstroke, under a conductor held above the
wings, and nothing moves on the upstroke. The part that brings the conductor
down rides the ram, so it lifts with the ram. The fork only holds Y and lets the
conductor slide down.

**A second route on the same press: a pneumatic snatch.** Keep pre-feed with
the conductor-holding parts on the ram, and let a proximity switch on the ram at
4–6 mm up the upstroke fire a 5/2 valve (TAILONZ 24 V, $16.99 [Prime]) and a
16 mm air slide that snatches the cassette back 7 mm before the feed finger
moves. It takes 22–48 ms including the valve, against the 50–90 ms window [calc
wave2 §1, piston speed and valve response estimated]. It keeps the "contact
waiting on the anvil" picture, it is tight, and it adds a second fast mechanism
beside the press. The DeWalt compressor is on hand [repo].

## The waiting contact and the mis-feed

In post-feed the anvil is empty at rest and the contact arrives under a
conductor already on its way down. A rolled, doubled or half-fed contact is then
crimped onto conductor *i*, and the redo is a whole-end cut-back of ~6 mm:
0.4 to 35 looms scrapped over the program at 2 to 10 % bad crimps [procedure
calc recovery_length].

- **Look one pitch upstream at rest** (step 1). The waiting contact on the
  carrier is the one that will feed. If the strip guides hide its barrels, a
  small mirror or a side view along the carrier is the next try.
- **Run from a reel only.** An 8,000 reel is threaded once. Digi-Key's
  100-piece cut strips mean a threading event every ~1.9 units, and a strip
  kinked in its bag is what a feed finger mis-indexes.
- **Continuity after the stroke** still catches a missing contact (no path from
  the far end to the applicator), and the conductor then goes back to the band
  uncrimped for another try.
- [b1b](b1b-applicator-in-slow-crank-press.md)'s stoppable crank shows the
  contact alone on the anvil before any conductor arrives; that is the full
  repair.

## The neighbours: one flat band, two tines

At the anvil the punch plates straddle the anvil and come down beside it. The
zone that crushes anything lying at anvil level is estimated at **3–6 mm either
side of the axis** [estimate; measure on the applicator that arrives]. At ribbon
pitch two conductors each side of the target lie inside even a 3 mm half-width
[calc geometry §1]. With the strip attached, the only open side is behind the
tooling: below the anvil is strip, track and shear; upstream are the next
contacts on their open wings; above is the punch. So every conductor but the
target is folded back over the clamp edge.

- **Split length.** The fold line must be in front of the tooling: tip-to-face
  depth 6–12 mm [estimate] plus 2–3 mm for the bend and the fork, so the split
  is **8–15 mm** [calc geometry §1].
- **Fold.** An ungrooved lid folds the split conductors back as one flat band
  in one motion (~5 s by hand, or the shuttle against a ramp). A grooved lid
  cannot sort them in one shot: a conductor beyond the first neighbour is
  caught by its own groove only if the groove pitch there is under 1.9–2.3 mm
  [procedure calc §12].
- **Pick.** Split conductors touch only along a line. The two blunt tines ride
  down the V-valleys either side of the target and wedge each neighbour aside
  by one tine thickness.
- **Return.** A crimped conductor goes back to its own place in the band, box in
  its pocket, so the band keeps its order and its valleys.
- **Copper keeps its shape.** Each root goes through about four reversals: park,
  lay forward, re-park, straighten for insertion. That is well under 1 % of
  strand fatigue life [procedure calc §11]. A set kink remains at the root.
  At 12 mm of free length a residual 5°, 10° or 15° shortens that conductor's
  front by 0.05, 0.18 or 0.41 mm at a gang insertion [TS §10], so the insertion
  comb runs root to tip twice to straighten before any gang push.

**Variant: split on demand, edge first.** The end is not fully split at the
prep station. A partial slit ([b4](b4-laser-slits-and-scores.md)'s laser to
70–90 % of the web, or b6's blade with a depth shoe) leaves a 0.05–0.2 mm
ligament, and the fork peels only the edge conductor, at ~1–5 N [procedure calc
§9]. The rest stays a ribbon and folds as one flap. The peel runs tip to root
and stops at the clamp, so the clamp edge is the root by construction. It trades
the prep station's full split for a peel per conductor, and depends on the peel
staying in the slit.

## Length geometry at the housing

The tips are trimmed at the cassette datum with the conductors straight at
ribbon pitch. At the housing they diverge to 2.5 mm, so each outer conductor
runs on a diagonal and its front lands short [procedure calc §7]:
- a single 4P or 5P lands 0.05–0.16 mm short, inside the ~±0.3 mm a gang
  insertion wants;
- J4 lands 0.37 mm short and J1 0.35–0.67 mm short, at splits of 15 down to
  8 mm.

For J1 and J4 the cassette's trim slot is a per-loom curve offset by those
amounts, so the tips are trimmed in the pose of the finished housing, before
the end is split and stripped. For single ribbons the slot is straight. Whether
a curved slot and a flush cutter hold ±0.05 mm is untested.

## References and tolerances

| Quantity | Needed | What provides it |
|---|---|---|
| Contact on anvil | the applicator's own (floats 0.003–0.005 in. approaching the anvil, Mecal [prior-art §3]) | applicator |
| Strands into the conductor barrel | 0.72 mm bundle into a 1.68–1.90 mm open barrel [facts §1] | the ram finger's V |
| Insulation into the open insulation wings, per side | clone contacts ±0.21–0.83 mm; Würth analog ±0.25–0.35 mm; JST's 1.95 mm envelope, if it is the open width, ±0.08–0.18 mm [TS §4] | the ram finger's V, set once on its bracket to centre within ~±0.05 mm [estimate]; with genuine JST that setting is the whole margin |
| Conductor axial | insulation edge inside the ~0.6–1.0 mm window between barrels, brush visible, roughly ±0.3 mm [estimate] | cassette datum, flush-cut tip, strip line from the datum, shuttle X; camera confirms before firing |
| Waiting height | conductor centre ≥4.6 mm above the barrel floor while the contact feeds in | fork height; clone wing height 3.2 +0.25 mm plus 0.3 mm [calc wave2 §1] |
| Ribbon pitch accumulation | 1.7 ±0.1 mm per conductor [facts §7] | under-width channel and centred datum: ≤0.23 mm on a 5P; the tines find the valleys regardless |
| Strip length Ls | a per-reel value: 2.4 mm for genuine JST [facts §1]; 1.85–2.1 mm for clone contacts [TS §3] | the prep station's setting, from the reel in use |
| Crimp height | ±0.05 mm around JST's value (0.8–0.9 mm expected, not public) [facts §1] | applicator dial, set once against micrometer readings |

## Printed and bought

- **Printed.**
  - Cassette: PETG plates, under-width channel, guillotine slot, fold lid,
    pins, magnet pocket, pocket row.
  - Fork body in PET-CF, with steel shim tines (1095 shim assortment, $53.39
    [Prime]).
  - Ram-finger bracket: PET-CF body, steel V insert, spring.
  - Neck-fork holder for the proof pull (the fork itself a 0.3–0.4 mm steel
    leaf; feeler gauge set, $8.99 [Prime]).
  - Shuttle brackets, camera mount, guard panels.
- **Bought.**
  - Press, applicator and reel: eBay or Made-in-China, not Prime.
  - MGN12 rails and carriages, NEMA 17 with Tr8×2, SKR Pico or MKS DLC32, one
    DS3218 servo, relay module, interlock switch, bar load cell with HX711,
    pogo pins: all [Prime] rows above.
  - For the snatch route: a 16 mm air slide (no Prime row), the 5/2 valve and
    an M8 proximity switch.
- **On hand:** ELP camera, 24 V supply, compressor [repo tools.md].

Rough cost:
- press $310 + applicator $125–165;
- freight, quoted rather than listed: a guess of $150–300 for a 50 kg crate
  [estimate];
- shuttle ~$150–200 [Prime rows];
- XH reel $188 (Digi-Key) or a clone reel ~$60.

## The insertion extension

An insertion station on the same Y rail beside the applicator: the Molex 1978
pattern of crimp, then adjacent insertion [prior-art §0].
- A housing sits in a nest on a small Y stage.
- The fork lays each crimped conductor forward through a straightening comb at
  2.5 mm pitch.
- Two slide-along jaws close lightly on the conductor, slide forward until they
  meet the insulation crimp, then clamp and push the contact home (Molex US
  4,936,011 [prior-art §5]).
- A pull-back passes when force arrives before distance (Boeing US 11,374,374
  [prior-art §5]).
- The fan from 1.7 to 2.5 mm forms as the housing indexes 2.5 mm per cavity
  while the cassette indexes 1.7.
- **Crossings.** J4's 3P GND goes to cavity 2 across three 4P conductors, and
  J7's 5P GND to cavity 7 across CLO and CHI [digest]. The crossing conductor is
  inserted **last**, so every other conductor is already tethered and the last
  one lands on top. The recipe carries an insertion order separate from the
  crimp order.
- **Trims.** J2's and J7's unused conductors are ones the fork never takes; a
  servo flush cutter at the clamp edge trims them at the root, by recipe,
  before the band is folded.
- Insertion force and retention are unmeasured [facts Unresolved 4].

**Recipes.** One per loom: crimp order, insertion order, skips, trims. Two
ribbons into one housing (J1, J2, J4, J7) are two ribbons clamped edge to edge
in one cassette.

**Redo.** A bad crimp means cutting the whole end back ~6 mm and going round
again, which costs loom length on every redo when the loom is cut first.
[b8](b8-spool-fed-borrowed-line.md) runs the same applicator at the spool, where
a redo costs only spool.

## Problems and their repairs, as they stand

- **The pre-feed runs into the crimped contact on a fast press.** Post-feed with
  a ram finger is the arrangement above; the pneumatic snatch is a second route;
  b1b's stoppable crank a third.
- **Nothing is seen between lay-in and crimp.** The look one pitch upstream, the
  picture over the empty anvil and the after-picture bracket the stroke; a
  conductor seated wrongly by the finger is caught after the fact and costs a
  whole-end redo. b1b can stop 2–4 mm above bottom for a look.
- **The press fires on a relay.** A 2 t press cycling on its own is this idea's
  most serious hazard. The repair is an enclosure panel across the front with an
  interlocked door in series with the relay coil; only the fork and cassette are
  inside the guard. The press's own finger guard is modified or replaced to let
  the fork in, which changes a safety part.
- **The applicator is set by its vendor for their contact.** Chinese applicator
  vendors set feed pitch, track and crimp height for a named terminal
  [assumption, typical of the trade]. Buy the reel from the vendor, or name
  SXH-001T-P0.6 when ordering. Carrier pitch and pilot hole must match the feed
  finger; neither is published [facts Unresolved 2]. The strip length follows
  the contact: 2.4 mm on a clone barrel gives a 0.40–0.85 mm brush that reaches
  the box over most of the range [TS §3].
- **The feed finger's envelope over the wire path** [assumption; nothing
  published shows it]. The pilot holes lie on each contact's centreline, under
  the wire's path. In post-feed the conductor already hangs over that line when
  the finger moves; near the barrels its underside is ~3.75 mm above the floor,
  sloping down toward the root at 14–25°. A finger in the station contact's own
  hole, or a lever standing more than ~3 mm above the carrier, would meet the
  held conductor. Stroking the applicator slowly in b1b's jack test with a
  conductor held at 4.6 mm settles it.
- **The proof pull needs a place to bear.** The box is 1.85–1.95 mm wide and
  the crimped insulation barrel ~1.8–2.0 mm, so a slot "narrower than the box
  and wider than the crimped barrels" may not exist; a plate reaching below the
  floor meets the lance tip end-on [TS §11]. The neck fork above the floor
  (step 8), or a plate edge ~2.0 mm above the floor on the box roof's rear edge,
  bears on the box and not the lance.
- **No in-line crimp height.** The camera, continuity and proof pull catch gross
  faults; crimp height is checked by sample, as industry does every 250–500 parts
  [prior-art §4]. A frame strain gauge on this fast press gets only ~2 HX711
  samples in the compaction window [calc presses §1b]; a force curve needs b1b.
- **Scrap carrier** leaves at one pitch per crimp, ~0.4–0.5 m per unit
  [estimate from 7–9.5 mm pitch], into a bin.

## Contribution

- The industry's own machine-fed configuration (post-feed, wire held above, the
  holding part on the ram) applied to a ribbon end, with a printer-parts
  shuttle as the "machine".
- The rule that no sprung holder can both locate a stranded 22 AWG conductor and
  yield before it sets: holders come off by timing, not compliance.
- The flat band and valley tines as a way to present one split conductor at a
  time to tooling that crushes everything within a few millimetres.

## Major unresolved problems

- **Applicator geometry.** Tooling half-width, tip-to-face depth, room for the
  ram finger beside the crimpers, whether the fork fits inside the guard: all
  come with the applicator and set the 8–15 mm split.
- **Post-feed on the OTP unit.** Whether it has both cam positions, and where in
  the downstroke its post-feed finishes. The finger meets the waiting conductor
  when the crimper face is ~7 mm above the floor, so the feed must be done by
  then [calc wave2 §1].
- **Seating on the fly.** Whether a ram finger seats a raised, angled conductor
  into the fresh contact cleanly in a ~0.5 s stroke, strands and all.
- **Tines in the band.** Whether blunt 0.25 mm tines enter the valleys without
  notching silicone, which tears from notches.
- **Contact match.** Genuine SXH against the vendor's clone, the reel's pitch
  against the feed finger, and the V's centring with genuine wings.
- **Safety** under automatic firing.
- **Freight and supply.** No Prime route for the press, applicator or reel;
  freight is quoted for a 50 kg crate; 110 V is listed but unconfirmed on the
  unit.
- **Press behaviour.** Whether the mute press's bottom dead centre is purely
  mechanical or servo-positioned, which bears on crimp-height drift
  [assumption].

## What rests on what

- **Derek:** placing, holding and crimping is the step he most wants
  automated; slowness is acceptable.
- **Facts** [facts]: contact and barrel dimensions (clone drawings), pull-out
  minimum, crimp force range, stock and prices, the applicator's feed and cam
  options, strip length 2.4 mm (JST).
- **Calculations:** the force window [calc wave2 §1]; neighbour zone and split
  length [calc geometry §1]; lateral capture by supply, strip length by
  contact, the kink and the proof-pull geometry [TS §3, §4, §10, §11]; person
  minutes [calc wave2 §5]; feed timing and recovery [procedure calc].
- **Estimates:** the 3–6 mm tooling half-width and 6–12 mm tip-to-face depth;
  freight; per-end loading, prep and folding times.
- **Assumptions:** the OTP unit follows the WERI pattern (two cam positions, a
  wire hold spring slot or room for one); the foot switch is a dry contact; the
  applicator has a crimp-height dial (mini-applicators in general do [facts
  §2]); a 20 N proof pull does not harm a good crimp.
