# v9 — Tack at the anvil: the watched tack made inside a stopped crank applicator, on a contact still on its carrier

Explorer: machine-that-sees-and-learns.

Combines this view's [v8](v8-tack-look-crimp.md) with borrowed-machines'
[b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md) and
[b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md).

Related:
- Branch [v9b](v9b-tack-by-hand-on-the-jack-test.md): the same tack, look and
  crimp by hand on b1b's jack test, in the first week, with no motor.
- Branch A1 (below): the same on
  [b1c](../../borrowed-machines/ideas/b1c-one-shaft-applicator-press.md)'s one
  cam shaft.
- For loose kit contacts, which an applicator cannot take: v8's bench tack
  station feeding hand-tool-as-press's one-nest SN die set
  ([a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md)),
  and force-and-form's tack on a docked strip segment
  ([f9b](../../force-and-form/ideas/f9b-tack-on-the-strip.md)).

Sketch: [`../sketches/w3-v9-tack-at-the-anvil.svg`](../sketches/w3-v9-tack-at-the-anvil.svg)
(schematic side elevation and crank-angle timeline).

Numbers:
- **[bm W §n]**: borrowed-machines'
  [`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt);
- **[calc: w3_final §n]**: this view's [`w3_final.out.txt`](../calc/w3_final.out.txt);
- **[calc: wave2 §n]**: this view's [`wave2.out.txt`](../calc/wave2.out.txt);
- **[bm wave2 §n]**, **[bm X §n]**: borrowed-machines'
  [`wave2.out.txt`](../../borrowed-machines/calc/wave2.out.txt) and
  [`exchange_ribbon_as_pallet.out.txt`](../../borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt);
- **[ff w2 §n]**: force-and-form's [`wave2.out.txt`](../../force-and-form/calc/wave2.out.txt);
- **[calc: w3_on_hand_tool_as_press §n]**: this view's
  [`w3_on_hand_tool_as_press.out.txt`](../calc/w3_on_hand_tool_as_press.out.txt);
- **[rap P §n]**: ribbon-as-pallet's
  [`exchange_on_machine_that_sees.out.txt`](../../ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt);
- **[Prime]**: a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
  observed 2026-09-28.

Axis words: "along the wire" and "across".

## Picture it

**Where things start.**
- **The press.** b1b as it stands: an OTP side-feed XH applicator on the bed of
  the VEVOR 12-ton H-frame press [repo: tools.md], its feed cam in
  **pre-feed**, so a contact waits open on the anvil at rest, still on its
  carrier. A 15 mm crank under the press's top beam drives the applicator's
  ram through a connecting rod with a preloaded disc-spring stack in it. The
  crank sits at top dead centre.
- **The ribbon end.** In b1's cassette on a two-rail shuttle in front of the
  applicator:
  - split, stripped to the reel contact's strip length, flush-cut;
  - every conductor folded back 180° over the clamp edge as one flat band on
    the cassette's top plate, pointing away from the press, so no waiting
    conductor ever lies over the applicator's upstream pressure plate or its
    wire-side scrap cover;
  - the loom's far end, unterminated because the XH end is made first, in a
    pogo block; the applicator body is grounded.
- **Two swing-in arms** on dowel pins in brackets bolted to the applicator base,
  on the downstream side, where only spent carrier leaves:
  - **The T-arm.** A short vertical guide holding a 1.2–1.5 mm steel former
    plate. Its lower edge is the applicator's own insulation-crimper profile,
    taken from a Revopoint scan and cut 0.1–0.2 mm wider (below). A DS3235
    35 kg·cm servo ($27.99 [Prime]) drives it through a 1:1 lever to a screw
    stop. A 20 kg bar load cell with an HX711 sits in the link.
  - **The M-arm.** A 10 mm first-surface mirror at 45° (cut from the
    100 × 100 mm plate, $20.90 [Prime]) with LEDs round its opening, two of
    them at 60–75° elevation on opposite sides of the barrel. The 16 MP IMX298
    M12 camera ($69.99 [Prime]) with a 12 mm lens ($9.99 [Prime]) looks into
    the mirror horizontally.
- **A second camera** across the anvil at wing height from the downstream
  side, with a thin side-lit diffuser vane standing between the active contact
  and the next contact upstream (one strip pitch away, 7.1–9.5 mm
  [xh-facts §1, estimate]).

**One conductor.**
1. **Look at the contact alone.** Crank at top dead centre, nothing near the
   anvil. Present, lance, roll, wings upright, against fiducials on the anvil.
   A bad contact gets b1b's reject turn and never meets a conductor.
2. **Lay in.** The shuttle indexes across. The fork's tines drop into the
   valleys either side of conductor *i* in the band and lay it forward into
   the waiting contact. The foot seats the jacket in the insulation barrel.
   With the crank at top dead centre nothing on the ram hangs within ~23–31 mm
   of the anvil [bm W §3, estimate].
3. **Side look and continuity.** Far-end channel *i* to the applicator reads
   closed: the strands touch the contact, and it is the conductor the recipe
   expects. The side camera sees the bundle in the U and nothing above the
   conductor wing tips.
4. **Tack.** The T-arm swings in to its dowel stop. The former descends at
   ~1 mm/s to its screw stop and closes the insulation wings loosely over the
   jacket, reacting on the applicator's own hardened insulation anvil. The
   cell logs the forming curve up to the knee where the former lands on its
   stop. The T-arm rises and swings out.
5. **Let go.** The foot lifts; the fork opens and parks. The tack alone holds
   the conductor: vertically by capture, since the wings are closed over the
   jacket; along the wire by its 0.2–1.5 N of grip, against tens of mN of
   copper spring-back from the lay-in bend.
6. **The look that matters.** The M-arm swings in; its mirror spans ~4–11 mm
   above the floor [bm W §3]. The LEDs light one at a time. The judge checks:
   - every strand between the wing tips, and none on a tip;
   - nothing silver on the anvil outside the contact's outline;
   - the brush past the front of the conductor barrel;
   - the insulation edge in the window between the barrels;
   - **the bundle's displaced shadow** under each 60–75° LED (below). A strand
     lying on the barrel floor casts none.
7. **Decide.**
   - **Pass.** The M-arm swings out. The station MCU turns the crank fast to a
     taught angle 0.95–1.7 mm above bottom, then crawls the ram at
     0.05–0.1 mm/s on a speed profile indexed to crank angle, checking force
     against angle every sample. At bottom dead centre both barrels are
     crimped, the insulation crimper re-forms the tack, and the shear cuts the
     tab.
   - **Fail.** The shuttle draws the conductor straight back along its own
     axis, out through the tack. The carrier holds the box. The draw stays
     flat, because the tab bends at 4–12 N of pull along the wire but yields
     at 0.5–1.7 N pushed sideways or up [bm W §4; rap P §3;
     bm X §5]. The empty tacked contact is crimped empty on the next turn (it
     matches the "contact, no wire" reference trace), blown off the anvil in
     the dwell by b1b's puff (TAILONZ 24 V 5/2 valve, $16.99 [Prime];
     compressor on hand [repo]), and the next pre-feed brings a fresh
     contact. A look at the conductor's insulation edge decides between
     retrying it as it is and re-stripping it.
8. **Dwell,** 40–100° after bottom dead centre, before the feed finger moves:
   - the shuttle withdraws the crimp ≥7 mm along its axis;
   - a thin fork drops into the neck behind the box and bears on the box's
     rear face above the floor, clear of the lance
     ([terminal-supply's repair of b1's catch plate](../../../exchange/terminal-supply--on--borrowed-machines-w3.md));
   - a 20 N proof pull through the cassette's load cell;
   - a backlit silhouette of the crimp over a blade at that withdraw position,
     with the box's front 1 mm read as a roll gauge ([v5](v5-inspection-booth.md)).
9. **Finish the turn.** The crank completes its revolution; the pre-feed
   advances a fresh contact onto the empty anvil. The fork parks the crimp in
   its place in the band, and the shuttle indexes.

**What locates what.** The reference for "fixed" is the applicator base
throughout.

| Moment | Contact | Conductor |
|---|---|---|
| Lay-in | The applicator's strip track, terminal stop and feed finger | Fork tines across; cassette datum and shuttle along the wire |
| Tack | The same, with the insulation barrel on the hardened insulation anvil | Fork and foot, until the tack closes |
| Look | The same | The tack |
| Crimp | The same | The tack and the contact |
| Pull | The neck fork on the box's rear face | The cassette clamp |

The former's guide is doweled to the applicator base, so its profile lines up
with the insulation crimper that finishes the tack. Its screw stop sets only
the tack height, which is loose on purpose: ±0.05–0.1 mm is enough.

**What drives the crimp and carries its force.**
- **The crimp:** b1b's crank. 0.8–2.6 kN [xh-facts §4] passes through the
  rod's disc stack (preloaded to ~4 kN, so it does not move during a good
  crimp) and the 12-ton frame.
- **Drive:** the NEMA 23 and DM542T through a 10:1 planetary (STEPPERONLINE,
  $48, 10 N·m permissible [Prime]), or a 30:1 worm that self-locks at every
  stop (Heechoo, $120 [Prime]; output torque not stated). The bench's NEMA 23
  lives in the weld rotator [repo], so this is a second motor or a borrowed
  one.
- **The ceiling:** the disc stack's travel trips a switch wired into the
  drivers' enable line with the e-stop and the lid switch. The force limit
  then does not live only in firmware ([v7](v7-the-run.md)).
- **The tack:** 33–132 N from the servo [calc: wave2 §5], reacting through the
  applicator's insulation anvil. With a 1:1 lever the servo can push
  137–172 N [calc: w3_final §2]; the stop takes the excess.
- The shuttle, the fork and the arms carry a few newtons at most.

**How it knows it worked.** In order:
- the contact alone, before any conductor;
- continuity and identity at lay-in;
- the forming curve at the tack (no jacket reads low; a jacket off centre reads
  lopsided [estimate]);
- the top look through the mirror, with the shadow test, and the side look;
- force against crank angle through the crawl, against the lot's envelope;
- the stack switch;
- in the dwell: roll-corrected silhouette height, the 20 N pull, and
  continuity through the crimp.

**What the person does.** As b1b:
- cuts the ribbon, loads and docks the cassette, closes the fold lid;
- changes reels and empties the reject cup;
- inserts into housings by hand, or keeps an insertion station stocked;
- answers [v7](v7-the-run.md)'s asks;
- checks crimp height by micrometer on samples until the silhouette and the
  crank's re-touch are trusted.

That is ~27 attended minutes a unit with hand insertion [bm wave2 §5].
The machine takes 72–142 s a conductor, 1.1–2.1 h a unit [bm W §11].

**Steps it covers:** supply contacts (the reel), place the contact on the
conductor (fork and foot, then the tack), hold both in the die (the
applicator's track and stop; the tack), crimp, verify the crimp (two looks
before anything irreversible, force against angle, stack switch, dwell
silhouette, proof pull, continuity).

**What it hands back:** cutting and cassette loading; splitting and stripping
unless a prep station is built (borrowed-machines
[b6](../../borrowed-machines/ideas/b6-pierce-at-the-root-pull-to-the-tip.md),
[b7](../../borrowed-machines/ideas/b7-borrowed-strip-head-one-conductor.md),
or this view's [v6](v6-patient-cell.md)); insertion; reels; sample crimp
heights.

## Where it comes from

A combination of this view's [v8](v8-tack-look-crimp.md) (a light tack, then
a straight-down look, then the heavy crimp) with borrowed-machines'
[b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md) (a
bought OTP side-feed XH applicator in pre-feed, driven by a slow crank in the
idle 12-ton shop-press frame) and
[b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md)'s
cassette, fork, foot and far-end pogo block. The stroke is run by
[v7](v7-the-run.md); the after-crimp silhouette is
[v5](v5-inspection-booth.md)'s. Proposed by borrowed-machines in its
[exchange on this view](../../../exchange/borrowed-machines--on--machine-that-sees-and-learns-w3.md)
(Combination A).

## Why the anvil is both stations

- [v8](v8-tack-look-crimp.md) at a bench station has **two datums**. It
  carries a tacked contact from T to C and needs a keyed box slot at C. An
  applicator has no such slot: its anvil locates a contact by strip track,
  terminal stop and feed finger, and a loose contact lowered onto it has
  nothing to stop it along the wire. The side-feed track leaves no room to add
  one without rebuilding the anvil block [borrowed-machines' exchange on this view, reading the MKS-L manual pp. 9, 20].
- Here T and C are one anvil. The contact never leaves its datum between the
  tack, the look, the crimp and the tab shear.
- b1b alone has to hold the conductor with a fork and a foot until the
  crimpers arrive, and no compliant holder has a force window that lets them
  stay [bm wave2 §1]; they must leave by timing, which on
  [b1c](../../borrowed-machines/ideas/b1c-one-shaft-applicator-press.md)'s
  shaft means a fork swing racing the descending ram. b1b's gate picture is
  oblique, under a raised punch.
- Here the tack is the holder. The fork and foot leave before the crank turns
  at all, and the gate looks straight down through a mirror.
- The back-out reacts on the carrier. v8's bench back-out needs a rear shoulder
  in the contact's undimensioned neck; this one needs none.

## The tack on this contact

**Height.** The tack is defined against the final insulation crimp of *this*
applicator on *this* wire, not as an absolute figure:
- tack height H_t = H_f + 0.2–0.5 mm, where H_f is the applicator's own
  insulation crimp height on the ribbon, measured on jack-test crimps
  ([v9b](v9b-tack-by-hand-on-the-jack-test.md));
- estimates of H_f on 1.7 mm silicone run 2.0–2.3 mm (force-and-form) to
  2.03–2.46 mm (an elliptical section as the upper bound) [ff w2 §5;
  calc: w3_on_hand_tool_as_press §9], so tack heights of 2.2–3.0 mm
  [calc: w3_final §1];
- an absolute 2.3–2.5 mm can fall below the final height at the narrow end,
  and would then be the crimp itself [bm W §1].

**Width.** The former is cut **0.1–0.2 mm wider** than the insulation crimper
it copies:
- At the crimper's own width the closed barrel squeezes the 1.7 ±0.1 mm jacket
  sideways by 3–22 %. force-and-form's thin-layer grip model puts that at up
  to ~7 N [calc: w3_final §1], past the 1.5 N at which a tacked contact must
  still slide off for a back-out.
- 0.1–0.2 mm wider brings the side squeeze to 0–17 % or 0–11 %, and more of
  the grip comes from the wing tips on the jacket's top, which the stop's
  height sets.
- The grip model spans a factor of eight, so the setting is found on the
  bench: v9b tacks a few contacts at each stop and pulls each off with the
  0.1 g scale.
- **What it asks of the crimper.** The applicator's insulation crimper has to
  take a tacked barrel 0.1–0.2 mm wider than its own width into its mouth
  [assumption: a flared B-crimper entry does; the jack test shows it].

**The stroke after a tack.** With both crimpers on one ram [calc: w3_final §1]:
- the conductor wings are met first, with 0.62–0.87 mm of stroke left;
- the insulation crimper meets the tacked barrel with 0.2–0.5 mm left, after
  the conductor wings have curled for 0.12–0.67 mm;
- compaction, the last 0.1–0.2 mm, starts with that retouch or after it.

The jacket is held by the tack through compaction either way. An untacked
stroke on this silicone meets the insulation wings at 0.29–1.40 mm left,
before or after the conductor wings depending on H_f. Whether a tacked and
re-formed insulation crimp ends up like a one-pass crimp is a sectioning
question: force-and-form's [f3b](../../force-and-form/ideas/f3b-two-station-forming.md)
has the arms, and v9b makes the sections.

## The look: a shadow, not a focus slice

Held by its jacket, the gathered 0.72 mm bundle hovers **0.30–0.52 mm above
the conductor-barrel floor**, its top 0.98–1.25 mm up against wing tips at
1.50–1.60 mm [bm W §2; the insulation and conductor floors are taken to share
one plane, as the clone drawings show].
- A strand lying on the floor has left the bundle.
- Two focus slices cannot separate 0.3–0.5 mm: depth of field is ~0.55–0.76 mm
  at 122 px/mm and ~1.1–1.5 mm at 86 px/mm [bm W §2, estimate].
- **An LED at 60–75° elevation** throws the bundle's shadow 0.08–0.30 mm
  sideways on the floor: 10–36 px at 122 px/mm. The lowest elevations that
  still reach the floor past the walls are 53–66° [bm W §2].
- The judge looks for silver with no displaced shadow beside it, under two
  LEDs on opposite sides in turn.
- **Unproven:** whether tinned strands on a tin floor give a shadow edge a fit
  can find. One photograph of a tacked conductor settles it.

## The crawl and the ceiling

- A crank turned at constant speed passes 0.3 mm above bottom at 0.67 mm/s on a
  30 s revolution, so one HX711 sample is 4.9–8.4 µm of travel: hundreds of
  newtons into a stiff obstruction [bm W §5].
- The station MCU therefore profiles the stepper so the ram crawls at
  0.05–0.1 mm/s from a taught *angle* 0.95–1.7 mm above bottom: 9–34 s. At
  0.05 mm above bottom through 30:1 that is 582 microsteps/s, well inside a
  DM542T's range [bm W §5].
- The envelope is indexed to crank angle. A doubled contact, met ~0.2 mm early,
  is stopped at ~200–212 N with an HX711 on the rod's strain gauges
  [bm W §5; the 200 N band is an estimate].
- The disc stack stays as the ceiling if the MCU is wrong.

## Crimp height

- **Set:** the applicator's dials, or b1b's stepper wedge under the base
  (35–52 µm of anvil rise per mm of wedge, self-locking under 3 kN
  [terminal-supply wave2 §8, via b1b]).
- **Read, twice:**
  - the dwell silhouette on the blade, corrected for roll by the box;
  - the crank as its own gauge (from [v3](v3-press-that-runs-experiments.md)'s
    campaign on the crank): a 10 N re-touch read by a 14-bit shaft encoder
    gives 0.2–0.5 µm of height per count near the re-touch point, once throw,
    rod and bottom dead centre are calibrated against one gauge block
    [bm W §6]. With both crimpers on one ram a re-touch reads whichever barrel
    springs back higher.

## Branch A1: on b1c's one shaft

[b1c](../../borrowed-machines/ideas/b1c-one-shaft-applicator-press.md) puts the
fork, foot, withdraw and pull on printed cams on the crankshaft. The room for a
former (~14–17 mm) and a mirror (~11 mm) exists only near top dead centre
[bm W §14]:

| Shaft angle | Crimper faces above the anvil |
|---|---|
| 0° | ~30.8 mm |
| 40° | ~26.8 mm |
| 90° | ~14.7 mm |
| 115° (b1c's gate) | ~8.5 mm |

So on b1c the shaft stops at 0–40° for lay-in, tack and look. The T-arm, the
M-arm and the along-wire withdraw for a back-out run on their own servos, not
on cam 4. The cams keep the crimp, the dwell withdraw, the pull and the park.
The fork never swings under a descending ram.

## Printed, steel, bought

**Printed:** arm brackets' covers, the servo lever, the mirror carrier, the LED
holder, the vane holder, the camera mounts, guard panels. The cassette,
shuttle parts and fork body are b1's.

**Steel:**
- the former: 1.2–1.5 mm hardenable flat stock (O1 or A2 ground stock; sourcing
  request), filed or wire-cut to the scanned profile plus 0.1–0.2 mm;
- the arm brackets and dowel pins (precision-ground M6 dowels, $6.49 [Prime]);
- the neck fork: 0.3 mm blue-tempered shim (1095 assortment, $53.39 [Prime]).

**Bought:**

| Item | Source |
|---|---|
| OTP side-feed XH applicator and a reel | Not on Prime; eBay or Made-in-China [Prime: no listing found] |
| DS3235 35 kg·cm servo | $27.99 [Prime] |
| 20 kg bar load cell with HX711 | sourcing request (the Prime 5 kg pair tops out at 49 N) |
| 16 MP IMX298 M12 camera, 12 mm lens | $69.99 and $9.99 [Prime] |
| First-surface mirror | $20.90 [Prime], cut to 10 mm |
| WS2812B 16-LED rings | $18.99 for five [Prime] |
| 5/2 valve for the blow-off | $16.99 [Prime] |
| NEMA 23 10:1 planetary | $48 [Prime] |
| BF350 gauges and HX711 for the rod | $6.99 and $11.50 [Prime] (b1b's) |
| Disc springs, DIN 2093 A35.5 | Industrial supplier; Prime has only a light stainless assortment [Prime] |

## Major unresolved problems

- **The room under the raised crimpers at top dead centre.** What hangs below
  the OTP crimper faces (hold-down, terminal stripper, wire-hold-spring slot) is
  unknown. The JST MKS-L manual shows a terminal stripper and a pressure-plate
  assembly [via bm exchange]. The former and guide need ~17 mm, the mirror
  ~11 mm; the jack test measures what is there.
- **The former's profile and alignment.** Doweling a guide to the applicator
  base modifies a bought tool. The profile comes from a scan of the crimper.
- **The tack's grip on this silicone,** and the width and height that give
  0.2–1.5 N. v9b's pliers-and-scale pulls settle it.
- **Whether the insulation crimper's mouth takes a tacked barrel 0.1–0.2 mm
  wider than itself** without shaving or folding a wing.
- **Tacked, then re-formed, against one pass,** for the insulation crimp
  (sections).
- **The shadow test on tin.** One photograph.
- **Blow-off.** Whether a 0.043 g crimped empty contact leaves the anvil every
  time.
- **Pre-feed only.** On b1's fast press with post-feed the anvil is empty at
  rest, so there is nothing to tack; this belongs to b1b and b1c.
- **Strip only.** Kit contacts cannot enter an applicator; the reel is bought
  (genuine SXH reel, Digi-Key, $0.0235 each at 8,000 [xh-facts §6]) or comes
  with the applicator. Neither the applicator nor the reel is on Prime, so lead
  time is the vendor's.
- **The applicator interface** (shut height, stroke, spring loads, feed-finger
  timing) is b1b's open problem, measured by the jack test.

## What rests on assumptions

- Room under the crimpers [estimate until the jack test].
- The grip model and the jacket's ±0.1 mm [ff w2 §5; xh-facts §7].
- First touches on clone dimensions without the crimper's mouth flare.
- That the insulation and conductor barrel floors share one plane (the shadow
  geometry).
- Load-cell overload at 150 % of rating [assumption].
- The OTP applicator tolerates any stroke speed and a stopped crank [b1b's
  assumption].
