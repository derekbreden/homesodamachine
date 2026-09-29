# p1 Cassette and benches

Sketches: [`../sketches/p1-cassette-and-benches.svg`](../sketches/p1-cassette-and-benches.svg)
(the cassette and the benches), [`../sketches/p1-crimp-station.svg`](../sketches/p1-crimp-station.svg)
(bench B in its B-drop form). Numbers: the first calcs in [`../calc/`](../calc/) by
name, [`../calc/wave2.out.txt`](../calc/wave2.out.txt) and
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) (cited as [calc wave2 §n] and
[calc wave3 §n]), and force-and-form's
[`exchange_procedure_w3.out.txt`](../../force-and-form/calc/exchange_procedure_w3.out.txt)
(cited as [calc FP §n]).

A printed **cassette** holds one housing's worth of ribbon end from the person's
hands to the finished housing. Separate single-purpose **benches** do one job
each, and the person carries cassettes between them. The cassette's pins are
the only reference the benches share. The crimp bench, the step Derek most wants
automated, can be built first and used alone; the others join later, and
[p1b](p1b-carousel-joins-the-benches.md) connects them with a carousel.

The crimp bench, bench B, stands in three forms that share the cassette:
- **B-drop** (this file): a slotted presser drops the waiting conductors beside a
  tall fin anvil that carries a contact already cut free;
- **B-lift** ([p1c](p1c-lift-once-tip-down-module.md)): conductor *k* alone is
  lifted 8.7–14.7 mm under an SN-2549 module lying on its side;
- **B-fin** ([p1d](p1d-lift-once-fin-from-below.md)): *k* alone is lifted 3.5 mm
  and a fin rises from below into a steel C.

## Picture it: J1, 5P + 4P into an XHP-9

**Where things start.**
- The person cuts the 5P and the 4P to J1's longest leg (~350 mm [repo]) plus
  service loop, square across, and peels the web back at the XH end: 25–30 mm for
  B-drop, 30–35 mm for B-lift, 20–25 mm for B-fin (today's step 2 [repo
  cable-assemblies.md]).
- The contacts are SXH-001T-P0.6 from a 100-, 500- or 1,000-piece strip
  [xh-facts §1, §6], or loose kit contacts. Either way they reach bench B cut
  free of any carrier: a one-pitch stub, a loose piece on a post, or a loose
  piece on a blade.
- The loom's far end is left raw. Its cut face goes into a pogo block that rides
  on the cassette.

**Loading (person, ~1 minute per cassette [estimate]).**
- The person lays both ribbons flat in the cassette's clamp, the 5P's edge
  against the datum wall, and closes a cam lever on TPU pads. The clamp has a
  hard stop that sets a 15–30 % squeeze of the jacket over 10–20 mm, so the
  copper cannot creep inside the jacket when a crimp is pulled [calc FP §4].
- The conductors go into a printed **fan plate**: nine grooves take them from
  1.7 mm ribbon pitch to 2.5 mm housing pitch over ~20 mm, under a hinged lid.
- They leave through a **comb** of 0.635 mm music-wire pins at 2.5 mm pitch
  [Prime: Music wire, 0.025 in, K&S 5005, $7.24].
- Each groove is a **key** numbered for the cavity it feeds: key 1 is cavity 1.
  The tips stick out loosely. Nobody measures anything.
- The tail (100–600 mm) coils flat into a tray under the cassette.

**Bench A, trim and strip.**
- The cassette drops onto two dowels (or three balls into three V-grooves
  [Prime: chrome steel balls, 6 mm, G25, $6.65]); a magnet holds it [Prime:
  N52 10 × 3 mm disc magnets, $23.99].
- A razor blade in a printed carrier slides along a slot in the cassette's own
  front. The slot is the blade guide, so the cut line belongs to the cassette.
  It cuts the nine conductors one after another as the angled blade passes
  (~40–65 N per conductor [calc spool_test §3]).
- Each conductor is then stripped 2.4 mm [mfr S6]: a lead screw indexes key *k*
  to the station line, a lift finger raises *k* clear of the row (nothing
  presses the others), V-jaws close 2.4 mm from the tip and pull the slug ~3 mm,
  and the slug drops.
- Or the webbed end is stripped whole before the person peels it, with
  [p7](p7-strip-before-split.md)'s lever at loading.
