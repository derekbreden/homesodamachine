# Diaphragm pump elbow

One printed TPU elbow joins a G Ganen port barb directly to 1/4 in OD LLDPE and
turns the line 90°. The same part serves the suction and discharge ports, two per
machine. It is clocked on the barb at assembly: the suction elbow's tube leg points
forward to V-K's outlet, and the discharge elbow's points 25° below forward to the
water check's inlet ([internal plumbing](/hardware/assembly/internal-plumbing.md) §2).
One clamp band closes on each socket's plain outside.

The turn happens inside the elbow, not in the tube. The tube leaves on an axis
[4.92](TUBE_AXIS) mm past the barb tip, and its mouth stands [18.5](TUBE_MOUTH) mm
from the barb axis, so both lines stay inside the pump's own width.

| Feature | Relaxed print dimension |
|---|---|
| Barb socket | Ø[9.00](BARB_BORE) mm × [11](BARB_DEPTH) mm, ending on the passage shelf |
| Tube socket | Ø[6.10](TUBE_BORE) mm × [15](TUBE_DEPTH) mm, ending on a shelf [3.5](TUBE_STOP) mm above the barb axis |
| Corner passage | Ø[4.40](PASSAGE) mm, two overlapping round bores |
| Barb / tube outside diameter | Ø[14.6](BARB_OD) / Ø[11.7](TUBE_OD) mm |
| Radial wall, both sockets | [2.80](MIN_WALL) mm |
| Heel and neck | the barb leg's own sphere about the corner, then a [6.5](NECK) mm smooth reduction to the tube leg |
| Clamp seats | complete [9](CLAMP_BAND) mm round bands at both mouths; [1](BAND_AIR) mm between the barb band and the tube leg |
| Flat foot | [88.9](FOOT_AREA) mm² across the heel's outer corner |
| Solid CAD volume | [3.432](VOLUME) cm³ |

## Fit basis

The [scanned G Ganen ports](/hardware/reference/g-ganen-pump/README.md) carry two
shallow barb crests each. Inside the socket's [11](BARB_DEPTH) mm the largest
scanned diameter on either port is Ø[10.26](CREST) mm, and the deepest valley
between the crests is Ø[9.23](VALLEY) mm. The [9.00](BARB_BORE) mm socket stretches
about [14](CREST_STRETCH)% over the crests and grips the valleys. The socket mouth
stands at the scanned Ø[10.26](ROOT) mm station, short of the casting's root band.

The [6.10](TUBE_BORE) mm tube socket has [0.25](INTERFERENCE) mm nominal diametral
interference with the 6.35 mm tube. Installed, the elbow measures about
Ø[15.41](BARB_OD_INSTALLED) mm over the barb and Ø[11.83](TUBE_OD_INSTALLED) mm over
the tube, conserving the annular section. The assembly places that installed
envelope; it is placement geometry, not an elastomer strain, sealing pressure or
retained clamp load.

The barb tip bottoms on the shelf where the socket steps down to the corner
passage. The tube bottoms on its own shelf, which keeps an over-pushed tube from
closing the corner.

The identified [Bambu TPU 85A article](/future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json)
of this geometry has a reported firm, stretchy friction fit, pushed on by hand
without a jig. The [TPU for AMS article](/future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpuams-mark1/physical-result.json)
is reported too stiff.

## Material and print

Print in **Siraya Tech Flex TPU 85A Clear** (SKU ST3008). 85A gives the stretch a
hand fit over the barb crests needs.

Use the
[accepted deposited-path pair](/future/pump-elbow-exploration/prints/2026-10-22-deposited-links-siraya85a-mark2/README.md)
and its
[processed archive](/future/pump-elbow-exploration/prints/2026-10-16-deposited-links-siraya85a-mark1/2026-10-16-elbows-deposited-links-siraya85a-right06-z000-mark1.gcode.3mf).
The accepted Mark2 print uses the right 0.6 mm nozzle, glued Engineering Plate,
zero user Z trim, 225°C first layer and 215°C normal layers, six walls, 100%
infill, 10 mm/s outer walls and no supports. It prints through turns along the
walls and cutaway fins, with contained straight transfers between deposited
paths and timelapse off. Use the processed archive directly; reslicing the
editable project omits this path processing.

The STL is exported in its print pose: a V standing on the flat foot, both
mouths up, [22.2](PRINT_HEIGHT) mm tall, every bore crown and lower face at 45° or
steeper. The
[Mark2 pair's physical result](/future/pump-elbow-exploration/prints/2026-10-22-deposited-links-siraya85a-mark2/physical-result.json)
records no strings seen and seal seeming as good as before. The
[stringing candidates](/future/pump-elbow-exploration/stringing-candidates.md)
record the routing mechanism and related trials.

Before fitting, look through both sockets and the corner passage against a light and
clear any strand. A loose strand in the suction elbow reaches the pump's own valves;
one in the discharge elbow reaches the water check's seat.

## Clamps

The owned 10–16 mm YDS butterfly clamps
([B07C33VLQ6](https://www.amazon.com/dp/B07C33VLQ6)) have a 9 mm band, and both
installed diameters fall inside their range. They have a 430 stainless band and
housing, a plated carbon-steel screw and a POM key, and the seller lists them for
low-pressure service. They suit the fit and pressure trial. The shipped clamp
needs maintained compression, wet-bay corrosion resistance and a duty rating, and
is chosen after the trial's pressure and retention result.

## Assemble

1. Slide one open clamp over each socket.
2. Push the barb socket onto the port until the barb tip stops on its shelf. Warm
   water eases the stretch; do not oil the barb.
3. Turn the elbow on the barb so the tube leg points along its line.
4. Square-cut the tube, mark [15](TUBE_DEPTH) mm from its end, and push it in until
   it stops on its shelf with the mark at the mouth.
5. Seat the barb clamp's band flush with the barb mouth and the tube clamp's band
   flush with the tube mouth, each housing turned away from the other leg. Tighten
   each by hand until the sleeve grips without being cut or the tube ovalized.

## Acceptance

Each result belongs to the identified print, filament and clamp. The Mark2
deposited-path pair has reported acceptance for no visible strings and a
qualitative seal comparison. Quantified pressure holding, retained grip and lifetime remain
unmeasured.

- **Fit:** both elbows seat on the pump without splitting or whitening, both tubes
  stop at their marks, and the clamps close within their range.
- **Discharge:** run the pump from a cup of water into the SENCTRL 0–200 psi gauge
  through a PP450822E, deadheaded, until its pressure switch stops it. The gauge
  records the pump's actual cut-out. Hold 30 minutes with no weep at either socket
  and the tube still at its mark.
- **Suction:** pressurize the suction tube from the BEAMNOVA hydro pump at the 80 psi
  household supply ceiling, through the pump to the deadheaded gauge, and hold 30
  minutes with the same criteria at both elbows.
- **Early relaxation:** leave both clamped and water-filled for 24 hours, then repeat
  both holds without retightening.

The hydro pump, gauge and KOOTANS nipple are the
[carbonator hydro rig](/hardware/assembly/pressure-vessel.md#7-hydro-test). Wetting
on the body points at the print; wetting at a cuff at interference and compression;
movement without wetting at retention and tube support. Endurance, clamp relaxation
and wetted-grade suitability remain separate. The
[layout and screening study](/future/pump-elbow-exploration/README.md) keeps the
print trials and the fixture detail.

Regenerate from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/diaphragm-pump-sleeve/diaphragm_pump_sleeve.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/diaphragm-pump-sleeve/diaphragm_pump_sleeve.py`
