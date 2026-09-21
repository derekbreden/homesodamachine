# Gas-chain fit and the shell print

The warm gas chain presents a **local back-top fit risk**, not a commissioning
prerequisite to printing an unpowered enclosure for assembly tests. The current
source models received-part dimensions nominally, and its gas-fit scorecard item is
a warning goal. The [source audit](source-audit.json) identifies the exact source
and captured Box hashes; it does not claim a physical fit or a fresh whole-shell pass.

| Back-top feature | Modeled part | Printed fit | Missing geometry observation |
|---|---|---|---|
| WR1110 barrel cradle | Ø19.0 mm; 27 mm round length | Ø19.3 mm; 9.5 mm rib length | Actual smooth-barrel OD; room for the rib entirely between the two hexes |
| GASHER inlet cradle | Ø15.5 × 11 mm round inlet boss | Ø15.8 mm; 9.5 mm rib length | Actual boss OD and clear round length from the female mouth to the wrench hex |
| Made-up gas-fitting ceiling pockets | PI010822S uses a nominal 18.5 mm exposed adapter reach; coupling is provisional Ø22 × 25.4 mm with 11 mm makeup | 2 mm plan air and 1 mm crown air over the modeled envelope | Coupling maximum OD/length and actual made-up collet reaches from the metal bearing datum |

The GASHER rib has only 0.75 mm nominal axial room at each end. A larger or shorter
round boss can meet that cradle. A longer or wider made-up coupling/adapter stack
can meet the ceiling pocket even when flexible hose cut lengths can be changed.
Those are concrete reasons a back-top print could need local correction; no actual
received-part interference has been established by this audit.

The minimum useful check is the two bearing-surface readings plus the external
envelope of the made-up units. A side photo that identifies the bearing datum and
collet ends helps place the step boundaries. Nominal comparisons are 94.0 mm
collet-to-collet for the regulator and 91.4 mm for the check assembly. The check's
collets lie 18.5 mm upstream and 72.9 mm downstream of its female metal inlet face.
These values describe the model; they are not measured fit limits.

Internal thread engagement need not be calipered separately for the shell: the
made-up external envelope includes its geometric effect. Thread engagement and
sealing, material/rating confirmation, reverse sealing and operating performance
remain assembly and commissioning qualifications. Printed tie access, actual hose
bends, insertion and wrench handling remain physical assembly observations.

Front-top's tee, spring, release-plate and cartridge stations do not depend on these
gas fittings. Front-top can proceed through its own current geometry and slice
checks. Neither lower quadrant has a direct gas-fitting cradle or ceiling pocket.
All four can be printed as the requested assembly trial, with this back-top fit
uncertainty recorded; claiming verified received-part gas fit requires the short
geometry observations above. No additional whole-part scan or separate coupon is
indicated by the current evidence.

```sh
tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-readiness/gas-chain-shell/audit_source.py
```

The audit parses source constants and the stored Box only. It does not regenerate
geometry, change layout, or release a printer job.
