# Tee connector — reference fitting (stand-in)

The production fitting is the **John Guest PP0208E** 1/4" union tee, black PP
— the part every Tee junction (Y-C/D/E/F/G/H/KA/KB) in the
[fluid topology](/hardware/topology/fluid-topology.md) is built from, committed
in the BOM (`hardware/bom.md` §8).

`tee-connector.step` is **McMaster 51175K143**, a 1/4" push-to-connect
drinking-water tee — simply a STEP that happened to be available, used as a
close-but-not-exact geometric stand-in for layout. The design iterates toward
the **installed characteristics of the PP0208E**, not this file; swap in
measured PP0208E geometry as parts come in hand. Six of the manifold's eight
junctions are this fitting ([`fluid-topology.md`](/hardware/topology/fluid-topology.md)
§Junctions): the **run** takes a pair of valve ports lying in line — one above
the other, once the trays are stacked — and the **branch** turns off to the
third leg.

## Geometry (measured from the STEP)

The McMaster stand-in's figures — close to the PP0208E, not identical;
reconcile against a measured production tee once one is in hand.

Overall body envelope **13.7 × 26.9 × 40.1 mm**. Three 1/4" ports: a **run**
of two in-line ports on the long axis (collet faces at ±20.07 mm), and one
**branch** perpendicular to the run (collet face at +20.07 mm). All three meet
at the body center.

In the file's own frame (run axis = Z):

| Port | Opens | Location |
|---|---|---|
| Run 1 | +Z, collet face Z ≈ +20.07 | centered, (0, 0) |
| Run 2 | −Z, collet face Z ≈ −20.07 | centered, (0, 0) |
| Branch | +Y, collet face Y ≈ +20.07 | centered, (0, 0) |

The run carries straight-through flow; the branch joins at 90°. Run
half-length and branch reach are both 20.07 mm.

Accepts 1/4" (6.35 mm) OD tube; the 1/4" bore radius is 3.175 mm.

## Measured on the PP0208E in hand

Calipered on the production tee itself, not on the stand-in STEP, so `stations_hold` does not
read them back. Both spans are collet face to collet face along the run. The three depths are
how far a 1/4" tube stands inside one collet from the sleeve's face with the sleeve pressed
home, which is where the tube was marked.

| | |
|---|---|
| run span, sleeves extended | 42.5 mm (`RUN_SPAN`) |
| run span, both sleeves pressed | 39.2 mm (`RUN_SPAN_PRESSED`) |
| one sleeve's stroke | 1.65 mm (`COLLET_TRAVEL`) |
| first resistance to the tube | 7.0 mm (`FIRST_RESISTANCE`) |
| the teeth hold | 8.5 mm (`GRIP_DEPTH`); at 8.4 mm the tube still draws out |
| the tube bottoms | 10.0 mm (`INSERTION`) |

The collet and its gripping teeth move during locking; the internal tube stop stays in the
body. The measured sleeve stroke sets the carrier's fore-to-aft movement. The 7 and 8.5 mm
insertion observations describe how the tube enters the fitting.

At the fore stop the plate holds each sleeve fully depressed and a bottomed tube projects
10 mm beyond that face. The return stroke is 2.15 mm: 1.65 mm of sleeve extension while its
nose stays at the plate, followed by a 0.5 mm plate-to-nose gap. Tube length places each tip at the internal stop with the carrier aft and the cartridge
fully seated: 11.65 mm beyond the extended sleeve. At the fore stop, the cartridge is
2.15 mm short of seating when its tubes bottom. Relax the squeeze and advance it through
that final 2.15 mm. Both the connected carrier and the empty carrier rest at the aft stop.
The springs remain preloaded there; final cartridge seating may require a push.

The stand-in's 40.14 mm run span is 2.36 mm short of the production tee's measured extended
span. Its envelope locates the pack; `depress_branch` moves its branch sleeve by the measured
PP0208E travel. `enclosure_assembly.collet_plate_spec` places the fixed face on those fully
depressed noses. The internal tube-bottom station uses the measured 10 mm depth.

## Observed push-connect action

Derek's physical checks use a tube-tight collar to hold the collet while the tube moves:

- With the collar continuously holding the collet in, the tube withdraws easily with a
  small pull. Derek considers four times that single-connection effort comfortable for
  cartridge removal.
- A collet that is free to move follows an extracting tube outward and locks again, even
  if it was pressed inward immediately beforehand. Release requires continued restraint
  throughout withdrawal.
- A very small separating tug on either the tube or the fitting draws the collet into its
  locked position. The required movement is the collet's short travel; Derek judges the
  effort compatible with spring return.
- During insertion, the tube pushes an extended collet inward, including against a small
  spring-level outward force.

The fixed enclosure plate supplies the continuous collet restraint during cartridge removal.
For insertion, the opposed cartridge/carrier grasp bottoms the tubes; relaxing the grasp
allows the carrier springs to supply the short separating movement that engages the collets.
These observations establish the connection action. They contain no instrumented force
reading for the complete printed carrier or its spring pair.
