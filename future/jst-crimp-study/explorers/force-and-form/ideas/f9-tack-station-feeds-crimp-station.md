# f9 — A light station puts contacts on; a heavy station crimps them one by one

Explorer: force-and-form. A combination: change-the-question's
[c1b](../../change-the-question/ideas/c1b-tack-first.md) (a light gang tack
fixes a whole half-row of contacts to their conductors) feeding a heavy crimp
station built from force-and-form's [`f3`](f3-knee-micropress.md) with its
strip replaced by a keyed steel nest ("f3-t", proposed as Combination 2 in
[change-the-question's reading of force-and-form](../../../exchange/change-the-question--on--force-and-form.md)).
[`f3b`](f3b-two-station-forming.md)'s station A is the alternative light
station. Branch: [`f9b-tack-on-the-strip.md`](f9b-tack-on-the-strip.md) (the
tack made on a docked strip at strip pitch, with no planes).
Sketch: [`../sketches/f9b-tack-on-the-strip.svg`](../sketches/f9b-tack-on-the-strip.svg)
shows the heavy station's keyed nest, which is the same here (schematic).
Numbers: [`../calc/wave2.out.txt`](../calc/wave2.out.txt) §5 [calc: wave2 §5],
[`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) [calc final §n],
[change-the-question calc off §n](../../change-the-question/calc/on_force_and_form.out.txt),
ribbon-as-pallet's [`exchange_on_force_and_form_w3.out.txt`](../../ribbon-as-pallet/calc/exchange_on_force_and_form_w3.out.txt)
[RP w3 §n].

## Picture it

- **The ribbon pallet** holds the web in a clamp whose face is exactly the
  split root (ribbon-as-pallet a7's tear stop), so folding a plane back never
  peels the web further. The same pallet travels from station T to station C:
  it is the datum for both.
- **Station T (tack), attended.** c1b's clamp and split put the odd conductors
  of a ribbon end in one plane at 3.4 mm; the even plane is folded down and
  back at the clamp face. The person, or a post bar pushed in one stroke, sets
  loose kit contacts into a pallet at the same pitch. A presser comb lays the
  half-row into the open barrels in one motion, the camera checks the lay, and
  a 1.2–1.5 mm sheet-steel comb with insulation profiles closes every insulation
  barrel of the half-row in one light stroke, stopped deliberately loose: 33–132
  N a contact, 66–660 N for 2–5 contacts, over a steel anvil strip, in two
  passes at 6.8 mm so the comb's teeth stay wide [change-the-question c1b]. The
  conductor barrels stay open. Then the even plane unfolds, the odd plane folds
  back, and the even half-row is tacked the same way. Every contact of the
  ribbon end is now pinned to its conductor at its axial position and roll.
- **Station C (crimp), unattended.** f3's knee press without its strip track.
  In its place is a **keyed steel nest**: a box slot with lead-in chamfers, a
  lance relief, and a front stop the box seats against, ±0.02–0.05 mm
  [calc: placement_budget]. The pallet sits on a kinematic seat on a small XYZ
  stage. Before each ribbon end, the plane not being crimped is folded back at
  the clamp face, and swapped once per ribbon end.
  1. With the crimper raised 5 mm, the stage carries one tacked contact
     box-first above the anvils and lowers it straight down into the nest; a
     fork bearing on the in-plane neighbours' contacts (rigid handles now, not
     floppy tips) holds them 3–4 mm up and clear of the crimper holder, 11–19°
     over a 12–20 mm split.
  2. Capture, camera look; the far-end port (ribbon-as-pallet a6) reads that
     only this conductor touches the grounded nest.
  3. The knee crimps the conductor barrel and re-forms the loosely closed
     insulation barrel to its final height; re-touch reads the height.
  4. A neck blade drops in front of the brush onto the box's rear face, and the
     stage draws the pallet back to ~20 N, reacted by the web clamp.
  5. The crimper rises, an ejector lifts the box, and the stage indexes.
- **What locates what.** Fixed is the pallet's web clamp until the tack (at T
  the tip stop, pocket and camera set the axial position), and the nest's box
  stop after it. The stage only has to reach the nest's chamfers (±0.3–0.5 mm);
  crimp height is the knee at straight in f3's steel loop, read by the
  indicator.
- **What carries the force.** At T, the tack comb's own steel stop and anvil
  strip; at C, f3's knee press. The pallet and stage carry none of the crimp.
- **How it knows.** The camera at T before the tack; identity, capture look,
  force curve, re-touch height and the proof pull at C.
- **The person** splits, strips and tacks at station T, a half-row at a time,
  seats the pallet at station C and leaves. About 34 calls per unit, none paced
  by the crimp [change-the-question calc off §7], if the pallet carries the
  ribbon end from T to C and the planes are swapped at C by a folding finger.
  If the person re-clamps each ribbon end once per plane instead, ~48 [estimate].

## What each side brings

- **c1b:** placement of a whole half-row in one motion, pinned at axial
  position and roll, with no feeder at the heavy station.
- **f3 (as f3-t):** the heavy crimp one contact at a time, in steel, to a
  geometric bottom, with a logged curve and a re-touch height; no threading, no
  pilot pin, no tab.
- **What goes away:** the per-crimp contact drop (f1) and the axial threading
  of 60 fine strands into a captured barrel (f3).
- **Loose kit contacts** become usable in an automated crimp.

## Physics of the handoff

- **What the tack must hold at station C.** The conductor between clamp and
  contact bends at 1–3 mN when a chamfer moves the contact 0.3–0.5 mm sideways,
  and twists at 0.03–0.2 N·mm when the slot squares a 5–10° roll on 10–30 mm of
  free conductor [RP w3 §3]. A tack on this silicone holds 0.4–9 N and
  0.4–2.5 N·mm [calc: wave2 §5]. So with 10 mm or more of free conductor, the
  conductor bends and twists long before the tack slips: a contact arriving
  rolled several degrees is squared by the slot without turning on its jacket.
- **Which way the tack is loaded.** A vertical entry loads the tack across the
  jacket, where the wrapped wings hold it. Along the jacket a loose tack may
  hold only 0.1–0.4 N [c1b], so the slot is cut only ~0.05 mm longer than the
  box and nothing pushes the contact along its wire.
- **A stronger tack:** f3b's station A curls the conductor wings onto the
  strands as well, which traps them mechanically; the price is ~180–580 N a
  contact and a steel stop for a gang.
- **Re-forming a loose insulation barrel.** The final insulation crimper meets
  wings already partly closed. They enter its flare if the tack is no wider
  than the flare's mouth, which a tack set looser than the final crimp
  satisfies by construction. Where the final height lands in this wire's window
  is [`f6`](f6-two-blades-two-drives.md)'s question.
- **The other plane at C.** Its tacked contacts hang ±1.7 mm in X from the
  working one, 3.4 mm above or below: inside the half-width of f3's crimper and
  nest block (1.75–2.2 mm) either way. So it is parked, folded back at the
  clamp face, while the first plane is crimped, which gives each conductor 3–4
  folds at the root across T and C. The clamp face being the split root is what
  keeps those folds from peeling the web.

## Hosts for station C

| Host | Locator | Condition |
|---|---|---|
| f3-t, the knee press with a keyed nest | box slot, lance relief, front stop | none beyond the nest; the crimper lifts clear |
| f1, the SN-2549 in its cradle | f1's swinging flap | the tacked contact enters the nest box-first from above, so the SN-2549's open nest must pass box plus lance, 2.8–3.25 mm (unmeasured) |
| a person with today's SN-2549 | the tack itself, with a box-keyed clip on the jaw (c1b) | the heavy crimp becomes a one-part placement instead of juggling contact, wire and tool; no motor |

## Tried against it

1. **The tack's grip under side loads**, above.
2. **Tack first changes the crimp.** Closing the insulation barrel before the
   conductor crimp reverses JST's two-step order (conductor first). Whether it
   matters is one of the four arms of the sectioning experiment in f3b.
3. **Two stations, two datums.** The tack fixes the axial position; station C
   only has to seat the box against its stop, so a tack placed 0.1 mm wrong
   along the wire makes a bellmouth 0.1 mm wrong. The camera at station T sees
   the insulation edge in the window before the tack.
4. **J4 and J7 crossings** are made at station T's lay, as in c1.
5. **The planes.** f9b removes them: tacked on a docked strip at strip pitch,
   the neighbours hang one strip pitch away and no plane is ever parked.

## Major unresolved problems

- **Tack grip on silicone**, measured: squeeze a kit contact's insulation
  barrel lightly onto the ribbon and pull and twist it with a hook and the
  bench scale.
- **Tack-first crimp quality**, sectioned and pulled.
- **Folding and swapping the parked plane** at station C without a person.
- **The fork's lift** at 3.4 mm, or a spread of the tacked contacts to 5.0 mm
  with c1's cam plate first.
- **The transition *t*** for the nest's anvil (t ≥ 0.34–0.74 mm) and the neck
  blade (t ≥ 0.50–0.70 mm) [calc final §3].

## Which conclusions rest on assumptions

- **Grip and torque** are estimates from a thin-layer model of the jacket.
- **Nest location** ±0.02–0.05 mm is an estimate for a steel slot and stop.
- **The call count** assumes the pallet carries each ribbon end from T to C.
