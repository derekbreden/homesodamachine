# p6 The spool-end bench that grows

Sketch: [`../sketches/p6-spool-end-bench.svg`](../sketches/p6-spool-end-bench.svg)
(schematic plan of stage 0, and the stages). Numbers:
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) §2 and §6 (cited as
[calc wave2 §n]), [`../calc/wave3.out.txt`](../calc/wave3.out.txt) (cited as
[calc wave3 §n]), the first calc files as [calc name §n].

Today's hand procedure, moved to the spool. The XH end is made by hand on the
free end of the ribbon while it is still on its reel. It is tested pin to pin
through the rest of the reel, then drawn off to the loom's length and cut, and
that cut squares the next end. The first build has no motor. It is useful the
week it is printed, because it changes what a bad crimp costs and when the pin
order is checked.

Motors then join one step at a time at the same clamp, in the order Derek wants
the work taken off his hands: the crimp first [Derek: "placing the metal bit on
the end of the cable, placing that metal bit and cable in something that crimps
and crimping it … I desire most to automate"]. Each stage keeps the previous
stage's parts and carries the interface the next motor takes over: a
knob-turned lead screw at stage 1 gets a stepper at stage 2; a peg the person
draws the housing to at stage 0 becomes a belt-driven puller at stage 4. The
order of work (terminate first, cut last) never changes; only who does each
step changes.

It grows toward [p3](p3-terminate-at-the-spool-cut-last.md) (with a puller where
p3 has a drop tube), change-the-question
[c5](../../change-the-question/ideas/c5-ends-as-stock.md) (ends as stock) and
ribbon-as-pallet [a4](../../ribbon-as-pallet/ideas/a4-spool-as-magazine.md) (the
spool as magazine). [p6b](p6b-reel-end-docks-on-a-strip.md) is the branch where
the reel's end docks onto a contact strip and a bought applicator crimps it.

## Picture it: stage 0, making J11 and then J1's 4P half

**Where things start.**
- **Three reels** stand on axles at the back of the bench: 5P, 4P and 3P.
  - Each is the BNTECHGO spool as bought, if its inner end can be reached.
  - Otherwise it is rewound once onto a printed reel through a printed roller
    straightener, the inner end brought out through a slot in the hub. The
    reel's hub radius is 80 mm, so the rewound ribbon takes no new set [calc
    wave2 §2]; off a 25 mm hub, a 40 mm free end rises 3–15 mm.
  - The inner end is hand-crimped into an XH housing that plugs into a small
    board in the hub: the **hub socket**.
- **The clamp** at the bench's front edge is a printed channel 0.2 mm under the
  ribbon's width, the marked edge against the wall (ribbon-as-pallet's
  registration, after AMP US 4,230,008), with a TPU pad on a cam lever. A slot at
  the clamp face guides the KATA flush cutters: **the cut line belongs to the
  clamp.**
- **The test board** is an ESP32 with real XH headers (B4B, B5B, B6B, B7B and
  B9B-XH-A on one small board; into-the-housing's i5 and change-the-question's
  real-wafer test) and an LED beside each post. The CQRobot kits include B*B-XH-A
  headers [Prime: CQRobot JST XH kit]. A flying lead reaches any hub socket.
- **The length rail** runs along the bench front: an aluminium extrusion with a
  printed peg at each loom's length from the clamp face (J5 ~100 mm to J11
  ~600 mm).
- **The partner nest** beside the clamp holds a half-housed pair end.

**One end: J11, 4P into an XHP-4, ~600 mm.**
1. The 4P end already sticks out of the clamp, square, because the previous
   loom's cut made it so. On a new reel the person cuts at the clamp face.
2. The person makes the XH end as today: peel, splay, strip with the Klein, crimp
   with the SN-2549, insert. The clamp holds the loom, so both hands are free.
   Any hand station works here unchanged: hand-tool-as-press
   [a6](../../hand-tool-as-press/ideas/a6-foot-closed-jig-bench.md)'s
   foot-closed jig, terminal-supply
   [x1](../../terminal-supply/ideas/x1-post-feeds-the-hand-tool.md)'s post pen,
   terminal-supply [a2c](../../terminal-supply/ideas/a2c-strip-locator-for-hand-tool.md)'s
   strip clip, or [p7](p7-strip-before-split.md)'s lever for a whole-end strip.
