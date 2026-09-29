# p1d Lift once, crimp upright: a fin rises from below into a steel C

Sketch: [`../sketches/p1d-fin-from-below.svg`](../sketches/p1d-fin-from-below.svg)
(schematic; the end view's clearances are from the calc).
Numbers: [`../calc/wave3.out.txt`](../calc/wave3.out.txt) (cited as
[calc wave3 §n]); force-and-form's
[`exchange_procedure_w3.out.txt`](../../force-and-form/calc/exchange_procedure_w3.out.txt)
(cited as [calc FP §n]); [`../calc/wave2.out.txt`](../calc/wave2.out.txt) §3 for the axial chain.

**A branch of [p1c](p1c-lift-once-tip-down-module.md), and a combination with
force-and-form.** It keeps p1c's order rule: lift conductor *k* alone, once, and
do everything to it in that pose. It replaces p1c's hand tool with purpose-made
steel that only needs *k* lifted 3.5 mm and makes every crimp upright, lance
down, the way the housing wants it.

Sources:
- this view: [p1](p1-cassette-and-benches.md)'s cassette (keys = cavities,
  crossings made in the loft, blanked keys, far end in a pogo block) or
  [p6](p6-spool-end-bench-that-grows.md)'s reel clamp; p1c's lift once, camera
  bare-length correction and post-measured contact offset;
- force-and-form: the steel C with a knee
  ([f3](../../force-and-form/ideas/f3-knee-micropress.md),
  [f4](../../force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md)), the fin
  anvil from ground stock on edge and the steel routes
  ([f7](../../force-and-form/ideas/f7-where-the-steel-comes-from.md)), the narrow
  stepped crimper and the lance relief
  ([f8](../../force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md)).
  force-and-form paired the two as FP1 in its
  [reading of this view](../../../exchange/force-and-form--on--procedure-is-the-machine-w3.md);
  its own drawing is
  [`fp1-lift-once-fin-from-below.svg`](../../force-and-form/sketches/fp1-lift-once-fin-from-below.svg);
- terminal-supply [a4](../../terminal-supply/ideas/a4-post-held-contacts.md):
  contacts held box-first on 0.64 mm posts.

## Picture it: J1 in its cassette at bench B

**Where things start.**
- **The cassette** is loaded as in [p1](p1-cassette-and-benches.md): the 5P and
  4P clamped, peeled, fanned into keys 1–9 (key *k* = cavity *k*), J4/J7-style
  crossings laid in the loft by the person, J2's key 3 blanked. The raw far end
  sits in a pogo block on the cassette, so every conductor is a wire to the
  controller.
  - A **root comb** of 0.635 mm music-wire pins [Prime: Music wire, 0.025 in,
    K&S 5005, $7.24] holds the conductors 20–30 mm behind the tips.
  - A **tip comb**, a second short row of the same pins, stands **5–7 mm behind
    the tip line**, tops ~1 mm above the row axis. It holds the neighbours
    sideways right beside the fin. Nearer than ~4.7 mm it would collide with
    the fin's insulation step [calc wave3 §2].
- **A post bar** rides the cassette's X carriage, ahead of the tips.
  - It carries J1's nine contacts box-first on 0.64 mm posts cut from header
    strip [Prime: 2.54 mm male pin headers, $7.99], one post per key, in key
    order. The person fills it at leisure; it is the build list.
  - The posts stand in **two tiers**: odd keys at one Y, even keys ~8 mm
    further forward. Open contacts on one tier are then 5.0 mm apart, so their
    2.46–3.0 mm open wings never touch [xh-facts §1].
  - A kit contact and a strip stub cut to one pitch are both "a contact on a
    post" (terminal-supply a4, x1).
  - The bar is stiff along Y and deliberately soft sideways (a printed
    flexure), so the steel, not the bar, centres the contact at the crimp.

