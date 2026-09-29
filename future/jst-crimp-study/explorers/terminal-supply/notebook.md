# Notebook — terminal-supply

## Log, wave 1 (2026-09-28)

1. **Read** the brief, shared context, working method, xh-facts, prior-art, and
   `hardware/assembly/cable-assemblies.md`.
2. **Supply as three machines.** Carrier strip, loose, person-loaded fixture.
   A fourth appeared while working: the housing itself as the fixture.
3. **Carrier pitch.** xh-facts leaves pitch at 7–9.5 mm.
   - Rendered the HDGC and DLL clone drawings. Their plan views scale to
     ~7.0 mm and ~8.5 mm; they are not to scale.
   - Found a dimensioned analog: Würth WR-WTB 2.50 mm female crimp contact
     646 101 137 22 (AWG 28–22), drawing sheet 1/3. It gives:
     - pitch 7.10 mm;
     - carrier 3.00 mm;
     - pilot holes Ø1.50;
     - 1,000-piece reel Ø200 mm on a 100 mm hub, 22 mm wide (sheet 2/3).
   - Its box is not XH's (1.45 wide against 1.85), so it is an analog for
     the strip only.
   - Source:
     https://www.we-online.com/components/products/datasheet/64610113722.pdf.
     The 100-piece bag variant 64600113722DEC is "bulk/loose delivery in a
     bag".
4. **Carrier side.** Confirmed from the HDGC and DLL side views that the
   carrier joins the contact at the rear of the insulation barrel, in the
   floor plane. The wire must cross the carrier to reach the barrels. That
   single fact decided three things in a2:
   - pins go in the neighbours' holes;
   - the tab is sheared by dropping the carrier;
   - the hold-down is kept off the station.
5. **JST MKS-L manual.** Read the MKS-L side-feed applicator instruction
   manual. JST Sales America, 27 pages, "The Quality Connection". A copy was
   in this session's scratch folder, fetched by an earlier pass; its public
   URL was not recorded. Facts used:
   - 6.4 kg;
   - feed distance 30 mm maximum;
   - shut height 160 mm for AP-K2N;
   - pre-feed cam;
   - crimp dials ~0.05 mm per graduation;
   - bell-mouth set by moving the feed plate;
   - the pressure plate keeps the strip from moving back;
   - the scrap cover collects cut carrier pieces;
   - bend-up, bend-down, twist and roll trace to feed position and anvil
     position.
6. **Posts.** A female contact's box is made to grip a 0.64 mm post, which
   led to a4 and a4b. No JST document gives per-contact mating or unmating
   force.
   - A search summary quoted Molex KK 254 (PS-10-07-001): 200 g minimum normal
     force and 57 g minimum unmating on 0.64 mm posts.
   - The Molex PDF timed out and was not opened.
   - Kept as a secondhand bracket.
7. **Screw presenters.** Price and rail evidence:
   - eBay ~$123–189;
   - ATO $369.38 (rail "bite-wing ~0.5 mm larger than thread", 200–220 cc
     hopper);
   - Hakko AT-1050 $630.17.
8. **Harbor Freight 1-ton arbor press.** $79.99, member $54.99, 2,000 lbf.
9. **Web search budget.** Exhausted for the session near the end. The MKS-L
   manual's URL and OTP knife-set prices could not be searched further.
10. **IDs.** Renumbered to one main arrangement per supply mechanism (a1–a5)
    with lettered branches.

## Log, wave 2 (2026-09-28)

1. **Read** the critique by machine-that-sees-and-learns
   (`../../exchange/machine-that-sees-and-learns--on--terminal-supply.md`), the
   wave-1 digest and every explorer's summary. No web search this wave.
