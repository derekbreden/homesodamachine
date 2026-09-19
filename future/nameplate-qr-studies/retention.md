# Concealed nameplate retention

The proposed nameplate presses into the rear-wall pocket. Two long spring rails,
concealed behind its side edges, deflect toward its centre as their lead-ins cross
the pocket mouth. Broad lips engage shoulders in the rigid enclosure. A separate
seating surface locates the face flush with the surrounding wall.

This is a mechanism study, not a replacement for the production screw-retained CAD.
The O–R compositions show the face that concealed retention would make available.

## Evidence from Faucet

Derek's complete Sculpted faucet prints establish useful physical evidence:

- The cover walls supply the compliance; the receiving neck is rigid. The lips
  have broad bearing lands and the seated walls remain under inward preload.
- Derek liked the 1.25 mm inward preload per wing in cover B.
- The A–F trial could not be interpreted as a spring-force comparison alone.
  Only A/B seated. Derek observed rounded groove edges and a loose supported
  layer consuming the fit allowance; that loose layer could crush enough to seat.
- With increased groove allowance and relieved lip corners, both complete revised
  covers snapped and retained. Derek reported that dislodging them required more
  than a small force. The subsequent whole Sculpted faucet in cosmetic-preserving
  orientations also received a successful physical report.

The [shared snap dimensions](../../hardware/printed-parts/faucet/_display_snap.py)
are 1.25 mm wing preload, 1.20 mm engagement, 3.00 mm lip height, 3.48 mm groove
height, 0.30 mm end clearance and 0.25 mm inner-edge relief. The real-part trial's
sliced envelopes leave 0.480 and 0.400 mm of height room for its two cover
orientations. These are toolpath measurements, not measured bead dimensions.

The [retention trial](../../hardware/printed-parts/fixtures/faucet-cover-retention/README.md),
its [physical log](../../hardware/printed-parts/fixtures/faucet-cover-retention/print-log.md),
and the [production print record](../../hardware/printed-parts/faucet/faucet-display-petgf.md)
identify the parts and settings. Faucet confirmed these findings by direct task
message. Industrial shares the dimensions; its physical result is not part of this
evidence. There is no measured retention-force or lifetime result.

## Application to the plate

The current plate is 104.53 × 66.07 × 4.5 mm. Its 4.5 mm pocket lies in a 6 mm
wall plateau, leaving 1.5 mm of continuous floor. The plate's current 3 mm rear
bevel and matching pocket bevel consume most of the depth near its edges.

The proposed spring length runs along the plate's side, in the plane of the
artwork. This uses the plate's generous height for compliance without requiring
long prongs projecting into the machine. Each rail joins the rigid body at one
end and carries a broad catch toward its free end. Clearance beside the rail
allows inward motion; clearance beneath the face keeps that motion independent
of the lettering surface. Roots receive generous radii.

The two side regions need a new rear profile and mating pocket recesses. The
current all-around bevel cannot remain unchanged beneath the catches. The centre
of the pocket retains its floor, and the spring envelope targets the existing
4.5 mm depth. This depth target still needs a solid model and sliced verification.
The existing rear bar also supports the water pump: removing the nameplate screws
does not by itself authorize removal of that structure.

The functional surfaces are distinct:

- A sloped entry face spreads each rail inward during insertion.
- A broad return shoulder retains the plate after the rail springs outward.
- A seating rim sets face depth. The return contact needs to bias the plate
  against this seat; groove clearance must not become unrestrained axial play.
- Rounded inside lip corners clear printed groove fillets without rounding away
  the useful retaining shoulder.

Preload, engagement, beam section and release behavior are dimensions to establish
for this geometry. The 1.25 mm faucet preload is not specified for these rails.
The nameplate uses PETG Basic and a 0.2 mm nozzle; the successful faucet uses
PET-GF and a 0.4 mm nozzle. Their force and print-clearance results are not
interchangeable.

## Printing and the representative trial

The intended print keeps the lettering face upward. Rear rail channels need to
remain open for cleaning or use short bridges whose underside cannot obstruct
spring travel. The retaining lands must not depend on a supported first layer
compressing. Pocket shoulders belong on the side walls so their bearing faces
can run vertically in the enclosure's established print orientation.

The representative fit trial is the complete nameplate and a receiving section
with the actual wall, bevel and pocket geometry, printed in their intended
orientations and materials. It should establish seating, face flatness, retention,
removal and the printed QR together. A QR scan of the rendered artwork only checks
its encoded content; it does not establish a printed scan result.
