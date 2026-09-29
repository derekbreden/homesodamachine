# a7 Zip station: tear each web along its own neck, stop the tear at the clamp, and let the tines that tore it hold the fan

## Picture it

A station for the step every arrangement in the study needs and most leave to the person:
parting the web between 22 AWG silicone conductors. The ribbon's construction
does the locating. Its conductors are round jackets 1.7 mm across at 1.7 mm
pitch, so neighbours meet at a line, the valley plane, fused over a neck nobody
has measured. A tear started in that neck and driven by a blunt wedge follows
it by itself, because it is the cheapest path through the material. The tool
does not need to know where the web is. Sketch:
[`../sketches/a7-zip-station.svg`](../sketches/a7-zip-station.svg) (schematic).

**Where things start.**
- One ribbon end (3P, 4P or 5P) is clamped in a pallet ([a1](a1-pallet-tour.md)'s,
  [a2](a2-two-pallets-meet.md)'s, [a3](a3-backshell-that-ships.md)'s backshell)
  or in a fixed clamp at a reel ([a4](a4-spool-as-magazine.md),
  [a9](a9-reel-end-docks.md)). A pair goes through as two ribbons.
- **The clamp's front face is the split root.** Its position is set per recipe
  at the parted length the loom needs: 14–18 mm for a housing-pitch fan,
  17–23 mm at 5 mm crimp pitch, 21–30 mm at strip pitch [calc §2], more for
  a1's tongue.
- The end stands 35–50 mm past the clamp on a **covered floor**: a plate under
  and a lid over the protrusion, up to the nicker, lifted only for the tines.
  Off a spool the ribbon keeps a curl that lifts a 35 mm protrusion's tip
  2.5–12.6 mm out of plane [P3 §9], and the nicker's noses sit just above and
  below a 1.7 mm ribbon.
- The tip is either roughly square (the cut that freed it), or already stripped
  webbed, with the slug's gaps open between bare bundles (order B of
  [a5](a5-part-fan-strip-in-the-pallet.md), procedure-is-the-machine's
  [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md)).

**What moves.** Only the pallet, in +Y toward a fixed comb, on a stage or by
hand along a rail (or at a reel clamp, the comb toward the fixed end). The
station has no motor.
1. **Nick,** for a square-cut tip. The tip meets the **nicker**: N−1 slivers of
   double-edge razor (0.10 mm) standing at 1.7 mm pitch, each on a printed
   flexure that lets it float ±0.3 mm sideways, with a printed V-nose above and
   below meeting the valley notch just before the sliver enters. The slivers go
   2 mm into the tip, in each valley plane, and spring aside. The nicks lie in
   the part the flush cut removes. **For a tip stripped webbed, there is no
   nicker:** the tine noses enter the ~0.98 mm gaps between bare bundles and
   meet each web at the strip line, which the slug's tear has already opened.
2. **Zip.** The end drives on onto the **wedge comb**: N−1 tines of laminated
   stainless, 0.2 mm thick at a blunt nose (radius ~0.05 mm) and 0.8 mm at the
   root, 15–20 mm long. Noses at 1.7 mm pitch, roots at 2.5 mm, so the tines
   diverge like a fan, at most 8° on a 5P [calc W2 §2]. Each nose enters its
   nick or gap and drives a tear along the neck. The tines are staggered 2 mm
   from the centre outward, so one tear starts at a time.
3. **Stop** with the tine noses 1 mm short of the clamp face. Under the clamp
   the conductors cannot move apart, so nothing opens the crack further.
4. **Look.** With the tines in, a backlight under the pallet's open floor shows
   every split as a bright slit to the ELP camera above.
5. **Trim.** For J2 and J7 the one unused conductor is cut off at the root by a
   razor set across the clamp face.
6. **Hand over.** The conductors come off the tines already fanned toward
   housing pitch, because the copper takes a set in any bend tighter than a
   radius of 39–78 mm [P3 C11; calc §4]. The next fan block takes them from there.

