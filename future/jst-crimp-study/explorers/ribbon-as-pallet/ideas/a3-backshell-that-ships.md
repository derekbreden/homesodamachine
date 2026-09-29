# a3 The backshell that ships: the clamp is applied once and never removed

## Picture it

"Clamped once", taken literally. The thing that clamps the ribbon at the start
is a small printed part that stays on the loom for good. It is the machine's
pallet, the loom's strain relief and the loom's label at once. The machine owns
only a universal holder that grips any backshell. Sketch:
[`../sketches/a3-backshell-that-ships.svg`](../sketches/a3-backshell-that-ships.svg)
(schematic).

**Where things start.**
- **The backshell.** For each of the 10 looms per unit the printer makes a clip
  about (ribbon width + 4) × 12 × 6 mm in PETG or PET-CF, 1–2 g, with:
  - a round **bar** across its width and a snap cover;
  - two accurate outer faces and a notch, which are the datum;
  - a **front face** that is the loom's split root;
  - the loom's name embossed on top (J4 SENSORS, J7 REEDS B);
  - a short code of notches on one edge that a feeler or the camera reads as the
    recipe: which ribbons, which conductor to trim, which housing;
  - optionally, two folded **bridge arms** hinged at the front corners.
- **Before the machine.** The ribbon is folded 180° around the bar, the tail
  running back along the loom, and the cover snaps over both layers: the
  strain-relief fold every IDC ribbon connector ships with. The end projects
  from the front face by the loom's parted length plus the tip.

**Why a fold and not ridges.** Ridges biting a silicone web need high local
pressure on a material that tears at 15–25 N/mm. A 180° wrap multiplies what the
cover holds on the tail by e^(μπ): 4.8× at μ 0.5, 23× at μ 1.0, 2.6× at μ 0.3.
A cover holding 3 N resists 14–69 N of loom pull at μ 0.5–1 [calc X §8]. For
scale, a 22 AWG conductor's silicone carries 17–23 N and its copper breaks at
85–100 N [calc X §8; source S23].

