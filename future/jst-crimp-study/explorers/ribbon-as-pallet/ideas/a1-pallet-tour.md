# a1 Pallet tour: one clamp, one stage, a fixed strip-fed crimp station

## Picture it

Sketch: [`../sketches/a1-pallet-tour.svg`](../sketches/a1-pallet-tour.svg)
(schematic).

**Where things start.**
- A cut length of ribbon lies in a printed pallet about 90 × 50 × 20 mm, its
  marked edge (conductor 1) against the pallet's datum wall.
- A hinged lid with a TPU pad clamps about 25 mm of webbed ribbon. **The lid's
  front face is the loom's split root.**
- The rest of the loom hangs behind or coils in a cup. Its far end is pressed
  into the pogo block of [a6](a6-housing-as-last-comb.md), which gives the
  machine a wire to every conductor.
- The contacts start on their reel, **SXH-001T-P0.6 on carrier strip**,
  threaded into an OTP side-feed XH mini-applicator. The applicator stands in a
  slow crank press built around the idle VEVOR 12-ton press (borrowed-machines'
  [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)).
- A kit **XHP housing** sits in a printed nest.

**What moves.** The pallet is pinned to the carriage of a two-axis stage: Y
toward a row of fixed stations, X across it. Every operation is the pallet
driven against a fixed tool:
1. **Part.** The zip station ([a7](a7-zip-station.md)) tears each web back to
   the lid's front face, where the tear stops.
2. **Fan.** The stage pushes the pallet under a lever that presses a printed,
   per-loom **fan block** over the parted conductors. Its grooves take them from
   1.7 mm to a **crimp pitch of 5.0 mm** and hold them **h ≈ 5 mm above the
   anvil plane**. Each groove ends in a hinged **tongue** 10–12 mm long.
3. **Flush cut** at the tongue lips + 9 mm, with a razor guillotine. It comes
   after the fan because the fan pulls a 5P's outer tips back 1.65 mm
   [calc W2 §3] (order A in [a5](a5-part-fan-strip-in-the-pallet.md)).
4. **Strip.** The rolling ring scorer ([a8](a8-rolling-ring-scorer.md)) scores
   every conductor at once and tears the slugs off, 2.4 mm [mfr S6].
5. **Crimp, one conductor at a time.**
   - The stage brings conductor k over the contact waiting on the anvil
     (pre-feed [prior-art §3]).
   - A fixed cam at the station presses conductor k's tongue down 5 mm. The
     tongue's covered groove carries the conductor down, and its lip turns it
     back level, so the stripped tip lies along the barrel floor.
   - The camera looks, and the far-end port reads conductor k continuous to the
     grounded applicator.
   - The crank turns: the crimpers close both barrels and the shear cuts the
     tab. The crank **pauses** after the crimpers clear the contact and before
     the feed finger moves. The stage backs out 10 mm in −Y in that pause,
     drawing the crimped contact off the anvil. The crank finishes its turn and
     the feed brings the next contact.
   - As the pallet leaves the cam, the tongue springs up and lifts the crimped
     conductor back to h. The stage indexes 5.0 mm in X.
6. **Insert.** The fan block is swapped for a 2.5 mm closing block, and the
   insertion clamp of [a6](a6-housing-as-last-comb.md) puts the row into the
   housing and tests it.

**What locates what, and the reference for fixed.**
- **"Fixed" is the anvil.** The stage frame and the applicator base are one
  plate. The stage finds the anvil once per session with the camera on a
  contact.
- **Laterally:** the fan block and tongue place each conductor to about
  ±0.1 mm at the lip. The contact's open wings then capture what is left, from
  +0.5 mm a side down to ~0 depending on whether the clone drawings' widths are
  inside or outside widths ([P3 §2]; see [a2](a2-two-pallets-meet.md)).
- **Axially:** the flush cut at the lips, the strip line and the stage's Y set
  where the insulation lands. The applicator's wire stop is not used.
- **The contact:** the applicator's strip track, feed finger and hold-down.

**What drives the crimp and carries its force.**
- Ram → crimpers → contact → anvil → applicator base → press frame. Peak force
  is 0.8–2.6 kN; design to 3 kN [xh-facts §4].
