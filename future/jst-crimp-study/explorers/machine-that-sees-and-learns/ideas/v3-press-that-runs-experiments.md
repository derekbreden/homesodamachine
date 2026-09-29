# v3 — The press that runs its own experiments: it finds the crimp height nobody published, then polices it

Explorer: machine-that-sees-and-learns.

Sketch: [`../sketches/v3-experiment-loop.svg`](../sketches/v3-experiment-loop.svg)
(schematic; the chart is axes only).

Numbers:
- **[calc: campaign §n]** [`../calc/campaign.out.txt`](../calc/campaign.out.txt);
- **[calc: wave2 §n]** [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
- **[calc: cycle_and_cost §n]** [`../calc/cycle_and_cost.out.txt`](../calc/cycle_and_cost.out.txt);
- **[calc: w3_final §n]** [`../calc/w3_final.out.txt`](../calc/w3_final.out.txt);
- **[calc: w3htp §n]** [`../calc/w3_on_hand_tool_as_press.out.txt`](../calc/w3_on_hand_tool_as_press.out.txt);
- **[rap P §n]** ribbon-as-pallet's
  [`exchange_on_machine_that_sees.out.txt`](../../ribbon-as-pallet/calc/exchange_on_machine_that_sees.out.txt);
- **[ff w2 §n]** force-and-form's [`wave2.out.txt`](../../force-and-form/calc/wave2.out.txt);
- **[bm W §n]** borrowed-machines'
  [`exchange_sees_learns_w3.out.txt`](../../borrowed-machines/calc/exchange_sees_learns_w3.out.txt);
- **[Prime]** a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
  observed 2026-09-28.

Run in [v7](v7-the-run.md)'s campaign mode, with Derek at the bench.
Related: coupons are ribbon-as-pallet's production-made ends
([a1](../../ribbon-as-pallet/ideas/a1-pallet-tour.md),
[a5](../../ribbon-as-pallet/ideas/a5-part-fan-strip-in-the-pallet.md)); height
stops from their [a2b](../../ribbon-as-pallet/ideas/a2b-gang-press-stop-die.md);
hit-and-re-touch from force-and-form's
[f3](../../force-and-form/ideas/f3-knee-micropress.md); hosts include
borrowed-machines' [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)
jack test and crank, and hand-tool-as-press's
[a1b](../../hand-tool-as-press/ideas/a1b-pawl-out.md) and
[a5](../../hand-tool-as-press/ideas/a5-two-squeeze-plier.md). Its results feed
[v1](v1-watched-nest.md), [v5](v5-inspection-booth.md), [v8](v8-tack-look-crimp.md)
and [v9](v9-tack-at-the-anvil.md).

## Picture it

**Where things start.**
- **A crimp host with three instruments:**
  1. **A way to set crimp height.** Any of:
     - a stepper-set stop: a fine screw or a wedge under the anvil (force-and-form's
       f3 wedge; b1b's stepper wedge under an applicator, 35–52 µm per mm);
     - hardened stop blocks on a feeler-gauge shim stack (ribbon-as-pallet's
       a2b); sixteen levels are sixteen stacks, and any force source drives it,
       including the idle 12-ton press by hand;
     - **no settable stop at all: hit, re-touch, hit again.** Unloading is
       elastic and reloading retraces to the previous peak, so two or three hits,
       each followed by a 10 N re-touch read across the dies, land within
       ±0.01 mm of a target [ff w2 §10]. Every approach comes from above,
       because a crimp cannot be un-crimped;
     - **a crank stopped short of bottom** (below).
  2. **A 0.001 mm indicator** across the dies (Clockwise DITR-0105, $52.99,
     RS232 [Prime]; its cable is not on Prime), and a load cell in the force
     path. Together they record force against true die gap.
  3. **A pull axis:** a small lead-screw carriage with a ~200 N load cell in
     line. A 22 AWG conductor breaks at ~85–100 N [xh-facts §1].
- v1's cameras and silhouette window at the host.
- **Coupons,** made the way production makes them (below).

**What moves.**
- The stage lays each coupon conductor into a contact as v1 does, or docks a
  whole coupon end onto a strip segment or pocket plate, or the reel feeds the
  contact (on an applicator).
- The host crimps at the campaign's current setting.
- The crimp is photographed.
- The pull axis pulls it to failure at 25.4 mm/min, UL's rate [prior-art §6].
- The camera photographs the broken end.

**What locates what.** As v1: the nest, strip or applicator locates the contact,
and the picture locates the conductor. **The setting is the knob; the result is
the measured crimp height.** Frame deflection and die compression mean the stop
is not the height. Each crimp's height is its re-touch reading or its
silhouette, and ~10 are checked by point micrometer (Shars 303-2307, $61.95
[Prime]; a point-and-blade crimp micrometer was not found on Prime). The
reference for "fixed" is the host's lower die, read across the dies.

**What drives the crimp and carries its force.** The host, through its own frame
to its geometric bottom. The pull axis carries up to ~100 N between its grip on
the coupon's far end and the reaction at the contact (below).

**How it knows it worked.** "Worked" means a measured answer. For each setting:
the crimp height; the pull-out force; the failure mode from the after-picture
(the conductor sliding out, or the wire breaking). The window is where the lower
tail of pull force clears 39.2 N with margin [mfr S6] and the pictures also pass
(bellmouth, brush, insulation position, no strands outside).

**What the person does.**
- Makes coupon ends: ~30 short 5P ends, about half an hour.
- Prepares the far-end grips, 1–4 h depending on method [calc: wave2 §6].
- Reads the report and decides whether to adopt the window.

The campaign runs ~8 h unattended and uses ~$2 of contacts
[calc: campaign §1].

**Steps it covers:** crimp (finding the window, then process control), verify
(destructive ground truth for every non-destructive check), place contact (as
v1 or by docking). **What it hands back:** coupon ends and grips; the decision
to adopt; any sectioning.

## Why this exists

The one number that decides whether a crimp is good, the conductor crimp height
for SXH-001T-P0.6 at 22 AWG, is not public; it sits in JST's licence-gated
handling manual [xh-facts §1, Unresolved 1]. On top of that the contacts on hand
are probably clones of unknown drawing [repo: bom.md §11; xh-facts §6]; the wire
is 60-strand silicone near the top of the insulation range [xh-facts §7]; and
JST warns that its fixed-die hand tools "may not" crimp every catalog wire
properly, and says to check pull strength [mfr S4]. The estimate is 0.69–1.12 mm,
central 0.88, with JST analogs near 0.80 [xh-facts calc C1]; the KONNRA clone
spec quotes 0.73 ±0.05 mm [digest]. For the insulation crimp on 0.49 mm silicone
the window has a floor (cut-through) and a ceiling (the cavity envelope), both
set by position [ff w2 §5]. A machine that can set its crimp height, destroy its
own test crimps and read the results can find both windows for *these* contacts
on *this* wire, and keep checking that it stays there.

## Hosts, from the first week to the crank

**The jack test (no motor).** borrowed-machines' b1b stage 0: an OTP applicator
on the idle VEVOR 12-ton press, its bottle jack stroking the applicator.
- An indicator from the applicator's ram to its base, read at a 10 N re-touch,
  takes up every internal clearance in the loading direction.
- Coupons come off the production reel through the production feed.
- A hand pump's travel per stroke is coarse near bottom, so the knob is the
  stop collar on a shim stack, not the pump.
- The applicator shears the tab in the stroke, so pulls react on a thin fork in
  the neck behind the box, not on the tab.

**Hand tools with a pusher ($22–39).** A second SN-2549 ($22.29 [Prime]) with
hand-tool-as-press's [a1b](../../hand-tool-as-press/ideas/a1b-pawl-out.md)
pawl-out and a pusher, or an Engineer PA-09 ($38.99, 1,719 ratings [Prime]) as
in their [a5](../../hand-tool-as-press/ideas/a5-two-squeeze-plier.md), sweeps
grip positions. The grip position is a setting, not a length, so every level
needs v5's silhouette to map it to a height; the map drifts with wear, which
v7's trend on the knee position at fixed force watches. a5's separate insulation
squeeze lets the insulation height be swept on its own.

**The crank as its own gauge.** On b1b's crank, stopped short of bottom dead
centre [bm W §6]:
- the ram moves 0.16–0.51 µm per microstep through a 10:1 planetary, and
  0.05–0.17 µm through a 30:1 worm, over the last 0.02–0.2 mm;
- holding 3 kN at 0.1 mm above bottom takes 6.5 N·m at the crank, which the
  worm holds unpowered;
- a 10 N re-touch read by a 14-bit shaft encoder gives 0.2–0.5 µm of height per
  count near the re-touch point (a 12-bit AS5600, $7.99 for three [Prime]:
  0.9–2.0 µm), once throw, rod and bottom dead centre are calibrated against one
  gauge block;
- the crank angle is then the height knob and the shaft encoder the height
  gauge. Production runs at bottom dead centre with the rod-end thread set to
  the campaign's height.
- **Uncertain:** with both crimpers on one ram, a re-touch reads whichever
  barrel springs back higher. An indicator across the dies has the same
  ambiguity.

**Knee, die set or stop blocks.** force-and-form's f3 with its wedge,
hand-tool-as-press's a4 die set, or a2b's stop blocks under the 12-ton press.

## Coupons made the way production makes them

- **The coupon.** A 5P piece ~80 mm long: flush-cut in the fan block; all five
  conductors stripped as production strips them (a whole-end slug while still
  webbed, or v6's stations), to the strip length of the contact being tested
  (1.6–2.1 mm for clone-drawn kit contacts, 2.4 mm for genuine SXH
  [calc: w3htp §4]); parted 25 mm and fanned.
- **Strip contacts** dock onto a 7-contact carrier segment, or come from the
  reel; **loose contacts** dock onto a [v4b](v4b-pocket-plate.md) plate, or v1
  lays them one at a time.
- Strip quality is production's own, so the sweep measures what production will
  make; five replicates per level come from one docking; far-end continuity
  confirms each conductor sits in its contact before the stroke.
- The far ends are parted too, and each conductor gets its own pull grip.

## Gripping a coupon for a pull to failure

A capstan does not work here [rap P §4]: three turns on a 10–15 mm drum need a
coupon of ~150–200 mm, and at 100 N the friction at the drum's entry puts
6–34 MPa of shear into a narrow strip of jacket, against silicone's 8–11 MPa
tensile strength. Two grips keep the jacket out of the path.

| Grip | How | Holds | Preparation |
|---|---|---|---|
| **Soldered lug** | 10 mm of the far end's tinned bundle soldered into a slotted lug with the bench Hakko; a fork hooks the lug | Solder shear 500–750 N, above wire break [rap P §4] | ~60–90 s a coupon [estimate] |
| **Bare-copper wrap on a pin** | 25–30 mm of the far end stripped; the bare bundle wrapped two turns on a 3–5 mm steel pin before a screw clamp | Capstan friction leaves 0.2–8 N of a 100 N pull at the clamp, for μ 0.2–0.5 [calc: wave2 §6]. Strand bending strain over the pin is 1.6–2.7 %, against copper's 20–30 % elongation | ~30–50 s a coupon [estimate] |

The soldered lug may add a failure mode above ~80 N where solder-stiffened
strands meet free ones; the wrap may start wire break at the pin's entry at an
estimated 80–95 % of straight break. Both lie above the 39–54 N region the
campaign resolves. A 20 N production proof pull can still grip the jacket
(0.5–1 MPa over 25 mm).

## Where the pull reacts at the contact

The lance, the brush and the neck share the space behind the box. A plate under
the floor strip loads the lance tip in its retention direction and folds it at
these loads.

| Contact form | Reaction | Range |
|---|---|---|
| Strip, tab uncut | The carrier tab in compression, with a hold-down on the box top 3–5 mm ahead of the tab and a support under it (8–28 N of hold-down at 100 N) | Tab yields at 72–96 N [rap P §3]. A crimp that survives to tab yield has held 1.8× JST's 39.2 N, so tab yield is a pass. On an applicator the shear punch comes out for campaign crimps, or the pull uses a neck fork |
| Loose, or strip with the tab sheared | A lance-notched plate, or a neck fork lowered onto the box's rear face, above the floor, clear of the lance tip (0.24–0.64 mm behind the box) | Box top wall plus upper side walls at 39.2 N: 50 MPa; at 100 N ~115–130 MPa, against ~450–500 MPa bronze yield [ff w2 §11; rap P §3] |
| Loose, neck too short | No per-crimp reaction behind the box; pull these through a strip analog, or only on strip contacts | — |

## The campaign

**The conductor-crimp sweep** [calc: campaign §1]: 16 target heights from 0.70
to 1.00 mm in 0.02 mm steps, 5 crimps each, all pulled to failure. With pull
scatter σ of 2–5 N [assumption], five crimps pin a level's mean to ±1.8–4.4 N;
the mean must reach ~45–54 N for mean − 3σ to clear 39.2 N [calc: campaign §2].
A crimp whose wire breaks before it pulls out needs no statistics.

**The insulation arm.** Insulation heights from ~1.8 to ~2.5 mm at the width the
die gives, tested by pull and by a bend test (60–90°, several times
[xh-facts §5]) while the camera watches for a cut jacket or a loosened grip.
force-and-form estimates that 1.8 mm (KONNRA's PVC-wire figure) cuts this
silicone, and 2.0–2.3 mm does not [ff w2 §5]; an elliptical section puts the
upper bound at 2.46 mm [calc: w3htp §9]. Where the insulation crimper has its own
drive, its force curve steepens 20–500× when the wing tips reach copper: a
cut-through sentinel that finds the floor.

**The tack arm, for [v8](v8-tack-look-crimp.md) and [v9](v9-tack-at-the-anvil.md).**
- Tack heights in 0.05 mm steps from 0.2 to 0.5 mm **above the final insulation
  height at the same contact and wire**, and former widths 0–0.2 mm wider than
  the final crimper [calc: w3_final §1].
- Measure the grip (the tacked contact pulled off with the 0.1 g scale, or the
  pull axis at low range) and the jacket after release.
- Tack-first crimps against one-pass crimps: pull, and a few sectioned.

**The insulation-edge arm.** The edge placed at five points across the window,
to find the real axial room on these contacts.

**The strip-length arm.** Strip lengths across 1.6–2.4 mm on each contact form,
since JST's own form S = E + A/2 + b gives 1.6–2.1 mm on the clone barrel and
2.4 mm implies a genuine barrel of ~1.8–2.05 mm [calc: w3htp §4].

**Proof-then-destroy pairs** at the chosen setting: crimps proof-pulled at
~20 N then pulled to failure, against crimps pulled to failure directly. This
answers whether a production proof pull is harmless.

**By supply form.** Genuine SXH on strip (Digi-Key, 100 for $4.71 [xh-facts §6])
and kit contacts are different contact-and-die pairs; the campaign runs per pair,
at least 10 of each at the chosen setting.

**Grid or adaptive.** A grid is enough for one knob. The supervisor zooms: once
the first pass shows where pull force climbs, the remaining coupons go there at
0.01 mm steps, and a level whose crimps disagree is re-run.

## The supervisor: Claude running the campaign

v7's campaign mode: an interactive Claude Code session at the bench with the
motion tools (`cell crimp --target 0.84`, `cell retouch`, `cell pull`,
`cell shoot`), the MCU's limits and the steel ceiling in force. Claude earns its
place on what a script cannot anticipate:
- **classifying every failure picture:** pull-out; wire break at the crimp's
  mouth; break at the grip (a bad test, repeated); insulation pulled off;
  contact deformed;
- **noticing anomalies:** a force peak twice the others (two contacts?); a
  height that ignores the knob (a stop slipped?); a lot whose silhouettes look
  different;
- **choosing where the next coupons go,** and saying why;
- **writing the report:** the table, the pictures, the chosen windows and what
  they rest on.

Cost is well under $20 a campaign [calc: cycle_and_cost §3].

## What the campaign leaves behind

1. **The windows.** A setting and a measured crimp-height band for this contact
   lot on this wire; an insulation height band; a tack height and width.
2. **The force envelope.** Force-against-gap curves of the crimps that tested
   good, which the station MCU checks every production stroke against.
3. **A labelled picture set.** Every destroyed crimp has a side silhouette, a top
   view and a physical verdict: ground truth for every non-destructive check in
   this view, and the source of Claude's reference crops.
4. **A re-check routine.** Every few units or each new contact lot: 10 coupon
   crimps at the production setting, pulled to failure, plotted beside the
   production heights and force peaks from the log. Where the per-crimp proof
   pull is dropped (loose contacts with no room behind the box), this carries
   pull strength by sample.

## Problems, and what answers them

- **"Just ask JST."** The handling manual would give JST's height for genuine
  SXH on UL1007-class wire. It is the first question for Derek. It does not
  settle kit clones or silicone wire, and JST says to check pull strength anyway
  [mfr S4].
- **Pull tests on silicone.** UL pulls with the insulation crimp loosened, so
  only the conductor crimp is tested [prior-art §6]. For the conductor sweep the
  insulation wings are left open or pre-cut; the insulation grip is tested by
  bends.
- **Three sigma from five samples** assumes a normal spread. The chosen setting
  gets ~20 extra proof-then-destroy crimps.
- **Measuring the height, not the stop.** Frame deflection and die compression
  (50–80 µm at peak [force-and-form]) make stop-to-height non-linear; the
  campaign plots against measured height.
- **Force monitoring's limits.** One strand of 60 is 1.7 % of the copper, inside
  a monitor's ±4 % band [calc: campaign §3]. The force curve polices gross faults
  only.
- **Strip quality confounding the sweep.** The tip picture records each strip,
  so bad strips are dropped from the analysis, not blamed on the crimp.

## Contribution

- It turns the study's largest unknown, the crimp height and the insulation
  window on this wire, into a night's measurement on the actual parts.
- It produces the labelled pictures that make every camera check here
  trustworthy, and keeps producing evidence for the life of the program.
- Any host with an indicator across the dies can be made into it, even one with
  no settable stop (hit and re-touch), a hand-pumped applicator (the jack test),
  or a crank that gauges its own height.

## Major unresolved problems

- **The contact-side reaction for loose contacts** depends on the neck gap.
- **Tab yield caps strip pulls at 72–96 N**: enough to call a pass, not to see
  where a strong crimp would fail.
- **The far-end grip's own failure modes** above ~80 N.
- **Pull-force scatter** is unknown.
- **One ram, two barrels:** a re-touch or an indicator reads whichever barrel
  springs back higher.
- **Cross-sections** (voids, strand distribution) are manual; whether to pot and
  grind a few is Derek's call.

## What rests on assumptions

- Pull-force scatter σ = 2–5 N.
- That kit contacts crimp consistently within a lot.
- That silhouette height tracks micrometer height with a fixed offset.
- force-and-form's insulation model and hit-and-re-touch physics.
- Grip friction coefficients for the wrap.
- A 14-bit encoder on the crank; which chip, and whether Klipper reads it, is
  open ([v7](v7-the-run.md)).
