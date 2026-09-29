# ribbon-as-pallet on force-and-form (wave 3)

Wave 3, second exchange.
- **The view doing the reading:** *the ribbon is a precision part*
  ([summary](../explorers/ribbon-as-pallet/summary.md)).
- **The view being read:** *a crimp is a small, slow sheet-metal forming
  operation* ([summary](../explorers/force-and-form/summary.md)). This is f1–f9
  as they stand after wave 2, with most weight on the new and changed files:
  [f5b](../explorers/force-and-form/ideas/f5b-half-row-cassette.md),
  [f6](../explorers/force-and-form/ideas/f6-two-blades-two-drives.md),
  [f7](../explorers/force-and-form/ideas/f7-where-the-steel-comes-from.md),
  [f8](../explorers/force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md),
  [f9](../explorers/force-and-form/ideas/f9-tack-station-feeds-crimp-station.md)
  and [f2c](../explorers/force-and-form/ideas/f2c-applicator-station-makes-t4-ends.md).

It does not repeat change-the-question's wave-2 reading
([`change-the-question--on--force-and-form.md`](change-the-question--on--force-and-form.md)).
That reading covered the call rate, the flap filled through the nest, the pilot
pin in the threading path, the fork with nothing to bear on, f4's exit, the
half-row cassette as a proposal, and f5-k.

**What this view brings.** Force-and-form has made the stroke, the steel and the
second barrel precise. This view looks at the conductors around that stroke:
- each conductor's **length from the web**, which nothing downstream can
  change;
- its **pitch**, and which datum it shares with its neighbours;
- a **wire to every conductor** through the far end.

Most points below are about length and datum around force-and-form's stroke.

**Citations.**
- **[w3 §n]:** this exchange's numbers,
  [`../explorers/ribbon-as-pallet/calc/exchange_on_force_and_form_w3.py`](../explorers/ribbon-as-pallet/calc/exchange_on_force_and_form_w3.py),
  with output in
  [`exchange_on_force_and_form_w3.out.txt`](../explorers/ribbon-as-pallet/calc/exchange_on_force_and_form_w3.out.txt).
- **[pg §n]** and **[W2 §n]:** my
  [`pallet_geometry.out.txt`](../explorers/ribbon-as-pallet/calc/pallet_geometry.out.txt)
  and
  [`stations_wave2.out.txt`](../explorers/ribbon-as-pallet/calc/stations_wave2.out.txt).
- **[f&f file §n]:** force-and-form's calc outputs in
  [`../explorers/force-and-form/calc/`](../explorers/force-and-form/calc/).
  "on_ith" is `on_into_the_housing.out.txt`.
- **[calc X §n]:** borrowed-machines'
  [`exchange_ribbon_as_pallet.out.txt`](../explorers/borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt).
- **[ctq off §n]:** change-the-question's
  [`on_force_and_form.out.txt`](../explorers/change-the-question/calc/on_force_and_form.out.txt).
- **[Prime]:** a row in [`../sourcing/amazon-prime.md`](../sourcing/amazon-prime.md),
  observed 2026-09-28 in Derek's signed-in Chrome.

**Coordinates.**
- Y runs along the contact, +Y toward the box (mating) end.
- X runs across the row.
- Z is up, with the barrels opening up and the lance hanging down.

---

## 1. Combinations

### K1: Dock on strip, tack the row, cut the tabs, then crimp each contact in a keyed steel nest

**Built from:**
- ribbon-as-pallet [a2](../explorers/ribbon-as-pallet/ideas/a2-two-pallets-meet.md):
  a fanned ribbon docked onto a carrier segment, the carrier as fixture,
  continuity before force, flush cut and strip at the fan block's face;
- force-and-form [f9](../explorers/force-and-form/ideas/f9-tack-station-feeds-crimp-station.md):
  a light gang tack hands contacts, already on their wires, to a heavy
  single-contact station;
- from force-and-form's other files, [f3](../explorers/force-and-form/ideas/f3-knee-micropress.md)'s
  knee, re-touch and neck blade, [f6](../explorers/force-and-form/ideas/f6-two-blades-two-drives.md)'s
  separate insulation blade, and the steel C of f4 and f8 with its throat
  toward the wire.

The tack itself is change-the-question's c1b.

**Why the pairing does something neither does alone.**
- **a2 alone.** It places every contact of a ribbon end on its conductor in
  one passive motion, from strip, in orientation, and checks each one
  electrically before any force. But its contacts stay on the carrier through
  the heavy stroke. Each hangs in the row on a 0.8 × 0.2 mm tab with 0.10–0.14
  mm of elastic lift [calc X §5]. So a2 needs one of:
  - a walking head (a2);
  - a row driven through a feedless applicator, with unknown downstream room
    and X located between end grips (a2e);
  - N matched dies (a2b).
- **f9 alone.** It gives the heavy station a contact already fixed to its wire,
  so that station is one keyed steel nest: no feeder, no pilot pin, no
  threading. But its tack station:
  - lays half-rows into loose contacts in pockets (~34 calls per unit
    [ctq off §7]);
  - splits the ribbon into two planes at 3.4 mm.

  Its heavy station then has to fork in-plane neighbours 3–4 mm aside and
  deal with the other plane (B4 below).
- **Paired.** The tack is made on the strip, right after docking, while the
  carrier is still clamped. The carrier's job ends at the tack. Every contact
  now belongs to the ribbon, one strip pitch (~7.1 mm) from its neighbours.
  The heavy station's jaws get ~11 mm of room [w3 §3], with no planes, no fork,
  no fold and no threading.

**Picture it.**

