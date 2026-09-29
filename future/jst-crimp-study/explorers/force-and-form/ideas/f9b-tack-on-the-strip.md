# f9b — Tack on the strip: dock a ribbon end onto a strip, tack every contact, cut the tabs, then crimp one contact at a time in a keyed steel nest

Explorer: force-and-form. Branch of [`f9`](f9-tack-station-feeds-crimp-station.md),
and a combination:
- ribbon-as-pallet's [a2](../../ribbon-as-pallet/ideas/a2-two-pallets-meet.md):
  a ribbon fanned to the strip's pitch and set down on a strip segment places
  every contact on its conductor in one passive motion, and every conductor is
  checked electrically before any force;
- change-the-question's [c1b](../../change-the-question/ideas/c1b-tack-first.md):
  a light gang tack of the insulation barrels pins each contact to its wire;
- force-and-form's heavy crimp: [`f3`](f3-knee-micropress.md)'s knee, re-touch
  gauge and neck blade, [`f6`](f6-two-blades-two-drives.md)'s separate
  insulation blade, and the fixed steel C of [`f4`](f4-crimp-head-goes-to-the-wire.md)
  and [`f8`](f8-narrow-press-at-the-housing-mouth.md) with its throat toward the
  wire.

ribbon-as-pallet proposed the pairing (K1 in
[its reading of force-and-form](../../../exchange/ribbon-as-pallet--on--force-and-form-w3.md)).
Sketch: [`../sketches/f9b-tack-on-the-strip.svg`](../sketches/f9b-tack-on-the-strip.svg) (schematic).
Numbers:
- [calc final §n]: [`../calc/final_w3.out.txt`](../calc/final_w3.out.txt);
- [calc wave2 §n], [calc drives §n], [calc gang §n], [calc FP §n],
  [calc placement_budget]: force-and-form's other outputs in [`../calc/`](../calc/)
  (FP is `exchange_procedure_w3.out.txt`);
- [RP w3 §n] and [RP pg §n]: ribbon-as-pallet's
  [`exchange_on_force_and_form_w3.out.txt`](../../ribbon-as-pallet/calc/exchange_on_force_and_form_w3.out.txt)
  and [`pallet_geometry.out.txt`](../../ribbon-as-pallet/calc/pallet_geometry.out.txt);
- [calc X §n]: borrowed-machines'
  [`exchange_ribbon_as_pallet.out.txt`](../../borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt). **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md), observed
2026-09-28.

## Picture it

**Where things start.**
- **The ribbon pallet** (ribbon-as-pallet's [a1](../../ribbon-as-pallet/ideas/a1-pallet-tour.md)
  type) holds the web in a lid whose front face is the split root. At its own
  stations the ribbon end has been:
  - parted back to the lid face ([a7](../../ribbon-as-pallet/ideas/a7-zip-station.md));
  - fanned, each ribbon of a pair on its own, to the strip's pitch in a fan
    block about 9–12 mm behind where the barrels will be;
  - flush-cut and ring-stripped **after** the fan, at a fixed distance from the
    fan block's face ([a8](../../ribbon-as-pallet/ideas/a8-rolling-ring-scorer.md)),
    so every insulation edge sits on one line;
  - wired at its far end to a pogo port that reads each conductor
    ([a6](../../ribbon-as-pallet/ideas/a6-housing-as-last-comb.md)).
- **The strip pallet** on the bench is a steel plate with:
  - slot pins in the carrier's rectangular slots;
  - a hardened **rail** under the row of insulation barrels only, its top flush
    with the contacts' floor and its rear edge a shear edge at the contacts'
    rear. A 3 × 3 mm HSS blank serves [Prime: HSS square tool bits, $9.99];
  - everything forward of the rail (conductor barrels, lance, box) overhangs,
    so each lance hangs free. On a flat shelf each contact would sit propped
    7.6–15.9° on its lance about its tab [RP w3 §5].
- **The strip segment.** The person snips N + 2 SXH-001T-P0.6 off a strip,
  cutting out the position under a trimmed conductor for J2 and J7, lays it on
  the pins, and flips a clamp bar onto the carrier between the conductor paths.
