# Face-up nameplate trial

The broad-leaf unit-0001 nameplate prints with its show face toward positive Z.
White `HOME / SODA / MACHINE` lettering stands 0.48 mm above the black face.
The faucet logo and QR are flush inlays. The plate perimeter, 32 mm leaves,
3.6 mm hooks and 1.23 mm nominal bearing clearance fit the existing broad-leaf
receiver coupon.

Mark2 uses black PET-GF on its left 0.4 mm hotend and white PET-GF on its right
0.4 mm hotend. The hook tips sit on the bed. Black normal supports with the Snug
style carry the plate back. The angled insertion noses build upward from the hook
tips. Support contacts are accessible
from the plate's open edges: separate the connected support mat, withdraw its
central region along the 38 mm plate axis between the leaves, and peel the outer
strips toward the short ends. Remove
all supports before fitting; preserve the leaf roots and the square catches.

The first layer is 0.20 mm, with 0.24 mm model layers except two short alignment
layers: 0.12 mm at Z 3.08–3.20 mm and 0.13 mm at Z 8.00–8.13 mm.
These preserve the hook shoulder at Z 4.40 mm, plate back at Z 13.65 mm,
flat show face at Z 16.05 mm and letter tops at Z 16.53 mm. The lettering has
two complete 0.24 mm layers above its embedded inlay.

Supports use three top interface layers, 0.20 mm top interface spacing and a
0.24 mm top Z gap. XY separation is 0.40 mm, with a separate 0.50 mm first-layer
gap. Both support material assignments select black and flushing into supports
is disabled. Requested Mark2 bed trim is +0.04 mm. Support removal and physical
surface quality require testing.

The verified native slice has 70 layers and estimates 63 minutes. Its final rear
interface is at Z 13.41 mm, providing the requested 0.24 mm separation below the
plate back. Both raised-letter layers contain only white extrusion; the logo and
QR end at the black show-face plane.

`face_up_trial.py` generates the two-colour STEP, combined exterior STL and viewer
payload. `prepare_print.py` produces the native slice; `verify_print.py` checks the
emitted layers, artwork, support contacts and colour assignments.
