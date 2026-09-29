# force-and-form on into-the-housing

force-and-form reads a crimp as a small, slow sheet-metal forming operation. It
asks where the force loop closes, what sets the bottom of the stroke, and which
part is the reference at each moment. This file reads
[into-the-housing](../explorers/into-the-housing/summary.md)'s arrangements
that way: its ideas, its
[handover](../explorers/into-the-housing/handover.md) and its
[calc](../explorers/into-the-housing/calc/insertion_geometry.out.txt).

Numbers marked **[calc §n]** are in
[`../explorers/force-and-form/calc/on_into_the_housing.py`](../explorers/force-and-form/calc/on_into_the_housing.py),
with output in
[`on_into_the_housing.out.txt`](../explorers/force-and-form/calc/on_into_the_housing.out.txt).
Coordinates follow into-the-housing's own: Y along the contact, +Y toward the
mating face; X across the row; Z up, barrels open up, lance down.

---

## i2 — crimp in the cavity

[i2](../explorers/into-the-housing/ideas/i2-crimp-in-the-cavity.md) puts more
steel, force and reference into a few tenths of a millimetre than any other idea
here. Six conflicts, each with its repair, then two transfers.

### Break 1: the lance sits where the anvil's front edge is

- **The conflict.**
  - The XH lance hangs 0.6–0.9 mm below the floor, with its tip 2.44 ±0.20 mm
    behind the contact front [source S22]. That is 0.24–0.64 mm behind the
    box's rear end, under the transition and the front of the conductor
    barrel.
  - i2 puts a flat anvil top at floor level, its front edge 0.2–0.3 mm behind
    the housing's rear face.
  - With the box 1.4–2.2 mm deep and the lance still free, the lance tip lies
    0.04–1.24 mm behind the rear face: over the anvil [calc §1b].
  - i2's own sketch, measured at its stated 25 px/mm, puts the lance tip
    0.44 mm behind the rear face and 0.68 mm below the floor, and the anvil's
    front edge 0.24 mm behind it. The drawn tip is 0.20 mm inside the anvil's
    steel [calc §1a].
- **The consequence.**
  - The contact rests on its lance tip, with its barrels 0.6–0.9 mm above the
    anvil.
  - The punch meets them early. The stroke flattens the lance, which is the
    retention feature, and bends the transition. The result is a crimped
    contact that cannot latch.
  - A force-against-gap monitor sees "contact seated high": the curve rises
    0.6–0.9 mm early [calc §1c]. It sees the fault only after the lance is
    ruined.
- **A second unknown in the same drawing.**
  - The lance root is drawn 0.6 mm inside the rear face, so the drawn lance
    crosses the rear face 0.39 mm below the cavity floor.
  - Either the entry is already folding the lance, in which case its tip rises
    toward the floor and may clear the anvil, or the contact cannot reach that
    depth.
  - Which one is true depends on the entry chamfer under the lance, which is
    unmeasured.
- **Repair A: a lance relief.**
  - The anvil's front stops behind the lance tip, or is slotted under the
    lance, as applicator terminal tracks are [assumption: applicator
    practice].
  - The conductor-barrel floor must still sit on steel. That needs the
    transition t, from the box rear to the conductor-barrel front, to be at
    least lance tip + 0.1 − 2.0 = 0.34–0.74 mm [calc §1d].
  - i2 assumed t = 0.2–0.5 mm. The length budget from the drawn contact
    lengths and the estimated barrel lengths spans 0.3–2.3 mm.
  - With t ≥ ~0.8 mm there is a window with a relieved anvil: box depth
    1.4–2.4 mm. With t ≤ 0.6 mm there is none while the lance hangs free under
    the barrel front [calc §1e].
- **Repair B: let the entry fold the lance.**
  - Push the box in until the lance root is inside the entry, so the rear-face
    edge holds the lance up.
  - The folded lance also springs the box against the cavity roof. That grips
    the box and takes over part of the backstop's job.
  - It costs box depth, so the conductor barrel comes closer to the rear face,
    which is i2's other window.
- **What it leaves uncertain.** t, the lance root position, and the entry
  chamfer under the lance. Two observations settle them:
  - one kit contact photographed side-on under the ELP camera, showing lance
    root, lance tip, box rear and conductor-barrel front;
  - one contact pushed into one kit housing to i2's depth, photographed from
    the side.
