# Broad-leaf nameplate retention trial

One complete unit-0001 black-and-white nameplate and a matching receiver coupon.
The face, artwork, QR, perimeter and 82 mm leaf pitch retain the nameplate dimensions.
Each leaf is 32 mm wide and 1.3 mm thick, with an inward R1 root, leaving 3 mm of
plate at each end. Each square hook projects 3.6 mm, with a 1.2 mm land and 3.2 mm
insertion nose.

The hook shoulder stands 9.25 mm behind the plate's back and its tip at 13.65 mm.
The receiver catch stands at 8.02 mm, leaving 1.23 mm nominal clearance for full
engagement despite rough supported faces. The inward slot clears the deflected tip
through insertion. Nominal lateral engagement is 3 mm per hook, at least 2.85 mm
at full plate float, across the complete 32 mm span.

[Geometry checks](geometry-check.json) verify the unchanged face and artwork, seated
fit, outward capture, inward stop and a geometric insertion sweep. Physical testing
checks clean engagement, bow, shake retention and support removal. The main enclosure
receiver is a separate integration task; this print is a matched test pair.

Mark2 prints the black body and receiver with the left 0.4 mm hotend and the white
artwork with the right 0.4 mm hotend, using the external PET-GF spools. The nameplate
prints artwork-down and the receiver in back-top's print orientation. A 0.17 mm
straight-shaft layer at Z 5.00–5.17 mm preserves the hook bearing at Z 11.65 mm.
The receiver uses the same short layer band to share the prime tower's layer schedule.
The first layer is 0.20 mm and other model layers are 0.24 mm. The saved profile's
speeds, temperatures, walls and accessible functional supports are retained, including
the 0.24 mm support top gap. Requested bed trim is +0.04 mm.

`nameplate_retention_trial.py` generates the cover and receiver with a private interface
instance; it does not alter the production interface. `prepare_print.py` replaces only
the meshes and names in the accepted two-colour project and adds the precision layer.
