# f10 — Lift once, crimp upright: a fixed steel C over a flat row, its anvil a fin rising from below

Explorer: force-and-form. A combination:
- procedure-is-the-machine's [p1c](../../procedure-is-the-machine/ideas/p1c-lift-once-tip-down-module.md)
  order (lift conductor *k* once and do everything to it in that pose), its
  [p1](../../procedure-is-the-machine/ideas/p1-cassette-and-benches.md) cassette
  (keys = cavities, crossings made in the loft, far end in a pogo block) or
  [p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md)'s
  reel clamp, and contacts held on 0.64 mm posts in key order
  (terminal-supply's a4 and x1);
- force-and-form's steel C with a knee standing still at the station
  ([`f4`](f4-crimp-head-goes-to-the-wire.md)'s head, not travelling;
  [`f3`](f3-knee-micropress.md)'s geometric bottom and re-touch gauge), the
  anvil as ground stock stood on edge ([`f7`](f7-where-the-steel-comes-from.md))
  and the lance relief ([`f8`](f8-narrow-press-at-the-housing-mouth.md)).

It is FP1 in
[force-and-form's reading of procedure-is-the-machine](../../../exchange/force-and-form--on--procedure-is-the-machine-w3.md),
developed here.
Sketch: [`../sketches/fp1-lift-once-fin-from-below.svg`](../sketches/fp1-lift-once-fin-from-below.svg)
(schematic; proportions follow the cited dimensions roughly).
Numbers:
- [calc FP §n]: [`../calc/exchange_procedure_w3.out.txt`](../calc/exchange_procedure_w3.out.txt);
- [calc final §n]: [`../calc/final_w3.out.txt`](../calc/final_w3.out.txt);
- [calc wave2 §n], [calc drives §n], [calc on_ith §n]: force-and-form's
  `wave2`, `drives` and `on_into_the_housing` outputs in [`../calc/`](../calc/);
- [calc P wave2 §n]: procedure-is-the-machine's
  [`wave2.out.txt`](../../procedure-is-the-machine/calc/wave2.out.txt). **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md), observed
2026-09-28.

## Picture it

The ribbon stays flat at housing pitch, 2.5 mm, in one plane. Only conductor
*k* is lifted, 3.5 mm. A fixed steel C crimps it from above, and the only part
of the press that ever enters the row's plane is a fin-shaped anvil rising from
below through *k*'s own empty slot. The crimp comes out upright, lance down, the
way every housing cavity wants it.

**Where things start (J1 in its cassette; a 4P end at a reel clamp works the
same).**
- **The cassette** is loaded as p1 loads it: keys 1–9 = cavities 1–9, J4's and
  J7's crossings made in the loft, J2's key 3 blanked, the far end in a pogo
  block that reads every conductor.
- **The comb** of 0.635 mm music-wire pins [Prime: K&S 5005 music wire,
  0.025 in, $7.24] holds the conductors 20–30 mm back.
- **A tip comb**, a second short row of the same pins on the cassette, stands
  4–6 mm behind the tip line, just behind where the insulation barrels will
  sit. Its tops are ~1 mm above the row axis.
- **A post bar** rides the cassette's X carriage. It holds J1's nine contacts
  box-first on 0.64 mm posts [Prime: 2.54 mm male pin headers, $7.99], one per
  key, in key order, open side up and lance down.
  - The posts stand in **two tiers**: odd keys at one Y, even keys ~8 mm
    further forward, so open contacts on one tier are 5.0 mm apart and open
    wings (2.46–3.0 mm) never touch.
  - The posts sit at the lifted height, ahead of the tips.
  - The person fills the bar at leisure; it is the build list. A kit contact
    and a strip stub cut to one pitch are both "a contact on a post".

**Fixed at the station.**
- The X slide that carries the cassette and its post bar.
- A lift finger on a servo under the station line, ~10 mm behind the
  contacts.
- A trim blade and a strip head on a Y carriage (p1c's), or none if the end
  was stripped before (procedure-is-the-machine's p7).
- The ELP camera looking **along X** at the lifted height, with a light pad on
  the far side [Prime: XIAOSTAR A5 light pad, $16.99]. Only *k* is at that
  height, so its silhouette stands alone.
- **The steel C.** Its spine stands ~15–20 mm ahead of the tips, its throat
  open toward the cassette, and the row indexes through the throat in X.
  - *Upper arm:* a knee pushed by a NEMA 17 on a Tr8×2 screw at 60–160 N
    [Prime: Iverntech 42HD6039-05, $27.99, thin] drives a crimper on two ground
    guide pins, with a 0.001 mm indicator across the dies [Prime: Clockwise
    DITR-0105, $52.99; its DTCR-01 data cable had no Prime listing].
  - *Lower arm:* lies entirely below the row. In a slot in it slides the
    **fin**. When the fin is up, a ground **gate block** slides under its foot
    on a servo, and a button load cell sits under the gate [Prime: 500 kg
    button load cell, $74.99, thin].

**One key, *k*** (about 60–90 s [estimate]):
1. **Index.** X brings key *k* to the station line. The fin is down, its top
   1 mm below the row's underside, and the crimper is open.
2. **Lift.** The finger raises *k* by **3.5 mm**. The neighbours stay in the
   row; *k* lifts out from between its two tip-comb pins.
3. **Trim.** The trim blade is grounded. Cutting through copper it touches
   *k*'s strands, so the far-end pogo block reads which conductor this is, and
   that no other conductor reads. Identity is taken where copper is touched
   anyway.
4. **Strip** in the pose (p1c), or already done.
5. **Look.** The side silhouette gives the bare length (where the insulation
   edge is) and whether the brush is whole.
6. **Place.** The post bar's Y slide [Prime: MGN9 rail and carriage, $16.12]
   moves contact *k* −Y onto *k*'s stripped end through its fully open
   barrels: 0.72 mm of strands into a 1.5–1.9 mm U, 1.7 mm of jacket into
   2.46–3.0 mm wings. It stops where the measured insulation edge lands
   mid-window. The contact's box-front-to-barrel offset was measured on its
   post (±0.07 mm RSS [calc P wave2 §3]), and nothing touches the contact
   between that measurement and the crimp. The other contacts on the bar ride
   over their own unlifted conductors: a lift of 2.8–3.1 mm keeps their lances
   clear [calc FP §1a].
7. **Fin up.** The fin rises 4.3 mm through *k*'s empty slot between *k*−1 and
   *k*+1, and the gate block slides under its foot. Its top meets the contact's
   floor under the barrels. The box overhangs the fin's front edge, so the fin
   stops behind the lance (f8's relief).
8. **Crimp.** The knee drives the crimper down to straight: 0.2 mm short of
   straight is ~1 µm (f3). At the end of the curl (~150–450 N, before
   compaction) the drive pauses: the wing tips are on the strands, so
   continuity through the post confirms identity a second time. Then
   compaction, with force logged against knee position.
9. **Height.** The crimper re-touches at ~10 N and the indicator reads the
   unloaded crimp height; or the knee chases a measured target in two or three
   hits [calc wave2 §10].
10. **Clear.** The knee opens, the gate slides out, the fin drops 4.3 mm
    (clearing the lance by far more than its 0.6–0.9 mm), and the post bar
    backs +Y off the box.
11. **Pull.** A hook drops into the neck behind the box's rear face and pulls
    +Y 20 N through a spring, with a switch. The cassette's clamp is the
    reaction; it must squeeze the jacket (below).
12. **Lay back.** The finger lowers *k*. At a 3.5 mm lift the residual rise is
    0.46–2.16 mm at 15 mm free, 0–0.77 mm at 20, 0–0.05 mm at 25 and none at
    30 [calc FP §1, procedure-is-the-machine's own set model]. p1c's squaring
    presser tidies what is left.
13. **Next key.** J1 takes ~9–14 minutes.

The unit's rows come out upright, squared, fronts on one line, lances down,
ready for a gang insertion (procedure-is-the-machine's bench C) or the person.

## What locates what

| Moment | What is located | Against | Held to |
|---|---|---|---|
| Dock | cassette | the station's dowels | ±0.02–0.05 mm |
| Index | key *k* | X lead screw | ±0.02 mm |
| Lift | *k*'s height at the contact | lift finger | ±0.1 mm (the open U forgives ±0.3) |
| Fin | *k*±1, laterally | tip-comb pins on the cassette | ±0.1–0.2 mm against 0.55–0.92 mm clearance |
| Place, axial | barrels against the insulation edge | post-bar Y slide, set from the silhouette and the on-post offset | ±0.07–0.09 mm RSS [calc P wave2 §3] |
| Place, lateral | contact on the fin | the crimper's entry flare; the post bar is built laterally compliant so the steel wins | ±0.02 mm at first touch |
| Crimp height | crimper to fin | knee at straight + gate block thickness, all in the C; read by the indicator | ±0.01 mm read; ±1.5–6 µm from force scatter at 100–200 kN/mm [calc FP §3] |

"Fixed" for position is the station frame. "Fixed" for crimp height is the
steel C alone.

## The fin and the lift

- **Only the fin enters the row plane.** A crimper of any width clears
  uncrimped neighbours at a lift of 2.5–2.7 mm and crimped, squared ones at
  2.9–3.1 mm; the posted contacts for *k*±2 clear their own conductors at
  2.8–3.1 mm. A 3.5 mm lift serves every case [calc FP §1a].
- **Width.** The anvil sits inside the crimper's channel, so its width sets
  the crimp's. JST's analog SXA-01T-P0.6 crimps 1.50 wide at 22 AWG [mfr S14].
  The fin is stepped: **1.45 mm** under the conductor barrel, **1.88 mm** under
  the insulation barrel. A 1.6–1.9 mm fin under the conductor barrel would make
  a crimp 1.66–1.96 wide and 0.05–0.12 mm lower than the analog profile
  [calc FP §2].
- **Clearance to the neighbours**, at 2.5 mm pitch [calc FP §2]:
  - conductor step (1.45): 1.42 mm a side to bare strands, 1.02 mm to a
    crimped conductor barrel;
  - insulation step (1.88–1.90): 0.70 mm a side to an uncrimped jacket, 0.55 mm
    to a crimped insulation barrel.
- **Column.** Narrow only through the ~4 mm row band, a 3.5 × 1.45 × 4 mm fin
  keeps 27 kN of Euler load against 3 kN, at 591 MPa [calc FP §2].
- **Where the fin comes from.** Ground flat stock stood on edge, its width the
  stock's ground thickness (1.5 mm gauge plate ±0.013 mm, lapped to 1.45; or
  0.075 in ground stock for the insulation step, not yet confirmed on Prime), its top lapped
  as the anvil face.
- **Target height at this width.** At a 1.51 mm channel the target is
  0.80–0.87 mm, found from the JST reference lead corrected for copper at the
  machine's own width [calc final §7].

## What drives the crimp and carries its force

- A NEMA 17 Tr8×2 pushes the knee joint at 60–160 N [calc drives §B].
- The loop is crimper → knee links → upper arm → spine → lower arm → load cell
  → gate block → fin → contact.
- The cassette, post bar, lift finger and slides carry positioning loads only.
  The post bar sees a few newtons when the crimper's flare centres the
  contact.

## How it knows it worked

- identity at the trim, and again at the end of the curl, through the far end;
- the force curve against knee position;
- the re-touch height on every crimp;
- the side silhouette before (bare length, brush) and after (bellmouth,
  insulation edge in the window);
- the 20 N proof pull and its switch;
- the squaring presser's force.

## What it automates, and what the person does

- **Automated:** trim, strip in the pose (or none if stripped before), measure,
  place the contact, crimp, measure height, proof pull, identity at every crimp,
  and square.
- **The person:** cuts; peels or splits the ribbon end; lays the cassette,
  including J4's and J7's crossings in the loft; fills the post bar in key order
  at leisure; docks the cassette (or a magazine of them); inserts at a gang
  insertion station or by hand; labels.

## Branches

- **At the reel (f10-reel).** At p6's reel clamp or procedure-is-the-machine
  p3's work clamp, the post bar rides the clamp's X slide. The whole reel reacts
  the proof pull, identity goes through the hub socket, and a bad crimp costs
  6 mm of reel.
- **An SN crimper half over the fin.** A harvested SN XH crimper half
  (f7's jaw source) as the upper die. At a lift of 3.1 mm or more its bar clears
  the neighbours [calc FP §1a], but it is 20–30 mm long in X and comes down on
  the posted contacts for *k*±2, so a single shuttle post replaces the bar, and
  the fin must be matched to the SN channel's width, read with pin gauges
  [Prime: Accusize 0.011–0.060 in pin gage set, $45.58].
- **A laminated fin.** 1095 blue-tempered shim [Prime: Precision Brand shim
  assortment, 0.005–0.032 in, $53.39] clamped face to face: 0.032 + 0.025 in =
  1.448 mm for the conductor step; 0.032 + 0.032 + 0.010 in = 1.88 mm for the
  insulation step; its top lapped across the leaves. Spring temper
  (~Rc 45–50 [assumption]) against 400–900 MPa of mean die pressure is its open
  question.
- **With f6's second blade.** The crimper carries only the conductor step, and
  [`f6`](f6-two-blades-two-drives.md)'s insulation blade on its own drive and
  wedge sets the insulation barrel to this wire's window.
- **By levers, the first build** (motorless). The cassette on a hand slide with
  2.5 mm detents, the lift finger and the fin on cam levers, the post bar on a
  hand slide, and a hand lever on the knee (60–160 N is a hand push) driven to
  the knee's stop. The camera and indicator are read on the Mac. It needs the
  steel C and its dies and nothing else that moves by motor.
- **A camshaft turns the knee** (procedure-is-the-machine p5 × f3). One shaft,
  one turn per conductor, cams for index, lift, post-bar Y, fin and gate, a knee
  lobe that drives the knee *through* straight to a stop just past it (so the
  printed lobe's profile error never reaches crimp height), the hook pull, and
  lower-and-square. Shaft torque from the crimp's work: 0.12–0.63 N·m average,
  ~0.25–1.9 N·m peak [calc FP §8]. A 12 V self-locking worm gearmotor at
  40 kg·cm and 10 rpm covers it [Prime: Greartisan, $26.99, 40 ratings], with
  an AS5600 on the shaft [Prime: UMLIFE AS5600, $7.99]. A small stepper on the
  post bar alone buys back the camera's axial correction.

## Contribution

- **Working a flat row at housing pitch without splitting it into planes.**
  The lift is set by die geometry (only the fin passes through the row), not by
  a hand tool's shape, and the crimp is upright.
- **The jaw's closing direction is the contact's floor normal.** Any head
  working a flat row must close normal to the row; a tool closing along the row
  rolls every crimp 90° (hand-tool-as-press a3's own finding).
- **Contact placed on the conductor, then the die closes on both.** The
  conductor never threads a captured barrel, so the pinched bore at capture
  (0.03–0.17 mm interference for floors of 1.6–1.7 mm [calc wave2 §1]) never
  matters.

## How it connects to the whole procedure

| Step | Who does it |
|---|---|
| Cut, peel or split, lay the cassette with crossings | the person |
| Trim, strip | **automated** in the pose, or p7 before |
| Supply contacts | the person fills the post bar in key order |
| Place the contact on the conductor | **automated** (post bar Y slide, camera-set) |
| Crimp, measure, pull, identity, square | **automated** |
| Insert | a gang insertion station or the person; rows arrive upright and in cavity order |

## Major unresolved problems

- **The steel.** The crimper profile comes from a knife set (price and profile
  unobserved) or wire EDM. All of f7's open list applies.
- **The transition *t*.** A fin that stops behind the lance and still carries
  the conductor barrel's front needs t ≥ 0.34–0.74 mm; the clone drawings'
  length budget gives 0.30–2.28 [calc on_ith §1d]. The hook in the neck needs
  t ≥ 0.50–0.70 mm [calc final §3].
- **Tip wander** near the tips against 0.55–0.92 mm of fin clearance. The tip
  comb is the repair, and it is unbuilt.
- **Set below 20 mm free.** At 15 mm free the rise is still 0.5–2.2 mm, so the
  squaring pass stays.
- **The gate block and fin drop over ~3,200 cycles**, and whether a load cell
  in the lower stack costs height stability; the indicator reads it anyway.
- **The post bar's lateral compliance** against its positioning.
- **The proof-pull reaction at a cut loom.** The cassette's clamp grips the
  jacket; the strands slip inside it at 1.4–6.3 N per mm of grip at 30 %
  squeeze, 0.5–2.1 N/mm at 10 %, so a clamp must squeeze 15–30 % over 5–20 mm
  or a good crimp fails the pull [calc FP §4]. At a reel it disappears.

## Which conclusions rest on assumptions

- The set model is procedure-is-the-machine's (elastic-plastic strands,
  silicone 2–6 MPa), imported read-only.
- Crimp width against fin width uses an equal-enclosed-area estimate.
- The laminated fin's hardness is assumed from spring temper.
- The cycle time per key is an estimate.