- **Not only i2's.** Every anvil in the study has to stop short of the lance or
  relieve it: i1b's rising anvil, and force-and-form's own f3, f4 and f5 dies
  and harvested SN jaws closed straight.

### Break 2: two locators for one contact in X

- **The conflict.**
  - The PA6 cavity holds the box. The steel die centres the barrels: the punch
    flare captures ±0.15–0.3 mm with tens to hundreds of newtons at first
    touch [estimate].
  - The offset between cavity n's axis and the die axis has three sources
    [estimate], which total ±0.14 mm root-sum-square and ±0.22 mm worst case
    [calc §2]:
    - the printed nest, ±0.1 mm;
    - the XHP pitch accumulated to the ninth cavity, ±0.1 mm;
    - the lead-screw step, ±0.02 mm.
  - The box's play in the cavity absorbs ±0.025–0.125 mm per side.
- **The consequence.**
  - The rest goes into an S-bend of the transition or into the PA6 wall.
    0.1 mm over a 0.6 mm transition is about 18° [calc §2].
  - The same offset also comes off the 0.2–0.45 mm between the punch and the
    seated neighbour's wire (Break 3).
- **Repair A: steel is the master in X and Z during the crimp.**
  - The nest floats in X and Z on light springs and is located only in Y.
  - An anvil top shaped to the barrel floor (a shallow radius) centres the
    contact under the presser's load before the punch arrives. The box then
    drags the housing onto the die axis.
  - The seated neighbours' wires accept a 0.1–0.2 mm shift over 10–30 mm of
    free length.
  - The Z float also removes i2's need to trim the anvil top to the cavity
    floor per housing lot.
- **Repair B: look, then step.**
  - At load, the camera measures each cavity's X on the rear face, or a pin
    touches into each cavity.
  - The carriage steps to the measured positions, ±0.02 mm, and the nest stays
    rigid.
- **Left uncertain.**
  - Repair A: whether the presser's light load is enough for a shaped anvil to
    centre the contact.
  - Repair B: the camera's resolution on a white PA6 rear face.

### Break 3: the narrow punch fails at its walls, not its column

- **The conflict.**
  - i2 and its calc size the punch at 2.4–2.85 mm, with 0.3–0.4 mm walls
    around a 1.8–2.05 mm crimp. That is the insulation crimp's width.
  - The conductor crimp is ~1.5 mm wide [mfr S14 analog], and it is the one
    that takes 0.8–2.4 kN.
- **The column is not the limit.** A neck 2.9 × 1.4 mm and 4 mm long runs at
  ~600 MPa at 2.4 kN, with an Euler load of 21 kN [calc §3].
- **The walls are.**
  - Confined compaction pushes the channel walls apart at k × 800–1,160 MPa,
    over ~0.7 × 1.4 mm [assumption: k = 0.3–1.0].
  - 0.3–0.4 mm walls on the conductor crimper reach 2,200–9,450 MPa at
    k = 0.3–0.5, and crack.
  - 0.85 mm walls reach ~490–1,180 MPa at k = 0.3–0.5, and 1,630–2,350 MPa at
    k = 1. Hardened D2's transverse rupture strength is ~2,500–3,500 MPa
    [calc §3; estimate]. 0.7 mm walls reach 720–1,740 MPa at k = 0.3–0.5.
  - The insulation crimper, at 30–130 N, is comfortable with 0.4 mm walls.
- **Where 0.8 mm walls fit.**
  - The neighbour's wire is round, and the free width follows its section.
    Take the neighbour's centre ~1.05 mm above the floor [estimate].
  - The free width is 3.30 mm at the neighbour's equator (Z ≈ 1.05), 3.35 mm
    at the conductor crimp's roof (Z ≈ 0.85), ≥ 3.56 mm below Z ≈ 0.6, and
    5 mm below Z ≈ 0.2 [calc §3].
  - A conductor step of 1.5 + 2 × 0.8 = 3.1 mm therefore fits, with ~0.1 mm a
    side at the equator.
  - The insulation step can be 2.5–2.7 mm.
  - That ~0.1 mm is less than the X offset in Break 2, so the punch only fits
    once Break 2 is repaired.