- In B-lift and B-fin, trim and strip move to bench B, in the pose the crimp
  uses, and bench A is not needed.

**Bench B in the B-drop form.**
- **The contact waits on a fin anvil before the wire arrives.**
  - The fin is hardened steel standing 9–10 mm above its base, **stepped**:
    ~1.45 mm wide under the conductor barrel and 1.8–1.9 mm under the insulation
    barrel. The anvil sits inside the crimper's channel, and JST's analog
    SXA-01T-P0.6 crimps 1.50 mm wide at 22 AWG [mfr S14]; a 1.6–1.9 mm fin under
    the conductor barrel would make a crimp 1.66–1.96 mm wide and lower than
    that profile [calc FP §2].
  - Free-topped at that width it buckles near 5.1–6.3 kN, above the 3 kN design
    force; the crimper's legs guide its top at compaction [calc wave3 §2].
  - The contact on it is cut free: a one-pitch carrier stub on a pin in its
    pilot hole (hand-tool-as-press a2), or a loose contact held by a1's 0.3 mm
    blade in its neck, box forward, barrels up.
  - The fin is ground flat stock stood on edge, or laminated 1095 shim
    (0.032 + 0.025 in = 1.448 mm; 0.032 + 0.032 + 0.010 in = 1.880 mm [Prime:
    Spring steel shim, 0.005–0.032 in, $53.39]), or cut from an SN jaw or an
    applicator's anvil plate (force-and-form
    [f7](../../force-and-form/ideas/f7-where-the-steel-comes-from.md)).
- **Why no strip reaches the fin.** A side-feed strip joins each contact at the
  rear of its insulation barrel, in the floor plane, running across the row
  [xh-facts §1]. Under that line sit the feed plate, the pressure plate, the
  shear blade supporter and the scrap chute, and upstream the next contacts
  stand open at ~7.1 mm pitch. Neighbours pressed 7 mm down land on that
  hardware [calc exchange_borrowed §1; hand-tool-as-press]. So B-drop takes
  contacts cut free and uses no applicator.
- **Selection.** The cassette sits on bench B's slide and indexes key *k* to the
  fin line at 2.5 mm per step. The slotted presser comes down over the row:
  every conductor under the plate goes ~7 mm down, and *k* passes up through the
  plate's slot and stays level. The fin stands between *k*−1 and *k*+1, which
  leave 3.3 mm between them.
- **The set this costs.** Each waiting conductor is pressed once per earlier
  cycle, and the first press leaves it low: 3.7–6.5 mm at 15 mm free, 1.3–4.5 mm
  at 20 mm, 0–0.9 mm at 30 mm [calc wave2 §1(a)]. So *k* is **captured from
  below**: a V-fork rises to a fixed height under key *k* 5–6 mm behind the
  strip line and lifts it to level. The V does not undo the tip's 0.4–1.1 mm
  pull-back at 15 mm, so B-drop wants a 25–30 mm split.
- **Placement.** A lay-in finger through the presser's slot pushes the conductor
  ~1.5 mm down into the open barrels: strands onto the conductor barrel's floor,
  insulation edge in the window, jacket between the insulation wings. The axial
  position comes from the trim line, carried by the cassette's pins, and from
  the contact's own reference on the fin (the blade on the box shoulder,
  ±0.075 mm).
- **Identity.** The strands land on the barrel floor, and the fin is an
  electrode, so the far-end pogo block reads which conductor lies in the
  contact before any force.