*Where things start.*
- **The ribbon pallet.** An a1-type pallet (the lid's front face is the split
  root) arrives from the preparation stations:
  - parted back to the lid face ([a7](../explorers/ribbon-as-pallet/ideas/a7-zip-station.md));
  - fanned to strip pitch in a fan block, each ribbon of a pair on its own;
  - flush-cut and ring-stripped at the fan block's face ([a8](../explorers/ribbon-as-pallet/ideas/a8-rolling-ring-scorer.md));
  - every tip touched off.
- **The strip pallet** on the bench is a steel plate with:
  - slot pins for the carrier;
  - a hardened rail under the row of insulation barrels only, its top flush
    with the contacts' floor and its rear edge a shear edge at the contacts'
    rear.

  Everything forward of the rail (conductor barrels, lance, box) overhangs,
  so each lance hangs free. On a flat shelf each contact would sit propped
  7.6–15.9° on its lance (§4).
- **The strip segment.** The person snips N + 2 SXH-001T-P0.6 off the strip,
  removing the position under a trimmed conductor for J2 and J7, and lays the
  segment on the slot pins. A clamp bar holds the carrier between the
  conductor paths.
- **The tack-and-shear block**, beside the strip pallet:
  - a notched steel tack comb, one insulation-barrel notch per contact at the
    measured strip pitch, driven by a lever to a hard stop;
  - a floating shear under the carrier.
- **The heavy station**, elsewhere on the bench: f4's fist-sized steel C,
  standing fixed, spine at +Y ahead of the boxes, throat toward −Y (the wire
  side).
  - **Upper jaw.** f3's knee drives the conductor crimper to a geometric
    bottom. f6's insulation blade slides beside it on its own small drive and
    wedge. A 0.001 mm indicator reads across the dies.
  - **Lower jaw.** A narrow post carries f9's keyed nest: a box slot with
    lead-in chamfers, a lance relief, a front stop for the box, the conductor
    and insulation anvils, and a button load cell under the anvils.
  - **In front of the throat,** a ribbon-pallet seat on an XYZ stage.

*What moves.*
1. **Dock.** The person sets the ribbon pallet onto three balls in dowel
   V-grooves, and magnets pull it home. Every conductor drops into every open
   contact:
   - strands between the conductor wings;
   - jacket between the insulation wings;
   - insulation edge in the window between the barrels.

   The far-end pogo port reads each conductor continuous to the grounded
   carrier. The ELP camera photographs the docked row.
2. **Tack.** The lever drives the tack comb down to its stop. Every insulation
   barrel of the ribbon end closes loosely on its jacket in one stroke:
   99–396 N for a 3P, 165–660 N for a 5P [w3 §3, from c1b's per-contact
   range]. The conductor barrels stay open.
3. **Cut.** The tack comb stays down as the hold-down pad. The shear drives the
   carrier down past the rail's edge and cuts every tab: 150–480 N for a 3P,
   250–800 N for a 5P [calc X §5]. Tab length is set by the rail edge's
   position against the slot pins.
4. **Lift.** The ribbon pallet lifts off. Every contact hangs from its
   conductor by the tack, and all have the same roll because the ribbon never
   turned over. The carrier and the two spares stay on the pins as scrap.
5. **Seat.** The person sets the pallet on the heavy station's seat, again
   three balls.
6. **Into the nest, one contact at a time.**
   - The crimper is raised 5 mm.
   - The stage carries contact k box-first in +Y, ~1.2 mm above the anvils.
     The lance, 0.6–0.9 mm below the floor, clears them (f4's exit rule, run
     in reverse).
   - The stage lowers it: the box enters its slot on the chamfers, the lance
     its relief, and the box front meets its stop.
   - The neighbours hang one strip pitch away on each side, beside the post
     and outside the crimper.
7. **Capture and look.** Both blades come down to capture height. The camera
   checks that the strands are in the U, none lies over a wing tip, and the
   insulation edge is in the window.
8. **Crimp the conductor barrel.** The knee goes to straight. Force is logged
   against true die gap, then a re-touch at ~10 N reads crimp height (f3).
9. **Re-form the insulation barrel.** f6's blade descends alone from the
   tack's height to the window height found by f6's sweep. Its load cell
   watches for the 20–500× steeper slope of wing tips reaching copper.
10. **Pull.** A 0.3 mm blade drops into the neck in front of the conductor
    crimp and bears on the box's rear face. A small jaw at the throat grips
    the jacket 3–5 mm behind the insulation barrel and pulls ~20 N (f3). The
    stage's belts carry none of this.
11. **Out.** The crimper rises. An ejector pin lifts the box out of its slot.
    The stage raises the contact 1.2 mm, backs out in −Y, and indexes one
    strip pitch.

*What locates what.*
- **At docking:**
  - the slot pins hold the carrier; contact-to-slot position is the
    stamping's, ±0.05 mm [assumption];
  - the kinematic seat locates the ribbon pallet to the same plate within
    ±0.01–0.02 mm;
  - the fan block holds each conductor to ±0.1 mm at its face, and the
    barrels capture ±0.5 mm laterally [a2];
  - axially, the strip line at the fan block face, measured against the slot
    pins, sets where each insulation edge lands (±0.2 mm stacked, a2e's
    table).
- **The tack** freezes that axial position and each contact's roll onto its
  jacket.
- **At the heavy station** the nest locates the contact: box slot and stop,
  ±0.02–0.05 mm [f&f placement_budget]. The stage only has to deliver the box
  into the chamfers' ±0.3–0.5 mm.
  - The conductor between fan block and contact bends to follow at 1–3 mN.
  - Squaring a 5–10° roll twists it at 0.03–0.2 N·mm.
  - The tack holds 0.4–9 N and 0.4–2.5 N·mm [w3 §3; f&f wave2 §5; f9].

  With 20–30 mm of free conductor, stage error never reaches the tack.