- **Branch: the dies bottom on each other and brace the walls.**
  - The crimper's walls land on shoulders of the anvil block below the floor
    (Z < 0), where there is 5 mm of room.
  - This sets crimp height (Break 4). A small lip on each shoulder also pins
    each wall's lower end at the moment of peak lateral load.
  - Pinned rather than free, each wall's root moment falls by a factor of
    roughly 2–4 [estimate].
- **Branch: a sheath.**
  - A 0.1 mm stainless shim sleeve on springs, with a rounded lower edge,
    lands first and stays still while the crimper slides inside it. The
    crimper's sharp edges never scrape the neighbour's silicone.
  - At 3.1 + 0.2 = 3.3 mm it presses the neighbour's silicone aside by up to
    ~0.1 mm. Whether silicone tolerates that without tearing is untested.

### Break 4: "stops at a set bottom" through a screw

- **The conflict.** i2 drives the punch with the NEMA 23 through a ball screw,
  a lever or a cam, and the press "stops at a set bottom".
  - A commanded screw position is not crimp height.
  - A printed or light frame opens 0.2–0.85 mm at peak force and drifts with
    creep and temperature [force-and-form [`force_loop.out.txt`](../explorers/force-and-form/calc/force_loop.out.txt) §1–2].
- **Transfer: a geometric bottom.**
  - **Dies that bottom** (Break 3's branch). The surplus force must be capped
    near 1 kN, which is ≤ ~450 MPa on the wall ends [calc §3].
    - A slow drive with a load cell does that: stop on the slope jump, or use
      a spring or a current limit.
  - **A knee.** Its straight position lands the dies just touching.
  - With either, the anvil's wedge and its drop-and-rise need no repeatable
    height, and the frame's stretch costs only travel.
- **Where the steel loop closes.**
  - The loop must go around the wire band. It closes in a C-frame whose back
    is to one side of the row, with a throat of ~30 mm (XHP-9 is 24.8 mm
    wide [mfr S2]).
  - That C is force-and-form's [f4](../explorers/force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md)
    head, a fist-sized steel C with a knee inside, turned so its throat faces
    the row. Its loop opens microns.
  - The carriage's bridge from nest to ribbon clamp runs on the C's open side.
- **Per-crimp crimp height.**
  - A 0.001 mm indicator reads across the dies. After the stroke, the press
    re-touches at ~10 N [force-and-form [`metrology.out.txt`](../explorers/force-and-form/calc/metrology.out.txt) §1–2].
  - A narrow in-row die is new tooling. Its crimp needs this number more than
    any bought head does.

### Break 5: the saddle cannot correct the tip's Y

- **The conflict.** The saddle's path length sets the stripped tip's Y.
  - The hump multiplies any Z seating error into Y by 1.7–3.0 [calc §12].
  - 0.1 mm of sag error moves the tip 0.17–0.30 mm, which is the whole
    ±0.2–0.3 mm axial window.
  - The camera can see the error. i2 has no axis that corrects it, because the
    presser foot moves in Z.
- **Repair: the hump is a lever.**
  - The saddle is set so the tip starts slightly short.
  - Before laying the tip in, the presser presses the hump down by the amount
    the camera measured. About 1 mm of foot travel moves the tip ~2 mm in +Y.
  - Copper sets below a ~67 mm radius, so the hump stays where it is pressed.
  - The feed stored for the push shrinks by the same amount, so the hump needs
    that margin.
- **Left uncertain.** Whether silicone slides in the saddle groove as the hump
  flattens.

### Break 6: a contact slid along the anvil top rides on its lance

- **The conflict.** "A fresh contact slides along the anvil top, lance down."
  - The lance, 0.6–0.9 mm proud, drags across the anvil's crimping section
    before it reaches the relief (Break 1), and can hook the anvil's edge.
  - The crimping section cannot carry a lance groove: the barrel floor would be
    crimped down into it.
- **Repair: feed with the anvil down.**
  - The contact slides along a channel plate with a lance groove until its box
    is in the entry.
  - The anvil then rises through a slot in that plate, under the barrels.
  - The anvil already drops for the push, so this is the same axis used twice.

### Transfer: the backstop is a proof-pull fork

- The slotted backstop behind the insulation barrel is force-and-form's
  proof-pull fork. i2 already has it.
- After the crimp and before the push, the pads that do the latch pull-back
  grip conductor n and pull it −Y to ~20 N, half of JST's 39.2 N, against the
  backstop.
- It belongs here and nowhere later because of the force ladder [calc §7]:

  | Force | What it is |
  |---:|---|
  | 5 N | latch test |
  | ~14.7 N | lance retention (analog) |
  | 19.6 N | crimp proof pull |
  | 39.2 N | crimp pull-out minimum |

- After latching, a 20 N pull draws a good contact out of its cavity. In every
  arrangement the crimp proof has to sit between the crimp and the insertion.

### Transfer: the cavity as a terminal guide

- Crimping tends to bow a contact up or down (JST's bend fault). Applicators
  resist it with terminal guides [assumption].
- In i2 the cavity holds the box square while the barrels are formed. With
  Break 2's floats, the die centres the barrels without bending the
  transition.
- i2 then forms the straightest contact of any arrangement in the study. The
  handover's item 2 asks for exactly that.

### The strip route

- **The crown.** Bending the strip over a crowned block so the neighbour
  contacts drop 3.6–4.0 mm below the housing takes a crown radius of
  6.3–12.5 mm for a 7.1–9.5 mm strip pitch [calc §10].
  - Carrier strain is 0.8–1.6 %, which is plastic. The feed is one-way and the
    carrier is scrap after the cut, so that is acceptable.
  - The feed pawl works on an arc.
- **Tab cut at the bottom.** The tab shear has to act while the punch still
  holds the barrels at the bottom of the stroke (the applicator's floating
  shear).
  - Cut after the punch rises, the shear's 50–160 N [xh-facts §4] pulls the
    contact's rear down with only the cavity walls holding the box.
- **Branch: the housing goes to the strip.**
  - The lead contact stays on a pilot pin, and the carriage moves the housing
    −Y ~2 mm onto the box.
  - The strip then gives X, Y and roll, which the backstop and the entry
    otherwise supply.
  - It needs a Y axis on the carriage.

---

## i2b — preload the whole housing

- **Anvil drop.** A 1.0 mm drop leaves 0.1 mm under the tallest clone lance of
  a neighbour. A 1.5 mm drop is comfortable [calc §11].
- **Punch room, recomputed with the stepped crimper of i2 Break 3.**
  - In i2b every contact sits at one depth. At the conductor crimper's Y the
    neighbours are crimped conductor barrels (~1.5 mm wide, edge 1.75 mm from
    the axis), not 1.7 mm wires.
  - The 3.1 mm conductor step clears them by ~0.2 mm a side.
  - At the insulation crimper's Y, a 2.5–2.7 mm step against a neighbour's
    1.9–2.0 mm crimped insulation barrel clears by 0.15–0.3 mm.
  - i2b's own Repair A (odds, then evens) avoids open neighbours entirely.
  - So i2b gives the conductor crimper more room than i2 does. In i2 the
    seated neighbour's 1.7 mm wire sits at the conductor crimper's Y.
- **X registration** (i2 Break 2) applies with every cavity loaded. A floating
  nest moves every preloaded contact with the housing.
- **Proof pull.** A per-cavity pull needs a backstop behind each contact: a
  slotted comb, i2b's comb pusher turned around.

---

## i2c — cut-down housing as locator

- **The lance takes a set with every fold** [calc §8].
  - A 0.2 mm bronze lance 1–3 mm long reaches first yield at 0.015–0.18 mm of
    tip travel. It stands 0.6–0.9 mm proud.
  - Folding it into any cavity is therefore partly plastic by design
    [assumption: the lance is about as long as the drawings suggest].
  - i2c adds three folds: a latch into the stub, a lift to release it, and a
    second latch into the product housing. Each costs lance height by an
    unknown amount.
- **Branch i2c′: a stub that never engages the lance.**
  - Cut the stub so that, with the box nose on the stub's front wall, the lance
    root is still outside.
  - The stub's walls hold X, Z and roll. Its front wall holds +Y, and a slotted
    backstop (the proof-pull fork) holds −Y.
  - After the crimp the contact leaves by a plain −Y pull. There is no lift pin
    and no XJ-06 motion, and the lance's first fold happens in the product
    housing.
  - It gives up the lance catch as the axial reference. The box nose on the
    front wall replaces it, and the contact's own box-to-barrel length carries
    the barrel position. That length is tight within one lot [assumption].
- **Branch i2c″: a steel pocket and a post.**
  - A pocket in laminated stencil steel, from the JLCPCB source into-the-housing
    found, with a 0.64 mm square post in its front wall.
  - The box mates onto the post as it will on the board, and its own spring
    holds it. This echoes the header-post hold in terminal-supply a4 and
    hand-tool-as-press a3.
  - Steel does not wear at a lance shoulder the way PA6 does.
- **Transfer back to force-and-form.** Either branch is the missing locator for
  [f1](../explorers/force-and-form/ideas/f1-motorised-ratchet-crimper.md)
  (SN-2549 in a cradle), in place of f1's printed keyed flap.

---

## i1b — narrow tooling in the row

- **"A rising anvil that must lock rigidly and repeat to ±0.02 mm."** It does
  not have to repeat if the dies set the bottom (i2 Break 4).
  - The crimper's walls land on the anvil block's own shoulders, so crimp
    height is the die pair's geometry. The anvil's lift only has to carry the
    force.
  - A knee under the anvil, straightened to lift it, carries the load through
    straight links and cannot back-drive. It is force-and-form's f3 knee
    turned upside down.
- **The anvil that "scoops" an open contact from below** carries it lance-down.
  The contact rides on its lance unless the anvil has the relief (i2 Break 1).
- **The punch** follows the wall rule of i2 Break 3: a 3.1 mm conductor step
  with ~0.8 mm walls, not 2.9 mm with 0.3–0.4 mm walls.
- **The loop** closes in a side-entry C, as in i2 Break 4.

---

## i1 — lift to the head

- **The head is force-and-form's f1 in practice.**
  - "The iCrimp closed one click by a servo on its handle" captures the
    contact. The crimp itself needs the whole stroke: an estimated 40–250 N at
    the handle ends for a 10–40:1 tool, over a handle travel nobody has
    measured [force-and-form [`drives.out.txt`](../explorers/force-and-form/calc/drives.out.txt) §E].
  - That calls for a linear actuator or lead screw on the handle, as in f1,
    not a hobby servo alone.
- **f1's ratchet problem transfers.** Once one click captures the contact, the
  ratchet cannot reopen without completing. A failed lay-in scraps the contact
  unless the release lever is reachable.
- **Leaving the jaws.**
  - The crimped contact cannot be drawn +Y along the nest. The crimped
    insulation barrel, 1.9–2.0 mm wide, does not pass the 1.5 mm conductor
    nest.
  - It leaves in Z with the jaws open, with a stripper if it sticks in the
    upper jaw (applicator practice), and then moves +Y.
  - With an applicator, the terminal stop and strip guide lie on the +Y side,
    so the path is up, over, then down.
- **A rigid grip through the crimp puts a permanent kink in the conductor.**
  - The anvil sets the barrel floor, and the gripper sets the wire 2–3 mm
    behind it.
  - Any Z or X mismatch of 0.05–0.4 mm forces an S-bend of 2.5–45 mm radius.
    Copper sets below ~67 mm [calc §4]. That is JST's bend fault, and it breaks
    the handover's "straight" requirement.
  - Repair: the fingers go loose in X and Z during the forming stroke, as a
    cage or as a flexure with a lock, and hold only in Y.
  - They then re-grip on the crimped barrel, which is i1's own roll repair 2.
- **A wire stop found by touch.**
  - A single 0.08 mm strand 2.1–2.4 mm past the insulation buckles at
    0.10–0.13 N [calc §5]. A ragged tip touches with a few strands first.
  - The load cell must stop at ~0.1–0.3 N, and drag along the barrel floor is
    the same size.
  - The camera's view of the insulation edge between the barrels is the
    stronger axial reference.
  - A light twist of the strands (as in force-and-form f3) stiffens the
    bundle.
- **Combination with [f2](../explorers/force-and-form/ideas/f2-crank-press-for-an-applicator.md).**
  - i1's gripper can operate an applicator in f2's slow crank press, the
    Kurabo pattern.
  - The applicator's pre-feed holds the contact open on its anvil and locates
    it. At the bottom of the stroke it crimps both barrels and cuts the tab.
  - i1 brings the lift and one grip for laying, carrying and pushing.
  - Uncertain: the applicator's base plate and body sit below its anvil. A row
    only 16–20 mm below the anvil top may collide with them, so the lift may
    grow or the row may come in from the side.

---

## i3 — converging shuttles, gang push

- **The fronts line up at the head, not at the stripper.**
  - i3 needs the fronts on one line to ±0.3 mm. As drawn they depend on clamp
    position, plus stripped length, plus where the head places the contact on
    the conductor (another ±0.2–0.3 mm).
  - Repair: during its crimp, shuttle n docks on a steel pin on the head, and
    the head's own locator places the contact (a strip pilot pin, or a keyed
    stop).
  - The contact front's distance to the clamp is then the head's geometry,
    ±0.03–0.06 mm on a strip pilot pin [force-and-form
    [`placement_budget.out.txt`](../explorers/force-and-form/calc/placement_budget.out.txt)].
  - The strip error lands where it belongs, inside the barrel window as
    bellmouth and brush.
  - What has to be on a line is the contacts, not the stripped edges.
- **Closing bends set, which helps.**
  - 13 mm of swing over 25–35 mm of free wire puts a bend of roughly 12–24 mm
    radius in J1's outer conductors [estimate, L²/4δ]. Copper sets it.
  - Once closed, the conductors hold their new shape and push nothing back
    against the guide comb. The finished loom carries the set fan.
- **The gang push is within the crimp's strength.** It loads each crimp in
  compression at 3–25 N through a clamp 2–4 mm behind the insulation barrel.
  That is inside both the crimp's strength and the buckling length
  [into-the-housing §1].
- **Proof pull before closing.** Right after its crimp, the shuttle clamp pulls
  the conductor at ~20 N against a fork on the head [calc §7].
- **Combinations K2 and K3** (below) build on i3.

---

## i3b — staggered push

- **The first crimps are loaded in compression** [calc §6].
  - The force path runs from the housing's front wall through box, contact,
    crimps and wire to a clamp 2–4 mm back.
  - With a 1 mm stagger, 36–70 N sustained is 92–179 % of JST's 39.2 N
    pull-out minimum. It pushes the way that drives the brush toward the box,
    and strands in the box are JST's fault.
  - At 60–70 N the 4 mm of wire between clamp and crimp also buckles; the
    K = 0.5 limit is 2.9–3.5 mm.
  - With a 0.3 mm stagger the peak is ~25–42 N, still 64–107 % of the pull-out
    minimum.
- **Repair: constant-force clamps.**
  - Flat coiled constant-force springs on each clamp, or hanging weights,
    which a slow machine can use. The load stays at the preload however far
    the clamp rides back.
  - Preload = 1.25 × the largest single insertion force [calc §6]:

    | Single insertion force | Preload | Share of pull-out minimum |
    |---:|---:|---:|
    | 12 N | 15 N | 38 % |
    | 15 N | 19 N | 48 % |
    | 25 N | 31 N | 80 % |

  - Derek's scale measurement under one housing (into-the-housing's question 4)
    decides whether i3b stands.

