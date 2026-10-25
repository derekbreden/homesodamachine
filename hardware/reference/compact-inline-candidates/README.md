# PISCO secondary regulator and Fluidfit check

The PISCO RVFUP1/4–1/4-0.3 preset regulator is the appliance's in-machine CO₂
secondary ([bom.md §4](/hardware/ledger/bom.md)). It is modeled from the
[OEM catalog](https://shop.pisco.com/wp-content/themes/agency-ecommerce/assets/images/preset-regulator.pdf),
PDF page 4. It is 62.4 mm overall with a 21.5 mm maximum diameter and 20 mm
secondary body diameter. Both 6.35 mm sockets take 17 mm insertion. The
catalog's L1=37.7 and L2=20.2 place their shoulders at Z24.7 and Z42.2.
Its long-neck inlet is `(0,0,0)` and short-neck outlet is `(0,0,62.4)`;
normal regulated flow is +Z.

The selected preset is 0.3 MPa, listed as 44 psi, with service pressure up to
145 psi. Its specification medium is air, and it allows reverse free flow;
the downstream check remains a separate component. CO₂ duty is not established
by this geometry. The model separates the estimated PBT body, aluminum outlet
fitting and POM release rings. Undimensioned necks and clipped wrench details
follow the OEM drawing/photo while retaining the published envelope.

The Fluidfit HCVU 1/4–1/4 check is not part of the appliance, whose two check
valves are both the [neoFit ACHV44-E](../neofit-achv44-check/README.md). The
HCVU is modeled from its
[exact OEM imperial drawing](https://www.fluidfit.net/eng/open_content/product/view.php?pm_no=262).
It has 6.35 mm push-connect sockets at both ends, 45.5 mm overall length,
15.5 mm maximum diameter and 16.1 mm tube insertion from each mouth.
The requested G color variant uses this family's dimensional row.

The native flow axis is **+Z**: inlet mouth `(0,0,0)`, outlet mouth
`(0,0,45.5)`. The OEM arrow points from the short stepped socket end toward
the long cylindrical-body end. The modeled blind sockets reach their full
16.1 mm depths, so inserted stems meet their nominal stop rather than a
shallow display cap. The valve mechanism is not modeled.

The body profile, necks and separate release collets are estimates from the
OEM outline. Overall length, maximum diameter and insertion depths follow
the table. The manufacturer catalog includes air/gas applications for its
POM family; this reference does not establish exact CO₂ duty qualification.

`geometry/candidate-regulator.step` and `geometry/candidate-check.step` are
native assemblies with separate body and collet solids. The corresponding
NPZ files have `v` and `f` arrays in the same frame.
`build.py` is editable; `dimensions.json` separates published dimensions,
estimated details and source evidence. `model.py` supplies a NumPy-only
`library()`, transformed `ports(kind)` and an `instance(kind)` helper, where
`kind` is `regulator` or `check`.

Rebuild both supported references manually through the CAD queue:

```sh
PYTHONPATH=. tmp/takeover/cadq "Compact inline reference models" -- tools/cad-venv/bin/python hardware/reference/compact-inline-candidates/build.py
```

This directory changes no assembly placement, recurring check or purchase record.
