# Regulatory Posture

Current regulatory scope for direct-to-consumer sale via homesodamachine.com. The
refrigerant category, applicable standard and complete product marking specification
remain open; the [refrigerant marking review](/hardware/markings/README.md) records the
primary sources, provisional artwork and remaining information.

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

[EPA's household definition](https://www.epa.gov/snap/substitutes-refrigeration-and-air-conditioning)
includes stand-alone household ice makers, supporting that category for the donor.
The rebuilt dispenser's category remains unresolved. Its service/disposal procedure
cannot assume that the donor's exemption transfers. Handling non-exempt refrigerants
requires the applicable recovery practices and technician qualifications; certification
does not itself authorize intentional venting.

## EPA SNAP — refrigerant end-use approval

SNAP (Significant New Alternatives Policy, Clean Air Act §612) approves refrigerants for specific product categories. Natural refrigerants are not blanket-exempt from SNAP — approval is granted per end-use.

The closest functional match is **refrigerated food processing and dispensing
equipment**: [EPA's definition](https://www.epa.gov/snap/retail-food-refrigeration)
explicitly includes chilled carbonated beverages and holding tanks that dispense
chilled product. A self-contained refrigeration circuit does not by itself make the
machine a stand-alone refrigerator.

[The current dispensing table](https://www.epa.gov/snap/substitutes-refrigerated-food-processing-and-dispensing-equipment)
lists R-290 with use conditions and has no pure R-600a entry. Household refrigeration
does list R-600a with use conditions. Whether this residential-only plumbed dispenser
qualifies for that household category requires confirmation. The R-600a approval for
the finished machine is therefore **not established**. The [prepared EPA inquiry](/hardware/markings/epa-inquiry.md)
describes the actual product and asks for the applicable listing; it has not been sent.

[The marking specification](/hardware/markings/README.md) uses the current A3
dispensing warnings as a provisional design target: complete exterior, compressor and
packaging warnings; 6.5 mm capital letters against a 6.4 mm target; GHS flame with A3;
and red service-port markings. The actual charge and any applicable calculated
room-area/installation-height marks remain open. A small flame and `FLAMMABLE
REFRIGERANT` footer are not a complete warning set.

## Applicable refrigeration safety standard

The [current commercial dispensing listing](https://www.govinfo.gov/content/pkg/FR-2024-06-13/pdf/2024-11690.pdf)
for R-290 incorporates UL 60335-2-89 and ASHRAE 15-2022. The
[household R-600a listing](https://www.epa.gov/sites/default/files/2018-08/documents/epa_frdoc_0001-22694.pdf)
incorporates UL 60335-2-24, second edition dated April 28, 2017. Product category and
the controlling listing determine the applicable edition and conditions. A complete
evaluation of this machine against either route is not established.

Factory donor charges are 15 g (Unit A, Antarctic Star HZB-12/Q) and 23 g (Unit B,
Frigidaire EFIC117-SS). The [assembly procedure](/hardware/assembly/refrigerant-loop.md)
targets 5–15 g above the donor charge for the wound evaporator. These are development
targets, not measured finished-unit charges or proof of meeting an applicable charge
limit. A universal 150 g cap or exemption from room-area marking is not established
for this machine.

The compressor's terminal block and clip-on PTC start relay/overload module remain under the R-600a donor's own moulded power-box cover. That cover is part of the harvested compressor assembly: it stays intact and securely retained, and the appliance connects only at the donor assembly's factory-external electrical interface without opening or modifying the cover. The current build adds no second sheet-metal shroud. The SEFUSE thermal fuse lies against the outside flank of the donor cover, the MQ-6 sensor sits low in the cabinet and gates the compressor relay, and the Teyleten relay that switches the compressor's AC lives remotely on the +X wall of back-top.

What remains open for an applicable 60335 fire-enclosure claim is **qualification of the retained donor cover**, not implementation of a cover. Before making that claim, record the cover's material markings, condition, retention method, and lead-opening geometry, and review them against the applicable enclosure provisions. A missing, cracked, modified, loose, or incorrectly retained donor cover is a build failure.

## UL 943 — ground-fault protection

Class A GFCI, 6 mA trip threshold, 120 V personnel protection. The 2015 revision of the standard mandates automatic self-test (periodic internal verification with lockout on test failure) for all manufacture from that point forward.

D2C sale does not require this listing. A Class I plumbed appliance — three bonded chassis surfaces (carbonator, compressor body, under-counter plate) returning fault current through the C14 cord per `hardware/wiring/ac-wiring-schedule.md` — carries the shock-protection obligation regardless of certification path. The standard codifies what ground-fault protection in a household appliance actually requires.

An integrated in-appliance GFCI on the AC side is deferred from the current build and held in [`/future/pie-in-the-sky/gfci.md`](/future/pie-in-the-sky/gfci.md), which carries the scoped device, the inline-on-the-AC-side wiring, and the swappable-cord rationale. The current build lands the C14 inlet onto the three mains splices in the +X wall's own Wago wells with no device in series (`enclosure._side_wells`).

## CPSC general safety duty

Federal Consumer Product Safety Commission applies to any consumer product sold in the US. Product must not be unreasonably dangerous. No listing or certification required — this is a general duty of care, independently honored by the project's design practice.

## AIM Act — not applicable

The American Innovation and Manufacturing Act regulates HFCs. R-600a is a hydrocarbon, not an HFC, and is outside the scope of AIM Act phase-down rules, leak-management thresholds (15 lb rule, Jan 2026), and refillable-cylinder requirements.

Applies only if the project pivots to an HFC refrigerant.

## Assembly-time safety — argon purge during brazing

Not a regulation, but load-bearing for the build path described in `hardware/reference/ice-maker/README.md` "Cold core architecture" — wherever the refrigerant loop is opened and brazed.

After the factory R-600a charge is vented, residual hydrocarbon remains dissolved in the compressor oil and pooled in low points of the tubing. When a torch is applied to copper near an oil-soaked compressor pocket, the flame front pulls residual hydrocarbon into itself. Mitigation is to flow low-pressure argon (a few psi, flowing — not static) through the opened loop during and through the braze, sweeping residual fuel out ahead of the heat.

The documented build path reuses the argon cylinder already present for laser welding, with the appropriate purge-side regulator / tubing setup for refrigeration brazing.
