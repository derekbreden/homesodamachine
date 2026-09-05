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

The teeth, O-ring and stop are the body's, so from the extended sleeve face, where the model
stands the noses, each depth is 1.65 mm deeper: 8.65, 10.15 and 11.65 mm
(`FIRST_RESISTANCE_EXTENDED`, `GRIP_DEPTH_EXTENDED`, `INSERTION_EXTENDED`).

The stand-in's 40.14 mm run span is 2.36 mm short of the tee's extended span, and every butt in
the pack is drawn on the stand-in. `enclosure_assembly.collet_plate_spec` builds the collet
plate's release stroke on `COLLET_TRAVEL`.
