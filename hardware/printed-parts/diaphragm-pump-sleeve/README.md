# Diaphragm pump sleeve

One printed TPU elbow joins a diaphragm pump port barb directly to 1/4 in OD
LLDPE and turns the line 90°. The same part serves the suction and discharge
ports. It is clocked on the barb at assembly, so its tube leg can point any way
square to the barb. One hose clamp closes on each socket's plain outside.

The customer outcome is a smaller machine. On the suction port the elbow stands
in for a reinforced-PVC hose, two SAE #6 clamps, a MAACFLOW barb adapter and a
PP450822E. On the discharge port it stands in for the hose, clamps and
MAACFLOW; the GASHER check stays, fed from the tube through a PP010822E. The
turn happens inside the elbow, not in the tube: the tube leaves on an axis
[4.27](TUBE_AXIS) mm past the barb tip, where a straight sleeve and an R[14](BEND_R) bend
in the tube put it [31.51](STRAIGHT_AXIS) mm past. No part of the elbow stands
more than [10.12](PAST_TIP) mm past the tip.

This is an **unprinted fit candidate**. The current assembly still carries the
hoses and made-up fitting chains in
[internal plumbing](/hardware/assembly/internal-plumbing.md) §2. Socket fit,
clamp retention, pressure holding and lifetime have no physical result.

| Feature | Relaxed print dimension |
|---|---|
| Barb socket | Ø[9.00](BARB_BORE) mm × [11](BARB_DEPTH) mm, ending on the passage shelf |
| Tube socket | Ø[6.10](TUBE_BORE) mm × [15](TUBE_DEPTH) mm, ending on a shelf [3.5](TUBE_STOP) mm above the barb axis |
| Corner passage | Ø[4.40](PASSAGE) mm |
| Tube leg axis / outer corner, past the barb tip | [4.27](TUBE_AXIS) / [10.12](PAST_TIP) mm |
| Tube mouth from the barb axis | [18.5](TUBE_MOUTH) mm |
| Barb / tube outside diameter | Ø[14.6](BARB_OD) / Ø[11.7](TUBE_OD) mm |
| Radial wall, both sockets and the corner | [2.80](MIN_WALL) mm |
| Solid CAD volume | [3.191](VOLUME) cm³ |

## Fit basis

The [scanned G Ganen ports](/hardware/reference/g-ganen-pump/README.md) carry
two shallow barb crests each. Inside the socket's [11](BARB_DEPTH) mm the
largest scanned diameter on either port is Ø[10.26](CREST) mm, and the deepest
valley between the crests is Ø[9.23](VALLEY) mm. The [9.00](BARB_BORE) mm
socket therefore stretches about [14](CREST_STRETCH)% over the crests and
grips the valleys. The socket mouth stands at the scanned Ø[10.26](ROOT) mm
station, short of the casting's root band. The scan profile is an external
reading, not a hose-retention rating.

The [6.10](TUBE_BORE) mm tube socket has [0.25](INTERFERENCE) mm nominal diametral
interference with the 6.35 mm tube. Installed, the elbow measures about
Ø[15.41](BARB_OD_INSTALLED) mm over the barb and Ø[11.83](TUBE_OD_INSTALLED) mm
over the tube, conserving the annular section. Both fall inside the owned
10–16 mm YDS butterfly clamps' range
([B07C33VLQ6](https://www.amazon.com/dp/B07C33VLQ6)). With the barb clamp's
[9](CLAMP_BAND) mm band flush with the barb mouth, the tube leg stands [0.35](BAND_AIR) mm
clear of it. Those clamps have a 430 stainless band and housing, a plated
carbon-steel screw and a POM key; the seller lists them for low-pressure
service. They suit the fit trial. A clamp for the shipped joint follows the
trial's pressure and retention result and the bay's wet exposure, which is why
the pump hoses carry 316 clamps today.

The barb tip bottoms on the shelf where the socket steps down to the
[4.40](PASSAGE) mm passage, which places the mouth short of the casting. The
tube bottoms on its own shelf. In a straight sleeve an over-pushed tube only
meets the barb; in this elbow it would close the corner passage, so the shelf
sets the tube's depth.

The installed CAD opens the sockets to the largest crest and the tube OD and
grows the outside radii by conserving annular area. It is placement geometry,
not an elastomer strain, sealing pressure or retained clamp load.

## Material

Both joints carry pressure. The suction side sees supply pressure while V-K
is open; the discharge side sees the pump's own outlet pressure, advertised at
110 psi. Print the trial in **Bambu TPU 95A HF**, the hardest of the shop's
soft TPUs (85A, 90A, 95A HF), for the most grip at a given stretch over the
barb; [14](CREST_STRETCH)% stretch over the crest is within what a 95A tube takes onto a
barb. How much a sleeve relaxes under its clamp depends on the TPU's chemistry
and temperature, not its hardness alone, and no grade here has a relaxation
result. Use dry filament and a solid process: 100% infill and
at least four wall loops. Keep hole and contour compensation at zero for the
first fit.

## Print and assemble

Print as a V standing on the [6.55](FOOT_WIDTH) × [11.7](FOOT_LENGTH) mm flat
across the outer corner, both mouths up, [22.2](PRINT_HEIGHT) mm tall. The STL
is exported in that pose. A 90° elbow cannot hold both of its bores steeper
than 45°. In this pose every bore crown and every lower face stands at 45°,
nothing shallower, and no support is needed. The foot keeps a full wall to the
corner passage.

1. Slide one open clamp over each socket.
2. Push the barb socket onto the port until the barb tip stops on its shelf.
   Warm water eases the stretch; do not oil the barb.
3. Turn the elbow on the barb so the tube leg points along its line.
4. Square-cut the tube, mark [15](TUBE_DEPTH) mm from its end, and push it in until it stops
   on its shelf with the mark at the mouth.
5. Seat the barb clamp's band flush with the barb mouth and the tube clamp's
   band flush with the tube mouth, each housing turned away from the other
   leg. Tighten each by hand until the sleeve grips without being cut or the
   tube ovalized.

## Acceptance

The trial decides whether the pump lanes are laid out around these elbows
instead of hoses and fitting chains. Each result belongs to the identified
print.

- **Fit:** both elbows seat on the pump without splitting or whitening, both
  tubes stop at their marks, and the clamps close within their range.
- **Discharge:** run the pump from a cup of water into the SENCTRL 0–200 psi
  gauge through a PP450822E, deadheaded. The gauge records the pump's actual
  maximum; hold it 30 minutes with no weep at either socket and the tube still
  at its mark.
- **Suction:** pressurize the suction tube from the BEAMNOVA hydro pump at the
  80 psi household supply ceiling, through the pump to the deadheaded gauge,
  and hold 30 minutes with the same criteria at both elbows.

The hydro pump, gauge and KOOTANS nipple are the
[carbonator hydro rig](/hardware/assembly/pressure-vessel.md#7-hydro-test).
Endurance, clamp relaxation and wetted-surface qualification remain separate.

Regenerate from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/diaphragm-pump-sleeve/diaphragm_pump_sleeve.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/diaphragm-pump-sleeve/diaphragm_pump_sleeve.py`