- **Crimp.** The V-fork drops away before the punch arrives, and a spring leaf
  on the punch stack holds the wire through the stroke (JST's "wire hold
  spring" for its MKS-L applicator). The punch descends slowly on a ram until
  steel stop blocks beside the fin meet: the stops set crimp height in a short
  steel loop. The ram is the bench's NEMA 23 on a lead screw, or a lever, and it
  pushes through a stiff spring so its overtravel past the stops costs only
  k × overtravel: a loop of 5–10 kN/mm pays 1.05–1.4× the crimp and caps a
  doubled contact at 3.9–5.4 kN [calc wave3 §4]. The force goes punch → stops
  and fin → bench frame; the cassette carries none of it.
- **Release.** The punch rises, the finger lifts, the presser lifts, and *k*
  springs back into the row carrying its contact.
- **Proof pull through the box, punch up.** A hook drops in behind the box's
  rear shoulder, and the slide pulls the cassette back 0.5 mm against a 20 N
  spring with a switch. The load goes box → crimp → conductor → cassette clamp.
  Holding the punch down instead would clamp the barrels with 30–400 N of
  friction and test nothing (hand-tool-as-press).
- **Knowing it worked.** The force curve from foil gauges on the fin holder, or
  a load cell under the whole lower die (fin holder and stops together, outside
  the stop loop [calc wave3 §4]; the HX711 samples at 80 Hz [prior-art §6]); the
  stop contact shows as a sharp rise in stiffness, and a crimp that climbs
  steeply before it is high. An ELP frame under a ring light [Prime: AmScope
  LED-144W-ZK ring light, $35.99]: brush, bellmouth, insulation in the window.
  The pull and its switch. Identity. Everything is logged against the
  cassette's ID and key.
- The next key follows; J1 takes nine cycles.

**Bench C, insert and test.**
- The XHP-9 sits in a nest in front of the comb, cavities on the keys' lines.
- All nine contacts end on one line, upright, so the housing slides back onto
  all of them at once [calc selector_and_bow §3].
- The housing then mates onto a B9B-XH-A test header. With the far end in the
  cassette's pogo block, the test is pin to pin: opens, adjacent shorts, pin
  order and J2's empty cavity 3.
- The person unclamps the cassette and labels the housing. Before bench C
  exists, the person inserts by hand from the cassette.

**J2 in the same cassette.** Six keys, key 3 blanked by a printed plug, so no
conductor can be laid there. 3P-a's third conductor is trimmed back at the fan
plate at loading. The cassette's ID tells bench B to skip key 3. The empty
cavity is decided physically at loading and cannot drift.

**J4 and J7.** A conductor has to cross others to reach its cavity [repo
pcba.tsx pin order]. The person makes the crossing at loading, in a raised loft
over the fan plate. After loading every cassette is "key *k* = cavity *k*", and
the benches never know a crossing happened. Identity at every crimp catches a
crossing laid into the wrong key.

## What locates what

| Moment | What is located | Against what | Held to |
|---|---|---|---|
| Loading | ribbon edge | cassette datum wall | ±1 mm, by hand |
| Trim | conductor tips | cassette blade slot | ±0.05 mm to the pins [estimate] |
| Any bench | cassette | bench dowels or V-grooves | ±0.02–0.05 mm [estimate] |
| Crimp, lateral | conductor *k* | B-drop: V-fork rising from below at the moment of use | ±0.05 mm |
| Crimp, axial | contact | fin and neck blade, or stub pin (bench frame) | ±0.075 mm |
| Crimp height | punch | stop blocks beside the fin, in a short steel loop | ±0.02–0.05 mm needed [xh-facts §4] |

"Fixed" is each bench's frame. Between benches the only reference is the
cassette's pins. Precision is needed at the trim, the fork's capture and the
bottom, and nowhere in between. The lateral chain comes to ±0.13 mm RSS with the
fork [calc transfer_capture §2]. The axial chain for B-drop (strip at bench A,
contact on the neck blade) is ±0.23 mm RSS, and ±0.33 mm with a loose contact
stopped by its box front, against a ±0.3 mm window; B-lift and B-fin, with the
camera measuring the bare length, are ±0.07–0.09 mm [calc wave2 §3].

## Build stages: what the machine does and what the person does

| Stage | Machine does | Person does |
|---|---|---|
| 1 cassette only | nothing | everything, with the cassette enforcing pin order and J2's blank; SN-2549 by hand, one key lifted at a time |
| 1.5 cassette + hand-tool-as-press a1 squeezer | hold, crimp, force curve, identity through the far-end block | index with a lever, lift *k* with a lever, place a contact, slide the cassette toward the tool, pedal. The squeezer lies on its side so the crimp is upright (p1c's pose, turned by hand) |
| 2 + bench B | place, crimp, log | cut, peel, load, trim at the cassette slot, strip with a jig or p7's lever, insert, test |
| 3 + bench A (B-drop), or bench B-lift / B-fin | trim, strip, place, crimp | cut, peel, load, insert, test |
| 4 + bench C | + insert, pin-to-pin test | cut, peel, load, carry cassettes, label |
| 5 p1b | + carrying | cut, load, label |

**Batching.** The person loads a unit's ten cassettes in one sitting into bench
B's magazine and walks away. Bench B runs the unit's 53 crimps alone, ~1–1.5 h
[calc person_timeline; calc wave3 §6]. The person's attended minutes fall from
~46 to ~36–44 [calc person_timeline; calc wave3 §6; estimates, compare rows].
The crimp is the most skill-dependent step but not the biggest share of the
person's time: peeling, laying in and inserting are.

**Recovery.** A crimp flagged at bench B stops that cassette, which goes to an
out-tray with its key noted. The person opens the clamp, slides the ribbon
~6 mm further out, re-peels ~6 mm more and re-closes. The whole end is trimmed
back at the same line, taking the bad contact and its good neighbours with it
[calc recovery_length §1]. The loom is ~6 mm shorter.
- How many redos a loom can absorb depends on how much shorter than its cut
  length it may end up, a question for Derek.
- With 12 mm allowed and a 2 % bad-crimp rate, ~0.4 looms are scrapped over the
  61-unit program; at 10 %, ~35 [calc recovery_length §3].
- Making the XH end before the far end's Fastons means a scrapped loom loses
  ribbon, not hand work. [p6](p6-spool-end-bench-that-grows.md) makes it on the
  reel, where a redo costs reel.

## Printed and bought

- **Printed** (PETG or PET-CF; TPU pads): cassette body, fan plate and lid, comb
  block with a crossing loft, key blanks, tail tray, ID bumps (a 4-bit pattern
  read by microswitches [Prime: KW12-3 roller micro switches, $5.99]) or a
  printed code the camera reads, presser, V-fork, lay-in finger, lift finger,
  strip-jaw carriers, the far-end pogo block.
- **Contacts:** SXH-001T-P0.6, Digi-Key 100/500/1,000 lots at $0.047/0.042/0.040,
  3,100/2,500/5,000 in stock [xh-facts §6]; or kit contacts [Prime: CQRobot JST
  XH kit, $7.99–10.99].
- **B-drop steel:** the stepped fin (above) and a punch: an SN-series crimper half
  (the only Prime route to a loose 2549 die comes in a frame [Prime: iCrimp
  IWS-0723K 7-piece set, $46.59]), or an OTP XH knife set or applicator (no
  Prime listing; ~$155 plus ~$91 shipping on eBay [prior-art §4]); stop blocks
  and shims.
- **Motion:** one lead-screw slide per bench [Prime: NEMA 17 with integrated
  T8×2 lead screw, $27.99; MGN12 rail, $20.49]; the bench's NEMA 23 + DM542T
  for the ram if it is free of the cap-weld rotator [repo tools.md]; a
  controller [Prime: BIGTREETECH SKR Pico, $35.99] or an ESP32.
- **Location:** dowel pins [Prime: M6 × 40 mm ground dowel pins, $6.49; 304,
  not hardened], 6 mm balls, magnets, music wire.
- **Sight and force:** the ELP camera on hand [repo]; ring light; foil gauges
  [Prime: BF350, $6.99] or a load cell and HX711 [Prime: SparkFun HX711,
  $11.50].
- **Test header:** B9B-XH-A, Digi-Key 44,226 in stock at $0.175–0.34 [source:
  findchips via into-the-housing], or the headers in the CQRobot kit.
- **Far end:** P75 pogo pins [Prime: MEETOOT P75-E2, 100 pack, $6.49].

## Problems, and what answers each

1. **Keys at 2.5 mm are too thin to print** (~0.3 mm walls for a 1.7 mm
   conductor). The grooves exist only in the fan plate, where the conductors
   are still converging under the lid; at 2.5 mm the comb is steel pins, which
   need no walls. A 0.64 mm pin leaves ~0.08 mm a side against a 1.7 mm
   conductor, so the silicone squeezes [assumption].
2. **Crimping in the row at 2.5 mm leaves no room for tooling** [into-the-housing
   calc §2]. Each form of bench B gets out of the plane a different way: B-drop
   drops the neighbours (price: cut-free contacts, a tall fin, set in every
   waiting conductor); B-lift lifts *k* 8.7–14.7 mm (price: a 30–35 mm split and
   squaring); B-fin lifts *k* 3.5 mm (price: made steel).
3. **Fanning wider than 2.5 mm to make room, then converging.** Trimming in the
   fanned pose leaves J1's outer conductors 1.2–4.4 mm long at 4–6 mm pitch, a
   4–7 mm bow at the housing [calc selector_and_bow §2]. It works only if the
   trim is made in the converged pose.
4. **The tip wanders after the trim**, 0.2–1 mm under a light touch at 8–10 mm
   stick-out [calc selector_and_bow §4]. The fork closes near the tip at the
   moment of use, so the free tip's position is never relied on.
5. **Moving a cassette between benches loses position**, but only to within the
   lead-in: each bench re-locates on its own pins. The carrier, not the crimped
   wire, is what gets re-located (the Cellios lesson [prior-art §0], turned
   round).
6. **The ribbon slips in the clamp when a slug or a proof pull pulls.** The
   clamp's hard stop sets a 15–30 % squeeze over 10–20 mm (above). A light clamp
   fails good crimps by letting the copper creep; it does not pass bad ones.
7. **The empty cavity.** A software skip alone can be wrong. The printed blank in
   key 3 makes a J2 cassette unable to hold six conductors, and the test header
   checks cavity 3 is open.

## Contribution

- The cassette turns "place the contact on the end of the cable" into "place the
  contact under a conductor whose position the cassette already knows". The
  person's dexterity is spent once per housing, at loading, not per crimp.
- The cassette is the interface that lets a crimp-only machine exist before
  anything else, and lets every later machine plug in without changing the ones
  before it.
- Loading is where the cassette absorbs what machines should never reason about:
  the crossings, the blank, which ribbon is which.

## Major unresolved problems

- **Silicone stripping at bench A** by V-jaw and pull is untested [xh-facts §7].
  p7's whole-end strip, a rotary head, or laser scoring are alternatives; the
  cassette does not care which it visits.
- **Web peel by hand** stays a person step until p1b's splitter (repo Open item
  5).
- **B-drop's axial window**: ±0.23–0.33 mm RSS against ±0.3 mm, most of it the
  unmeasured strip-length scatter.
- **B-drop's fin and cut-free supply**: a 1.45/1.88 mm stepped fin 9–10 mm tall
  made and hardened without cracking, and a contact supply that reaches it from
  above or the front without crossing the dropped row.
- **Set in waiting conductors (B-drop)**: a 25–30 mm split, or capture from below
  at every key.
- **Gang insertion needs all fronts on one line ±0.3 mm and parallel**
  [into-the-housing]. Plausible because every tip came from one trim line;
  untested.
- **Ten cassette kinds or one universal**: a universal 9-key cassette with
  removable blanks is one print; per-loom cassettes make mistakes harder.

## What rests on assumptions

- The ~7 mm drop, and a hardened stepped fin that survives being made.
- The set tables: strand yield 60–120 MPa and silicone 2–6 MPa [calc wave2 §1].
- The 0.64 mm pins squeeze the silicone rather than jam.
- Minutes per unit are estimates; the ledger books 45 minutes for all twelve
  harnesses [repo labor.md], so compare rows, not absolutes.
- Redo counts depend on the loom's length tolerance, which Derek has not stated.

## Loose kit contacts in this arrangement

The CQRobot contacts are loose [repo bom.md]. Every form of bench B takes a
contact already cut free, so loose kit contacts and strip stubs are the same
problem: one oriented contact to the fin or the tool.
- **B-lift and B-fin:** posts loaded by hand in key order at leisure
  (terminal-supply a4, x1): p1c's revolver, p1d's two-tier post bar.
- **B-drop:** a1's neck blade holds a loose contact on the fin, fed from
  hand-tool-as-press a2b's revolver, or a strip stub on a pin in its pilot hole.
- A small vibratory bowl or a rotating-scoop singulator [prior-art §3].
- The person dropping one contact per crimp, which puts the person back in the
  loop per conductor.

Related in other explorers: ribbon-as-pallet (a pallet that tours stations;
a6's far-end pogo block), terminal-supply (posts and strip locators),
into-the-housing (gang insertion, crossings).
