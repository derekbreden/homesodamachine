# YZMSZ fixed 0.3 MPa water regulator

The ordered [YZMSZ regulator, ASIN B0CGS34P93](https://www.amazon.com/dp/B0CGS34P93),
is the **1/4 inch OD, non-adjustable 0.3 MPa** variant. It has native axial
push-connect sockets at both ends and a nominal outlet pressure of **43.5 psi**.
The listing describes household water and reverse-osmosis applications with an
engineering-plastic housing.

The reference uses a **67 mm tube-mouth span and 27 mm maximum diameter** as
an exterior layout estimate. The seller supplies one photograph of the fixed
variant and no dimension drawing. Its proportions resemble the dimensioned
Frizzlife PRV01 housing, whose 66.802 mm overall length and 26.67 mm maximum
diameter provide the size proxy. Common manufacture is not established. The
working uncertainty range is 60–74 mm long and 24–30 mm maximum diameter.

The native frame uses **+X flow**, following the pictured arrow from the broad,
windowed cap end to the narrow-neck connector end. Inlet and outlet mouths are
`(0,0,0)` and `(67,0,0)`, with outward axes `−X` and `+X`. Both annular mouth
faces are named in `geometry/yzmsz-water-regulator.step`. The through bore is
display geometry; regulator internals and seals are omitted. Collet details,
shoulder positions, shallow window recesses and 15 mm tube insertion are estimates.

`dimensions.json` records published facts, estimates, source links and geometry
hashes. `model.py` exposes `library()`, `instances()`, `ports()` and `mates()`
without importing production CAD. Frozen `v`/`f` geometry is in
`geometry/yzmsz-water-regulator.npz`.

Rebuild manually through the shared CAD queue:

```sh
PYTHONPATH=. tmp/takeover/cadq "YZMSZ water regulator reference" -- tools/cad-venv/bin/python hardware/reference/yzmsz-water-regulator/build.py
```