3. **Test.** The person plugs the housing onto the B4B header and the flying lead
   into the 4P reel's hub socket. The ESP32 drives each inner-end conductor in
   turn and reads every post: one conductor to one post, in pin order, nothing
   else touching. About 0.1–0.9 Ω of reel is in series, which is irrelevant to an
   open-or-closed reading [calc spool_test §1].
   - Green: pin order, no opens, no adjacent shorts; for J2, cavity 3 open.
   - Red names the pin. The person cuts the end back ~6 mm at the clamp face and
     makes it again. The loom does not exist yet, so no loom is ever short.
4. **Draw and cut.** The person unplugs the flying lead, opens the clamp, and
   draws the ribbon out along the rail by holding it just behind the housing,
   not by the housing, so the reel's drag never passes through a crimp. The
   housing goes to J11's peg. The person closes the clamp and cuts at the face.
   J11 is free, and the end in the clamp is square for the next loom.
5. The far end (Faston, ferrule, IDC) is made later, as today, after the XH end
   has passed.

**J1's 4P half** goes into cavities 6–9 of an XHP-9. The test checks posts 6–9
and that posts 1–5 read open. It is drawn to J1's peg, cut, and waits. When the
5P reel's turn comes, the person clips the half-housed J1 into the partner nest
and makes the 5P end into cavities 1–5; the test checks the 5P conductors on
posts 1–5 and that posts 6–9 read open from all of them. The person draws the
housing, with the 4P loom hanging from it, to the same peg and cuts the 5P. The
pair is equal length to the peg's ±1–2 mm [calc wave2 §6].

**Crossings and skips.** J4: the person lays the 3P's GND into cavity 2 by hand,
and the test through the 3P reel confirms it reached post 2 before the 3P is
cut. J7 the same through the 5P reel. J2: the test confirms cavity 3 open. A
crossing laid wrong is found while the ribbon is still on the reel, when fixing
it costs 6 mm of reel.

**What stage 0 buys, with no motor.**
- **A redo costs reel, never a loom.** No loom carries a length reserve. At a
  10 % bad-crimp rate that is ~43 mm of reel a unit; a cut-first order with a
  12 mm reserve scraps ~35 looms over the program [calc recovery_length §3–4].
- **Pin order, opens and adjacent shorts before the loom exists.** The far end
  needs no stripping, terminal block or pogo block per loom. One inner-end
  connection serves a whole reel, 5–11 units of looms.
- **Pair lengths set by one peg.** **Both hands free**, and a square end every
  time.

**What it costs.** About 5 attended minutes a unit more than today on the same
task library (51 against 46): the per-end test, spool changes with a rewind once
per spool, and pairing at the partner nest [calc wave2 §6; estimates]. Parts: an
ESP32, a header board, an extrusion, magnets and prints, about $25–45
[estimate].

## The stages

| Stage | What joins | Machine does | Person does | Person min/unit | Longest alone | Added cost |
|---|---|---|---|---:|---:|---:|
| 0 | reels, clamp, test board, rail, partner nest | tests each end through its reel | everything by hand at the clamp; draw and cut | 51 | — | $25–45 |
| 1 | crimp module at the clamp, knob-turned slides, lift lever | hold, crimp, force curve, identity before each crimp | split, strip, index and lift, place each contact, turn Y to the light, pedal; insert | 61 | — | +$100–170 |
| 2 | steppers on the same screws, lift servo, post revolver or post bar | walks the row: index, lift, place contact, feed to depth, crimp, pull | split and strip the end; load the posts in loom order; insert | 40 | one end, ~11 min | +$90–140 |
| 3 | strip head on the tool carriage (or p7 at the clamp) | strips each conductor in the lifted pose | split; load the posts; insert | 33 | ~16 min | +$20–60 |
| 4 | belt puller on the rail, encoder, guillotine, slip ring, housing tube | draws off, cuts, gang-inserts single-ribbon ends | split; posts; pairs at the partner nest; J4 and J7 | 24 | ~18 min | +$120–200 |
| 5 | split station at the clamp | the whole single-ribbon end, reel after reel | posts, housing tubes, reels; pairs; J4 and J7 | 15 | 4P reel ~5 h | +$20–60 |

