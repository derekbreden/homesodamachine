# Cartridge and cap support review

The complete production cartridge and cap are prepared for the fresh enclosure
assembly. The cartridge prints upright and the cap prints crown-down. The exact
two-part native archive passes its offline geometry, settings, toolpath-bound and
support-access review. Full-assembly integration findings currently hold further
submissions; Mark2 release remains with the coordinating task.

The plate has **496 layers and 179,260 source triangles**, with no native geometry
warning. Estimated time is **10 h 9 min 17 s**. The saved profile reports **419.9 g**
at 1.29 g/cm³; the same material volume is **465.5 g** at the repository's PET-GF
density of 1.43 g/cm³. Actual model and support paths retain **29.275 mm** minimum
clearance to the 325 × 320 mm nozzle area and **31.799 mm** between the two objects.

The plate inherits `petgf.3mf`: left 0.4 mm nozzle, black PET-GF, whole-layer
printing, 0.24 mm layers with a 0.20 mm first layer, two walls and 15% infill.
Automatic tree support uses a 0.45 mm top gap, two interface layers, 0.5 mm interface
spacing and 0.4 mm object clearance. Temperatures are 265°C nozzle / 80°C bed on
the first layer and 280°C / 80°C thereafter. The inherited `auto_brim` setting
produces **zero Brim extrusion roads** in this archive. Requested +0.04 mm trim
emits `G29.1 Z0.02` after the textured-plate compensation.

| Piece / support | Contact region | Root | Build-up | Removal lane before hardware installation |
| --- | --- | --- | --- | --- |
| Cartridge west | Flat hand-pull roof and rounded roof/end junction | Bed | 105.84 mm | Detach the interface and withdraw outward through the open −X hand-pull mouth; the lower stem stands outside the cartridge |
| Cartridge east | Flat hand-pull roof and rounded roof/end junction | Bed | 105.84 mm | Detach the interface and withdraw outward through the open +X hand-pull mouth; the lower stem stands outside the cartridge |
| Cap west motor opening | Annulus at the wider terminal well | Bed | 4.08 mm | Detach and withdraw through the open Ø45 mm well toward the crown, original +Z |
| Cap east motor opening | Annulus at the wider terminal well | Bed | 4.08 mm | Detach and withdraw through the open Ø45 mm well toward the crown, original +Z |
| Cap aft screw | Flat screw-head seat | Bed | 14.16 mm | Withdraw through its open crown-side counterbore in original +Z |
| Cap fore screw | Flat screw-head seat | Bed | 14.16 mm | Withdraw through its open crown-side counterbore in original +Z |

The flat hand-bearing roofs, circular motor shoulders and flat screw-head seats
keep their working shapes. Remove support while both parts are loose, before
installing pumps, wires or screws. The screw-seat support leaves through the head
counterbore; its route does not use the smaller screw-shaft bore. The six bodies
and six interface islands describe the slice. Physical removal effort and contact
finish are observations from the printed parts.

The [current offline review](../tee-readiness/full-enclosure-print/2026-09-21-pump-cartridge-mark2-v2.json)
binds the exact source STEP/STL files, saved profile, native G-code, support ledger
and the qualified fluid-2 guard-only source equivalence. The native archive is
`.cache/prints/2026-09-21-pump-cartridge-mark2-v2/ready/pump-cartridge-cap-black-z004-mark2-v2.gcode.3mf`,
SHA-256 `5df9a09154864e1916fd3de02e76441c23a91f92d70547785c7c35ff0e6dda01`.
The G-code SHA-256 is
`fa57cf15e877a9d2854bea8adfbe0309ce694bcfc24bad55341b422595ec4133`.
