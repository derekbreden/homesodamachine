# Diaphragm pump sleeve

One printed TPU sleeve joins a diaphragm pump port barb directly to 1/4 in OD
LLDPE. The same part serves the suction and discharge ports. One hose clamp
closes on each socket's plain outside. The customer outcome is a smaller
machine. On the suction port the sleeve stands in for a reinforced-PVC hose,
two SAE #6 clamps, a MAACFLOW barb adapter and a PP450822E. On the discharge
port it stands in for the hose, clamps and MAACFLOW; the GASHER check stays,
fed from the tube through a PP010822E. The line leaving either sleeve is
flexible 1/4 in tube that turns at R14 wherever the layout needs it.

This is an **unprinted fit candidate**. The current assembly still carries the
hoses and made-up fitting chains in
[internal plumbing](/hardware/assembly/internal-plumbing.md) §2. Socket fit,
clamp retention, pressure holding and lifetime have no physical result.

| Feature | Relaxed print dimension |
|---|---|
| Barb socket | Ø[9.00](BARB_BORE) mm × [11](BARB_DEPTH) mm |
| Tube socket | Ø[6.10](TUBE_BORE) mm × [15](TUBE_DEPTH) mm insertion |
| Bore transition | Smooth taper, [60](TAPER_ANGLE)° above the print bed |
| Overall length | [28.51](LENGTH) mm, [17.51](BEYOND_TIP) mm of it past the barb tip |
| Barb / tube outside diameter | Ø[14.6](BARB_OD) / Ø[11.7](TUBE_OD) mm |
| Radial wall, both sockets | [2.80](MIN_WALL) mm |
| Solid CAD volume | [2.531](VOLUME) cm³ |

## Fit basis

The [scanned G Ganen ports](/hardware/reference/g-ganen-pump/README.md) carry
two shallow barb crests each. Inside the socket's [11](BARB_DEPTH) mm the
largest scanned diameter on either port is Ø[10.26](CREST) mm, and the deepest
valley between the crests is Ø[9.23](VALLEY) mm. The [9.00](BARB_BORE) mm
socket therefore stretches about [14](CREST_STRETCH)% over the crests and
grips the valleys. The socket mouth stands at the scanned Ø[10.26](ROOT) mm
station, short of the casting's root band. The scan profile is an external
reading, not a hose-retention rating.

The [6.10](TUBE_BORE) mm tube socket has 0.25 mm nominal diametral
interference with the 6.35 mm tube. Installed, the sleeve measures about
Ø[15.41](BARB_OD_INSTALLED) mm over the barb and Ø[11.83](TUBE_OD_INSTALLED) mm
over the tube, conserving the annular section. Both fall inside the owned
10–16 mm YDS butterfly clamps' range
([B07C33VLQ6](https://www.amazon.com/dp/B07C33VLQ6)). Those clamps have a
430 stainless band and housing, a plated carbon-steel screw and a POM key; the
seller lists them for low-pressure service. They suit the fit trial. A clamp
for the shipped joint follows the trial's pressure and retention result and
the bay's wet exposure, which is why the pump hoses carry 316 clamps today.

The installed CAD opens the sockets to the largest crest and the tube OD and
grows the outside radii by conserving annular area. It is placement geometry,
not an elastomer strain, sealing pressure or retained clamp load.

## Material

Both joints carry pressure. The suction side sees supply pressure while V-K
is open; the discharge side sees the pump's own outlet pressure, advertised at
110 psi. Print the trial in **Bambu TPU 95A HF**, the hardest of the shop's
soft TPUs (85A, 90A, 95A HF). A harder sleeve relaxes less under its clamp and
resists blow-off better, and 14% stretch over the crest is within what a 95A
tube takes onto a barb. Use dry filament and a solid process: 100% infill and
at least four wall loops. Keep hole and contour compensation at zero for the
first fit.

## Print and assemble

Print upright, barb socket on the bed and tube socket up. The internal reducer
and both bore-entry chamfers rise 60° above the bed. The outside steps in
toward the tube end, so no surface overhangs and no support is needed.

1. Slide one open clamp over each end of the sleeve.
2. Push the barb socket fully onto the port until the barb tip is inside the
   reducer and the mouth stands just short of the casting. Warm water eases
   the stretch; do not oil the barb.
3. Square-cut the 1/4 in tube, mark 15 mm from its end, and insert it until
   the mark meets the tube mouth.
4. Seat the barb clamp's band flush with the barb mouth and the tube clamp's
   band flush with the tube mouth. Tighten each by hand until the sleeve grips
   without being cut or the tube ovalized.

## Acceptance

The trial decides whether the pump lanes are laid out around sleeves instead
of hoses and fitting chains. Each result belongs to the identified print.

- **Fit:** both sleeves seat on the pump without splitting or whitening, both
  tubes reach their marks, and the clamps close within their range.
- **Discharge:** run the pump from a cup of water into the SENCTRL 0–200 psi
  gauge through a PP450822E, deadheaded. The gauge records the pump's actual
  maximum; hold it 30 minutes with no weep at either socket and the tube still
  at its mark.
- **Suction:** pressurize the suction tube from the BEAMNOVA hydro pump at the
  80 psi household supply ceiling, through the pump to the deadheaded gauge,
  and hold 30 minutes with the same criteria at both sleeves.

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