**What moves.** The machine's holder, on a stage as in [a1](a1-pallet-tour.md)
or on seats as in [a1b](a1b-hand-shuttle.md), grips the backshell by its datum
faces with a spring jaw against two hard faces. Then:
- **Part.** [a7](a7-zip-station.md)'s tines drive up to the front face, which
  is the tear stop; or a laser slits each valley from the tip back to the face
  (borrowed-machines' [b4](../../borrowed-machines/ideas/b4-laser-slits-and-scores.md)).
- **Fan, flush cut, strip** ([a8](a8-rolling-ring-scorer.md)), referenced to the
  front face.
- **Crimp** by any station in this directory.
- **Close to 2.5 mm and insert** ([a6](a6-housing-as-last-comb.md)).
- **Arms variant:** a last station folds the two bridge arms forward and snaps
  their hooks over the XHP's end flanges, making housing, fan and backshell one
  piece.

**What locates what, and the reference for fixed.** **"Fixed" is the
backshell's datum faces,** printed to about ±0.1 mm [estimate]. The split root,
flush cut and strip line are all measured from the front face, so its own
printing error cancels axially. Laterally, the fan block and crimp station do
what they do in a1.

**What drives the crimp and carries its force.** The crimp station's own frame.
The backshell carries none of the crimp; it carries the pull of zip, strip and
insertion through its fold.

**How it knows.**
- **The recipe is read, not keyed in:** the camera or a feeler reads the notch
  code before anything happens.
- **Swap guard:** J4 and J7 backshells carry different codes, and a coded
  housing nest refuses a J7 housing in a J4 run. That covers the swap the repo
  worries about [repo cable-assemblies.md].
- **Crimp checks** are the station's.

**What the person does.** Prints backshells with the unit's other prints; folds
each ribbon end around its bar and snaps the cover; drops it into the holder;
takes out a finished, labelled, strain-relieved loom end.

## Steps it covers and what it hands back

- **Covers:** clamp and datum for every station, recipe identification and the
  J4/J7 swap guard, the split root as a tear stop, strain relief and label in
  the product.
- **Hands back:** printing and folding every backshell, loading it, far ends;
  every other step is the station's that it rides through.

## In the product: the strain relief the insulation crimp is not

force-and-form's [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md)
finds that on this silicone the strands slip inside the jacket at 0.4–9 N, so
the insulation barrel cannot carry a loom's pull [w3 K5]. The fold carries
14–69 N at μ 0.5–1 and never loads a crimp. With arms, a pull goes through the
fold and the arms to the housing. The backshell therefore has a job in the
product whatever machine makes the loom:
- **label**, at the housing, readable in the enclosure;
- **strain relief**;
- **fan protection** between two rigid ends;
- **trimmed conductors** (J2's conductor 3, J7's spare) cut back at the face.

## As the reel puller's grip

At a reel clamp ([a9](a9-reel-end-docks.md); procedure-is-the-machine's
[p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md)
and [p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md))
a puller draws each loom off the reel and must not pull through a crimp. Folded
on before the zip, the backshell is the puller's handle: a 3 N clip on the
cover resists 14–69 N. Its front face is then the split root and the tear stop
at the reel too.

## With fold-back parking and a split made from the face

borrowed-machines' [b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md)
parks every conductor but the active one folded back 180° over its cassette,
which needs the clamp edge exactly on the split root, or the fold peels the web.
The backshell's front face is that edge by construction. The zip's tear stops
at the face, or b4's slits end at it; the conductors fold back over the
backshell's top between crimps; and the split falls to **8–15 mm**, only what
the housing fan and the fold need [borrowed-machines calc geometry §1].

## How tall it stands

The board's XH wafers are vertical THT [repo jlcpcb-parts.md], so the housing
stands with its wires going up. With the backshell at the split root, its top
stands at the parted length + ~21.8 mm (XHP mated 9.8 mm, backshell 12 mm)
[calc X §7; calc F §2]:

| Parting | Parted length | Top above the board |
|---|---|---|
| fold-back parking | 8–15 mm | 30–37 mm |
| housing-pitch fan only | 14–18 mm | 36–40 mm |
| [a1c](a1c-crimp-upstream-first-park-after.md), [a2c](a2c-loose-contact-cassette.md) at 5 mm, per ribbon | 17–23 mm | 39–45 mm |
| [a2](a2-two-pallets-meet.md), [a2e](a2e-docked-strip-through-a-feedless-applicator.md), [a10](a10-dock-tack-then-nest.md) at ~7 mm, per ribbon | 21–30 mm | 43–52 mm |
| [a9](a9-reel-end-docks.md), equal-path at ~7.1 mm | 22–33 mm | 44–55 mm |
| [a1](a1-pallet-tour.md) with the tongue | 30–47 mm | 52–69 mm |

The doubled ribbon in the fold adds ~1.7 mm of thickness.

## Variants kept beside it

1. **Without arms.** Clamp, datum and label only; no fit to the housing. The
   fold still takes loom pull; the fan between it and the housing is
   unprotected.
2. **With an internal fan.** The backshell's inside is a 1.7 → 2.5 mm fan and
   its front face a comb at housing pitch. Crimping free ends at 2.5 mm in plane
   is impossible (open contacts collide [calc §3a]), so the conductors would
   stand ~15 mm proud during crimping and the backshell slide forward along
   them afterwards. That conflict is unresolved.

## Printed and bought parts

Printed: backshells (about 10 per unit) and the machine's holder. Bought:
nothing beyond the stations it rides through.

## Major unresolved problems

- **Room above the board:** 30–69 mm depending on the parting (table). Nobody
  has checked the enclosure for it.
- **Arms on an XHP:** whether hooks grip the end walls without reaching the
  wafer's shroud. The XHP is A + 4.8 overall against A + 3.2 body [xh-facts §3],
  about 0.8 mm of flange a side. Untested.
- **Silicone on PETG friction,** which sets the fold's grip.
- **A part on every loom** is Derek's decision, not the machine's.

## Related ideas

- Rides through: [a1](a1-pallet-tour.md), [a1b](a1b-hand-shuttle.md),
  [a2](a2-two-pallets-meet.md) and its branches, [a9](a9-reel-end-docks.md).
- Other explorers: borrowed-machines
  [b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md),
  [b4](../../borrowed-machines/ideas/b4-laser-slits-and-scores.md);
  force-and-form [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md);
  procedure-is-the-machine [p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md),
  [p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md).

## What rests on assumptions

- Board clearance [estimate]; silicone-on-PETG friction [assumption]; hook fit
  on XHP ends [assumption]; H2C feature accuracy [estimate].

## Labels

As [a1](a1-pallet-tour.md#labels); [w3 K5] is combination K5 in
[`../../../exchange/ribbon-as-pallet--on--force-and-form-w3.md`](../../../exchange/ribbon-as-pallet--on--force-and-form-w3.md).
