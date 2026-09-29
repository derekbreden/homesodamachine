# c1b — Tack first: a light machine places and pins every contact; the heavy crimp comes after, anywhere

Branch of [c1](c1-half-rows.md). A sibling, [c6](c6-pre-form-the-contact.md),
reaches the same flag without a tack stroke on the wire. The tacked row crimped
in its own pallet is [c1c](c1c-crimp-in-the-row.md). Other explorers' tack
stations: force-and-form [f9](../../force-and-form/ideas/f9-tack-station-feeds-crimp-station.md),
machine-that-sees-and-learns [v8](../../machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md),
hand-tool-as-press [a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md)
and [a6c](../../hand-tool-as-press/ideas/a6c-flags-by-machine-foot-crimp.md).
Sketch: [`../sketches/c1b-tack-first.svg`](../sketches/c1b-tack-first.svg)
(schematic). Numbers: [`../calc/ctq.out.txt`](../calc/ctq.out.txt) [ctq §n];
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) [w2 §n]; hand-tool-as-press's
[`exchange_ctq_w3.out.txt`](../../hand-tool-as-press/calc/exchange_ctq_w3.out.txt) [htq §n].

## Picture it

**Where things start.** As c1, steps 1–4: the ribbon is clamped, stripped
flat and split into two planes; plane B is parked; pallet A, loaded with open
contacts at 3.4 mm, sits under plane A; the presser comb has laid every
conductor into its contact; the camera has checked the lay. "Fixed" is the web
clamp's frame, which carries the pallet's datum.

**The tack.**
- A **tack comb** comes down on the half-row: a steel plate ~1.2–1.5 mm thick,
  as thick as an insulation barrel is long [estimate from clone drawings,
  xh-facts §1], with insulation-crimp profiles along its bottom edge.
- **Two passes with wide contacts.** Each profile's flared mouth must catch the
  open wing tips, so it is as wide as the open wings. At 3.4 mm the steel left
  between neighbouring mouths would be 0.15 mm for worst-case clone wings,
  0.6 mm at nominal [terminal-supply exchange calc §3]; a laser-cut plate
  cannot hold a 0.15 mm tooth. So the comb carries profiles at **6.8 mm** and
  tacks the odd positions of the half-row, shifts 3.4 mm, and tacks the even
  ones. Teeth are then ≥3.5 mm wide, and the second pass works beside
  neighbours already tacked narrow. With contacts no wider than ~2.8 mm, one
  pass at 3.4 mm is enough.
- Under the insulation barrels the pallet carries a **steel anvil strip**, a
  ground bar with a shallow saddle per pocket. A printed carrier cannot take
  it: 132 N on ~2.3 mm² is ~58 MPa, above PETG's yield [ctq §5].
- The comb closes each insulation barrel to a **deliberately loose** tack
  height set by a hard stop, looser than the final insulation crimp, so the
  final die finishes it rather than fighting it.
- **What drives it and carries the force.** 33–132 N per barrel, 66–660 N
  for a half-row of two to five [ctq §5], closing through comb, contacts,
  anvil strip and the pallet's frame. Any of these delivers it:
  - a printed lever;
  - a NEMA 17 with an integrated Tr8×2 lead screw (Iverntech 42HD6039-05,
    Prime-confirmed, $27.99 [sourcing/amazon-prime.md]);
  - the person's hand on a toggle clamp (POWERTEC 305CM, Prime-confirmed,
    $18.25 a pair, 500 lb [sourcing/amazon-prime.md]).
- The conductor barrels are untouched and stay open, the strands lying in them,
  held down by the tacked insulation behind.

**What comes out.** The pallet opens and the half-row lifts clear. Each
conductor carries its contact like a **flag**: axial position set by the tip
stop and pocket, roll set by the pocket, held by the tack's grip on the
silicone. Row B follows. The ribbon end leaves with every contact tacked on.