---

## i4 — gantry hand

- **Compliance during the crimp.** i1's kink applies to i4 too. The wrist
  flexure, ~5 N/mm in Y, is the right idea turned 90°: fingers compliant in X
  and Z during the forming stroke, stiff in Y.
- **The station.** The software-commanded crimp station is force-and-form's f1
  (motorised SN-2549 with a load cell) or
  [f3](../explorers/force-and-form/ideas/f3-knee-micropress.md) (knee press:
  pause at capture, re-touch height, proof pull).
  - f3's order suits a hand. The press captures the contact first, and the
    hand threads the conductor axially through a funnel.
  - The fingers never go into the die from above.
- **Combination K6** is below.

---

## i5 — the person starts each contact on a sensing nest

- **The crimp's own checks fit on this bench.** Every contact already passes
  through the person's hand here, so two checks can sit beside the nest for
  today's hand crimps:
  - **A proof-pull fork.** The person drops the crimped barrel into a steel
    fork on the load-cell base and pulls the wire until the ESP32 beeps at
    ~20 N. It happens before the contact is started into its cavity, never
    after [calc §7].
  - **A crimp-height pocket.** A point-and-blade anvil sits under a 0.001 mm
    indicator on a lever. The same ESP32 reads it through TouchDRO's
    protocols [force-and-form [`metrology.out.txt`](../explorers/force-and-form/calc/metrology.out.txt) §1].
  - Every hand crimp's height and proof load are then logged beside its latch
    trace. That is also the SN-2549 measurement the whole study is waiting
    on, taken during normal production.
