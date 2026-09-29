# Notebook — into-the-housing

## Log

### Wave 1

- **Read the brief, shared context, working method, xh-facts and prior-art in
  full.**
- **Checked the repo for pin order.**
  - `hardware/pcb/pcba/pcba.tsx` gives J4 = 3V3, GND, V5, IO25, IO26, IO27,
    IO23 and J7 = RB1, RB2, RB3, RB4, CLO, CHI, GND.
  - `cable-assemblies.md` puts J4's 3V3/IO26/V5/IO25 on the 4P and IO27/IO23/GND
    on the 3P; J7's reservoir column (RB1–RB4 + GND) on the 5P and CLO/CHI on
    the 3P.
  - J4 needs ≥ 3 crossings and J7 ≥ 2 before the housing
    ([calc wave 1 §3](calc/insertion_geometry.out.txt),
    [sketch](sketches/pin-order-crossings.svg)); that count lets the 4P's pairs
    separate.
- **Read the JST XH catalog (2025), CJT's A2501 catalog, JST's handling
  precautions, the Sogang arXiv paper, and Molex Mini-SPOX figures** (the last
  from a search summary). Details in wave-1 summary.
- **Ran calc wave 1.** Buckling, 2.5 mm clearances, crossings, crimp-in-cavity
  window, gang force, latch sensing, split for wide pitch, feed-length rule,
  time per unit.
- **Web search budget ran out** partway; further facts by direct page fetch.

### Wave 2

- **Read** force-and-form's critique of this explorer, all eight other
  summaries, the digest, and this explorer's own exchange on hand-tool-as-press
  (its C1–C6 and "where their work changes my ideas"). Glanced at
  force-and-form's new f8 (their development of K1) and terminal-supply's a6.
- **Accepted from the critique**, and written into the idea files as they now
  stand:
  - i2: lance condition, floating nest (steel master), 3.1 mm stepped crimper
    with 0.8 mm walls landing on anvil shoulders, knee in a steel C, hump as a
    lever, anvil-down feed, backstop as proof-pull fork, cavity as terminal
    guide. i2 as it stands is K1.
  - i2b: 1.5 mm anvil drop; odd-then-even gives the crimper crimped neighbours.
  - i2c: the lance takes a set with every fold; branch i2d.
  - i1/i1b: f1-class actuator, ratchet release, leaving in Z, loose fingers for
    the stroke, camera as the axial reference, dies bottoming, knee under the
    anvil.
  - i3/i3b: fronts at the head by docking, proof pull before closing,
    constant-force springs.
  - i4: loose wrist for the stroke, capture-then-thread station.
  - i5: proof-pull fork and crimp-height pocket beside the nest (K4).
  - handover: insulation-die dimension, lobed grip, proof pull before the push,
    lance intact, tab cut at the bottom of the stroke.
- **Where I disagree, in part** (calc F): the critique says any grip mismatch
  above ~0.02 mm kinks the conductor. The silicone jacket is compliant and
  takes 20–70 % of a mismatch over 2 mm; at 0.05 mm what remains sets only
  ~1°. At 0.1–0.2 mm it is a real kink, so loose fingers remain the repair.
- **Found (calc G):** the lance condition t ≥ lance tip + 0.1 − box belongs to
  the contact, not the housing. Box depth drops out. The SN-2549 meets the same
  inequality today, or has a relief; one look at its anvil answers it for i2,
  i2d and every cradle.
- **New direction: i6, sort then push.** The J4/J7 crossings, pairs and J2's gap
  automated. Calc A: every loom is one layer except J4 and J7; each carries one
  group over the rest to an end of the housing. Calc C: waiting conductors
  staged 8–10 mm above placed ones never trap, if the lower layer goes first
  and the order runs from the housing's centre outward. Branch i6b (post bed),
  combination k6 (with force-and-form f4).
- **i2d**, developed from force-and-form's i2c′/i2c″: a housing stub the lance
  never enters, first on the SN-2549 by hand.