**What locates what, and the reference for fixed.**
- **"Fixed" is the clamp face.** The comb is found once per session with a
  pallet that carries a feeler.
- **Laterally, the ribbon locates the tear:** the neck is where it goes. The
  nicker's slivers only have to start inside it; their V-noses find the valleys
  to about ±0.05 mm, independent of the ribbon's pitch stack [calc W2 §1]. A
  slug's gap needs no finding.
- **Axially, the clamp locates the split root.** The copper arms yield at a
  moment of 0.31–0.61 N·mm [P3 C11], so each conductor hinges near the crack
  tip instead of flexing as a long elastic beam, and the crack stays within
  about a millimetre of the tine noses [estimate; it scales with the yield
  moment]. The stage's stop sets the root to about ±1 mm and the clamp face
  backs it up.

**Force.** The station carries no crimp force. The zip needs, per web and for a
5P with all four webs at once [calc W2 §2, tear strength 10–25 N/mm from
Primasil wire grades]:

| Neck t_n | Per web | 5P, four webs |
|---|---|---|
| 0.15 mm | 1.5–3.8 N | 6–15 N |
| 0.25 mm | 2.5–6.2 N | 10–25 N |
| 0.35 mm | 3.5–8.8 N | 14–35 N |
| 0.50 mm | 5.0–12.5 N | 20–50 N |

The stagger keeps the peak near one web's force plus the others' sliding
friction. A lid with a TPU pad at ~100 N holds 50–100 N at μ 0.5–1. A 0.2 mm
tine buckles at ~5 N free, and at 40–70 N supported by silicone on both sides
[calc W2 §2], so the tines stand free less than 5 mm ahead of the ribbon.

**How it knows the web parted cleanly.**
- **Silhouette:** every parted conductor should be 1.60–1.80 mm wide along its
  whole parted length. A tear that ran into a jacket shows as a notch in one
  conductor and a flag of web on its neighbour.
- **Force trace:** a load cell under the comb reads a flat plateau for a tear
  along the neck; a tear that leaves the neck has to cut the 0.49 mm wall and the
  plateau steps up, visibly only when the neck is clearly thinner than the wall.
- **Copper touch:** the tines are isolated and wired; with the far-end port
  ([a6](a6-housing-as-last-comb.md)) or the reel's hub socket, a tine that
  reaches strands names the conductor.

**What the person does.** Nothing on a stage or at a reel clamp. In the hand
version, slides the pallet along a rail into the comb until it stops, looks,
pulls it back.

## Steps it covers and what it hands back

- **Covers:** split to the root, trim J2/J7, a first fan toward housing pitch,
  verification of the split.
- **Hands back:** nothing at the station, beyond sliding the pallet in the hand
  version.

## Why a blunt wedge and not a blade

- **Which path the tear takes.** Per millimetre of advance a tear along the neck
  separates t_n of silicone; one that leaves the neck along a conductor has to
  split its ~0.49 mm wall, then runs along the silicone-to-copper interface,
  which barely bonds. The neck is the cheaper path while t_n is well under the
  wall [calc W2 §2, energy argument, estimate]:

  | t_n | t_n / wall | Expected |
  |---|---|---|
  | 0.15 mm | 0.31 | zips |
  | 0.25 mm | 0.51 | zips |
  | 0.35 mm | 0.71 | marginal: may wander |
  | ≥ 0.49 mm | ≥ 1.0 | wanders into a jacket: cut instead ([a7b](a7b-plough-station.md)) |

- **A blunt nose cannot cut;** it only opens the crack ahead of it, so the
  material chooses the line. A sharp tine would cut wherever the ribbon's pitch
  error pointed it.
- **No kerf:** a 0.23 mm blade removes 0.115 mm from each flank even centred
  [calc W2 §1].
- **The tines become the fan:** they part and fan to housing pitch in one pass.

## Parts

