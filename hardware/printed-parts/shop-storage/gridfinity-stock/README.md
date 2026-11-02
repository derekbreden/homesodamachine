# Gridfinity stock profiles

These fine models contain the unmodified `GridfinityBox` and
`GridfinityBaseplate` bodies from cqgridfinity 0.5.7. The manifest records each
constructor's parameters, the package source hashes, CadQuery/OCP versions,
scalar dimensions, model hashes, and native bounds, area and volume. The
package's MIT license is in `LICENSE`.

Box profiles stand three height units tall. Their floor, feet, stacking lip,
label ledges, divider positions and fillets keep the library's geometry.
The 8.23–8.27 mm band contains vertical faces throughout every box profile.
`holders.rs` splits at 8.25 mm and extends that section to the catalog's height,
then cuts the holder's authored troughs, slots and nominal bores. The Python
modules hold those dimensions and layouts.

Models use f64 vertices and the 0.005 mm absolute / 0.05 rad angular meshing
rule. Each triangle retains its stock face record. The manifest also records
one native seating witness per footprint for the existing dock gap check.