2. **Accepted from the critique, with physics checked:**
   - a2 Break 1 (other conductors land on fresh contacts): reproduced in
     `calc/wave2.py` §1. No 4P or 5P fan clears at 7.1 mm.
   - a2 Break 2 (one taught Y): accepted. The taught position becomes a
     starting guess, and the insulation edge as seen steers.
   - a2 Break 3 (drop-shear kinks the carrier next to the next contact):
     accepted. With the upstream carrier clamped just upstream of the station
     tab, the kink ends up in scrap after the next index (§9).
   - a2 Break 4 (the grazing view meets the next contact): accepted; the vane
     for a2, the crown for a2d.
   - a2b's tag pull (eccentric, bends the tab) and hole-versus-box-tip:
     accepted. Added a two-point grip (pin in the hole, fingers on the
     crimped insulation barrel) to take the neck out of the loop.
   - a2c's ±90° swing twists the strip: accepted. Added a third place to cut:
     after capture and before the wire.
   - a3b's punch along the rail: accepted the turning-pocket repair; the
     shuttle anvil is kept as a variant.
   - a4's nozzle cannot load a post: accepted. The loading nest in a4, and a6
     as the idea carried to its end.
   - a5's pivot in the mouth: accepted the pivot, with one disagreement
     written into a5. The droop before the anvil arrives costs nothing; what
     matters is the anvil's height against the cavity's floor line, within
     the mouth's clearance. A self-locking 2–3° wedge sets it per cavity (§8).
3. **Found while repairing:** the carrier's pilot holes belong to the carrier,
   not the contacts. Removing every other contact therefore keeps every hole,
   halves the neighbours, and costs $35–85 over the program at LCSC or
   Digi-Key reel prices (§7). With a crown of R 25–30 mm (elastic), the next
   kept contact's wing tips fall 0.5–1.2 mm below the station plane (§2).
   Wrote a2d.
4. **Found while repairing a2c and a6:** cutting the carrier before any wire
   exists removes the reason for every drop-shear in the study (the wire lies
   over the tab). It needs the contact held by something other than the
   carrier at that moment: a captive click in a hand tool, or a post in the
   box.
5. **New direction, a6:** the post as a travelling gripper, which makes the
   die the same whatever the supply. Box-front datum, stripper sleeve, Z float
   as the hold-down, silhouette on the post. The pin protrudes 1.5–1.8 mm so
   its tip stays inside the 2 mm box; the a4 and a4b numbers were brought in
   line.
6. **Combination x1:** a6's head feeding hand-tool-as-press a1's SN-2549
   cradle, and the post pen as its motorless form.
7. **a7:** what a switch to genuine SXH strip changes, arrangement by
   arrangement (about 75 arrangements, read from wave-1 summaries).
8. **Sketches:** `sketches/make_sketches_w2.py` draws a2d and a6 (with x1 as
   panel 3).