- **The trace doubles as a lance check.** A lance flattened by crimp tooling
  (i2 Break 1) shows as a missing fold rise and snap.
- **Post grip against the tug.** A box's spring on a 0.64 mm post probably
  withdraws at ~0.5–2 N per contact [estimate], under a 5 N tug. Measure it as
  i5 proposes.

---

## handover.md

- **Item 3, "narrow enough", is an insulation-die dimension.**
  - A crude ellipse model of the closed insulation barrel on 1.7 mm silicone
    [calc §9, estimate]:
    - 1.90 mm wide stands 1.94–2.33 mm tall;
    - 1.80 mm wide stands 2.05–2.46 mm tall, over the 2.4 mm envelope unless
      the silicone extrudes along the wire.
  - Narrowing the insulation crimp makes it taller. The 1.7 mm silicone, near
    the top of XH's 0.9–1.9 mm range, nearly fills the cavity section.
  - Today's SN-2549 crimps enter the housing. Their insulation width and height
    by caliper are the target any machine die copies.
- **Item 5, "grip on the crimped barrels (flat)".** A B-crimp's top is two
  lobes with a cusp; its floor is flat. A flat pad on the floor and a pad
  shaped to the lobes on top hold roll.
- **Items worth adding:**
  - proof-pulled at ~20 N before the push (the force ladder);
  - lance intact: the fold rise is present in the insertion trace;
  - tab cut at the bottom of the stroke with the barrels held, ≤ one stock
    thickness.