- **Fetched** JLCPCB's capabilities page: hole position ±0.075 mm, press-fit
  holes ±0.05 mm (for i6b).
- **Ran calc wave 2** ([`calc/wave2.out.txt`](calc/wave2.out.txt)): layers,
  travel and bows, staging height with order search, slot grip and blade,
  post stiffness, jacket compliance, lance condition, stub depth, time.

### Wave 3 (final pass)

- **Read** change-the-question's second-exchange critique
  ([`../../exchange/change-the-question--on--into-the-housing-w3.md`](../../exchange/change-the-question--on--into-the-housing-w3.md))
  and its calc, the Prime pass in `sourcing/amazon-prime.md`, and
  change-the-question's c6, c6b, c1c, c5 and c2.
- **Ran** [`calc/wave3.py`](calc/wave3.py) ([out](calc/wave3.out.txt)): the
  insulation mouth with a push-aside allowance, the hump's elastic push, a
  preloaded nose stop, roll with a floor shim, length spread in a gang push, the
  post bed's true free length, silicone at Shore 50–70A in this explorer's own
  models, seated rear depth, pallet A's path, and the pre-formed contact at
  2.5 mm.
- **Accepted and written into the idea files:**
  - the insulation-mouth condition for every narrow crimper at 2.5 mm (i2, i1b,
    i2b, k6);
  - pass-2 loading limits in i2b (open wings only up to ~2.8 mm);
  - growth against a rigid nose stop (i2d), repaired by a 10–30 N preloaded stop;
  - clone-box roll above 5° (i2d), repaired by a floor shim;
  - length spread against a rigid backing blade (i6, i6b, i3, i2b), repaired by
    pushing to the first wall and finishing each contact with one tine;
  - the proof pull moved upstream of i6's target comb;
  - 0.32 mm (not 0.36) for 2.54 against 2.50 over an XHP-9;
  - the Shore-derived silicone modulus;
  - seated rear up to 1.8 mm inside the rear face (blade reach ~2 mm);
  - the carrier-pitch attribution in i2's crown;
  - the two crossing metrics and one 4P order for every family;
  - the board pin-order option.
- **New:** [k7](ideas/k7-pre-formed-contacts-crimped-in-the-cavity.md) (c6 +
  i2/K1, with the two-pass, strip and T4 spool branches) and
  [k8](ideas/k8-half-rows-crimped-then-sorted.md) (c1c + i6). The flag route
  (c6b + i2d), the JST reference lead (c2) and the closed ring (c6) in k6 went
  into existing files.
- **Where I disagree, in part:**
  - The critique holds that i2's camera-set tip rests only on copper set until
    the crimper arrives. The hump presser works 5–15 mm behind the dies, outside
    their footprint, so it can stay down through the stroke. The presser foot
    that must leave held Z, not Y. A sprung hold-down pad takes Z.
  - k7 keeps the hump presser down too, because the bore's 0.2–4 N grip is below
    the hump's possible 0.4–5.7 N elastic push at the low end.
- **Found myself** that i6b's post stiffness used an 8 mm free length that
  assumed support at the rear face. Unsupported, a post is free for ~15.6 mm
  from the front wall: 0.45 mm per N in steel, 0.9 in bronze. A support comb
  near the tips repairs it and makes the pin material irrelevant.
- **Found myself** that i6's backing blade must follow into the cavity mouths,
  since the housing's rear face passes the contacts' rears by up to 1.8 mm.
- **Found** that in i1b the spreader fingers already give ~0.5 mm, more than the
  widest clone wing's 0.33 mm shortfall at the insulation mouth.
- **Sketches:** new [`insulation-mouth.svg`](sketches/insulation-mouth.svg),
  [`k7-snap-in-the-cavity.svg`](sketches/k7-snap-in-the-cavity.svg),
  [`i6b-post-bed.svg`](sketches/i6b-post-bed.svg) and
  [`k8-pallets-then-sort.svg`](sketches/k8-pallets-then-sort.svg) (generator
  [`calc/sketch_wave3.py`](calc/sketch_wave3.py)). Updated labels in i1, i2,
  i2d, i3, i5 and i6.