All minutes are [estimate] from one task library [calc wave2 §6]; today by the
same library is ~46. Compare rows with each other, not with the ledger. Costs
count only what the bench does not already have [estimate].

### Stage 1: the crimp, Derek's priority step, is the first motor

**The clamp gets two slides and a lift.** The clamp rides an **X slide**, a lead
screw turned by a knob with a printed detent wheel at one 2.5 mm step per click.
A comb of 0.64 mm pins at 2.5 mm pitch stands on its front face, and the person
fans the split conductors into it. Under the station line sits a **lift lever**,
a finger that raises whichever conductor is over it.

**The crimp module stands in two forms.** Both crimp upright, lance down, the
way the housing wants it.

- **Stage 1-SN.** A dedicated SN-2549 [Prime: iCrimp SN-2549, $22.29] lies **on
  its side** in a printed, insulating cradle on a **Y slide** (another
  knob-turned lead screw along the wire axis): long axis across the ribbon, jaws
  closing vertically, anvil half underneath. A NEMA 17 on a Tr8×2 screw [Prime:
  NEMA 17 with integrated T8×2 lead screw, $27.99] bolted to its lower handle
  pushes the upper handle through a load cell (hand-tool-as-press a3's module).
  a1's sprung 0.3 mm flap blade sits in the contact's neck and is wired to the
  ESP32.
  - The lift is *a* + 2.7 mm, *a* being the anvil jaw half's depth below the
    nest, 6–12 mm [assumption]: 8.7–14.7 mm. That wants a **30–35 mm split**
    and a squaring push after each crimp [calc wave3 §1].
  - On a reel, the same geometry can be had with the tool hung tip-down if the
    reel lies flat on a vertical axle and the clamp holds the ribbon on edge
    (hand-tool-as-press a3's on-edge fixture).
- **Stage 1-fin.** [p1d](p1d-lift-once-fin-from-below.md)'s station at the
  clamp: a small steel C whose knee drives a narrow stepped crimper, and a fin
  rising from below through the lifted conductor's empty slot. The lift is
  3.5 mm and a 20–25 mm split leaves essentially no set [calc wave3 §1]. The
  price is made steel (force-and-form
  [f7](../../force-and-form/ideas/f7-where-the-steel-comes-from.md)).

**Per conductor *k*, stage 1-SN.**
1. The person clicks the X knob to *k*, pulls the lift lever, and puts a contact
   into the open nest with x1's post pen (or a strip stub on a2c's pin).
2. A button closes the pusher **until the upper jaw's flare touches the wing
   tips**, found as the first few newtons on the load cell. The contact is
   located, its wings still open; the first ratchet tooth would pinch the
   insulation bore to 1.4–1.6 mm [force-and-form calc wave2 §1].
3. The person turns the Y knob, sliding the contact onto *k*, until the LED for
   *k* lights: the strand tips have touched the flap blade, and the ESP32 reads
   continuity from the blade to inner-end conductor *k* and to no other. Depth
   and identity come from the same touch. If a different conductor lights, the
   crimp is refused: a crossing laid wrong, or the wrong key.
4. The pedal [Prime: TEMCo CN0002 foot switch, $13.76]: the pusher completes the
   ratchet cycle and the force curve is logged against the reel, the loom and
   the pin.
5. The pusher opens to the blade, and the person backs the Y knob 0.5 mm against
   a 20 N spring stop: a proof pull through the box, never through the dies. The
   whole reel anchors the copper, so the pull tests only the crimp.
6. The person releases the lever and pushes the crimp back into the comb's line.

**What stage 1 adds and costs.** About 10 minutes a unit against stage 0,
because the person turns knobs and waits on each crimp [calc wave2 §6]. p4's
accounting holds: a person-paced powered crimp buys consistency, a curve and an
identity check, not minutes.

**Stages 0 and 1 are the qualification rig.** At the reel clamp every sample
crimp gets identity, open and short through the hub socket, a proof pull
reacted by the whole reel, a bend-and-look, and costs 6 mm of reel if bad. That
is where force-and-form's insulation-window sweep
([f6](../../force-and-form/ideas/f6-two-blades-two-drives.md)) and its
comparison of four steel sources (f7) can run on the real ribbon, judged against
the JST ASXHSXH22K305 factory lead ($0.90 [digest]) with Derek watching. Stage 1
is also where the module's unknowns are measured: *a*, the wing-touch position,
the handle force curve and whether the jaws bottom, the neck length *n* for the
blade, and what a 20 N pull does.

### Stage 2: motors on the same screws, and the person stops touching contacts

- Steppers go onto the X and Y lead screws, and a servo onto the lift lever
  [Prime: DS3218MG, $14.99]. A BTT SKR Pico [Prime: $35.99] runs them from the
  Mac or an ESP32.
- **Contacts on posts.** For 1-SN, a printed revolver on the clamp's X slide
  carries 12 posts cut from 0.64 mm header pins [Prime: 2.54 mm male pin
  headers, $7.99], parallel to the wire axis on a 20 mm radius, loaded box-first
  in loom order at leisure (terminal-supply a4); the module picks from it as in
  [p1c](p1c-lift-once-tip-down-module.md), closing only to wing touch. For
  1-fin, p1d's two-tier post bar rides the X slide and slides each contact onto
  its conductor before the fin rises.
- **Depth from the camera, identity from copper that is touched anyway.** The ELP
  camera reads each conductor's bare length on a backlight and Y corrects to it
  (±0.07–0.09 mm RSS [calc wave2 §3]). Identity then comes from the tool at the
  end of the wing curl (1-SN: the insulated SN; 1-fin: the C), not from the
  blade: with camera depth, the tips must stop short of the blade, which needs
  a neck of 0.70–0.90 mm [force-and-form calc exchange_procedure_w3 §5]. If the
  kit contact's neck is shorter, 1-SN keeps stage 1's touch-off depth.
- **Person per end:** split, strip each conductor by hand with the lift lever,
  load the posts, press go. The machine runs the end alone, J1's nine conductors
  in ~11 minutes [estimate]. The person inserts, tests, draws and cuts: ~14 calls
  a unit.

### Stages 3–5, briefly

- **Stage 3: strip in the pose.** A strip head goes on the tool's Y carriage
  (the Klein 11063W in a second squeezer, hand-tool-as-press a2c;
  ribbon-as-pallet's [a8b](../../ribbon-as-pallet/ideas/a8b-spindle-with-touch-off.md)
  spindle; or V-jaws with a pull). With a grounded trim blade beside it, identity
  is read at the trim. The alternative is [p7](p7-strip-before-split.md): one
  stroke across the whole webbed end at the clamp face, before the split.
- **Stage 4: the draw-off is powered, and pulled rather than pushed.** The stage-0
  rail gets a GT2 belt and a small carriage, the **puller**, which clips the
  ribbon just behind the housing and draws the loom out to its length, read by
  an encoder wheel (±3–6 mm on 600 mm at 0.5–1 % slip [calc spool_test §4]). A
  fold of the ribbon round a bar in the clip multiplies a 3 N clip to 14–69 N
  (ribbon-as-pallet a3's fold [borrowed-machines calc
  exchange_ribbon_as_pallet §8]). The clamp closes, and a guillotine at the clamp face
  cuts (40–65 N per conductor with an angled blade [calc spool_test §3]). A
  6-circuit slip ring on each reel axle [Prime: 12.5 mm capsule slip ring,
  6 × 2 A, $9.99] replaces the flying lead, because the reel turns under
  power between tests. Single-ribbon housings drop from a tube into a nest in
  front of the comb and slide onto all contacts at once, after the crimps are
  squared into the row. The four pair housings still go half-housed to the
  partner nest.
