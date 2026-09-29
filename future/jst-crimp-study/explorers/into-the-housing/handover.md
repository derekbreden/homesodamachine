# What insertion needs from the crimp

The step after crimping belongs to this view, so this file says what state a
crimped conductor has to be in when it reaches the housing. Any crimp
arrangement from any explorer can be checked against it. Numbers are in
[`calc/insertion_geometry.out.txt`](calc/insertion_geometry.out.txt),
[`calc/wave2.out.txt`](calc/wave2.out.txt) and
[`calc/wave3.out.txt`](calc/wave3.out.txt) unless a source is named;
force-and-form's reading of this file is in
[`../force-and-form/calc/on_into_the_housing.out.txt`](../force-and-form/calc/on_into_the_housing.out.txt).

**Coordinates used in every file here.** Y is the contact's axis, +Y toward the
housing's mating face (the box leads). X runs across the row, the pitch
direction. Z is up: the barrels open up, and the lance and the housing's
windows face down.

## The reference

**The ribbon clamp is "fixed".** It grips the unsplit ribbon (the web) and is
the one datum that strip, crimp and insertion all refer to. A conductor's
length from the web to its stripped tip is set once, when it is stripped, and
nothing downstream can change it.

- The finished loom puts every seated contact at a set distance from the web.
- Any contact crimped short of its seated position has to travel forward by the
  difference after its crimp.

## The feed-length rule

**One contact at a time.** The conductor being crimped carries its insertion
travel as extra length, a hump or a lift. Nothing else can supply it, because the
web is clamped and the neighbours are already seated. [calc geometry §9]

| Where the crimp happens | Travel after the crimp | Stored as |
|---|---:|---|
| Box already ~2 mm into its own cavity (i2) | ~5.2 mm | a 4–6 mm hump over a 10–20 mm free length |
| Box nose 1 mm behind the rear face (i1b) | ~8.2 mm | a 5–8 mm hump |
| At a head 5 mm behind the rear face | ~12 mm | a hump of ~7–10 mm, or a lift of 16–25 mm to a head above the row (i1) |
| **All of a ribbon at once, housing moved onto the row (i3, i6)** | **0** | **nothing** |

**What it costs.** During the build the split conductors need ~10–30 mm of free
length behind the housing, while the finished fan needs ~6–9 mm (J1's outermost
conductor moves 3.2 mm [context calc C1 §2]). A rework cut shortens one
conductor by roughly a contact length, and that comes out of the same budget.

## What the crimped conductor must be, at handover