- **Which way the tack is loaded.** The box goes into its slot vertically, so
  entry friction loads the tack across the jacket, where the wrapped wings
  hold it.
  - c1b's box-first push into a slot (0.1–0.5 N, c1b's estimate) loads the
    tack along the jacket instead. There a loose tack may hold as little as
    0.1–0.4 N [c1b; f&f wave2 §5].
  - The slot is ~0.3 mm longer than the box. After the vertical entry the
    stage moves the contact +Y until the box meets the front stop. That push
    is tenths of a newton, through ~9 mm of straight overhang that buckles
    only at ~1.8 N [w3 §3], and under the tack's grip.
- **"Fixed"** is the slot pins until the tack, and the nest's box stop after
  it.

*What drives the crimp and carries its force.*
- The knee inside the C, pushed at 60–160 N by a NEMA 17 lead screw
  [f&f drives §B]. The Iverntech 42HD6039-05 integrated Tr8×2 motor is
  [Prime], $27.99 (thin, 21 ratings).
- The force loop is C, knee, crimper, crimp, anvils, load cell, C. The ribbon
  pallet and the stage carry none of it.
- The tack block's loads, 0.1–0.7 kN for the tack and 0.15–0.8 kN for the
  shear, close through its own steel.
  - The POWERTEC 305CM push-pull toggle clamp ([Prime], $18.25 for two,
    500 lb hold) can serve as each lever, driving to a stop.

*How it knows.*
- **Before any force:**
  - conductor-to-carrier continuity for every conductor;
  - the camera frame of the docked row.
- **Identity at the heavy station.** The far-end port reads which conductor
  touches the grounded nest, and only conductor k may read closed. That names
  the conductor in the press before the stroke. A stage mis-index, or a J4/J7
  recipe error made at loading, stops here.
- **The crimp checks:**
  - f3's capture look, its force-against-gap curve and re-touch height;
  - f6's insulation curve and silhouette;
  - the pull.

*What the person does.*
- **Per ribbon end**, about 55 s in all [w3 §3]:
  - snips and lays a strip segment (~20 s);
  - sets the ribbon pallet on its balls (~10 s);
  - pulls the tack lever and the shear lever (~15 s);
  - moves the pallet to the heavy station (~10 s).
- **Per unit:** ~13 min, plus loading the ribbon pallets and insertion.
- **The heavy station** runs 53–106 min per unit unattended, at 1–2 min per
  crimp.
- **Calls:** one per ribbon end, 14 per unit. A pallet rack at the heavy
  station would cut that [estimate].

**What each side brings, and what the pairing removes.**

| | a2 / a2e alone | f9 alone | K1 |
|---|---|---|---|
| Contact supply | strip | loose contacts in pockets, per half-row | strip, orientation from the strip |
| Placement | one docking per ribbon end | a presser comb per half-row, after a split into planes | one docking per ribbon end |
| Check before force | continuity to the carrier; camera | camera | continuity to the carrier; camera; identity in the nest |
| What holds the contact in the heavy stroke | a 0.8 × 0.2 mm tab in a row (0.10–0.14 mm elastic lift) | a keyed steel nest | a keyed steel nest |
| Neighbours in the heavy stroke | one strip pitch away, on the carrier | 3.4 mm away, forked 3–4 mm up; the other plane to park (B4) | one strip pitch away, hanging free; jaws ≤10.8–11.4 mm at 6.8–7.1 mm pitch [w3 §3] |
| Crimp height | applicator dials, stop blocks, or ΔF/k | knee and re-touch | knee and re-touch |
| Insulation height | one fixed step, or an IH wedge set by hand | re-formed by f3's step | f6's blade, set to the window per crimp |
| Parted length | 21–30 mm | 12–20 mm | 21–30 mm |
| Calls per unit | ~14 | ~34 | ~14 |

**Numbers** [w3 §3].
- **Contacts.** 81 per unit at N + 2 per ribbon end, with trimmed positions
  snipped out. That costs $1.90 from the SXH reel, $3.82 from 100-piece cut
  strip, or $0.64 from the CJT clone reel [xh-facts §6].
- **Tack comb.** Each notch mouth is as wide as the open wings (up to
  ~3.25 mm), which leaves 3.55–3.85 mm of steel between mouths at 6.8–7.1 mm
  strip pitch.
  - One pass tacks the whole ribbon end. c1b, at 3.4 mm, needs two passes with
    profiles at 6.8 mm for the same reason.
  - A loose tack's profile tolerance is a tenth or two, so laser-cut steel at
    ±0.127 mm serves (SendCutSend, 2–4 days [f&f f7]).
  - The plate is about as thick as the insulation barrel is long, 1.2–1.5 mm
    (c1b's figure), so it stays out of the window between the barrels.
    SendCutSend's thin gauges were not read [assumption].
- **Parted length.** 21, 25 and 30 mm for a 3P, 4P and 5P fanned alone to
  ~7 mm [pg §2].

**Branches.**
- **K1 by hand, the first week.** A dock jig, and the tack comb and shear on
  toggle levers. Then each tacked contact is crimped in today's SN-2549
  ([Prime], $22.29).
  - The tack is the locator the SN-2549 lacks. The person seats a contact
    that is already on its wire at its depth and roll, and squeezes: f9's
    third host.
  - Nothing moves by motor.
  - It tests docking, the tack's grip on silicone and the tack-first crimp on
    this ribbon before any press is built.
- **K1 with f7's cartridge.** The heavy station is a cartridge with a keyed
  nest in the VEVOR AP-1 arbor press ([Prime], $61.90, 150 mm opening, 90 mm
  plate, 281 ratings). The person strokes it to the cartridge's own stop.
- **K1-k: every k-th conductor** (f5-k × a2).
  - The parted length falls to what a 3–4 mm lift needs, 12–20 mm, at the
    cost of k docks and k tacks per ribbon end.
  - At the heavy station the neighbours then sit 1.7 mm away and must be
    lifted, which gives back the 11 mm jaw allowance.
- **K1 on loose kit contacts.** [a2c](../explorers/ribbon-as-pallet/ideas/a2c-loose-contact-cassette.md)'s
  keyed nest bar at 5 mm replaces the strip, and everything after docking is
  unchanged. A 5P needs 20–23 mm parted [pg §2], and pocket loading returns.
- **K1 with a curl tack.** f3b's station A is the gang tack, at strip pitch.
  - At 180–580 N per contact, a 5P takes 0.9–2.9 kN, so the tack block needs
    a steel local stop.
  - Curled wings trap the strands, not only the jacket.

**What it leaves open.**
- The tack's grip on silicone, and the tack-first crimp (f3b's four-arm
  sectioning experiment).