- **Stage 5: split at the clamp.** A razor comb in the valleys (p1b) or
  ribbon-as-pallet's [a7](../../ribbon-as-pallet/ideas/a7-zip-station.md) zip
  station, its tear stopped at the clamp face; after p7's slug is gone, the zip
  starts from the gap it left. A reel of single-ribbon looms then runs alone:
  the 4P reel makes five units of J3, J5, J9, J11, J13 and the 4P halves of J1
  and J4 in ~5 hours [calc wave2 §6]. This is p3, with the puller.

### What each stage measures for the next

| Stage | Settles |
|---|---|
| 0 | whether the web peels cleanly (repo Open item 5); curl off the reel; strip length on this ribbon (2.4 mm JST vs 1.6–2.1 mm clone spec) against pulled crimps; the kit contacts' fit; whether per-end testing catches what the final test caught |
| 1 | *a*, wing touch, grip force curve, jaw bottoming; the neck *n*; the 20 N pull; identity through the reel at every crimp; the steel sources and the insulation window, against the JST reference lead |
| 2 | post grip and pick repeatability; camera bare length on black silicone; how often the machine calls |
| 3 | stripping silicone in the pose: tear raggedness, nicks seen on the backlit tip |
| 4 | puller and guillotine on silicone; gang insertion with squared fronts |
| 5 | machine splitting on this web |

