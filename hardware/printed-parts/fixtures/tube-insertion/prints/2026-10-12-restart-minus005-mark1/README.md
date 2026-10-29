# Liner restart trial — minus 0.05 mm

This offline trial changes only the liner recipe's filament restart
compensation to −0.05 mm. Native G-code retracts 1.00 mm and restores
0.95 mm at each of the 310 object starts. The STL, two-object placement,
wall order, seam positions, 225°C nozzle temperature, 10 mm/s retraction
and unretraction speeds, 0.18 mm layers, 100% infill and Mark1 liner
job's 0.00 mm user Z trim retain their settings.

The [physical photos and direct observation](../2026-10-12-liners-d775-mark1/wall-start-observation.json)
show intermittent projecting loops at a channel edge, forming when a wall
starts after arrival from the other object. One liner is markedly worse
than the other. Excess material delivered at restart is the leading
hypothesis; the photos and balanced original G-code do not establish that
cause. No outward pulling motion is identified for the observed arrival.

The customer outcome is a clean, continuous tube-contact surface. This
small reduction tests whether the stationary restart delivery contributes
to the loops while keeping the grip dimensions and other print settings.
It is a diagnostic candidate, not a physically accepted process.

## Files

- [Editable project](tube-insertion-liners-d775-restart-minus005-z000-mark1.3mf)
- [Native print archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-12-restart-minus005-mark1/tube-insertion-liners-d775-restart-minus005-z000-mark1.gcode.3mf)
- [Exact native G-code](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-12-restart-minus005-mark1/tube-insertion-liners-d775-restart-minus005-z000-mark1.gcode)
- [Recipe change](tube-insertion-liners-d775-restart-minus005-z000-mark1.print.json)
- [Native review](tube-insertion-liners-d775-restart-minus005-z000-mark1.readiness.json)

The reviewed archive uses Mark1's right fixed 0.6 mm nozzle and external
black TPU 85A spool 255 on textured PEI. It has 155 layers, no supports,
at least 143.2 mm full-bead bed-edge clearance and no slicer warning.
Estimated use is 9.4 g and 1 hour 9 minutes. No trial print is submitted.

## Assessment

If printed, use the same spool and prepared two-liner placement. Label
the left and right objects before removing them so the layer-first and
layer-second paths remain identifiable. With the same ordinary viewing
light used for the supplied photos, examine the complete channel lip and
the first few millimetres of each perimeter after its seam. Compare with
the preserved baseline photos.

The working surface should have no projecting restart loops and no new
seam gaps or visibly thin starts. Fewer loops supports the restart-delivery
hypothesis; new gaps reject this reduction because they interrupt the
tube-contact surface. Unchanged loops leave the hypothesis unconfirmed.
The visual result establishes no grip force, strength or lifetime.