**What the tack has to hold.**
- The grip of a loose tack on a 0.49 mm silicone wall spans ~0.1 N to ~50 N,
  depending on the silicone's modulus, the squeeze (0.05–0.2 mm), confinement,
  barrel length and friction; a middle case is ~2 N [terminal-supply exchange
  calc §7]. force-and-form's thin-layer model gives 0.4–9 N at 10–30 %
  squeeze [force-and-form wave-2 calc §5].
- What the next step asks of it: its own weight, 0.4 mN; a keyed slot,
  0.1–0.5 N; a push onto a 0.64 mm post, 0.2–1.6 N [terminal-supply calc §7].
  So a tacked flag goes into a slot-type locator at almost any grip in the
  range and may slip on a post. The heavy crimp's locator is a slot.
- A person pushing the flag's jacket against a stop exceeds the low end of
  the range before feeling anything, so a hand crimp station says "at the stop"
  with a lamp (below).

**The heavy crimp, four ways, all outside this machine.**
1. **By hand, in the SN-2549 with a flag seat.** The flag cannot enter the nest
   from the front face, because the loom trails behind it; it enters box-first
   from the wire side, through the open jaws. Dragged on the anvil, its lance
   (0.6–0.9 mm proud, tip rearward) folds on the jaw's edge at 1–5 N and the
   contact stops while the jacket keeps moving [htq §4]. So the flag is carried
   level on a sprung seat at 1.1–1.7 mm above the anvil (a rear U on the
   jacket, a keyed slot for box and lance in front) to a leaf stop that lights
   a lamp; then Derek squeezes. That needs the SN-2549 to open 3.6–4.4 mm at the
   nest for a tacked flag [htq §4, via hand-tool-as-press's
   [flag seat](../../hand-tool-as-press/sketches/flag-seat.svg)]; box plus lance
   alone is 2.8–3.3 mm [xh-facts §1]. The seat is c6b's
   ([c6b](c6b-by-hand-this-week.md)); a6c closes the tool by foot.
2. **With JST's locator.** A WC-110 [mfr S6, S7] takes the contact by its box in
   the flap locator. $536.51 at Digi-Key, 147 in stock [xh-facts §2].
3. **By machine, one flag at a time.** force-and-form
   [f9](../../force-and-form/ideas/f9-tack-station-feeds-crimp-station.md): a
   knee press with a keyed steel nest (slot, lance relief, front stop), a
   carriage lowering one tacked contact into it while a fork holds the tacked
   neighbours aside.
4. **In the row, in the same pallet.** Tacked neighbours are ~2.0–2.2 mm wide,
   so a single-nest punch fits between them at 3.4 mm with no lift:
   [c1c](c1c-crimp-in-the-row.md).

**How it knows it worked.** The camera after the tack: every insulation barrel
closed, the conductor barrels still open, strands inside every U. A light pull
on the web clamp: the pocket shoulders react it, and a contact that slides
shows on camera. The heavy crimp's own checks happen wherever it happens.

**What the person does.** As c1 for loading and routing. The tacked end then
goes to the heavy crimp: by hand at ~10 s per contact [estimate], or into a
station.

**Steps covered:** split, place (a whole half-row in one motion), tack (fixes
contact to conductor). **Hands back:** the conductor crimp, insertion,
loading pallets, the J4/J7 crossings, and stripping.

## Why the split is at the insulation barrel

- **The insulation crimp is the forgiving one.** J.S.T. UK gives the insulation
  width ±0.10 mm and leaves the height "dependant on the specification of the
  wire used" [mfr S13, S14]. It carries no current. A steel tack plate cut to
  ±0.1 mm is adequate for it [estimate]; it would not be for the conductor
  profile.
- **The pitch-tight part is the placement.** A gang of profiles is one plate;
  at 6.8 mm per pass its teeth are wide.
- **The force-heavy part does not need pitch.** Once each contact is pinned to
  its wire, the heavy crimp can happen one at a time in a die of any width.
- **Tacking the conductor wings instead** grips mechanically, so the contact
  cannot slide or roll, but costs ~180–580 N per contact and may not re-form
  into a proper B in the final die. force-and-form's
  [f3b](../../force-and-form/ideas/f3b-two-station-forming.md) develops it.