## What locates what

| Moment | Located | Against |
|---|---|---|
| Every stage | ribbon end | channel wall and floor of the clamp (fixed to the bench) |
| Cut | tips | clamp-face cut guide |
| Test | conductor identity | inner end through the hub socket |
| Stage 1–3 crimp | conductor *k* laterally | comb pin slot, then the lifted pose |
| Stage 1–3 crimp | contact | 1-SN: anvil nest and flap blade; 1-fin: post, then the crimper's flare over the fin |
| Stage 1 depth | insulation edge | touch-off of strands on the blade (±0.22 mm RSS with the strip scatter) |
| Stage 2+ depth | insulation edge | camera bare length, Y corrected (±0.07–0.09 mm RSS) |
| Crimp height | dies | 1-SN: the SN-2549's own jaws; 1-fin: the knee at straight and the gate wedge, in the steel C |
| Length | loom | peg (stages 0–3, ±1–2 mm) or puller and encoder (stage 4+) |

"Fixed" is the bench under the clamp; the reels, the rail and the test board are
all referenced to the clamp face.

## What drives the crimp and carries its force

Stage 0: Derek's hand on the SN-2549. Stage 1-SN on: a NEMA 17 Tr8×2 pushing the
SN's handle, the loop closed inside the tool; the slides and the clamp carry
positioning loads only. Stage 1-fin on: a NEMA 17 Tr8×2 pushing a knee inside a
steel C, the loop closed inside the C.

## How it knows it worked

Pin order, opens and shorts through the reel before every cut (all stages);
from stage 1, identity before every crimp, a force curve, a proof pull reacted
by the reel; from stage 2, the backlit bare length and brush; with 1-fin, a
re-touched crimp height on every crimp.

## Printed and bought

- **Printed:** reels with an 80 mm hub radius and hub-socket pockets; the roller
  straightener body; the channel clamp and cut guide, pegs, partner nest; at
  stage 1, the tool cradle or the C's base, comb block, lift lever, detent wheels
  and knobs; at stage 2, the revolver or post bar; at stage 4, the puller
  carriage and housing tube.
- **Bought** (Prime rows observed 2026-09-28, unless a source is named): an ESP32
  (requested; not yet Prime-confirmed); 2020 extrusion (requested; not yet
  confirmed); 608 bearings for the straightener; the CQRobot kit's headers, or
  B4B–B9B-XH-A (Newark 171,802 in stock for B4B, Digi-Key 44,226 for B9B
  [source: findchips via into-the-housing]); a second SN-2549 ($22.29); NEMA 17
  T8×2 ($27.99) and MGN12 rails [Prime: $20.49]; a bar load cell and HX711
  [Prime: $9.99]; the foot switch ($13.76); header pins ($7.99); the SKR Pico
  ($35.99); at stage 4 a GT2 belt and pulleys [Prime: $5.99], an encoder
  [Prime, search result only: bare 600 P/R encoder, $18.99] with a printed wheel, and slip rings
  ($9.99).