## Ideas that changed how every arrangement looks

- **The feed-length rule** (wave 1). One-at-a-time insertion stores its travel
  as length; a gang push stores none.
- **A crossing is an order of placement** (wave 2). Later lies over earlier.
  Any pin map can be placed one at a time from a plane above into a plane
  below. Only arrangements with fixed levels care how many layers there are.
- **The lance condition is the contact's** (wave 2). Every anvil in the study
  and the hand tool share it.
- **The insulation mouth decides narrow crimping at 2.5 mm** (wave 3). A
  crimper narrow enough to pass a neighbour has a mouth narrower than the kit's
  open wings. A soft neighbour can give way; a crimped one cannot. Pre-forming
  moves the problem off the machine.
- **Every front stop must give way during coining** (wave 3). Hold until
  capture, then yield at 10–30 N, or reference from behind.
- **A gang push stops at the first wall** (wave 3). Contact lengths differ, so
  each contact is finished alone.

## Rejected directions, why, and what would revive them

- **A round tube around the wire as a guide into the cavity.** The box's
  diagonal is 3.09 mm, so a round tube needs ≥ 3.5 mm OD, wider than the 3.3 mm
  free between neighbour wires. Revive as a rectangular channel or U-channel.
- **Pushing the contact through the wire from a grip far behind.** Buckles
  within 1.2–3.9 mm at 3–25 N with the nose free. Revive only with the nose
  guided and a grip within ~3–8 mm.
- **Crimping in the row with any existing hand tool's jaw.** 3.3 mm free; jaws
  are several times that.
- **Post continuity alone as a latch check.** The box touches the post before
  the lance is home. Kept as cavity identifier; the tug or pull-back tests the
  latch.
- **A camera on the lance windows while the housing sits on a header.** The
  header covers the mating face. Choose per arrangement.
- **Loading contacts into a housing by vibration.** A jam generator
  [estimate]. Revive if hand-loading in i2b is the bottleneck, as a vibratory
  track ending at one cavity.
- **Odd-then-even crimping to avoid widening the pitch in i3.** The evens are
  back at 2.5 mm to their neighbours.
- **Two-level shuttles on rods for crossings** (wave 2). Shuttles on the same
  rods keep their order, and a conductor lifted out of its shuttle leaves an
  empty shuttle that blocks its neighbours from closing up (J7's GND shuttle
  sits between RB4's and CLO's). Replaced by i6's fixed target row filled by a
  carrier. Revive if shuttles can leave their rods.
- **A staging comb directly above the target comb** (wave 2). Its U-slots open
  upward block the conductor's way down. Replaced by conductors cantilevered
  from a root comb near the web, in a plane above the target row.
- **terminal-supply a6's post head delivering into i2d's stub** (wave 2). The
  head sits in front of the box, where the stub's front wall is. A post head
  can feed an open nest; the stub's own post version (i2d″) is the post route.
- **Interleaving crimp and sort in k6** (wave 2). The travelling head's lower
  jaw would reach down toward conductors already lowered. Crimp all, then sort.
- **Letting the hump presser lift before the crimp** (wave 3). The hump's
  elastic share can push the tip back with up to 0.4–5.7 N, and an open U holds
  nothing. Revive if a hump is pressed fully plastic and measured not to
  recover.
- **A rigid nose stop at the crimp** (wave 3). Barrel growth bows the transition
  against steel or dents PA6. Revive if the growth test shows no bow.
- **A rigid backing blade as the whole push** (wave 3). The longest contact
  bottoms first and the shortest may not latch. Revive if one lot's lengths
  measure within ~0.05 mm.
- **An unsupported post bed** (wave 3). The posts are free for ~15.6 mm and
  deflect 0.45–0.9 mm per N. Revive only with posts supported near the tips.