- Whether the loosely closed insulation wings hold each contact on the rail
  edge through 50–160 N of tab shear. The comb's fixed stop keeps it from
  crushing them further; the rail edge's position decides the rest.
- The nest's conductor anvil under the lance. That needs f&f's transition
  t ≥ 0.34–0.74 mm, or a lance slot in the anvil (§4).
- Lifting a box out of a slot with 0.05 mm clearance, by ejector.
- The strip pitch (the $4.71 strip settles it) and 21–30 mm of split behind
  the housing (Derek's call).

### Other pairings, named

- **K2: a docked row through a fixed knee** (a2 × f3, f6, f7).
  - The contacts stay on the carrier. The carriage moves the docked row in X
    through a fixed knee press whose narrow tooling is drawn for one strip
    pitch on each side. The strip pallet's rail is flush with the press's
    anvil, and a lance groove runs along X.
  - Each crimp gets a re-touch height and f6's insulation blade. The proof
    pull is made with a pad on the crimped barrels (§4).
  - It trades a2e's bought-applicator unknowns for a press Derek draws.
  - It keeps the tab window, now across a moving joint that must hold 0.05 mm,
    and X located between end grips.
- **K3: f8 fed by a pallet of per-conductor slides** (a7, a8, a6 × f8).
  - a7's tines fan the ribbon to housing pitch at the lid face, so conductors
    arrive in cavity order at 2.5 mm.
  - Each conductor rides in its own slide, which moves +Y with its contact on
    the push. The slides sit on two levels, odd above and even below, so each
    level is at 5.0 mm and a slide can be ~4.6 mm wide.
  - Stored feed becomes 5.2 mm of slide travel. The tip moves one-for-one with
    its slide, instead of the hump's gain of 1.7–3 [f&f on_ith §12]. Each
    tip's Y comes from touch-off at the fan face (0.01–0.05 mm [W2 §6]).
  - The person no longer lays conductors over saddles. J4's and J7's
    crossings stay by hand.
- **K4: half-rows cut from a housing-pitch fan and inserted as one merged row**
  (a1 pallet, a7 × f5b × into-the-housing i3). This is the repair of B1.
  - f5b's cassette crimps one plane while the other waits folded back at the
    lid face.
  - Both crimped rows then unpark into a 2.5 mm comb, where they are already
    interleaved at 2.5 mm [w3 §1], and the housing moves onto the row.
  - change-the-question's S2 (c1c + i6), in its wave-3 file on
    into-the-housing, reaches the same shape from its side.
- **K5: the backshell is the strain relief that the insulation crimp is not**
  (a3 × f6).
  - f6's number: on this silicone the strands slip inside the jacket at
    0.4–9 N, so the insulation barrel cannot carry the loom's pull.
  - a3's IDC-style fold carries 14–69 N at μ 0.5–1 [calc X §8] and never
    loads a crimp. This gives a3 a reason to exist that does not depend on
    the machine.
- **K6: bend-and-look on a whole row, with the pallet as the bending arm**
  (a6 × f6). This is the repair of B3.
  - The crimped contacts are held by their barrels in a row of pockets (the
    front pockets of a6's 2.5 mm clamp, or a comb at crimp pitch), with the
    insulation barrels' rear line on a steel edge.
  - The ribbon pallet swings on a hinge whose axis lies along that edge. At
    60–90° down, a fan-block face 9 mm behind the edge moves 7.8–9 mm down
    and 4.5–9 mm forward [w3 §6].
  - A downward swing puts the top of every insulation crimp on the outside of
    the bend, in one camera frame. Then it swings up, three times.
- **K7: f4's head as a touch probe** (a6's far-end port × f4).
  - The head's captured contact is on grounded steel. Brushing the barrel
    mouth's rim against a tip's sides and end closes the far-end circuit.
  - That locates each tip in X, Z and Y to ~0.01–0.05 mm [W2 §6] before
    threading. The camera then checks the tip rather than finds it.

---

## 2. What still breaks

### B1: f5b, f2c and f4's "where it leads": the later half-row has no feed to enter with

**The conflict.**
- **What each idea does:**
  - f5b's picture and sketch show a web clamp and give it no motion. The odd
    plane is laid straight into pockets, and a pusher drives the half-row into
    alternate cavities of a housing held at the lower shoe's front edge. The
    housing shifts 2.5 mm, and the even plane is laid into the reloaded
    pockets and pushed.
  - f2c's carriage holds the web. It sets crimped contacts into two 5.0 mm
    pallets, which are then pushed in turn.
  - In f4, a housing moves onto the first half-row, and "the second plane
    follows".
- **The stroke.** The insertion stroke, from fully behind the rear face to
  latched, is 6.0–9.0 mm with clone contact lengths and 6.3–8.2 mm with JST's
  [w3 §1].
- **The rule.** Every conductor of a ribbon end has the same length from the
  web, so every latched contact sits at the same distance D from it. A contact
  that starts behind the rear face sits at D − s on a conductor of length D.
  It needs s of stored feed.
- **What a straight lay gives.** A half-row laid straight can give only its
  spread's slack: 0.02–0.42 mm for rows of 2–5 (straight diagonals over
  12–20 mm), 0.1–0.73 mm through a tight fan [w3 §1].