- **The tack-and-shear block**, beside the strip pallet:
  - a notched steel **tack comb**, one loose insulation profile per contact at
    the measured strip pitch, on a toggle lever that drives it to a steel stop;
  - a floating **shear** under the carrier on a second lever.
- **The heavy station**, elsewhere on the bench: a fist-sized steel C, fixed,
  its spine at +Y ahead of where the boxes will be and its throat open toward
  −Y, the wire side.
  - *Upper arm:* f3's knee drives the conductor crimper to a geometric bottom;
    f6's insulation blade slides beside it on its own small drive and wedge; a
    0.001 mm indicator reads across the dies.
  - *Lower arm:* a narrow post carries a **keyed steel nest**: a box slot with
    lead-in chamfers, a front stop for the box, a lance relief, the conductor
    anvil (its front edge behind the lance tip), the insulation anvil, and a
    button load cell under the anvils.
  - *Above the post:* a 0.3 mm neck blade on a small servo.
  - *In front of the throat:* a kinematic seat for the ribbon pallet on an XYZ
    stage.

**What moves.**
1. **Dock.** The person sets the ribbon pallet onto three balls in dowel
   V-grooves on the strip pallet, and magnets pull it home
   [Prime: 6 mm chrome steel balls, $6.65; N52 10 × 3 mm magnets, $23.99]. Every
   conductor drops into every open contact: strands between the conductor
   wings, jacket between the insulation wings, insulation edge in the window.
   The far-end port reads each conductor continuous to the grounded carrier,
   and the ELP camera photographs the docked row.
2. **Tack.** The comb lever goes to its stop. Every insulation barrel of the
   ribbon end closes loosely on its jacket in one stroke, 33–132 N a contact:
   99–396 N for a 3P, 165–660 N for a 5P [RP w3 §3, from c1b]. The conductor
   barrels stay open, their strands lying in the U.
3. **Cut.** The comb stays at its stop and becomes the hold-down. The shear
   lever drives the carrier down past the rail's rear edge and parts every tab
   (below). Tab length is the rail edge's position against the slot pins.
4. **Lift.** The ribbon pallet lifts off. Every contact hangs from its
   conductor by its tack, all with one roll, because the ribbon never turned
   over. The carrier and the two spares stay on the pins as scrap.
5. **Seat.** The person sets the pallet on the heavy station's seat (three
   balls again), starts the run and leaves.
6. **Into the nest.** With the crimper raised 5 mm, the stage carries contact
   *k* box-first (+Y) about 1.2 mm above the anvils, so the lance (0.6–0.9 mm
   below the floor) clears them, then **lowers it straight down**. The box
   enters its slot on the chamfers, the lance its relief, and the box front
   lands against its stop. The neighbours hang one strip pitch away on either
   side, beside the post and outside the crimper.
7. **Capture and look.** Both blades come down to capture height. The camera
   checks that the strands are in the U, none lies over a wing tip, and the
   insulation edge is in the window. The far-end port reads that only
   conductor *k* touches the grounded nest.
8. **Crimp the conductor barrel.** The knee goes to straight. Force is logged
   against true die gap; a re-touch at ~10 N reads crimp height (f3).
9. **Re-form the insulation barrel.** f6's blade descends alone from the tack
   height to the height f6's sweep found for this wire. Its load cell watches
   for the 20–500× steeper slope of wing tips reaching copper.