**Fixed at the station** (bench B's frame):
- the X slide that carries the cassette and its post bar;
- a **lift finger** on a servo under the station line, ~10 mm behind the
  contacts, narrow enough (≤2.5 mm) to rise in *k*'s own slot;
- a grounded **trim blade** and a **strip head** on a small Y carriage, or none
  if [p7](p7-strip-before-split.md) has stripped the end at loading;
- the **ELP camera** looking along X at the lifted height over a light pad on
  the far side [Prime: LED light pad, A5, $16.99]. Only *k* is at that height,
  so its silhouette stands alone;
- **the steel C**, fist-sized, its spine ~25–30 mm ahead of the tips so the
  post bar's two tiers fit in its throat, the throat opening toward the cassette
  so the row and the post bar index through it in X:
  - **upper arm:** a knee (two short steel links on hardened pins) pushed at the
    joint by a NEMA 17 on a Tr8×2 screw [Prime: NEMA 17 with integrated T8×2
    lead screw, $27.99] at 60–160 N; it drives a narrow stepped **crimper** on
    two ground guide pins [Prime: ground shaft, 8 or 10 mm]; a 0.001 mm
    indicator reads across crimper and lower arm [Prime: Digital indicator,
    0.001 mm, $52.99];
  - **lower arm:** entirely below the row. A **fin** slides vertically in a
    slot in it. When the fin is up, a ground **gate block** slides under the
    fin's foot on a servo. The gate block is a shallow wedge, so its position
    is the crimp-height dial (f3's wedge);
  - the C stands on a printed base that insulates it from the bench, so the C
    itself is an electrode read through the far-end pogo block.

**One key, *k*, ~55–76 s** [calc wave3 §6]:
1. **Index.** X brings key *k* to the station line. The fin is down, its top
   ~1 mm below the row's underside; the crimper is up.
2. **Lift.** The finger raises *k* by **3.5 mm**. The neighbours stay in the
   row, held sideways by the tip comb. While lifted, *k*'s tip pulls back
   0.33–0.55 mm at 20–30 mm free [calc wave3 §1], once, before anything is
   measured.
3. **Trim.** The grounded trim blade squares *k*'s tip in this pose. It cuts
   copper, so the far end reads which conductor it is, and that no other
   conductor reads: **identity where copper is touched anyway.**
4. **Strip** in the pose, or already done by p7.
5. **Look.** The backlit side silhouette gives the bare length (where the
   insulation edge actually is) and whether the 60-strand brush is whole.
   Force monitoring cannot see one strand in 60 [digest]; this picture is the
   strand guard.
6. **Place.** The post bar's Y slide (an MGN9 [Prime: MGN9 rail, $16.12] and a
   small stepper) carries contact *k* −Y onto *k*'s stripped end, barrels
   fully open: 0.72 mm of strands into a 1.68–1.90 mm U, and the 1.7 mm jacket
   into 2.46–3.0 mm wings [xh-facts §1]. Nothing pinches the bore. It stops
   where the measured insulation edge lands mid-window, using that contact's
   box-to-barrel offset measured on its post by the camera. The other contacts
   on the bar ride 2+ mm over their own unlifted conductors [calc FP §1a].
7. **Fin up.** The fin rises ~4.8 mm through *k*'s empty slot [calc wave3 §2]
   and the gate block slides under its foot. The fin meets the contact's floor
   under the barrels and stops behind the lance (the box overhangs its front
   edge). If the strands already rest on the barrel floor, the C reads *k*
   through the contact now.
8. **Crimp.** The knee drives the crimper down.
   - At the end of the wing curl (~150–450 N, before compaction) the drive
     pauses. The wing tips are on the strands, so the C reads *k* through the
     contact: identity a second time, before any copper is formed.
   - Then the knee goes to straight. The bottom is geometry: 0.2 mm short of
     straight is 1–3 µm on 15–30 mm links [calc wave3 §3].
9. **Height.** The knee backs off and re-touches at ~10 N; the indicator reads
   the unloaded crimp height (f3). If the height is off target, the gate wedge
   moves and a second hit chases it [force-and-form calc wave2 §10].
10. **Clear.** The knee opens, the gate block slides out, the fin drops, clearing
    the lance's 0.6–0.9 mm by several millimetres. The post bar backs +Y off the
    box.
11. **Pull.** A hook drops into the neck behind the box's rear face and pulls
    +Y to 20 N through a spring, with a switch that sees whether the hook
    followed. Only the crimp carries the load: box → barrels → strands →
    conductor → cassette clamp.
12. **Lay back.** The finger lowers *k*. At 3.5 mm of lift the residual rise at
    the tip is 0–0.77 mm at 20 mm free and 0–0.05 mm at 25 mm [calc wave3 §1],
    so a squaring presser only tidies.
13. **Next key.** J1 takes ~8–11 minutes; a unit's 53 crimps ~49–67 minutes of
    machine time [calc wave3 §6].

The row leaves upright, squared, fronts on one line, lances all down: ready for
bench C's gang insertion (p1) or the person's hands.

**Order within an end.** Odd keys first, then even keys, moves the post bar
back by its tier offset only once, and each odd crimp is made between two
uncrimped neighbours (fin clearance 0.71–0.92 mm a side) while each even crimp
is made between two crimped, squared ones (0.56–1.02 mm) [calc wave3 §2].

## What locates what

| Moment | Located | Against | Held to |
|---|---|---|---|
| Dock | cassette | bench B dowels or three balls | ±0.02–0.05 mm [estimate] |
| Index | key *k* | X lead screw | ±0.02 mm |
| Lift | *k*'s height at the contact | lift finger | ±0.1 mm (the open U forgives ±0.3) [estimate] |
| Beside the fin | *k*±1 sideways | tip comb pins on the cassette | ±0.1–0.2 against 0.56–1.42 mm clearance [calc wave3 §2] |
| Place, axial | insulation edge in the window | post-bar Y slide, corrected by the silhouette and the on-post offset | ±0.07–0.09 mm RSS [calc wave2 §3] |
| Place, lateral | contact on the fin | the crimper's entry flare; the post bar is soft sideways so the steel wins | ±0.02 mm at first die touch [estimate] |
| Crimp height | crimper to fin | knee at straight + gate wedge, all inside the steel C; read by the indicator | read to ±0.01 mm; ±1.5–6 µm of scatter at 100–200 kN/mm [calc wave3 §3] |

**"Fixed" for position is bench B's frame. "Fixed" for crimp height is the steel
C alone.** Precision is needed at two moments, first die touch and the bottom,
and the steel supplies both. The cassette, post bar, finger and slides only have
to bring things inside the crimper's flare.

## What drives the crimp and carries its force

- A NEMA 17 on a Tr8×2 screw pushes the knee joint at 60–160 N. Near straight
  the knee's advantage makes that the 0.8–2.6 kN the crimp needs [digest].
- **The force loop:** crimper → knee links → upper arm → spine → lower arm →
  gate wedge → fin → contact → crimper. It closes inside the C.
- The cassette, the post bar, the lift finger and the X/Y slides carry
  positioning loads only; the post bar sees a few newtons when the flare
  centres the contact.
- **Force sensing without adding compliance:** foil gauges on the spine
  [Prime: foil strain gauges BF350] read force against knee position. A 500 kg
  button cell under the gate would add ±3–12 µm of height scatter inside the
  loop [calc wave3 §4]; the indicator reads it either way.

## How it knows it worked

- identity at the trim and again at the end of the curl, both through the far
  end;
- the backlit silhouette before (bare length, brush) and after (bellmouth,
  insulation edge in the window);
- the force curve against knee position;
- the re-touched crimp height, every crimp;
- the 20 N proof pull and its switch;
- the squaring presser's force.

## Steps it covers, and what it hands back

- **Automated:** trim (square cut), strip in the pose (or p7), measure, place
  the contact on the conductor, crimp, measure height, proof pull, identity at
  every crimp, square.
- **The person:**
  - cuts and peels, or strips the webbed end with p7's lever first;
  - lays the cassette, including the crossings in the loft;
  - loads the post bar in key order;
  - docks the cassette, or a magazine of a unit's ten;
  - inserts at bench C or by hand, labels.
- About 40–44 attended minutes a unit on the same task library that gives ~46 by
  hand [calc wave3 §6; estimate]. The minutes barely move, because cutting,
  peeling, laying in and inserting are most of the person's time. What moves is
  that the priority step is made the same way every time, measured and logged,
  and the machine calls once a unit.

## Printed and bought

- **Printed:** the cassette, root and tip comb blocks, the post bar with its
  lateral flexure, the lift finger, the trim and strip carriers, the C's
  insulating base, the camera mount.
- **Steel, the part to choose** (f7's routes):
  - **Fin:** precision-ground flat stock stood on edge, lapped on top, stepped
    1.45 mm under the conductor barrel and 1.88 mm under the insulation barrel
    (JST's analog crimps 1.50 wide [mfr S14]), its front end relieved behind the
    lance. Or laminated from Prime 1095 blue-tempered shim [Prime: Spring steel
    shim, 0.005–0.032 in, $53.39]: 0.032 + 0.025 in = 1.448 mm and
    0.032 + 0.032 + 0.010 in = 1.880 mm [calc wave3 §2], clamped face to face
    and lapped across the leaves.
  - **Crimper:** a narrow stepped profile, ~3.1 mm wide at the conductor step
    and 2.5–2.7 mm at the insulation step (f8's), cut by wire EDM (±0.01 mm from
    a good shop; JLCCNC states ±0.05 mm [force-and-form f7]), or taken from an
    OTP XH knife set (no Prime listing; price not observed).
  - **The C:** steel plate cut to a drawing, or bar stock drilled on the WEN
    drill press [repo tools.md]; ground guide pins; hardened dowels for the knee.
- **Bought** (Prime rows observed 2026-09-28): NEMA 17 T8×2 ($27.99), MGN9 rail
  ($16.12), music wire ($7.24), header pins ($7.99), light pad ($16.99), digital
  indicator ($52.99; its data cable had no Prime listing), BF350 gauges ($6.99),
  HX711 ($11.50), MG90S servos for the finger and gate ($13.88 for four), a
  BTT SKR Pico ($35.99). The ELP camera and the NEMA 23 are on hand [repo].

## Problems, and what answers each

1. **The contact's neck, *n* (box rear to conductor barrel front).** The fin must
   carry the conductor barrel's front and still stop behind the lance:
   *n* ≥ 0.34–0.74 mm. The clone drawings' length budget gives 0.30–2.28 mm
   [calc FP §5; force-and-form on_into_the_housing §1d]. One kit contact
   photographed side-on under the ELP camera settles it. If *n* is short, the
   fin stops at the lance and the barrel's front 0.1–0.3 mm is carried by the
   crimper's flare alone.
2. **Tip wander against the fin's clearance.** 0.56–1.42 mm a side [calc wave3
   §2]. The tip comb 5–7 mm back is the answer, and it is unbuilt. The camera
   sees a neighbour inside the fin's path before the fin rises.
3. **The insulation crimp on silicone.** The crimper's step fixes insulation
   height relative to conductor height. On this jacket the insulation barrel
   grips the conductor only weakly, and its window runs between cutting the
   jacket and the 2.4 mm cavity ceiling (force-and-form
   [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md)). Branch
   **p1d-f6** below separates it.
4. **The proof pull's reaction at a cut loom.** The cassette clamp grips the
   jacket, and the copper must not slide inside it: a clamp squeezing the jacket
   15–30 % over 5–20 mm holds 20 N [calc FP §4]. A light clamp fails good crimps
   (the copper creeps and the switch sees the hook follow); it does not pass bad
   ones. At a reel the whole reel anchors the copper.
5. **Squaring below 20 mm free.** At 15 mm the rise is 0.46–2.16 mm [calc wave3
   §1], so squaring does real work. A 20–25 mm split makes it tidying.
6. **The gate, the fin slide and the knee pins over ~3,200 cycles**, and whether
   the fin's slide lets it tip at first die touch. The indicator reads the
   result every crimp either way.

## Branches kept beside it

- **p1d-reel.** The same station at [p6](p6-spool-end-bench-that-grows.md)'s reel
  clamp or [p3](p3-terminate-at-the-spool-cut-last.md)'s work clamp. The post bar
  rides the clamp's X slide; identity goes through the hub socket or slip ring;
  the whole reel reacts the proof pull (problem 4 disappears); a bad crimp
  costs 6 mm of reel.
- **p1d-SN-crimper.** A harvested SN XH crimper half as the upper die over the
  fin (f7 route a). At *h* ≥ 3.1 mm its bar clears the neighbours, but it is
  20–30 mm long in X and would come down on the posted contacts for *k*±2, so
  the post bar gives way to a single shuttle post loaded from a revolver. The
  fin must match the SN channel's width; pin gauges read it [Prime: Precision
  pin gauges, $45.58]. This is the cheapest steel route and the least
  controlled profile.
- **p1d-f6.** The crimper carries only the conductor step. f6's separate
  insulation blade, on its own small drive and wedge, forms the insulation
  barrel to its measured window.
- **p1d-hand.** The knee closed by a hand lever instead of the NEMA 17, the X
  index by a detent knob, the lift by a lever: a bench jig once the steel
  exists.
- **In other arrangements of this view:** [p2](p2-still-ribbon-tool-turret.md)'s
  head F (the same C on the turret), [p5c](p5c-camshaft-turns-a-knee.md) (one
  camshaft drives this station), [p6](p6-spool-end-bench-that-grows.md)'s stage
  1-fin.

## Contribution

- **The lift is set by die geometry, not by a hand tool's shape.** Only the fin
  passes through the row plane, so *k* rises 3.5 mm and keeps essentially no
  set at 25 mm free. The same order with an SN-2549 needs 8.7–14.7 mm.
- **Every crimp is upright** on a flat row, which is what gang insertion and
  every housing cavity want.
- **The contact goes onto the conductor before any tool closes**, so nothing
  pinches the insulation bore while the conductor enters, and the tool closes
  once, around both.
- **Crimp height is a setting, measured on every crimp**, from steel Derek
  chooses.
- **The station is fixed and small.** The row comes to it, as it comes to every
  bench of p1.

## Major unresolved problems

- **The steel:** the crimper profile (EDM to a traced drawing, or a knife set of
  unknown profile and price) and the fin's temper. This is force-and-form f7's
  whole open list.
- **The neck *n*** (problem 1).
- **Tip wander** against 0.56–1.42 mm of fin clearance; the tip comb is
  unbuilt.
- **The insulation crimp on silicone** at a fixed step.
- **The proof-pull reaction** through the cassette clamp.
- **Wear of the gate, fin slide and knee** over the program.

## What rests on assumptions

- The contact's neck, barrel lengths and lance position are read from clone
  drawings [xh-facts §1]; the kit contacts are unmeasured.
- The set figures use strand yield 60–120 MPa and silicone 2–6 MPa [assumption,
  calc wave2 §1].
- Cycle time and person minutes [estimate].
- The crimper's first-touch centring of a contact on a laterally soft post bar
  [estimate].
- Laminated shim surviving 400–900 MPa of die pressure [assumption].