**Consequence.**
- **As drawn** (web fixed, lay straight), the first push meets the conductors'
  length within half a millimetre. From there the pusher either pulls each
  crimp toward the web in the pull-out direction, or drags the ribbon through
  the web clamp.
- **If the web follows the first push,** the other plane's contacts are carried
  to D with it. D is inside the housing, so they can never reach their
  cavities' rear entries.
- **In f4,** once the housing sits over the first plane's contacts, the second
  plane cannot even be crimped at its comb position: that position is inside
  the housing.

**Repairs, each a branch.**
- **One merged row and one housing move, with zero stored feed (K4).**
  - Crimp plane A in the pockets, lift it out (the pockets are open on top),
    and park it folded back. Lay and crimp plane B.
  - Unpark both rows into a 2.5 mm comb and move the housing onto the row
    (into-the-housing i3).
  - The planes, each spread about the ribbon's centre by 5.0/3.4, interleave
    at exactly 2.5 mm [w3 §1]. Crimped contacts fit side by side at 2.5 mm,
    with 0.45–0.7 mm between insulation crimps.
  - *Costs:*
    - f5b's "the lower shoe is the insertion pallet" does not survive: its
      pocket walls stand where the other plane's contacts must go.
    - Each conductor folds at the root once or twice more. The clamp face
      must be exactly the split root (a7's tear stop, or a3's backshell face)
      so the folds do not peel the web.
- **Store s in every conductor.**
  - Fix the web at the loom's final distance, and lay every conductor of both
    planes over a hump of 4.7–7.7 mm on a 10–20 mm chord [w3 §1]. Each push
    consumes its own row's humps.
  - *Costs:*
    - The humps must fit in a 12–20 mm split that already holds the V-tooth
      comb and the presser comb.
    - The upper shoe needs a relief over the humps.
    - The hump's Z-to-Y gain of 1.7–3 [f&f on_ith §12] acts on each tip at
      the stop bar.
- **Cut the planes to different lengths.** A two-level fan block could do it,
  but the finished loom would then carry 6–9 mm of bow in half its
  conductors. It is recorded here, not developed.

**Agreement.** change-the-question reaches the same rule for c1 and c1c in its
wave-3 file on into-the-housing (S2 and §4 there, "a bow of 4–9 mm").

**Left uncertain.** Whether a parked, crimped half-row can unpark into a
2.5 mm comb with no pick (straight looms), or needs i6's sort (J4 and J7).

### B2: f5b stripped before the spread, and the V-tooth comb's limit

**Stagger.**
- c1 and f5b strip flat while the ribbon is webbed, then spread each plane
  from 3.4 to 5.0 mm. The spread pulls outer tips back against inner ones by
  its path excess.
- The resulting insulation-edge stagger [w3 §2]:

  | Row of | Straight diagonals over 20–12 mm | Tight S-bend (R 5 mm, 30°) |
  |---:|---|---|
  | 2 | 0.02–0.03 mm | 0.11 mm |
  | 3 | 0.06–0.11 mm | 0.31 mm |
  | 4 | 0.14–0.24 mm | 0.52 mm |
  | 5 | 0.25–0.42 mm | 0.73 mm |

- The axial window is ±0.2–0.3 mm [f&f placement_budget].
- f5b's stop bar can bring the tips to one line only by pushing the inner
  conductors into a bow. The stagger then moves to the insulation edges.
- *Repair:* strip after the spread, at the comb face. a8 rolls a whole row
  under two fixed razors at any pitch, and the stagger is then zero by
  construction. For rows of 2–3 the existing order stands.

**Capture.**
- A straight-descending V-tooth comb captures a move under half a slot, less
  the lay error. Rows of 4 and 5 fail by −0.1 and −0.9 mm [ctq off §4].
- A grooved fan block pressed down from the root captures differently. Its
  grooves start at the plane's 3.4 mm pitch, where the conductors already lie,
  so it captures at the root and the capture propagates outward. The move
  itself never limits it.
- What does limit it is the ribbon's pitch stack at the root: 0.23 mm worst
  for a 5-conductor end, 0.43 mm for J1's 9 conductors. Against a 1.7 mm
  half-pitch in the plane that leaves 1.27–1.47 mm of margin [w3 §2; pg §1].
- J1's 5-row and the 4-rows then lay without a tilted or rolling comb.

**Transport.**
- f5b loads at a bench under the camera, and then the cassette goes under the
  press with the conductors lying loose in open barrels.
- The web clamp has to travel with the lower shoe. A ribbon pallet seated
  kinematically on the lower shoe does that.

### B3: f6's bend-and-look, done at the press, can only bend the way that closes a tip cut

**The conflict.**
- The wing tips of a B/F insulation crimp sit on top. f6's window model has
  "the curled wing tips of a B/F insulation crimp press p = 0.1–0.3 mm deeper
  than the roof's mean inner surface" [f&f wave2 §5].
