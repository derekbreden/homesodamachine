# Face-up nameplate trial

The broad-leaf unit-0001 nameplate prints with its show face toward positive Z.
All white artwork stands 0.48 mm above the black face: `HOME / SODA / MACHINE`,
the faucet logo and drop, and the unit-0001 QR. The plate perimeter, 32 mm leaves,
3.6 mm hooks and 1.23 mm nominal bearing clearance fit the existing broad-leaf
receiver coupon.

Mark2 uses black PET-GF on its left 0.4 mm hotend and white PET-GF on its right
0.4 mm hotend. The hook tips sit on the bed. Black normal supports with the Snug
style carry the plate back. The angled insertion noses build upward from the hook
tips. Physical support removal is rejected: material between the catches and the plate back is trapped and does not withdraw as one mat. The plate visibly warps before removal. The raised relief of the lettering, logo/drop and QR is accepted. Relative colour alignment is not accepted; the white print is visibly displaced from its black cavities. The [horizontal-wing trial](../horizontal-wing-trial/README.md) carries the face-up design forward without plate supports.

The first layer is 0.20 mm, with 0.24 mm model layers except two short alignment
layers: 0.12 mm at Z 3.08–3.20 mm and 0.13 mm at Z 8.00–8.13 mm.
These preserve the hook shoulder at Z 4.40 mm, plate back at Z 13.65 mm,
flat show face at Z 16.05 mm and every white artwork top at Z 16.53 mm. All three
artwork groups have two complete 0.24 mm layers above their embedded inlays.

Support contact settings come from the shared `petgf.3mf`: two top interface
layers, 0.50 mm interface spacing and a 0.45 mm top Z gap. This orientation uses
normal Snug supports, 0.80 mm nominal XY separation, 0.45 mm bottom Z separation
above the catches, and a separate 0.50 mm first-layer gap. Both support material
assignments select black and flushing into supports is disabled. Requested Mark2
bed trim is +0.04 mm. Support removal and plate flatness are rejected; raised-artwork relief is accepted, with colour registration pending.

The verified native slice has 70 layers and estimates 61 minutes. Its final rear
interface is at Z 13.17 mm, providing 0.48 mm separation below the plate back.
The support bottoms above both catches also leave 0.48 mm. Emitted bead edges
have at least 0.518 mm lateral clearance across all shared leaf/support layers.
Both raised-artwork layers contain white extrusion in each of the
lettering, logo/drop and QR regions. The generated face toolpaths decode to
`HTTPS://HOSM.US/0001`; scanning the physical print remains a separate check.

`face_up_trial.py` generates the two-colour STEP, combined exterior STL and viewer
payload. `prepare_print.py` produces the native slice; `verify_print.py` checks the
emitted layers, artwork, support contacts and colour assignments.
