# c3 — Fold and solder: close the wings lightly, make the joint with solder instead of coining force

A joint change, and with it a change of the product's basis: **not a crimp,
and outside what JST supports.** The XH contact's wings are folded around the
strands with a tenth of a crimp's force, and solder makes the electrical and
mechanical joint. The contact, housing and wire stay the same. It is here so
Derek can see how much of every crimp machine exists only because of coining.
Sketch: [`../sketches/c3-fold-and-solder.svg`](../sketches/c3-fold-and-solder.svg)
(schematic). Numbers: [`../calc/ctq.out.txt`](../calc/ctq.out.txt) §6.

## Picture it

**Where things start.** Two supplies work:
- **On strip.** The contact stays on its carrier through fold and solder and is
  sheared off afterward (below, "On the strip").
- **Loose.** Contacts sit in a nest bar with steel inserts under the barrels,
  one at a time or a half-row at a time, as in [`c1`](c1-half-rows.md).

The stripped conductor is laid into the open barrels by a presser comb.

**The fold.**
- A **folder** comes down over the barrels: a punch-shaped arch with no
  coining land, cut from sheet steel and carried in a printed holder, closed by
  a hobby servo through a small lever or by a lead-screw stepper.
- The arch is steel because the 0.2 mm wing edges meet it first along a line.
  At the 8 N per wing the plastic hinge needs, peak line-contact pressure is
  ~220–310 MPa on PETG and ~340–490 MPa on PET-CF; at 40 N, 485–770 MPa;
  against yields of ~48 and ~80 MPa [terminal-supply exchange calc §8,
  Hertz line contact, estimate]. A printed arch would be dented at the first
  touch point on every fold and its shape would drift over ~3,200 folds.
  Printed parts carry the steel profile; they are not the profile. It is the
  same steel part as [c1b](c1b-tack-first.md)'s tack comb.
- It curls the conductor wings over the strands and the insulation wings
  over the silicone. It stops at a height ~0.2–0.3 mm above a real crimp
  height, so the strands are enclosed but not compacted [estimate].
- The force is tens to a few hundred newtons, against a steel anvil pin:
  - the plastic-hinge force to bend a 0.2 mm bronze wing is ~6–10 N at its
    root [calc §6];
  - curling it against an arch with friction is the "tens to a few hundred
    N" of the facts estimate [xh-facts §4].

**What locates what.** The contact by its nest (steel inserts under the
barrels, box against a stop) or by the strip's pilot holes; the conductor by
the presser comb and a tip stop. "Fixed" is the nest bar or the strip track.
The fold's 0.1–0.3 kN closes through arch, contact and steel pin anvil into a
printed frame with a hard stop; ±0.1 mm on the fold height is enough.

**A variant: fold in the crimp tool, stopped short.** The SN-2549's own stroke,
stopped 0.2–0.3 mm above crimp height, is this fold in the profile the contact
was designed around, with no custom arch. hand-tool-as-press's
[a1b](../../hand-tool-as-press/ideas/a1b-pawl-out.md) pawl-out cradle stops the
tool at any grip position: 3–20 N at the grip through a gain of 15–30 delivers
the 0.1–0.3 kN fold (hand-tool-as-press K5, in
[`../../../exchange/hand-tool-as-press--on--change-the-question-w3.md`](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md)).
The flag then leaves the tool for the solder station.

**The solder.**
- The nest bar indexes to a soldering station:
  - the bench's **Hakko FX-888D** with a small chisel tip on a vertical
    slide;
  - a **solder feeder**: a stepper pushing 0.5 mm flux-cored solder through
    a tube, like a 3D-printer extruder.
- The tip touches the side of the closed conductor barrel. The feeder
  pushes a metered length, ~3–5 mm of 0.5 mm wire [estimate], against the
  barrel's front, where the brush is.
- Solder melts, flows into the strands inside the barrel and wets the
  tin-plated barrel. The tip lifts after a timed dwell of 1–3 s.
- Heating the contact plus 10 mm of conductor by 230 K takes ~6 J [calc §6].
  The dwell is set by tip contact, not by power.
- Silicone does not melt or shrink back at soldering temperature. It serves
  to 200 °C [source S31]. So the insulation edge stays put, unlike PVC.

**How it knows it worked.**
- The camera sees the fillet: solder visible at the brush, none on the box,
  none on the insulation barrel.
- **Joint resistance.** A four-wire milliohm check from the contact's box to
  the conductor's far end [prior-art §6]. It resolves ~1 mΩ.
- A pull to 39.2 N [mfr S6]. A soldered joint in a 1.4 mm barrel should
  exceed the wire's own strength [estimate].
- There is no crimp height to measure. That is the point, and the problem.