- A cut at a tip opens only when the top is on the outside of the bend, which
  means bending **down**. At f3/f6's press:
  - **Down is blocked.** f3's strip track and carrier lie at floor level
    directly behind the dies. The floating shear drops the carrier, not the
    track.
  - **Sideways is blocked.** A 60–90° bend over a 2 mm pin sweeps at least
    1.8–2.7 mm to that side. Between jackets there are 1.7 mm at 3.4 mm pitch
    and 3.3 mm at 5.0 mm [w3 §6], and the fork's neighbours are there.
  - **Up is free,** and bending up puts the tip zone on the inside of the
    bend, in compression.

**Consequence.** A crimp whose tips have cut the jacket passes bend-and-look at
the press. The check built for this failure closes the cut while it looks.

**Repairs.**
- Drop a section of the track behind the insulation barrel, with the floating
  shear, after the tab cut. That leaves at least ~3 mm below the barrel's rear
  edge for a downward bend.
- K6: bend the whole crimped row downward at once at a pallet station.
- f6's overlap-profile branch moves the tips to the sides. Sideways bends then
  matter, and the neighbours are the obstacle.

**A number to correct.** f&f wave2 §7 labels its pins by radius: a "1 / 2 /
3 mm pin" gives strain 0.46 / 0.30 / 0.22. f6's 2 mm hardened dowel, in both
the idea and the sourcing request, is a diameter. Its surface strain is 0.46,
and a through-cut gapes 0.23–0.56 mm, not 0.15–0.37 [w3 §6]. The cut is easier
to see than stated, and the bend is harder on the jacket.

**Left uncertain.** Whether a tip cut in this silicone shows only at the top,
or also where the wing edges meet the jacket's sides.

### B4: f9, the other plane at station C

**The conflict.**
- Station T tacks both half-rows, odd then even, so at station C both planes
  hang from one clamp.
- The other plane's tacked contacts sit ±1.7 mm in X from the working one.
  That is inside the half-width of f3's crimper and nest block (1.75–2.2 mm),
  whether they hang 3.4 mm below (into the nest block) or above (into the
  crimper holder).
- f9 names the fork that lifts in-plane neighbours at 3.4 mm. It does not name
  the other plane.

**Consequence.**
- The other plane must be parked at C as it was at T, folded back at the root,
  and swapped once per ribbon end. Each conductor then sees 3–4 root reversals
  across T and C.
- Or the person re-clamps each ribbon end once per plane, and ~34 calls per
  unit become ~48 [estimate].

**Repairs.**
- Tack on strip at strip pitch (K1): there are no planes.
- Keep the planes, but make the clamp face exactly the split root, so the
  folds do not peel the web (a7's tear stop, a3's backshell).

**What these numbers settle in f9.**
- f9's first open item: "a contact that arrives rolled several degrees and is
  squared by the chamfers asks more, and may turn on the jacket".
- Squaring a 5–10° roll on 10–30 mm of free conductor takes 0.03–0.2 N·mm,
  with the strands free to slip (GJ ≈ 11.7 N·mm² [w3 §3]). Moving the contact
  0.3–0.5 mm sideways takes 1–3 mN.
- The tack holds 0.4–2.5 N·mm and 0.4–9 N. So the conductor twists and bends
  long before the tack slips, as long as at least 10 mm of conductor is free.

**Datum.** At C the person re-clamps the tacked ends into the carriage, so each
tacked contact's position relative to the new clamp is whatever handling left.
One pallet carried from T to C keeps it, and the nest does the rest.

### B5: f1, the fork's bend is a set, not a gentle bend

- f1 says the fork "holds neighbours up and out of the jaw plane; with
  20–30 mm of split this is a gentle bend".
- While conductor i reaches into the nest, the neighbour tips must stand clear
  of the jaw's top face, 4–6 mm higher [estimate: the barrels sit 3–4 mm into
  the nest, plus clearance]. That puts them 30–46° out of line over 20–30 mm
  [w3 §9].
- The copper sets below a ~67 mm radius [pg §4]. So every neighbour leaves f1
  with a 30–46° set at the fork line. It points one way for conductors crimped
  before it and the other way for those after it.
- Insertion then has to take it out: a6's clamp, or a person.
- c1's planes (neighbours at 3.4 mm in the plane) do not change the height
  that must be cleared, only which conductors have to clear it.

### B6: f8, the 3.1 mm crimper against a seated neighbour's jacket

**The clearance.**
- f8's own numbers are 3.30 mm free at a seated neighbour's equator against a
  3.1 mm conductor step, "~0.1 mm a side". With the ribbon's OD at 1.7 ±0.1 mm
  that is 0.05–0.15 mm a side.
- The seated wire also has play in the cavity's rear opening: 0.07–0.25 mm for
  an opening of 1.95–2.10 mm [assumption; the real opening is unmeasured].
- Net: −0.10 to −0.02 mm [w3 §8]. The crimper's walls rub each seated
  neighbour's jacket at its equator.

**Consequence.** Small. The jacket moves ≤0.1 mm under sub-newton force, and the
neighbour is latched. It shows as a scuff at the equator of the neighbours on
each side of every crimp.

**Repair.**
- Walls of 0.7 mm, the low end of f8's own wall rule, return 0.1 mm a side.
- A comb 3–5 mm behind the rear face, outside the crimper's Y range, centres
  the seated wires. It does not remove their play in the opening.

---

## 3. Consistency