9. **a1 corrected:** the Harbor Freight 1-ton arbor press opens 139.7 mm,
   too short for an OTP applicator (force-and-form f2b's finding). a1's
   frames are now a steel O-frame with a ball screw, b1b's crank in the
   VEVOR frame, or f2's crank press.
10. **a5 staging:** a horizontal housing is staged by a post that takes the
    contact from a shuttle nest and pulls it 1.5 mm into the mouth; the
    gravity variant (rear face up) makes the crimp a3b's turned crimp.

## Log, final pass (2026-09-28)

1. **Read** into-the-housing's reading of this explorer
   (`../../exchange/into-the-housing--on--terminal-supply-w3.md`) and its calc
   (`../into-the-housing/calc/exchange_terminal_supply_w3.out.txt`). No web
   search; no Amazon.
2. **Accepted, with the physics checked in `calc/w3.py`:**
   - Post capture is set by the box entry (0.60–0.70 mm), not the box inside:
     ±0.08–0.31 mm by chamfer. The wave-2 figure (±0.4/±0.6) is withdrawn [w3 §1].
     A camera-steered head needs ±0.04–0.07, so aim is not the problem.
   - Height is: a barrels-up contact rocks on its lance on a flat floor, nose up
     or down, and its entry stands 0.9–1.7 mm high. A lance groove 1.0 wide and
     ≥ 1.0 deep along every bare-contact pocket (a4, a4b, a5, a6, x1, x3, a4c)
     [w3 §2].
   - a6's float must go down as well as up: ±0.2 mm in Z, preloaded from above.
   - a5's push is 5.25–5.45 mm, not ~4.5; a4b's is 13.95–14.45 mm. One-at-a-time
     seating stores that in conductor k as a 6–8 mm or 11–15 mm hump [w3 §3].
   - The web clamp must ride the housing's stage once a contact latches.
   - The waiting side of a5 and a4b meets 3.5–4.0 mm punches: lift it, or narrow
     dies.
   - a5's flat-anvil window is ~0.06 mm on its own numbers; about half the clone
     range needs a lance slot [w3 §4].
   - The floating nest replaces a5's per-cavity wedge; the wedge keeps a one-time
     use.
   - a2d's punch-holder rule counts the crimped neighbour's box (half 0.98), not a
     conductor: p ≥ 2.5–2.8 mm for 2.5–3.0 mm blades [w3 §5].
   - Seat pull 5 N, not 10 [w3 §9].
   - a2b's tag cannot enter 1.5–1.6 mm wire combs.
3. **Found while checking:**
   - With a narrow blade, a flat skip-2 strip (no crown) already lets 4P and 5P
     lie flat (p 2.5–2.8 ≤ 2.9); the crown adds the level view, the hold-down and
     any width [w3 §5].
   - Gravity staging into a rear-face-up housing stops at the lance (~2.4 mm), too
     deep for an anvil; the post as a depth stop fixes it (a3, a5, x3).
   - "Web follows the push" is a third way to supply a5's and a4b's stored length;
     strand fatigue is not the limit (hundreds of bows), the waiting conductors are.
   - Any stagger in Y between neighbours at the crimp is stored in the finished
     loom by a single push [w3 §3].
   - Stage depth is a dial from x3 (1.5 mm inside the mouth, 5.3 mm push) to a4c
     (7.5 mm out on posts, 14 mm push).
   - Lance tip: xh-facts' table says 2.4–2.6 mm; into-the-housing used 2.24–2.64.
     Both ranges give the same conclusion (flat anvil fits about half); stated in
     the files.
4. **Combinations developed:** x2 (a2d + i6 + a6's head, into-the-housing's T1,
   with loose, tag and post-bed branches); x3 (a5 + i2b, T2); a4c (a4b + i6b +
   i2b's order, the repair a4b's stored length pointed to). T3 (stub pen) went into
   x1 as a variant; T4 into a3 and x3 as a supply; T5 into a2d; T6 into a4b; T7
   into a6.
5. **Settled every idea file** to read cold: Picture it first; what locates what
   and the reference for fixed; force; how it knows; steps and hand-back; problems
   with repairs; unresolved; what each conclusion rests on. History phrasing
   removed; other explorers attributed by link.
6. **Sketches:** stale labels fixed in a2, a2b, a4, a4b, a5 (`make_sketches.py`)
   and a2d, a6 (`make_sketches_w2.py`); new x2, x3, a4c
   (`make_sketches_w3.py`).
7. **a7** updated: into-the-housing's rows; this explorer's new ideas; a table of
   arrangements added later across explorers; pre-formed contacts (c6) as a
   fourth supply.

## Rejected or parked directions

- **Make my own carrier: tape loose contacts to Kapton, SMT style.**
  - Why parked: the tape would have to hold a 0.04 g part square and let it go
    under a die. A post (a4) does both better, and is conductive.
  - Revive if post grip turns out too weak or too variable on the kit
    contacts.
- **A stick magazine with contacts nose to tail** (an end-feed imitation).
  - Why parked: an open-U contact's box nests into the previous contact's
    insulation U at no repeatable depth, so the stick has no pitch.
  - Revive as a buffer between a3's rail and a station, if the rail's rate is
    uneven.
- **Vacuum pick on the box's top face.** The box top is a flat ~1.85 × 2.0 mm;
  a 1 mm nozzle could lift 0.04 g, the LumenPnP way [prior-art §3].
  - Why parked: a post does the same pick and also locates, holds for the
    crimp and gives continuity.
  - Revive if a post cannot reach a contact presented on its side.
- **Magnetic handling.** Phosphor bronze is non-magnetic, and the clones'
  nickel underplate is micrometres thick. Rejected.
- **Insert a whole comb** (a2b) into the housing at once.
  - Why rejected: carrier pitch ~7.1 mm against housing pitch 2.5 mm.
    Coplanar neighbours hit the housing's rear face.
  - Kept: the comb as a transport object.
- **Stage every contact in its housing at once** (a5). Rejected: open clone
  wings 2.46–3.0 mm wide collide at 2.5 mm pitch, and ordinary dies cannot fit
  between staged neighbours. Every other cavity at once, with narrow stepped
  dies for the second half, is x3 (and a4c on posts). Revive every cavity at
  once if genuine or pre-formed contacts are inside ~2.0 mm.
- **Thin cantilevered die walls** so a knife-set die fits between seated
  neighbours (a5). Rejected [ts §8]: 2,400–7,200 MPa in a 0.5 mm wall under
  100–300 N. Sweep the neighbours instead. into-the-housing's and
  force-and-form's narrow stepped crimper is a different case: 0.8 mm walls
  (~940 MPa at 100 N as a cantilever) that land on the anvil's shoulders, so
  they are held at both ends at the bottom of the stroke. x3, a4c and a5's
  narrow-die option rely on it; making it stays their open problem.
- **Laser-cut the tab** with the XLaserlab fibre laser.
  - Why parked: heat next to a fresh tin-plated crimp, and fume; the kW-class
    tool's low-power control is unknown [xh-facts §7].
  - Revive if drop-shear and bend-off stubs are out of criteria.
- **The 12-ton shop press** as the crimp drive. It is hand-pumped hydraulic,
  and nothing about it is automatic. Rejected for a machine; fine for a
  one-off test of force.
- **Hang genuine JST contacts on their lance** (a3). Parked: the lance is a
  spring and should not carry a vibrating part.

- **The critique's C3, a static hanging plate with a post from below**
  (a3's stepped slots in a flat plate, filled by brushing).
  - Why parked: a post rising from below into a contact hanging box-down
    lifts it, but the contact can then leave only upward, and the post only
    by an open-ended slot. That is a3's rail with its end pocket, not a plate.
  - a6 takes loose contacts from v4b's pocket plate, lying down, instead.
  - Revive if the pocket plate's pose odds are poor for kit contacts and a
    comb plate with open-ended slots proves easy to fill.
- **Crown with every contact kept** (R ~8 mm).
  - Why parked: it bends the carrier plastically at every contact that
    passes, which is a2's Break 3 repeated.
  - Revive if the carrier proves soft enough to take it without rolling the
    contacts, or if removing contacts is unwelcome.
- **A post head that stages a bare contact into a cavity mouth.**
  - Rejected: the pin occupies the box's front, the end that enters the
    cavity.
  - a5 stages instead by a post through the cavity pulling the contact in.
- **Two of three contacts removed (21.3 mm).** Kept as a number in a2d
  (≥4.8 mm clearance), not developed; 1.33 reels for the program.

- **Staggering neighbours in Y at the crimp** so each die has room, then one push.
  - Why rejected: one move seats the nearer contacts first and carries them on,
    so the stagger stays in the finished loom as a bow [w3 §3].
  - Revive with a two-phase push and a web that moves between phases.
- **The post head threading crimped contacts onto a post bed** (x2 with i6b).
  - Why rejected: the bed post and the head's pin both want the box front.
  - Revive with a head that grips the box from outside while its pin retracts
    just ahead of the bed post; not pictured.
- **Round 0.025 in music wire as posts.**
  - Why parked: the post's flats set the contact's roll; a round pin does not.
  - Revive where roll is set elsewhere: the post pen in the SN-2549's nest, where
    the jaws square the contact.
- **Per-cavity anvil wedge in a5.**
  - Why parked: a nest that floats ±0.2 mm in X and Z lets a fixed anvil set the
    line, with no per-cavity measurement [ith-w3 G].
  - Revive if the floating housing yields to the punch's lead-in instead of the
    barrels centring on the die.
- **Gravity staging with no depth stop.**
  - Why rejected: the contact slides to its lance's stop, ~2.4 mm, where the
    conductor barrel meets the face.
  - Revive if the kit housing's rear mouth has a counterbore that leaves anvil
    room at that depth (one look).

## Things other explorers may want

- **The carrier lies in the floor plane, behind the insulation barrel. The
  wire crosses it.** Any strip design must keep the space above the tab clear.
- **Pitch ~7.1 mm, Ø1.5 holes, 3.0 mm carrier** (Würth analog). A unit's
  contacts are 0.38 m of strip.
- **Inspect the waiting contact before the wire arrives.** Pre-feed plus dwell
  makes it free.
- **Hanging by the insulation barrel's lower edge** references the barrels
  within 0.4 mm. A carrier references them through a tab that varies
  ±0.15–0.2 mm.
- **A post through the target cavity** (a4b) and **staging the bare contact**
  (a5). Both are insertion ideas that come from the supply side.

- **Cut the carrier before the wire exists.** Once the contact is held by a
  captive ratchet click or by a post in its box, nothing lies over the tab, and
  a flush cut from above works. The stub length is then set from the contact's
  own rear edge as seen (a2c, a6).
- **A skip-pitch strip keeps every pilot hole.** Removing every other contact
  halves the neighbours for $35–85 over the program. The removed contacts are
  loose stock (a2d).
- **A crowned anvil** (R 25–30 mm, elastic) drops the next kept contact's wing
  tips 0.5–1.2 mm below the station plane (a2d, `calc/wave2.py` §2).
- **The post as a gripper** holds a contact by its own socket, and the
  stripper sleeve releases it anywhere (a6). Its Z float is also the hold-down
  on the anvil.
- **Anvil height per cavity by a 2–3° self-locking wedge** (a5, §8).
- **Genuine wings, if inside 1.95 mm, break every wing-as-head orienter**
  (a3, v4b) and make every-cavity preloading (i2b) possible (§10, a7).

- **A lance groove** (1.0 wide, ≥ 1.0 deep) along any pocket a bare contact lies
  in barrels-up; without it the contact rocks 8–22° on its lance [w3 §2].
- **Post capture is set by the box entry**: ±0.08–0.31 mm by pin-tip chamfer
  [w3 §1].
- **Crimp every contact of a housing at one Y** when one move seats them; any
  stagger is stored in the finished loom [w3 §3].
- **Stage depth is a dial** from 1.5 mm inside the mouth (5.3 mm push) to 7.5 mm
  out on posts (14 mm push): x3 to a4c.
- **A flat skip-2 strip** already lets a 4P or 5P lie flat beside a narrow blade;
  the crown adds the level view and any width [w3 §5].
- **The web can follow a one-at-a-time push** instead of storing length in the
  conductor; the waiting conductors, not strand fatigue, limit it [w3 §3].

## Open questions for Derek

- **Kit contacts:**
  - open-wing width, box size, lance height (one caliper session);
  - count per kit;
  - whether male headers are in the kits.
- **Real SXH strip pitch and pilot-hole geometry.** One Digi-Key 100 strip.
- **Post grip of a kit contact on a header pin.** A 0.1 g scale and a hanging
  weight.
- **Does a long header pin pass through an XHP cavity** from the front opening
  to the rear?
- **Where the seated contact's rear sits relative to the housing's rear
  face.**
- **Wave 2:**
  - Do the kit contacts have a tab stub at the rear of the insulation barrel?
    That would mean they were cut from a (probably clone) reel.
  - Bend one strip round a 50 mm bar and release it. Does it spring back
    flat? That is the carrier's temper, which sets a2d's crown radius.
  - One phone photo of an XHP-4 held against a flashlight, square-on from the
    rear. It settles a4b's straight line through the cavity and v6's lit
    square.
  - Twenty kit contacts on a light pad in one photo: open-wing and box widths
    for the whole bag, and pose odds for the pocket plate.
- **Final pass:**
  - One kit contact laid barrels-up on a card and photographed side-on: does it
    rock on its lance, nose up or nose down? It decides the lance groove in every
    bare-contact pocket.
  - One kit contact latched in a kit housing: how far inside the rear face is the
    box front, or how thick is the front wall? It sets every push after a crimp
    (a4b, a5, x3, a4c; into-the-housing i6b).
  - The SN-2549's XH anvil from the side: does it have a lance relief? And one
    kit contact side-on: where is the lance tip against the conductor barrel?
    Together they decide flat anvil or lance slot.
  - Are the Prime-listed 2.54 mm header pins really 0.64 mm square? One caliper
    reading.
  - How much split behind a housing is acceptable on a finished loom (9–26 mm in
    a2d and x2, plus i6's set step)?