- **i6's proof pull behind the target comb on J4** (wave 3). Only ~7–8 mm of
  uncrossed wire is left next to the comb. Revive for straight looms, or with a
  grip that fits above and below there.
- **One-pass preloading of a whole housing, even with pre-formed contacts**
  (wave 3). The conductor step misses by up to 0.23 mm beside an open
  conductor-barrel neighbour. Revive if the conductor barrel is pre-narrowed
  without spoiling the crimp.
- **Parking pallet A down and back in k8** (wave 3). Its swing crosses the sorted
  conductors. Revive with ribbon orders that put every upper-layer conductor in
  row B and a pallet B that translates instead of swinging.

## Questions that stayed open

- XHP internal geometry: entry chamfer, cavity width, floor height, lance
  shoulder depth, and whether a 0.64 mm post passes along a cavity's axis.
- XH insertion and retention forces (KONNRA clone spec: ≤ 9.8 N, ≥ 19.6 N).
- Post grip of kit contacts on a 0.64 mm post.
- Kit contact transition t, lance length and root, and where its length
  tolerance sits (box nose to barrels).
- Silicone torsional stiffness and modulus (BNTECHGO states no hardness; the
  study uses Shore 50–70A, E 2.5–5.5 MPa by Gent).
- Whether a crimped contact can be gripped by its barrels and released without
  rolling.
- Conductor-barrel growth at the bottom of the stroke, and how it divides
  toward the box and the rear.
- What a pre-formed keyhole does to the final insulation crimp on 1.7 mm
  silicone.
- The contact length spread within one lot.

## Questions for Derek

1. **One side photo of a kit contact** under the ELP camera: lance root, lance
   tip, box rear, conductor-barrel front. It settles the lance condition (i2,
   k7, i2d), the stub depth, and whether the nose or the box shoulder is the
   better axial reference.
2. **The kit contacts' open insulation-wing width**, caliper on three. At
   ≤ ~2.3 mm a narrow crimper swallows them as they come; wider, K1 needs the
   neighbour pushed aside or pre-formed contacts (k7), and i2b and k6's 2.5 mm
   variant need pre-formed contacts.
3. **The SN-2549, looked at closely.**
   - Is its XH anvil a plain block where the lance hangs, or does it have a slot
     or step?
   - With a kit contact at one click, does the lance tip hang in front of the
     anvil's front face, and by how much?
   - Held closed against a light: are the jaw faces flush with the anvil's
     front edge?
   - Fully open: is the gap at the XH nest wider than 2.8–3.25 mm (a flag's box
     and lance)?
4. **Growth.** Five SN-2549 crimps with the box nose touching a feeler leaf held
   across the front of the nest, five with the nose free, side photos. Does the
   transition bow?
5. **Split length.** How long a split behind the housing is acceptable on a
   finished loom? i6, k6 and k8 want ~25–30 mm during the build on J4 and J7;
   5 mm crimp pitch wants 23–36 mm on J1.
6. **J4's 4P order.** Fix it as V5, IO25, 3V3, IO26 | GND, IO27, IO23 in
   `cable-assemblies.md`? It is the least-crossing order for the sort and for
   half-rows alike.
7. **J7.** Which 3P conductor is "third": the one beside the 5P or the far one?
   Does the 5P follow the reed column with GND at one edge?
8. **Board pin order.** Would a board revision of J4's (and J7's) pin order,
   making every loom straight across, be on the table? Or the J7 rewire that
   moves GND onto the 3P?
9. **Feel, on the 0.1 g scale.** The push force at the click, the tug that pulls
   a latched contact out, and how far inside the rear face a latched contact's
   rear sits.
10. **Contact lengths.** Five kit contacts from one bag, overall length by
    caliper. The spread decides how much the finishing tine does.
11. **A long header pin through an XHP-4** from the front post opening: does it
    come out the rear cleanly? (i6b)
12. **The closed insulation barrel** of an SN-2549 crimp on the ribbon, and of
    one JST ASXHSXH22K305 lead: width and height, against 1.95 × 2.4 mm.