| Part | Source | Note |
|---|---|---|
| Tines: 0.1–0.2 mm stainless leaves in a printed root block | laser-cut sheet, or feeler leaves filed | JLCPCB 304 stencils from $3, shipped in about a day (into-the-housing); thicknesses not observed [assumption]. Hotop 0.02–1.00 mm feeler set, $8.99 [Prime] |
| Nicker slivers | double-edge razor blades | Amazon, Prime to be confirmed ([`../sourcing-requests.md`](../sourcing-requests.md)) |
| Flexures, V-noses, root block, rail, stop, covered floor | printed PET-CF | |
| Backlight | bought | XIAOSTAR A5 light pad, $16.99 [Prime] |
| Load cell under the comb | bought | 5 kg bar cell with HX711, two for $9.99 [Prime] |

## By hand, first

The comb on a printed block with a rail and a hard stop. Lay a ribbon end in
[a1b](a1b-hand-shuttle.md)'s hand pallet, slide it into the nicker and on into
the comb, look at the slits against a phone torch, pull it back. No motors, no
electronics. It answers the station's two questions in an afternoon: does the
web zip, and does the tear stop at the clamp? A 5P end stripped webbed with two
razors on shims (p7), with a flat feeler driven into the slug's gap, answers the
same for order B.

## Branches and variants kept beside it

- **[a7b](a7b-plough-station.md), the plough:** floating razor slivers that cut
  along each valley, for a neck too thick to tear.
- **Laser slit** (borrowed-machines'
  [b4](../../borrowed-machines/ideas/b4-laser-slits-and-scores.md)): the same
  pallet on a laser bed, a slit along each valley back to the clamp face. It needs
  no web geometry and adds char and ash. Recorded as another cartridge.
- **Nick only, peel by hand:** the nicker alone, then the person peels each web
  back to the clamp face. The smallest useful build if the web zips.
- **Tines kept as the fan:** the pallet goes straight on to a housing-pitch
  crimp with neighbours out of plane; one comb per pallet.

## What it contributes

- **The ribbon locates its own split:** its pitch stack (up to ±0.23 mm across a
  5P from a centred datum [calc §1]) never enters the parting.
- **A tear stop as a datum:** the split root is the clamp face, which every other
  station measures from; fold-back parking needs exactly that.
- **Zero kerf, no cutting edge near a jacket, a self-reporting split.**

## Major unresolved problems

- **Neck thickness, and whether the web zips** (repo Open item 5): t_n must be
  well under the wall, ~0.6 of it for the zip from a slug's gap. One fresh
  cross-section under the ELP camera gives t_n; a metre peeled by hand shows the
  path.
- **Whether a wedge-driven tear in this silicone runs straight** at slow speed;
  filled rubbers can tear in a stick-slip or wandering way.
- **The tines:** a diverging laminated comb accurate to ±0.05 mm at the noses is
  fiddly handwork, or a laser-cut part of uncertain thickness.
- **Whether the crack stops at the lid** or creeps a millimetre or two under a
  soft TPU pad.

## Related ideas

- Branch: [a7b](a7b-plough-station.md). Module: [a5](a5-part-fan-strip-in-the-pallet.md).
- Used by [a1](a1-pallet-tour.md), [a2](a2-two-pallets-meet.md) and branches,
  [a3](a3-backshell-that-ships.md), [a4](a4-spool-as-magazine.md),
  [a9](a9-reel-end-docks.md), [a10](a10-dock-tack-then-nest.md).
- Other explorers: procedure-is-the-machine
  [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md) (the slug's
  gap); borrowed-machines [b4](../../borrowed-machines/ideas/b4-laser-slits-and-scores.md).

## What rests on assumptions

- Silicone tear strength 10–25 N/mm [source: Primasil grades], not BNTECHGO's.
- The energy argument for the tear path, and the crack staying within ~1 mm of
  the nose [estimate].
- Stencil sheet thickness [assumption].

## Labels

As [a1](a1-pallet-tour.md#labels).
