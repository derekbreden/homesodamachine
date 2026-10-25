# Soda-riser insulation

One 15 mm length of owned CARGEN closed-cell nitrile pipe foam surrounds the
straight soda tube at X50/Y354.3696, from Z264.5 to Z279.5. Nominal stock is
6.35 mm inside diameter and 25.4 mm outside diameter. The native reference uses
the enclosure-world frame with an identity placement.

Make two square end cuts and a straight longitudinal slit. Wrap the piece
around the tube with the pump installed, then close the slit with the existing
foil tape. The tube retains 11.1 mm bare below the sleeve and 7.826 mm bare
above it. The meter and fitting bodies remain bare.

[soda_rise_insulation.py](soda_rise_insulation.py) defines the nominal uncompressed
annulus. Its geometry matches the selected
[study sleeve](../../manifold-layout/studies/funnel-gate/parts/soda-rise-insulation.json).
The [production review](../../mechanical-qualification/enclosure-above-core/native-review.json)
checks this sleeve against the exported mounts, equipment and wiring. Geometric
fit establishes no foam compression, tape retention or thermal performance.

Stock: [purchases §9](../../ledger/purchases.md), CARGEN B0D2XFK337.