**What the person does.**
- Loads contacts, or a strip.
- Lays the ribbon.
- Keeps the solder spool and iron tip in order: tinning, tip replacement.
- Inserts into the housing (or c1's insertion does it).

**Steps covered:** place, fold (light), join (solder), verify (fillet,
milliohms, pull). **Hands back:** insertion, loading contacts or strip, solder
and tip upkeep, and the decision whether a soldered XH joint is acceptable.

## What gets simpler

| | Crimp (every other arrangement) | Fold and solder |
|---|---|---|
| Peak force | 0.75–2.3 kN per contact [xh-facts §4] | ~0.1–0.3 kN [estimate] |
| Precision that matters | Bottom dead centre ±0.02–0.05 mm | Fold height ±0.1 mm; solder volume and dwell |
| Die | Hardened punch with the B-profile | Sheet-steel arch in a printed holder; a steel pin anvil |
| Frame | A closed C that stays stiff at kN | Printed, servo-driven, around steel profiles |
| Actuator | NEMA 23 through a screw and lever | Hobby servo, NEMA 17 |
| Detects a bad joint by | Force against stroke (coarse for fine strands [prior-art §6]) | Camera fillet, milliohms, pull |

A printed machine around two small steel profiles, with servos and the iron
already on the bench, becomes plausible. That is what this idea shows.

## Problems worked through

1. **JST does not support it.**
   - JST: "always use application tooling specified by JST … JST cannot
     accept any liability for failures due to the use of non-JST application
     tooling" [mfr S5, handling precautions §Precautions for Crimping
     Process 1].
   - That sentence also applies to every home-built crimp machine in this
     study, and to the iCrimp tool on the bench today.
   - The difference is degree. A crimp made to JST's dimensions is at least
     the joint JST designed. A soldered fold is a different joint.
2. **Solder wicks up the strands and makes a stiff point that fatigues.**
   - This is the standard objection to solder in a crimp barrel. The
     compressor and pumps vibrate the appliance.
   - Silicone insulation does not shrink back, so solder can wick under it
     by capillary action. Metering the solder and heating only the barrel
     front limits the distance, but does not stop it [assumption].
   - The insulation barrel, folded over the silicone, supports the wire just
     behind the conductor barrel. The stiff-to-flexible transition sits
     inside that support if wicking stays under ~1.5 mm [estimate].
   - Unverified. The test: vibrate a sample loom on a speaker or orbital
     sander for hours, then pull.
3. **Flux creeps into the contact box and spoils the mating spring.**
   - The box is ~2 mm in front of the conductor barrel [xh-facts §1].
     No-clean flux in the solder's core can run forward.
   - Flux residue in the box raises contact resistance on the header post
     [assumption].
   - Repair: solder from the barrel's rear half, with the contact tilted box-up
     so flux runs away from the box. Or use solder paste with less flux.
   - Left uncertain.
4. **IPC/WHMA-A-620 probably calls solder in a crimp a defect.** The
   standard was not read, since it is paid [xh-facts §5], and its crimp
   sections cover formed joints [source S25 table of contents]. This joint
   would be assessed as a soldered joint, not a crimp.
5. **Heat may anneal the box spring.**
   - Phosphor bronze relaxes with sustained heat. A 1–3 s touch at ~300 °C
     2 mm from the box probably does not reach the box at that temperature
     [assumption].
   - The check: insertion and withdrawal force on the header post before and
     after, at 20 cycles.

## On the strip

- **Heat.** The tab neck joining contact to carrier (0.6–1.0 mm wide, 0.2 mm
  thick, 0.8 mm long) conducts only ~1.7–4 W at a 230 K rise
  [terminal-supply exchange calc §8]. Against a 60–70 W iron it is a thermal
  choke, so a contact can be folded and soldered while still on its carrier,
  then sheared off.
- **What the strip gives.** Location by pilot pins, orientation, no loose
  loading, and a carrier to shear from below afterward.
- **Flux.** The strip can be tilted box-up as a whole, so flux and molten solder
  run rearward, away from the box. Rearward is also toward the insulation, so
  the tilt trades flux in the box (problem 3) for wicking under the silicone
  (problem 2). Only a sectioned sample shows which is worse.

## Contribution

- It separates two things every crimp machine carries together:
  - putting the contact and the wire together, which is light;
  - making the joint, which is heavy and precise.
- It shows what a machine is when only the first is mechanical: light,
  printed and cheap.
- Covers **place, fold and join**. It hands back insertion and anything the
  machine's nest does not load.
- Its fold station is the same steel part as [`c1b`](c1b-tack-first.md)'s
  tack comb. The two ideas share hardware whether or not solder is ever used.

## Major unresolved problems

- It is **not a crimp**. Whether a soldered XH joint is acceptable in this
  appliance, which has vibration and a sealed, not field-serviced box
  [repo cable-assemblies.md], is Derek's decision. It is outside JST's
  support.
- **Wicking, fatigue and flux migration** (problems 2 and 3) are real and untested.
- **The iron tip wears.** An unattended station needs tip cleaning (a brass
  wool poke between joints) and a check that solder actually flowed. The
  camera sees a fillet; it does not see a cold joint inside the barrel.

## What rests on assumptions

- Fold force, from a plastic-hinge estimate [calc §6] and the context's
  forming range.
- Solder volume and dwell [estimate].
- Flux behaviour and heat at the box [assumption].
