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
the face and standing proud of it. The brand mark stands over a rule. Below them a translucent
PETG window sits in a white ring, with ON under it in the nameplate's identification letterforms.
The window follows the diameter of the LED's mounting bore and fills the plate's complete
thickness, flush with both faces. A black margin separates it from the white ring, whose line
weight matches the frame and rule. Black, white and translucent PETG occupy disjoint volumes.
The plate prints face up on its flat back, like the cover.

Derek accepts the full-thickness window's illumination with the blue LED. The
[archived physical result](https://github.com/derekbreden/homesodamachine/blob/1fb531af577d22cb70a034cdff4710a7583601c0/hardware/printed-parts/enclosure/display-cover/prints/2026-11-09-status-light/physical-result.json)
and [unlit and lit photographs](https://github.com/derekbreden/homesodamachine/tree/1fb531af577d22cb70a034cdff4710a7583601c0/hardware/printed-parts/enclosure/display-cover/prints/2026-11-09-status-light)
record his in-person assessment. He notes that the photographs do not do the result justice.

The light is the [CHANZON prewired clear-lens blue LED](https://www.amazon.com/dp/B08G4Z6KPV).
Its clear lens directs light into the printed diffuser. The LED sits in a round pocket behind
the window. The pocket's floor continues the lower faces of the diamond lead channel, which
opens into the display's PCB cavity. The channel's roof follows the print frame.
The wires reach the display's terminal strip: the blue positive lead on VIN beside the J9 loom's
V12, the black lead on DOUT0. The
EDGELEC's positive lead is red. Both lamps have an inline resistor. The display firmware lights it as
the board comes up ([`src_front/README.md`](/firmware/src_front/README.md)).

Fit the wired lamp into the round pocket with the status plate and display removed. Feed the
free wires through the lead channel into the accessible display cavity, then fit the flat
status plate over the lamp. Keep force off the epoxy-to-lead joint, resistor and solder joints.
The [physical observations](wired-led-fit/physical-observations.json) hold the acquired lamp's
measurements and Derek's reported installation in the printed housing. The deeper, shared
floor requires its own physical confirmation.

The program that cuts the cover also writes `status-plate` and `status-plate-fasteners` in the
cover's own frame, so the machine places all of them with the cover's transform. The
[mount dimensions](mount-dimensions.json) carry the plate's numbers.