---

## Combinations

**K1 — i2 inside a closed steel C (i2 + f4/f3).**
- **The arrangement.**
  - f4's fist-sized steel C, with a knee and a NEMA 17 inside, is fixed on the
    bench with its ~30 mm throat facing the housing carriage.
  - It carries i2's stepped narrow dies: a 3.1 mm conductor step with ~0.8 mm
    walls and a 2.5–2.7 mm insulation step. They bottom on shoulders of the
    anvil block below the floor.
  - The anvil has a lance relief and rises on its own knee.
  - The nest floats in X and Z. i2's backstop is the proof-pull fork.
  - One load cell sits under the anvil, and one 0.001 mm indicator reads
    across the dies.
- **What one station logs:**
  - the crimp force against the true die gap;
  - the re-touch crimp height;
  - the proof pull against the backstop;
  - through the pusher's cell, the insertion trace and the latch pull-back.
- **force-and-form brings:**
  - a geometric bottom in a short steel loop;
  - per-crimp height and pull;
  - the wall rule for narrow dies.
- **into-the-housing brings:**
  - a molded, $0.05 locator;
  - no transfer between crimp and insertion;
  - the feed-length rule;
  - latch sensing.
- **Left open:**
  - t and the lance (one photograph);
  - die making (quick-turn EDM at ±0.05 mm is coarse for 0.8 mm walls around a
    1.5 mm channel);
  - X registration.

