# Expanding show-edge treatment

`cadlib/overhang_round.py` supplies additive chamfer/tapers inside the original
unrounded stock. The R6 profile starts 2.292 mm inward and advances 0.5 mm per
millimetre of build rise until it meets the retained round at 3.317 mm. The
straight profile advances 0.12 mm per normal 0.24 mm layer. Top/inward rounds
retain fine layers.

The geometry applies to the tee carrier aft bed edges, upper exterior rims of
the enclosure and pump-cartridge hand pockets, and exterior roof side edges. Hand-pocket fills leave their flat lifting
ceilings and lower rims in place. Roof fills share the front/back silhouette.

`geometry-check.json` records samples from the actual STL sections and the
zero-area facets reported by lint. The largest sampled grip advance is
0.126 mm per 0.24 mm; the smooth corner loft and mesh tessellation are not
mathematically exact ruled chamfers. These samples do not establish all corner
returns or native extrusion overlap.

The accepted tee print is the physical reference. Fresh slices of the other
parts must apply the 0.20 mm first layer, 0.24 mm expanding bands, six local
walls, saved wall order and speeds, and no support contacts on those show
transitions. Functional support faces retain accessible supports. Existing
3MFs and older support audits do not qualify the new meshes. Production slice
review and physical surface checks remain pending.