## Transfers and combinations

- **Hand stations from other views plug in at stage 0 unchanged.** a6's jig
  bench, b2b's pedal-less station and x1's post pen are built around a loom that
  has already been cut. At the reel, the far-end fixture they need (a terminal
  block, a pogo block on the cut face) is replaced by the hub socket, one
  connection per reel, and their recovery becomes reel-cost instead of loom
  length.
- **p1d at the reel** (1-fin): the whole reel reacts the proof pull, identity
  goes through the hub socket, a bad crimp costs 6 mm of reel.
- **change-the-question c5.** From stage 4 the same bench can make stock ends of
  standard length if Derek prefers bins of ends to looms made to order.
- **into-the-housing i5 / change-the-question's real-wafer test.** The test
  board is that header board, read through the reel instead of a far-end block.
- **force-and-form f6 and f7** at stages 0–1 (the qualification rig above).

## Problems, and what answers each

1. **The spool's inner end is not reachable.** A rewind, once per spool, ~5
   minutes with the HOTO screwdriver or the drill press chuck turning the
   printed reel [estimate], through the roller straightener. Without it stage 0
   loses its test; recovery at the reel, pegs and a square cut remain.
2. **Ribbon off a small hub is curled.** Off a 25 mm hub radius the residual curl
   radius is 55–240 mm, and a 40 mm free end rises 3–15 mm; off 35 mm,
   0.1–7 mm [calc wave2 §2]. The clamp holds the ribbon flat to its face, so
   curl matters only past it; the straightener or the 80 mm reel removes it. The
   BNTECHGO hub size is unrecorded.
3. **Pulling the loom off by its housing loads the crimps.** The person, and at
   stage 4 the puller, hold the ribbon just behind the housing.
4. **Stage 1 costs minutes**: 61 against 51 at stage 0 and 46 today [calc wave2
   §6]. It is built because it is the first motor on the priority step, because
   the module's unknowns are measured there with a person watching, and because
   its slides are stage 2's.
5. **Pairs need two reels at once.** Not at stages 0–4: the half-housed end waits
   in the partner nest. p3b's two lanes are the branch that makes pairs
   together.
6. **Batching by reel means finished looms ahead of units.** At stages 0–3 the
   person works a unit at a time and re-threads a different reel (~1 minute
   [estimate]). From stage 4 a reel's run makes 5–11 units of one ribbon type,
   which is Derek's batching question.

## Contribution

- **An answer to "which first build is useful the week it is made".** Stage 0 is
  the procedure Derek already does, in the order that makes recovery and testing
  free. It needs no mechanism the study has not already sized.
- **The priority step is the first motor**, and the module that stage 1 builds is
  the one stage 5 still uses; the slides, comb, clamp and test board are all
  kept.
- **One reel connection replaces a far-end fixture on every loom**, for every hand
  or machine station in the study that wants the far end as an electrode.
- **A pull-out replaces a push-out.**
- **The reel is the place to qualify steel**, because every sample is tested and
  cheap to throw away.

## Major unresolved problems

- **The inner end and the rewind:** whether it is needed, and how long it takes.
- **Stage 1's form:** 1-SN depends on *a* and asks for a 30–35 mm split and a
  squaring push each crimp; 1-fin depends on made steel.
- **Pairs travel half-housed**, and the partner nest needs the person at stages
  0–4. J4 and J7 need hands at every stage.
- **Bench space:** a ~650 mm rail along the bench front, three reels behind, the
  clamp at the edge.
- **Minutes rise at stages 0 and 1.**
- **Whether a straightener takes curl out of silicone ribbon** without marking
  the jacket or twisting the ribbon.

## What rests on assumptions

- Task times, cycle times, costs and the ~5 minute rewind [estimate].
- Strand yield 60–120 MPa and the unrecorded hub radius behind the curl numbers.
- *a* = 6–12 mm; the revolver's clearance assumes a jaw half-width of ~8 mm.
- The post grip of 0.2–1.6 N is terminal-supply's estimate.
