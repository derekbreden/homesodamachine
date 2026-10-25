# Straight ASSE cuffs · TPU 85A

Two straight cuffs connect the Multiplex ASSE's inlet and outlet to 6.35 mm
OD tube. Their compact, coaxial sockets leave the regulator, pump and wiring
bay accessible above the cold core. The enclosure assembly calls this
generator for the installed geometry.

These are **unprinted nominal fit candidates**. The CAD bores match the
reference interfaces without an interference allowance. Neither the model
nor the generated print files establish a water seal, axial retention,
pressure capacity, food-contact suitability or service life.

| Dimension | Inlet | Outlet |
|---|---:|---:|
| Metal socket diameter | 17.15 mm | 15.88 mm |
| Metal socket depth | 13 mm | 14 mm |
| Metal socket radial wall | 2.8 mm | 2.8 mm |
| Reducer length | 5 mm | 5 mm |
| Tube socket diameter | 6.35 mm | 6.35 mm |
| Tube socket depth | 15 mm | 15 mm |
| Tube socket outside diameter | 11.832 mm | 11.832 mm |
| Minimum nominal radial wall | 2.741 mm | 2.741 mm |
| Overall axial length | 33 mm | 34 mm |

The passage narrows to a 4.4 mm diameter throat behind the tube end.
Metal interface dimensions come from the
[native Multiplex reference](../../reference/multiplex-asse1022/README.md).
Thread crests, actual tube dimensions and compliant fit remain properties of
the physical mating parts. The socket sizes are source parameters for fit
work; no print acceptance is assigned to these cuffs.

Print each cuff on its tube end, the metal socket mouth up. The flat floor of the
metal socket then faces up and prints as a floor. The 1 mm tube-stop shoulder
prints as a short overhang wall, and the outer reducer taper rises at 42.5°. No
support is used. The recipe is the vent sleeve's
[accepted Siraya single](../asse-drain-adapter/README.md#print-and-assemble):
Siraya Tech Flex TPU 85A on Mark1's right 0.6 mm nozzle, a glued Engineering
Plate, zero user Z trim, and an attached 5 mm outer brim around the 11.8 mm
footprint. The plate is `asse-cuffs` in
[trial preparation](../enclosure/trial-preparation/README.md).

Available TPU 85A stock and the
[pump sleeve's physical records](../diaphragm-pump-sleeve/README.md) establish
printing experience for their identified parts. They do not transfer fit,
seal or pressure acceptance to this geometry.

The two independent files are `asse-inlet-cuff` and `asse-outlet-cuff`, each
with STEP, STL, viewer payload and material sidecar. The exported solid has
the metal socket mouth at Z=0; the print turns it over. Use `assembly_shape(side)` for
installation; it returns the exact selected shape in the ASSE flow-axis
frame, whose origin is native ASSE `(0, 0, 27)`.

Regenerate from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/asse-straight-cuffs/asse_straight_cuffs.py
```