- **C1: crimp height and width (digest, KONNRA, f3, f7).**
  - The digest lists KONNRA's 0.73 ±0.05 mm beside the context's ~0.88 mm as
    two different crimp heights. With their widths they describe the same
    compaction [w3 §7]:

    | Source | Width × height | W·H |
    |---|---|---:|
    | KONNRA clone spec | 1.75 × 0.73 mm | 1.28 mm² |
    | Context estimate | 1.50 × 0.88 mm | 1.32 mm² |
    | JST's SXA analog [mfr S14] | 1.50 × 0.80 mm | 1.20 mm² |

    Each is right for its own width.
  - For force-and-form, f7's ground-stock anvils give channels of 1.54–1.58 mm
    (1.5 mm gauge plate) or 1.63–1.67 mm (1/16 in). Their targets are
    0.72–0.86 mm.
  - A height copied unchanged from a ~1.5 mm-wide reference over-compacts by
    3–10 %. That reference is the JST lead, through ctq's copper correction,
    which assumes W = 1.5 mm.
  - So the copper correction has to be redone at the machine's own channel
    width, both for f3's wedge target and for f2's dial.
- **C2: channel tolerance (f7 and wave2 §8, against xh-facts §1).**
  - f7 asks for ±0.01 mm on the conductor channel. wave2.py states that figure
    without deriving it.
  - J.S.T. UK publishes conductor crimp width ±0.05 mm for SXA and SXH-002
    [mfr S13, S14]. At a fixed height stop, ±0.05 mm of width changes
    compaction by ±3.3 % [w3 §7].
  - The tighter need is the anvil's fit in the channel. That is met by
    choosing the anvil to suit the cut channel, from ground stock in several
    thicknesses.
  - Width alone therefore does not rule out quick-turn EDM at ±0.05 mm. What
    nobody has toleranced is the roof's form: the arches and the cusp height.
- **C3: bend strain (f&f wave2 §7, against f6).** The calc's pin sizes are
  radii; f6's are diameters. The strain is 0.46, not 0.30 (B3).
- **C4: latch retention (f3, f8, on_ith §7).**
  - "A latched contact holds only ~15 N" comes from a Molex analog (14.7 N).
    KONNRA's XH clone spec gives ≥19.6 N (cited in a6; into-the-housing's
    summary lists both).
  - For an XH part the clone spec is the nearer figure.
  - The conclusion, a proof pull before insertion, stands. Its reason shifts:
    a 20 N pull after latching sits at the clone's minimum retention, not
    above it.
- **C5: the insulation crimp on silicone agrees across two calcs.**
  - f&f wave2 §5 finds that KONNRA's 1.80 mm height needs 20–30 % of the jacket
    squeezed out. My W2 §9 finds that 1.80 × 2.05 leaves the jacket at ~70–80 %
    of its area. The two were reached separately and agree.
  - f6's window, 1.8–1.9 mm wide, leaves 0.6–0.7 mm between insulation crimps
    at 2.5 mm pitch. a6 assumed 0.45 mm at KONNRA's 2.05 mm, so a6's clamp
    pockets gain room.
- **C6: the f8 clearance** (B6). on_ith §2 takes the X offset "off the
  0.2–0.45 mm clearance", but that clearance belongs to a narrower punch than
  f8's. Under f8's own 3.1 mm crimper from §3, a ±0.14 mm RSS offset has
  nowhere to go except into the floating-nest repair.
- **C7: f2b's open press height is answered by the Prime pass**
  ([Prime], *Crimp and press*).
  - The Harbor Freight 1 t press opens 139.7 mm. The VEVOR AP-1 (1 t) opens
    150 mm. Both are short of the 166–176 mm an applicator needs.
  - The VEVOR AP-3 (3 t, $255.90, 310 mm opening, 130 mm throat, 28 ratings,
    thin) and the VEVOR PR-3 ratchet (3 t, $262.14, 310 mm, 44 ratings, 50+
    bought in past month) both open far enough.
  - Pinion radius and ram play remain unmeasured.
- **C8: other Prime rows that change force-and-form's evidence.**
  - *f3's 0.001 mm indicator:* the Clockwise DITR-0105 is $52.99 with an RS232
    port, against f3's $451–668 Mitutoyo. Its DTCR-01 cable had no Prime
    listing.
  - *f7 route 1, SN-2549 replacement jaws:* no Prime listing. The only Prime
    2549 die is in the IWS-0723K set ($46.59, 9 ratings), and it comes in a
    frame.
  - *f7's disc-spring pusher:* the Prime Belleville assortment is light-duty
    stainless, and no 3–4 kN stack is shown.
  - *f1's actuator:*
    - Justech 1,500 N, 50 mm stroke, $29.99, no position feedback;
    - PA-01-POT, 750 N with a potentiometer, $155.39.
  - *f2's OTP applicator and f7 route 2's knife set:* no Prime listing. They
    stay with eBay, AliExpress and Alibaba.
- **C9: f1's "gentle bend"** (B5), against the 67 mm set radius [pg §4].
- **C10: the insertion stroke agrees.** c1's "~7 mm", into-the-housing's
  8.2 mm (box nose 1 mm behind the rear face) and [w3 §1]'s 6.0–9.0 mm are
  consistent.

---

## 4. Transfers

### From this view into force-and-form's

1. **Length from the web is a design quantity** (B1). Every contact of a
   ribbon end latches at the same distance from the web. Any group that enters
   after another needs its stroke stored as length, or the groups go in
   together.
2. **Flush-cut and strip after the fan** (B2), into f5b and f4's comb board.
   Otherwise rows of 4–5 carry a 0.14–0.42 mm insulation-edge stagger.
3. **A fan that captures at the root** (B2), into f5b's lay and f4's comb.
4. **The ribbon pallet as the travelling datum:**
   - f9, from T to C;
   - f5b, from bench to press to push;
   - f2c, where it also answers "setting a crimped contact into a ~2.1 mm
     pocket from a carriage holding the web 12–20 mm back". The conductor
     bends at 1–3 mN [w3 §3], so the pocket's chamfers do the locating and the
     carriage only has to reach them.
