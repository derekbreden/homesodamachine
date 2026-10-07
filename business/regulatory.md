# Regulatory Posture

Current regulatory scope for direct-to-consumer sale via homesodamachine.com.
The residential machine uses the household R-600a route under EPA SNAP Rule 22 and
UL 60335-2-24, second edition, April 28, 2017, as its best-supported design basis.
The [marking specification](/hardware/markings/README.md) records the source clauses,
two-panel warning artwork, ordinary appliance information and implementation work.

## Sales channels

The sales channel is homesodamachine.com. No UL or ETL listing is held or sought.
Sales channel alone does not establish the applicable product, installation or
certification requirements. SNAP use conditions can incorporate safety standards;
those obligations require review independently of retailer requirements.

## EPA Section 608 — refrigerant handling

[40 CFR 82.154(a)(1)(ix)](https://www.govinfo.gov/content/pkg/CFR-2025-title40-vol21/pdf/CFR-2025-title40-vol21-sec82-154.pdf)
exempts R-600a only in named end-uses: household refrigerators/freezers, retail food
stand-alone refrigerators/freezers, and vending machines. The exemption covers the
venting prohibition and Subpart F requirements for those uses. Natural refrigerants
have no blanket exemption.

The [household design basis](/hardware/markings/README.md) places the donor ice maker
and this residential beverage appliance in an exempt R-600a end-use. This is the
project's reasoned classification, not an individual EPA determination. The handling
method still addresses the refrigerant's flammability; the end-use exception is not
a finding that a release is safe in a confined space or near ignition sources.

## EPA SNAP — refrigerant end-use approval

SNAP (Significant New Alternatives Policy, Clean Air Act §612) approves refrigerants for specific product categories. Natural refrigerants are not blanket-exempt from SNAP — approval is granted per end-use.

**Household refrigeration is the design basis** for the residential-only machine.
[EPA's end-use definitions](https://www.epa.gov/snap/substitutes-refrigeration-and-air-conditioning)
include household beverage centers and stand-alone household ice makers.
[R-600a is listed as acceptable with use conditions](https://www.epa.gov/snap/substitutes-household-refrigerators-and-freezers).
The retail-food dispensing category concerns goods for commercial sale; that is a
weaker match to the intended use. Replacing the donor evaporator changes the design
subject to the safety requirements, not automatically the end-use classification.

The [household marking specification](/hardware/markings/README.md) uses one exterior
disposal panel and one service panel near the compressor/exposed tubing. It specifies
6.4 mm minimum warning lettering, a 15 mm minimum ISO 7010 W021 flame triangle,
R-600a and actual charge identification, and PMS 185 red at service-opening locations.
The brand/serial/QR plate and ordinary rating information can occupy separate faces.

## Applicable refrigeration safety standard

The [household R-600a listing](https://www.epa.gov/sites/default/files/2018-08/documents/epa_frdoc_0001-22694.pdf)
incorporates UL 60335-2-24, second edition dated April 28, 2017. It sets a **150 g
maximum per refrigerant circuit**, along with design, marking and testing provisions.
Later editions' smaller warning text does not replace that incorporated edition.
The relevant leakage/ignition, electrical, mechanical and abnormal-operation tests
apply to the finished design; the donor's qualification does not establish their
results for the custom evaporator and enclosure.

Factory donor charges are 15 g (Unit A, Antarctic Star HZB-12/Q) and 23 g (Unit B,
Frigidaire EFIC117-SS). The [assembly procedure](/hardware/assembly/refrigerant-loop.md)
requires a qualified charge for the redesigned loop; donor charge and evaporator volume
do not establish a final target or automatic overage. The finished charge must meet the
applicable limit and belongs on the unit and in its measured record. No minimum-room-area or installation-height label is
specified in the reviewed household marking clauses. Installation instructions still
need the actual ventilation and clearance requirements.

The compressor's terminal block and clip-on PTC start relay/overload module remain under the R-600a donor's own moulded power-box cover. That cover is part of the harvested compressor assembly: it stays intact and securely retained, and the appliance connects only at the donor assembly's factory-external electrical interface without opening or modifying the cover. The current build adds no second sheet-metal shroud. The SEFUSE thermal fuse lies against the outside flank of the donor cover, the MQ-6 sensor sits low in the cabinet and gates the compressor relay, and the Teyleten relay that switches the compressor's AC lives remotely on the +X wall of back-top.

What remains open for an applicable 60335 fire-enclosure claim is **qualification of the retained donor cover**, not implementation of a cover. Before making that claim, record the cover's material markings, condition, retention method, and lead-opening geometry, and review them against the applicable enclosure provisions. A missing, cracked, modified, loose, or incorrectly retained donor cover is a build failure.

## UL 943 — ground-fault protection

Class A GFCI, 6 mA trip threshold, 120 V personnel protection. The 2015 revision of the standard mandates automatic self-test (periodic internal verification with lockout on test failure) for all manufacture from that point forward.

D2C sale does not require this listing. A Class I plumbed appliance — three bonded chassis surfaces (carbonator, compressor body, under-counter plate) returning fault current through the C14 cord per `hardware/wiring/ac-wiring-schedule.md` — carries the shock-protection obligation regardless of certification path. The standard codifies what ground-fault protection in a household appliance actually requires.

An integrated in-appliance GFCI on the AC side is deferred from the current build and held in [`/future/pie-in-the-sky/gfci.md`](/future/pie-in-the-sky/gfci.md), which carries the scoped device, the inline-on-the-AC-side wiring, and the swappable-cord rationale. The current build lands the C14 inlet onto the three mains splices in the +X wall's own Wago wells with no device in series (`enclosure._side_wells`).

## CPSC general safety duty

Federal Consumer Product Safety Commission applies to any consumer product sold in the US. Product must not be unreasonably dangerous. No listing or certification required — this is a general duty of care, independently honored by the project's design practice.

## ASSE 1022 — backflow protection and vent discharge

Simply having a 1022 already puts us ahead of most of these products. A 1022 that vents into the bowl at the faucet would be the only home arrangement I've found where the vent's discharge is defined, drained and visible.

The U.S. home sparkling-water manual survey covers:

- **No supply backflow preventer named:** Kohler Aquifer K-34113, Samsung SodaStream refrigerators, Lilium, Brio 630, SeltzaHub, Lifeplus ST02, Everpure Exubera and Waterlogic WL500.
- **ASSE 1022 specified, with no vent discharge location described:** GROHE Blue includes it; Zip HydroTap requires the installer to add it on the supply.
- **Office-product reference:** Bevi describes discharge over an internal carbonator tray with a leak-detection valve, or through a tube to a container in the cabinet.

Open engineering items are tracked separately in the [hardware concerns register](/hardware/concerns.md).

## AIM Act — not applicable

The American Innovation and Manufacturing Act regulates HFCs. R-600a is a hydrocarbon, not an HFC, and is outside the scope of AIM Act phase-down rules, leak-management thresholds (15 lb rule, Jan 2026), and refillable-cylinder requirements.

Applies only if the project pivots to an HFC refrigerant.

## Assembly-time safety — hydrocarbon service and brazing

The circuit work in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) requires a technician trained for R-600a and equipment appropriate to flammable refrigerants. The donor charge is removed through a controlled handling route before opening; residual fuel can remain in oil after the pressure reaches atmospheric.

[Secop's hydrocarbon service guidance](https://www.secop.com/sustainability/natural-refrigerants/compressor-service) calls for separate dry-nitrogen clearing of high and low branches and flowing nitrogen protection during brazing. The technician's setup specifies pressure/flow control, open discharge paths, ventilation and ignition control. The welder's argon cylinder and a pressure dial do not establish that setup. Drier replacement, final process closure, micron-gauge decay limits, finished-unit charge and printed-plug thermal protection have their own qualification hold points in the assembly procedure.