**K2 — shuttles through a knee press, with i2's crown (i3 + f3 + i2).**
- **The arrangement.**
  - i3's shuttle base gets a Y slide. f3's strip-fed knee press stands beside
    the row at 5 mm pitch, its nose under ~6 mm wide in 8.3 mm of free width.
  - For shuttle n, docked on the press's pin:
    1. The press captures the lead contact, and the camera looks.
    2. The base moves +Y ~3 mm to thread the conductor through a funnel.
    3. The press crimps and re-touches.
    4. The base moves −Y to proof-pull against a fork.
    5. The tab is cut at the bottom of a stroke.
  - The contact fronts land on a common line to the pilot pin's ±0.03–0.06 mm.
  - i3's fan plate then closes the row, and the housing goes on in one push
    with no stored feed.
- **A conflict found by combining.**
  - Threading moves every conductor +Y. The uncrimped neighbours at ±5 and
    ±10 mm run into the unused contacts on the strip at ±7–9.5 mm.
  - i2's crowned block drops the unused strip 3.6–4 mm away: radius
    6–12.5 mm, strain 0.8–1.6 %, one-way [calc §10].
- **Contributions.** f3 brings the crimp: strip locator, capture then thread,
  height and pull. i3 brings the pitch change and insertion with zero stored
  feed.
