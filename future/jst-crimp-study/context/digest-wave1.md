# Digest of wave 1

The coordinator's cross-reading of the nine explorers' first pass, the facts
pass ([`xh-facts.md`](xh-facts.md)) and the prior-art pass
([`prior-art.md`](prior-art.md)). It has four parts:

- findings several explorers reached, and numbers everyone can use without
  re-deriving them;
- convergences between views;
- disagreements;
- the parts of the problem that have had the least thought.

Each explorer's full account is its `summary.md`.

## Numbers the whole study can stand on

**The crimp**
- **Force.**
  - Peak die force is about 0.8–2.6 kN; design for 3 kN.
  - The force is needed only in the last 0.1–0.2 mm of the stroke. Through
    the ~0.7 mm of wing curl before that it is tens to a few hundred newtons.
  - Energy is about 0.13–0.48 J per crimp. [calc: `context/calc`,
    `force-and-form/calc/stroke_model`]
  - A slow stroke is benign: copper's flow stress is 5–8 % *lower* at crawl
    speed, and there is no inertia at the bottom. [force-and-form, source cited]
- **Drive is not the hard part.** Each of these delivers the crimp:
  - a NEMA 17 through a 30:1 worm on a 2.5 mm eccentric;
  - a 15 mm crank at under 4 N·m;
  - a knee (toggle) pushed with 60–160 N;
  - a NEMA 17 on a Tr8×2 screw at a hand tool's grip (~280 N).

  Applicator return springs, not the crimp, set motor size on a crank press.
- **Precision is the bottom-of-stroke position, ±0.02–0.05 mm.** Every
  explorer that looked found the same answer: set height by geometry, not by
  the actuator. The options are:
  - dies that bottom on each other;
  - a hard stop in a short steel loop;
  - crank bottom dead centre (1° off is 3–4 µm);
  - a knee at straight.

  Then any springy, printed or hand-pumped frame and drive only costs travel.
- **Printed parts cannot be die faces.** A wing tip on a printed face sees
  thousands of MPa. They can be:
  - cradles and combs;
  - funnels and forks;
  - tracks and covers;
  - coarse locators.
- **Placement windows at first die touch.**
  - Contact axial ±0.1 mm (bellmouth is about one stock thickness).
  - Contact lateral ±0.15–0.3 mm.
  - Conductor axial ±0.2–0.3 mm.
  - Roll 5–11°.

**Quality**
- **Crimp height** is licence-gated at JST.
  - Estimate for SXH-001T-P0.6 on this ribbon: ~0.88 mm (0.69–1.12).
  - A clone spec (KONNRA) quotes 0.73 ±0.05 mm conductor height and 1.80 mm
    insulation height at 22 AWG.
- **Pull-out minimum** at 22 AWG: 39.2 N (JST) and 35.6 N (UL 486A).
- **Force monitoring** sees gross faults only:
  - It catches a missing conductor, insulation in the barrel, and a missing,
    high or rolled contact.
  - One strand of 60 is ~1.7 % of force, and a monitor's band is ±4 %.
  - The backlit picture of the stripped tip, before it disappears into the
    barrel, is the strand guard.
- **A genuine factory crimp to measure** exists for $0.90: JST ASXHSXH22K305,
  a 22 AWG socket-to-socket lead. [change-the-question]

**The contact**
- **Genuine SXH-001T-P0.6 is plentiful and cheap.**
  - Digi-Key: ~1.3 M on reels, $0.047 each in 100-piece strips.
  - LCSC: $0.013.
  - Clone reels exist (CJT A2501-TP, $0.008).
  - A 100-piece strip covers ~1.9 units, and an 8,000 reel ~150.
- **Strip geometry.** The carrier is side-feed:
  - It joins at the rear of the insulation barrel, in the contact's floor
    plane.
  - Ø1.5 mm round pilot holes sit on each contact's centreline, under the
    wire's path.
  - Rectangular slots lie between the holes.
  - Pitch is ~7.1 mm (Würth's public drawing of the analog part; JST's figure
    is unpublished).
  - A tab is sheared by dropping the carrier away from the wire.
- **Open contacts collide at 2.5 mm pitch.** Clone insulation wings open
  2.46–3.0 mm wide.
  - Crimping needs the neighbours out of plane, or a wider crimp pitch.
  - About 3.4 mm fits every contact type, and 4–6 mm fits common die widths.
  - Close to 2.5 mm only for insertion.
- **Strip length disagreement.** JST's WC-110 specification says 2.4 mm; the
  KONNRA clone spec says 1.6–2.1 mm.