- The pallet carries only the cam's push on one tongue.
- The press keeps the applicator's feed, so it needs the applicator's full
  stroke: a 15 mm crank. That takes 2.2–6 N·m, set mostly by the ram's return
  spring [P3 §5].
  - A NEMA 23 with a 10:1 planetary does it (b1b's drive). The bench's own
    NEMA 23 and DM542T are installed in the cap-weld tube rotator
    [shared-context], so this is a second set or a shared one.
  - A NEMA 17 with a 26.85:1 planetary (3 N·m permissible, 5 N·m momentary,
    $41.91 [Prime: NEMA 17 planetary geared stepper]) does it only if the
    return spring is light.
- The crank's slowness is what makes the pause in step 5 possible.

**How it knows the crimp worked.**
- **Before the stroke:** conductor k reads continuous to the grounded applicator
  through the far-end port, and a camera frame shows strands in the conductor
  barrel and the insulation edge in the window.
- **Force curve.** Strain gauges on the crank's rod give ~19–21 HX711 samples
  through the last 0.2 mm [calc X §10; P3 §5]. The trace catches a missing
  contact or conductor and insulation in the conductor barrel. The crank can
  stop short of bottom when the curve leaves its band.
- **Crimp height in line.** Bottom dead centre fixes where the ram would stop.
  The frame stretches under each crimp's peak by ΔF/k, ±8–23 µm at 13–39 kN/mm
  for ±15 % force scatter [calc X §9]. Once a micrometer has set the baseline on
  the session's first crimps, the peak gives every crimp's height.
- **After:** a camera frame, and the proof pull at insertion
  ([a6](a6-housing-as-last-comb.md)).

**What the person does.**
- Cuts the ribbon to length ([a4](a4-spool-as-magazine.md) and
  [a9](a9-reel-end-docks.md) remove this).
- Lays it in the pallet, closes the lid, drops a housing into the nest, presses
  start.
- Takes out a loom whose board end is finished, and makes the far end by hand
  (Faston, ferrule, IDC).
- Keeps the reel threaded, and empties the offcut cup and scrap chute.

## Steps it covers and what it hands back

| Step | Who |
|---|---|
| Cut to length | person |
| Split (a7), fan, flush cut, strip (a8) | machine |
| Supply contacts | the applicator's feed, from the reel |
| Place contact on conductor | machine: pre-fed contact, tongue lay-in |
| Crimp and tab cut | machine: applicator in the slow crank |
| Verify crimp | machine: continuity, force curve, ΔF/k height, camera |
| Insert, verify pin order | machine, through [a6](a6-housing-as-last-comb.md) |
| Far end, housing supply, reel threading | person |

The person's time is ~20 minutes a unit, and the machine runs ~11 minutes
alone between calls [P3 §7, estimate].

## Mechanism

### The pallet

- **Body.** Printed PET-CF or PETG. It pins to the stage carriage with two
  hardened dowels, one round and one in a slot. It carries no motors and no
  wires.
- **Channel.** Width is set by a per-ribbon insert: 6.8, 8.5, 10.2, 11.9, 13.6
  and 15.3 mm for 4P, 5P, 3+3, 4+3, 5+3 and 5+4. It is cut about 0.2 mm under
  nominal so the silicone is squeezed into register, as in AMP US 4,230,008,
  whose jaw cavity is "a nominal width less than the nominal width of the
  cable" ([source](https://patents.google.com/patent/US4230008A/en)).
- **Why the ribbon can be the reference.** Worst-case stacking of the ribbon's
  ±0.1 mm per conductor puts J1's ninth conductor 0.85 mm from nominal from one
  edge, but 0.43 mm worst and 0.12 mm RSS from a centred datum [calc §1]. Either
  is inside a comb slot's ±0.85 mm lead-in.
- **Per-loom recipe parts** travel with the pallet: the channel insert, the
  crimp-pitch fan block with its tongues, a 2.5 mm closing block, and the trim
  positions for J2's conductor 3 and J7's spare 3P conductor.
- **Actuation.** Every mechanism on the pallet is moved by the stage pushing a
  lever, slider or tongue against a fixed stop or cam [assumption: the
  passive-pallet habit of transfer lines]. That keeps the pallet cheap enough to
  print one per loom type.

### The tongue: lay-in and lift-back in one pallet part

A point finger on the ram cannot make this lay-in. At a 9 mm overhang it acts
only 1.2–3.5 mm from the fan block's face, where no S-bend fits, and it applies
no moment, so the tip dives 2.5–7 mm below it [calc X §1, borrowed-machines].
The tongue does it from the pallet:
- **Shape.** Each groove continues into a tongue 10–12 mm long, hinged at the
  block's face and held up by a light spring. The groove is covered, so the
  conductor goes where the tongue goes. Its front end is a lip that turns the
  groove back to horizontal.
- **Down.** At the crimp station a fixed printed cam catches only the tongue at
  the station's X and presses it down 5 mm, at 25–30° [calc W2 §7]. The
  conductor bends over the hinge's rounded edge and back over the lip. The 9 mm
  of conductor ahead of the lip lies level at barrel height.
- **Up.** When the stage backs out and indexes, the cam lets go. The tongue's
  spring lifts the crimped conductor back to h, clear of the next waiting
  contact.
- **Cost.** The overhang ahead of the fan block becomes 19–21 mm instead of 9,
  so parted length grows by 10–12 mm [calc W2 §7], to ~30–47 mm. Any 5–6 mm
  drop costs that, whether a tongue, a moved-back block or a ram sole makes it.

### Beside the tongue: the ram sole

- A flat sole at least 3 mm long with a V-groove, on the ram, pressing the
  conductor onto the carrier line behind the insulation barrel. The fan block
  then stands 17–19 mm back from the tip (borrowed-machines' repair).
- JST's MKS-L applicator has a factory slot for this part, its **wire hold
  spring**, between crimper (B) and the punch [mfr: MKS-L manual p. 19]. If the
  OTP applicator has the slot, the sole is a bought part.
- The sole costs the same parted length as the tongue. The tongue also lifts
  the conductor back and needs nothing on the ram; the sole needs nothing on the
  pallet. The applicator's wire-entry face decides which fits.

### What the crimp station must offer

- **Room at h over the upstream side.** Waiting contacts lie beside the anvil
  at strip pitch with wings 2.75–3.2 mm tall. In the anvil plane some neighbour
  falls into a waiting contact at every plausible strip pitch [calc X §2]. At h
  the neighbours pass over bare contacts (h 4.1–4.55 mm clears them). The feed
  plates are the conflict: guide plates, the spring pressure plate and its wing
  bolt, and the feed finger stand upstream over the strip, several centimetres
  long [mfr: MKS-L manual pp. 9, 16–19]. h rises to 6.3 mm if their tops stand
  5 mm above the strip, 9.3 mm at 8 mm [calc X §2].
- **A pause** between the crimpers clearing the contact and the feed finger
  moving. borrowed-machines' timing model of an MKS-L-like cam puts the
  crimpers clear of the box at ~220° and the pre-feed finger moving at
  ~266–285° ([b1c](../../borrowed-machines/ideas/b1c-one-shaft-applicator-press.md)'s
  timing table), which would leave a window [assumption for the OTP cam].
- **A datum** the stage can find: a hardened pin or a flat on the applicator
  base, located to the anvil.

### References and tolerances at the moments that matter

| Moment | What must be right | Set by | Tolerance |
|---|---|---|---|
| Lay-in | strands inside the conductor-barrel opening; jacket inside the insulation-barrel opening | fan block and tongue lip (±0.1), stage to anvil | capture between ~0 and ±0.5 mm (open-wing reading [P3 §2]) |
| Lay-in, axial | insulation edge in the ~0.5–0.8 mm gap between barrels [estimate]; JST's "approximately 50/50" [mfr S5] | flush cut ±0.05, strip line ±0.05, stage Y ±0.02, contact on anvil ±0.05–0.1 | ~±0.15 mm stacked; the camera trims Y after the first crimp |
| First crimper touch | contact seated on the anvil, wings square | applicator track and hold-down | the applicator's job |
| Bottom of stroke | crimp height ±0.05 mm [mfr S13, S14] | crank bottom dead centre and the applicator dial | ±0.008–0.024 mm frame scatter [calc X §9] |
| Release | crimped contact off the anvil before the feed moves | crank pause; stage backs out −Y | timing, not position |
| Index | crimped conductor back at h | tongue spring | coarse (±1 mm) |

## Printed and bought parts

| Part | Source | Evidence and note |
|---|---|---|
| Pallet body, lid, channel inserts, fan blocks with tongues, station cam, housing nest | printed (PET-CF, PETG, TPU pad) | H2C, a few hours per set |
| Two-axis stage, 100–150 mm travel, ~100 N push | bought | MGN12 300 mm rail with MGN12H carriage, $20.49 [Prime]; Iverntech NEMA 17 with integrated Tr8×2 screw, $27.99 [Prime, thin listing] |
| Station servos (guillotine, strip blades, clamp) | bought | MG996R 4-pack $18.99; DS3218 20 kg $14.99 [Prime] |
| Razor guillotine | bought blades | AccuTec 0.009 in single-edge, 100 for $12.90 [Prime, thin listing]; American Cutting Edge $10 per 100 ([source](https://americancuttingedge.com/converting/single-edge-razor-blades)) |
| XH side-feed applicator | bought | no Prime listing [Prime: "no Prime listing found"]; eBay $150–167 plus $80–90 shipping, Alibaba $200–250 [force-and-form, borrowed-machines key findings] |
| Slow crank press | built | borrowed-machines b1b around the VEVOR press; UCP204 pillow blocks $26.99 for two [Prime] |
| SXH-001T-P0.6 reel | bought | Digi-Key reel $0.0235 each at 8,000 [xh-facts §6] |
| Strain gauges, HX711 | bought | BF350 gauges $6.99; SparkFun HX711 $11.50 [Prime] |

## Problems, repairs and branches

1. **Neighbours fall into the next contact on the strip** if they lie in the
   anvil plane. The fan block holds them at h and only the active one goes
   down, on its tongue.
2. **A 5 mm drop has nowhere to happen, and a point finger leaves the tip
   diving.** The tongue with a levelling lip, or a ram sole with the block moved
   back. Either costs 10–12 mm of parted length [calc W2 §7].
3. **The neighbours at h sit over the applicator's feed plates.** Open in a1
   itself; it depends on the plates' height. Raising h to 6–9 mm lengthens the
   tongue and the split again. Two branches go around it:
   - [a1c](a1c-crimp-upstream-first-park-after.md): crimp from the upstream
     end with the fan flat downstream, and fold each finished conductor back;
   - [a2e](a2e-docked-strip-through-a-feedless-applicator.md): remove the feed
     hardware and dock the whole row onto a strip segment.
4. **Pre-feed pushes the next contact into the crimped one.** The feed advances
   the strip on the upstroke while the cut-free crimped contact still sits on
   the anvil. A conductor held 6–9 mm back yields at 40–60 mN, so it is bent
   37–58° sideways for good [calc X §3]. The crank's pause is the repair. A
   bought fast press cannot do this. Setting the cam to post-feed is not a
   repair, because the contact would then arrive under a conductor already
   laid in.
5. **A ramp behind the anvil would sit where the shear blade and scrap chute
   are.** The tongue lifts the conductor back, so there is no ramp.
6. **The laid-in conductor keeps its bends.** Annealed strands take a set below
   a bend radius of ~39–78 mm [P3 C11; calc §4]. Each tongue root carries two
   reversals of set, which the closing block and insertion clamp straighten.
   Whether the conductor then enters its cavity straight is uncertain.
7. **The insulation edge misses the window.** The stack is ~±0.15 mm against a
   ~0.5–0.8 mm gap. The first crimp of a session goes under the camera and the
   stage's Y offset is corrected from it.
8. **Strands splay at lay-in.** The tongue carries the jacket, not the strands,
   and the conductor wings corral the bundle as they close.
   [a8b](a8b-spindle-with-touch-off.md)'s quarter turn of twist is a further
   answer. Stray strands show in the camera frame.
9. **The finished loom carries the fan's length difference.** Cut and stripped
   after a 5 mm fan, a 5P's outer conductors are 1.34 mm longer than its centre
   one once closed to 2.5 mm. That stays in the loom as a 3–4 mm arc over a
   20–30 mm split [calc F §5]. [a9](a9-reel-end-docks.md)'s order (cut before
   the split, equal-path fan) leaves none.
10. **A lot of machine for 53 crimps.** [a1b](a1b-hand-shuttle.md) keeps the
    pallet and drops the stage.
11. **Guarding.** A stage that fires a press on its own needs an interlocked
    enclosure. At a crank's walking pace it is a pinch point, not a 2 t blow.

## What it contributes

- **Placement split into coarse and fine.** The pallet delivers each conductor
  to about ±0.1 mm at the lip; the contact waits on the anvil, delivered by the
  strip; the open wings take the rest.
- **The wire stop moves into the pallet.** Strip length and where the
  insulation lands come from the pallet's own cut and strip line, the same for
  every conductor.
- **Contact roll is set by the ribbon.** The ribbon stays flat from clamp to
  crimp, so every contact leaves the anvil with the same roll, which carries
  into the housing.
- **A passive lay-in mechanism.** A tongue per conductor, bumped by a station
  cam, lays in and lifts back with no actuator on the pallet or the ram.

## Major unresolved problems

- **The applicator's upstream envelope:** how high the feed plates stand, and so
  what h, tongue drop and parted length a1 needs. The Revopoint MINI 2 on hand
  can scan the applicator's wire-entry face and upstream side when one arrives.
- **Parted length of ~30–47 mm** at 5 mm crimp pitch with the tongue, the
  longest in this directory. A backshell at that root stands 52–69 mm above the
  board [calc F §2]. Whether it fits behind the housing is Derek's call.
- **The crank's pause window** on the OTP cam. Hand-cycle the applicator and
  note the ram height at which the feed finger starts to move.
- **Set from the tongue's bend and lift-back**, and straight insertion after it.
- **The press itself** (b1b): shut height, frame stiffness, guarding, and a
  motor that the weld station is not using.

## Related ideas

- Branches: [a1b](a1b-hand-shuttle.md) (moved by hand between seats),
  [a1c](a1c-crimp-upstream-first-park-after.md) (flat fan downstream, fold after
  crimp).
- Around the same problem: [a2e](a2e-docked-strip-through-a-feedless-applicator.md),
  [a9](a9-reel-end-docks.md).
- Modules it uses: [a5](a5-part-fan-strip-in-the-pallet.md),
  [a6](a6-housing-as-last-comb.md), [a7](a7-zip-station.md),
  [a8](a8-rolling-ring-scorer.md), [a3](a3-backshell-that-ships.md) (as the
  pallet that ships).
- Other explorers: borrowed-machines
  [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)
  (the press), [b1c](../../borrowed-machines/ideas/b1c-one-shaft-applicator-press.md)
  (one shaft timing everything).

## What rests on assumptions

- Strip pitch ~7.1 mm [Würth's 7.10 mm analog, via change-the-question and
  terminal-supply]; clone drawings, not to scale, give 6.8–9.5 mm [calc §2;
  xh-facts §1].
- The barrel gap of about 0.5–0.8 mm [estimate].
- That the OTP applicator is laid out like JST's MKS-L [assumption,
  borrowed-machines].
- The ribbon's ±0.1 mm tolerance applying per conductor [repo bom.md,
  interpretation].

## Labels

- [calc §n]: [`../calc/pallet_geometry.out.txt`](../calc/pallet_geometry.out.txt);
  [calc W2 §n]: [`../calc/stations_wave2.out.txt`](../calc/stations_wave2.out.txt);
  [calc F §n]: [`../calc/final_w3.out.txt`](../calc/final_w3.out.txt).
- [calc X §n]: borrowed-machines'
  [`exchange_ribbon_as_pallet.out.txt`](../../borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt);
  [P3 §n]: procedure-is-the-machine's
  [`exchange_ribbon_w3.out.txt`](../../procedure-is-the-machine/calc/exchange_ribbon_w3.out.txt);
  [P3 Cn]: consistency item n of that explorer's reading of this directory,
  [`procedure-is-the-machine--on--ribbon-as-pallet-w3.md`](../../../exchange/procedure-is-the-machine--on--ribbon-as-pallet-w3.md);
  [w3 §n]: [`../calc/exchange_on_force_and_form_w3.out.txt`](../calc/exchange_on_force_and_form_w3.out.txt).
- [Prime: …]: a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
  observed 2026-09-28 in Derek's signed-in Chrome.
- [mfr S…], [xh-facts §n]: [`../../../context/xh-facts.md`](../../../context/xh-facts.md).