## Does a tack before the conductor crimp change the crimp?

- JST's two-step hand tools form the conductor barrel first, then the
  insulation barrel [force-and-form f9]. A single-stroke tool does the
  opposite: the SN-2549, and any punch whose insulation section closes higher
  than its conductor section, touches the insulation wings first, 0.65–1.7 mm
  of die travel before the conductor die touches anything [htq §3, edge model,
  estimate]. A tack looser than that mid-stroke state is a state every
  single-stroke crimp passes through.
- So the question is confined to tacks tighter than that point. The physics of
  the risk there: coining lengthens the conductor barrel and extrudes the
  strand bundle both ways; rearward extrusion goes into the ~0.4 mm window
  between the barrels. With the jacket already held tightly, the strands in the
  window can bow instead of pushing the jacket back.
- The check: cross-section and pull-test ten contacts done each way, one arm of
  force-and-form's f3b sectioning experiment.

## Printed and bought

**Printed:** everything of c1 except the ram and punch; the tack comb's holder
and lever.

| Part | Source |
|---|---|
| Tack comb: 1.2–1.5 mm stainless or spring-steel plate, profiles at 6.8 mm, laser-cut or wire-EDM'd | laser-cut sheet services; quick-turn wire EDM at ±0.05 mm (JLCCNC, Xometry) [force-and-form source]; not priced. Or the insulation section cut from a spare SN-2549 jaw, so the tack is the SN's own stroke paused (hand-tool-as-press a4c) |
| Anvil strip: ground flat stock, or a 3 × 3 mm HSS blank | Prime-confirmed, five × 200 mm for $9.99 |
| Lead-screw motor or toggle clamp | Prime-confirmed, above |

## Problems worked through

1. **A tack on soft silicone will not hold the contact square.** A slot locator
   at the heavy crimp squares roll from the box and asks only 0.1–0.5 N;
   tacking nearer the final height raises the grip; carrying the half-row to
   the crimp still in its pallet (c1c) makes the grip irrelevant. The grip on
   this ribbon is measurable in an afternoon with the bench scale and a hook.
2. **The final die re-crimps the insulation barrel; does it cut the
   silicone?** Only if the tack was already tighter than the final profile. The
   tack's hard stop is set looser on purpose.
3. **Why not tack with a hand tool?** A hand tool tacks one at a time and needs
   the contact already placed and held, which is the hard part. The value here
   is a whole half-row placed by the presser comb and pinned before anything
   lets go.
4. **The tack comb's teeth are a knife edge at 3.4 mm** with worst-case clone
   wings: hence two passes at 6.8 mm.

## Contribution

- It makes "place the contact on the conductor" a machine of its own: light
  forces (under 700 N), mostly printed parts and a sheet-steel comb, no
  hardened die geometry and no crimp-height precision.
- It can be built and used before any crimp machine exists, with Derek
  crimping by hand against a seat and a lamp.
- It narrows every open contact to ~2.0–2.2 mm, which lets c1c crimp in the
  row.

## Major unresolved problems

- **Tack grip on silicone** is unknown across more than two orders of
  magnitude (0.1–50 N). It decides whether a flag can be handled loose.
- **Tack-first crimp quality** for tacks tighter than the single-stroke
  mid-point: sectioning.
- **The SN-2549's opening** at the nest must pass a flag carried on a seat
  (3.6–4.4 mm), and a seat on the jaw's front face must leave the jaws' travel
  free. Unmeasured.
- It inherits c1's J4 and J7 crossings and its split-length question.

## What rests on assumptions

- Insulation forming at 33–132 N per barrel: the facts-pass estimate [calc C1
  §4], not a measurement.
- That laser-cut sheet holds ±0.1 mm on a small profile [estimate].
- The pull and roll behaviour of a tacked contact [assumption].
- The SN-2549's insulation-first window [htq §3, estimate].
- The two-step tool order as force-and-form reports it; the tool manuals were
  not read here.