**The wire**
- **Ribbon construction.** Each conductor is 60 × 0.08 mm tinned strands, and
  the ribbon holds 1.7 ±0.1 mm per conductor.
- **Copper sets the shape.** The strands yield below a ~67 mm bend radius, so
  fans and lay-in bends hold their shape and must be undone deliberately.
- **Buckling.** A free conductor buckles at ~6 N over 5 mm and ~40 N over 2 mm.
  An insertion push must come from within ~2 mm of the insulation barrel, or
  through a guide.
- **Silicone** has a tensile strength of 8–11 MPa and a tear strength of
  15–25 N/mm, and it does not melt. Two stripping approaches exploit that:
  - **Cut shallow, tear the rest.** A 0.15–0.3 mm ligament costs 3–15 N of
    pull.
  - **Score, then tear** with a laser. At 455 nm copper absorbs ~65 %, so a
    diode laser must score and never strip through. CO2 is the selective
    wavelength.
- **The H2C takes Bambu's 10 W and 40 W 455 nm laser modules** ($698 and
  $1,348 upgrade kits, in stock). [borrowed-machines]

**The looms**
- **J4 and J7 are not in ribbon order**, found independently by
  into-the-housing, procedure-is-the-machine and change-the-question.
  - J4 needs at least two or three crossings between ribbon and housing.
  - J7 needs one or two. It becomes straight if GND rides the 3P with CLO and
    CHI and the 5P's fifth conductor is the trimmed one. That is a wiring
    choice for Derek, labelled as such.
- **One end type dominates.** 4P into XHP-4 (J3, J5, J9, J11, J13) is 5 of 10
  housings and 38 % of crimps, with no pair, skip or crossing.
- **Recovery.** A single conductor cannot be re-crimped: a whole ribbon end is
  cut back ~6 mm. Terminating the XH end before the far end, or at the spool
  before cutting, keeps a bad crimp from scrapping a loom.

**Person time**
- **Loading is the cost, not crimping.** In every arrangement where it was
  estimated, the person's time is dominated by loading ribbon ends into
  fixtures: about 10–30 min per unit. Machine time, from ~20 min to ~6 h per
  unit, is irrelevant against a week of printing. What matters is how often
  the machine calls the person back.

## Convergences between views

Several ideas were reached independently from different directions.

- **Terminate at the spool, cut last.** ribbon-as-pallet a4,
  procedure-is-the-machine p3/p3b and change-the-question c5. The cut that
  frees one loom squares the next end. The rest of the spool, with a slip ring
  on its inner end, becomes a test lead.
- **The force stays inside a travelling head, so any light gantry positions
  it.** hand-tool-as-press a3, force-and-form f4 and borrowed-machines b3.
- **The housing itself as the crimp locator.** terminal-supply a5 and
  into-the-housing i2 and i2c.
- **Holding a loose contact by mating it onto a 0.64 mm header post.**
  hand-tool-as-press a3 (post column) and terminal-supply a4 and a4b.
- **The carrier strip as a precision pallet, handle and datum.**
  terminal-supply a2 and a2b, ribbon-as-pallet a2, force-and-form f3 and f5,
  and borrowed-machines b2 and b3.
- **A slow crank or eccentric press around a bought mini-applicator.**
  - terminal-supply a1;
  - force-and-form f2;
  - borrowed-machines b1 and b1b;
  - hand-tool-as-press a4 (SN jaws in a die set);
  - procedure-is-the-machine p5 (camshaft).
- **The far end as an electrode array.**
  - hand-tool-as-press: a terminal block, so each conductor becomes a touch
    sensor and identity check;
  - ribbon-as-pallet a6: pogo pins on the cut face;
  - procedure-is-the-machine p3: the slip ring through the spool.
- **A cassette or pallet as the one travelling datum**, with each station
  locating it on its own pins. ribbon-as-pallet a1, procedure-is-the-machine
  p1 and borrowed-machines' cassette.
- **Every crimp of a ribbon end in one stroke of the idle 12-ton press**, with
  stop blocks setting height. force-and-form f5 and ribbon-as-pallet a2b.
- **Neighbours out of plane.** Folded back 180° in borrowed-machines, dropped
  by a slotted presser in procedure-is-the-machine, lifted in
  change-the-question, and lifted by a comb and fork in hand-tool-as-press.
- **A real XH header as nest and tester.** into-the-housing i5 and
  change-the-question's real-wafer test. JST's handling precautions say to
  check continuity only against the applicable header.
- **Existence proofs from industry.**
  - JCW-2TE clamps a pre-split ribbon, steps it by conductor pitch and uses a
    wire fork over a pre-fed side-feed contact.
  - Kurabo's robot plays the operator of an unmodified crimp press.
  - Sogang's printed, servo-driven inserter puts ribbon contacts into
    2.5 mm housings; lean-and-slide succeeded 18/20 against 3/20 for a
    straight push.
  - No maker build automating JST or Dupont crimping was found.

