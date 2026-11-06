# Machine display cover

The flat PET-GF bezel retains the display with black socket-head screws along its
side borders. Rounded corners, equal screw insets and shallow head seats echo the
rear nameplate. The heads remain visible above the bezel face.

The cover section follows the enclosure's nominal wall. Its counterbores retain a
solid bearing floor; the screws engage short heat-set inserts in broad, continuous
housing stock. The [mount dimensions](mount-dimensions.json) define the cover,
window, screw stations and hardware engagement. Glass clearance and the PCB opening
belong to the matching enclosure receiver.

A flat TPU ring lies between the cover's lap and the glass border. It spreads the
light clamping load and accommodates printed surface variation. Seat the glass,
place the ring and cover, start every screw, and draw them down evenly until the
cover rests on its seats. The gasket retains the glass without hard clamping
against individual printed high spots.

Install the short inserts through the open display face before fitting the glass.
The cover prints face up on its flat back, without supports. The counterbores face
upward. Its screw-bearing stock uses solid deposition.

## Status plate

The display sits off the facet's centre, and the status plate takes the rest of the flat run
beside it, with one margin at each side edge and the same margin between the two. The plate is
as tall as the cover. Its four screws stand level with the cover's, at the same inset from its
own edges, so its white frame runs inside the screw heads.

The plate follows the rear nameplate: black PETG with the nameplate's white artwork, sunk into
the face and standing proud of it. The brand mark stands over a rule. Below them the light's
small aperture sits in a ring, with ON under it in the nameplate's identification letterforms.
The black is cut where the white stands, so the two colours are disjoint volumes. It prints face
up on its flat back, like the cover.

The light is a prewired blue LED from the EDGELEC assortment. It sits set back in a bore behind
the aperture, so it stays in the aperture's shadow when unlit. Its leads run down a channel from
the bore's foot into the display's PCB pocket and land on the display's terminal strip: the red
lead on VIN beside the J9 loom's V12, the black lead on DOUT0. The display firmware lights it as
the board comes up ([`src_front/README.md`](/firmware/src_front/README.md)).

The program that cuts the cover also writes `status-plate` and `status-plate-fasteners` in the
cover's own frame, so the machine places all of them with the cover's transform. The
[mount dimensions](mount-dimensions.json) carry the plate's numbers.