- **Left open.** J1's split (i3's own problem), the strip pitch, and feeding on
  an arc.

**K3 — cassette, then fan plate (f5 + i3), for the 4P family.**
- **Scope.** Five housings, 38 % of crimps.
- **The arrangement.**
  - f5's cassette crimps a whole 4P end at strip pitch in one stroke of the
    shop press. The carrier holds every contact on one line, and the floating
    shear cuts the tabs.
  - The cassette's comb is i3's shuttle row. The ribbon end moves straight to
    the fan plate, closes to 2.5 mm, and the housing is pushed on.
- **Checks.** f5's summed force cannot name a failed station. i3's per-shuttle
  pull-back can, and so can a 20 N proof pull per shuttle before closing.
- **Split.** A 4P at 7.1–7.5 mm pitch moves its outer conductor ~8–9 mm, which
  needs 15–24 mm of split [into-the-housing §7]. J1 is too wide for this path.

**K4 — i5 + a crimp-height pocket + a proof fork.** A bench quality station
for today's hand crimps (see i5 above).

**K5 — f1 + i2c′.** A non-latching XHP stub is the contact locator in the
SN-2549 cradle.

**K6 — one gantry, two tools (i4 + f4).**
- The gantry carries both f4's closed-loop crimp head and i4's hand.
- The ribbon lies in a comb at ~5 mm pitch, and f4 crimps it there with no
  conductor carried to a station.
- The hand then carries each crimped contact to its cavity, up to ~5 mm of
  lateral travel for a 5P.

---

## What into-the-housing's view has not yet seen

- **Crimp quality is treated as the head's, "already understood" (i1).** For
  this ribbon it is not.
  - The SN-2549's crimp height on 1.7 mm silicone is unmeasured, and the narrow
    in-row dies of i1b, i2 and i2b are new tooling.
  - Every in-row arrangement needs the crimp measured where it is made:
    re-touch height and force against die gap.
- **Contact feed to the head** is handed to terminal-supply or the person.
  force-and-form's arrangements take it on:
  - a strip on a pilot pin with a pawl (f3);
  - a dispenser shear (f4);
  - an applicator's pre-feed (f2).
- **No arrangement proof-loads the crimp.** The force ladder puts that step
  between the crimp and the push.
- **The lance** sits under the crimp zone (i2 Break 1) and takes a set with
  each fold (i2c).
- **The insulation crimp's width and height** are the insertability
  specification.
- **Tab-cut timing:** at the bottom of the stroke, barrels held.

## Where their work changes force-and-form's ideas

- **Lance relief.** f3, f4 and f5 anvils, and harvested SN jaws closed
  straight, need one. The placement budget's ±0.1 mm axial window now also
  keeps the lance in its relief.
- **The feed-length rule.** f4 (5 mm comb) and f5 (strip pitch) crimp contacts
  off their seated positions, so insertion needs stored feed or a gang push.
  f5 leads naturally into i3's fan plate (K3).
- **The web clamp as the one datum.** f3's carriage clamp becomes the loom's
  web clamp, and threading depth is referenced to it.
- **f1's locator** becomes a non-latching XHP stub instead of a printed flap
  (K5).
- **f3's insertion push.** f3's note that "the same press can do the insertion
  push" becomes K1, a branch to develop.
- **J4/J7 crossings** need raised routes in f4's comb board and f5's comb.
- **2.5 mm pitch.** The 3.3 mm of free width and "grip above and below, never
  beside" apply to force-and-form's forks (f2, f3), which bend neighbours
  aside.
- **Order of checks.** f3's proof pull at ~20 N comes before insertion, and a
  tug of 5 N or less after.