1. **Orientation.**
   - Lance down, barrel seams up, the same face as the ribbon's "down" side.
   - Roll within about ±10–15°, so the cavity's lead-in can square it
     [estimate].
   - The Sogang ribbon inserter's failures came from roll, pitch and yaw of
     free-hanging terminals; "lean and slide" took its insertion from 3/20 to
     18/20 ([arXiv 2608.06996](https://arxiv.org/html/2608.06996)) [source].
   - A crimp made with the jaws closing across the row (a hand tool hung
     tip-down over a comb) comes out rolled 90°: barrels opening sideways, lance
     pointing along the row. Twisting it back over a 20–35 mm split takes a
     partial torsional set [calc: exchange_hand_tool_as_press §8].
2. **Straight.**
   - No bend up or down, twist or roll at the barrels beyond JST's appearance
     checks ([JST handling precautions §3.4][jsth]) [mfr]. A 5° bend over the
     2 mm box moves the nose ~0.2 mm, about an entry chamfer [estimate].
   - A gripper that holds the wire rigidly 2–3 mm behind a barrel while the
     anvil sets the barrel floor bends the conductor by any mismatch; copper
     sets below ~67 mm radius [force-and-form §4]. The silicone jacket absorbs
     33–52 % of it over 2 mm and 13–24 % over 3 mm, at Shore 50–70A
     [calc wave3 G]. Grips go loose in X and Z for the forming stroke.
   - A front stop at the box nose must give way during coining. The conductor
     barrel's front grows ~0.03–0.11 mm toward the box [estimate,
     change-the-question]. Against a rigid steel stop the transition bows
     (JST's bend fault); a fixed PA6 stop dents. A stop preloaded at 10–30 N,
     or a rear reference (tab stub, box shoulder), avoids it [calc wave3 C].
3. **Narrow and low enough for the cavity.**
   - The closed insulation barrel must fit the box's end-view envelope,
     1.95 × 2.4 mm [mfr S1]. This is an **insulation-die dimension**: on 1.7 mm
     silicone a narrower crimp grows taller. A crude ellipse model gives
     1.90 mm wide at 1.94–2.33 mm tall, and 1.80 mm wide at 2.05–2.46 mm tall
     unless the silicone extrudes along the wire [force-and-form §9, estimate].
   - Today's SN-2549 crimps enter the housing, so their insulation width and
     height by caliper are the target any machine die copies. JST's own factory
     crimp on a 22 AWG lead (ASXHSXH22K305, $0.90 at Digi-Key [source, via
     change-the-question c2]) is the other reference; its wire is probably PVC.
   - Wing tips tucked, not flared. A narrow insulation crimper working beside a
     neighbour at 2.5 mm has a mouth of only ~2.3–2.6 mm, narrower than most
     clone open wings (2.46–3.25 mm): a tip that lands on the wall's end face
     flares. The ways through are pushing a neighbour's jacket aside, a
     pre-formed keyhole (1.96–2.14 mm), or narrow wings [calc wave3 A].
   - The cut-off tab about one stock thickness (≤ ~0.3 mm), cut at the bottom of
     the stroke while the barrels are still held; cut after, its 50–160 N pulls
     the rear down [force-and-form].
4. **Clean.**
   - No strand outside either barrel; at 2.5 mm pitch a stray reaches a
     neighbour or snags the entry.
   - The brush stops short of the box (JST's rule [mfr S5]); strands in the box
     keep the post out.
5. **Held close, by the barrels.**
   - A push through the wire buckles it unless held within ~1.5–3.5 mm of the
     insulation barrel with the nose free, ~3–8 mm with the contact guided
     (3–15 N; at 25 N ~1.2 and ~2.4–5.3 mm) [calc geometry §1].
   - Grips close on the crimped barrels: their floor is flat and their top is
     two lobes with a cusp, so a flat pad below and a pad shaped to the lobes
     above hold roll [force-and-form]. Grips on the round wire farther back let
     the contact roll.
6. **Proved before the push.** Proof-pulled to ~20 N (half of JST's 39.2 N)
   against a fork or backing blade, between the crimp and the insertion. A proof
   load that means anything about the crimp would pull a latched contact out of
   its cavity (retention ≥ 14.7 N analog, ≥ 19.6 N clone spec), so after
   insertion only the latch can be tested (≤ 5 N) [force-and-form §7].
7. **Lance intact and sprung.** Every flat anvil must leave the lance hanging
   free ahead of its front edge, or in a slot: the contact's transition
   t ≥ lance tip + 0.1 − box = 0.34–0.74 mm, whatever holds the box [calc wave2 G].
   The lance is never loaded rearward against steel at the crimp station, for
   example by a proof pull that bears on it [calc: exchange_hand_tool_as_press
   §4]. The insertion trace's fold rise and snap prove it survived.
8. **In order** (next section).
9. **For a gang push only.** All fronts on one line to ±0.3 mm [estimate, about a
   lead-in chamfer], contacts parallel, each reacted within 0–4 mm of its
   insulation barrel (a clamp, or a backing blade on its rear).
   - Contact lengths differ (clone drawings 5.8–6.73 mm, each ±0.25 [source
     S19–S22]), so a rigid blade bottoms the longest first. The push stops at
     the first wall and a single finishing tine brings each contact to its own
     wall, or the tines ride on constant-force springs [calc wave3 E].
   - Whatever reacts the push has to follow up to ~2 mm into the cavity: a
     seated rear lies 0–1.8 mm inside the rear face [calc wave3 H].
10. **Labelled.** The loom's name travels with it. J4 and J7 take the same 7-way
    housing, and a swap is a wiring fault [repo: `cable-assemblies.md`]. Any crimp
    flagged at the crimp step arrives marked, so it is cut off and redone before
    it is buried in a housing.

## Pin order: two looms cross, and a crossing is a layer

The repo's ribbon assignment [repo: `hardware/assembly/cable-assemblies.md`
§ Ribbon pairs] against the board's pin order [repo: `hardware/pcb/pcba/pcba.tsx`,
J4 and J7] cannot be laid straight across from ribbon to housing for J4 and J7
[calc geometry §3, calc wave2 A; sketches
[`pin-order-crossings.svg`](sketches/pin-order-crossings.svg) and
[`pin-map-layers.svg`](sketches/pin-map-layers.svg)].

- **A crossing is one conductor lying over another in the split.** A pin map
  splits into layers, each laid in order without crossings. The fewest layers is
  the longest run of conductors whose pins decrease in web order.
- **J7 REEDS B** (5P RB1–RB4 + GND, 3P CLO + CHI + trimmed): 2 layers, 2 crossings.
  GND rides over CLO and CHI to pin 7.
- **J4 SENSORS** (4P 3V3/IO26 and V5/IO25 pairs, 3P GND/IO27/IO23):
  - with the 4P's pairs kept adjacent for the far-end peel, the fewest crossings
    is 5. Laid V5, IO25, 3V3, IO26 | GND, IO27, IO23 it is 2 layers: 3V3 and GND
    ride over the rest to pins 1 and 2. Laid 3V3, IO26, V5, IO25 it is 3 layers;
  - with the 1-wire pair split around the flow pair (3V3, V5, IO25, IO26) it is 3
    crossings and 2 layers, GND riding over V5, IO25 and IO26.
- In both, the upper layer lands at an end of the housing, beside the lower
  layer.
- **Straight across:** J1, J2 (cavity 3 is an empty slot, not a crossing) and the
  six single-ribbon looms are one layer.

**Two counts, one order.** change-the-question's half-row machines count
something else: conductors that must change plane at the parity split, and
crossings within each plane. Both counts are right for their own machines
[change-the-question calc on_into_the_housing_w3 §9]:

| J4 laid | Layers, crossings (one plane) | Off-parity, crossings (half-rows) |
|---|---|---|
| V5, IO25, 3V3, IO26 \| GND, IO27, IO23 | 2, 5 | 2, 2 |
| 3V3, IO26, V5, IO25 \| GND, IO27, IO23 | 3, 5 | 2, 2 |
| 3V3, V5, IO25, IO26 \| GND, IO27, IO23 (pairs split) | 2, 3 | 4, 1 |

- V5, IO25, 3V3, IO26 is the least-crossing 4P order for both families. Fixing it
  in `cable-assemblies.md` is Derek's choice.
- For J7 in one plane it does not matter which 3P conductor is trimmed. In
  half-rows, trimming the one beside the 5P gives (0, 1) and the far one (2, 1).
  The repo's "third conductor trimmed" names one end only once the 3P's
  orientation is fixed.

**Or change the board.** Board pin orders that make every ribbon one layer:
J4 = 3V3, IO26, V5, IO25, GND, IO27, IO23 (or V5, IO25, 3V3, IO26, GND, IO27,
IO23) and J7 = RB1, RB2, RB3, RB4, GND, CLO, CHI [same calc §9]. J7 can
instead be made straight with no board change, by moving GND onto the 3P with
CLO and CHI and trimming the 5P's fifth conductor (procedure-is-the-machine's
rewire). The J4 order costs routing work: `pcba.tsx` routes IO25, IO26 and IO27
so the present order lands uncrossed [repo]. With both, a fixed comb per loom
places a whole unit.

**What each kind of arrangement does with it.**
- **One at a time** (i1, i2, i4, i5): any order works if the conductors still
  waiting are held above the plane where placed ones lie, by more than
  2.0 mm / f at their crossing points (f = fraction of the span from the root).
  With the lower layer first and the order running from the housing's centre
  outward, 5–8 mm covers every loom [calc wave2 C].
- **Gang** (i2b, i3): the row's order is set when conductors are laid in, so a
  person makes the crossing, or a sort ([i6](ideas/i6-sort-then-push.md),
  [k6](ideas/k6-one-gantry-crimps-in-the-fan-then-sorts.md),
  [k8](ideas/k8-half-rows-crimped-then-sorted.md)) places each contact into a
  fixed target row first.
- An automatic splayer that keeps ribbon order into a gang push misses J4 and J7.

[jsth]: https://www.jst-mfg.com/product/pdf/eng/handling_e.pdf
