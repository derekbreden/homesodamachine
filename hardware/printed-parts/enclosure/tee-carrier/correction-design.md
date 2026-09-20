# Carrier correction geometry

**Production held.** The carrier has a bounded upper-backing correction. The standalone
joint coupon and axial spring-guide study remain separate from the production mechanism.
The full-width carrier has not passed the requested stiffness or spring-capture qualification.

## Retained backing above the tees

Each production `_station_cutters()` cylinder ends at the reference tee's maximum run-end
envelope plus the required axial air. With the current 0.3 mm tube allowance, its boundary is:

```python
trough_top_z = tee_axis_z + tee.RUN_HALF + 0.3
```

The flat stub relief continues above that boundary. A retained-stock probe above
`trough_top_z`, between the stub-relief floor and the web's aft face, must lie entirely inside
each finished half. [verify_upper_backing.py](verify_upper_backing.py) reads the generated
native solids and proves this check rejects a reconstructed full-height overcut. It also
measures sections of the actual print mesh and confines the added stock to the declared web
insertion envelope. These checks do not qualify the actual purchased tee reference.

The generated current-reference carrier retains **13.45 mm** of upper height with
**4.108291 mm** backing. [upper-backing-check.json](upper-backing-check.json) records
271.28 mm³ added per half, zero removed material, zero added material outside the existing
web entry envelope, and zero added overlap with the current tee-arm probes. Recreating the
full-height overcut makes all four retained-stock checks fail. The outer tee centre's
printed-mesh Izz is **151.865 mm⁴**, **2.208×** the pre-spring-relocation section.

For scale only, hold the existing placement and stub-relief floor fixed and use Derek's
**21.25 mm extended run half-span**. The upper backing is then 12.27 mm tall and 4.108291 mm
thick; the lower 40.55 mm retains 2.5 mm thickness. Two-rectangle integration about the
combined section's centroid gives **Izz=145.47 mm⁴**, versus **68.776 mm⁴** for the full-height
2.5 mm section: **2.12× local resistance to fore/aft bending at equal modulus**.

This is a dimensioned section estimate, not exported revised geometry or a whole-carrier
stiffness result. The production tee's larger collar, changed placement and actual bowed
tube may alter the available upper stock. Recompute the retained section from the final
native solid and print mesh. Preserve the aft coil's installation corridor and the full
tie backing; an enlarged trough must not spend either silently.

## Centre connection

[The interlocking joint coupon](joint-coupon/README.md) is generated and checked separately.
Its two headed keys engage during the existing 3.25 mm outward seating movement. The
keeper's rigid blocks prevent reversal, and its flexible catch holds those blocks in their
seat. Neither a loose flat lap nor the flexible catch is the primary bending connection.

The coupon checks native solids, entry and seating volumes, capture and printable meshes.
It has 0.15 mm nominal fore/aft and 0.40 mm supported vertical air; these gaps still need
measurement in the actual material. The final tee stations, full-half insertion route and
rear access for the keeper remain integration requirements. A successful short coupon
does not replace a full-width comparative deflection test.

## Return spring capture

The delivered pair measures **6 mm OD, 27 mm free and approximately 7 mm compressed**.
Its current bearing separations, 19.50–24.15 mm, give 2.85 mm minimum nominal compression.
The [measured sample model](tee_carrier_spring.py) provides its occupied envelope and
compression ranges. Rate, wire, inside diameter and forces remain unknown; its displayed
cylinder is not spring material and supplies no mass or stiffness result.

The moving end needs a positively retained closure of its 10 mm side-loading opening.
Both end guides must remain engaged throughout the 4.65 mm mechanism travel and under
unequal grip displacement. A keeper alone closes an escape opening; it does not establish
continuous alignment across the current 6.40–11.05 mm gap between guide mouths.

An internal guide depends on the measured spring bore/wire, not on the catalog identity.
An outside sleeve avoids that unknown but increases the guide envelope. A nominal 6.6 mm
spring passage with a 1.5 mm sleeve wall is 9.6 mm OD; at the current X=97.535 mm axis its
outer surface reaches X=102.335 mm, inside the retaining shoulder's X=101.25–104.25 mm
band. It cannot simply be added without a shoulder and insertion-path review. The final
outward seating movement must also clear any fixed guide installed before the carrier.

A separate **19.0 mm guide projection from the fixed seat floor**, inserted axially after
the carrier is seated, is a feasible next candidate. It clears the moving bore floor by
0.50 mm at release and enters the moving bore by 5.95 mm at the aft limit. The remaining
5.15 mm of spring at that limit lies within the closed moving bore. This route still
requires the measured spring ID and a retained closure of the moving loading window.

The current native enclosure has 6.549 mm of wall between the fore access face at
Y=79.519 and the spring-seat floor at Y=86.068, on X=±97.535 and Z=210.1. A separate native
solid review finds the fore insertion corridor clear with the pump cartridge absent.
The pin would need 25.549 mm from the fore wall face to its tip for a 19.0 mm projection.
Its head must be recessed and positively retained: the seated cartridge ends at Y=79.269,
only 0.250 mm fore of that wall. A projecting head consumes that operating clearance.
Repeat this access check after the production tee establishes the final spring axis.

The local mechanism coupon must include the actual tee, release face, both guide ends,
spring, loading closure and the fore retaining shoulder. It must demonstrate spring
installation, keeper engagement, complete travel, positive end capture and free return.
This design note supplies no claim that an unspecified keeper or guide already passes.

## Qualification loads

Use the complete joined carrier and the intended printed material, supported at its actual
flank bearings. Record equal fore/aft loads and deflection at the centre and each outer tee,
then repeat with only one handhold loaded. Compare with the pre-relocation carrier under
the same load, support and temperature. Record permanent set and joint play after cycling.
The geometrically strengthened upper stock and broad keys are useful changes only if this
complete assembly is measurably stiffer while retaining free release and return.