13. **The marked edge.** Is it visible to a camera? Or is each loom's far end
    free to sit in a terminal block while its board end is made?
14. **One extra mating cycle per contact** (i5's header nest, i6b's posts):
    acceptable?
15. **Dies.** Keep crimping with the SN-2549 (i1, i2d, i3, i4, i5) or make
    narrow stepped dies (i1b, i2, i2b, k7)?

## Index of this explorer's files

- **Arrangements:**
  [i1](ideas/i1-lift-to-the-head.md) (branch [i1b](ideas/i1b-narrow-tooling-in-the-row.md)),
  [i2](ideas/i2-crimp-in-the-cavity.md) (K1; branches [i2b](ideas/i2b-preload-the-whole-housing.md),
  [i2c](ideas/i2c-cut-down-housing-locator.md), [i2d](ideas/i2d-locator-the-lance-never-touches.md)),
  [i3](ideas/i3-converging-shuttles-gang-push.md) (branch [i3b](ideas/i3b-staggered-row-one-push.md)),
  [i4](ideas/i4-gantry-hand-with-eyes.md),
  [i5](ideas/i5-person-inserts-on-a-sensing-nest.md) (K4),
  [i6](ideas/i6-sort-then-push.md) (branch [i6b](ideas/i6b-post-bed-through-the-housing.md)).
- **Combinations:** [k6](ideas/k6-one-gantry-crimps-in-the-fan-then-sorts.md)
  (force-and-form f4 + i6), [k7](ideas/k7-pre-formed-contacts-crimped-in-the-cavity.md)
  (change-the-question c6 + i2/K1), [k8](ideas/k8-half-rows-crimped-then-sorted.md)
  (change-the-question c1c + i6).
- **What insertion needs from the crimp:** [`handover.md`](handover.md).
- **Sketches:**
  [feed-length rule](sketches/feed-length-rule.svg),
  [pin-order crossings](sketches/pin-order-crossings.svg) (fewest crossings with
  the 4P's pairs free),
  [pin-map layers](sketches/pin-map-layers.svg) (pairs adjacent),
  [latch signature](sketches/latch-signature.svg),
  [insulation mouth](sketches/insulation-mouth.svg),
  [i1](sketches/i1-lift-to-the-head.svg),
  [i2](sketches/i2-crimp-in-the-cavity.svg),
  [i2d](sketches/i2d-stub-locator.svg),
  [i3](sketches/i3-converging-shuttles.svg),
  [i5](sketches/i5-sensing-nest.svg),
  [i6](sketches/i6-sort-then-push.svg),
  [i6b](sketches/i6b-post-bed.svg),
  [k7](sketches/k7-snap-in-the-cavity.svg),
  [k8](sketches/k8-pallets-then-sort.svg).
- **Numbers:** [`calc/insertion_geometry.py`](calc/insertion_geometry.py)
  ([out](calc/insertion_geometry.out.txt)),
  [`calc/exchange_hand_tool_as_press.py`](calc/exchange_hand_tool_as_press.py)
  ([out](calc/exchange_hand_tool_as_press.out.txt)),
  [`calc/exchange_terminal_supply_w3.py`](calc/exchange_terminal_supply_w3.py)
  ([out](calc/exchange_terminal_supply_w3.out.txt)),
  [`calc/wave2.py`](calc/wave2.py) ([out](calc/wave2.out.txt)),
  [`calc/wave3.py`](calc/wave3.py) ([out](calc/wave3.out.txt)); sketch generators
  [`calc/sketch_pin_map_layers.py`](calc/sketch_pin_map_layers.py),
  [`calc/sketch_i6_sort_then_push.py`](calc/sketch_i6_sort_then_push.py),
  [`calc/sketch_wave3.py`](calc/sketch_wave3.py).
- **Amazon items:** [`sourcing-requests.md`](sourcing-requests.md).
- **`summary.md`** is rendered by the coordinator from the structured return.