10. **Proof pull.** The neck blade drops into the neck, in front of the brush,
    and bears on the upper part of the box's rear face. The stage draws the
    pallet −Y to ~20 N (a spring and switch in the stage's Y drive); the ribbon
    pallet's web clamp is the reaction.
11. **Bend and look (every crimp or a sample).** With the crimper resting on
    the crimp at re-touch force, the stage lowers the pallet so the wire bends
    60–90° **down** over the insulation anvil's radiused rear edge; the camera
    looks at the top of the insulation crimp, where a tip cut would gape
    (f6; [calc final §1]).
12. **Out.** The crimper rises, an ejector pin lifts the box out of its slot,
    and the stage raises the contact 1.2 mm, backs out −Y and indexes one
    strip pitch.

**What locates what, and the reference for fixed.**

| Moment | What is located | Against | Held to |
|---|---|---|---|
| Dock | carrier | slot pins | contact to slot is the stamping's, ±0.05 mm [assumption] |
| Dock | ribbon pallet | balls in V-grooves on the same plate | ±0.01–0.02 mm [estimate] |
| Dock | each conductor, laterally | the fan block's groove; the open barrels capture ±0.5 mm | ±0.1 mm at the fan face [a2] |
| Dock | each insulation edge, axially | the strip line (cut after the fan) against the slot pins | ±0.2 mm stacked [a2e's table] |
| Tack | contact's axial position and roll on its wire | frozen by the tack | as docked |
| Cut | tab length | rail edge against the slot pins | ±0.05 mm [estimate] |
| Heavy station | contact to dies | box slot and front stop | ±0.02–0.05 mm [calc placement_budget] |
| Heavy station | pallet to nest | stage; only has to reach the chamfers | ±0.3–0.5 mm |
| Crimp height | crimper to anvil | knee at straight in the C, wedge; read by the indicator | ±0.01 mm read |

"Fixed" is the strip pallet's slot pins until the tack, and the nest's box stop
after it. Crimp height is fixed by the steel C alone.

Why the stage's error never reaches the tack: the free conductor between fan
block and contact bends at 1–3 mN when a chamfer moves the contact 0.3–0.5 mm
sideways, and twists at 0.03–0.2 N·mm when the slot squares a 5–10° roll. The
tack holds 0.4–9 N and 0.4–2.5 N·mm [RP w3 §3; calc wave2 §5]. With 10 mm or more
of free conductor the conductor gives way long before the tack slips.

Which way the tack is loaded: the box goes into its slot vertically, so the
entry loads the tack **across** the jacket, where the wrapped wings hold it.
Along the jacket a loose tack may hold only 0.1–0.4 N [c1b; calc wave2 §5]. So the
slot is cut only ~0.05 mm longer than the box, with chamfers at both ends, and
the vertical entry seats the box against the stop: nothing pushes the contact
along its wire.

## What drives the crimp and carries its force

- **Heavy station.** A NEMA 17 on a Tr8×2 screw pushes the knee at 60–160 N
  [calc drives §B] [Prime: Iverntech 42HD6039-05, $27.99, thin]. The loop is C →
  knee → crimper → crimp → anvils → load cell → C. The ribbon pallet and the
  stage carry none of it. The insulation blade's drive never sees more than
  ~150 N (f6).
- **Tack.** 0.1–0.7 kN per ribbon end, through the comb's own steel stop. A
  POWERTEC 305CM push-pull toggle clamp serves as the lever
  [Prime: POWERTEC 305CM, $18.25 for two, 500 lb].
- **Shear.** 53–104 N per tab by shear strength [calc final §2], 50–160 N by
  borrowed-machines' figure [calc X §5]: 0.15–0.8 kN per ribbon end, rail edge →
  tab → shear punch, all steel.
  - *What the shear does to the tack.* The carrier going down behind the rail
    edge can put into each contact no more than the tab's plastic moment,
    3.6–6 N·mm. The comb, standing at its stop on the wings it just formed,
    reacts that with 2–8 N [calc final §2]. The tack itself carries none of the
    shear.
  - *Condition:* the comb never lifts between the tack and the shear.

## How it knows it worked

- **Before any force:** each conductor reads continuous to the grounded
  carrier through the far-end port; the camera frame of the docked row shows
  none sitting on a wing tip.
- **Identity at the heavy station.** Only conductor *k* may read closed to the
  grounded nest. A stage mis-index, or a J4/J7 recipe error made at loading,
  stops here, before the stroke.
- **The crimp:** f3's capture look, the force-against-gap curve and the
  re-touch height; f6's insulation curve and silhouette; the proof pull; the
  downward bend-and-look.

## What the person does

- Per ribbon end, about 55 s [RP w3 §3, estimate]: snip and lay a strip segment
  (~20 s), set the ribbon pallet on its balls (~10 s), pull the tack and shear
  levers (~15 s), move the pallet to the heavy station (~10 s).
- Per unit: ~13 min plus the pallet's own loading and preparation, and
  insertion. The heavy station runs 53–106 min per unit unattended at 1–2 min a
  crimp.
- Calls: one per ribbon end, 14 per unit. A rack of pallets at the heavy
  station would lower that [estimate].

## Numbers

- **Contacts:** 81 per unit at N + 2 per ribbon end: $1.90 from the SXH reel,
  $3.82 from 100-piece cut strip, $0.64 from the CJT clone reel [RP w3 §3;
  xh-facts §6]. No Prime listing exists for XH strip [Prime: "XH contacts on
  carrier strip", none found]; Digi-Key's 100-piece strip is $4.71.
- **Tack comb:** notch mouths as wide as the open wings (up to ~3.25 mm) leave
  3.55–3.85 mm of steel between mouths at 6.8–7.1 mm strip pitch, so one pass
  tacks the whole ribbon end [RP w3 §3]. A loose tack's profile tolerance is a
  tenth or two, so laser-cut steel at ±0.127 mm serves (SendCutSend, 2–4 days
  [source: sendcutsend.com, via f7]). The plate is about as thick as the
  insulation barrel is long, 1.2–1.5 mm (c1b), which keeps it out of the window;
  SendCutSend's thin gauges were not read [assumption].
- **Parted length:** 21, 25 and 30 mm for a 3P, 4P and 5P fanned alone to
  ~7 mm [RP pg §2].
- **Heavy station width:** the jaws, nest block and crimper holder may be up
  to 10.8–11.4 mm wide where the neighbours pass at 6.8–7.1 mm pitch [RP w3 §3].
  f3's crimper is 3.5–4.4 mm [calc gang §1].
- **Neck blade for the pull:** dropped after the crimp, it needs the
  transition *t* ≥ 0.50–0.70 mm (box clearance 0.05, blade 0.3, clearance 0.05,
  brush 0.1–0.3). It bears on ~0.8 mm² of the box's rear face above floor +
  1 mm: 24 MPa at 20 N, 48 MPa at 39.2 N [calc final §3].
- **Why the pull is reacted at the web clamp:** a 3–5 mm jaw on the jacket
  reaches 20 N only at ~30 % squeeze and the stiffer silicone; the strands slip
  inside the jacket at 1.4–6.3 N per mm of grip at 30 %, 0.5–2.1 N/mm at 10 %
  [calc final §3; calc FP §4].

## What each side brings

| | ribbon-as-pallet a2 alone | f9 alone | f9b |
|---|---|---|---|
| Contact supply | strip | loose contacts in pockets, a half-row at a time | strip, orientation from the strip |
| Placement | one docking per ribbon end | a presser comb per half-row, after a split into planes | one docking per ribbon end |
| Check before force | continuity to the carrier; camera | camera | continuity to the carrier; camera; identity in the nest |
| What holds the contact in the heavy stroke | a 0.8 × 0.2 mm tab in a row (0.10–0.14 mm elastic lift) | a keyed steel nest | a keyed steel nest |
| Neighbours in the heavy stroke | one strip pitch away, on the carrier | 3.4 mm away, forked 3–4 mm up; the other plane parked | one strip pitch away, hanging free |
| Insulation height | fixed step, or a wedge set by hand | re-formed by the stepped crimper | f6's blade, set to this wire's window |
| Parted length | 21–30 mm | 12–20 mm | 21–30 mm |
| Calls per unit | ~14 | ~34 | ~14 |

## Branches

- **f9b by hand, the first week** (motorless). A dock jig, the tack comb and
  the shear on toggle levers, and today's SN-2549 [Prime: iCrimp SN-2549,
  $22.29] for the heavy crimp. The tack is the locator the SN-2549 lacks: the
  person seats a contact that is already on its wire at its depth and roll, and
  squeezes (f9's third host). A tacked contact enters the SN nest box-first from
  the wire side, so the open nest must pass box plus lance, 2.8–3.25 mm (one
  pin gauge), with change-the-question c1b's box-keyed clip on the jaw's face
  giving the axial stop. Nothing moves by motor. It tests docking, the tack's
  grip on silicone and the tack-first crimp on this ribbon before any press is
  built.
- **f9b with a die cartridge.** The heavy station is one of
  [`f7`](f7-where-the-steel-comes-from.md)'s cartridges with a keyed nest,
  closed by hand in the VEVOR AP-1 arbor press [Prime: VEVOR AP-1, $61.90,
  150 mm opening, 281 ratings, 300+ bought in past month]. The person strokes it
  to the cartridge's own stop.
- **f9b-k: every k-th conductor** (f5's every-k-th variant × a2). The parted
  length falls to what a 3–4 mm lift needs, 12–20 mm, at the cost of k docks
  and k tacks per ribbon end. At the heavy station the neighbours then hang
  1.7 mm away and must be lifted, which gives up the 11 mm jaw allowance.
- **f9b on loose kit contacts.** ribbon-as-pallet's
  [a2c](../../ribbon-as-pallet/ideas/a2c-loose-contact-cassette.md) keyed nest
  bar at ~5 mm replaces the strip, and everything after docking is unchanged.
  A 5P needs 20–23 mm parted [RP pg §2], the rail becomes a steel insert in the
  bar, the shear step disappears, and pocket loading returns.
- **f9b with a curl tack.** [`f3b`](f3b-two-station-forming.md)'s station A is
  the gang tack: conductor wings curled onto the strands as well. At 180–580 N a
  contact a 5P takes 0.9–2.9 kN, so the tack block needs a steel local stop.
  Curled wings trap the strands, not only the jacket, and the tack's grip stops
  being a question.

## Contribution

- **The carrier's job ends at the tack.** Every contact then belongs to its
  ribbon, one strip pitch from its neighbours, so the heavy station gets a keyed
  nest with no feeder, no pilot pin, no threading, no planes and no fork.
- **Checks before any force for a whole ribbon end**, and an identity check at
  every crimp.
- **Loads on the tack are chosen, not suffered:** vertical entry across the
  jacket, the shear's moment held by the comb at its stop.

## How it connects to the whole procedure

| Step | Who does it |
|---|---|
| Cut, part, fan, strip | ribbon-as-pallet's pallet stations (a7, a8), or the person |
| Supply contacts | the person lays a strip segment |
| Place contacts on conductors | the docking, one motion per ribbon end |
| Tack, tab cut | two levers |
| Crimp both barrels, measure, pull, bend-and-look | **automated** at the heavy station |
| Identity | far-end port, before force and in the nest |
| Insert | after: the crimped row sits at ~7 mm and must converge to 2.5 mm (a6's clamp, or ribbon-as-pallet's K4) |

## Major unresolved problems

- **The tack's grip on this silicone**, and the **tack-first crimp**
  (insulation barrel closed before the conductor crimp, the reverse of JST's
  two-step order). The hand test is in the questions; the sectioning
  experiment is f3b's four arms.
- **The transition *t*.** The conductor anvil must stop behind the lance
  (t ≥ 0.34–0.74 mm) and the neck blade needs t ≥ 0.50–0.70 mm. One kit contact
  side-on under the ELP camera settles both.
- **Ejecting a box** from a slot 0.05 mm longer than itself; an ejector pin
  under the box, or one slot wall on a light spring.
- **Strip pitch** (the $4.71 strip settles it), and a **21–30 mm split** behind
  the housing, which is Derek's call.
- **Converging the crimped row** from ~7 mm to 2.5 mm for insertion, and the
  copper set that fanning leaves (copper sets below a ~67 mm radius [RP pg §4]).
- **The loose tack re-formed** by f6's blade: it enters the blade's flare only
  if the tack is looser than the final crimp, which the comb's stop sets.
- **Bend-and-look at the station** moves the neighbours 8–9 mm down beside the
  C's lower arm; with an 11 mm arm at 7.1 mm pitch that leaves ~0.5 mm
  [estimate]. Otherwise it runs on a sample at a separate bend nest.
- **The heavy station's stage** (a printer-class XYZ; its repeatability only
  has to reach the chamfers).

## Which conclusions rest on assumptions

- Tack grip and torque come from a thin-layer model of the jacket
  [calc wave2 §5].
- Contact-to-slot position on the strip is the stamping's, assumed ±0.05 mm.
- Tab yield and shear use a phosphor-bronze range assumed for C5191 spring
  temper.
- The 55 s per ribbon end is ribbon-as-pallet's estimate.