5. **The far-end port as a per-station check.**
   - In f5 and f5b it reads each conductor to the grounded shoe before the
     stroke. That names the station the summed force cannot name.
   - In f3, f9's C and f8 it is an identity check: only conductor k may touch
     the nest.
6. **Touch-off as a probe** in f4 (K7).
7. **The clamp face as the split root,** wherever force-and-form parks a plane:
   f5b, f9, and f2's fork between planes. a7's tear stop or a3's backshell face
   keeps each fold from peeling the web.
8. **Grip each conductor at the fan face for a proof pull** (f5's pull on a
   fanned row). A pull across the whole pallet straightens the S-bends at
   0.36 N·mm before any crimp is loaded [pg §4].
9. **A whole row bent at once** for f6's check (K6).
10. **The backshell fold** as the loom's strain relief (K5).

### From force-and-form's view into this one

1. **The lance, wherever a2 touches a contact.**
   - *a2's support comb, a2e's loading shelf, a2b's strip-pallet windows.* On a
     flat face every contact sits propped 7.6–15.9° about its tab on its lance,
     against the tab's ~2.3° elastic bend [w3 §5]. Each face needs one of:
     - a groove along X under the lance line, 2.2–2.7 mm behind the contact
       front and at least 1.1 mm deep, as c1's carriers have;
     - a rail under the insulation barrel only (K1).
   - *a2's walking head.* It approaches from the box end with its lower die at
     floor level, and the lance hangs across that path. The die can pass under
     the lance and rise behind its tip only if the transition t ≥ 0.34–0.74 mm
     [w3 §5; f&f on_ith §1d]. That is the same unknown that decides f8.
     Otherwise the head's lower die drops and rises, as f4's anvil does.
   - *a2b's anvils,* rising through windows, each need f&f's lance relief.
2. **Pull on the box's rear face, or hold the barrels down.** a2 and a2e
   proof-pull each conductor against the carrier.
   - The wire's axis stands 0.95 mm above the tab's mid-plane, so the tab
     yields at a pull of 2.5–4.6 N. Every contact pitches about its tab long
     before 20 N [w3 §4; calc X §5].
   - Repair: the shear comb's pad on the crimped barrels during the pull
     (3.8–6.3 N of pad).
   - Or f3's neck blade bearing on the box's rear face.
3. **f6's window, into a2b and a2e.**
   - a2b's one-piece punches fix the insulation step for all N stations (f5b's
     own note).
   - a2b's sub-branch "gang the conductor barrels, walk the insulation
     barrels" becomes the way to set each insulation crimp by position.
   - a2e's IH wedge is set to ~2.0–2.2 mm by f6's sweep, not left at a PVC
     setting.
4. **f7's cartridges and one-piece plates, into a2b and a2d.**
   - At a strip pitch of 7.1 mm, a one-piece crimper plate's webs are
     5.1–5.6 mm (at 5.0 mm pitch, 3.0–3.5 mm).
   - Ground stock stood on edge makes the anvil block and the shear comb's
     die edge.
5. **Re-touch, into a2e.** Back the crank off and bring it down to 10 N with an
   indicator across ram and base. That reads each crimp's height directly,
   alongside b1b's ΔF/k.
6. **f8's crown, into a2e's downstream room.**
   - a2e's open problem is whether crimped contacts still on their carrier can
     move downstream past the anvil.
   - Bend the carrier down over a crown just downstream of the anvil. That
     drops the crimped contacts 3.6–4 mm below the tooling, with a crown radius
     of 5.8–7.0 mm and 1.4–1.7 % carrier strain [w3 §10]. The carrier is scrap
     after the tab shear anyway.
   - The crimped contacts' conductors take a small set (S radius 14–56 mm on
     15–30 mm of free conductor), which a6's clamp takes out.
7. **The neck blade as a local placement check.**
   - In a2, a2e and K1, the far-end pogo port confirms placement. That needs
     the person to press every loom's far end into a pogo block.
   - f3's neck blade closes blade → strands → barrel → contact locally.
   - A comb of insulated neck blades on the strip pallet, one per contact in
     the neck between box and conductor barrel, would confirm each
     conductor's strands at depth with no far-end wiring.
   - It works only if t leaves room for a 0.3 mm blade. That is the same t
     again.
8. **The tack** (f9, from c1b). It is what lets a docked row leave its carrier
   before the heavy stroke (K1).
9. **Scale the target height with channel width** (C1), into a2b's stop blocks
   and a2e's dial.

---

## Questions this exchange adds for Derek

- **One kit contact, side-on under the ELP camera.** Photograph the transition
  t from the box's rear to the conductor barrel's front, and the lance's root
  and tip. It now decides f8, a2's walking head, K1's nest anvil and the
  neck-blade comb.
- **A tack test by hand.**
  1. Lay three contacts of a strip segment under three split, stripped
     conductors.
  2. Close each insulation barrel loosely with smooth pliers, and cut the
     tabs.
  3. Pull and twist each contact on its conductor with the bench scale.

  It settles K1's and f9's first question at once.
- **Five SN-2549 crimps on the ribbon, bent down.** Bend each 90° over a 2 mm
  dowel just behind the insulation barrel, and look from above. This is f6's
  check done the way that can open a tip cut.
- **Is a 21–30 mm split behind the housing acceptable?** K1 and a2 need it.
  f5b needs 12–20 mm, but B1 then asks for either extra folds or 5–8 mm humps
  in that split.