## Disagreements and open tensions

- **What sets crimp height in a motorised hand tool.** It depends on whether
  the SN-2549's jaws bottom face to face. If they do, the dies set it; if not,
  the cradle's stiffness does. Unknown until Derek holds the closed tool to a
  light.
- **Printed frames.**
  - force-and-form: fine if the height-setting stop sits in a short steel loop.
  - Others: frames creep and drift with temperature.

  Both can be true. The difference is where the stop sits.
- **Gang crimping pitch.**
  - force-and-form: stations need at least ~3.8–4.7 mm pitch.
  - change-the-question: half-rows at 3.4 mm work if each carrier lifts 3–4 mm
    into a punch.

  These are different die geometries, not a contradiction.
- **Split length behind the housing.** Arrangements want anywhere from ~8 mm
  (fold-back parking) to 25–48 mm (fanning to carrier pitch). Nobody knows
  what length is acceptable on a finished loom. Derek's question.
- **Person-paced stations.** procedure-is-the-machine p4 argues a station that
  waits on the person saves no minutes and buys only consistency and a log.
  Others count consistency and a log as the point.
- **Strip length.** 2.4 mm (JST) against 1.6–2.1 mm (clone spec). It matters
  for every stripper and wire stop.
- **Arms.**
  - An SO-101 carries cassettes between docks only; its tip wanders about
    ±2–6 mm.
  - A Dobot MG400 (±0.05 mm, $2,900–3,500) can present conductors to an
    unmodified press, as Kurabo does.

## The least-developed parts of the problem

These have the least thought so far. Wave 2's new directions can go here.

- **Stripping soft silicone at 22 AWG** as a station in its own right. Options
  appear as modules (ribbon-as-pallet a5, borrowed-machines b4 laser score),
  but none is developed as deeply as the crimp ideas:
  - blade with a ligament and tear;
  - V-blades;
  - a hollow rotary spindle;
  - pinch-and-pull;
  - diode score on the H2C;
  - borrowed automatic strippers;
  - a twist to gather strands.
- **Parting the web in practice**, including the untested peel (repo Open
  item 5). Options:
  - valley-riding blades;
  - an under-width channel (AMP US 4,230,008);
  - interlaced toothed jaws (US 4,179,964);
  - laser slitting.
- **The insulation crimp on soft silicone.** What the insulation barrel does
  to a 0.49 mm silicone wall. Whether it grips or cuts, and how that shows in
  a picture or a pull.
- **Loose kit contacts in any automated path**, against switching to strip.
  Several arrangements assume strip; the kit contacts are what is on hand.
- **Crossings and pairs in automated insertion** (J4, J7, and the four
  two-ribbon housings). Most insertion ideas hand crossings back to the person.
- **The control and software stack.** What runs the motors and cameras:
  - Klipper, FluidNC or an ESP32;
  - Python on the Mac;
  - the ask queue;
  - the log.

  How a session with Claude supervises it, and what the first day of running
  looks like.
- **An incremental path from today's bench.** Which first build is useful on
  its own the week it is made, and how it grows. procedure-is-the-machine p1
  starts on this.
- **Manual jigs with no motors** that make today's hand procedure precise:
  ribbon-as-pallet a2d, into-the-housing i5, terminal-supply a2c's strip clip.
  They are few, and they are cheap first steps.

## Measurements that would settle many things at once

Explorers asked for overlapping measurements. The shortest list that answers
most of them:

1. **One 100-piece SXH-001T-P0.6 strip** (Digi-Key 455-1135-100-ND, $4.71),
   under a caliper or the Revopoint. It settles:
   - carrier pitch;
   - pilot hole;
   - tab length;
   - the neck between barrel and box;
   - genuine open-wing width.
2. **One kit contact** under the caliper and the ELP camera: open-wing width,
   box size, lance position, and which face goes toward the housing windows.
3. **Five crimps with the SN-2549 on the ribbon**, which settle:
   - crimp height by caliper;
   - handle force by bathroom or luggage scale;
   - whether the jaws bottom face to face;
   - pull-out with a hook and scale.
4. **The web.** Peel a metre each of 3P and 5P, and put a fresh cross-section
   under the camera.
5. **One contact into one kit housing:** where it first resists, the push at
   the click, the tug that pulls a latched contact out, and how far inside the
   rear face it seats.
6. **Five JST ASXHSXH22K305 leads** ($4.50) as genuine reference crimps.
