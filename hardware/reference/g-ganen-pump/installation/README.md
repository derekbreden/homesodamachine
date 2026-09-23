# Installed G Ganen pump

The pump uses four identical purchased rubber feet with nominal **7 mm pads**.
Each foot is an instance of the [shared scan-derived shape](../common-foot/g_ganen_foot.py),
including its rounded pad, elongated screw opening, underside reliefs and raised
rail clip. The feet slide independently along the casing rails and are removable.

The full 18 mm clip spans the observed rail from reference X = **0.5–18.5 mm**
at the front and **58.5–76.5 mm** at the rear. Slot centers are **X = 9.5 and
67.5 mm**, **Y = ±38.5 mm**, giving a **58 mm fore/aft span**. These are the
outermost positions with the complete visible clip engaged. The scans also show
partial overhang; they do not establish its retention or a physical end stop.

## Mount and assembly

Each foot uses one **M3 × 20 screw** and a **Ø9 × 0.8 mm washer**. The screw axis
is **1.5 mm outward from the slot center**, within the elongated opening. At that
position the nominal screw has **0.4 mm minimum slot clearance**, the washer
clears the raised shoulder by **0.5 mm**, and **38.29 mm²** of its annulus bears
on the flat pad, including solid material on both sides of the slot.

The matching cap columns and lid holes have these coordinates in the cap frame:

| Fore/aft pair | Cap X (mm) | Cap Y (mm) |
| --- | ---: | ---: |
| Front | −58.935458 | −37.928865, 42.071135 |
| Rear | −116.935458 | −37.928865, 42.071135 |

The nominal pad, washer and 5.4 mm lid leave **6.8 mm screw reach** into the
column, covering its **5.7 mm insert**. The **8.5 mm blind depth** leaves **1.7 mm
of screw-tip reserve** and **6.1 mm of floor stock**. That reserve is geometry;
actual rubber compression is read during assembly.

Place the pump on the lid, slide each foot to align its slot with the printed
hole, and fasten all four washers and screws. Fasten the pump **before the rear
keystone, flavor fittings and fluid-18 tube** occupy the driver approach. Check
actual screw passage, flat washer seating and clamp engagement while the pump
is accessible. The casing carries load through its rails and rubber feet into
the lid and the four internal cap columns.

The columns rise vertically from the cup floor. Their blind bores open at the
top, and the lid holes pass straight through; both have open support-removal
paths before assembly.

## Installed datums

`enclosure_assembly.build_water_pump()` rotates the reference **+90° about Z**,
puts the nominal bearing plane on the cap face, and leaves **9.7 mm** between
the rigid motor rear and the core rear. The reference-origin translation is
**(2.071135, 373.235458, 253.400000) mm**. Reference +Y discharge points toward
**enclosure −X**, as Derek identifies.

Rigid casing sections locate the pump laterally. Each complete foot is checked
against the actual stepped rear fitting, tubes and shell. The rear +Y foot has
**1.2745 mm** clearance to the flavor-A union. The pump's cap-bearing datum,
rigid-body placement and sliding-foot positions are separate inputs.

Both pump fitting chains retain their cap anchors. The pan retains its
core-relative withdrawal station. The pump hoses and adjacent reservoir-A fill
route follow the measured port axes and current pump placement.

## Native interfaces and checks

`g_ganen_installation.py` exposes the selected screw axes through
`mount_stations()` and `mount_holes()`. Each row also records its distinct
`slot_center_mm`, common pad thickness and rail engagement interval.
`CAP_MOUNT_XY` supplies the matching printed columns; `pump_mount_rows()` checks
them independently through the actual assembly transforms.

`rigid_shape()`, `feet_shapes(carry)` and `discharge_shape(carry)` keep the casing,
feet and port geometry independently queryable. `bearing_datum()` and
`placed_bearing_z(carry)` establish the lid contact plane. Occupied casing
volumes fill hidden cavities and are not material, mass or strength models.

Run the bounded mount check from the repository root:

```sh
HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python hardware/reference/g-ganen-pump/installation/validate_installation.py --skip-hoses --output hardware/reference/g-ganen-pump/installation/corrected-mount-check.json
```

It builds the current cap and lid in memory and checks screw-axis alignment,
rail-end placement, rigid clearance, insert reach, blind floor stock and screw
passage. The complete native assembly additionally checks the updated hoses,
reservoir fill route and surrounding components. Physical washer fit, loaded
rubber behavior and hose retention remain full-assembly observations.

The printed consumers are `foam-cap-top` and `foam-cap-lid-top`; their producer
feeds `foam-assembly`, `cold-core-assembly`, the enclosure Box and the complete
assembly. Their reviewed print archives are listed in the
[slice reviews](../../../printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/README.md).
